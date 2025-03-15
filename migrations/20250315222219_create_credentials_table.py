#!/usr/bin/env python3
"""
@migration: create_credentials_table
@generated: 2025-03-15 22:22:19
@description: Creates a table for storing user credentials for MCP servers
"""


def up() -> str:
    """
    Returns the SQL for the forward migration.

    Returns:
        SQL string to be executed for the up migration
    """
    return """
        -- Drop table if it exists
        DROP TABLE IF EXISTS credentials CASCADE;

        -- Create the credentials table
        CREATE TABLE credentials (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            credential_id CHAR(21) NOT NULL UNIQUE,
            name VARCHAR(255) NOT NULL,
            service VARCHAR(255) NOT NULL,
            credentials JSONB NOT NULL DEFAULT '{}'::jsonb,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        -- Create indexes for faster lookups
        CREATE INDEX idx_credentials_user_id ON credentials(user_id);
        CREATE INDEX idx_credentials_credential_id ON credentials(credential_id);
        CREATE INDEX idx_credentials_service ON credentials(service);
        CREATE INDEX idx_credentials_created_at ON credentials(created_at);
        CREATE INDEX idx_credentials_updated_at ON credentials(updated_at);

        -- Create a GIN index on the JSONB field for efficient querying of JSON contents
        CREATE INDEX idx_credentials_json ON credentials USING GIN (credentials);
    """


def down() -> str:
    """
    Returns the SQL for the rollback migration.

    Returns:
        SQL string to be executed for the down migration
    """
    return """
        -- Drop the credentials table and related indexes
        DROP INDEX IF EXISTS idx_credentials_user_id;
        DROP INDEX IF EXISTS idx_credentials_credential_id;
        DROP INDEX IF EXISTS idx_credentials_service;
        DROP INDEX IF EXISTS idx_credentials_created_at;
        DROP INDEX IF EXISTS idx_credentials_updated_at;
        DROP INDEX IF EXISTS idx_credentials_json;
        DROP TABLE IF EXISTS credentials;
    """
