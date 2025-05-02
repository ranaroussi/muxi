"""
Extensions for the MUXI Framework.

This module provides extension points for adding functionality to the framework.
"""

# Import any extensions that should be available by default
try:
    from packages.core.extensions.sqlite_vec import SQLiteVecExtension
    __all__ = ["SQLiteVecExtension"]
except ImportError:
    __all__ = []
