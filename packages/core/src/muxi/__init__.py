"""
MUXI Framework Facade

This module provides a simplified interface to work with the MUXI framework.
It allows users to create and manage agents, start servers, and interact with
the framework with minimal code, using configuration files instead of direct API calls.
"""

from .facade import Muxi

__all__ = ["Muxi"]


def muxi(db_connection_string=None):
    """
    Create a new MUXI facade instance.

    Args:
        db_connection_string: Optional database connection string.
            If None, will be loaded from DATABASE_URL environment variable
            when needed (only if an agent with long-term memory is created).

    Returns:
        Muxi: A new MUXI facade instance
    """
    return Muxi(db_connection_string)
