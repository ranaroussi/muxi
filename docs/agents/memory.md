---
layout: default
title: Context Memory
parent: Building Agents
nav_order: 2
permalink: /agents/memory
---

# Context Memory

This guide explains how to enhance your MUXI agents with user-level memory capabilities, allowing them to remember previous interactions with users, maintain chat context, and store important information across conversations.

## Memory Types in MUXI

MUXI provides several memory systems:

1. **Buffer Memory**: Short-term memory for recent conversations
2. **Long-Term Memory**: Persistent storage for important information
3. **Memobase**: User-specific memory management for multi-user applications

## Buffer Memory

Buffer memory is a short-term memory system that stores recent conversation history, enabling agents to maintain context within a single session.

{: .note }
> Buffer memory is turned on by default (with a buffer size of 5). If you want to turn it off, set the buffer to zero.

### Basic Buffer Memory Example

<h4>Declarative way</h4>

`configs/buffer_memory_agent.json`

```json
{
  "agent_id": "assistant",
  "description": "A helpful assistant with short-term memory for conversations.",
  "model": {
    "provider": "openai",
    "api_key": "${OPENAI_API_KEY}",
    "model": "gpt-4o"
  },
  "memory": {
    "buffer": 20
  }
}
```

`app.py`

```python
from muxi import muxi
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize MUXI
app = muxi()

# Add agent from configuration
app.add_agent("configs/buffer_memory_agent.json")

# The agent will remember the conversation context
response1 = await app.chat("assistant", "My name is Alice.")
print(response1)  # The agent acknowledges and remembers the name

response2 = await app.chat("assistant", "What's my name?")
print(response2)  # The agent should respond with "Alice"
```

<h4>Programmatic way</h4>

```python
import os
from muxi.core.orchestrator import Orchestrator
from muxi.core.models.openai import OpenAIModel
from muxi.core.memory.buffer import BufferMemory

# Initialize components
orchestrator = Orchestrator()
model = OpenAIModel(
    api_key=os.getenv("OPENAI_API_KEY"),
    model="gpt-4o"
)
buffer = BufferMemory()

# Create an agent with buffer memory
orchestrator.create_agent(
    agent_id="assistant",
    description="A helpful assistant with short-term memory for conversations.",
    model=model,
    buffer_memory=buffer
)

# The agent will remember the conversation context
response1 = orchestrator.chat("assistant", "My name is Alice.")
print(response1)  # The agent acknowledges and remembers the name

response2 = orchestrator.chat("assistant", "What's my name?")
print(response2)  # The agent should respond with "Alice"
```

## Long-Term Memory

Long-term memory provides persistent storage for important information across sessions. MUXI uses vector databases to store and retrieve memories semantically.

{: .warning }
> Long-term memory requires database access. Please ensure you set `POSTGRES_DATABASE_URL` in your environment variables.

### Basic Long-Term Memory Example

<h4>Declarative way</h4>


```yaml
# configs/long_term_memory_agent.yaml
---
agent_id: assistant
description: A helpful assistant with both short-term and long-term memory capabilities.
model:
  provider: openai
  api_key: "${OPENAI_API_KEY}"
  model: gpt-4o
memory:
  buffer: 15
  long_term: true # <= set this to true

```


```python
# app1.py
from muxi import muxi
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize MUXI with database configuration
app = muxi()

# Set up database for long-term memory (or use environment variables)
app.configure_database(connection_string=os.getenv("POSTGRES_DATABASE_URL"))

# Add agent with long-term memory
app.add_agent("configs/long_term_memory_agent.yaml")

# The agent will store important information in long-term memory
await app.chat("assistant", "Remember that my favorite color is blue.")
```

`<-- restart the application -->`

```python
# app2.py
from muxi import muxi
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize MUXI with database configuration
app = muxi()

# Set up database for long-term memory (or use environment variables)
app.configure_database(connection_string=os.getenv("POSTGRES_DATABASE_URL"))

# Add agent with long-term memory
app.add_agent("configs/long_term_memory_agent.yaml")

# The agent can recall information from long-term memory
response = await app.chat("assistant", "What's my favorite color?")
print(response)  # Should mention "blue"
```

<h4>Programmatic way</h4>

```python
import os
from muxi.core.orchestrator import Orchestrator
from muxi.core.models.openai import OpenAIModel
from muxi.core.memory.buffer import BufferMemory
from muxi.core.memory.long_term import LongTermMemory

# Initialize components
orchestrator = Orchestrator()
model = OpenAIModel(
    api_key=os.getenv("OPENAI_API_KEY"),
    model="gpt-4o"
)
buffer = BufferMemory()
long_term = LongTermMemory(
    connection_string=os.getenv("POSTGRES_DATABASE_URL")
)  # This requires a database connection

# Create an agent with both buffer and long-term memory
orchestrator.create_agent(
    agent_id="assistant",
    description="A helpful assistant with both short-term and long-term memory capabilities.",
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

### Searching Long-Term Memory

You can explicitly search an agent's memory:

<h4>Declarative way</h4>

```python
# Search the memory explicitly
search_results = await app.search_memory(
    agent_id="assistant",
    query="What do I like?",
    k=3,  # Return top 3 results
    threshold=0.7  # Minimum similarity threshold (0-1)
)

print("Memory search results:")
for result in search_results:
    print(f"Memory: {result['content']}")
    print(f"Relevance: {result['similarity']}")
    print("---")
```

<h4>Programmatic way</h4>

```python
# Search the agent's memory for relevant information
results = agent.search_memory(
    query="What do I like?",
    k=3,  # Return top 3 results
    threshold=0.7  # Minimum similarity threshold (0-1)
)

# Or, search the all agents' memory for relevant information
# results = orchestrator.search_memory(
#     query="What do I like?",
#     k=3,  # Return top 3 results
#     threshold=0.7  # Minimum similarity threshold (0-1)
# )

print("Memory search results:")
for result in results:
    print(f"Memory: {result['content']}")
    print(f"Relevance: {result['similarity']}")
    print("---")
```

## Multi-User Memory with Memobase

For applications serving multiple users, MUXI provides the Memobase system, which partitions memory by user ID.

### Setting Up Memobase

<h4>Declarative way</h4>

```python
# app.py
from muxi import muxi
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Initialize MUXI
app = muxi()

# Add multi-user agent
app.add_agent("configs/long_term_memory_agent.yaml")

# Chat with the agent as different users
user_1_response = await app.chat(
    message="My name is Bob and I like hiking.",
    user_id="user_1"
)

user_2_response = await app.chat(
    message="My name is Carol and I like painting.",
    user_id="user_2"
)

# Later, the agent will remember each user's specific information
user_1_question = await app.chat(
    message="What hobby do I enjoy?",
    user_id="user_1"
)
print(f"User 1 response: {user_1_question}")  # Should mention hiking

user_2_question = await app.chat(
    message="What hobby do I enjoy?",
    user_id="user_2"
)
print(f"User 2 response: {user_2_question}")  # Should mention painting
```

<h4>Programmatic way</h4>

```python
...
# Chat with the agent as different users
user_1_response = orchestrator.chat(
    message="My name is Bob and I like hiking.",
    user_id="user_1"
)

user_2_response = orchestrator.chat(
    message="My name is Carol and I like painting.",
    user_id="user_2"
)

# Later, the agent will remember each user's specific information
user_1_question = orchestrator.chat(
    message="What hobby do I enjoy?",
    user_id="user_1"
)
print(f"User 1 response: {user_1_question}")  # Should mention hiking

user_2_question = orchestrator.chat(
    message="What hobby do I enjoy?",
    user_id="user_2"
)
print(f"User 2 response: {user_2_question}")  # Should mention painting
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
- Configure your agents with specific settings - see [Agent Configuration](../configuration/)
- Explore deep dives into memory architecture - see [Memory System](../../technical/memory/)
