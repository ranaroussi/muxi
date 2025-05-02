"""
Utilities for the MUXI Framework.

This module provides various utility functions used throughout the framework.
"""

# Re-export utility functions
from muxi.core.utils.id_generator import get_default_nanoid
from muxi.core.utils.version import get_version
from muxi.core.utils.document import load_document, chunk_text

__all__ = [
    "get_default_nanoid",
    "get_version",
    "load_document",
    "chunk_text",
]
