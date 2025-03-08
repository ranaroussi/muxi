"""
Command-line interface for the AI Agent Framework.

This module provides a rich command-line interface for interacting with
agents created with the AI Agent Framework.
"""

import argparse
import asyncio

from dotenv import load_dotenv
from rich.console import Console
from rich.markdown import Markdown
from rich.prompt import Prompt
from rich.table import Table
from rich.text import Text

from src.config import config
from src.core.orchestrator import Orchestrator
from src.memory.buffer import BufferMemory
from src.memory.long_term import LongTermMemory
from src.models import OpenAIModel
from src.tools.calculator import Calculator
from src.tools.web_search import WebSearch
from src.utils import get_version

console = Console()


def create_agent_from_config(orchestrator: Orchestrator, agent_id: str) -> None:
    """
    Create an agent from the configuration.

    Args:
        orchestrator: The orchestrator to register the agent with.
        agent_id: The ID of the agent to create.
    """
    # Get LLM configuration
    model_config = config.model

    # Create LLM
    model = OpenAIModel(
        api_key=model_config.api_key,
        model=model_config.model,
        temperature=model_config.temperature,
    )

    # Create memory
    buffer_memory = BufferMemory(
        dimension=model_config.embedding_dimension,
        max_size=config.memory.buffer_max_size,
    )

    # Create long-term memory if enabled
    long_term_memory = None
    if config.memory.use_long_term:
        long_term_memory = LongTermMemory(
            connection_string=config.database.connection_string,
            collection_name=config.memory.collection_name,
        )

    # Create tools
    tools = []

    # Load tools based on configuration
    if config.tools.enable_calculator:
        tools.append(Calculator())

    if config.tools.enable_web_search:
        tools.append(WebSearch())

    # Create agent
    orchestrator.create_agent(
        agent_id=agent_id,
        model=model,
        buffer_memory=buffer_memory,
        long_term_memory=long_term_memory,
        tools=tools,
        system_message=config.app.system_message,
        set_as_default=True,
    )


async def chat_loop(orchestrator: Orchestrator, agent_id: str) -> None:
    """
    Run the chat loop with the agent.

    Args:
        orchestrator: The orchestrator containing the agent.
        agent_id: The ID of the agent to chat with.
    """
    welcome_text = f"""# AI Agent Framework CLI

You are now chatting with an AI agent ({agent_id}).
Type `/help` for available commands or `/exit` to quit.
"""
    console.print(Markdown(welcome_text))

    agent = orchestrator.get_agent(agent_id)
    if not agent:
        console.print(f"[bold red]Error:[/bold red] Agent '{agent_id}' not found.")
        return

    tools_list = agent.get_available_tools()

    # Show available tools
    if tools_list:
        tools_table = Table(title="Available Tools")
        tools_table.add_column("Name")
        tools_table.add_column("Description")

        for tool in tools_list:
            tools_table.add_row(tool["name"], tool["description"])

        console.print(tools_table)

    # Chat loop
    while True:
        # Get user input
        user_input = Prompt.ask("\n[bold cyan]You[/bold cyan]")

        # Process commands
        if user_input.startswith("/"):
            command = user_input[1:].lower()

            if command in ["exit", "quit", "bye"]:
                console.print("[bold yellow]Goodbye![/bold yellow]")
                break

            elif command == "help":
                help_text = """
## Available Commands

- `/exit`, `/quit`, `/bye` - Exit the chat
- `/help` - Show this help message
- `/clear` - Clear the screen
- `/memory <query>` - Search the agent's memory
- `/tools` - List available tools
                """
                console.print(Markdown(help_text))
                continue

            elif command == "clear":
                console.clear()
                continue

            elif command.startswith("memory "):
                query = command[7:].strip()
                if query:
                    with console.status("[bold green]Searching memory...[/bold green]"):
                        memories = await agent.search_memory(query)

                    if memories:
                        memory_table = Table(title=f"Memory Results for '{query}'")
                        memory_table.add_column("Text")
                        memory_table.add_column("Source")
                        memory_table.add_column("Distance")

                        for memory in memories:
                            memory_table.add_row(
                                Text(memory["text"], overflow="fold"),
                                memory["source"],
                                f"{memory['distance']:.4f}",
                            )

                        console.print(memory_table)
                    else:
                        console.print("[yellow]No memories found.[/yellow]")
                else:
                    console.print("[bold red]Error:[/bold red] Please provide a search query.")
                continue

            elif command == "tools":
                if tools_list:
                    tools_table = Table(title="Available Tools")
                    tools_table.add_column("Name")
                    tools_table.add_column("Description")

                    for tool in tools_list:
                        tools_table.add_row(tool["name"], tool["description"])

                    console.print(tools_table)
                else:
                    console.print("[yellow]No tools available.[/yellow]")
                continue

            else:
                console.print(f"[bold red]Unknown command:[/bold red] {command}")
                continue

        # Process regular message
        with console.status("[bold green]Agent is thinking...[/bold green]"):
            try:
                response = await orchestrator.run(user_input)
                console.print("\n[bold green]Agent:[/bold green]")
                console.print(Markdown(response))
            except Exception as e:
                console.print(f"[bold red]Error:[/bold red] {str(e)}")


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="AI Agent Framework CLI")
    parser.add_argument(
        "--agent-id", type=str, default="cli_agent", help="ID for the agent (default: cli_agent)"
    )
    parser.add_argument(
        "--no-config",
        action="store_true",
        help="Don't use configuration file, use defaults instead",
    )
    parser.add_argument("--version", action="store_true", help="Show the version and exit")
    return parser.parse_args()


async def run_cli_async() -> None:
    """Run the CLI application asynchronously."""
    # Parse arguments
    args = parse_args()

    # Show version and exit if requested
    if args.version:
        version_str = f"AI Agent Framework version [bold]{get_version()}[/bold]"
        console.print(version_str)
        return

    # Load environment variables
    load_dotenv()

    # Create orchestrator
    orchestrator = Orchestrator()

    try:
        # Create agent from config
        create_agent_from_config(orchestrator, args.agent_id)

        # Run chat loop
        await chat_loop(orchestrator, args.agent_id)
    except KeyboardInterrupt:
        console.print("\n[bold yellow]Interrupted. Goodbye![/bold yellow]")
    except Exception as e:
        console.print(f"\n[bold red]Error:[/bold red] {str(e)}")


def run_cli() -> None:
    """Run the CLI application."""
    try:
        asyncio.run(run_cli_async())
    except KeyboardInterrupt:
        console.print("\n[bold yellow]Interrupted. Goodbye![/bold yellow]")
