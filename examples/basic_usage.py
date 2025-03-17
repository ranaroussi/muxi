"""
Basic usage example of the MUXI Framework.

This example demonstrates the simplest way to use the MUXI Framework.
"""

import asyncio
import os

from dotenv import load_dotenv

from muxi.core.orchestrator import Orchestrator
from muxi.core.models.providers.openai import OpenAIModel


# Load environment variables
load_dotenv()


async def main():
    # Create an OpenAI model
    model = OpenAIModel(
        api_key=os.getenv("OPENAI_API_KEY"),
        model="gpt-4o",
        temperature=0.7,
    )

    # Create an orchestrator
    orchestrator = Orchestrator()

    # Add a basic agent with default memory and no tools
    orchestrator.add_agent(
        agent_id="basic_agent",
        system_message="You are a helpful AI assistant.",
        model=model,
    )

    # Chat with the agent
    response = await orchestrator.process_message(
        "Hello, who are you?",
        agent_id="basic_agent",
    )
    print(f"Agent: {response.content}")

    # Continue the conversation
    response = await orchestrator.process_message(
        "What can you tell me about the MUXI Framework?",
        agent_id="basic_agent",
    )
    print(f"Agent: {response.content}")


if __name__ == "__main__":
    asyncio.run(main())
