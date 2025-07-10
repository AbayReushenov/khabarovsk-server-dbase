"""Tests for health check endpoint.

This module contains unit tests for the health check functionality
to ensure the API is working correctly.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from app.main import app


client = TestClient(app)


def test_health_check_success():
    """Test successful health check."""
    with patch('app.services.supabase_client.supabase_client.execute_query') as mock_query:
        # Mock successful database connection
        mock_query.return_value = [{'?column?': 1}]

        response = client.get("/api/v1/health")

        assert response.status_code == 200
        data = response.json()

        assert data["status"] == "healthy"
        assert data["version"] == "1.0.0"
        assert "timestamp" in data

        # Verify database query was called
        mock_query.assert_called_once_with("SELECT 1", fetch=True)


def test_health_check_database_failure():
    """Test health check with database connection failure."""
    with patch('app.services.supabase_client.supabase_client.execute_query') as mock_query:
        # Mock database connection failure
        mock_query.side_effect = Exception("Database connection failed")

        response = client.get("/api/v1/health")

        assert response.status_code == 503
        data = response.json()

        assert "Service unavailable" in data["detail"]


def test_root_endpoint():
    """Test root endpoint returns API information."""
    response = client.get("/")

    assert response.status_code == 200
    data = response.json()

    assert data["name"] == "Habarovsk Forecast Buddy API"
    assert data["version"] == "1.0.0"
    assert data["status"] == "running"
    assert "/docs" in data["docs"]
    assert "/api/v1/health" in data["health"]


def test_docs_endpoint():
    """Test that API documentation is accessible."""
    response = client.get("/docs")

    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]


def test_redoc_endpoint():
    """Test that ReDoc documentation is accessible."""
    response = client.get("/redoc")

    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]


@pytest.mark.parametrize("invalid_endpoint", [
    "/api/v1/nonexistent",
    "/invalid",
    "/api/v2/health"
])
def test_invalid_endpoints(invalid_endpoint):
    """Test that invalid endpoints return 404."""
    response = client.get(invalid_endpoint)
    assert response.status_code == 404
