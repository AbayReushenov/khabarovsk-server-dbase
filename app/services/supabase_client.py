"""Supabase client for database operations.

This module provides a connection to Supabase PostgreSQL database
using psycopg2 for direct SQL operations.
"""

import os
import psycopg2
import psycopg2.extras
from contextlib import contextmanager
from typing import List, Dict, Any, Optional
from urllib.parse import urlparse

from app.utils.logger import app_logger


class SupabaseClient:
    """Client for Supabase PostgreSQL database operations."""

    def __init__(self):
        """Initialize Supabase client with connection parameters."""
        self.test_mode = os.getenv("ENVIRONMENT") == "test" or os.getenv("SUPABASE_URL") == "dummy_url"

        if self.test_mode:
            app_logger.info("SupabaseClient initialized in test mode")
            self.database_url = "dummy_url"
            self.connection_params = {}
        else:
            self.database_url = os.getenv("DATABASE_URL") or self._build_database_url()
            self.connection_params = self._parse_database_url(self.database_url)
            app_logger.info("SupabaseClient initialized")

    def _build_database_url(self) -> str:
        """Build database URL from Supabase environment variables."""
        supabase_url = os.getenv("SUPABASE_URL", "")
        service_key = os.getenv("SUPABASE_SERVICE_KEY", "")

        if not supabase_url:
            raise ValueError("SUPABASE_URL environment variable is required")
        if not service_key:
            raise ValueError("SUPABASE_SERVICE_KEY environment variable is required")

        # Extract host from Supabase URL
        parsed = urlparse(supabase_url)
        project_ref = parsed.hostname.split('.')[0]

        # Build PostgreSQL connection string for Supabase
        return f"postgresql://postgres:{service_key}@db.{project_ref}.supabase.co:5432/postgres"

    def _parse_database_url(self, url: str) -> Dict[str, str]:
        """Parse database URL into connection parameters."""
        parsed = urlparse(url)
        return {
            "host": parsed.hostname,
            "port": parsed.port or 5432,
            "database": parsed.path.lstrip("/") or "postgres",
            "user": parsed.username,
            "password": parsed.password,
        }

    @contextmanager
    def get_connection(self):
        """Get database connection with automatic cleanup."""
        if self.test_mode:
            # In test mode, yield a mock connection
            from unittest.mock import MagicMock
            mock_conn = MagicMock()
            yield mock_conn
            return

        conn = None
        try:
            conn = psycopg2.connect(**self.connection_params)
            yield conn
        except Exception as e:
            app_logger.error(f"Database connection error: {e}")
            if conn:
                conn.rollback()
            raise
        finally:
            if conn:
                conn.close()

    def execute_query(
        self,
        query: str,
        params: Optional[tuple] = None,
        fetch: bool = True
    ) -> List[Dict[str, Any]]:
        """Execute a SQL query and return results.

        Args:
            query: SQL query string
            params: Query parameters
            fetch: Whether to fetch results

        Returns:
            List of dictionaries representing query results
        """
        if self.test_mode:
            # Return mock data for tests
            if fetch and "SELECT 1" in query:
                return [{'?column?': 1}]
            return []

        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
                cursor.execute(query, params)
                if fetch:
                    results = cursor.fetchall()
                    return [dict(row) for row in results]
                else:
                    conn.commit()
                    return []

    def insert_sales_data(self, sales_data: List[Dict[str, Any]]) -> int:
        """Insert sales data into the sales_data table.

        Args:
            sales_data: List of sales data dictionaries

        Returns:
            Number of rows inserted
        """
        if not sales_data:
            return 0

        if self.test_mode:
            # Return mock data for tests
            app_logger.info(f"Mock: Inserted/updated {len(sales_data)} rows into sales_data")
            return len(sales_data)

        insert_query = """
        INSERT INTO sales_data (sku_id, date, units_sold, revenue, weather_temp, season)
        VALUES (%(sku_id)s, %(date)s, %(units_sold)s, %(revenue)s, %(weather_temp)s, %(season)s)
        ON CONFLICT (sku_id, date) DO UPDATE SET
            units_sold = EXCLUDED.units_sold,
            revenue = EXCLUDED.revenue,
            weather_temp = EXCLUDED.weather_temp,
            season = EXCLUDED.season,
            updated_at = CURRENT_TIMESTAMP
        """

        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.executemany(insert_query, sales_data)
                conn.commit()
                rows_affected = cursor.rowcount

        app_logger.info(f"Inserted/updated {rows_affected} rows into sales_data")
        return rows_affected

    def get_sales_data(self, sku_id: str, limit: int = 52) -> List[Dict[str, Any]]:
        """Get sales data for a specific SKU.

        Args:
            sku_id: SKU identifier
            limit: Maximum number of records to return

        Returns:
            List of sales data records
        """
        query = """
        SELECT sku_id, date, units_sold, revenue, weather_temp, season, created_at, updated_at
        FROM sales_data
        WHERE sku_id = %s
        ORDER BY date DESC
        LIMIT %s
        """

        results = self.execute_query(query, (sku_id, limit))
        app_logger.info(f"Retrieved {len(results)} sales records for SKU {sku_id}")
        return results

    def insert_forecast(self, forecast_data: Dict[str, Any]) -> int:
        """Insert forecast data into the forecasts table.

        Args:
            forecast_data: Forecast data dictionary

        Returns:
            Forecast ID
        """
        insert_query = """
        INSERT INTO forecasts (sku_id, forecast_period, predictions, total_predicted_units,
                             total_predicted_revenue, average_confidence, model_explanation)
        VALUES (%(sku_id)s, %(forecast_period)s, %(predictions)s, %(total_predicted_units)s,
                %(total_predicted_revenue)s, %(average_confidence)s, %(model_explanation)s)
        RETURNING id
        """

        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(insert_query, forecast_data)
                forecast_id = cursor.fetchone()[0]
                conn.commit()

        app_logger.info(f"Inserted forecast with ID {forecast_id} for SKU {forecast_data['sku_id']}")
        return forecast_id

    def get_forecast_history(self, sku_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get forecast history for a specific SKU.

        Args:
            sku_id: SKU identifier
            limit: Maximum number of forecasts to return

        Returns:
            List of forecast records
        """
        query = """
        SELECT id, sku_id, forecast_period, generated_at, total_predicted_units,
               total_predicted_revenue, average_confidence, model_explanation
        FROM forecasts
        WHERE sku_id = %s
        ORDER BY generated_at DESC
        LIMIT %s
        """

        results = self.execute_query(query, (sku_id, limit))
        app_logger.info(f"Retrieved {len(results)} forecast records for SKU {sku_id}")
        return results


# Global instance
supabase_client = SupabaseClient()
