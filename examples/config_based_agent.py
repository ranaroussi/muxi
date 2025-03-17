"""
Configuration-based agent example with the MUXI Framework.

This example demonstrates how to create agents from YAML/JSON configuration files.
"""

import asyncio
from dotenv import load_dotenv
from muxi import muxi

# Load environment variables (including API keys)
load_dotenv()

async def main():
    # Create a new MUXI instance
    app = muxi()

    # Create an agent from a configuration file (YAML)
    # This would be a file like:
    # name: assistant
    # system_message: You are a helpful AI assistant.
    # model:
    #   provider: openai
    #   api_key: "${OPENAI_API_KEY}"
    #   model: gpt-4o
    #   temperature: 0.7
    # memory:
    #   buffer: 10
    #   long_term: true
    # tools:
    # - enable_calculator
    # - enable_web_search
    await app.add_agent("assistant", "configs/assistant.yaml")

    # You can also create an agent from a JSON file
    # await app.add_agent("researcher", "configs/researcher.json")

    # Send a message to the agent and get the response
    response = await app.chat("Hello, who are you?")
    print(f"Agent: {response}")

    # Continue the conversation with conversation memory
    response = await app.chat("What can you help me with?")
    print(f"Agent: {response}")

    # Ask something that requires tool use
    response = await app.chat("What is the square root of 144?")
    print(f"Agent: {response}")

    # Ask something that requires web search
    response = await app.chat("What is the current weather in New York?")
    print(f"Agent: {response}")

if __name__ == "__main__":
    asyncio.run(main())
