"""Tests for API endpoints.

This module contains tests for the main API functionality including
CSV upload, forecast generation, and data retrieval.
"""

import pytest
import io
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
import csv
from datetime import datetime

from app.main import app
from app.models.schemas import GigaChatResponse

# The client fixture is defined in conftest.py and available automatically
# @pytest.fixture
# def client():
#     """Create test client."""
#     return TestClient(app)


def load_sales_data_from_csv(file_path: str):
    """Load sales data from CSV for tests."""
    data = []
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            data.append({
                "id": reader.line_num - 1,
                "date": row["date"],
                "sku_id": row["sku_id"],
                "sales_quantity": int(row["sales_quantity"]),
                "avg_temp": float(row["avg_temp"]),
                "created_at": datetime.now().isoformat()
            })
    return data

class TestCSVUpload:
    """Tests for CSV upload functionality."""

    def test_upload_csv_success(self, client):
        """Test successful CSV upload."""
        # Create test CSV content
        csv_content = """sku_id,date,units_sold,revenue,weather_temp,season
DOWN_JACKET_001,2024-01-15,5,15000.00,-15.5,winter
DOWN_JACKET_002,2024-01-16,3,9500.00,-12.0,winter"""

        csv_file = io.BytesIO(csv_content.encode('utf-8'))

        with patch('app.services.csv_service.csv_service.validate_and_parse_csv') as mock_parse, \
             patch('app.services.supabase_client.supabase_client.insert_sales_data') as mock_insert:

            # Mock successful parsing
            mock_parse.return_value = ([
                {
                    'sku_id': 'DOWN_JACKET_001',
                    'date': '2024-01-15',
                    'units_sold': 5,
                    'revenue': 15000.00,
                    'weather_temp': -15.5,
                    'season': 'winter'
                }
            ], [], 2)

            # Mock successful database insert
            mock_insert.return_value = 1

            response = client.post(
                "/api/v1/upload-csv",
                files={"file": ("test.csv", csv_file, "text/csv")}
            )

            assert response.status_code == 200
            data = response.json()
            assert data["rows_processed"] == 1
            assert "Successfully processed" in data["message"]

    def test_upload_csv_invalid_file_type(self, client):
        """Test CSV upload with invalid file type."""
        txt_content = b"This is not a CSV file"
        txt_file = io.BytesIO(txt_content)

        response = client.post(
            "/api/v1/upload-csv",
            files={"file": ("test.txt", txt_file, "text/plain")}
        )

        assert response.status_code == 400
        assert "Only CSV files are allowed" in response.json()["detail"]

    def test_upload_csv_empty_file(self, client):
        """Test CSV upload with empty file."""
        empty_file = io.BytesIO(b"")

        response = client.post(
            "/api/v1/upload-csv",
            files={"file": ("empty.csv", empty_file, "text/csv")}
        )

        assert response.status_code == 400
        assert "File is empty" in response.json()["detail"]


class TestForecastGeneration:
    """Tests for forecast generation functionality."""

    def test_generate_forecast_with_csv_data(self, client):
        """Test forecast generation using data from a CSV file."""

        csv_path = 'mok-data/sales_data_minimal.csv'
        sales_data = load_sales_data_from_csv(csv_path)

        with patch('app.services.forecast_service.supabase_client.get_sales_data') as mock_get_sales_data, \
             patch('app.services.forecast_service.gigachat_service.generate_forecast') as mock_gigachat, \
             patch('app.services.forecast_service.supabase_client.insert_forecast') as mock_insert_forecast:

            mock_get_sales_data.return_value = sales_data

            mock_gigachat_response = GigaChatResponse(
                predictions=[
                    {"date": "2025-01-01", "predicted_units": 10, "confidence": 0.9},
                    {"date": "2025-01-02", "predicted_units": 12, "confidence": 0.85},
                ],
                explanation="Forecast based on historical data and trends.",
                confidence_scores=[0.9, 0.85]
            )
            mock_gigachat.return_value = mock_gigachat_response
            mock_insert_forecast.return_value = 123 # Dummy forecast ID

            request_payload = {
                "sku_id": "SKU_001",
                "period": "7",
                "context": "Regular week, no promotions."
            }

            response = client.post("/api/v1/forecast", json=request_payload)

            assert response.status_code == 200

            mock_get_sales_data.assert_called_once_with(sku_id="SKU_001", limit=52)
            mock_gigachat.assert_called_once()
            mock_insert_forecast.assert_called_once()

            data = response.json()
            assert data["success"] is True
            assert data["data"]["sku_id"] == "SKU_001"
            assert len(data["data"]["predictions"]) == 2
            assert data["data"]["predictions"][0]["predicted_sales"] == 10

    def test_generate_forecast_success(self, client):
        """Test successful forecast generation."""
        with patch('app.services.forecast_service.forecast_service.generate_forecast') as mock_forecast:
            # Mock successful forecast response
            mock_forecast.return_value = MagicMock(
                sku_id="DOWN_JACKET_001",
                forecast_period=7,
                predictions=[],
                total_predicted_units=35,
                total_predicted_revenue=105000.0,
                average_confidence=0.85,
                model_explanation="Test forecast"
            )

            response = client.post(
                "/api/v1/forecast",
                json={
                    "sku_id": "DOWN_JACKET_001",
                    "period": "7",
                    "context": "Cold weather expected"
                }
            )

            assert response.status_code == 200
            mock_forecast.assert_called_once()

    def test_generate_forecast_invalid_period(self, client):
        """Test forecast generation with invalid period."""
        response = client.post(
            "/api/v1/forecast",
            json={
                "sku_id": "DOWN_JACKET_001",
                "period": "invalid",
                "context": "Test context"
            }
        )

        assert response.status_code == 422  # Validation error

    def test_generate_forecast_missing_sku(self, client):
        """Test forecast generation with missing sku."""
        response = client.post(
            "/api/v1/forecast",
            json={
                "period": "7",
                "context": "Test context"
            }
        )

        assert response.status_code == 422  # Validation error


class TestDataRetrieval:
    """Tests for data retrieval functionality."""

    def test_get_sales_data_success(self, client):
        """Test successful sales data retrieval."""
        with patch('app.api.endpoints.supabase_client.get_sales_data') as mock_get_data:
            # Mock successful data response
            mock_get_data.return_value = [{
                'id': 1,
                'sku_id': 'DOWN_JACKET_001',
                'date': '2024-01-15',
                'sales_quantity': 5,
                'avg_temp': -15.5,
                'created_at': '2024-01-15T10:00:00'
            }]

            response = client.get("/api/v1/data/DOWN_JACKET_001")

            assert response.status_code == 200
            data = response.json()
            assert data["sku_id"] == "DOWN_JACKET_001"
            assert data["total_records"] == 1

    def test_get_sales_data_with_limit(self, client):
        """Test sales data retrieval with custom limit."""
        with patch('app.api.endpoints.supabase_client.get_sales_data') as mock_get_data:
            mock_get_data.return_value = []

            response = client.get("/api/v1/data/DOWN_JACKET_001?limit=10")

            assert response.status_code == 200
            mock_get_data.assert_called_once_with("DOWN_JACKET_001", 10)

    def test_get_forecast_history_success(self, client):
        """Test successful forecast history retrieval."""
        with patch('app.api.endpoints.supabase_client.get_forecast_history') as mock_get_history:
            # Mock successful history response
            mock_get_history.return_value = []

            response = client.get("/api/v1/forecast-history/DOWN_JACKET_001")

            assert response.status_code == 200
            data = response.json()
            assert data["sku_id"] == "DOWN_JACKET_001"


class TestUtilityEndpoints:
    """Tests for utility endpoints."""

    def test_download_sample_csv(self, client):
        """Test sample CSV download."""
        response = client.get("/api/v1/sample-csv")

        assert response.status_code == 200
        assert response.headers["content-type"] == "text/csv; charset=utf-8"
        assert "attachment" in response.headers["content-disposition"]

        # Check CSV content
        content = response.content.decode('utf-8')
        assert "sku_id" in content
        assert "DOWN_JACKET_001" in content


class TestErrorHandling:
    """Tests for error handling."""

    def test_404_endpoint(self, client):
        """Test 404 error for non-existent endpoint."""
        response = client.get("/api/v1/nonexistent")
        assert response.status_code == 404

    def test_invalid_json_format(self, client):
        """Test handling of invalid JSON in request body."""
        response = client.post(
            "/api/v1/forecast",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )

        assert response.status_code == 422
