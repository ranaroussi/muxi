---
layout: default
title: Buffer Memory
parent: Memory System
grand_parent: Technical Deep Dives
nav_order: 1
permalink: /technical/memory/buffer
---

# Buffer Memory

This page provides a technical deep dive into the Buffer Memory system in the MUXI Framework.

## Overview

Buffer Memory is the short-term conversational memory system that maintains conversation context for agents. It stores a fixed window of recent messages and automatically processes them to provide relevant context for subsequent interactions.

## Architecture

Buffer Memory is designed with the following components:

```
┌──────────────────────┐
│    BufferMemory      │
├──────────────────────┤
│ - messages: List     │      ┌──────────────────┐
│ - max_size: int      │◄────►│      Message     │
│ - buffer_multiplier: int│    ├──────────────────┤
│ - summarizer: Opt    │      │ - role: str      │
└──────────┬───────────┘      │ - content: str   │
           │                  │ - timestamp: dt  │
           ▼                  │ - metadata: Dict │
┌──────────────────────┐      └──────────────────┘
│   MemorySummarizer   │
└──────────────────────┘
```

The core components include:

- **Message Store**: An ordered list of messages with role (user/assistant), content, timestamp, and optional metadata
- **Size Management**: Fixed-size buffer window with automatic truncation and total buffer capacity determined by buffer_multiplier
- **Vector Search**: FAISS-backed vector similarity search for semantic retrieval
- **Hybrid Retrieval**: Combines semantic relevance with recency bias for optimal context retrieval
- **Summarization**: Optional component that creates memory summaries when the buffer overflows
- **Serialization**: Methods for converting to/from JSON for persistence

## Implementation Details

### Buffer Management

Buffer Memory manages a fixed window of messages with a configurable total capacity:

```python
from muxi.core.memory.buffer import BufferMemory
from muxi.core.models.providers.openai import OpenAIModel

# Create embedding model for vector search
embedding_model = OpenAIModel(model="text-embedding-ada-002", api_key="your_api_key")

# Create a buffer with context window size 5 and total capacity of 50 messages
buffer = BufferMemory(
    max_size=5,                # Context window size
    buffer_multiplier=10,      # Total capacity = 5 × 10 = 50 messages
    model=embedding_model,     # Model for generating embeddings
    vector_dimension=1536,     # Dimension for OpenAI embeddings
    recency_bias=0.3           # Balance between semantic (0.7) and recency (0.3)
)

# Add messages
buffer.add("user", "Hello, my name is Alice.")
buffer.add("assistant", "Hello Alice! How can I help you today?")

# When buffer exceeds capacity, oldest messages are removed from the total buffer
for i in range(60):
    buffer.add("user", f"Message {i}")

# Buffer now contains only the most recent 50 messages in the total buffer
# But when searching for context, only the most recent 5 messages would be returned for recency-only search
```

The implementation uses FAISS for vector similarity search:

```python
async def add(
    self,
    content: str,
    metadata: Optional[Dict[str, Any]] = None
) -> None:
    """Add an item to the buffer."""
    # Create buffer item
    buffer_item = {
        "content": content,
        "timestamp": time.time(),
        "metadata": metadata or {}
    }

    # Add to buffer
    self.buffer.append(buffer_item)

    # Generate and store vector if we have a model
    if self.has_vector_search and self.model:
        try:
            vector = await self.model.embed(content)
            self.vectors.append(vector)
            self.buffer_to_index[len(self.buffer) - 1] = len(self.vectors) - 1
            self.index_to_buffer[len(self.vectors) - 1] = len(self.buffer) - 1

            # Update FAISS index
            if len(self.vectors) % self.rebuild_every == 0:
                self._rebuild_index()
        except Exception as e:
            logger.error(f"Error generating vector for buffer item: {e}")

    # Maintain buffer size limit
    if len(self.buffer) > self.max_size * self.buffer_multiplier:
        self._trim_buffer()
```

### Hybrid Retrieval

The search method combines semantic relevance with recency bias:

```python
async def search(
    self,
    query: str,
    limit: int = 10,
    filter_metadata: Optional[Dict[str, Any]] = None,
    query_vector: Optional[List[float]] = None,
    recency_bias: float = 0.3,
) -> List[Dict[str, Any]]:
    """Search the buffer for relevant items."""
    # If we don't have vector search capability, return most recent messages
    if not self.has_vector_search or not self.model:
        return self._recency_search(limit, filter_metadata)

    # Generate embedding for query if not provided
    if not query_vector:
        try:
            query_vector = await self.model.embed(query)
        except Exception as e:
            logger.error(f"Error generating query vector: {e}")
            return self._recency_search(limit, filter_metadata)

    # Perform vector search
    try:
        # Convert to numpy array
        query_np = np.array([query_vector], dtype=np.float32)

        # Search the index
        distances, indices = self.index.search(query_np, min(len(self.vectors), limit * 2))

        # Process results with hybrid scoring
        results = []
        for i in range(len(indices[0])):
            idx = indices[0][i]
            if idx == -1:  # FAISS returns -1 for empty slots
                continue

            # Get buffer index
            buffer_idx = self.index_to_buffer.get(idx)
            if buffer_idx is None or buffer_idx >= len(self.buffer):
                continue

            buffer_item = self.buffer[buffer_idx]

            # Filter by metadata if needed
            if filter_metadata and not self._matches_metadata(buffer_item, filter_metadata):
                continue

            # Calculate combined score (semantic + recency)
            semantic_score = 1.0 / (1.0 + float(distances[0][i]))
            recency_score = 1.0 - (buffer_idx / len(self.buffer))
            combined_score = (1 - recency_bias) * semantic_score + recency_bias * recency_score

            # Add to results
            results.append({
                **buffer_item,
                "score": combined_score
            })

        # Sort by combined score and limit
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:limit]

    except Exception as e:
        logger.error(f"Error in vector search: {e}")
        return self._recency_search(limit, filter_metadata)
```

### Context Window vs. Total Buffer Size

BufferMemory introduces two distinct parameters related to size:

```python
def __init__(
    self,
    max_size: int = 10,               # Context window size
    buffer_multiplier: int = 10,       # Multiplier for total capacity
    model: Optional[BaseModel] = None, # Model for embeddings
    vector_dimension: int = 1536,      # Dimension for vectors
    # ... other parameters
)
```

- `max_size`: Defines the context window size - the number of recent messages included when retrieving by recency
- `buffer_multiplier`: Multiplies the context window size to determine the total buffer capacity
- Total buffer capacity = max_size × buffer_multiplier (default: 10 × 10 = 100)

This design addresses the need to have a larger storage capacity for vector similarity search while still maintaining a smaller, focused context window for pure recency-based retrieval.

### User-Specific Partitioning

BufferMemory supports user-specific partitioning through metadata filtering:

```python
# Create buffer
buffer = BufferMemory(
    max_size=5,
    buffer_multiplier=10,
    model=embedding_model
)

# Add messages for different users
await buffer.add(
    "I'm Alice",
    metadata={"user_id": "user1"}
)
await buffer.add(
    "I'm Bob",
    metadata={"user_id": "user2"}
)

# Get messages for a specific user
alice_messages = await buffer.search(
    "alice",
    filter_metadata={"user_id": "user1"}
)
bob_messages = await buffer.search(
    "bob",
    filter_metadata={"user_id": "user2"}
)
```

## Performance Considerations

The BufferMemory system is designed for efficiency, balancing performance and accuracy:

- **Vector Search**: Uses FAISS for efficient vector similarity search
- **Hybrid Scoring**: Combines semantic relevance with recency for optimal results
- **Graceful Degradation**: Falls back to recency-only search when needed
- **Thread Safety**: All operations are thread-safe for concurrent access

For optimal performance, consider these factors:

- **Context Window Size**: Set `max_size` based on your LLM's context window limitations
- **Buffer Multiplier**: Adjust `buffer_multiplier` based on memory constraints and retrieval needs
- **Recency Bias**: Tune `recency_bias` for your specific use case:
  - Higher values (0.5-0.7) for conversation-heavy applications
  - Lower values (0.1-0.3) for knowledge-heavy applications

## Integration with Agents

Agents automatically integrate with BufferMemory:

```python
from muxi.core.agent import Agent
from muxi.core.models.providers.openai import OpenAIModel
from muxi.core.memory.buffer import BufferMemory
from muxi.core.orchestrator import Orchestrator

# Create buffer memory
buffer = BufferMemory(
    max_size=10,               # Context window size
    buffer_multiplier=10,      # Total capacity = 10 × 10 = 100
    model=OpenAIModel(model="text-embedding-ada-002")
)

# Create orchestrator with buffer memory
orchestrator = Orchestrator(buffer_memory=buffer)

# Create agent that will use orchestrator's memory
agent = Agent(
    name="assistant",
    model=OpenAIModel("gpt-4"),
    system_message="You are a helpful assistant.",
    orchestrator=orchestrator
)

# Each chat interaction automatically uses and updates the buffer
agent.chat("Hello, my name is Charlie.")
agent.chat("What's my name?")  # Will include "Charlie" in response
```

## Configuration Examples

```python
# Different configurations for different use cases

# For high-recall in knowledge-intensive applications
buffer_high_recall = BufferMemory(
    max_size=15,
    buffer_multiplier=20,    # Larger multiplier (300 total messages)
    recency_bias=0.1         # Strong preference for semantic similarity
)

# For conversational applications with immediate context
buffer_conversational = BufferMemory(
    max_size=10,
    buffer_multiplier=5,     # Smaller multiplier (50 total messages)
    recency_bias=0.6         # Strong preference for recency
)

# For balanced general-purpose use
buffer_balanced = BufferMemory(
    max_size=10,
    buffer_multiplier=10,    # Default multiplier (100 total messages)
    recency_bias=0.3         # Balanced semantic/recency priority
)
```

## Best Practices

- **Size Configuration**:
  - Set `max_size` based on your LLM's ideal context window:
    - Short, factual exchanges: 3-5 messages
    - Complex conversations: 8-12 messages
    - Technical discussions: 10-15 messages
  - Set `buffer_multiplier` based on how much history you want to maintain:
    - Limited memory needs: 5-8× multiplier
    - Standard applications: 10× multiplier (default)
    - Knowledge-heavy applications: 15-20× multiplier

- **Recency Bias**:
  - Human conversations: `recency_bias=0.5` (more recency)
  - Factual queries: `recency_bias=0.2` (more semantic)
  - Default `recency_bias=0.3` works well for general use

- **Metadata Usage**: Use metadata to track important message attributes (user_id, session_id, etc.)

## Related Topics

- [Long-Term Memory](../long-term) - Persistent memory storage
- [Multi-User Memory (Memobase)](../memobase) - User-specific memory partitioning
- [Domain Knowledge](../domain-knowledge) - Structured knowledge integration
