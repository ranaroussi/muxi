#!/usr/bin/env python
"""
Declarative Knowledge Agent Demo

This script demonstrates how to create an agent with knowledge capabilities
using the declarative approach with YAML configuration.
"""

import asyncio
from dotenv import load_dotenv

from muxi import muxi


async def main():
    # Load environment variables
    load_dotenv()

    # Initialize MUXI
    app = muxi()

    # Add knowledge-enabled agent from YAML
    app.add_agent("examples/knowledge/knowledge_agent.yaml")

    # Chat with the agent using knowledge
    print("\nChatting with knowledge-enabled agent...")
    response = await app.chat(
        "knowledge_assistant",
        "What are the key features of the MUXI Framework?"
    )
    print(f"\nAgent response:\n{response}")

    # Another query using knowledge
    response = await app.chat(
        "knowledge_assistant",
        "How can I use memory in the MUXI Framework?"
    )
    print(f"\nAgent response:\n{response}")

    # Search the knowledge base
    print("\nSearching knowledge base for 'memory systems'...")
    # Get the agent instance to access knowledge methods
    agent = app.get_agent("knowledge_assistant")
    results = await agent.search_knowledge("memory systems")

    # Display search results
    for i, result in enumerate(results):
        print(f"\nResult {i+1} (Relevance: {result['relevance']:.2f}):")
        print(f"Source: {result['source']}")
        print(f"Content: {result['content']}")


if __name__ == "__main__":
    asyncio.run(main())
