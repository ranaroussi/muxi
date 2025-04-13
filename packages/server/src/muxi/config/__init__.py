"""
Configuration for the MUXI Framework.

This module provides configuration settings for the MUXI Framework.
"""

import os
from importlib import import_module

from pydantic import BaseModel, Field

from muxi.server.config.database import DatabaseConfig, database_config
from muxi.server.config.memory import MemoryConfig, memory_config
from muxi.server.config.model import ModelConfig, model_config
from muxi.server.config.routing import RoutingConfig, routing_config


class Config(BaseModel):
    """
    Main configuration class for the MUXI Framework.

    This class combines all configuration settings into a single object.
    """

    database: DatabaseConfig = Field(default_factory=lambda: database_config)
    memory: MemoryConfig = Field(default_factory=lambda: memory_config)
    model: ModelConfig = Field(default_factory=lambda: model_config)
    routing: RoutingConfig = Field(default_factory=lambda: routing_config)
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
            return import_module(f"muxi.providers.{provider_type}.{provider_name}")
        except (ImportError, ModuleNotFoundError):
            module_path = f"muxi.providers.{provider_type}.{provider_name}"
            raise ImportError(f"Could not import provider module {module_path}")


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
    "routing_config",
    "RoutingConfig",
]
