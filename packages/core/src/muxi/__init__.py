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
            If None, will be loaded from POSTGRES_DATABASE_URL environment variable
            when needed (only if an agent with long-term memory is created).

    Returns:
        Muxi: A new MUXI facade instance
    """
    return Muxi(db_connection_string)


def use_extension(name, **kwargs):
    """Initialize a MUXI extension by name.

    Args:
        name: The name of the extension to initialize
        **kwargs: Extension-specific initialization parameters

    Returns:
        The result of the extension initialization

    Raises:
        ValueError: If the extension is not found
        ImportError: If there is an error loading the extension
    """
    from muxi.core.extensions.base import Extension

    extension_cls = Extension.get(name)
    if not extension_cls:
        available = ", ".join(Extension.list()) or "none available"
        raise ValueError(f"Extension '{name}' not found. Available extensions: {available}")

    return extension_cls.init(**kwargs)
