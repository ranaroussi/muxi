#!/usr/bin/env python3
"""
Agent Creation Test Script

This script tests the ability to create agents from configuration files
without testing the routing capability.
"""

import os
import yaml
import json
from dotenv import load_dotenv
from muxi.core.models.providers.openai import OpenAIModel
from muxi.core.agent import Agent
from muxi.core.orchestrator import Orchestrator

# Load environment variables from .env file
load_dotenv()

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
  buffer_size: 5
  buffer_multiplier: 10
  long_term: false
mcp_servers:
- name: weather_api
  url: http://localhost:5001
  credentials:
  - id: weather_api_key
    param_name: api_key
    required: true
    env_fallback: WEATHER_API_KEY
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
        "buffer_size": 5,
        "buffer_multiplier": 10,
        "long_term": false
    },
    "mcp_servers": [
        {
            "name": "stock_api",
            "url": "http://localhost:5002",
            "credentials": [
                {
                    "id": "stock_api_key",
                    "param_name": "api_key",
                    "required": true,
                    "env_fallback": "STOCK_API_KEY"
                }
            ]
        }
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


def test_agent_creation():
    """Test creating agents from configuration files."""
    print("=== Agent Creation Test ===\n")

    # Create test configuration files
    create_test_configs()

    # Create an orchestrator
    print("Creating orchestrator...")
    orchestrator = Orchestrator()

    # Create a model (we'll use this for testing)
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("No OpenAI API key found in environment. Set OPENAI_API_KEY.")
        return

    model = OpenAIModel(model="gpt-4o-mini", api_key=api_key)

    # Create an agent programmatically (baseline test)
    print("Creating agent programmatically...")
    Agent(
        model=model,
        system_message="You are a test assistant.",
        orchestrator=orchestrator  # Pass the orchestrator
    )
    print("Agent created successfully!\n")

    # Now test creating agents from config files
    print("Creating weather agent from YAML config...")

    # 1. Load the configuration
    weather_config = load_yaml_config(f"{CONFIGS_DIR}/weather_agent.yaml")
    weather_config["model"]["api_key"] = api_key  # Ensure we use the actual API key

    # 2. Create the weather agent
    weather_model = OpenAIModel(
        model=weather_config["model"]["model"],
        temperature=weather_config["model"]["temperature"],
        api_key=api_key
    )

    # Create the agent
    orchestrator.create_agent(
        agent_id="weather",
        model=weather_model,
        system_message=weather_config["system_message"],
        description=weather_config["description"]
    )

    # 3. Connect to MCP server (in a real scenario, this would be an async context)
    if weather_config.get("mcp_servers"):
        print(f"Would connect to {len(weather_config['mcp_servers'])} MCP servers")

    print("Weather agent created successfully!")

    # Create finance agent from JSON config
    print("\nCreating finance agent from JSON config...")

    # 1. Load the configuration
    finance_config = load_json_config(f"{CONFIGS_DIR}/finance_agent.json")
    finance_config["model"]["api_key"] = api_key  # Ensure we use the actual API key

    # 2. Create the finance agent
    finance_model = OpenAIModel(
        model=finance_config["model"]["model"],
        temperature=finance_config["model"]["temperature"],
        api_key=api_key
    )

    # Create the agent
    orchestrator.create_agent(
        agent_id="finance",
        model=finance_model,
        system_message=finance_config["system_message"],
        description=finance_config["description"]
    )

    # 3. Connect to MCP server (in a real scenario, this would be an async context)
    if finance_config.get("mcp_servers"):
        print(f"Would connect to {len(finance_config['mcp_servers'])} MCP servers")

    print("Finance agent created successfully!")

    # List all agents
    print("\nAgents available in orchestrator:")
    for agent_id in orchestrator.agents:
        agent_desc = orchestrator.agent_descriptions[agent_id]
        print(f"- {agent_id}: {agent_desc}")

    print("\n=== Test Completed ===")


if __name__ == "__main__":
    test_agent_creation()
