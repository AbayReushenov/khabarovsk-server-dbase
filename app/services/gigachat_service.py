"""GigaChat service for forecast generation.

This module provides integration with GigaChat API for generating
sales forecasts based on historical data and context.
"""

import json
import os
import base64
import requests
import urllib3
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import asyncio
from dotenv import load_dotenv

from app.utils.logger import app_logger
from app.models.schemas import GigaChatResponse, ForecastResult

# Load environment variables
load_dotenv()

# Disable SSL warnings (similar to rejectUnauthorized: false in Node.js)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class GigaChatService:
    """Service for GigaChat API integration."""

    def __init__(self):
        """Initialize GigaChat service."""
        # Check for legacy credentials first
        self.legacy_credentials = os.getenv("GIGACHAT_CREDENTIALS")

        # New configuration approach
        self.client_id = os.getenv("GIGACHAT_CLIENT_ID")
        self.client_secret = os.getenv("GIGACHAT_CLIENT_SECRET")
        self.client_auth_key = os.getenv("GIGACHAT_CLIENT_AUTH_KEY")  # Pre-encoded auth key
        self.scope = os.getenv("GIGACHAT_SCOPE", "GIGACHAT_API_PERS")
        self.auth_url = os.getenv("GIGACHAT_AUTH_URL", "https://ngw.devices.sberbank.ru:9443/api/v2/oauth")
        self.base_url = os.getenv("GIGACHAT_BASE_URL", "https://gigachat.devices.sberbank.ru/api/v1")

        # Determine if we're in mock mode
        self.mock_mode = not (self.legacy_credentials or (self.client_id and self.client_secret) or self.client_auth_key)

        if self.mock_mode:
            app_logger.warning("GigaChat credentials not configured, using mock mode")
        else:
            if self.legacy_credentials:
                app_logger.info("GigaChat initialized with legacy credentials")
            else:
                app_logger.info("GigaChat initialized with new OAuth configuration")

        app_logger.info(f"GigaChatService initialized (mock_mode: {self.mock_mode})")

        # Cache for access token
        self._access_token = None
        self._token_expires_at = None

        # Create session with SSL verification disabled
        self.session = requests.Session()
        self.session.verify = False

    def _get_access_token(self) -> str:
        """Get OAuth access token for GigaChat API."""
        if self.legacy_credentials:
            return self.legacy_credentials

        # Check if we have a valid cached token
        if (self._access_token and self._token_expires_at and
            datetime.now() < self._token_expires_at):
            return self._access_token

        try:
            # Prepare OAuth request according to official Sber documentation
            if self.client_auth_key:
                # Use pre-encoded auth key
                auth_string = self.client_auth_key
                app_logger.info("Using pre-encoded auth key")
            else:
                # Encode client_id:client_secret
                auth_string = base64.b64encode(f"{self.client_id}:{self.client_secret}".encode()).decode()
                app_logger.info("Using client_id:client_secret encoding")

            # Generate unique RqUID as required by Sber documentation
            rq_uid = str(uuid.uuid4())

            headers = {
                "Content-Type": "application/x-www-form-urlencoded",
                "Accept": "application/json",
                "RqUID": rq_uid,
                "Authorization": f"Basic {auth_string}"
            }

            # According to Sber docs: only scope in payload, no grant_type
            payload = {
                "scope": self.scope
            }

            app_logger.info("Requesting new GigaChat access token")
            app_logger.debug(f"Auth URL: {self.auth_url}")
            app_logger.debug(f"Scope: {self.scope}")
            app_logger.debug(f"RqUID: {rq_uid}")

            # Add retry logic for rate limiting
            max_retries = 3
            retry_delay = 2

            for attempt in range(max_retries):
                try:
                    # Use data= instead of json= as per Sber documentation
                    response = self.session.post(self.auth_url, headers=headers, data=payload, timeout=60)

                    app_logger.debug(f"Token response status: {response.status_code}")
                    app_logger.debug(f"Token response headers: {dict(response.headers)}")

                    if response.status_code == 429:
                        if attempt < max_retries - 1:
                            app_logger.warning(f"Rate limited, retrying in {retry_delay} seconds... (attempt {attempt + 1}/{max_retries})")
                            import time
                            time.sleep(retry_delay)
                            retry_delay *= 2  # Exponential backoff
                            continue
                        else:
                            app_logger.error("Rate limit exceeded, no more retries")

                    if response.status_code != 200:
                        app_logger.error(f"Token request failed: {response.status_code} - {response.text}")

                    response.raise_for_status()
                    break

                except requests.exceptions.RequestException as e:
                    if attempt < max_retries - 1:
                        app_logger.warning(f"Request failed, retrying... (attempt {attempt + 1}/{max_retries}): {e}")
                        import time
                        time.sleep(retry_delay)
                        retry_delay *= 2
                        continue
                    else:
                        raise

            token_data = response.json()
            self._access_token = token_data["access_token"]

            # Calculate expiration time (subtract 60 seconds for safety)
            expires_in = token_data.get("expires_in", 3600)
            self._token_expires_at = datetime.now() + timedelta(seconds=expires_in - 60)

            app_logger.info("Successfully obtained GigaChat access token")
            return self._access_token

        except Exception as e:
            app_logger.error(f"Failed to get GigaChat access token: {e}")
            app_logger.debug(f"Exception details: {type(e).__name__}: {str(e)}")
            raise

    def _build_forecast_prompt(
        self,
        sku_id: str,
        historical_data: List[Dict[str, Any]],
        forecast_period: int,
        context: Optional[str] = None
    ) -> str:
        """Build prompt for forecast generation."""
        # Prepare historical data summary
        if historical_data:
            total_units = sum(row.get('units_sold', 0) for row in historical_data)
            total_revenue = sum(row.get('revenue', 0.0) for row in historical_data)
            avg_units = total_units / len(historical_data) if historical_data else 0
            avg_revenue = total_revenue / len(historical_data) if historical_data else 0

            # Get recent trends (last 7 days vs previous 7 days)
            recent_data = historical_data[:7] if len(historical_data) >= 7 else historical_data
            older_data = historical_data[7:14] if len(historical_data) >= 14 else []

            recent_avg = sum(row.get('units_sold', 0) for row in recent_data) / len(recent_data) if recent_data else 0
            older_avg = sum(row.get('units_sold', 0) for row in older_data) / len(older_data) if older_data else recent_avg

            trend = "растущий" if recent_avg > older_avg else "падающий" if recent_avg < older_avg else "стабильный"
        else:
            total_units = 0
            total_revenue = 0.0
            avg_units = 0
            avg_revenue = 0.0
            trend = "неизвестный"

        prompt = f"""
Ты эксперт по прогнозированию продаж пуховиков в Хабаровске.
Проанализируй исторические данные и создай прогноз продаж на {forecast_period} дней.

ДАННЫЕ ДЛЯ АНАЛИЗА:
SKU: {sku_id}
Период прогноза: {forecast_period} дней
Исторические данные: {len(historical_data)} записей
Общее количество проданных единиц: {total_units}
Общая выручка: {total_revenue:.2f} руб.
Средние продажи в день: {avg_units:.1f} единиц
Средняя выручка в день: {avg_revenue:.2f} руб.
Тренд: {trend}

ДЕТАЛЬНЫЕ ДАННЫЕ (последние записи):
"""

        # Add recent data details
        for i, row in enumerate(historical_data[:10]):  # Show last 10 records
            date = row.get('date', 'N/A')
            units = row.get('units_sold', 0)
            revenue = row.get('revenue', 0.0)
            temp = row.get('weather_temp', 'N/A')
            season = row.get('season', 'N/A')

            prompt += f"Дата: {date}, Продано: {units} шт, Выручка: {revenue:.2f} руб, Температура: {temp}°C, Сезон: {season}\n"

        if context:
            prompt += f"\nДОПОЛНИТЕЛЬНЫЙ КОНТЕКСТ: {context}\n"

        prompt += f"""
ЗАДАЧА:
Создай прогноз продаж на следующие {forecast_period} дней, учитывая:
1. Сезонность продаж пуховиков (зима - высокий спрос, лето - низкий)
2. Влияние температуры (холоднее = больше продаж)
3. Тренды из исторических данных
4. Особенности Хабаровского климата

ФОРМАТ ОТВЕТА (строго JSON):
{{
    "predictions": [
        {{
            "date": "2024-01-01",
            "predicted_units": 5,
            "predicted_revenue": 15000.0,
            "confidence": 0.85
        }}
    ],
    "explanation": "Объяснение логики прогноза",
    "confidence_scores": [0.85, 0.82, ...]
}}

Начинай прогноз с завтрашнего дня. Уровень доверия (confidence) от 0 до 1.
Ответь только JSON, без дополнительного текста.
"""
        return prompt

    def _call_gigachat_api(self, prompt: str) -> str:
        """Make actual API call to GigaChat."""
        try:
            access_token = self._get_access_token()

            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }

            payload = {
                "model": "GigaChat",
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "max_tokens": 2000,
                "temperature": 0.1
            }

            response = self.session.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=60
            )
            response.raise_for_status()

            data = response.json()
            return data["choices"][0]["message"]["content"]

        except Exception as e:
            app_logger.error(f"GigaChat API call failed: {e}")
            raise

    def _parse_gigachat_response(self, response_text: str) -> GigaChatResponse:
        """Parse GigaChat response and extract forecast data."""
        try:
            # Try to extract JSON from response
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1

            if start_idx == -1 or end_idx == 0:
                raise ValueError("No JSON found in response")

            json_text = response_text[start_idx:end_idx]
            data = json.loads(json_text)

            return GigaChatResponse(
                predictions=data.get("predictions", []),
                explanation=data.get("explanation", ""),
                confidence_scores=data.get("confidence_scores", [])
            )

        except (json.JSONDecodeError, ValueError) as e:
            app_logger.error(f"Failed to parse GigaChat response: {e}")
            app_logger.debug(f"Raw response: {response_text}")

            # Return fallback response
            return GigaChatResponse(
                predictions=[],
                explanation="Ошибка парсинга ответа от модели",
                confidence_scores=[]
            )

    def _generate_mock_forecast(
        self,
        sku_id: str,
        forecast_period: int,
        historical_data: List[Dict[str, Any]]
    ) -> GigaChatResponse:
        """Generate mock forecast for development/testing."""
        app_logger.info("Generating mock forecast")

        # Calculate base values from historical data
        if historical_data:
            avg_units = sum(row.get('units_sold', 0) for row in historical_data) / len(historical_data)
            avg_revenue = sum(row.get('revenue', 0.0) for row in historical_data) / len(historical_data)
        else:
            avg_units = 3
            avg_revenue = 9000.0

        predictions = []
        confidence_scores = []

        for i in range(forecast_period):
            # Add some variability
            variation = 0.8 + (i % 3) * 0.15  # Vary between 0.8 and 1.1
            predicted_units = max(1, int(avg_units * variation))
            predicted_revenue = avg_revenue * variation
            # Simple sinusoidal mock temperature: colder at start, warmer later
            predicted_temp = round(-20 + 15 * (i / max(forecast_period - 1, 1)), 1)
            confidence = 0.75 + (i % 2) * 0.1  # Vary between 0.75 and 0.85

            forecast_date = datetime.now() + timedelta(days=i + 1)

            predictions.append({
                "date": forecast_date.strftime("%Y-%m-%d"),
                "predicted_units": predicted_units,
                "predicted_revenue": round(predicted_revenue, 2),
                "predicted_temp": predicted_temp,
                "confidence": round(confidence, 2)
            })
            confidence_scores.append(confidence)

        return GigaChatResponse(
            predictions=predictions,
            explanation=f"Мок-прогноз для SKU {sku_id} на {forecast_period} дней на основе исторических данных",
            confidence_scores=confidence_scores
        )

    async def generate_forecast(
        self,
        sku_id: str,
        historical_data: List[Dict[str, Any]],
        forecast_period: int,
        context: Optional[str] = None
    ) -> GigaChatResponse:
        """Generate forecast using GigaChat API."""
        if self.mock_mode:
            return self._generate_mock_forecast(sku_id, forecast_period, historical_data)

        try:
            prompt = self._build_forecast_prompt(sku_id, historical_data, forecast_period, context)

            app_logger.info(f"Generating forecast for SKU {sku_id}, period: {forecast_period} days")

            # Call GigaChat API
            response_text = self._call_gigachat_api(prompt)

            app_logger.info("Successfully received GigaChat response")
            app_logger.debug(f"Response length: {len(response_text)} characters")

            return self._parse_gigachat_response(response_text)

        except Exception as e:
            app_logger.error(f"Error generating forecast with GigaChat: {e}")

            # Return fallback forecast
            return self._generate_mock_forecast(sku_id, forecast_period, historical_data)


# Global instance
gigachat_service = GigaChatService()
