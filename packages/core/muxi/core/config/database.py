"""
Database configuration for the MUXI Framework.

This module provides database-related configuration settings.
"""

import os

from pydantic import BaseModel, Field


class DatabaseConfig(BaseModel):
    """Database configuration settings."""

    connection_string: str = Field(
        default_factory=lambda: os.getenv(
            "POSTGRES_DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/ai_agent_db"
        )
    )

    pool_size: int = Field(default_factory=lambda: int(os.getenv("DB_POOL_SIZE", "5")))

    max_overflow: int = Field(default_factory=lambda: int(os.getenv("DB_MAX_OVERFLOW", "10")))

    pool_timeout: int = Field(default_factory=lambda: int(os.getenv("DB_POOL_TIMEOUT", "30")))

    pool_recycle: int = Field(default_factory=lambda: int(os.getenv("DB_POOL_RECYCLE", "1800")))


# Create a global database config instance
database_config = DatabaseConfig()
