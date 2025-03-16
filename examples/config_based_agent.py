"""
Example of using the MUXI Framework with configuration files.

This example demonstrates how to create agents from configuration files,
interact with them, and start the API server with minimal code.
"""

from dotenv import load_dotenv
from src import muxi

# Load environment variables
# This is useful for setting API keys and other credentials
# that will be referenced in the configuration with ${ENV_VAR}
load_dotenv()

# Create a MUXI instance
# No need to provide database connection - it will be loaded automatically
# from DATABASE_URL when an agent with long-term memory is created
app = muxi()

# Add an agent from a YAML configuration file
app.add_agent(
    name="weather_assistant",
    path="examples/configs/weather_agent.yaml"
)

# Add another agent from a JSON configuration file
app.add_agent(
    name="finance_assistant",
    path="examples/configs/finance_agent.json"
)

# Add domain knowledge for a specific user
user_id = 123
knowledge = {
    "name": "Alice",
    "age": 30,
    "location": {"city": "New York", "country": "USA"},
    "interests": ["AI", "programming", "music"],
    "family": {"spouse": "Bob", "children": ["Charlie", "Diana"]}
}
app.add_user_domain_knowledge(user_id=user_id, knowledge=knowledge)

# --- Option 1: Interactive usage ---

# Chat with a specific agent (explicitly specifying the agent)
response = app.chat("What's the weather in London?", agent_name="weather_assistant")
print(f"Weather Assistant: {response}")

# Chat without specifying the agent (orchestrator will select the appropriate agent)
response = app.chat("What's the weather in my city?", user_id=user_id)
print(f"Auto-selected Agent: {response}")

# --- Option 2: Start a server ---

# Uncomment to start the API server
# app.start_server(port=5050)

# --- Option 3: Start both API server and web UI ---

# Uncomment to start both the API server and web UI
# app.run()
