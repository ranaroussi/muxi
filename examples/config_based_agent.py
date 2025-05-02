"""
Config-based agent example with the MUXI Framework.

This example demonstrates how to create agents from YAML/JSON configuration files.
"""

import asyncio
from pathlib import Path

from dotenv import load_dotenv

from muxi import muxi


# Load environment variables from .env file
load_dotenv()


async def main():
    """Run the config-based agent example."""
    print("=== Config-based Agent Example ===\n")

    # Create the MUXI app
    app = muxi(
        buffer_size=10,           # Context window size
        buffer_multiplier=10,     # Total capacity = 10 × 10 = 100 messages
    )

    # Determine the correct path to the config file
    examples_dir = Path(__file__).parent
    config_path = examples_dir / "configs" / "assistant.yaml"

    print(f"Loading agent from config file: {config_path}")

    # Add agent from config file
    await app.add_agent("assistant", str(config_path))

    # Get a reference to the agent for manual use
    agent = app.get_agent("assistant")
    print(f"Agent loaded successfully: {agent.name}")
    print(f"MCP Servers: {list(agent.mcp_servers.keys())}")

    # Chat with the agent
    print("\n--- Conversation ---")

    # Ask a general question
    question1 = "Tell me a fun fact about AI."
    response = await app.chat(message=question1, agent_name="assistant")
    print(f"User: {question1}")
    print(f"Agent: {response}")

    # Ask a question that might use web search
    question2 = "What is the tallest mountain in the world?"
    response = await app.chat(message=question2, agent_name="assistant")
    print(f"\nUser: {question2}")
    print(f"Agent: {response}")

    # Ask a math question that might use the calculator
    question3 = "What is the square root of 169?"
    response = await app.chat(message=question3, agent_name="assistant")
    print(f"\nUser: {question3}")
    print(f"Agent: {response}")

    print("\n=== Example Completed ===")


if __name__ == "__main__":
    asyncio.run(main())
