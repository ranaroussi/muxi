"""
Language model configuration for the AI Agent Framework.

This module provides model-related configuration settings.
"""

import os
from typing import Optional

from pydantic import BaseModel, Field


class ModelConfig(BaseModel):
    """Language model configuration settings."""

    provider: str = Field(default_factory=lambda: os.getenv("DEFAULT_MODEL_PROVIDER", "openai"))
    default_model: str = Field(default_factory=lambda: os.getenv("DEFAULT_MODEL_NAME", "gpt-4o"))
    openai_api_key: Optional[str] = Field(default_factory=lambda: os.getenv("OPENAI_API_KEY"))
    anthropic_api_key: Optional[str] = Field(default_factory=lambda: os.getenv("ANTHROPIC_API_KEY"))
    temperature: float = Field(default_factory=lambda: float(os.getenv("MODEL_TEMPERATURE", "0.7")))
    max_tokens: Optional[int] = Field(
        default_factory=lambda: int(os.getenv("MODEL_MAX_TOKENS", "1000"))
    )
    embedding_dimension: int = Field(
        default_factory=lambda: int(os.getenv("EMBEDDING_DIMENSION", "1536"))
    )
    top_p: float = Field(default_factory=lambda: float(os.getenv("TOP_P", "1.0")))
    frequency_penalty: float = Field(
        default_factory=lambda: float(os.getenv("FREQUENCY_PENALTY", "0.0"))
    )
    presence_penalty: float = Field(
        default_factory=lambda: float(os.getenv("PRESENCE_PENALTY", "0.0"))
    )


# Create a global model config instance
model_config = ModelConfig()
