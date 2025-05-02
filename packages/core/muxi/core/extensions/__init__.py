"""
Extensions for the MUXI Framework.

This module provides extension points for adding functionality to the framework.
"""

from .base import Extension
from .sqlite_vec import SQLiteVecExtension

__all__ = ["Extension", "SQLiteVecExtension"]
