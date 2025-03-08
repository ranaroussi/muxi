"""
Script to run database migrations.

This script executes SQL migration files in the migrations directory
in order based on their filenames.
"""

import argparse
import glob
import os
from pathlib import Path
from typing import List, Optional

import psycopg2
from dotenv import load_dotenv
from loguru import logger

load_dotenv()


def get_migration_files() -> List[str]:
    """Get all migration files sorted by name."""
    migrations_dir = Path(__file__).parent
    files = glob.glob(os.path.join(migrations_dir, "*.sql"))
    return sorted(files)


def get_db_connection():
    """Get a connection to the PostgreSQL database."""
    conn = psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port=os.getenv("POSTGRES_PORT", "5432"),
        database=os.getenv("POSTGRES_DB", "postgres"),
        user=os.getenv("POSTGRES_USER", "postgres"),
        password=os.getenv("POSTGRES_PASSWORD", "postgres"),
    )
    conn.autocommit = False
    return conn


def run_migration(conn, file_path: str) -> None:
    """Run a single migration file."""
    logger.info(f"Running migration: {os.path.basename(file_path)}")

    with open(file_path, "r") as f:
        sql = f.read()

    cursor = conn.cursor()
    try:
        cursor.execute(sql)
        conn.commit()
        logger.success(f"Successfully applied {os.path.basename(file_path)}")
    except Exception as e:
        conn.rollback()
        logger.error(f"Error running migration {os.path.basename(file_path)}: {str(e)}")
        raise
    finally:
        cursor.close()


def run_migrations(specific_file: Optional[str] = None) -> None:
    """Run all migrations or a specific migration file."""
    conn = get_db_connection()

    try:
        if specific_file:
            run_migration(conn, specific_file)
        else:
            migration_files = get_migration_files()
            for file_path in migration_files:
                run_migration(conn, file_path)
    finally:
        conn.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run database migrations")
    parser.add_argument("--file", help="Run a specific migration file", required=False)

    args = parser.parse_args()

    logger.info("Starting migrations")
    run_migrations(args.file)
    logger.info("Migrations completed")
