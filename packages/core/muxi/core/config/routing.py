# =============================================================================
# FRONTMATTER
# =============================================================================
# Title:        Routing Configuration - LLM-Based Message Routing Settings
# Description:  Configuration for intelligent message routing between agents
# Role:         Provides settings for the message routing system
# Usage:        Imported by components using the routing system
# Author:       Muxi Framework Team
#
# The Routing Configuration module provides centralized settings for the
# LLM-based message routing functionality in the Muxi Framework. This system
# enables intelligent message routing between different specialized agents
# based on message content and agent capabilities.
#
# Key features include:
#
# 1. Routing LLM Configuration
#    - Model selection for routing decisions
#    - Temperature and token settings
#    - System prompt customization
#
# 2. Performance Optimization
#    - Caching settings for routing decisions
#    - TTL configuration for cached routes
#
# 3. Environment Integration
#    - Environment variable based configuration
#    - Sensible defaults for quick setup
#
# Example usage:
#
#   from muxi.core.config import routing_config
#
#   # Access routing configuration
#   model = routing_config.model
#   system_prompt = routing_config.system_prompt
#   use_cache = routing_config.use_caching
# =============================================================================

import os
from pydantic import BaseModel, Field


class RoutingConfig(BaseModel):
    """
    Configuration for the LLM-based message routing system.

    This class defines parameters for the language model used to make
    intelligent routing decisions between agents. It includes model selection,
    generation parameters, caching settings, and prompt customization.
    """

    provider: str = Field(
        default=os.getenv("ROUTING_LLM", "openai"),
        description="The LLM provider to use for routing decisions",
    )

    model: str = Field(
        default=os.getenv("ROUTING_LLM_MODEL", "gpt-4o-mini"),
        description="The specific model to use for routing decisions (smaller models preferred)",
    )

    temperature: float = Field(
        default=float(os.getenv("ROUTING_LLM_TEMPERATURE", "0.0")),
        description="Temperature setting for routing (low for consistent decisions)",
    )

    max_tokens: int = Field(
        default=int(os.getenv("ROUTING_LLM_MAX_TOKENS", "256")),
        description="Maximum response length for routing decisions",
    )

    use_caching: bool = Field(
        default=os.getenv("ROUTING_USE_CACHING", "true").lower() == "true",
        description="Whether to cache routing decisions to improve performance",
    )

    cache_ttl: int = Field(
        default=int(os.getenv("ROUTING_CACHE_TTL", "3600")),
        description="Time to live for cached routing decisions in seconds",
    )

    system_prompt: str = Field(
        default=os.getenv(
            "ROUTING_SYSTEM_PROMPT",
            "You are a routing assistant that determines which agent should handle a user message. "
            "Based on the user's message and the available agents' descriptions, select the most "
            "appropriate agent to handle the request. Respond with just the agent ID.",
        ),
        description="System prompt that guides the routing model's behavior",
    )


# Create a global instance of the routing configuration for easy imports
routing_config = RoutingConfig()
