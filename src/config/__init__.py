"""
Configuration package for the AI Agent Framework.

This package provides a centralized configuration management system.
"""

from dotenv import load_dotenv
from pydantic import BaseModel, Field
from typing import Dict, Any

# Import configuration components
from src.config.database import database_config, DatabaseConfig
from src.config.memory import memory_config, MemoryConfig
from src.config.llm import llm_config, LLMConfig
from src.config.tools import tools_config, ToolsConfig
from src.config.logging import logging_config, LoggingConfig, configure_logging
from src.config.app import app_config, AppConfig

# Load environment variables from .env file
load_dotenv()


class Config(BaseModel):
    """
    Main configuration class that combines all component configurations.
    """

    database: DatabaseConfig = Field(default_factory=lambda: database_config)
    memory: MemoryConfig = Field(default_factory=lambda: memory_config)
    llm: LLMConfig = Field(default_factory=lambda: llm_config)
    tools: ToolsConfig = Field(default_factory=lambda: tools_config)
    logging: LoggingConfig = Field(default_factory=lambda: logging_config)
    app: AppConfig = Field(default_factory=lambda: app_config)

    # Custom configuration values
    custom: Dict[str, Any] = Field(default_factory=dict)

    def get_custom(self, key: str, default: Any = None) -> Any:
        """
        Get a custom configuration value.

        Args:
            key: The key of the custom configuration value.
            default: The default value to return if the key is not found.

        Returns:
            The custom configuration value, or the default if not found.
        """
        return self.custom.get(key, default)

    def set_custom(self, key: str, value: Any) -> None:
        """
        Set a custom configuration value.

        Args:
            key: The key of the custom configuration value.
            value: The value to set.
        """
        self.custom[key] = value


# Create a global config instance
config = Config()

# Initialize logging
configure_logging()

# Export components for direct access
__all__ = [
    "config", "Config", "configure_logging",
    "database_config", "DatabaseConfig",
    "memory_config", "MemoryConfig",
    "llm_config", "LLMConfig",
    "tools_config", "ToolsConfig",
    "logging_config", "LoggingConfig",
    "app_config", "AppConfig"
]
