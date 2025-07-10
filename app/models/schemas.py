"""Pydantic models for data validation and serialization.

This module contains all the data models used throughout the application
for request/response validation, database interaction, and data transformation.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, field_validator, ConfigDict
from enum import Enum


class ForecastPeriod(str, Enum):
    """Enum for forecast period options."""
    WEEK = "7"
    TWO_WEEKS = "14"
    MONTH = "30"


class HealthResponse(BaseModel):
    """Health check response model."""
    status: str = "healthy"
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    version: str = "1.0.0"


class CSVUploadResponse(BaseModel):
    """Response model for CSV upload endpoint."""
    message: str
    rows_processed: int
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class SalesDataRow(BaseModel):
    """Model for a single sales data row."""
    sku_id: str = Field(..., description="SKU identifier")
    date: datetime = Field(..., description="Sales date")
    units_sold: int = Field(..., ge=0, description="Number of units sold")
    revenue: float = Field(..., ge=0, description="Revenue amount")
    weather_temp: Optional[float] = Field(None, description="Weather temperature")
    season: Optional[str] = Field(None, description="Season identifier")

    @field_validator('sku_id')
    @classmethod
    def validate_sku_id(cls, v):
        """Validate SKU ID format."""
        if not v or len(v.strip()) == 0:
            raise ValueError('SKU ID cannot be empty')
        return v.strip()


class SalesDataResponse(BaseModel):
    """Response model for sales data retrieval."""
    sku_id: str
    data: List[SalesDataRow]
    total_records: int


class ForecastRequest(BaseModel):
    """Request model for forecast generation."""
    sku_id: str = Field(..., description="SKU identifier to forecast")
    period: ForecastPeriod = Field(..., description="Forecast period (7, 14, or 30 days)")
    context: Optional[str] = Field(None, description="Additional context for forecast")


class ForecastResult(BaseModel):
    """Individual forecast result for a specific date."""
    date: datetime
    predicted_units: int = Field(..., ge=0)
    predicted_revenue: float = Field(..., ge=0)
    confidence: float = Field(..., ge=0, le=1, description="Confidence score 0-1")


class ForecastResponse(BaseModel):
    """Response model for forecast generation."""
    model_config = ConfigDict(protected_namespaces=())

    sku_id: str
    forecast_period: int
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    predictions: List[ForecastResult]
    total_predicted_units: int
    total_predicted_revenue: float
    average_confidence: float
    model_explanation: Optional[str] = None


class ForecastHistoryItem(BaseModel):
    """Model for historical forecast item."""
    model_config = ConfigDict(protected_namespaces=())

    id: int
    sku_id: str
    forecast_period: int
    generated_at: datetime
    total_predicted_units: int
    total_predicted_revenue: float
    average_confidence: float
    model_explanation: Optional[str] = None


class ForecastHistoryResponse(BaseModel):
    """Response model for forecast history."""
    sku_id: str
    forecasts: List[ForecastHistoryItem]
    total_count: int


class ErrorResponse(BaseModel):
    """Standard error response model."""
    error: str
    detail: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class GigaChatRequest(BaseModel):
    """Internal model for GigaChat API requests."""
    prompt: str
    max_tokens: int = 2000
    temperature: float = 0.1


class GigaChatResponse(BaseModel):
    """Internal model for GigaChat API responses."""
    predictions: List[Dict[str, Any]]
    explanation: str
    confidence_scores: List[float]
