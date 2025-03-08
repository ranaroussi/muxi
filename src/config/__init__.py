"""
Configuration for the MUXI Framework.

This module provides configuration settings for the MUXI Framework.
"""

import os
from importlib import import_module

from pydantic import BaseModel, Field

from src.config.database import DatabaseConfig, database_config
from src.config.memory import MemoryConfig, memory_config
from src.config.model import ModelConfig, model_config
from src.config.tools import ToolsConfig, tools_config


class Config(BaseModel):
    """
    Main configuration class for the MUXI Framework.

    This class combines all configuration settings into a single object.
    """

    database: DatabaseConfig = Field(default_factory=lambda: database_config)
    memory: MemoryConfig = Field(default_factory=lambda: memory_config)
    model: ModelConfig = Field(default_factory=lambda: model_config)
    tools: ToolsConfig = Field(default_factory=lambda: tools_config)
    debug: bool = Field(default=os.getenv("DEBUG", "false").lower() == "true")
    telemetry_enabled: bool = Field(
        default=os.getenv("TELEMETRY_ENABLED", "true").lower() == "true"
    )

    def register_provider(self, provider_type: str, provider_name: str) -> None:
        """
        Register a custom provider module.

        Args:
            provider_type: Type of provider (e.g., "embeddings", "model")
            provider_name: Name of the provider module
        """
        try:
            import_module(f"src.providers.{provider_type}.{provider_name}")
        except ImportError as error:
            module_path = f"src.providers.{provider_type}.{provider_name}"
            raise ImportError(f"Could not import provider module {module_path}: {error}")


# Create a global config instance
config = Config()


__all__ = [
    "config",
    "Config",
    "database_config",
    "DatabaseConfig",
    "memory_config",
    "MemoryConfig",
    "model_config",
    "ModelConfig",
    "tools_config",
    "ToolsConfig",
]
