"""
Routing configuration for the MUXI Framework.

This module provides routing-related configuration settings, specifically
for the LLM-based message routing functionality.
"""

import os
from pydantic import BaseModel, Field


class RoutingConfig(BaseModel):
    """
    Configuration for the routing LLM.

    This class defines the configuration parameters for the LLM used for
    intelligent message routing between agents.
    """

    provider: str = Field(
        default=os.getenv("ROUTING_LLM", "openai"),
        description="The provider to use for routing decisions",
    )
    model: str = Field(
        default=os.getenv("ROUTING_LLM_MODEL", "gpt-4o-mini"),
        description="The model to use for routing decisions",
    )
    temperature: float = Field(
        default=float(os.getenv("ROUTING_LLM_TEMPERATURE", "0.0")),
        description="The temperature to use for routing decisions",
    )
    max_tokens: int = Field(
        default=int(os.getenv("ROUTING_LLM_MAX_TOKENS", "256")),
        description="The maximum number of tokens to generate",
    )
    use_caching: bool = Field(
        default=os.getenv("ROUTING_USE_CACHING", "true").lower() == "true",
        description="Whether to cache routing decisions",
    )
    cache_ttl: int = Field(
        default=int(os.getenv("ROUTING_CACHE_TTL", "3600")),
        description="Time in seconds to cache routing decisions",
    )
    system_prompt: str = Field(
        default=os.getenv(
            "ROUTING_SYSTEM_PROMPT",
            "You are a routing assistant that determines which agent should handle a user message. "
            "Based on the user's message and the available agents' descriptions, select the most "
            "appropriate agent to handle the request. Respond with just the agent ID.",
        ),
        description="System prompt for the routing LLM",
    )


# Create a global instance of the routing configuration
routing_config = RoutingConfig()
