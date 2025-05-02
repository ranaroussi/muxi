"""
Extensions for the MUXI Framework.

This module provides extension points for adding functionality to the framework.
"""

# Dynamically populate __all__ based on available extensions
__all__ = []

try:
    # Import specifically to check availability and add to __all__
    from .sqlite_vec import SQLiteVecExtension
    __all__.append("SQLiteVecExtension")
    del SQLiteVecExtension
except ImportError:
    # SQLiteVecExtension is optional
    pass
