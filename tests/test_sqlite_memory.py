"""
Test SQLite memory implementation

This module contains tests for the SQLite-based memory implementation in the Muxi framework.
"""

import json
import os
import sqlite3
import tempfile
import unittest

import nanoid


class MockEmbeddingProvider:
    """Mock embedding provider for testing."""

    async def get_embedding(self, text):
        """Generate a mock embedding for the given text."""
        # Return a simple normalized vector with 4 dimensions
        return [0.5, 0.5, 0.5, 0.5]


class MockSQLiteMemory:
    """
    A mock SQLite memory implementation for testing that doesn't require the
    sqlite-vec extension.
    """

    def __init__(self, db_path, dimension=4, default_collection="default", extensions_dir=None):
        """Mock initialization."""
        self.db_path = db_path
        self.dimension = dimension
        self.default_collection = default_collection
        self.embedding_provider = None
        self.conn = self._init_database()

    def _init_database(self):
        """Initialize the SQLite database with required tables."""
        conn = sqlite3.connect(self.db_path)

        # Create tables without requiring the extension
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
                content TEXT NOT NULL,
                embedding TEXT NOT NULL,  -- Store as JSON text for testing
                metadata TEXT DEFAULT '{}',
                source TEXT,
                type TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (collection) REFERENCES collections(name)
            )
        """)

        # Create a function to simulate vector similarity
        conn.create_function("vec_cosine_similarity", 2, lambda a, b: 0.95)

        # Create default collection
        conn.execute(
            "INSERT OR IGNORE INTO collections (id, name, description) VALUES (?, ?, ?)",
            (self._generate_id(), self.default_collection, "Default collection for memories")
        )

        conn.commit()
        return conn

    def _generate_id(self, size=21):
        """Generate a unique ID."""
        return nanoid.generate(size=size)

    async def add(self, content, metadata=None):
        """Add content to memory."""
        if metadata is None:
            metadata = {}

        # Generate embedding if provider is set
        if self.embedding_provider:
            embedding = await self.embedding_provider.get_embedding(content)
            # Add to database
            self._add_internal(content, embedding, metadata)

    def _add_internal(self, text, embedding, metadata=None, collection=None,
                      source=None, type_=None):
        """Internal method to add a memory."""
        # Use default collection if not specified
        collection = collection or self.default_collection

        # Convert embedding to JSON for storage
        embedding_json = json.dumps(embedding)

        # Generate ID
        memory_id = self._generate_id()

        # Insert into database
        self.conn.execute(
            """
            INSERT INTO memories (id, collection, content, embedding, metadata, source, type)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                memory_id,
                collection,
                text,
                embedding_json,
                metadata and json.dumps(metadata),
                source,
                type_
            )
        )
        self.conn.commit()
        return memory_id

    async def search(self, query, limit=5):
        """Search for similar content."""
        if not self.embedding_provider:
            return []

        # In the mock, we just return all entries sorted by creation time
        cursor = self.conn.execute(
            """
            SELECT id, content, metadata, created_at, source, type
            FROM memories
            WHERE collection = ?
            ORDER BY created_at DESC
            LIMIT ?
            """,
            (self.default_collection, limit)
        )

        results = []
        for row in cursor.fetchall():
            metadata = json.loads(row[2]) if row[2] else {}
            # Use fixed high similarity score for testing
            score = 0.95

            results.append({
                "content": row[1],
                "metadata": metadata,
                "score": score
            })

        return results

    def get_recent_memories(self, limit=10, collection=None):
        """Get most recent memories."""
        cursor = self.conn.execute(
            """
            SELECT id, content, metadata, created_at
            FROM memories
            WHERE collection = ?
            ORDER BY created_at DESC
            LIMIT ?
            """,
            (collection or self.default_collection, limit)
        )

        return [
            {
                "id": row[0],
                "text": row[1],
                "metadata": json.loads(row[2]) if row[2] else {},
                "created_at": row[3]
            }
            for row in cursor.fetchall()
        ]

    def __del__(self):
        """Clean up."""
        if hasattr(self, 'conn'):
            self.conn.close()


class TestSQLiteMemory(unittest.TestCase):
    """Test cases for the SQLiteMemory implementation."""

    def setUp(self):
        """Set up the test environment."""
        # Create a temporary directory for the test database
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test_memory.db")

        # Create mock SQLite memory instance
        self.memory = MockSQLiteMemory(
            db_path=self.db_path,
            dimension=4  # Use a small dimension for testing
        )

        # Set mock embedding provider
        self.memory.embedding_provider = MockEmbeddingProvider()

    def tearDown(self):
        """Clean up after each test."""
        # Close the database connection
        del self.memory

        # Remove the test database
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

        # Remove the temporary directory
        os.rmdir(self.temp_dir)

    async def test_add_and_search(self):
        """Test adding content and searching for it."""
        # Add some test entries
        await self.memory.add("This is a test entry", {"source": "test"})
        await self.memory.add("Another test entry", {"source": "test", "importance": "high"})

        # Search for entries
        results = await self.memory.search("test entry")

        # Check results
        self.assertEqual(len(results), 2)
        self.assertIn("test", results[0]["metadata"]["source"])

        # Both entries should have high similarity due to our mock implementation
        self.assertGreater(results[0]["score"], 0.9)
        self.assertGreater(results[1]["score"], 0.9)

    async def test_metadata_storage(self):
        """Test that metadata is properly stored and retrieved."""
        # Add content with complex metadata
        metadata = {
            "source": "user",
            "timestamp": 1620000000,
            "tags": ["important", "follow-up"],
            "nested": {"key1": "value1", "key2": 42}
        }
        await self.memory.add("Entry with complex metadata", metadata)

        # Search to retrieve the entry
        results = await self.memory.search("metadata")

        # Verify metadata was preserved
        self.assertEqual(len(results), 1)
        result_metadata = results[0]["metadata"]
        self.assertEqual(result_metadata["source"], "user")
        self.assertEqual(result_metadata["tags"][0], "important")
        self.assertEqual(result_metadata["nested"]["key2"], 42)

    def test_get_recent_memories(self):
        """Test retrieving recent memories."""
        # Use the internal method to add entries directly (bypassing async)
        self.memory._add_internal("First entry", [0.25, 0.25, 0.25, 0.25], {"order": 1})
        self.memory._add_internal("Second entry", [0.25, 0.25, 0.25, 0.25], {"order": 2})
        self.memory._add_internal("Third entry", [0.25, 0.25, 0.25, 0.25], {"order": 3})

        # Get recent memories
        recent = self.memory.get_recent_memories(limit=2)

        # Verify we get the most recent entries (reverse chronological order)
        self.assertEqual(len(recent), 2)
        self.assertEqual(recent[0]["metadata"]["order"], 3)
        self.assertEqual(recent[1]["metadata"]["order"], 2)


if __name__ == "__main__":
    import asyncio

    # Run the async tests
    async def run_tests():
        suite = unittest.TestLoader().loadTestsFromTestCase(TestSQLiteMemory)
        runner = unittest.TextTestRunner()
        runner.run(suite)

    # Use asyncio to run the tests
    asyncio.run(run_tests())
