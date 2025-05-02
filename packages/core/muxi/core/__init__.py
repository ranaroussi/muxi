"""
MUXI Core Framework.

This is the main entry point for the MUXI Core Framework.
"""

# Import facade classes for easy access
from muxi.core.facade import Muxi
from muxi.core.orchestrator import Orchestrator
from muxi.core.run import run_server, is_port_in_use

__version__ = "0.1.0"

__all__ = [
    "Muxi",
    "Orchestrator",
    "run_server",
    "is_port_in_use",
]
