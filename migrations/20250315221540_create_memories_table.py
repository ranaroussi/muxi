#!/usr/bin/env python3
"""
@migration: create_memories_table
@generated: 2025-03-15 22:15:40
@description: Creates the memories table with pgvector support for storing user memories
"""


def up() -> str:
    """
    Returns the SQL for the forward migration.

    Returns:
        SQL string to be executed for the up migration
    """
    return """
        -- Enable the pgvector extension if not already enabled
        CREATE EXTENSION IF NOT EXISTS vector;

        -- Drop table if it exists
        DROP TABLE IF EXISTS memories CASCADE;

        -- Create the memories table
        CREATE TABLE memories (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            memory_id CHAR(21) NOT NULL UNIQUE,
            collection_id INTEGER REFERENCES collections(id) ON DELETE SET NULL,
            content TEXT NOT NULL,
            metadata JSONB DEFAULT '{}'::jsonb,
            embedding vector(1536),
            source VARCHAR(255),
            type VARCHAR(50),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        -- Create an index for vector similarity search
        CREATE INDEX memories_embedding_idx
        ON memories USING ivfflat (embedding vector_cosine_ops)
        WITH (lists = 100);

        -- Create indexes for faster lookups
        CREATE INDEX idx_memories_user_id ON memories(user_id);
        CREATE INDEX idx_memories_memory_id ON memories(memory_id);
        CREATE INDEX idx_memories_collection_id ON memories(collection_id);
        CREATE INDEX idx_memories_source ON memories(source);
        CREATE INDEX idx_memories_type ON memories(type);
        CREATE INDEX idx_memories_created_at ON memories(created_at);
    """


def down() -> str:
    """
    Returns the SQL for the rollback migration.

    Returns:
        SQL string to be executed for the down migration
    """
    return """
        -- Drop the memories table and related indexes
        DROP INDEX IF EXISTS memories_embedding_idx;
        DROP INDEX IF EXISTS idx_memories_user_id;
        DROP INDEX IF EXISTS idx_memories_memory_id;
        DROP INDEX IF EXISTS idx_memories_collection_id;
        DROP INDEX IF EXISTS idx_memories_source;
        DROP INDEX IF EXISTS idx_memories_type;
        DROP INDEX IF EXISTS idx_memories_created_at;
        DROP TABLE IF EXISTS memories;

        -- Note: We don't drop the vector extension as it might be used by other tables
    """
