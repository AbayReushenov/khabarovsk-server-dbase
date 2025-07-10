"""Main application module for Habarovsk Forecast Buddy.

This module initializes the FastAPI application with all necessary
configurations, middleware, and route handlers.
"""

import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

from app.utils.logger import app_logger
from app.api.endpoints import router
from app.models.schemas import ErrorResponse


# Load environment variables
load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context manager.

    Handles startup and shutdown events for the application.
    """
    # Startup
    app_logger.info("Starting Habarovsk Forecast Buddy API")

    # Test database connection on startup
    try:
        from app.services.supabase_client import supabase_client
        if supabase_client.health_check():
            app_logger.info("Database connection established")
        else:
            app_logger.warning("Database health check failed")
    except Exception as e:
        app_logger.error(f"Database connection failed: {e}")
        # Don't stop the app, but log the error

    # Test GigaChat service initialization
    try:
        from app.services.gigachat_service import gigachat_service
        app_logger.info(f"GigaChat service initialized (mock_mode: {gigachat_service.mock_mode})")
    except Exception as e:
        app_logger.error(f"GigaChat service initialization failed: {e}")

    yield

    # Shutdown
    app_logger.info("Shutting down Habarovsk Forecast Buddy API")


# Create FastAPI application
app = FastAPI(
    title="Habarovsk Forecast Buddy API",
    description="API for sales forecasting of down jackets in Khabarovsk using AI",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)


# Custom exception handler for validation errors
@app.exception_handler(422)
async def validation_exception_handler(request: Request, exc):
    """Handle Pydantic validation errors."""
    app_logger.warning(f"Validation error: {exc}")

    return JSONResponse(
        status_code=422,
        content=ErrorResponse(
            error="Validation Error",
            detail="Invalid request data. Please check your input.",
        ).dict()
    )


# Custom exception handler for general errors
@app.exception_handler(500)
async def internal_server_error_handler(request: Request, exc):
    """Handle internal server errors."""
    app_logger.error(f"Internal server error: {exc}")

    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="Internal Server Error",
            detail="An unexpected error occurred. Please try again later.",
        ).dict()
    )


# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log incoming HTTP requests."""
    start_time = time.time()

    # Log request
    app_logger.info(f"Request: {request.method} {request.url}")

    # Process request
    response = await call_next(request)

    # Log response
    process_time = time.time() - start_time
    app_logger.info(
        f"Response: {response.status_code} - "
        f"Processing time: {process_time:.3f}s"
    )

    return response


# Include API routes
app.include_router(router, prefix="/api/v1")


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information."""
    return {
        "name": "Habarovsk Forecast Buddy API",
        "version": "1.0.0",
        "description": "AI-powered sales forecasting for down jackets in Khabarovsk",
        "docs": "/docs",
        "health": "/api/v1/health",
        "status": "running"
    }


# Add import for time module
import time


if __name__ == "__main__":
    import uvicorn

    # Get configuration from environment
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))

    app_logger.info(f"Starting server on {host}:{port}")

    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=os.getenv("ENVIRONMENT") == "development",
        log_level="info"
    )
