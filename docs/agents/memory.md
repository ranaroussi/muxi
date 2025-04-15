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

`configs/muxi_config.json`

```json
{
    "agent_id": "assistant",
    "description": "A helpful assistant with short-term memory for conversations.",
    "model": {
        "provider": "openai",
        "api_key": "${OPENAI_API_KEY}",
        "model": "gpt-4o"
    }
}
```

`app.py`

```python
from muxi import muxi
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize MUXI with buffer memory
app = muxi(
    buffer_memory=20,
    config_file="configs/muxi_config.json"
)

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
from muxi.core.agent import Agent
from muxi.models.providers.openai import OpenAIModel
from muxi.server.memory.buffer import BufferMemory

# Initialize components
model = OpenAIModel(
    api_key=os.getenv("OPENAI_API_KEY"),
    model="gpt-4o"
)
buffer = BufferMemory(15)

# Initialize orchestrator with buffer memory
orchestrator = Orchestrator(
    buffer_memory=buffer
)

# Create an agent that will use the orchestrator's memory
orchestrator.create_agent(
    agent_id="assistant",
    description="A helpful assistant with short-term memory for conversations.",
    model=model
)

# The agent will remember the conversation context
response1 = orchestrator.chat("assistant", "My name is Alice.")
print(response1)  # The agent acknowledges and remembers the name

response2 = orchestrator.chat("assistant", "What's my name?")
print(response2)  # The agent should respond with "Alice"
```

## Long-Term Memory

Long-term memory provides persistent storage for important information across sessions. MUXI supports two database options for long-term memory:

1. **PostgreSQL with pgvector**: Recommended for production and multi-user deployments
2. **SQLite with sqlite-vec**: Ideal for local development and single-user deployments

{: .note }
> Long-term memory requires a database. MUXI makes it easy to use either PostgreSQL or SQLite based on your needs.

### When to Use Each Database Option

**Choose SQLite with sqlite-vec for:**
- Local development and testing
- Single-user applications
- Edge computing and resource-constrained environments
- Situations where a simple file-based database is preferred
- Rapid prototyping and proof-of-concept projects

**Choose PostgreSQL with pgvector for:**
- Production environments
- Multi-user applications
- High-throughput systems
- Enterprise deployments with high availability requirements
- Scenarios requiring horizontal scaling

### PostgreSQL Configuration Example

<h4>Declarative way</h4>

```yaml
# configs/muxi_config.yaml
---
agents:
  - agent_id: assistant
    description: A helpful assistant with PostgreSQL-based long-term memory.
    model:
      provider: openai
      api_key: "${OPENAI_API_KEY}"
      model: gpt-4o
```

```python
# app.py
from muxi import muxi
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Initialize MUXI with both buffer and PostgreSQL long-term memory
app = muxi(
    buffer_memory=15,
    long_term_memory="postgresql://user:pass@localhost/db",
    config_file="configs/muxi_config.yaml"
)

# The agent will store important information in long-term memory
await app.chat("assistant", "Remember that my favorite color is blue.")
```

### SQLite Configuration Example

<h4>Declarative way</h4>

```yaml
# configs/muxi_config.yaml
---
agents:
  - agent_id: assistant
    description: A helpful assistant with SQLite-based long-term memory.
    model:
      provider: openai
      api_key: "${OPENAI_API_KEY}"
      model: gpt-4o
```

{: .note }
> You can also use `long_term_memory=True` to use a default SQLite database named "muxi.db" in your application's root directory.

```python
# app.py
from muxi import muxi
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Initialize MUXI with both buffer and SQLite long-term memory
app = muxi(
    buffer_memory=15,
    long_term_memory="sqlite:///data/memory.db",
    config_file="configs/muxi_config.yaml"
)

# The agent will store important information in long-term memory
await app.chat("assistant", "Remember that my favorite color is blue.")
```

<h4>Programmatic way</h4>

```python
import os
from muxi.core.orchestrator import Orchestrator
from muxi.core.agent import Agent
from muxi.models.providers.openai import OpenAIModel
from muxi.server.memory.buffer import BufferMemory
from muxi.server.memory.long_term import LongTermMemory

# Initialize components
model = OpenAIModel(
    api_key=os.getenv("OPENAI_API_KEY"),
    model="gpt-4o"
)
buffer = BufferMemory(15)

# Option 1: PostgreSQL long-term memory (for production/multi-user deployments)
postgres_connection = "postgresql://user:password@localhost:5432/muxi"
# Or use environment variable:
# postgres_connection = os.getenv("POSTGRES_DATABASE_URL")

# Option 2: SQLite long-term memory (for local/single-user deployments)
sqlite_connection = "sqlite:///data/memory.db"

# Choose the memory system based on your needs
connection_string = sqlite_connection  # or postgres_connection
long_term_memory = LongTermMemory(connection_string=connection_string)

# Initialize orchestrator with both buffer and long-term memory
orchestrator = Orchestrator(
    buffer_memory=buffer,
    long_term_memory=long_term_memory
)

# Create an agent that will use the orchestrator's memory
orchestrator.create_agent(
    agent_id="assistant",
    description="A helpful assistant with both short-term and long-term memory capabilities.",
    model=model
)

# The agent will store important information in long-term memory
orchestrator.chat("assistant", "Remember that my favorite color is blue.")
```

### Searching Long-Term Memory

You can explicitly search memory, regardless of whether you're using PostgreSQL or SQLite:

<h4>Declarative way</h4>

```python
# Search the memory explicitly
search_results = await app.orchestrator.search_memory(
    query="What do I like?",
    agent_id="assistant",  # Optional: filter by agent_id
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
# Search the orchestrator's memory for relevant information
results = orchestrator.search_memory(
    query="What do I like?",
    agent_id="assistant",  # Optional: filter by agent_id
    k=3,  # Return top 3 results
    threshold=0.7  # Minimum similarity threshold (0-1)
)

print("Memory search results:")
for result in results:
    print(f"Memory: {result['content']}")
    print(f"Relevance: {result['similarity']}")
    print("---")
```

## Multi-User Memory with Memobase

For applications serving multiple users, MUXI provides the Memobase system, which partitions memory by user ID.

{: .note }
> For multi-user applications, we recommend using PostgreSQL with pgvector due to its better concurrency handling and scalability.

### Setting Up Memobase

<h4>Declarative way</h4>

```python
# app.py
from muxi import muxi
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Initialize MUXI with multi-user memory
app = muxi(
    buffer_memory=15,
    long_term_memory="postgresql://user:pass@localhost/db",
    config_file="configs/muxi_config.yaml"
)

# Chat with the agent as different users
user_1_response = await app.chat(
    message="My name is Bob and I like hiking.",
    agent_name="assistant",
    user_id="user_1"
)

user_2_response = await app.chat(
    message="My name is Carol and I like painting.",
    agent_name="assistant",
    user_id="user_2"
)

# Later, the agent will remember each user's specific information
user_1_question = await app.chat(
    message="What hobby do I enjoy?",
    agent_name="assistant",
    user_id="user_1"
)
print(f"User 1 response: {user_1_question}")  # Should mention hiking

user_2_question = await app.chat(
    message="What hobby do I enjoy?",
    agent_name="assistant",
    user_id="user_2"
)
print(f"User 2 response: {user_2_question}")  # Should mention painting
```

<h4>Programmatic way</h4>

```python
# Initialize orchestrator with multi-user memory support
from muxi.server.memory.memobase import Memobase

# Create Memobase for multi-user support
long_term_memory = LongTermMemory(connection_string="postgresql://user:pass@localhost/db")
memobase = Memobase(long_term_memory=long_term_memory)

# Initialize orchestrator with multi-user memory
orchestrator = Orchestrator(
    buffer_memory=buffer,
    long_term_memory=memobase
)

# Create an agent
orchestrator.create_agent(
    agent_id="assistant",
    description="A helpful assistant with multi-user memory.",
    model=model
)

# Chat with the agent as different users
user_1_response = orchestrator.chat(
    "assistant",
    "My name is Bob and I like hiking.",
    user_id="user_1"
)

user_2_response = orchestrator.chat(
    "assistant",
    "My name is Carol and I like painting.",
    user_id="user_2"
)

# Later, the agent will remember each user's specific information
user_1_question = orchestrator.chat(
    "assistant",
    "What hobby do I enjoy?",
    user_id="user_1"
)
print(f"User 1 response: {user_1_question}")  # Should mention hiking

user_2_question = orchestrator.chat(
    "assistant",
    "What hobby do I enjoy?",
    user_id="user_2"
)
print(f"User 2 response: {user_2_question}")  # Should mention painting
```

## Database Technical Details

### SQLite with sqlite-vec

MUXI uses the sqlite-vec Python package for vector operations in SQLite. This provides several advantages:

- **Simplified installation**: No need to manage binary extensions
- **Cross-platform compatibility**: Works consistently across operating systems
- **Simple deployment**: Single file database easy to back up and manage
- **Suitable for edge computing**: Runs well in resource-constrained environments

### PostgreSQL with pgvector

For production and multi-user deployments, MUXI supports PostgreSQL with the pgvector extension:

- **Horizontal scaling**: Supports larger deployments with multiple users
- **Advanced indexing**: Better performance for large vector datasets
- **Concurrency**: Handles multiple simultaneous connections efficiently
- **Enterprise features**: Replication, backup, and monitoring options

## Best Practices for Memory Management

1. **Balance Buffer Size**: Keep buffer memory large enough for context but not too large for model context limits
2. **Prioritize Important Information**: Store only significant information in long-term memory
3. **Use Context Knowledge for Static Information**: Context knowledge is perfect for unchanging facts
4. **Separate Concerns with Memobase**: Always use Memobase for multi-user applications
5. **Choose the Right Database**:
   - Use SQLite for development, single-user, and resource-constrained environments
   - Use PostgreSQL for production, multi-user, and high-scalability needs
6. **Regular Memory Maintenance**: Implement policies to clear or archive old memories
7. **Security and Privacy**: Be mindful of what information you store and for how long

## Next Steps

Now that you've added memory to your agents, you might want to:

- Learn how to create multi-agent systems - see [Multi-Agent Systems](../multi-agent/)
- Configure your agents with specific settings - see [Agent Configuration](../configuration/)
- Explore deep dives into memory architecture - see [Memory System](../../technical/memory/)
