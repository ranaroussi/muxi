"""
Routing configuration for the MUXI Framework.

This module provides routing-related configuration settings, specifically
for the LLM-based message routing functionality.
"""

import os
from pydantic import BaseModel, Field


class RoutingConfig(BaseModel):
    """Routing configuration settings."""

    # LLM provider to use for routing (e.g., "openai", "anthropic")
    provider: str = Field(default_factory=lambda: os.getenv("ROUTING_LLM", "openai"))

    # Model name to use for routing
    model: str = Field(default_factory=lambda: os.getenv("ROUTING_LLM_MODEL", "gpt-4o-mini"))

    # Temperature for routing model (lower = more deterministic)
    temperature: float = Field(
        default_factory=lambda: float(os.getenv("ROUTING_LLM_TEMPERATURE", "0.0"))
    )

    # Max tokens to generate for routing responses
    max_tokens: int = Field(
        default_factory=lambda: int(os.getenv("ROUTING_LLM_MAX_TOKENS", "256"))
    )

    # Whether to use caching for routing decisions (to reduce API calls)
    use_caching: bool = Field(
        default_factory=lambda: os.getenv("ROUTING_USE_CACHING", "true").lower() == "true"
    )

    # Time in seconds to cache routing decisions
    cache_ttl: int = Field(
        default_factory=lambda: int(os.getenv("ROUTING_CACHE_TTL", "3600"))
    )

    # System prompt prefix for the routing model
    system_prompt: str = Field(
        default_factory=lambda: os.getenv(
            "ROUTING_SYSTEM_PROMPT",
            "You are a message routing assistant. Your job is to determine which specialized agent "
            "should handle a user message based on their descriptions and capabilities."
        )
    )


# Create a global routing config instance
routing_config = RoutingConfig()
