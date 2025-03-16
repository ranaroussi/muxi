"""
Command-line interface for the MUXI Framework.

This module provides a modern command-line interface using Click
for interacting with the MUXI Framework.
"""

import asyncio
import sys
from typing import Optional

import click

from src.cli.app import chat_loop, create_agent_from_config
from src.core.orchestrator import Orchestrator
from src.utils import get_version


@click.group()
@click.version_option(get_version(), prog_name="muxi")
def cli_main():
    """MUXI Framework command-line interface."""
    pass


@cli_main.command()
@click.option("--agent-id", default="cli_agent", help="ID for the agent (default: cli_agent)")
@click.option(
    "--no-config", is_flag=True, help="Don't use configuration file, use defaults instead"
)
def chat(agent_id: str, no_config: bool):
    """Start an interactive chat session with an agent."""
    # Create orchestrator
    orchestrator = Orchestrator()

    try:
        # Create agent from config
        create_agent_from_config(orchestrator, agent_id)

        # Run chat loop
        asyncio.run(chat_loop(orchestrator, agent_id))
    except KeyboardInterrupt:
        click.echo("\nInterrupted. Goodbye!")
    except Exception as e:
        click.echo(f"\nError: {str(e)}", err=True)
        sys.exit(1)


@cli_main.command()
@click.option("--host", default="0.0.0.0", help="Host to bind the API server to")
@click.option("--port", default=5050, type=int, help="Port to bind the API server to")
@click.option("--reload", is_flag=True, help="Enable auto-reload for development")
def api(host: str, port: int, reload: bool):
    """Run the API server."""
    from src.api.app import start_api

    click.echo(f"Starting API server on {host}:{port}...")
    start_api(host=host, port=port, reload=reload)


@cli_main.command()
def run():
    """Run both the API server and web UI."""
    from src.__main__ import main

    main()


@cli_main.command()
@click.argument("agent_id")
@click.option("--user-id", help="User ID for multi-user agents")
@click.argument("message")
def send(agent_id: str, message: str, user_id: Optional[str] = None):
    """Send a message to an agent and get a response."""
    from src.core.orchestrator import Orchestrator

    async def send_message():
        orchestrator = Orchestrator()

        # Create agent from config
        create_agent_from_config(orchestrator, agent_id)

        # Send message
        kwargs = {"agent_id": agent_id, "message": message}
        if user_id:
            kwargs["user_id"] = user_id

        response = await orchestrator.chat(**kwargs)
        click.echo(response)

    asyncio.run(send_message())


@cli_main.group()
def create():
    """Create various MUXI resources."""
    pass


@create.command("mcp-server")
@click.option("--output-dir", default="./mcp_servers", help="Directory to create the MCP server in")
@click.option("--name", help="Name for the MCP server")
def create_mcp_server(output_dir: str, name: Optional[str] = None):
    """
    Create a new MCP server through an interactive CLI wizard.

    This command guides you through creating a custom MCP server with
    a chat-like interface, generating all necessary boilerplate code.
    """
    from src.cli.mcp_generator import run_mcp_generator

    try:
        # Run the MCP server generator
        run_mcp_generator(output_dir, name)
        click.echo(f"\nMCP server created successfully in {output_dir}")
    except KeyboardInterrupt:
        click.echo("\nInterrupted. MCP server creation canceled.")
    except Exception as e:
        click.echo(f"\nError: {str(e)}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    cli_main()
