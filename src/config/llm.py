"""
LLM configuration for the AI Agent Framework.

This module provides LLM-related configuration settings.
"""

import os
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class LLMConfig(BaseModel):
    """LLM configuration settings."""

    default_provider: str = Field(
        default_factory=lambda: os.getenv("DEFAULT_LLM_PROVIDER", "openai")
    )

    default_model: str = Field(
        default_factory=lambda: os.getenv("DEFAULT_LLM_MODEL", "gpt-4o")
    )

    openai_api_key: Optional[str] = Field(
        default_factory=lambda: os.getenv("OPENAI_API_KEY")
    )

    anthropic_api_key: Optional[str] = Field(
        default_factory=lambda: os.getenv("ANTHROPIC_API_KEY")
    )

    temperature: float = Field(
        default_factory=lambda: float(os.getenv("LLM_TEMPERATURE", "0.7"))
    )

    max_tokens: int = Field(
        default_factory=lambda: int(os.getenv("LLM_MAX_TOKENS", "1000"))
    )

    default_embedding_model: str = Field(
        default_factory=lambda: os.getenv(
            "DEFAULT_EMBEDDING_MODEL",
            "text-embedding-3-small"
        )
    )

    provider_settings: Dict[str, Any] = Field(default_factory=dict)


# Create a global LLM config instance
llm_config = LLMConfig()
