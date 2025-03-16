#!/usr/bin/env python3

from src.core.orchestrator import Orchestrator
from src.models.providers.openai import OpenAIModel

# Example demonstrating agent creation and usage
if __name__ == "__main__":
    # Create an orchestrator
    orchestrator = Orchestrator()

    # Create weather-focused agent
    orchestrator.create_agent(
        agent_id="weather_agent",
        model=OpenAIModel(model="gpt-4o", api_key="your-openai-key-here"),
        system_message="You are a helpful assistant specialized in weather forecasts.",
        description=(
            "Expert in providing weather forecasts, current conditions, and answering "
            "questions about climate and meteorology."
        )
    )

    # Create finance-focused agent
    orchestrator.create_agent(
        agent_id="finance_agent",
        model=OpenAIModel(model="gpt-4o", api_key="your-openai-key-here"),
        system_message="You are a helpful assistant specialized in finance and investments.",
        description=(
            "Expert in financial analysis, investment strategies, market trends, "
            "stock recommendations, and personal finance advice."
        )
    )

    # Demonstrate intelligent routing
    print("\n=== Weather Query ===")
    weather_response = orchestrator.chat("What's the weather like in New York today?")
    print(f"Selected agent: {weather_response.agent_id}")
    print(f"Response: {weather_response.response}")

    print("\n=== Finance Query ===")
    finance_response = orchestrator.chat("How should I diversify my investment portfolio?")
    print(f"Selected agent: {finance_response.agent_id}")
    print(f"Response: {finance_response.response}")

    # You can still specify an agent explicitly if needed
    print("\n=== Explicit Agent Selection ===")
    explicit_response = orchestrator.chat("Tell me about bonds.", agent_name="finance_agent")
    print(f"Selected agent: {explicit_response.agent_id}")
    print(f"Response: {explicit_response.response}")
