"""
MUXI Framework Extensions

This module provides the base classes and registry for MUXI extensions.
"""

from muxi.core.extensions.base import Extension
from muxi.core.extensions.sqlite_vec import SQLiteVecExtension

__all__ = ["Extension", "SQLiteVecExtension"]
