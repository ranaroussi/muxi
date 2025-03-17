"""
Language model module for the MUXI Framework.

This module contains implementations of various language model providers.
"""

from muxi.models.base import BaseModel
from muxi.models.providers.openai import OpenAIModel

# Make classes available at the module level
__all__ = ["BaseModel", "OpenAIModel"]
