#!/usr/bin/env python3
"""
Multi-agent example with intelligent routing.

This example demonstrates how to create multiple specialized agents and
use the intelligent routing system to automatically direct messages to
the most appropriate agent based on their content.
"""

import asyncio
from dotenv import load_dotenv
from src import muxi

# Load environment variables from .env file
load_dotenv()


async def main():
    """Run the multi-agent example."""
    # Create a new MUXI application
    app = muxi()

    # Add specialized agents from configuration files
    app.add_agent("weather", "examples/configs/weather_agent.yaml")
    app.add_agent("finance", "examples/configs/finance_agent.json")

    # Start the server
    await app.start_server(port=5000)

    print("\n=== Multi-Agent System with Intelligent Routing ===\n")

    # Example 1: Weather-related query
    weather_query = "What's the weather forecast for New York this weekend?"
    print(f"User: {weather_query}")
    response = await app.chat(weather_query)
    print(f"Agent: {response}\n")

    # Example 2: Finance-related query
    finance_query = "Should I invest in tech stocks or bonds right now?"
    print(f"User: {finance_query}")
    response = await app.chat(finance_query)
    print(f"Agent: {response}\n")

    # Example 3: Ambiguous query that could go to either agent
    ambiguous_query = "How will the hurricane affect the stock market?"
    print(f"User: {ambiguous_query}")
    response = await app.chat(ambiguous_query)
    print(f"Agent: {response}\n")

    # Example 4: Direct query to a specific agent
    direct_query = "What's your opinion on cryptocurrency?"
    print(f"User: {direct_query} (directed to finance agent)")
    response = await app.chat(direct_query, agent_name="finance")
    print(f"Agent: {response}\n")

    # Stop the server
    await app.stop_server()

if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())
