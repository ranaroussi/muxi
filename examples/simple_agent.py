"""
Simple agent example with the MUXI Framework.

This example demonstrates how to create a simple agent with memory, tools, and a large language model.
"""

import asyncio
import os

from dotenv import load_dotenv

from muxi.core.orchestrator import Orchestrator
from muxi.core.memory import BufferMemory
from muxi.core.models import OpenAIModel
from muxi.core.tools.calculator import CalculatorTool
from muxi.core.tools.web_search import WebSearchTool

# Load environment variables from .env file
load_dotenv()

async def main():
    # Create an LLM model instance
    model = OpenAIModel(
        api_key=os.getenv("OPENAI_API_KEY"),
        model="gpt-4o",
        temperature=0.7,
    )

    # Create tools
    calculator = CalculatorTool()
    web_search = WebSearchTool()

    # Create a memory system
    memory = BufferMemory(max_tokens=4000)

    # Create an orchestrator (manages agents)
    orchestrator = Orchestrator()

    # Add an agent
    orchestrator.add_agent(
        agent_id="assistant",
        system_message="You are a helpful assistant.",
        tools=[calculator, web_search],
        memory=memory,
        model=model,
    )

    # Chat with the agent
    response = await orchestrator.process_message(
        "What is the weather like in New York City today?",
        agent_id="assistant",
    )
    print(f"Agent: {response.content}")

    # Demonstrate conversation memory
    response = await orchestrator.process_message(
        "What about tomorrow?",
        agent_id="assistant",
    )
    print(f"Agent: {response.content}")

    # Demonstrate tool usage
    response = await orchestrator.process_message(
        "What is the square root of 144?",
        agent_id="assistant",
    )
    print(f"Agent: {response.content}")

if __name__ == "__main__":
    asyncio.run(main())
