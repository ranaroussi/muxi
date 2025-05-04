# =============================================================================
# FRONTMATTER
# =============================================================================
# Title:        Database Configuration - Database Connection Settings
# Description:  Centralized database configuration for the Muxi Framework
# Role:         Provides database connection settings for the framework
# Usage:        Imported by components that need database access
# Author:       Muxi Framework Team
#
# The Database Configuration module provides centralized settings for database
# connections across the Muxi Framework. It uses a Pydantic model to ensure
# type safety and validation of configuration values.
#
# Key features include:
#
# 1. Connection Management
#    - Database URL configuration
#    - Connection pool settings
#    - Timeout and recycling parameters
#
# 2. Environment Integration
#    - Environment variable based configuration
#    - Sensible defaults for development
#
# All settings can be overridden via environment variables, allowing for
# easy configuration in different deployment environments without code changes.
#
# Example usage:
#
#   from muxi.core.config import database_config
#
#   # Access database configuration
#   connection_string = database_config.connection_string
#   pool_size = database_config.pool_size
# =============================================================================

import os

from pydantic import BaseModel, Field


class DatabaseConfig(BaseModel):
    """
    Database configuration settings for the Muxi Framework.

    This class defines database connection and pool settings using Pydantic
    for validation and type safety. All settings can be configured via
    environment variables, with sensible defaults provided.
    """

    connection_string: str = Field(
        default_factory=lambda: os.getenv(
            "POSTGRES_DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/ai_agent_db"
        ),
        description="Database connection URL (supports PostgreSQL)",
    )

    pool_size: int = Field(
        default_factory=lambda: int(os.getenv("DB_POOL_SIZE", "5")),
        description="Maximum number of database connections to keep in the pool",
    )

    max_overflow: int = Field(
        default_factory=lambda: int(os.getenv("DB_MAX_OVERFLOW", "10")),
        description="Maximum number of connections that can be created beyond pool_size",
    )

    pool_timeout: int = Field(
        default_factory=lambda: int(os.getenv("DB_POOL_TIMEOUT", "30")),
        description="Seconds to wait before giving up on getting a connection from the pool",
    )

    pool_recycle: int = Field(
        default_factory=lambda: int(os.getenv("DB_POOL_RECYCLE", "1800")),
        description="Seconds after which a connection is automatically recycled (30 minutes)",
    )


# Create a global database config instance for easy imports
database_config = DatabaseConfig()
