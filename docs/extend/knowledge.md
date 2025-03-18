---
layout: default
title: Domain Knowledge
parent: Extending Capabilities
nav_order: 3
permalink: /extend/knowledge/
---

# Domain Knowledge

{: .fs-5 .fw-600 }
This guide explains how to enhance your MUXI agents with domain knowledge, allowing them to access and utilize information from external sources when responding to user queries.

## Understanding Domain Knowledge

Domain knowledge in MUXI represents static information that agents can reference during conversations, providing them with:

1. **Factual information** from documents, files, and other sources
2. **Context-specific data** for specialized applications
3. **Up-to-date information** without relying solely on model training data

Unlike memory which tracks conversation history, domain knowledge provides agents with external information they can search and reference.

## Knowledge Types in MUXI

Currently, MUXI supports the following knowledge source types:

1. **File Knowledge**: Text-based documents containing domain-specific information

## Adding Knowledge to Agents

You can enhance agents with knowledge sources in both declarative and programmatic ways.

### Basic Knowledge Example

<h4>Declarative way</h4>

`configs/knowledge_agent.yaml`

```yaml
---
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

`app.py`

```python
from muxi import muxi
from dotenv import load_dotenv
import os
import asyncio

# Load environment variables
load_dotenv()

# Initialize MUXI
app = muxi()

# Add agent with knowledge from configuration
app.add_agent("configs/knowledge_agent.yaml")

async def main():
    # The agent can now answer questions based on the knowledge sources
    response = await app.chat("What products do you offer?")
    print(response)

    # The agent will use relevant knowledge to answer specific questions
    response = await app.chat("What is the price of the Premium Plan?")
    print(response)

if __name__ == "__main__":
    asyncio.run(main())
```

<h4>Programmatic way</h4>

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
    pricing_knowledge = FileKnowledge(
        path="knowledge/pricing.txt",
        description="Pricing information for our products"
    )
    faq_knowledge = FileKnowledge(
        path="knowledge/faq.txt",
        description="Frequently asked questions about our products"
    )

    # Add knowledge sources to the agent
    await agent.add_knowledge(product_knowledge)
    await agent.add_knowledge(pricing_knowledge)
    await agent.add_knowledge(faq_knowledge)

    # The agent can now answer questions based on the knowledge sources
    response = await orchestrator.chat("product_assistant", "What products do you offer?")
    print(response)

    # The agent will use relevant knowledge to answer specific questions
    response = await orchestrator.chat("product_assistant", "What is the price of the Premium Plan?")
    print(response)

if __name__ == "__main__":
    asyncio.run(main())
```

## Searching Knowledge Explicitly

You can explicitly search an agent's knowledge base to retrieve relevant information:

<h4>Declarative way</h4>

```python
# app.py
from muxi import muxi
from dotenv import load_dotenv
import asyncio

# Load environment variables
load_dotenv()

# Initialize MUXI
app = muxi()

# Add agent with knowledge
app.add_agent("configs/knowledge_agent.yaml")

async def main():
    # Get the agent instance to access knowledge methods
    agent = app.get_agent("product_assistant")

    # Search the knowledge base explicitly
    results = await agent.search_knowledge(
        query="Premium Plan features",
        top_k=3,  # Return top 3 most relevant results
        threshold=0.7  # Minimum relevance score (0-1)
    )

    # Display search results
    print("Knowledge search results:")
    for result in results:
        print(f"Content: {result['content']}")
        print(f"Source: {result['source']}")
        print(f"Relevance: {result['relevance']:.2f}")
        print("---")

if __name__ == "__main__":
    asyncio.run(main())
```

<h4>Programmatic way</h4>

```python
import os
import asyncio
from muxi.core.orchestrator import Orchestrator
from muxi.core.models.openai import OpenAIModel
from muxi.knowledge.base import FileKnowledge

async def main():
    # Initialize orchestrator
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

    # Add knowledge sources
    product_knowledge = FileKnowledge(
        path="knowledge/products.txt",
        description="Information about our product catalog"
    )
    await agent.add_knowledge(product_knowledge)

    # Search the knowledge base explicitly
    results = await agent.search_knowledge(
        query="Premium Plan features",
        top_k=3,  # Return top 3 most relevant results
        threshold=0.7  # Minimum relevance score (0-1)
    )

    # Display search results
    print("Knowledge search results:")
    for result in results:
        print(f"Content: {result['content']}")
        print(f"Source: {result['source']}")
        print(f"Relevance: {result['relevance']:.2f}")
        print("---")

if __name__ == "__main__":
    asyncio.run(main())
```

## Managing Knowledge Sources

You can add, remove, and list knowledge sources dynamically:

### Adding Knowledge Sources

<h4>Programmatic way</h4>

```python
# Add a new knowledge source to an existing agent
new_knowledge = FileKnowledge(
    path="knowledge/new_products.txt",
    description="Information about newly launched products"
)
await agent.add_knowledge(new_knowledge)
```

### Removing Knowledge Sources

<h4>Programmatic way</h4>

```python
# Remove a knowledge source by file path
success = await agent.remove_knowledge("knowledge/outdated_products.txt")
if success:
    print("Knowledge source removed successfully")
else:
    print("Failed to remove knowledge source or file not found")
```

### Listing Knowledge Sources

<h4>Programmatic way</h4>

```python
# Get a list of all knowledge sources
sources = agent.get_knowledge_sources()
print("Current knowledge sources:")
for source in sources:
    print(f"- {source}")
```

## Knowledge Embedding and Retrieval

Behind the scenes, MUXI:

1. **Processes knowledge sources**: Documents are loaded and split into chunks
2. **Generates embeddings**: Text chunks are converted to vector embeddings
3. **Builds vector index**: Embeddings are stored in a FAISS index for fast retrieval
4. **Implements semantic search**: Relevance-based retrieval of information

{: .note }
> MUXI automatically determines the appropriate embedding dimension based on the agent's model.

## Knowledge Caching

For efficiency, MUXI caches knowledge embeddings:

1. Embeddings are stored in `.cache/knowledge_embeddings` directory
2. Cached embeddings are reused when the same knowledge source is added again
3. Embeddings are regenerated when the source file is modified

## Best Practices for Domain Knowledge

1. **Focus on Quality**: Include high-quality, relevant information in knowledge sources
2. **Right-Size Documents**: Break large documents into smaller, topic-focused files
3. **Descriptive Metadata**: Provide clear descriptions for knowledge sources
4. **Regular Updates**: Keep knowledge sources up-to-date with the latest information
5. **Knowledge vs. Memory**: Use domain knowledge for static information, memory for conversation context
6. **Strategic Search**: Set appropriate threshold and top_k values for your use case

## Next Steps

Now that you've added domain knowledge to your agents, you might want to:

- Combine domain knowledge with memory - see [User Context Memory](../memory/)
- Create multi-agent systems with specialized knowledge - see [Multi-Agent Systems](../multi-agent/)
- Configure your agents with specific settings - see [Agent Configuration](../configuration/)
