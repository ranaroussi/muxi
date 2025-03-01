"""
Main entry point for the CLI when run as a module.

This allows running the CLI with:
python -m src.cli
"""

from src.cli.commands import cli_main

if __name__ == "__main__":
    cli_main()
