# =============================================================================
# FRONTMATTER
# =============================================================================
# Title:        Application Configuration - Core App Settings
# Description:  Central application configuration for the Muxi Framework
# Role:         Provides application-wide settings and defaults
# Usage:        Imported by components needing application configuration
# Author:       Muxi Framework Team
#
# The Application Configuration module provides a centralized way to manage
# application-wide settings using a Pydantic model for validation. It includes:
#
# 1. Core Server Settings
#    - Host and port configuration
#    - Environment mode (development/production)
#    - Debug toggle
#    - Base URL configuration
#
# 2. Security Configuration
#    - CORS settings
#    - Secret key management
#    - JWT authentication settings
#
# 3. Agent Configuration
#    - Default agent ID
#    - System message templates
#
# All settings can be configured via environment variables with appropriate
# defaults provided. This enables easy configuration in different deployment
# environments without code changes.
#
# Example usage:
#
#   from muxi.core.config import app_config
#
#   # Access configuration settings
#   host = app_config.host
#   port = app_config.port
#   is_debug = app_config.debug
# =============================================================================

import os
from typing import Optional

from pydantic import BaseModel, Field


class AppConfig(BaseModel):
    """
    Application configuration settings for the Muxi Framework.

    This class defines core application settings using Pydantic for validation
    and type safety. Settings can be configured via environment variables, with
    sensible defaults provided for all options.
    """

    default_agent_id: str = Field(
        default_factory=lambda: os.getenv("DEFAULT_AGENT_ID", "default_agent"),
        description="Identifier for the default agent to use when none is specified",
    )

    environment: str = Field(
        default_factory=lambda: os.getenv("ENVIRONMENT", "development"),
        description="Application environment (development, production, etc.)",
    )

    debug: bool = Field(
        default_factory=lambda: os.getenv("DEBUG", "false").lower() == "true",
        description="Enable debug mode for additional logging and development features",
    )

    host: str = Field(
        default_factory=lambda: os.getenv("HOST", "0.0.0.0"),
        description="Host IP address to bind the server to",
    )

    port: int = Field(
        default_factory=lambda: int(os.getenv("PORT", "8000")),
        description="Port number for the server to listen on",
    )

    base_url: Optional[str] = Field(
        default_factory=lambda: os.getenv("BASE_URL"),
        description="Base URL for the server, used for constructing absolute URLs",
    )

    cors_origins: str = Field(
        default_factory=lambda: os.getenv("CORS_ORIGINS", "*"),
        description="Allowed CORS origins, comma-separated or '*' for all origins",
    )

    secret_key: str = Field(
        default_factory=lambda: os.getenv("SECRET_KEY", os.urandom(24).hex()),
        description="Secret key for cryptographic operations and session signing",
    )

    jwt_algorithm: str = Field(
        default_factory=lambda: os.getenv("JWT_ALGORITHM", "HS256"),
        description="Algorithm to use for JWT token generation and validation",
    )

    jwt_expiration: int = Field(
        default_factory=lambda: int(os.getenv("JWT_EXPIRATION", "86400")),
        description="JWT token expiration time in seconds (default: 24 hours)",
    )

    system_message: str = Field(
        default_factory=lambda: os.getenv(
            "SYSTEM_MESSAGE",
            "You are a helpful AI assistant. "
            "Use the available tools to assist the user with their tasks.",
        ),
        description="Default system message for AI assistants",
    )


# Create a global instance for easy imports
app_config = AppConfig()
