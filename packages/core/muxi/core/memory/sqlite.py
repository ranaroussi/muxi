"""
SQLite-based long-term memory implementation.

This module provides a long-term memory system using SQLite with the sqlite-vec
extension for vector similarity search.
"""

import json
import os
import sqlite3
import time
from typing import (
    Any, Dict, List, Optional, Tuple, Union
)

import numpy as np
from loguru import logger

from muxi.core.memory.base import BaseMemory
from muxi.core.extensions import SQLiteVecExtension


class SQLiteMemory(BaseMemory):
    """
    SQLite-based long-term memory implementation.

    This class provides a persistent vector database using SQLite with the
    sqlite-vec extension for storing and retrieving information based on
    semantic similarity.
    """

    def __init__(
        self,
        db_path: str,
        dimension: int = 1536,
        default_collection: str = "default",
        extensions_dir: str = "extensions"
    ):
        """
        Initialize SQLite-based long-term memory.

        Args:
            db_path: Path to the SQLite database file
            dimension: Dimension of the embedding vectors
            default_collection: Name of the default collection
            extensions_dir: Directory containing sqlite-vec extensions
        """
        self.db_path = db_path
        self.dimension = dimension
        self.default_collection = default_collection
        self.extensions_dir = extensions_dir
        self.embedding_provider = None  # Will be set by the agent

        # Create database directory if it doesn't exist
        os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)

        # Initialize database
        self.conn = self._init_database()

    def _init_database(self) -> sqlite3.Connection:
        """Initialize the SQLite database with required tables."""
        conn = sqlite3.connect(self.db_path)

        # Load sqlite-vec extension using the extension system
        try:
            SQLiteVecExtension.load_extension(conn)
        except ImportError:
            # If extension system not available, raise an error
            raise ImportError(
                "SQLiteVecExtension not available. Please install it with:"
                " pip install muxi-extensions-sqlite-vec"
            )

        # Create tables
        conn.execute("""
            CREATE TABLE IF NOT EXISTS collections (
                id TEXT PRIMARY KEY,
                name TEXT UNIQUE NOT NULL,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS memories (
                id TEXT PRIMARY KEY,
                collection TEXT NOT NULL,
                text TEXT NOT NULL,
                embedding BLOB NOT NULL,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (collection) REFERENCES collections(name)
            )
        """)

        # Create default collection if it doesn't exist
        conn.execute(
            "INSERT OR IGNORE INTO collections "
            "(id, name, description) VALUES (?, ?, ?)",
            (
                self._generate_id(),
                self.default_collection,
                "Default collection for memories"
            )
        )

        conn.commit()
        return conn

    def _generate_id(self, size: int = 21) -> str:
        """Generate a unique ID for memories and collections."""
        import nanoid
        return nanoid.generate(size=size)

    async def add(
        self,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Add content to memory.

        Args:
            content: The text content to store
            metadata: Optional metadata to associate with the content
        """
        if metadata is None:
            metadata = {}

        # Generate embedding if provider is set
        if self.embedding_provider:
            embedding = await self.embedding_provider.get_embedding(content)

            # Add timestamp to metadata
            metadata["timestamp"] = time.time()

            # Add to database
            self._add_internal(content, embedding, metadata, self.default_collection)

    def _add_internal(
        self,
        text: str,
        embedding: Union[List[float], np.ndarray],
        metadata: Dict[str, Any] = None,
        collection: Optional[str] = None
    ) -> str:
        """
        Internal method to add a memory to the database.

        Args:
            text: The text content to store
            embedding: The vector embedding of the text
            metadata: Optional metadata to associate with the content
            collection: Optional collection name

        Returns:
            The ID of the newly created memory entry
        """
        # Convert numpy array to list if necessary
        if isinstance(embedding, np.ndarray):
            embedding = embedding.astype(np.float32)

        # Use default collection if none specified
        collection = collection or self.default_collection

        # Generate memory ID
        memory_id = self._generate_id()

        # Insert memory
        self.conn.execute(
            """
            INSERT INTO memories
            (id, collection, text, embedding, metadata)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                memory_id,
                collection,
                text,
                embedding,
                metadata and json.dumps(metadata)
            )
        )
        self.conn.commit()

        return memory_id

    async def search(
        self,
        query: str,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Search for similar content in memory.

        Args:
            query: The text query to search for
            limit: Maximum number of results to return

        Returns:
            List of dictionaries containing the search results with content and metadata
        """
        # Generate embedding for query if provider is set
        if not self.embedding_provider:
            return []

        query_embedding = await self.embedding_provider.get_embedding(query)

        # Search with embedding
        results = self._search_internal(query_embedding, limit, self.default_collection)

        # Format results
        formatted_results = []
        for score, memory in results:
            formatted_results.append({
                "content": memory["text"],
                "metadata": memory["metadata"] if "metadata" in memory else {},
                "score": score
            })

        return formatted_results

    def _search_internal(
        self,
        query_embedding: Union[List[float], np.ndarray],
        k: int = 5,
        collection: Optional[str] = None
    ) -> List[Tuple[float, Dict[str, Any]]]:
        """
        Internal method to search for similar content.

        Args:
            query_embedding: The query embedding vector
            k: Maximum number of results to return
            collection: Optional collection to search in

        Returns:
            List of tuples containing (similarity_score, memory_dict)
        """
        # Convert numpy array to float32 if necessary
        if isinstance(query_embedding, np.ndarray):
            query_embedding = query_embedding.astype(np.float32)

        # Build query
        query = """
            SELECT
                id,
                text,
                metadata,
                created_at,
                vec_distance_cosine(embedding, ?) as score
            FROM memories
            WHERE collection = ?
            ORDER BY score ASC
            LIMIT ?
        """

        # Execute search
        cursor = self.conn.execute(
            query,
            (
                query_embedding,
                collection or self.default_collection,
                k
            )
        )

        # Format results
        results = []
        for row in cursor.fetchall():
            metadata = json.loads(row[2]) if row[2] else {}
            # Convert distance to similarity score (1 - distance)
            similarity = 1.0 - float(row[4])
            results.append((
                similarity,  # similarity score (1 - cosine distance)
                {
                    "id": row[0],
                    "text": row[1],
                    "metadata": metadata,
                    "created_at": row[3],
                }
            ))

        return results

    def get(self, memory_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a specific memory by ID.

        Args:
            memory_id: The ID of the memory to retrieve

        Returns:
            The memory object if found, otherwise None
        """
        cursor = self.conn.execute(
            "SELECT id, text, metadata, created_at FROM memories WHERE id = ?",
            (memory_id,)
        )

        row = cursor.fetchone()
        if not row:
            return None

        return {
            "id": row[0],
            "text": row[1],
            "metadata": json.loads(row[2]) if row[2] else {},
            "created_at": row[3]
        }

    def get_recent_memories(
        self,
        limit: int = 10,
        collection: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get the most recent memories.

        Args:
            limit: Maximum number of memories to return
            collection: Collection to retrieve memories from

        Returns:
            List of memories in reverse chronological order (newest first)
        """
        # Ensure we're sorting by created_at in descending order (newest first)
        cursor = self.conn.execute(
            """
            SELECT id, text, metadata, created_at
            FROM memories
            WHERE collection = ?
            ORDER BY created_at DESC
            LIMIT ?
            """,
            (collection or self.default_collection, limit)
        )

        # Parse results
        results = [
            {
                "id": row[0],
                "text": row[1],
                "metadata": json.loads(row[2]) if row[2] else {},
                "created_at": row[3]
            }
            for row in cursor.fetchall()
        ]

        # Log the result order for debugging
        if results:
            orders = [m.get('metadata', {}).get('order') for m in results]
            logger.debug(f"Recent memories order: {orders}")

        return results

    def __del__(self):
        """Clean up database connection."""
        if hasattr(self, 'conn'):
            self.conn.close()
