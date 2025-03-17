---
layout: default
title: Buffer Memory
parent: Memory System
grand_parent: Technical Deep Dives
nav_order: 1
permalink: /technical/memory/buffer/
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
│ - messages: List     │      ┌─────────────────┐
│ - buffer_size: int   │◄────►│     Message     │
│ - summarizer: Opt    │      ├─────────────────┤
└──────────┬───────────┘      │ - role: str     │
           │                  │ - content: str   │
           ▼                  │ - timestamp: dt  │
┌──────────────────────┐      │ - metadata: Dict │
│   MemorySummarizer   │      └─────────────────┘
└──────────────────────┘
```

The core components include:

- **Message Store**: An ordered list of messages with role (user/assistant), content, timestamp, and optional metadata
- **Size Management**: Fixed-size buffer window with automatic truncation
- **Summarization**: Optional component that creates memory summaries when the buffer overflows
- **Serialization**: Methods for converting to/from JSON for persistence

## Implementation Details

### Buffer Management

Buffer Memory manages a fixed window of messages using a queue-like structure:

```python
from muxi.core.memory.buffer import BufferMemory

# Create a buffer with size 5
buffer = BufferMemory(buffer_size=5)

# Add messages
buffer.add_message("user", "Hello, my name is Alice.")
buffer.add_message("assistant", "Hello Alice! How can I help you today?")

# When buffer exceeds capacity, oldest messages are removed
for i in range(10):
    buffer.add_message("user", f"Message {i}")

# Buffer now contains only the 5 most recent messages
```

The implementation uses a list with maintenance operations when new messages are added:

```python
def add_message(self, role: str, content: str, metadata: Optional[Dict] = None) -> None:
    """Add a message to the buffer."""
    message = {
        "role": role,
        "content": content,
        "timestamp": datetime.datetime.now().isoformat(),
    }

    if metadata:
        message["metadata"] = metadata

    self.messages.append(message)

    # Maintain buffer size
    if len(self.messages) > self.buffer_size:
        if self.summarizer:
            # Create summary of oldest messages
            to_summarize = self.messages[:(len(self.messages) - self.buffer_size)]
            summary = self.summarizer.summarize(to_summarize)
            self.summary = summary

        # Remove oldest messages
        self.messages = self.messages[-(self.buffer_size):]
```

### Automatic Summarization

When messages exceed the buffer size, the oldest messages can be automatically summarized (if a summarizer is configured):

```python
from muxi.core.memory.buffer import BufferMemory, MemorySummarizer
from muxi.core.models.openai import OpenAIModel

# Create summarizer with a model
summarizer = MemorySummarizer(
    model=OpenAIModel("gpt-3.5-turbo")
)

# Create buffer with summarizer
buffer = BufferMemory(
    buffer_size=5,
    summarizer=summarizer
)

# When buffer overflows, oldest messages are summarized
for i in range(10):
    buffer.add_message("user", f"Message {i}")

print(buffer.summary)  # Contains summary of oldest messages
```

The summarizer uses an LLM to create concise summaries:

```python
def summarize(self, messages: List[Dict]) -> str:
    """Summarize a list of messages."""
    prompt = "Summarize the following conversation concisely, focusing on key facts and important information:\n\n"

    for msg in messages:
        prompt += f"{msg['role'].title()}: {msg['content']}\n"

    response = self.model.generate(prompt)
    return response
```

### Accessing Messages

The buffer provides methods to access and format messages:

```python
# Get all messages
all_messages = buffer.get_messages()

# Get messages formatted for LLM consumption
formatted_messages = buffer.get_formatted_messages()

# Get messages with summary (if available)
context_messages = buffer.get_context()
```

The formatting logic ensures messages are in the expected format for LLM APIs:

```python
def get_formatted_messages(self) -> List[Dict[str, str]]:
    """Get messages formatted for LLM consumption."""
    formatted = []

    # Add summary if available
    if self.summary:
        formatted.append({
            "role": "system",
            "content": f"Previous conversation summary: {self.summary}"
        })

    # Add current messages
    for msg in self.messages:
        formatted.append({
            "role": msg["role"],
            "content": msg["content"]
        })

    return formatted
```

### User-Specific Partitioning

Buffer Memory supports user-specific partitioning:

```python
# Create buffer
buffer = BufferMemory(buffer_size=5)

# Add messages for different users
buffer.add_message("user", "I'm Alice", metadata={"user_id": "user1"})
buffer.add_message("assistant", "Hello Alice!", metadata={"user_id": "user1"})

buffer.add_message("user", "I'm Bob", metadata={"user_id": "user2"})
buffer.add_message("assistant", "Hello Bob!", metadata={"user_id": "user2"})

# Get messages for a specific user
alice_messages = buffer.get_messages(filter_metadata={"user_id": "user1"})
bob_messages = buffer.get_messages(filter_metadata={"user_id": "user2"})
```

The filtering mechanism checks message metadata:

```python
def get_messages(self, filter_metadata: Optional[Dict] = None) -> List[Dict]:
    """Get messages, optionally filtering by metadata."""
    if not filter_metadata:
        return self.messages

    return [
        msg for msg in self.messages
        if "metadata" in msg and all(
            msg["metadata"].get(k) == v for k, v in filter_metadata.items()
        )
    ]
```

### Serialization and Persistence

Buffer Memory can be serialized to JSON for persistence:

```python
# Serialize to JSON
json_data = buffer.to_json()

# Load from JSON
new_buffer = BufferMemory.from_json(json_data)
```

The implementation handles conversion to and from JSON:

```python
def to_json(self) -> str:
    """Serialize the buffer to JSON."""
    data = {
        "messages": self.messages,
        "buffer_size": self.buffer_size,
        "summary": self.summary
    }
    return json.dumps(data)

@classmethod
def from_json(cls, json_data: str) -> "BufferMemory":
    """Create a buffer from JSON."""
    data = json.loads(json_data)
    buffer = cls(buffer_size=data["buffer_size"])
    buffer.messages = data["messages"]
    buffer.summary = data.get("summary")
    return buffer
```

## Performance Considerations

The Buffer Memory system is designed for efficiency:

- **Time Complexity**: O(1) for common operations like adding messages and retrieving context
- **Space Complexity**: O(n) where n is the buffer size
- **Memory Usage**: Configurable through buffer_size parameter

For larger buffer sizes, consider these factors:

- **Context Window Limits**: LLMs have context window limits, so very large buffers may not be fully usable
- **Summarization Cost**: Frequent summarization increases API costs
- **Retrieval Efficiency**: Smaller buffers with good summarization often outperform larger raw buffers

## Integration with Agents

Agents automatically integrate with Buffer Memory:

```python
from muxi.core.agent import Agent
from muxi.core.models.openai import OpenAIModel
from muxi.core.memory.buffer import BufferMemory

# Create buffer
buffer = BufferMemory(buffer_size=10)

# Create agent with buffer
agent = Agent(
    name="assistant",
    model=OpenAIModel("gpt-4"),
    system_message="You are a helpful assistant.",
    buffer_memory=buffer
)

# Each chat interaction automatically uses and updates the buffer
agent.chat("Hello, my name is Charlie.")
agent.chat("What's my name?")  # Will include "Charlie" in response
```

## Best Practices

- **Size Configuration**: Set buffer_size based on your application's needs:
  - Short, factual exchanges: 3-5 messages
  - Complex conversations: 8-12 messages
  - Technical discussions: 10-15 messages

- **Summarization**: Enable summarization for longer conversations to maintain context while controlling token usage

- **Metadata Usage**: Use metadata to track important message attributes (user_id, session_id, etc.)

- **User Partitioning**: For multi-user scenarios, filter messages by user_id metadata

## Related Topics

- [Long-Term Memory](../long-term) - Persistent memory storage
- [Multi-User Memory (Memobase)](../memobase) - User-specific memory partitioning
- [Domain Knowledge](../domain-knowledge) - Structured knowledge integration
