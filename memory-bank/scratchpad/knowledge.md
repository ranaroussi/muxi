# Agent-Level Knowledge Base PRD

## Overview

This document outlines the agent-specific domain knowledge capabilities in the MUXI Framework, providing lightweight RAG (Retrieval-Augmented Generation) capabilities at the agent level. This feature enables agents to access specialized information sources, allowing them to provide more accurate, contextual, and helpful responses in their areas of expertise.

## Problem Statement

Currently, MUXI supports context memory at the user level, which allows for personalization based on user-specific data. However, agents lack dedicated knowledge bases that align with their specialized roles and expertise. This limitation means that agents rely solely on their pre-trained knowledge, which may be outdated or insufficient for specific domains.

## Scope and Implementation

MUXI is designed primarily as an agent routing system where MCP servers handle specialized, computation-heavy tasks. We've implemented a lightweight, focused approach to agent knowledge:

1. **File-based knowledge only** - For simplicity and minimal dependencies, we support text-based file sources.
2. **In-memory vector store** - We leverage FAISS for efficient in-memory vector storage, avoiding additional database dependencies.
3. **Embedding persistence** - To optimize costs, embeddings are persisted locally in `.cache/knowledge_embeddings`, regenerated only when files change.
4. **Dynamic embedding dimensions** - We automatically determine the appropriate embedding dimension based on the agent's model.
5. **No additional embedding dependencies** - We use each agent's configured model for generating embeddings, avoiding the need for additional embedding-specific dependencies or services.

This focused approach aligns with MUXI's philosophy of maintaining clean, simple APIs while providing essential functionality.

## Implemented Features

### Agent Knowledge Configuration

YAML/JSON configuration for agent knowledge sources:

```yaml
agent_id: product_assistant
description: A helpful assistant with knowledge about our products.
model:
  provider: openai
  api_key: "${OPENAI_API_KEY}"
  model: gpt-4o
knowledge:
  - path: "knowledge/products.txt"
    description: "Information about our product catalog"
  - path: "knowledge/pricing.txt"
    description: "Pricing information for our products"
  - path: "knowledge/faq.txt"
    description: "Frequently asked questions about our products"
```

### Knowledge Source Types

Currently, MUXI supports the following knowledge source types:

- **File Knowledge**: Text-based documents containing domain-specific information

### Knowledge Management API

The implemented agent knowledge API provides methods for managing knowledge sources:

```python
# Add knowledge to an agent
await agent.add_knowledge(file_knowledge)

# List knowledge sources
sources = agent.get_knowledge_sources()

# Remove knowledge
success = await agent.remove_knowledge("path/to/file.txt")

# Search knowledge
results = await agent.search_knowledge(
    query="search query",
    top_k=3,
    threshold=0.7
)
```

### Knowledge Embedding and Retrieval

Behind the scenes, MUXI:

1. **Processes knowledge sources**: Documents are loaded and split into chunks
2. **Generates embeddings**: Text chunks are converted to vector embeddings
3. **Builds vector index**: Embeddings are stored in a FAISS index for fast retrieval
4. **Implements semantic search**: Relevance-based retrieval of information
5. **Caches embeddings**: Embeddings are stored in `.cache/knowledge_embeddings` for efficiency

## Technical Implementation

### Knowledge Handler Class

The `KnowledgeHandler` class manages knowledge sources and embedding operations:

```python
class KnowledgeHandler:
    def __init__(self, agent_id, embedding_dimension=1536, cache_dir=".cache/knowledge_embeddings"):
        self.agent_id = agent_id
        self.embedding_dimension = embedding_dimension
        self.cache_dir = cache_dir
        self.embedding_file = f"{cache_dir}/{agent_id}_embeddings.pickle"
        self.metadata_file = f"{cache_dir}/{agent_id}_metadata.pickle"

        # Create cache directory if it doesn't exist
        os.makedirs(cache_dir, exist_ok=True)

        # Initialize index and documents
        self._load_cached_embeddings()

    async def add_file(self, knowledge_source, generate_embeddings_fn):
        """Add a file to the knowledge base"""
        # Implementation details...

    async def remove_file(self, file_path):
        """Remove a file from the knowledge base"""
        # Implementation details...

    async def search(self, query, generate_embedding_fn, top_k=5, threshold=0.0):
        """Search the knowledge base for relevant information"""
        # Implementation details...

    def get_sources(self):
        """Get a list of knowledge sources"""
        # Implementation details...
```

### Agent Class Integration

The `Agent` class has been extended with knowledge handling capabilities:

```python
async def _initialize_knowledge(self, knowledge_sources):
    """Initialize the knowledge handler and add knowledge sources"""
    # Get embedding dimension from model
    sample_embedding = await self.model.embed("Sample text to determine embedding dimension")
    embedding_dimension = len(sample_embedding)

    # Create knowledge handler with the correct embedding dimension
    self.knowledge_handler = KnowledgeHandler(
        self.agent_id,
        embedding_dimension=embedding_dimension
    )

    # Add knowledge sources
    for source in knowledge_sources:
        await self.add_knowledge(source)

async def add_knowledge(self, knowledge_source):
    """Add a knowledge source to the agent"""
    # Implementation details...

async def remove_knowledge(self, file_path):
    """Remove a knowledge source from the agent"""
    # Implementation details...

def get_knowledge_sources(self):
    """Get a list of knowledge sources"""
    # Implementation details...

async def search_knowledge(self, query, top_k=5, threshold=0.0):
    """Search the knowledge base for relevant information"""
    # Implementation details...
```

## Usage Examples

### Declarative Configuration

```python
from muxi import muxi
from dotenv import load_dotenv
import asyncio

# Load environment variables
load_dotenv()

# Initialize MUXI
app = muxi()

# Add agent with knowledge from configuration
app.add_agent("configs/knowledge_agent.yaml")

async def main():
    # The agent can now answer questions based on the knowledge sources
    response = await app.chat("product_assistant", "What products do you offer?")
    print(response)

if __name__ == "__main__":
    asyncio.run(main())
```

### Programmatic Approach

```python
import os
import asyncio
from muxi.core.orchestrator import Orchestrator
from muxi.core.models.openai import OpenAIModel
from muxi.knowledge.base import FileKnowledge

async def main():
    # Initialize components
    orchestrator = Orchestrator()
    model = OpenAIModel(
        api_key=os.getenv("OPENAI_API_KEY"),
        model="gpt-4o"
    )

    # Create an agent
    agent = orchestrator.create_agent(
        agent_id="product_assistant",
        description="A helpful assistant with knowledge about our products.",
        model=model
    )

    # Add knowledge sources to the agent
    product_knowledge = FileKnowledge(
        path="knowledge/products.txt",
        description="Information about our product catalog"
    )

    await agent.add_knowledge(product_knowledge)

    # The agent can now answer questions based on the knowledge sources
    response = await orchestrator.chat("product_assistant", "What products do you offer?")
    print(response)

if __name__ == "__main__":
    asyncio.run(main())
```

## Best Practices

1. **Focus on Quality**: Include high-quality, relevant information in knowledge sources
2. **Right-Size Documents**: Break large documents into smaller, topic-focused files
3. **Descriptive Metadata**: Provide clear descriptions for knowledge sources
4. **Regular Updates**: Keep knowledge sources up-to-date with the latest information
5. **Knowledge vs. Memory**: Use domain knowledge for static information, context memory for conversation context
6. **Strategic Search**: Set appropriate threshold and top_k values for your use case

## Conclusion

The agent-level knowledge base feature is now fully implemented in the MUXI Framework, enabling agents to access and utilize specialized information to provide more accurate and contextual responses. The implementation maintains MUXI's design philosophy of simplicity and flexibility while providing powerful knowledge capabilities for a wide range of applications.

For comprehensive documentation on using this feature, refer to the [Domain Knowledge](../docs/agents/knowledge.md) guide.
