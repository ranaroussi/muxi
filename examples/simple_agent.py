"""
Simple example of using the AI Agent Framework.

This script demonstrates how to create and use a simple agent with the
AI Agent Framework.
"""

import asyncio
import os

from dotenv import load_dotenv

from src.core.orchestrator import Orchestrator
from src.memory.buffer import BufferMemory
from src.models import OpenAIModel
from src.tools.calculator import CalculatorTool
from src.tools.web_search import WebSearchTool


async def main():
    """Run the example."""
    # Load environment variables from .env file
    load_dotenv()

    # Check for API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError(
            "OPENAI_API_KEY environment variable not set. "
            "Please set it in a .env file or in your environment."
        )

    # Create language model
    model = OpenAIModel(
        api_key=api_key,
        model="gpt-4o",  # You can change this to any supported model
    )

    # Create memory
    memory = BufferMemory(
        dimension=1536,  # OpenAIModel embeddings dimension
        max_size=100,  # Maximum number of items to store
    )

    # Create tools
    tools = [
        WebSearchTool(),
        CalculatorTool(),
    ]

    # Create orchestrator
    orchestrator = Orchestrator()

    # Create agent
    orchestrator.create_agent(
        agent_id="simple_agent",
        model=model,
        buffer_memory=memory,
        tools=tools,
        system_message=(
            "You are a helpful AI assistant. You can search the web and "
            "perform calculations to help answer questions."
        ),
        set_as_default=True,
    )

    print("Agent created! You can now chat with it.")
    print("Type 'exit' to quit.")

    # Chat loop
    while True:
        # Get user input
        user_input = input("\nYou: ")

        # Check for exit command
        if user_input.lower() in ["exit", "quit", "bye"]:
            print("Goodbye!")
            break

        # Process input
        print("\nAgent: ", end="")
        response = await orchestrator.run(user_input)
        print(response)


if __name__ == "__main__":
    asyncio.run(main())
