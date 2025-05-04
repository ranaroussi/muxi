# =============================================================================
# FRONTMATTER
# =============================================================================
# Title:        Logging Configuration - Framework Logging Setup
# Description:  Unified logging configuration for the Muxi Framework
# Role:         Provides standardized logging setup across the framework
# Usage:        Imported and called during framework initialization
# Author:       Muxi Framework Team
#
# The Logging Configuration module provides a centralized system for configuring
# logging throughout the Muxi Framework. It uses a Pydantic model to define
# logging settings and offers a convenient setup function for initializing
# the logging system.
#
# Key features include:
#
# 1. Configuration Settings
#    - Log level control (DEBUG, INFO, WARNING, ERROR)
#    - Customizable formatting
#    - File and console output options
#
# 2. Log File Management
#    - Log rotation by size
#    - Retention policies
#    - Compression options
#
# 3. Easy Integration
#    - Environment variable configuration
#    - One-line setup function
#
# Example usage:
#
#   from muxi.core.config import configure_logging
#
#   # Set up logging with configured settings
#   configure_logging()
# =============================================================================

import os
from typing import Optional

from pydantic import BaseModel, Field


class LoggingConfig(BaseModel):
    """
    Logging configuration settings for the Muxi Framework.

    This class defines logging behavior using Pydantic for validation and
    type safety. Settings include log levels, formatting options, and file
    handling parameters, all of which can be configured via environment
    variables.
    """

    level: str = Field(
        default_factory=lambda: os.getenv("LOG_LEVEL", "INFO"),
        description="Minimum log level to display (DEBUG, INFO, WARNING, ERROR, CRITICAL)",
    )

    file: Optional[str] = Field(
        default_factory=lambda: os.getenv("LOG_FILE"),
        description="Path to log file (if None, only console logging is enabled)",
    )

    format: str = Field(
        default_factory=lambda: os.getenv(
            "LOG_FORMAT",
            "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
            "<level>{message}</level>",
        ),
        description="Log message format using loguru formatting syntax",
    )

    rotation: str = Field(
        default_factory=lambda: os.getenv("LOG_ROTATION", "10 MB"),
        description="When to rotate logs (e.g., '10 MB', '1 day', '1 week')",
    )

    retention: str = Field(
        default_factory=lambda: os.getenv("LOG_RETENTION", "1 week"),
        description="How long to keep log files (e.g., '1 week', '1 month')",
    )

    compression: str = Field(
        default_factory=lambda: os.getenv("LOG_COMPRESSION", "zip"),
        description="Compression format for rotated logs (e.g., 'zip', 'gz')",
    )


# Create a global logging config instance for easy imports
logging_config = LoggingConfig()


def configure_logging():
    """
    Configure the logging system based on the current configuration settings.

    This function sets up the logging system using the loguru library according
    to the settings in the LoggingConfig instance. It:

    1. Removes the default handler to start with a clean slate
    2. Adds a console handler with the configured format and level
    3. Optionally adds a file handler if a log file is specified
    4. Creates directories for log files if they don't exist

    Usage:
        from muxi.core.config import configure_logging
        configure_logging()  # Call early in the application startup
    """
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
