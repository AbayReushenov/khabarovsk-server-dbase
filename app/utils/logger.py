"""Logger utility module for the application.

This module provides a centralized logging configuration for the entire application.
It sets up structured logging with appropriate levels and formatting.
"""

import logging
import sys
import os
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
    # Отключаем все логи: уровень выше CRITICAL и удаляем обработчики
    logger.setLevel(logging.CRITICAL + 1)
    logger.propagate = False
    # Удаляем все обработчики
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    return logger


# Default application logger (level can be overridden via LOG_LEVEL env var)
DEFAULT_LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

app_logger = setup_logger("habarovsk_forecast_buddy", level=DEFAULT_LOG_LEVEL)
