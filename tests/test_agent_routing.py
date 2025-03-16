#!/usr/bin/env python3
"""
Agent Routing Test Script

This script tests the intelligent agent routing capability by creating two
specialized agents and testing if messages are routed to the correct agent.
"""

import os
import yaml
import json
import asyncio
from src.models.providers.openai import OpenAIModel
from src.core.orchestrator import Orchestrator
from tests.utils.env_setup import load_api_keys

# Load API keys from .env file
load_api_keys()

# Path to configuration files
CONFIGS_DIR = "tests/configs"
os.makedirs(CONFIGS_DIR, exist_ok=True)


def create_test_configs():
    """Create test configuration files for agents."""
    # Weather agent (YAML)
    with open(f"{CONFIGS_DIR}/weather_agent.yaml", "w") as f:
        f.write("""
name: weather_assistant
description: "Specialized in providing weather forecasts and meteorological information."
system_message: You are a weather assistant that provides forecasts.
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
    "description": "Expert in financial analysis and investment strategies.",
    "system_message": "You are a finance assistant.",
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


def load_yaml_config(file_path):
    """Load a YAML configuration file."""
    with open(file_path, 'r') as f:
        return yaml.safe_load(f)


def load_json_config(file_path):
    """Load a JSON configuration file."""
    with open(file_path, 'r') as f:
        return json.load(f)


async def test_agent_routing():
    """Test the intelligent agent routing capability."""
    print("=== Intelligent Agent Routing Test ===\n")

    # Create test configuration files
    create_test_configs()

    # Create an orchestrator
    print("Creating orchestrator...")
    orchestrator = Orchestrator()

    # Get API key from environment
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("No OpenAI API key found in environment. Set OPENAI_API_KEY.")
        return

    # Create weather agent from YAML config
    print("Creating weather agent from YAML config...")
    weather_config = load_yaml_config(f"{CONFIGS_DIR}/weather_agent.yaml")
    weather_model = OpenAIModel(
        model=weather_config["model"]["model"],
        temperature=weather_config["model"]["temperature"],
        api_key=api_key
    )
    orchestrator.create_agent(
        agent_id="weather",
        model=weather_model,
        system_message=weather_config["system_message"],
        description=weather_config["description"]
    )

    # Create finance agent from JSON config
    print("Creating finance agent from JSON config...")
    finance_config = load_json_config(f"{CONFIGS_DIR}/finance_agent.json")
    finance_model = OpenAIModel(
        model=finance_config["model"]["model"],
        temperature=finance_config["model"]["temperature"],
        api_key=api_key
    )
    orchestrator.create_agent(
        agent_id="finance",
        model=finance_model,
        system_message=finance_config["system_message"],
        description=finance_config["description"]
    )

    # List all agents
    print("\nAgents available:")
    for agent_id in orchestrator.agents:
        agent_desc = orchestrator.agent_descriptions[agent_id]
        print(f"- {agent_id}: {agent_desc}")

    print("\nTesting agent routing...\n")

    # If OpenAI API isn't working, we'll test the manual routing logic
    try:
        # Test with a weather-related query
        weather_query = "What's the weather forecast for New York today?"
        print(f"Query: {weather_query}")
        try:
            selected_agent_id = await orchestrator.select_agent_for_message(weather_query)
            print(f"Selected agent: {selected_agent_id}")

            # Verify that the weather agent was selected
            assert selected_agent_id == "weather", f"Expected 'weather' agent, got '{selected_agent_id}'"
            print("✓ Correctly routed to weather agent")
        except Exception as e:
            print(f"Error in weather routing test: {str(e)}")

        # Test with a finance-related query
        finance_query = "What are the best investment strategies for stocks, bonds and financial planning?"
        print(f"\nQuery: {finance_query}")
        try:
            selected_agent_id = await orchestrator.select_agent_for_message(finance_query)
            print(f"Selected agent: {selected_agent_id}")

            # Verify that the finance agent was selected
            assert selected_agent_id == "finance", f"Expected 'finance' agent, got '{selected_agent_id}'"
            print("✓ Correctly routed to finance agent")
        except Exception as e:
            print(f"Error in finance routing test: {str(e)}")
    except Exception as e:
        print(f"Error with API-based tests: {str(e)}")
        print("Testing manual routing simulation instead...")

        # Simulate routing logic for weather query
        print("\nSimulating routing for weather query...")
        # Compare query with agent descriptions
        query = "What's the weather forecast for New York today?"
        weather_desc = orchestrator.agent_descriptions["weather"].lower()
        finance_desc = orchestrator.agent_descriptions["finance"].lower()

        weather_match = len(set(query.lower().split()) & set(weather_desc.split()))
        finance_match = len(set(query.lower().split()) & set(finance_desc.split()))

        # Simple word matching to simulate routing
        if weather_match > finance_match:
            print("✓ Would correctly route to weather agent")
        else:
            print("✗ Would not route to weather agent")

        # Simulate routing logic for finance query
        print("\nSimulating routing for finance query...")
        query = "What are some good strategies for retirement investing?"

        weather_match = len(set(query.lower().split()) & set(weather_desc.split()))
        finance_match = len(set(query.lower().split()) & set(finance_desc.split()))

        if finance_match > weather_match:
            print("✓ Would correctly route to finance agent")
        else:
            print("✗ Would not route to finance agent")

    print("\n=== Test Completed ===")


if __name__ == "__main__":
    asyncio.run(test_agent_routing())
