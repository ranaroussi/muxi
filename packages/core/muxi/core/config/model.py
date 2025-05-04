# =============================================================================
# FRONTMATTER
# =============================================================================
# Title:        Model Configuration - Language Model Settings
# Description:  Configuration settings for language models in the Muxi Framework
# Role:         Provides central settings for all language model interactions
# Usage:        Imported by components using language models
# Author:       Muxi Framework Team
#
# The Model Configuration module provides centralized settings for language
# model access and behavior across the Muxi Framework. It includes settings
# for model selection, API keys, and generation parameters.
#
# Key features include:
#
# 1. Provider Management
#    - Default provider selection (OpenAI, Anthropic, etc.)
#    - API key storage and management
#    - Model selection preferences
#
# 2. Generation Parameters
#    - Temperature controls
#    - Token limits
#    - Sampling parameters (top_p, frequency/presence penalties)
#
# 3. Embedding Configuration
#    - Embedding model dimensions
#    - Default embedding models
#
# All settings can be configured via environment variables, allowing for
# easy configuration in different deployment environments without code changes.
#
# Example usage:
#
#   from muxi.core.config import model_config
#
#   # Access model configuration
#   provider = model_config.provider
#   model = model_config.default_model
#   temperature = model_config.temperature
# =============================================================================

import os
from typing import Optional

from pydantic import BaseModel, Field


class ModelConfig(BaseModel):
    """
    Language model configuration settings for the Muxi Framework.

    This class defines parameters for language model selection, API access,
    and generation behavior. It uses Pydantic for validation and type safety,
    with all settings configurable via environment variables.
    """

    provider: str = Field(
        default_factory=lambda: os.getenv("DEFAULT_MODEL_PROVIDER", "openai"),
        description="Default LLM provider to use (e.g., 'openai', 'anthropic')",
    )

    default_model: str = Field(
        default_factory=lambda: os.getenv("DEFAULT_MODEL_NAME", "gpt-4o"),
        description="Default model name to use from the selected provider",
    )

    openai_api_key: Optional[str] = Field(
        default_factory=lambda: os.getenv("OPENAI_API_KEY"),
        description="API key for OpenAI services",
    )

    anthropic_api_key: Optional[str] = Field(
        default_factory=lambda: os.getenv("ANTHROPIC_API_KEY"),
        description="API key for Anthropic services",
    )

    temperature: float = Field(
        default_factory=lambda: float(os.getenv("MODEL_TEMPERATURE", "0.7")),
        description="Temperature for model generation (0-1, higher = more creative)",
    )

    max_tokens: Optional[int] = Field(
        default_factory=lambda: int(os.getenv("MODEL_MAX_TOKENS", "1000")),
        description="Maximum number of tokens to generate in responses",
    )

    embedding_dimension: int = Field(
        default_factory=lambda: int(os.getenv("EMBEDDING_DIMENSION", "1536")),
        description="Dimension of embedding vectors (OpenAI default is 1536)",
    )

    top_p: float = Field(
        default_factory=lambda: float(os.getenv("TOP_P", "1.0")),
        description="Top-p sampling parameter (0-1, lower = more focused)",
    )

    frequency_penalty: float = Field(
        default_factory=lambda: float(os.getenv("FREQUENCY_PENALTY", "0.0")),
        description="Penalty for token frequency (-2.0 to 2.0, higher = more variety)",
    )

    presence_penalty: float = Field(
        default_factory=lambda: float(os.getenv("PRESENCE_PENALTY", "0.0")),
        description="Penalty for token presence (-2.0 to 2.0, higher = less repetition)",
    )


# Create a global model config instance for easy imports
model_config = ModelConfig()
