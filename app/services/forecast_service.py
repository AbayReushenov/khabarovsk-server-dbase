"""Forecast service for sales prediction.

This module coordinates forecast generation by integrating historical data
retrieval, GigaChat API calls, and forecast storage.
"""

import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

from app.utils.logger import app_logger
from app.models.schemas import (
    ForecastRequest, ForecastResponse, ForecastResult,
    ForecastHistoryResponse, ForecastHistoryItem
)
from app.services.supabase_client import supabase_client
from app.services.gigachat_service import gigachat_service


class ForecastService:
    """Service for sales forecast generation and management."""

    def __init__(self):
        """Initialize forecast service."""
        app_logger.info("ForecastService initialized")

    def _convert_gigachat_predictions_to_results(
        self,
        predictions: List[Dict[str, Any]]
    ) -> List[ForecastResult]:
        """Convert GigaChat predictions to ForecastResult objects.

        Args:
            predictions: List of prediction dictionaries from GigaChat

        Returns:
            List of ForecastResult objects
        """
        results = []

        for pred in predictions:
            try:
                # Parse date
                if isinstance(pred.get('date'), str):
                    date = datetime.strptime(pred['date'], '%Y-%m-%d').date()
                else:
                    date_value = pred.get('date', datetime.now())
                    if hasattr(date_value, 'date'):
                        date = date_value.date()
                    else:
                        date = datetime.now().date()

                result = ForecastResult(
                    date=date,
                    predicted_sales=int(pred.get('predicted_units', 0)),
                    confidence=float(pred.get('confidence', 0.8))
                )
                results.append(result)

            except (ValueError, TypeError, KeyError) as e:
                app_logger.warning(f"Error parsing prediction: {pred}, error: {e}")
                continue

        return results

    async def generate_forecast(self, request: ForecastRequest) -> ForecastResponse:
        """Generate sales forecast for a specific SKU.

        Args:
            request: Forecast request parameters

        Returns:
            Complete forecast response with predictions
        """
        app_logger.info(f"Generating forecast for SKU: {request.sku_id}, period: {request.period}")

        try:
            # Get historical sales data
            historical_data = supabase_client.get_sales_data(
                sku_id=request.sku_id,
                limit=52  # Get up to 52 weeks of data
            )

            if not historical_data:
                app_logger.warning(f"No historical data found for SKU: {request.sku_id}")

            # Generate forecast using GigaChat
            forecast_period = int(request.period.value)
            gigachat_response = await gigachat_service.generate_forecast(
                sku_id=request.sku_id,
                historical_data=historical_data,
                forecast_period=forecast_period,
                context=request.context
            )

            # Convert predictions to ForecastResult objects
            predictions = self._convert_gigachat_predictions_to_results(
                gigachat_response.predictions
            )

            if not predictions:
                app_logger.error("No valid predictions generated")
                raise ValueError("Failed to generate valid predictions")

            # Calculate totals and averages
            total_predicted_sales = sum(pred.predicted_sales for pred in predictions)
            average_confidence = sum(pred.confidence for pred in predictions) / len(predictions)

            # Create forecast response
            forecast_response = ForecastResponse(
                sku_id=request.sku_id,
                forecast_period=forecast_period,
                predictions=predictions,
                total_predicted_sales=total_predicted_sales,
                average_confidence=average_confidence,
                model_explanation=gigachat_response.explanation
            )

            # Save forecast to database
            # Convert predictions to JSON-serializable format
            predictions_json = []
            for pred in predictions:
                pred_dict = pred.dict()
                if 'date' in pred_dict:
                    pred_dict['date'] = pred_dict['date'].isoformat() if hasattr(pred_dict['date'], 'isoformat') else str(pred_dict['date'])
                predictions_json.append(pred_dict)

            forecast_data = {
                'sku_id': request.sku_id,
                'forecast_period': forecast_period,
                'predictions': json.dumps(predictions_json),
                'total_predicted_sales': total_predicted_sales,
                'average_confidence': average_confidence,
                'model_explanation': gigachat_response.explanation
            }

            forecast_id = supabase_client.insert_forecast(forecast_data)
            app_logger.info(f"Forecast saved with ID: {forecast_id}")

            return forecast_response

        except Exception as e:
            app_logger.error(f"Error generating forecast: {e}")

            # Return fallback forecast
            return self._generate_fallback_forecast(request)

    def _generate_fallback_forecast(self, request: ForecastRequest) -> ForecastResponse:
        """Generate a simple fallback forecast when main generation fails.

        Args:
            request: Original forecast request

        Returns:
            Basic forecast response
        """
        app_logger.info("Generating fallback forecast")

        forecast_period = int(request.period.value)
        predictions = []

        # Generate simple predictions based on minimal assumptions
        base_units = 3
        base_revenue = 9000.0

        # Start from tomorrow
        base_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)

        for i in range(forecast_period):
            prediction_date = base_date + timedelta(days=i)

            # Simple variation
            variation = 0.8 + (i % 3) * 0.15

            prediction = ForecastResult(
                date=prediction_date.date(),
                predicted_sales=max(1, int(base_units * variation)),
                confidence=0.6  # Lower confidence for fallback
            )
            predictions.append(prediction)

        # Calculate totals
        total_predicted_sales = sum(pred.predicted_sales for pred in predictions)
        average_confidence = 0.6

        return ForecastResponse(
            sku_id=request.sku_id,
            forecast_period=forecast_period,
            predictions=predictions,
            total_predicted_sales=total_predicted_sales,
            average_confidence=average_confidence,
            model_explanation="Базовый прогноз сгенерирован системой (основная модель недоступна)"
        )

    def get_forecast_history(self, sku_id: str, limit: int = 10) -> ForecastHistoryResponse:
        """Get forecast history for a specific SKU.

        Args:
            sku_id: SKU identifier
            limit: Maximum number of forecasts to return

        Returns:
            Forecast history response
        """
        app_logger.info(f"Retrieving forecast history for SKU: {sku_id}")

        try:
            # Get forecast history from database
            history_data = supabase_client.get_forecast_history(sku_id, limit)

            # Convert to ForecastHistoryItem objects
            forecasts = []
            for item in history_data:
                forecast_item = ForecastHistoryItem(
                    id=item['id'],
                    sku_id=item['sku_id'],
                    forecast_period=item['forecast_period'],
                    generated_at=item['generated_at'],
                    total_predicted_units=item['total_predicted_units'],
                    total_predicted_revenue=item['total_predicted_revenue'],
                    average_confidence=item['average_confidence'],
                    model_explanation=item.get('model_explanation')
                )
                forecasts.append(forecast_item)

            return ForecastHistoryResponse(
                sku_id=sku_id,
                forecasts=forecasts,
                total_count=len(forecasts)
            )

        except Exception as e:
            app_logger.error(f"Error retrieving forecast history: {e}")

            # Return empty history
            return ForecastHistoryResponse(
                sku_id=sku_id,
                forecasts=[],
                total_count=0
            )

    def get_sales_data(self, sku_id: str, limit: int = 52) -> Dict[str, Any]:
        """Get sales data for a specific SKU.

        Args:
            sku_id: SKU identifier
            limit: Maximum number of records to return

        Returns:
            Sales data response
        """
        app_logger.info(f"Retrieving sales data for SKU: {sku_id}")

        try:
            # Get sales data from database
            sales_data = supabase_client.get_sales_data(sku_id, limit)

            return {
                'sku_id': sku_id,
                'data': sales_data,
                'total_records': len(sales_data)
            }

        except Exception as e:
            app_logger.error(f"Error retrieving sales data: {e}")

            # Return empty data
            return {
                'sku_id': sku_id,
                'data': [],
                'total_records': 0
            }


# Global instance
forecast_service = ForecastService()
