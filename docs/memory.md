# Memory Systems

Memory is a crucial component of the AI Agent Framework that allows agents to retain information over time. The framework provides three complementary memory systems:

1. **Buffer Memory**: Short-term memory for the current conversation context
2. **Long-term Memory**: Persistent memory for storing information across multiple sessions
3. **Memobase**: Multi-user memory system that partitions memories by user ID

## Buffer Memory

Buffer memory is designed to store the recent conversation history, providing context for the agent's responses.

### How Buffer Memory Works

Buffer memory:
- Maintains a fixed-size buffer of recent messages
- Ensures the context stays within token limits for LLM processing
- Uses FAISS for semantic search capabilities
- Handles automatic summarization when needed

### Using Buffer Memory

#### Basic Initialization

```python
from src.memory.buffer import BufferMemory

# Create a buffer memory with default settings
buffer = BufferMemory()

# Create a buffer memory with custom settings
buffer = BufferMemory(
    max_tokens=4000,  # Maximum token count to maintain
    model="gpt-3.5-turbo",  # Model used for token counting
    summarize_after=20  # Summarize after 20 messages
)
```

#### Adding Messages

```python
# Add a user message
await buffer.add_message("user", "What is artificial intelligence?")

# Add an assistant message
await buffer.add_message("assistant", "Artificial intelligence is the simulation of human intelligence by machines.")

# Add a system message
await buffer.add_message("system", "The user seems interested in AI concepts.")
```

#### Retrieving Messages

```python
# Get all messages
messages = await buffer.get_messages()
for msg in messages:
    print(f"{msg['role']}: {msg['content']}")

# Get formatted messages for sending to an LLM
formatted_messages = await buffer.get_formatted_messages()
```

#### Searching the Buffer

```python
# Search for relevant messages
search_results = await buffer.search("machine learning", top_k=3)
for result in search_results:
    print(f"Score: {result['score']}, Message: {result['message']}")
```

#### Clearing the Buffer

```python
# Clear all messages
await buffer.clear()
```

## Long-term Memory

Long-term memory provides persistent storage for important information across multiple sessions, using a vector database for efficient semantic retrieval.

### How Long-term Memory Works

Long-term memory:
- Stores embeddings of important information in a database
- Uses pgvector extension in PostgreSQL for vector similarity search
- Enables retrieval of relevant information based on semantic similarity
- Persists across sessions and agent restarts

### Using Long-term Memory

#### Initialization

```python
from src.memory.long_term import LongTermMemory

# Create a long-term memory with database connection
memory = LongTermMemory(
    connection_string="postgresql://user:password@localhost:5432/ai_agent_db",
    table_name="agent_memories",
    embedding_model="text-embedding-ada-002"  # OpenAI embedding model
)

# Initialize the database schema (run once)
await memory.initialize()
```

#### Storing Memories

```python
# Store a simple memory
await memory.store("The capital of France is Paris.")

# Store a memory with metadata
await memory.store(
    "The user prefers Python over JavaScript for data science projects.",
    metadata={
        "source": "conversation",
        "date": "2023-06-15",
        "topic": "programming preferences"
    }
)

# Store a memory with a custom embedding
custom_embedding = [0.1, 0.2, 0.3, ...]  # Your custom embedding
await memory.store_with_embedding(
    "Solar panels convert sunlight into electricity.",
    embedding=custom_embedding
)
```

#### Retrieving Memories

```python
# Search for relevant memories
results = await memory.search("What programming language is best for data science?", top_k=5)
for result in results:
    print(f"Score: {result['score']}, Memory: {result['text']}")

# Search with metadata filters
results = await memory.search(
    "programming preferences",
    top_k=3,
    metadata_filter={"topic": "programming preferences"}
)
```

#### Advanced Operations

```python
# Delete a specific memory
await memory.delete(memory_id)

# Clear all memories
await memory.clear()

# Update a memory
await memory.update(memory_id, "The user now prefers JavaScript over Python for web development.")
```

## Memobase

Memobase is a multi-user memory manager that provides user-specific memory contexts using PostgreSQL/PGVector for storage. It's ideal for multi-tenant applications where each user should have their own memory context.

### How Memobase Works

Memobase:
- Partitions memories by user ID
- Creates separate collections for each user
- Maintains user context between sessions
- Uses PostgreSQL/PGVector for efficient semantic search
- Provides a simple interface for user-specific operations

### Using Memobase

#### Initialization

```python
from src.memory.long_term import LongTermMemory
from src.memory.memobase import Memobase

# First, initialize a long-term memory instance
long_term_memory = LongTermMemory(
    connection_string="postgresql://user:password@localhost:5432/ai_agent_db"
)

# Then create a Memobase instance with the long-term memory
memobase = Memobase(
    long_term_memory=long_term_memory,
    default_user_id=0  # Default user ID for single-user mode
)
```

#### Adding Memories for Specific Users

```python
# Add a memory for user 123
await memobase.add(
    content="My name is Alice",
    metadata={"type": "user_info"},
    user_id=123
)

# Add a memory for user 456
await memobase.add(
    content="My name is Bob",
    metadata={"type": "user_info"},
    user_id=456
)

# Add to default user (single-user mode)
await memobase.add(
    content="System-wide information",
    metadata={"type": "system_info"}
)
```

#### Searching Memories for Specific Users

```python
# Search for user 123's memories
results = await memobase.search(
    query="What is my name?",
    user_id=123,
    limit=5
)
# Will find "My name is Alice"

# Search for user 456's memories
results = await memobase.search(
    query="What is my name?",
    user_id=456,
    limit=5
)
# Will find "My name is Bob"

# Search default user memories
results = await memobase.search(
    query="system information"
)
# Will find "System-wide information"
```

#### Clearing User-Specific Memories

```python
# Clear all memories for user 123
memobase.clear_user_memory(user_id=123)

# Clear default user memories
memobase.clear_user_memory()
```

#### Retrieving All Memories for a User

```python
# Get all memories for user 123
memories = memobase.get_user_memories(
    user_id=123,
    limit=10,
    sort_by="created_at",
    ascending=False
)

# Display the memories
for memory in memories:
    print(f"Content: {memory['content']}")
    print(f"Metadata: {memory['metadata']}")
    print(f"Created at: {memory['created_at']}")
```

### Advanced Filtering

```python
# Search with additional metadata filters
results = await memobase.search(
    query="info",
    user_id=123,
    additional_filter={"type": "user_info"}
)
```

## Integrating Memory with Agents

### Using Memobase with Agents

```python
from src.core.orchestrator import Orchestrator
from src.models import OpenAIModel
from src.memory.buffer import BufferMemory
from src.memory.long_term import LongTermMemory
from src.memory.memobase import Memobase

# Initialize memory systems
buffer_memory = BufferMemory()
long_term_memory = LongTermMemory(
    connection_string="postgresql://user:password@localhost:5432/ai_agent_db"
)
memobase = Memobase(long_term_memory=long_term_memory)

# Create an agent with multi-user support
orchestrator = Orchestrator()
orchestrator.create_agent(
    agent_id="multi_user_agent",
    model=OpenAIModel(model="gpt-4o"),
    buffer_memory=buffer_memory,
    memobase=memobase,
    system_message="You are an assistant that remembers information about different users."
)

# Chat with the agent with different user contexts
response1 = await orchestrator.chat("multi_user_agent", "My name is Alice", user_id=123)
response2 = await orchestrator.chat("multi_user_agent", "My name is Bob", user_id=456)

# Each user has their own memory context
response1 = await orchestrator.chat("multi_user_agent", "What is my name?", user_id=123)
# Agent responds: "Your name is Alice."

response2 = await orchestrator.chat("multi_user_agent", "What is my name?", user_id=456)
# Agent responds: "Your name is Bob."
```

### Memory Augmented Generation

When an agent processes a user message with both buffer and long-term memory:

1. The user message is added to buffer memory
2. The system searches long-term memory for relevant information
3. Relevant memories are included in the context provided to the LLM
4. The LLM response is added to buffer memory
5. Important information from the interaction may be stored in long-term memory

```python
async def process_message_with_memory(agent, user_message):
    # Add the user message to buffer memory
    await agent.buffer_memory.add_message("user", user_message)

    # Retrieve relevant memories
    memories = await agent.long_term_memory.search(user_message, top_k=3)

    # Format memories as context
    memory_context = "Relevant information from my memory:\n"
    for memory in memories:
        memory_context += f"- {memory['text']}\n"

    # Create a system message with the memory context
    await agent.buffer_memory.add_message("system", memory_context)

    # Get all messages for the LLM
    messages = await agent.buffer_memory.get_formatted_messages()

    # Send to LLM for processing
    response = await agent.model.generate(messages)

    # Add the response to buffer memory
    await agent.buffer_memory.add_message("assistant", response)

    # Store important information in long-term memory
    # (This could be automated or triggered based on certain conditions)
    if "important_fact" in response:
        await agent.long_term_memory.store(response)

    return response
```

## Custom Memory Implementations

You can create custom memory implementations by extending the base classes:

### Custom Buffer Memory

```python
from src.memory.buffer import BufferMemory

class CustomBufferMemory(BufferMemory):
    def __init__(self, max_tokens=2000, **kwargs):
        super().__init__(max_tokens=max_tokens, **kwargs)
        self.custom_property = kwargs.get("custom_property")

    async def add_message(self, role, content):
        # Custom pre-processing
        if role == "user":
            content = f"[User Input]: {content}"

        # Call the parent method
        await super().add_message(role, content)

        # Custom post-processing
        # e.g., log the message, trigger an event, etc.
        print(f"Added message: {role}: {content[:30]}...")

    async def custom_method(self):
        # Implement custom functionality
        pass
```

### Custom Long-term Memory

```python
from src.memory.long_term import LongTermMemory

class CustomLongTermMemory(LongTermMemory):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.importance_threshold = kwargs.get("importance_threshold", 0.7)

    async def store(self, text, metadata=None):
        # Add importance score
        importance = self._calculate_importance(text)

        if metadata is None:
            metadata = {}

        metadata["importance"] = importance

        # Only store if important enough
        if importance >= self.importance_threshold:
            return await super().store(text, metadata)

        return None

    def _calculate_importance(self, text):
        # Custom logic to determine importance
        # This is a simplified example
        keywords = ["critical", "important", "remember", "key fact"]
        score = sum(1 for keyword in keywords if keyword in text.lower()) / len(keywords)
        return score
```

## Memory Strategies

### Context Window Management

To effectively manage the LLM's context window:

```python
class ContextWindowManager:
    def __init__(self, buffer_memory, max_tokens=4000):
        self.buffer_memory = buffer_memory
        self.max_tokens = max_tokens

    async def optimize_context(self):
        # Get current token count
        messages = await self.buffer_memory.get_messages()
        current_tokens = self._count_tokens(messages)

        if current_tokens > self.max_tokens:
            # Summarize oldest messages
            oldest_messages = messages[:len(messages)//2]
            summary = await self._summarize_messages(oldest_messages)

            # Replace oldest messages with summary
            await self.buffer_memory.clear()
            await self.buffer_memory.add_message("system", f"Summary of previous conversation: {summary}")

            # Add back the most recent messages
            for msg in messages[len(messages)//2:]:
                await self.buffer_memory.add_message(msg["role"], msg["content"])

    async def _summarize_messages(self, messages):
        # Implementation of summarization logic
        # This could use the LLM itself
        pass

    def _count_tokens(self, messages):
        # Implementation of token counting
        pass
```

### Information Extraction for Long-term Storage

```python
class MemoryExtractor:
    def __init__(self, model, long_term_memory):
        self.model = model
        self.long_term_memory = long_term_memory

    async def extract_and_store(self, conversation):
        # Prompt the LLM to extract important information
        prompt = f"""
        Please extract important facts and information from this conversation that should be remembered long-term.
        Format each fact as a separate bullet point.

        Conversation:
        {conversation}

        Important facts to remember:
        """

        extraction_result = await self.model.generate([{"role": "user", "content": prompt}])

        # Parse the bullet points
        facts = [line.strip("- ") for line in extraction_result.split("\n") if line.strip().startswith("-")]

        # Store each fact in long-term memory
        for fact in facts:
            await self.long_term_memory.store(fact)

        return facts
```

## Best Practices

1. **Buffer Size Management**: Set appropriate buffer sizes to balance context richness with token limits

2. **Memory Pruning**: Regularly clean up outdated or irrelevant memories from long-term storage

3. **Semantic Search Optimization**: Fine-tune search parameters for better retrieval relevance

4. **Memory Metadata**: Use detailed metadata to enhance filtering and retrieval capabilities

5. **Backup and Recovery**: Implement backup systems for long-term memory to prevent data loss

6. **Privacy Considerations**: Implement proper data retention policies and user controls for stored memories

## Troubleshooting

### Buffer Memory Issues

- **Out of Memory Errors**: Reduce max_tokens or implement more aggressive summarization
- **Context Loss**: Adjust the summarization strategy to preserve important information
- **Relevance Issues**: Fine-tune the embedding model for better semantic search

### Long-term Memory Issues

- **Database Connection Failures**: Check connection strings and ensure the database is running
- **Slow Queries**: Add appropriate indexes to the vector database
- **Embedding Generation Errors**: Verify API keys and model availability for embedding generation

## Next Steps

After implementing memory systems, you might want to explore:

- Creating [custom tools](./tools.md) that can access and manipulate memory
- Setting up [WebSocket connections](./websocket.md) for real-time memory updates
- Implementing advanced [MCP features](./mcp.md) to better control how the LLM uses memory
- Developing [agent collaboration](./orchestrator.md) methods that share memory between agents
