"""
SQLite Vector Extension

This module provides the SQLiteVecExtension class for loading the
sqlite-vec extension for vector similarity search in SQLite databases.
"""

import os
import sqlite3

from loguru import logger

from muxi.core.extensions.base import Extension


@Extension.register
class SQLiteVecExtension(Extension):
    """SQLite Vector extension for vector similarity operations in SQLite.

    This extension enables vector operations in SQLite, which is used by MUXI
    for local-first vector storage and semantic search.
    """
    name = "sqlite-vec"
    _is_initialized = False

    @classmethod
    def init(cls, path: str, **kwargs):
        """Initialize the SQLite Vector extension.

        Args:
            path: Path to the SQLite Vector extension library (.so, .dll, .dylib)

        Returns:
            True if initialized successfully, False otherwise

        Raises:
            ImportError: If the extension cannot be loaded
        """
        if cls._is_initialized:
            logger.info("SQLite Vector extension already initialized")
            return True

        # Store the initialization info for later connections
        cls._init_path = path

        # Flag that initialization was attempted (will be set to True on success)
        cls._is_initialized = True

        logger.info(f"Initialized SQLite Vector extension with path: {path}")
        return True

    @classmethod
    def load_extension(cls, conn: sqlite3.Connection):
        """Load the SQLite Vector extension into a SQLite connection.

        Args:
            conn: The SQLite connection to load the extension into

        Raises:
            ImportError: If the extension cannot be loaded
        """
        conn.enable_load_extension(True)

        # If a specific path was provided during init, use it
        if cls._init_path:
            if not os.path.exists(cls._init_path):
                raise ImportError(f"SQLite Vector extension not found at: {cls._init_path}")
            try:
                conn.load_extension(cls._init_path)
                logger.info(f"Loaded SQLite Vector extension from: {cls._init_path}")
                return
            except Exception as e:
                raise ImportError(f"Failed to load SQLite Vector extension: {e}")

        # Otherwise try to use the Python package
        try:
            import sqlite_vec
            sqlite_vec.load(conn)
            logger.info("Loaded SQLite Vector extension using Python package")
            return
        except ImportError:
            raise ImportError(
                "SQLite Vector extension package not available. "
                "Please install it with: pip install sqlite-vec"
            )
        except Exception as e:
            raise ImportError(f"Failed to load SQLite Vector extension: {e}")

    @classmethod
    def configure_database(cls, conn: sqlite3.Connection):
        """Configure a SQLite database connection to use the Vector extension.

        Args:
            conn: The SQLite connection to configure

        Returns:
            The configured connection
        """
        cls.load_extension(conn)
        return conn
