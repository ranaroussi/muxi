"""
Configuration for the MUXI Framework.

This module provides configuration settings for the MUXI Framework.
"""

from muxi.core.config.database import DatabaseConfig, database_config
from muxi.core.config.loader import ConfigLoader
from muxi.core.config.memory import MemoryConfig, memory_config
from muxi.core.config.model import ModelConfig, model_config
from muxi.core.config.routing import RoutingConfig, routing_config

from pydantic import BaseModel, Field


class Config(BaseModel):
    """
    Main configuration class for the MUXI Framework.

    This class combines all configuration settings into a single object.
    """

    database: DatabaseConfig = Field(default_factory=lambda: database_config)
    memory: MemoryConfig = Field(default_factory=lambda: memory_config)
    model: ModelConfig = Field(default_factory=lambda: model_config)
    routing: RoutingConfig = Field(default_factory=lambda: routing_config)


# Create a global config instance
config = Config()


__all__ = [
    "ConfigLoader",
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
