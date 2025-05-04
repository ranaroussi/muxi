# =============================================================================
# FRONTMATTER
# =============================================================================
# Title:        Model Providers Package Initialization
# Description:  Language model provider implementations for the Muxi Framework
# Role:         Centralizes model provider imports and exports
# Usage:        Imported when accessing any model provider implementation
# Author:       Muxi Framework Team
#
# The providers package provides concrete implementations of the BaseModel
# interface for various language model providers. It currently includes:
#
# 1. OpenAI Provider
#    - Supports latest OpenAI models including GPT-4o
#    - Implements chat, text generation, and embedding functionality
#    - Handles authentication and API-specific parameters
#
# This package is designed to be extended with additional providers
# such as Anthropic (Claude), Cohere, or other model providers.
# Each provider must fully implement the BaseModel interface.
#
# Providers are typically accessed through the Muxi facade:
#
#   # Using the Muxi facade (recommended)
#   app = muxi()
#   app.add_agent("assistant", "configs/openai-agent.yaml")
#
# Or directly through their class implementations:
#
#   # Direct usage
#   from muxi.core.models.providers import OpenAIModel
#
#   model = OpenAIModel(
#       model="gpt-4o",
#       api_key="sk-..."
#   )
#
#   response = await model.chat([{"role": "user", "content": "Hello"}])
#
# Adding new providers requires implementing the BaseModel interface
# and adding the new class to the __all__ export list in this file.
# =============================================================================

from muxi.core.models.providers.openai import OpenAIModel

__all__ = [
    "OpenAIModel",
]
