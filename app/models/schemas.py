"""Minimal Pydantic models for testing"""

from datetime import datetime, date
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict
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
    id: Optional[int] = None
    sku_id: str
    date: date
    sales_quantity: int
    avg_temp: Optional[float] = None
    created_at: Optional[datetime] = None


class SalesDataResponse(BaseModel):
    """Response model for sales data retrieval."""
    sku_id: str
    data: List[SalesDataRow]
    total_records: int


class ForecastRequest(BaseModel):
    """Request model for forecast generation."""
    sku_id: str
    period: ForecastPeriod
    context: Optional[str] = None


class ForecastResult(BaseModel):
    """Individual forecast result for a specific date."""
    date: date
    predicted_sales: int
    confidence: float
    predicted_temp: Optional[float] = None  # New: forecasted average temperature


class ForecastResponse(BaseModel):
    """Response model for forecast generation."""
    model_config = ConfigDict(protected_namespaces=())

    sku_id: str
    forecast_period: int
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    predictions: List[ForecastResult]
    total_predicted_sales: int
    average_confidence: float
    model_explanation: Optional[str] = None
    generated_by_gigachat: bool = True  # True if main GigaChat model used, False if fallback/mock


class ForecastHistoryItem(BaseModel):
    """Model for historical forecast item."""
    id: int
    sku_id: str
    forecast_date: date
    predicted_sales: int
    confidence_score: Optional[float]
    key_factors: Optional[List[str]]
    created_at: datetime


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
    predictions: List[dict]
    explanation: str
    confidence_scores: List[float]
