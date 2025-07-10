"""Logger utility module for the application.

This module provides a centralized logging configuration for the entire application.
It sets up structured logging with appropriate levels and formatting.
"""

import logging
import sys
from typing import Optional


def setup_logger(
    name: str = __name__,
    level: str = "INFO",
    format_string: Optional[str] = None
) -> logging.Logger:
    """Set up and configure logger for the application.

    Args:
        name: Logger name, defaults to module name
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        format_string: Custom format string for log messages

    Returns:
        Configured logger instance
    """
    if format_string is None:
        format_string = (
            "%(asctime)s - %(name)s - %(levelname)s - "
            "[%(filename)s:%(lineno)d] - %(message)s"
        )

    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))

    # Avoid adding handlers multiple times
    if not logger.handlers:
        # Create console handler
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(getattr(logging, level.upper()))

        # Create formatter
        formatter = logging.Formatter(format_string)
        handler.setFormatter(formatter)

        # Add handler to logger
        logger.addHandler(handler)

    return logger


# Default application logger
app_logger = setup_logger("habarovsk_forecast_buddy")
