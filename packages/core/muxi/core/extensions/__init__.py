# =============================================================================
# FRONTMATTER
# =============================================================================
# Title:        Extensions Package Initialization
# Description:  Entry point for Muxi Framework extension system
# Role:         Exposes extension classes and manages extension imports
# Usage:        Imported when using framework extensions
# Author:       Muxi Framework Team
#
# The extensions package provides a pluggable system for extending the Muxi
# framework with additional functionality. This includes:
#
# 1. Extension Base System
#    - Provides the Extension base class for creating new extensions
#    - Handles extension registration and discovery
#    - Manages extension lifecycle
#
# 2. Built-in Extensions
#    - SQLiteVecExtension for vector operations in SQLite
#    - Additional extensions can be added and registered here
#
# Extensions follow a consistent pattern where they register with the central
# Extension registry and expose a standard interface for initialization and use.
# This allows the framework to be extended with new capabilities without modifying
# core components.
# =============================================================================

from .base import Extension
from .sqlite_vec import SQLiteVecExtension

__all__ = ["Extension", "SQLiteVecExtension"]
