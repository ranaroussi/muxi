# =============================================================================
# FRONTMATTER
# =============================================================================
# Title:        Configuration System - Framework Configuration Management
# Description:  Centralized configuration system for the Muxi framework
# Role:         Provides settings for all framework components
# Usage:        Imported by components needing configuration settings
# Author:       Muxi Framework Team
#
# The configuration system provides a centralized way to manage all settings
# for the Muxi framework. It combines:
#
# 1. Environment-Based Configuration
#    - Loads settings from environment variables
#    - Uses sensible defaults for missing values
#    - Follows consistent naming conventions
#
# 2. Component-Specific Settings
#    - Database connection settings
#    - Memory configuration (buffer size, vector search, etc.)
#    - Model settings (providers, parameters, API keys)
#    - Routing rules for agent selection and message handling
#
# 3. Configuration Validation
#    - Uses Pydantic for type validation and conversion
#    - Ensures configuration values are within acceptable ranges
#    - Provides helpful error messages for invalid settings
#
# The configuration system can be accessed in several ways:
#
#   # Using the global config object (recommended):
#   from muxi.core.config import config
#
#   buffer_size = config.memory.buffer_size
#   vector_search = config.memory.vector_search_enabled
#
#   # Using component-specific config objects:
#   from muxi.core.config import memory_config
#
#   buffer_size = memory_config.buffer_size
#
#   # Accessing from the Orchestrator:
#   buffer_size = orchestrator.config.memory.buffer_size
#
# The configuration is typically loaded once at application startup and then
# accessed throughout the framework as needed. Any component that requires
# configuration settings should import and use this module.
# =============================================================================


from muxi.core.config.database import DatabaseConfig, database_config
from muxi.core.config.loader import ConfigLoader
from muxi.core.config.memory import MemoryConfig, memory_config
from muxi.core.config.model import ModelConfig, model_config
from muxi.core.config.routing import RoutingConfig, routing_config

from pydantic import BaseModel, Field


class Config(BaseModel):
    """
    Main configuration class for the MUXI Framework.

    This class combines all component-specific configuration settings into a single
    unified object, providing a centralized point of access for all framework
    configuration. It uses Pydantic for validation and ensures settings are properly
    typed and within acceptable ranges.

    Configuration is typically loaded from environment variables but can also
    be set programmatically when needed. The class uses Field with default_factory
    to defer loading of component configs until they're actually needed.
    """

    database: DatabaseConfig = Field(default_factory=lambda: database_config)
    memory: MemoryConfig = Field(default_factory=lambda: memory_config)
    model: ModelConfig = Field(default_factory=lambda: model_config)
    routing: RoutingConfig = Field(default_factory=lambda: routing_config)


# Create a global config instance that can be imported and used throughout the framework
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
