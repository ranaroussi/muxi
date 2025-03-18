"""
Simple agent example with the MUXI Framework.

This example demonstrates how to create a simple agent with memory and a language model
that connects to MCP servers for specialized capabilities.
"""

import asyncio
import os

from dotenv import load_dotenv

from muxi.core.orchestrator import Orchestrator
from muxi.server.memory.buffer import BufferMemory
from muxi.models.providers.openai import OpenAIModel

# Load environment variables from .env file
load_dotenv()


async def main():
    # Create an LLM model instance
    model = OpenAIModel(
        api_key=os.getenv("OPENAI_API_KEY"),
        model="gpt-4o",
        temperature=0.7,
    )

    # Create a memory system
    memory = BufferMemory(max_size=100)

    # Create an orchestrator (manages agents)
    orchestrator = Orchestrator()

    # Add an agent
    agent = orchestrator.create_agent(
        agent_id="assistant",
        system_message="You are a helpful assistant.",
        memory=memory,
        model=model,
    )

    # Connect to MCP servers
    await agent.connect_mcp_server(
        name="calculator",
        url="http://localhost:5001",
        credentials={"api_key": os.getenv("CALCULATOR_API_KEY")}
    )

    await agent.connect_mcp_server(
        name="web_search",
        url="http://localhost:5002",
        credentials={"api_key": os.getenv("SEARCH_API_KEY")}
    )

    # Chat with the agent
    weather_message = "What is the weather like in New York City today?"
    response = await agent.process_message(weather_message)
    print(f"Agent: {response.content}")

    # Demonstrate conversation memory
    followup_message = "What about tomorrow?"
    response = await agent.process_message(followup_message)
    print(f"Agent: {response.content}")

    # Demonstrate MCP server usage
    math_message = "What is the square root of 144?"
    response = await agent.process_message(math_message)
    print(f"Agent: {response.content}")

if __name__ == "__main__":
    asyncio.run(main())
