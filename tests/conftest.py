"""Pytest configuration and fixtures.

This module contains pytest fixtures and configuration for testing
the Habarovsk Forecast Buddy API.
"""

import os
import sys
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Set up test environment variables."""
    # Set test environment variables
    os.environ["ENVIRONMENT"] = "test"
    os.environ["SUPABASE_URL"] = "dummy_url"
    os.environ["SUPABASE_SERVICE_KEY"] = "dummy_key"
    os.environ["GIGACHAT_CREDENTIALS"] = ""
    os.environ["DATABASE_URL"] = "dummy_db_url"

    yield

    # Cleanup after tests
    for var in ["ENVIRONMENT", "SUPABASE_URL", "SUPABASE_SERVICE_KEY",
                "GIGACHAT_CREDENTIALS", "DATABASE_URL"]:
        os.environ.pop(var, None)


@pytest.fixture
def client():
    """Create test client."""
    from app.main import app
    return TestClient(app)


@pytest.fixture
def mock_supabase_client():
    """Mock Supabase client for testing."""
    with patch('app.services.supabase_client.supabase_client') as mock:
        mock.execute_query.return_value = [{'?column?': 1}]
        mock.insert_sales_data.return_value = 1
        mock.get_sales_data.return_value = []
        mock.insert_forecast.return_value = 1
        mock.get_forecast_history.return_value = []
        yield mock


@pytest.fixture
def mock_csv_service():
    """Mock CSV service for testing."""
    with patch('app.services.csv_service.csv_service') as mock:
        mock.validate_and_parse_csv.return_value = ([], [], 0)
        mock.generate_sample_csv.return_value = "sku_id,date,units_sold,revenue\nTEST,2024-01-01,1,100"
        yield mock


@pytest.fixture
def mock_forecast_service():
    """Mock forecast service for testing."""
    with patch('app.services.forecast_service.forecast_service') as mock:
        mock_response = MagicMock()
        mock_response.sku_id = "TEST_SKU"
        mock_response.forecast_period = 7
        mock_response.predictions = []
        mock_response.total_predicted_units = 10
        mock_response.total_predicted_revenue = 30000.0
        mock_response.average_confidence = 0.8
        mock_response.model_explanation = "Test forecast"

        mock.generate_forecast.return_value = mock_response
        mock.get_sales_data.return_value = {
            'sku_id': 'TEST_SKU',
            'data': [],
            'total_records': 0
        }

        mock_history = MagicMock()
        mock_history.sku_id = "TEST_SKU"
        mock_history.forecasts = []
        mock_history.total_count = 0
        mock.get_forecast_history.return_value = mock_history

        yield mock


@pytest.fixture
def sample_csv_data():
    """Sample CSV data for testing."""
    return """sku_id,date,units_sold,revenue,weather_temp,season
DOWN_JACKET_001,2024-01-15,5,15000.00,-15.5,winter
DOWN_JACKET_002,2024-01-16,3,9500.00,-12.0,winter
DOWN_JACKET_001,2024-01-17,7,21000.00,-18.2,winter"""


@pytest.fixture
def sample_forecast_request():
    """Sample forecast request data."""
    return {
        "sku_id": "DOWN_JACKET_001",
        "period": "7",
        "context": "Cold weather expected next week"
    }
