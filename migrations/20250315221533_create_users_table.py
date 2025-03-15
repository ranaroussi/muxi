#!/usr/bin/env python3
"""
@migration: create_users_table
@generated: 2025-03-15 22:15:33
@description: Creates the users table with id and user_id columns
"""


def up() -> str:
    """
    Returns the SQL for the forward migration.

    Returns:
        SQL string to be executed for the up migration
    """
    return """
        -- Enable the pgcrypto extension if not already enabled
        CREATE EXTENSION IF NOT EXISTS pgcrypto;

        -- Drop table if it exists
        DROP TABLE IF EXISTS users CASCADE;

        -- Create the users table
        CREATE TABLE users (
            id SERIAL PRIMARY KEY,
            user_id CHAR(21) NOT NULL UNIQUE
        );

        -- Create an index on user_id for faster lookups
        CREATE INDEX idx_users_user_id ON users(user_id);
    """


def down() -> str:
    """
    Returns the SQL for the rollback migration.

    Returns:
        SQL string to be executed for the down migration
    """
    return """
        -- Drop the users table and related indexes
        DROP INDEX IF EXISTS idx_users_user_id;
        DROP TABLE IF EXISTS users;
    """
