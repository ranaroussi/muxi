#!/usr/bin/env python3
"""
Migration Utility

A simple database migration utility for managing database schema changes.

Usage:
    python migrations/run.py [create|up|down|remove] [name]
"""

import os
import sys
import sqlite3  # Used only for tracking migrations
import importlib.util
import datetime
import glob
from typing import List
import dotenv
import urllib.parse
import psycopg2


class MigrationUtility:
    def __init__(self):
        # Set up paths
        self.migrations_dir = os.path.dirname(os.path.abspath(__file__))
        self.root_dir = os.path.dirname(self.migrations_dir)  # Go up one level to get to the root

        # Ensure migrations directory exists
        if not os.path.exists(self.migrations_dir):
            os.makedirs(self.migrations_dir, exist_ok=True)

        # Load environment variables
        env_path = os.path.join(self.root_dir, '.env')
        dotenv.load_dotenv(env_path)

        # Initialize SQLite database for tracking migrations
        self.init_sqlite_db()

        # Connect to the main PostgreSQL database using POSTGRES_DATABASE_URL
        self.pg_connection = self.connect_to_postgres()

    def connect_to_postgres(self):
        """
        Connect to the PostgreSQL database using POSTGRES_DATABASE_URL from .env file.
        """
        database_url = os.getenv('POSTGRES_DATABASE_URL')

        if not database_url:
            print("[!] POSTGRES_DATABASE_URL not found in .env file. Cannot proceed.")
            sys.exit(1)

        # Parse the POSTGRES_DATABASE_URL
        parsed_url = urllib.parse.urlparse(database_url)

        # Check if it's a PostgreSQL URL
        if parsed_url.scheme not in ['postgres', 'postgresql']:
            print(f"[!] Unsupported database type: {parsed_url.scheme}")
            print("    This migration utility requires a PostgreSQL database.")
            sys.exit(1)

        # Extract connection parameters from the URL
        try:
            username = parsed_url.username
            password = parsed_url.password
            hostname = parsed_url.hostname
            port = parsed_url.port or 5432
            database = parsed_url.path[1:]  # Remove leading slash

            # Connect to PostgreSQL
            conn = psycopg2.connect(
                host=hostname,
                port=port,
                user=username,
                password=password,
                dbname=database
            )
            # Set autocommit to False to use transactions
            conn.autocommit = False
            return conn
        except Exception as e:
            print(f"[!] Failed to connect to PostgreSQL database: {str(e)}")
            sys.exit(1)

    def init_sqlite_db(self) -> None:
        """Initialize the SQLite database used for tracking migrations."""
        sqlite_path = os.path.join(self.migrations_dir, 'migrations.sqlite')
        self.sqlite_db = sqlite3.connect(sqlite_path)
        cursor = self.sqlite_db.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS migrations (
                id INTEGER PRIMARY KEY,
                name TEXT,
                batch INTEGER
            )
        ''')
        self.sqlite_db.commit()

    def create(self, name: str) -> None:
        """
        Create a new migration file.

        Args:
            name: The name of the migration
        """
        timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        created_at = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        filename = f"{timestamp}_{name}.py"

        # Check if a migration with the same name already exists
        existing_files = glob.glob(os.path.join(self.migrations_dir, f"*_{name}.py"))
        if existing_files:
            print(f"[!] A migration with the name '{name}' already exists.")
            return

        # Generate migration content
        content = self.get_migration_template(name, created_at)

        # Write migration file
        file_path = os.path.join(self.migrations_dir, filename)
        with open(file_path, 'w') as f:
            f.write(content)

        print(f"[✓] Migration created: {filename}")

    def up(self) -> None:
        """Run all pending migrations."""
        migrations = self.get_pending_migrations()
        batch = self.get_next_batch_number()

        if not migrations:
            print("No pending migrations.")
            return

        for migration in migrations:
            migration_module = self.load_migration_module(migration)

            if migration_module and hasattr(migration_module, 'up'):
                try:
                    # Get SQL from the migration function
                    sql = migration_module.up()

                    # Execute the SQL in a transaction
                    cursor = self.pg_connection.cursor()
                    cursor.execute(sql)
                    self.pg_connection.commit()

                    # Mark migration as run
                    self.mark_migration_as_run(os.path.basename(migration), batch)
                    print(f"Migrated: {os.path.basename(migration)}")
                except Exception as e:
                    self.pg_connection.rollback()
                    print(f"Error migrating {os.path.basename(migration)}: {str(e)}")
            else:
                print(f"No valid 'up' function found in {os.path.basename(migration)}")

    def down(self) -> None:
        """Roll back the last batch of migrations."""
        last_batch = self.get_last_batch_number()
        migrations = self.get_last_batch_migrations(last_batch)

        if not migrations:
            print("No migrations to roll back.")
            return

        for migration in reversed(migrations):
            migration_module = self.load_migration_module(migration)

            if migration_module and hasattr(migration_module, 'down'):
                try:
                    # Get SQL from the migration function
                    sql = migration_module.down()

                    # Execute the SQL in a transaction
                    cursor = self.pg_connection.cursor()
                    cursor.execute(sql)
                    self.pg_connection.commit()

                    # Remove migration record
                    self.remove_migration_record(os.path.basename(migration))
                    print(f"Rolled back: {os.path.basename(migration)}")
                except Exception as e:
                    self.pg_connection.rollback()
                    print(f"Error rolling back {os.path.basename(migration)}: {str(e)}")
            else:
                print(f"No valid 'down' function found in {os.path.basename(migration)}")

    def remove(self, name: str) -> None:
        """
        Remove a migration file if it hasn't been run yet.

        Args:
            name: The name of the migration to remove
        """
        files = glob.glob(os.path.join(self.migrations_dir, f"*_{name}.py"))

        if not files:
            print(f"[!] No migration found with the name '{name}'.")
            return

        if len(files) > 1:
            print(f"[!] Multiple migrations found with name '{name}'.")
            print("    Please specify the full filename:")
            for file in files:
                print(f"   {os.path.basename(file)}")
            return

        file = files[0]
        filename = os.path.basename(file)

        # Check if the migration has been run
        cursor = self.sqlite_db.cursor()
        cursor.execute("SELECT * FROM migrations WHERE name = ?", (filename,))
        migration = cursor.fetchone()

        if migration:
            print(f"[!] Cannot remove migration '{filename}'.")
            print(f"    It has already been run (batch {migration[2]}).")
            print("    Use the 'down' command to revert it.")
            return

        # Remove the file
        try:
            os.remove(file)
            print(f"[✓] Migration removed: {filename}")
        except Exception as e:
            print(f"[!] Failed to remove migration file: {filename}")
            print(f"    Error: {str(e)}")

    def get_pending_migrations(self) -> List[str]:
        """
        Retrieve all pending migrations.

        Returns:
            A list of pending migration file paths
        """
        files = glob.glob(os.path.join(self.migrations_dir, "*.py"))
        # Filter out the run.py file
        files = [f for f in files if os.path.basename(f) != "run.py"]
        ran_migrations = self.get_ran_migrations()
        return [f for f in files if os.path.basename(f) not in ran_migrations]

    def get_ran_migrations(self) -> List[str]:
        """
        Retrieve all migrations that have been run.

        Returns:
            A list of migration names that have been run
        """
        cursor = self.sqlite_db.cursor()
        cursor.execute("SELECT name FROM migrations")
        return [row[0] for row in cursor.fetchall()]

    def get_next_batch_number(self) -> int:
        """
        Get the next batch number for migrations.

        Returns:
            The next batch number
        """
        cursor = self.sqlite_db.cursor()
        cursor.execute("SELECT MAX(batch) FROM migrations")
        result = cursor.fetchone()[0]
        return 1 if result is None else result + 1

    def get_last_batch_number(self) -> int:
        """
        Get the last batch number of migrations.

        Returns:
            The last batch number
        """
        cursor = self.sqlite_db.cursor()
        cursor.execute("SELECT MAX(batch) FROM migrations")
        result = cursor.fetchone()[0]
        return 0 if result is None else result

    def get_last_batch_migrations(self, batch: int) -> List[str]:
        """
        Retrieve migrations from the last batch.

        Args:
            batch: The batch number

        Returns:
            A list of migration file paths from the specified batch
        """
        cursor = self.sqlite_db.cursor()
        cursor.execute("SELECT name FROM migrations WHERE batch = ?", (batch,))
        migrations = [row[0] for row in cursor.fetchall()]
        return [os.path.join(self.migrations_dir, name) for name in migrations]

    def mark_migration_as_run(self, migration: str, batch: int) -> None:
        """
        Mark a migration as run in the database.

        Args:
            migration: The migration filename
            batch: The batch number
        """
        cursor = self.sqlite_db.cursor()
        cursor.execute("INSERT INTO migrations (name, batch) VALUES (?, ?)", (migration, batch))
        self.sqlite_db.commit()

    def remove_migration_record(self, migration: str) -> None:
        """
        Remove a migration record from the database.

        Args:
            migration: The migration filename
        """
        cursor = self.sqlite_db.cursor()
        cursor.execute("DELETE FROM migrations WHERE name = ?", (migration,))
        self.sqlite_db.commit()

    def load_migration_module(self, migration_path: str):
        """
        Load a migration module dynamically.

        Args:
            migration_path: Path to the migration file

        Returns:
            The loaded module or None if loading fails
        """
        try:
            spec = importlib.util.spec_from_file_location("migration_module", migration_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return module
        except Exception as e:
            print(f"Error loading migration {os.path.basename(migration_path)}: {str(e)}")
            return None

    def get_migration_template(self, name: str, created_at: str) -> str:
        """
        Generate the content for a new migration file.

        Args:
            name: The name of the migration
            created_at: The creation timestamp

        Returns:
            The content of the migration file
        """
        return f'''#!/usr/bin/env python3
"""
@migration: {name}
@generated: {created_at}
@description: ...
"""


def up() -> str:
    """
    Returns the SQL for the forward migration.

    Returns:
        SQL string to be executed for the up migration
    """
    return """
        -- Your SQL for the 'up' migration
        -- For example:
        -- CREATE TABLE users (
        --     id SERIAL PRIMARY KEY,
        --     username VARCHAR(255) NOT NULL UNIQUE,
        --     email VARCHAR(255) NOT NULL UNIQUE,
        --     password_hash VARCHAR(255) NOT NULL,
        --     first_name VARCHAR(255),
        --     last_name VARCHAR(255),
        --     is_active BOOLEAN NOT NULL DEFAULT TRUE,
        --     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        --     updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        -- );
        --
        -- CREATE INDEX idx_users_username ON users(username);
        -- CREATE INDEX idx_users_email ON users(email);
    """

def down() -> str:
    """
    Returns the SQL for the rollback migration.

    Returns:
        SQL string to be executed for the down migration
    """
    return """
        -- Your SQL for the 'down' migration
        -- For example:
        -- DROP INDEX IF EXISTS idx_users_email;
        -- DROP INDEX IF EXISTS idx_users_username;
        -- DROP TABLE IF EXISTS users;
    """
'''


def main():
    """Main entry point for the migration utility."""
    if len(sys.argv) < 2:
        print("Usage: python migrations/run.py [create|up|down|remove] [name]")
        sys.exit(1)

    command = sys.argv[1].lower()
    utility = MigrationUtility()

    if command == "create":
        if len(sys.argv) < 3:
            print("Error: Migration name is required for 'create' command.")
            print("Usage: python migrations/run.py create [name]")
            sys.exit(1)
        utility.create(sys.argv[2])
    elif command == "up":
        utility.up()
    elif command == "down":
        utility.down()
    elif command == "remove":
        if len(sys.argv) < 3:
            print("Error: Migration name is required for 'remove' command.")
            print("Usage: python migrations/run.py remove [name]")
            sys.exit(1)
        utility.remove(sys.argv[2])
    else:
        print(f"Unknown command: {command}")
        print("Available commands: create, up, down, remove")
        sys.exit(1)


if __name__ == "__main__":
    main()
