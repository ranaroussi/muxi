#!/usr/bin/env python3
"""
Multi-agent example with the MUXI Framework.

This example demonstrates how to create multiple specialized agents and how
the orchestrator automatically routes messages to the most appropriate agent.
"""

import asyncio

from dotenv import load_dotenv

from muxi import muxi

# Load environment variables
load_dotenv()


async def main():
    # Create a new MUXI instance
    app = muxi(
        buffer_size=10,  # Context window size
        buffer_multiplier=10,  # Total capacity = 10 × 10 = 100 messages
    )

    # Add multiple agents with different specializations
    await app.add_agent("weather", "configs/weather_agent.yaml")
    await app.add_agent("finance", "configs/finance_agent.json")
    await app.add_agent("travel", "configs/travel_agent.yaml")

    # The orchestrator will automatically select the most appropriate agent
    print("\n--- Weather Question ---")
    response = await app.chat("What's the weather forecast for Tokyo this weekend?")
    print(f"Selected Agent: {response.agent_id}")
    print(f"Response: {response.content}")

    print("\n--- Finance Question ---")
    response = await app.chat("Should I invest in tech stocks right now?")
    print(f"Selected Agent: {response.agent_id}")
    print(f"Response: {response.content}")

    print("\n--- Travel Question ---")
    response = await app.chat("What are the best attractions in Barcelona?")
    print(f"Selected Agent: {response.agent_id}")
    print(f"Response: {response.content}")

    print("\n--- General Question ---")
    response = await app.chat("Who was Albert Einstein?")
    print(f"Selected Agent: {response.agent_id}")
    print(f"Response: {response.content}")


if __name__ == "__main__":
    asyncio.run(main())
