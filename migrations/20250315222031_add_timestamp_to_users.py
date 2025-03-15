#!/usr/bin/env python3
"""
@migration: add_timestamp_to_users
@generated: 2025-03-15 22:20:31
@description: Adds created_at and updated_at columns to the users table with indexes
"""


def up() -> str:
    """
    Returns the SQL for the forward migration.

    Returns:
        SQL string to be executed for the up migration
    """
    return """
        -- Add timestamp columns to users table
        ALTER TABLE users ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
        ALTER TABLE users ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;

        -- Add indexes on timestamp columns
        CREATE INDEX IF NOT EXISTS idx_users_created_at ON users(created_at);
        CREATE INDEX IF NOT EXISTS idx_users_updated_at ON users(updated_at);
    """


def down() -> str:
    """
    Returns the SQL for the rollback migration.

    Returns:
        SQL string to be executed for the down migration
    """
    return """
        -- Drop indexes
        DROP INDEX IF EXISTS idx_users_created_at;
        DROP INDEX IF EXISTS idx_users_updated_at;

        -- Drop columns
        ALTER TABLE users DROP COLUMN IF EXISTS created_at;
        ALTER TABLE users DROP COLUMN IF EXISTS updated_at;
    """
