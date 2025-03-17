---
layout: default
title: Adding Memory
parent: Building Agents
nav_order: 3
permalink: /agents/memory/
---

# Adding Memory

This guide explains how to enhance your MUXI agents with memory capabilities, allowing them to remember previous interactions and store important information.

## Memory Types in MUXI

MUXI provides several memory systems:

1. **Buffer Memory**: Short-term memory for recent conversations
2. **Long-Term Memory**: Persistent storage for important information
3. **Memobase**: User-specific memory management for multi-user applications

## Buffer Memory

Buffer memory is a short-term memory system that stores recent conversation history, enabling agents to maintain context within a single session.

### Basic Buffer Memory Example

```python
from muxi.core.orchestrator import Orchestrator
from muxi.core.models.openai import OpenAIModel
from muxi.core.memory.buffer import BufferMemory

# Initialize components
orchestrator = Orchestrator()
model = OpenAIModel(model="gpt-4o")
buffer = BufferMemory()

# Create an agent with buffer memory
orchestrator.create_agent(
    agent_id="assistant",
    model=model,
    buffer_memory=buffer
)

# The agent will remember the conversation context
response1 = orchestrator.chat("assistant", "My name is Alice.")
print(response1)  # The agent acknowledges and remembers the name

response2 = orchestrator.chat("assistant", "What's my name?")
print(response2)  # The agent should respond with "Alice"
```

### Customizing Buffer Memory

You can customize buffer memory settings:

```python
# Create a buffer memory with custom settings
buffer = BufferMemory(
    max_tokens=2000,           # Maximum tokens to store
    include_system_messages=True,  # Include system messages in the context
    include_timestamps=True    # Add timestamps to messages
)
```

## Long-Term Memory

Long-term memory provides persistent storage for important information across sessions. MUXI uses vector databases to store and retrieve memories semantically.

### Basic Long-Term Memory Example

```python
from muxi.core.orchestrator import Orchestrator
from muxi.core.models.openai import OpenAIModel
from muxi.core.memory.buffer import BufferMemory
from muxi.core.memory.long_term import LongTermMemory

# Initialize components
orchestrator = Orchestrator()
model = OpenAIModel(model="gpt-4o")
buffer = BufferMemory()
long_term = LongTermMemory()  # This requires a database connection

# Create an agent with both buffer and long-term memory
orchestrator.create_agent(
    agent_id="assistant",
    model=model,
    buffer_memory=buffer,
    long_term_memory=long_term
)

# The agent will store important information in long-term memory
orchestrator.chat("assistant", "Remember that my favorite color is blue.")

# Later, even after restarting the application...
# (Simulated by clearing the buffer memory)
buffer.clear()

# The agent can recall information from long-term memory
response = orchestrator.chat("assistant", "What's my favorite color?")
print(response)  # Should mention "blue"
```

### Configuring Long-Term Memory

Long-term memory requires a database. MUXI supports multiple backends, with PostgreSQL (using pgvector) being the default:

```python
# Configure long-term memory with PostgreSQL
long_term = LongTermMemory(
    connection_string="postgresql://username:password@localhost:5432/muxidb",
    collection="agent_memories",
    embedding_model="text-embedding-3-small"
)
```

### Searching Long-Term Memory

You can explicitly search an agent's memory:

```python
# Search the agent's memory for relevant information
results = agent.search_memory(
    query="What do I like?",
    k=3,  # Return top 3 results
    threshold=0.7  # Minimum similarity threshold (0-1)
)

for result in results:
    print(f"Memory: {result['content']}")
    print(f"Relevance: {result['similarity']}")
    print("---")
```

## Multi-User Memory with Memobase

For applications serving multiple users, MUXI provides the Memobase system, which partitions memory by user ID.

### Setting Up Memobase

```python
from muxi.core.orchestrator import Orchestrator
from muxi.core.models.openai import OpenAIModel
from muxi.core.memory.buffer import BufferMemory
from muxi.core.memory.long_term import LongTermMemory
from muxi.core.memory.memobase import Memobase

# Initialize memory systems
buffer = BufferMemory()
long_term = LongTermMemory()
memobase = Memobase(long_term_memory=long_term)

# Create an agent with Memobase for multi-user support
orchestrator = Orchestrator()
orchestrator.create_agent(
    agent_id="assistant",
    model=OpenAIModel(model="gpt-4o"),
    buffer_memory=buffer,
    long_term_memory=memobase  # Use Memobase instead of directly using long_term
)

# Chat with the agent as different users
user_1_response = orchestrator.chat(
    agent_id="assistant",
    message="My name is Bob and I like hiking.",
    user_id="user_1"
)

user_2_response = orchestrator.chat(
    agent_id="assistant",
    message="My name is Carol and I like painting.",
    user_id="user_2"
)

# Later, the agent will remember each user's specific information
user_1_question = orchestrator.chat(
    agent_id="assistant",
    message="What hobby do I enjoy?",
    user_id="user_1"
)
print(f"User 1 response: {user_1_question}")  # Should mention hiking

user_2_question = orchestrator.chat(
    agent_id="assistant",
    message="What hobby do I enjoy?",
    user_id="user_2"
)
print(f"User 2 response: {user_2_question}")  # Should mention painting
```

## Domain Knowledge

Domain knowledge provides a way to add structured information to an agent's memory:

```python
from muxi.core.orchestrator import Orchestrator
from muxi.core.models.openai import OpenAIModel
from muxi.core.memory.buffer import BufferMemory
from muxi.core.memory.domain_knowledge import DomainKnowledge

# Initialize domain knowledge
domain_knowledge = DomainKnowledge()

# Add structured knowledge
domain_knowledge.add(
    user_id="user_123",
    knowledge={
        "preferences": {
            "food": ["Italian", "Japanese"],
            "travel": ["mountains", "beaches"],
            "reading": ["science fiction", "biographies"]
        },
        "restrictions": {
            "allergies": ["nuts", "shellfish"],
            "dietary": ["vegetarian"]
        }
    }
)

# Create agent with domain knowledge
orchestrator = Orchestrator()
orchestrator.create_agent(
    agent_id="personal_assistant",
    model=OpenAIModel(model="gpt-4o"),
    buffer_memory=BufferMemory(),
    domain_knowledge=domain_knowledge
)

# The agent will access relevant domain knowledge when responding
response = orchestrator.chat(
    agent_id="personal_assistant",
    message="Can you recommend a restaurant for me?",
    user_id="user_123"
)
print(response)  # Should recommend Italian or Japanese vegetarian food, avoiding nuts and shellfish
```

## Advanced Memory Management

### Memory Lifetime Control

You can manage how long information persists in memory:

```python
# Configure memory with time-based expiration
from datetime import timedelta

buffer = BufferMemory(
    message_lifetime=timedelta(hours=1)  # Messages expire after 1 hour
)

long_term = LongTermMemory(
    default_expiration=timedelta(days=30)  # Memories expire after 30 days
)
```

### Explicit Memory Operations

You can explicitly manage memories:

```python
# Add a memory directly
agent.add_memory(
    content="User prefers English documentaries with subtitles",
    metadata={"source": "explicit", "importance": "high"},
    user_id="user_123"
)

# Clear memories
agent.clear_memory()  # Clear buffer memory
agent.clear_memory(clear_long_term=True)  # Clear both buffer and long-term memory

# Clear memory for a specific user
agent.clear_memory(user_id="user_123", clear_long_term=True)
```

## Combining Memory Systems

For optimal performance, combine different memory types:

```python
from muxi.core.orchestrator import Orchestrator
from muxi.core.models.openai import OpenAIModel
from muxi.core.memory.buffer import BufferMemory
from muxi.core.memory.long_term import LongTermMemory
from muxi.core.memory.memobase import Memobase
from muxi.core.memory.domain_knowledge import DomainKnowledge

# Initialize memory systems
buffer = BufferMemory(max_tokens=4000)
long_term = LongTermMemory(connection_string="postgresql://user:pass@localhost/muxidb")
memobase = Memobase(long_term_memory=long_term)
domain_knowledge = DomainKnowledge()

# Add domain knowledge
domain_knowledge.add(
    user_id="user_456",
    knowledge={
        "company": {
            "name": "Acme Inc.",
            "products": ["Widget A", "Widget B", "Service C"],
            "values": ["Innovation", "Customer focus", "Quality"]
        }
    }
)

# Create a fully-featured agent
orchestrator = Orchestrator()
orchestrator.create_agent(
    agent_id="enterprise_assistant",
    model=OpenAIModel(model="gpt-4o"),
    buffer_memory=buffer,
    long_term_memory=memobase,
    domain_knowledge=domain_knowledge,
    system_message="You are an enterprise assistant that helps with company information."
)

# The agent will use all memory systems together
response = orchestrator.chat(
    agent_id="enterprise_assistant",
    message="Tell me about our company's products.",
    user_id="user_456"
)
print(response)  # Should include information about Acme Inc.'s products
```

## Best Practices for Memory Management

1. **Balance Buffer Size**: Keep buffer memory large enough for context but not too large for model context limits

2. **Prioritize Important Information**: Store only significant information in long-term memory

3. **Use Domain Knowledge for Static Information**: Domain knowledge is perfect for unchanging facts

4. **Separate Concerns with Memobase**: Always use Memobase for multi-user applications

5. **Regular Memory Maintenance**: Implement policies to clear or archive old memories

6. **Security and Privacy**: Be mindful of what information you store and for how long

## Next Steps

Now that you've added memory to your agents, you might want to:

- Learn how to create multi-agent systems - see [Multi-Agent Systems](../multi-agent/)
- Configure your agents with specific tools - see [Agent Configuration](../configuration/)
- Explore deep dives into memory architecture - see [Memory System](../../technical/memory/)
