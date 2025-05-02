"""
Logging configuration for the MUXI Framework.

This module provides logging-related configuration settings.
"""

import os
from typing import Optional

from pydantic import BaseModel, Field


class LoggingConfig(BaseModel):
    """Logging configuration settings."""

    level: str = Field(default_factory=lambda: os.getenv("LOG_LEVEL", "INFO"))

    file: Optional[str] = Field(default_factory=lambda: os.getenv("LOG_FILE"))

    format: str = Field(
        default_factory=lambda: os.getenv(
            "LOG_FORMAT",
            "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
            "<level>{message}</level>",
        )
    )

    rotation: str = Field(default_factory=lambda: os.getenv("LOG_ROTATION", "10 MB"))

    retention: str = Field(default_factory=lambda: os.getenv("LOG_RETENTION", "1 week"))

    compression: str = Field(default_factory=lambda: os.getenv("LOG_COMPRESSION", "zip"))


# Create a global logging config instance
logging_config = LoggingConfig()


def configure_logging():
    """Configure logging based on the configuration."""
    import sys

    from loguru import logger

    # Remove default handler
    logger.remove()

    # Add console handler
    logger.add(sink=sys.stdout, level=logging_config.level, format=logging_config.format)

    # Add file handler if configured
    if logging_config.file:
        # Create directory if it doesn't exist
        log_dir = os.path.dirname(logging_config.file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)

        logger.add(
            sink=logging_config.file,
            level=logging_config.level,
            rotation=logging_config.rotation,
            retention=logging_config.retention,
            compression=logging_config.compression,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | "
            "{name}:{function}:{line} - {message}",
        )
