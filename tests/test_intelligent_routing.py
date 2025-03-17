#!/usr/bin/env python3
"""
Intelligent Routing Test Script

This script tests the intelligent agent routing capability by creating two
specialized agents from configuration files and sending messages that should
be routed to the correct agent based on their content.
"""

import asyncio
import os
from muxi import muxi
from tests.utils.env_setup import load_api_keys

# Load API keys from .env file
load_api_keys()

# Path to configuration files
CONFIGS_DIR = "tests/configs"
os.makedirs(CONFIGS_DIR, exist_ok=True)

# Create test config files if they don't exist
def create_test_configs():
    # Weather agent (YAML)
    with open(f"{CONFIGS_DIR}/weather_agent.yaml", "w") as f:
        f.write("""
name: weather_assistant
description: "Specialized in providing weather forecasts, current weather conditions,
  and meteorological information for locations worldwide."
system_message: You are a weather assistant. You provide accurate information
  about weather conditions and forecasts.
model:
  provider: openai
  api_key: "${OPENAI_API_KEY}"
  model: gpt-4o-mini
  temperature: 0.2
memory:
  buffer: 5
  long_term: false
tools:
- enable_calculator
""")

    # Finance agent (JSON)
    with open(f"{CONFIGS_DIR}/finance_agent.json", "w") as f:
        f.write("""
{
    "name": "finance_assistant",
    "description": "Expert in financial analysis, investment strategies, market trends and personal finance advice.",
    "system_message": "You are a finance assistant. You provide analysis and advice on financial matters.",
    "model": {
        "provider": "openai",
        "api_key": "${OPENAI_API_KEY}",
        "model": "gpt-4o-mini",
        "temperature": 0.2
    },
    "memory": {
        "buffer": 5,
        "long_term": false
    },
    "tools": [
        "enable_calculator"
    ]
}
""")

async def test_intelligent_routing():
    # Create test configuration files
    create_test_configs()

    print("=== Intelligent Agent Routing Test ===\n")

    # Initialize MUXI
    print("Initializing MUXI framework...")
    mx = muxi()

    # Add agents from configuration files
    print("Adding agents from config files...")
    mx.add_agent("weather", f"{CONFIGS_DIR}/weather_agent.yaml")
    mx.add_agent("finance", f"{CONFIGS_DIR}/finance_agent.json")

    print("\nRouting test cases:")

    # Test 1: Weather-related query (should route to weather agent)
    weather_query = "What's the weather forecast for New York this weekend?"
    print(f"\n1. Query: {weather_query}")
    response = await mx.chat(weather_query)
    print(f"Agent response: {response}")

    # Test 2: Finance-related query (should route to finance agent)
    finance_query = "What are some good strategies for retirement investing?"
    print(f"\n2. Query: {finance_query}")
    response = await mx.chat(finance_query)
    print(f"Agent response: {response}")

    # Test 3: Explicit agent selection
    explicit_query = "I need information about investment options."
    print(f"\n3. Query with explicit agent: {explicit_query}")
    response = await mx.chat(explicit_query, agent_name="finance")
    print(f"Agent response: {response}")

    print("\n=== Test Completed ===")

if __name__ == "__main__":
    asyncio.run(test_intelligent_routing())
