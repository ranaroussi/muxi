"""
CLI module for the AI Agent Framework.

This module provides a command-line interface for interacting with agents.
"""

from src.cli.commands import cli_main

# For backward compatibility
def run_cli():
    """
    Run the CLI application.

    This function maintains backward compatibility with the old CLI.
    New code should use cli_main() from commands module.
    """
    from src.cli.commands import chat
    chat(agent_id="cli_agent", no_config=False)

__all__ = ["run_cli", "cli_main"]
