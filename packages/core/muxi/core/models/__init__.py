# =============================================================================
# FRONTMATTER
# =============================================================================
# Title:        Models Package - Language Model Interface
# Description:  Language model abstractions and implementations
# Role:         Provides standardized access to various LLM providers
# Usage:        Imported when working with language models
# Author:       Muxi Framework Team
#
# The models package provides a unified interface for working with language
# models from various providers. It consists of:
#
# 1. Base Model Interface
#    - Abstract base class defining the interface for all model implementations
#    - Standardized methods for chat, embeddings, and structured generation
#    - Model-agnostic response format (ModelResponse)
#
# 2. Provider Implementations
#    - Concrete implementations for specific LLM providers
#    - Currently supports OpenAI (GPT models)
#    - Extensible design for adding new providers
#
# 3. Utilities and Helpers
#    - Common utilities for working with language models
#    - Parameter validation and transformation
#    - Response parsing and formatting
#
# The models package is designed to make it easy to:
# - Use different LLM providers with a consistent interface
# - Switch between models without changing application code
# - Handle provider-specific parameters and configuration
# - Process and standardize model responses
#
# Example usage:
#
#   # Using OpenAI models
#   from muxi.core.models.providers import OpenAIModel
#
#   model = OpenAIModel(
#       model="gpt-4o",
#       temperature=0.7,
#       api_key="sk-..."  # Or use OPENAI_API_KEY env var
#   )
#
#   # Generate a chat completion
#   response = await model.chat([
#       {"role": "system", "content": "You are a helpful assistant"},
#       {"role": "user", "content": "Tell me about AI"}
#   ])
#
#   # Get embeddings for semantic search
#   embedding = await model.embed("Text to embed")
# =============================================================================


from muxi.core.models.base import BaseModel, ModelResponse

__all__ = [
    "BaseModel",
    "ModelResponse",
]
