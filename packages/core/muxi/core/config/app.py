"""
Application configuration for the MUXI Framework.

This module provides general application configuration settings.
"""

import os
from typing import Optional

from pydantic import BaseModel, Field


class AppConfig(BaseModel):
    """Application configuration settings."""

    default_agent_id: str = Field(
        default_factory=lambda: os.getenv("DEFAULT_AGENT_ID", "default_agent")
    )

    environment: str = Field(default_factory=lambda: os.getenv("ENVIRONMENT", "development"))

    debug: bool = Field(default_factory=lambda: os.getenv("DEBUG", "false").lower() == "true")

    host: str = Field(default_factory=lambda: os.getenv("HOST", "0.0.0.0"))

    port: int = Field(default_factory=lambda: int(os.getenv("PORT", "8000")))

    base_url: Optional[str] = Field(default_factory=lambda: os.getenv("BASE_URL"))

    cors_origins: str = Field(default_factory=lambda: os.getenv("CORS_ORIGINS", "*"))

    secret_key: str = Field(default_factory=lambda: os.getenv("SECRET_KEY", os.urandom(24).hex()))

    jwt_algorithm: str = Field(default_factory=lambda: os.getenv("JWT_ALGORITHM", "HS256"))

    jwt_expiration: int = Field(default_factory=lambda: int(os.getenv("JWT_EXPIRATION", "86400")))

    system_message: str = Field(
        default_factory=lambda: os.getenv(
            "SYSTEM_MESSAGE",
            "You are a helpful AI assistant. Use the available tools to assist the user with their tasks.",
        )
    )


# Create a global instance
app_config = AppConfig()
