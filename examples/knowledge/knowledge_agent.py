#!/usr/bin/env python
"""
Knowledge Agent Demo

This script demonstrates how to create an agent with knowledge capabilities,
add knowledge sources, and query the knowledge base.
"""

import asyncio
import os
from dotenv import load_dotenv

from muxi.core.orchestrator import Orchestrator
from muxi.core.models.providers.openai import OpenAIModel
from muxi.core.knowledge.base import FileKnowledge


async def main():
    # Load environment variables
    load_dotenv()

    # Initialize the orchestrator
    orchestrator = Orchestrator()

    # Create an OpenAI model
    model = OpenAIModel(
        api_key=os.getenv("OPENAI_API_KEY"),
        model="gpt-4o"
    )

    # Create an agent with knowledge capabilities
    knowledge_agent = orchestrator.create_agent(
        agent_id="knowledge_assistant",
        description="An assistant with knowledge about the MUXI Framework",
        model=model,
        system_message=(
            "You are a helpful assistant with specialized knowledge about the MUXI Framework."
        )
    )

    # Add a knowledge source
    knowledge_file = FileKnowledge(
        path="examples/knowledge/sample.txt",
        description="General information about the MUXI Framework"
    )

    print("Adding knowledge source...")
    chunks_added = await knowledge_agent.add_knowledge(knowledge_file)
    print(f"Added {chunks_added} chunks to the knowledge base")

    # Get list of knowledge sources
    sources = knowledge_agent.get_knowledge_sources()
    print(f"Knowledge sources: {sources}")

    # Search the knowledge base
    print("\nSearching knowledge base for 'memory systems'...")
    results = await knowledge_agent.search_knowledge("memory systems")

    # Display search results
    for i, result in enumerate(results):
        print(f"\nResult {i+1} (Relevance: {result['relevance']:.2f}):")
        print(f"Source: {result['source']}")
        print(f"Content: {result['content']}")

    # Chat with the agent using knowledge
    print("\nChatting with knowledge-enabled agent...")
    response = await orchestrator.chat(
        "knowledge_assistant",
        "What are the key features of the MUXI Framework?"
    )
    print(f"\nAgent response:\n{response}")

    # Another query using knowledge
    response = await orchestrator.chat(
        "knowledge_assistant",
        "How can I use memory in the MUXI Framework?"
    )
    print(f"\nAgent response:\n{response}")

    # Try removing knowledge and see the difference
    print("\nRemoving knowledge source...")
    removed = await knowledge_agent.remove_knowledge("examples/knowledge/sample.txt")
    print(f"Knowledge removed: {removed}")

    # Check current knowledge sources
    sources = knowledge_agent.get_knowledge_sources()
    print(f"Knowledge sources after removal: {sources}")

if __name__ == "__main__":
    asyncio.run(main())
