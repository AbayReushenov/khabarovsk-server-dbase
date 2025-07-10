"""Supabase client for database operations via REST API.

This module provides a connection to Supabase database using REST API
instead of direct PostgreSQL connection due to pooler issues.
"""

import os
import requests
from typing import List, Dict, Any, Optional
from datetime import datetime, date
import json

from app.utils.logger import app_logger


class SupabaseClient:
    """Client for Supabase database operations via REST API."""

    def __init__(self):
        """Initialize Supabase REST API client."""
        self.test_mode = os.getenv("ENVIRONMENT") == "test" or os.getenv("SUPABASE_URL") == "dummy_url"

        if self.test_mode:
            app_logger.info("SupabaseClient initialized in test mode")
            self.base_url = "dummy_url"
            self.anon_key = "dummy_key"
            self.service_key = "dummy_service_key"
        else:
            self.base_url = os.getenv("SUPABASE_URL", "").rstrip('/')
            self.anon_key = os.getenv("SUPABASE_ANON_KEY", "")
            self.service_key = os.getenv("SUPABASE_SERVICE_KEY", "")

            if not self.base_url:
                raise ValueError("SUPABASE_URL environment variable is required")
            if not self.anon_key:
                raise ValueError("SUPABASE_ANON_KEY environment variable is required")

            self.rest_url = f"{self.base_url}/rest/v1"
            app_logger.info("SupabaseClient initialized for REST API")

    def _get_headers(self, use_service_key: bool = False) -> Dict[str, str]:
        """Get headers for REST API requests."""
        key = self.service_key if use_service_key and self.service_key else self.anon_key
        return {
            "apikey": key,
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json"
        }

    def _handle_response(self, response: requests.Response) -> List[Dict[str, Any]]:
        """Handle REST API response."""
        if response.status_code >= 400:
            error_msg = f"API error {response.status_code}: {response.text}"
            app_logger.error(error_msg)
            raise Exception(error_msg)

        if response.text.strip():
            return response.json() if isinstance(response.json(), list) else [response.json()]
        return []

    def health_check(self) -> bool:
        """Check if Supabase REST API is accessible."""
        if self.test_mode:
            return True

        try:
            response = requests.get(
                f"{self.rest_url}/sales_data?limit=1",
                headers=self._get_headers(),
                timeout=10
            )
            return response.status_code < 400
        except Exception as e:
            app_logger.error(f"Health check failed: {e}")
            return False

    def insert_sales_data(self, sales_data: List[Dict[str, Any]]) -> int:
        """Insert sales data into the sales_data table via REST API.

        Args:
            sales_data: List of sales data dictionaries

        Returns:
            Number of rows inserted
        """
        if not sales_data:
            return 0

        if self.test_mode:
            app_logger.info(f"Mock: Inserted {len(sales_data)} rows into sales_data")
            return len(sales_data)

        try:
            # Convert data to match database schema
            formatted_data = []
            for row in sales_data:
                formatted_row = {
                    "sku_id": row.get("sku_id"),
                    "date": row.get("date").isoformat() if isinstance(row.get("date"), date) else row.get("date"),
                    "sales_quantity": row.get("sales_quantity", row.get("units_sold", 0)),
                    "avg_temp": row.get("avg_temp", row.get("weather_temp"))
                }
                formatted_data.append(formatted_row)

            response = requests.post(
                f"{self.rest_url}/sales_data",
                headers=self._get_headers(use_service_key=True),
                json=formatted_data,
                timeout=30
            )

            result = self._handle_response(response)
            rows_affected = len(result) if result else len(formatted_data)

            app_logger.info(f"Inserted {rows_affected} rows into sales_data via REST API")
            return rows_affected

        except Exception as e:
            app_logger.error(f"Error inserting sales data: {e}")
            raise

    def get_sales_data(self, sku_id: str, limit: int = 52) -> List[Dict[str, Any]]:
        """Get sales data for a specific SKU via REST API.

        Args:
            sku_id: SKU identifier
            limit: Maximum number of records to return

        Returns:
            List of sales data records
        """
        if self.test_mode:
            # Return mock data for tests
            return [{
                "id": 1,
                "sku_id": sku_id,
                "date": "2024-01-01",
                "sales_quantity": 100,
                "avg_temp": -15.0,
                "created_at": "2024-01-01T00:00:00"
            }]

        try:
            response = requests.get(
                f"{self.rest_url}/sales_data",
                headers=self._get_headers(),
                params={
                    "sku_id": f"eq.{sku_id}",
                    "order": "date.desc",
                    "limit": limit
                },
                timeout=10
            )

            results = self._handle_response(response)
            app_logger.info(f"Retrieved {len(results)} sales records for SKU {sku_id}")
            return results

        except Exception as e:
            app_logger.error(f"Error getting sales data: {e}")
            raise

    def insert_forecast(self, forecast_data: Dict[str, Any]) -> int:
        """Insert forecast data into the forecasts table via REST API.

        Args:
            forecast_data: Forecast data dictionary

        Returns:
            Forecast ID
        """
        if self.test_mode:
            app_logger.info(f"Mock: Inserted forecast for SKU {forecast_data.get('sku_id')}")
            return 1

        try:
            # Format data for database
            formatted_data = {
                "sku_id": forecast_data["sku_id"],
                "forecast_date": forecast_data["forecast_date"].isoformat() if isinstance(forecast_data["forecast_date"], date) else forecast_data["forecast_date"],
                "predicted_sales": forecast_data["predicted_sales"],
                "confidence_score": forecast_data.get("confidence_score"),
                "key_factors": forecast_data.get("key_factors", [])
            }

            response = requests.post(
                f"{self.rest_url}/forecasts",
                headers=self._get_headers(use_service_key=True),
                json=formatted_data,
                timeout=30
            )

            result = self._handle_response(response)
            forecast_id = result[0]["id"] if result and result[0].get("id") else 1

            app_logger.info(f"Inserted forecast with ID {forecast_id} for SKU {forecast_data['sku_id']}")
            return forecast_id

        except Exception as e:
            app_logger.error(f"Error inserting forecast: {e}")
            raise

    def get_forecast_history(self, sku_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get forecast history for a specific SKU via REST API.

        Args:
            sku_id: SKU identifier
            limit: Maximum number of forecasts to return

        Returns:
            List of forecast records
        """
        if self.test_mode:
            return [{
                "id": 1,
                "sku_id": sku_id,
                "forecast_date": "2024-01-01",
                "predicted_sales": 150,
                "confidence_score": 0.85,
                "key_factors": ["temperature", "season"],
                "created_at": "2024-01-01T00:00:00"
            }]

        try:
            response = requests.get(
                f"{self.rest_url}/forecasts",
                headers=self._get_headers(),
                params={
                    "sku_id": f"eq.{sku_id}",
                    "order": "created_at.desc",
                    "limit": limit
                },
                timeout=10
            )

            results = self._handle_response(response)
            app_logger.info(f"Retrieved {len(results)} forecast records for SKU {sku_id}")
            return results

        except Exception as e:
            app_logger.error(f"Error getting forecast history: {e}")
            raise

    def get_all_sku_ids(self) -> List[str]:
        """Get all unique SKU IDs from sales data."""
        if self.test_mode:
            return ["SKU_001", "SKU_002"]

        try:
            response = requests.get(
                f"{self.rest_url}/sales_data",
                headers=self._get_headers(),
                params={
                    "select": "sku_id",
                    "order": "sku_id.asc"
                },
                timeout=10
            )

            results = self._handle_response(response)
            sku_ids = list(set(row["sku_id"] for row in results if row.get("sku_id")))
            app_logger.info(f"Retrieved {len(sku_ids)} unique SKU IDs")
            return sorted(sku_ids)

        except Exception as e:
            app_logger.error(f"Error getting SKU IDs: {e}")
            return []


# Global instance
supabase_client = SupabaseClient()
