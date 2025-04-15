"""
MUXI Framework Facade

This module provides a simplified interface to work with the MUXI framework.
It allows users to create and manage agents, start servers, and interact with
the framework with minimal code, using configuration files instead of direct API calls.
"""

from typing import Optional, Union

from .facade import Muxi
from muxi.server.memory.buffer import BufferMemory
from muxi.server.memory.long_term import LongTermMemory
from muxi.server.memory.memobase import Memobase

__all__ = ["Muxi"]


def muxi(
    buffer_memory: Optional[Union[int, BufferMemory]] = None,
    long_term_memory: Optional[Union[str, bool, LongTermMemory, Memobase]] = None,
    credential_db_connection_string: Optional[str] = None
):
    """
    Create a new MUXI facade instance with memory configuration.

    Args:
        buffer_memory: Optional buffer memory configuration.
            Can be an integer (buffer size), a BufferMemory instance, or None.
        long_term_memory: Optional long-term memory configuration.
            Can be a connection string, a boolean (True for default SQLite),
            an instance of LongTermMemory/Memobase, or None.
        credential_db_connection_string: Optional database connection string for credential storage.
            If None, will try to use the long_term_memory connection if it's a database string,
            or fall back to POSTGRES_DATABASE_URL environment variable.

    Returns:
        Muxi: A new MUXI facade instance
    """
    return Muxi(
        buffer_memory=buffer_memory,
        long_term_memory=long_term_memory,
        credential_db_connection_string=credential_db_connection_string
    )


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
