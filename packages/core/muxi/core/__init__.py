# =============================================================================
# FRONTMATTER
# =============================================================================
# Title:        Core Framework Package Initialization
# Description:  Main entry point for the Muxi Core Framework
# Role:         Defines package-level imports and version information
# Usage:        Imported when accessing core framework components
# Author:       Muxi Framework Team
#
# This file initializes the Muxi Core framework package and defines what's
# available when importing from muxi.core. It exports:
#
# 1. High-Level Interfaces
#    - Muxi facade for declarative framework usage
#    - Orchestrator for direct agent and memory management
#
# 2. Utility Functions
#    - Server startup functionality
#    - Network utility functions
#
# The core package is the foundation of the Muxi Framework, providing
# the essential components for building AI agent applications.
# =============================================================================

# Import facade classes for easy access
from muxi.core.facade import Muxi
from muxi.core.orchestrator import Orchestrator
from muxi.core.run import run_server, is_port_in_use

# Current version of the Muxi Core framework
__version__ = "0.1.0"

# Explicitly define what's available when using "from muxi.core import *"
__all__ = [
    "Muxi",
    "Orchestrator",
    "run_server",
    "is_port_in_use",
]
