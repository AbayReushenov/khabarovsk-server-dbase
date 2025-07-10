"""API endpoints for the Habarovsk Forecast Buddy application.

This module defines all the REST API endpoints for CSV upload,
forecast generation, data retrieval, and health checks.
"""

from datetime import datetime
from typing import List
from fastapi import APIRouter, HTTPException, UploadFile, File, Depends, Query
from fastapi.responses import Response

from app.utils.logger import app_logger
from app.models.schemas import (
    HealthResponse, CSVUploadResponse, ForecastRequest, ForecastResponse,
    ForecastHistoryResponse, SalesDataResponse, ErrorResponse
)
from app.services.csv_service import csv_service
from app.services.supabase_client import supabase_client
from app.services.forecast_service import forecast_service


# Create router instance
router = APIRouter()


@router.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Health check endpoint for monitoring and deployment.

    Returns:
        Health status information
    """
    app_logger.info("Health check requested")

    try:
        # Test database connection
        supabase_client.execute_query("SELECT 1", fetch=True)

        return HealthResponse(
            status="healthy",
            timestamp=datetime.utcnow(),
            version="1.0.0"
        )
    except Exception as e:
        app_logger.error(f"Health check failed: {e}")
        raise HTTPException(
            status_code=503,
            detail="Service unavailable - database connection failed"
        )


@router.post("/upload-csv", response_model=CSVUploadResponse, tags=["Data"])
async def upload_csv(file: UploadFile = File(...)):
    """Upload and process CSV file with sales data.

    Args:
        file: CSV file containing sales data

    Returns:
        Upload processing results

    Raises:
        HTTPException: If file processing fails
    """
    app_logger.info(f"CSV upload requested: {file.filename}")

    # Validate file type
    if not file.filename.lower().endswith('.csv'):
        raise HTTPException(
            status_code=400,
            detail="Only CSV files are allowed"
        )

    # Validate file size (10MB limit)
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

    try:
        # Read file content
        file_content = await file.read()

        if len(file_content) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=413,
                detail="File too large. Maximum size is 10MB"
            )

        if len(file_content) == 0:
            raise HTTPException(
                status_code=400,
                detail="File is empty"
            )

        # Process CSV
        parsed_data, errors, total_rows = csv_service.validate_and_parse_csv(
            file_content, file.filename
        )

        if errors and not parsed_data:
            raise HTTPException(
                status_code=400,
                detail=f"CSV processing failed: {'; '.join(errors[:5])}"
            )

        # Insert data into database
        rows_inserted = 0
        if parsed_data:
            rows_inserted = supabase_client.insert_sales_data(parsed_data)

        # Prepare response message
        message = f"Successfully processed {rows_inserted} rows"
        if errors:
            message += f" with {len(errors)} warnings"

        app_logger.info(f"CSV upload completed: {rows_inserted} rows inserted, {len(errors)} errors")

        return CSVUploadResponse(
            message=message,
            rows_processed=rows_inserted,
            timestamp=datetime.utcnow()
        )

    except HTTPException:
        raise
    except Exception as e:
        app_logger.error(f"Unexpected error processing CSV: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error during file processing"
        )


@router.post("/forecast", response_model=ForecastResponse, tags=["Forecasting"])
async def generate_forecast(request: ForecastRequest):
    """Generate sales forecast for a specific SKU.

    Args:
        request: Forecast generation parameters

    Returns:
        Generated forecast with predictions

    Raises:
        HTTPException: If forecast generation fails
    """
    app_logger.info(f"Forecast request for SKU: {request.sku_id}, period: {request.period}")

    try:
        # Generate forecast using forecast service
        forecast_response = await forecast_service.generate_forecast(request)

        app_logger.info(f"Forecast generated successfully for SKU: {request.sku_id}")
        return forecast_response

    except Exception as e:
        app_logger.error(f"Error generating forecast: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to generate forecast. Please try again later."
        )


@router.get("/data/{sku_id}", response_model=SalesDataResponse, tags=["Data"])
async def get_sales_data(
    sku_id: str,
    limit: int = Query(52, ge=1, le=200, description="Number of records to return")
):
    """Retrieve sales data for a specific SKU.

    Args:
        sku_id: SKU identifier
        limit: Maximum number of records to return (1-200)

    Returns:
        Historical sales data

    Raises:
        HTTPException: If data retrieval fails
    """
    app_logger.info(f"Sales data request for SKU: {sku_id}, limit: {limit}")

    try:
        # Get sales data using forecast service
        data_response = forecast_service.get_sales_data(sku_id, limit)

        if data_response['total_records'] == 0:
            app_logger.warning(f"No sales data found for SKU: {sku_id}")

        return SalesDataResponse(
            sku_id=sku_id,
            data=data_response['data'],
            total_records=data_response['total_records']
        )

    except Exception as e:
        app_logger.error(f"Error retrieving sales data: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve sales data"
        )


@router.get("/forecast-history/{sku_id}", response_model=ForecastHistoryResponse, tags=["Forecasting"])
async def get_forecast_history(
    sku_id: str,
    limit: int = Query(10, ge=1, le=50, description="Number of forecasts to return")
):
    """Retrieve forecast history for a specific SKU.

    Args:
        sku_id: SKU identifier
        limit: Maximum number of forecasts to return (1-50)

    Returns:
        Historical forecast data

    Raises:
        HTTPException: If data retrieval fails
    """
    app_logger.info(f"Forecast history request for SKU: {sku_id}, limit: {limit}")

    try:
        # Get forecast history using forecast service
        history_response = forecast_service.get_forecast_history(sku_id, limit)

        if history_response.total_count == 0:
            app_logger.warning(f"No forecast history found for SKU: {sku_id}")

        return history_response

    except Exception as e:
        app_logger.error(f"Error retrieving forecast history: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve forecast history"
        )


@router.get("/sample-csv", tags=["Data"])
async def download_sample_csv():
    """Download sample CSV file for reference.

    Returns:
        CSV file with sample data format
    """
    app_logger.info("Sample CSV download requested")

    try:
        # Generate sample CSV content
        csv_content = csv_service.generate_sample_csv()

        return Response(
            content=csv_content,
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=sample_sales_data.csv"}
        )

    except Exception as e:
        app_logger.error(f"Error generating sample CSV: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to generate sample CSV"
        )


# Error handlers are now handled in main.py at the FastAPI app level
