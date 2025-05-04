# =============================================================================
# FRONTMATTER
# =============================================================================
# Title:        SQLite Vector Extension - Vector Operations for SQLite
# Description:  Extension for enabling vector similarity search in SQLite
# Role:         Provides vector operations capabilities in local SQLite databases
# Usage:        Used by vector storage components requiring local-first operation
# Author:       Muxi Framework Team
#
# The SQLiteVecExtension provides seamless integration with the sqlite-vec
# extension for SQLite, enabling efficient vector operations in SQLite databases.
# This is essential for local-first vector storage and semantic search without
# requiring external vector database services. Key features include:
#
# 1. Cross-Platform Support
#    - Detects and loads the appropriate extension for the current platform
#    - Supports major operating systems (macOS, Windows, Linux)
#    - Handles both x86_64 and ARM64 architectures
#
# 2. Graceful Fallbacks
#    - Tries multiple extension loading strategies
#    - Falls back to Python package if native extension not found
#    - Provides clear error messages for troubleshooting
#
# 3. Database Integration
#    - Configures SQLite connections for vector operations
#    - Enables cosine distance, L2 distance, and other vector functions
#    - Simplifies using vector operations in SQLite queries
#
# This extension is particularly valuable for:
# - Edge computing scenarios requiring local vector search
# - Privacy-sensitive applications that need to avoid remote vector DBs
# - Embedded systems with limited connectivity
# - Development and testing environments
#
# Example usage:
#
#   # Configure a SQLite connection with vector capabilities
#   conn = sqlite3.connect("my_database.db")
#   SQLiteVecExtension.load_extension(conn)
#
#   # Create a table with vector column
#   conn.execute('''
#       CREATE TABLE IF NOT EXISTS items (
#           id TEXT PRIMARY KEY,
#           embedding BLOB
#       )
#   ''')
#
#   # Query using vector similarity
#   conn.execute('''
#       SELECT id, vec_distance_cosine(embedding, ?) as score
#       FROM items ORDER BY score ASC LIMIT 5
#   ''', (query_vector,))
# =============================================================================

import os
import platform
import sqlite3

from loguru import logger

from muxi.core.extensions.base import Extension


@Extension.register
class SQLiteVecExtension(Extension):
    """
    SQLite Vector extension for vector operations in SQLite.

    This extension enables vector similarity search operations in SQLite databases,
    which is used by Muxi for local-first vector storage and semantic search without
    requiring external vector database services.
    """

    name = "sqlite-vec"
    _is_initialized = False
    _init_path = None

    @classmethod
    def _get_platform_extension_path(cls):
        """
        Get the platform-specific extension path for SQLite vector extension.

        Determines the correct extension file path based on the current operating system
        and machine architecture (x86_64 or ARM64). The extension file has different
        formats (.so, .dll, .dylib) depending on the platform.

        Returns:
            str: Path to the platform-specific extension file

        Raises:
            ImportError: If the current architecture or operating system is not supported
        """
        # Get machine architecture
        machine = platform.machine().lower()
        if machine == "x86_64":
            arch = "x86_64"
        elif machine == "arm64" or machine == "aarch64":
            arch = "arm64"
        else:
            raise ImportError(f"Unsupported architecture: {machine}")

        # Get operating system
        system = platform.system().lower()
        if system == "darwin":
            os_name = "darwin"
            extension = "dylib"
        elif system == "windows":
            os_name = "windows"
            extension = "dll"
        elif system == "linux":
            os_name = "linux"
            extension = "so"
        else:
            raise ImportError(f"Unsupported operating system: {system}")

        # Construct the platform identifier
        platform_id = f"{arch}-{os_name}"

        # Construct the path to the extension file
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        loadable_dir = os.path.join(base_dir, "extensions", "loadable", "sqlite_vec", platform_id)

        # Create the loadable directory if it doesn't exist
        os.makedirs(loadable_dir, exist_ok=True)

        ext_path = os.path.join(loadable_dir, f"sqlite_vec.{extension}")

        logger.debug(f"Looking for SQLite Vector extension at: {ext_path}")
        return ext_path

    @classmethod
    def init(cls, path: str = None, **kwargs):
        """
        Initialize the SQLite Vector extension.

        This method prepares the extension for use, setting up the necessary paths and
        initialization parameters. It does not actually load the extension into any
        specific connection - use load_extension() for that.

        Args:
            path: Optional explicit path to the SQLite Vector extension library (.so, .dll, .dylib).
                If not provided, a platform-specific path will be determined automatically.
            **kwargs: Additional parameters for extension initialization (not currently used)

        Returns:
            bool: True if initialized successfully, False otherwise

        Raises:
            ImportError: If the extension cannot be located or is incompatible
        """
        if cls._is_initialized:
            logger.info("SQLite Vector extension already initialized")
            return True

        # If no explicit path is provided, use the platform-specific path
        if not path:
            try:
                path = cls._get_platform_extension_path()
            except ImportError as e:
                logger.error(f"Failed to determine platform-specific extension path: {e}")
                # Will try fallbacks in load_extension

        # Store the initialization info for later connections
        cls._init_path = path

        # Flag that initialization was attempted (will be set to True on success)
        cls._is_initialized = True

        logger.info(f"Initialized SQLite Vector extension with path: {path}")
        return True

    @classmethod
    def load_extension(cls, conn: sqlite3.Connection):
        """
        Load the SQLite Vector extension into a SQLite connection.

        This method attempts to load the extension using several strategies:
        1. Use the path provided during initialization (if available)
        2. Try the platform-specific path
        3. Fall back to the Python package if available

        Args:
            conn: The SQLite connection to load the extension into

        Raises:
            ImportError: If the extension cannot be loaded using any available method
        """
        conn.enable_load_extension(True)

        # If a specific path was provided during init, use it
        if cls._init_path:
            if not os.path.exists(cls._init_path):
                logger.warning(f"SQLite Vector extension not found at: {cls._init_path}")
                # Will try fallbacks below
            else:
                try:
                    conn.load_extension(cls._init_path)
                    logger.info(f"Loaded SQLite Vector extension from: {cls._init_path}")
                    return
                except Exception as e:
                    logger.warning(f"Failed to load SQLite Vector extension from path: {e}")
                    # Will try fallbacks below

        # Try to use the platform-specific extension
        try:
            path = cls._get_platform_extension_path()
            if os.path.exists(path):
                conn.load_extension(path)
                logger.info(f"Loaded SQLite Vector extension from platform path: {path}")
                return
            else:
                logger.warning(f"SQLite Vector extension not found at: {path}")
                logger.warning(f"You may need to place the sqlite_vec extension at: {path}")
        except Exception as e:
            logger.warning(f"Failed to load platform-specific SQLite Vector extension: {e}")

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
        """
        Configure a SQLite database connection to use the Vector extension.

        Convenience method that loads the extension and returns the configured connection,
        enabling method chaining for cleaner setup code.

        Args:
            conn: The SQLite connection to configure

        Returns:
            sqlite3.Connection: The configured connection with vector capabilities enabled
        """
        cls.load_extension(conn)
        return conn
