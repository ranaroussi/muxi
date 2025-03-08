"""
Language model module for the MUXI Framework.

This module contains implementations of various language model providers.
"""

from src.models.base import BaseModel
from src.models.providers.openai import OpenAIModel

# Make classes available at the module level
__all__ = ["BaseModel", "OpenAIModel"]
