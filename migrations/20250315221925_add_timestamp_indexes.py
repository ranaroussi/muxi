#!/usr/bin/env python3
"""
@migration: add_timestamp_indexes
@generated: 2025-03-15 22:19:25
@description: Adds timestamp and name indexes to improve query performance
"""


def up() -> str:
    """
    Returns the SQL for the forward migration.

    Returns:
        SQL string to be executed for the up migration
    """
    return """
        -- Add timestamp indexes to collections table
        CREATE INDEX IF NOT EXISTS idx_collections_created_at ON collections(created_at);
        CREATE INDEX IF NOT EXISTS idx_collections_updated_at ON collections(updated_at);
        CREATE INDEX IF NOT EXISTS idx_collections_name ON collections(name);

        -- Add timestamp indexes to memories table
        CREATE INDEX IF NOT EXISTS idx_memories_updated_at ON memories(updated_at);

        -- Add composite index for user's memories by date (common query pattern)
        CREATE INDEX IF NOT EXISTS idx_memories_user_created_at ON memories(user_id, created_at);
    """


def down() -> str:
    """
    Returns the SQL for the rollback migration.

    Returns:
        SQL string to be executed for the down migration
    """
    return """
        -- Drop collections indexes
        DROP INDEX IF EXISTS idx_collections_created_at;
        DROP INDEX IF EXISTS idx_collections_updated_at;
        DROP INDEX IF EXISTS idx_collections_name;

        -- Drop memories indexes
        DROP INDEX IF EXISTS idx_memories_updated_at;
        DROP INDEX IF EXISTS idx_memories_user_created_at;
    """
