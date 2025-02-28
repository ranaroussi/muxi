"""
Tools configuration for the AI Agent Framework.

This module provides tools-related configuration settings.
"""

import os
from typing import Optional
from pydantic import BaseModel, Field


class ToolsConfig(BaseModel):
    """Tools configuration settings."""

    # Tool enablement
    enable_web_search: bool = Field(
        default_factory=lambda: os.getenv(
            "ENABLE_WEB_SEARCH", "true"
        ).lower() == "true"
    )

    enable_calculator: bool = Field(
        default_factory=lambda: os.getenv(
            "ENABLE_CALCULATOR", "true"
        ).lower() == "true"
    )

    # Search tools
    serper_api_key: Optional[str] = Field(
        default_factory=lambda: os.getenv("SERPER_API_KEY")
    )

    google_search_api_key: Optional[str] = Field(
        default_factory=lambda: os.getenv("GOOGLE_SEARCH_API_KEY")
    )

    search_engine_id: Optional[str] = Field(
        default_factory=lambda: os.getenv("SEARCH_ENGINE_ID")
    )

    # Browser tools
    browserless_api_key: Optional[str] = Field(
        default_factory=lambda: os.getenv("BROWSERLESS_API_KEY")
    )

    # File tools
    max_file_size_mb: int = Field(
        default_factory=lambda: int(os.getenv("MAX_FILE_SIZE_MB", "10"))
    )

    allowed_file_types: str = Field(
        default_factory=lambda: os.getenv(
            "ALLOWED_FILE_TYPES",
            "txt,pdf,doc,docx,csv,json,html,md"
        )
    )

    file_storage_path: str = Field(
        default_factory=lambda: os.getenv("FILE_STORAGE_PATH", "./data/files")
    )

    # Email tools
    smtp_server: Optional[str] = Field(
        default_factory=lambda: os.getenv("SMTP_SERVER")
    )

    smtp_port: Optional[int] = Field(
        default_factory=lambda: int(os.getenv("SMTP_PORT", "587"))
        if os.getenv("SMTP_PORT") else None
    )

    smtp_username: Optional[str] = Field(
        default_factory=lambda: os.getenv("SMTP_USERNAME")
    )

    smtp_password: Optional[str] = Field(
        default_factory=lambda: os.getenv("SMTP_PASSWORD")
    )


# Create a global tools config instance
tools_config = ToolsConfig()
