#!/usr/bin/env python3
"""
@migration: create_collections_table
@generated: 2025-03-15 22:15:37
@description: Creates the collections table that belongs to users
"""


def up() -> str:
    """
    Returns the SQL for the forward migration.

    Returns:
        SQL string to be executed for the up migration
    """
    return """
        -- Drop table if it exists
        DROP TABLE IF EXISTS collections CASCADE;

        -- Create the collections table
        CREATE TABLE collections (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            collection_id CHAR(21) NOT NULL UNIQUE,
            name VARCHAR(255) NOT NULL,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        -- Create indexes for faster lookups
        CREATE INDEX idx_collections_user_id ON collections(user_id);
        CREATE INDEX idx_collections_collection_id ON collections(collection_id);
    """


def down() -> str:
    """
    Returns the SQL for the rollback migration.

    Returns:
        SQL string to be executed for the down migration
    """
    return """
        -- Drop the collections table and related indexes
        DROP INDEX IF EXISTS idx_collections_collection_id;
        DROP INDEX IF EXISTS idx_collections_user_id;
        DROP TABLE IF EXISTS collections;
    """
