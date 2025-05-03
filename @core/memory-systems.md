# Memory Systems in Muxi Core

Memory systems are a core component of Muxi Core, enabling agents to retain information across conversation turns and sessions. This document provides a comprehensive overview of the memory capabilities available in Muxi Core.

## Memory Architecture

Muxi Core provides three primary memory systems, each serving a different purpose:

```mermaid
graph TD
    subgraph "Muxi Memory Architecture"
        Orchestrator -->|Manages| Buffer[Buffer Memory]
        Orchestrator -->|Manages| LongTerm[Long-Term Memory]
        Orchestrator -->|Manages| Memobase[Memobase]

        Buffer -->|Recent Context| Agent
        LongTerm -->|Persistent Knowledge| Agent
        Memobase -->|User Information| Agent

        subgraph "Buffer Memory"
            Buffer --> FAISS[FAISS Vector Index]
            Buffer --> Recency[Recency Retrieval]
            Buffer --> Hybrid[Hybrid Scoring]
        end

        subgraph "Long-Term Memory"
            LongTerm --> Embedding[Vector Embeddings]
            LongTerm --> Postgres[PostgreSQL Storage]
            LongTerm --> Categories[Knowledge Categories]
        end

        subgraph "Memobase"
            Memobase --> MongoDB[MongoDB Storage]
            Memobase --> UserInfo[User Information]
            Memobase --> StructuredData[Structured Knowledge]
        end
    end
```

## Buffer Memory

Buffer Memory provides short-term retention of recent messages and context.

### Key Features

- **Hybrid Retrieval**: Combines semantic similarity with recency
- **FAISS Integration**: Uses FAISS for efficient vector storage and retrieval
- **Context Window**: Maintains recent messages for immediate context
- **Buffer Multiplier**: Extends total storage beyond the context window

### Configuration

```python
from muxi.core.memory.buffer import BufferMemory
from muxi.core.models.providers.openai import OpenAIModel

# Create a model for generating embeddings
embedding_model = OpenAIModel(model="text-embedding-3-large")

# Create buffer memory
buffer = BufferMemory(
    max_size=10,               # Context window size
    buffer_multiplier=10,      # Total capacity = max_size * buffer_multiplier
    vector_dimension=1536,     # Embedding dimension for OpenAI embeddings
    model=embedding_model      # Embedding model
)
```

### Adding Items

```python
# Add a message to buffer memory
await buffer.add(
    "The customer preference is dark mode with blue accents.",
    metadata={
        "role": "user",
        "topic": "design",
        "importance": 0.8
    }
)

# Add another message with different metadata
await buffer.add(
    "We should use sans-serif fonts for better readability.",
    metadata={
        "role": "assistant",
        "topic": "design",
        "importance": 0.6
    }
)
```

### Searching Buffer Memory

```python
# Search with semantic capability
results = await buffer.search(
    query="What design preferences did the user have?",
    limit=5,  # Number of results to retrieve
    recency_bias=0.3  # Balance between semantic similarity and recency
)

# Search with metadata filtering
results = await buffer.search(
    query="design preferences",
    filter_metadata={"role": "user", "topic": "design"}
)

# Get most recent messages (pure recency-based retrieval)
recent_messages = buffer.get_recent(5)
```

### Hybrid Retrieval Mechanism

The Buffer Memory uses a sophisticated hybrid approach that balances semantic relevance with recency:

```python
# How hybrid scoring works (simplified implementation)
def hybrid_score(semantic_score, recency_score, recency_bias=0.3):
    # Semantic score is from vector similarity (higher is better)
    # Recency score is based on position in buffer (newer items have higher scores)

    # Combine the scores with the recency bias as a weighting factor
    return (1 - recency_bias) * semantic_score + recency_bias * recency_score
```

### Buffer Capacity Management

```python
# Initialize buffer with extended capacity
buffer = BufferMemory(
    max_size=10,           # Context window of 10 most recent messages
    buffer_multiplier=10   # Total capacity of 100 messages
)

# When buffer exceeds capacity (100 items), oldest items are removed
# while always maintaining at least the context window size (10 items)
```

### Without Embedding Model

Buffer Memory gracefully degrades to simple recency-based retrieval when no embedding model is provided:

```python
# Create buffer without semantic search capability
buffer = BufferMemory(max_size=10)

# Adds items to the buffer (works the same)
await buffer.add("This is a message")

# Searches fall back to recency-based retrieval
results = await buffer.search("query")  # Returns most recent items
```

## Long-Term Memory

Long-Term Memory provides persistent storage for important information that should be retained indefinitely.

### Key Features

- **PostgreSQL Storage**: Durable storage in PostgreSQL database
- **Vector Search**: Efficient semantic search using vector embeddings
- **Categorization**: Organize memories by category/type
- **Metadata Filtering**: Flexible filtering based on metadata
- **Importance Scoring**: Prioritize memories by importance

### Configuration

```python
from muxi.core.memory.long_term import LongTermMemory
from muxi.core.models.providers.openai import OpenAIModel

# Create embedding model
embedding_model = OpenAIModel(model="text-embedding-3-large")

# Create long-term memory
long_term_memory = LongTermMemory(
    connection_string="postgresql://user:password@localhost:5432/muxi_memory",
    model=embedding_model,
    table_name="long_term_memories",
    vector_dimension=1536
)
```

### Adding Items

```python
# Add a memory with metadata
await long_term_memory.add(
    content="The client requires SOC 2 compliance for all data storage.",
    metadata={
        "category": "requirements",
        "project": "client_portal",
        "importance": 0.9,
        "source": "client_meeting"
    }
)

# Add memory with importance score
await long_term_memory.add(
    content="API rate limits are set to 100 requests per minute.",
    metadata={
        "category": "technical",
        "service": "api",
        "importance": 0.7
    }
)
```

### Searching Long-Term Memory

```python
# Basic semantic search
results = await long_term_memory.search(
    query="What compliance requirements do we have?",
    limit=5
)

# Search with category filter
results = await long_term_memory.search(
    query="rate limits",
    filter_metadata={"category": "technical"}
)

# Search with multiple filters
results = await long_term_memory.search(
    query="client requirements",
    filter_metadata={
        "category": "requirements",
        "project": "client_portal"
    }
)

# Search with minimum importance
results = await long_term_memory.search(
    query="compliance",
    filter_metadata={"importance": {"$gte": 0.8}}
)
```

### Managing Long-Term Memory

```python
# Delete a memory by ID
await long_term_memory.delete(memory_id="mem_123456")

# Delete memories matching a filter
await long_term_memory.delete_many(
    filter_metadata={"project": "deprecated_project"}
)

# Update a memory's metadata
await long_term_memory.update(
    memory_id="mem_123456",
    metadata={"importance": 0.95, "verified": True}
)

# Get all memories in a category
technical_memories = await long_term_memory.get_by_metadata(
    metadata={"category": "technical"}
)
```

### Memory Categories

Long-Term Memory categories help organize different types of knowledge:

```python
# Example categorical storage
categories = [
    "client_requirements",   # Client requirements and preferences
    "technical_specs",       # Technical specifications and details
    "decisions",             # Key decisions made and their rationales
    "best_practices",        # Best practices and guidelines
    "project_context",       # Overall project context and information
    "external_information"   # Information from external sources
]

# Store with category
await long_term_memory.add(
    content="The authorization system must use OAuth 2.0 with PKCE.",
    metadata={"category": "technical_specs", "system": "auth"}
)

# Retrieve all items from a category
auth_specs = await long_term_memory.get_by_metadata(
    metadata={"category": "technical_specs", "system": "auth"}
)
```

## Memobase

Memobase is specialized for managing user-specific information and structured knowledge.

### Key Features

- **MongoDB Storage**: Flexible document storage with MongoDB
- **User Information**: Store and retrieve user-specific information
- **Information Extraction**: Automatically extract user information from conversations
- **Structured Knowledge**: Store structured data with nested properties
- **Semantic Search**: Search user memory with semantic understanding

### Configuration

```python
from muxi.core.memory.memobase import Memobase
from muxi.core.models.providers.openai import OpenAIModel

# Create embedding model
embedding_model = OpenAIModel(model="text-embedding-3-large")

# Create memobase
memobase = Memobase(
    mongodb_uri="mongodb://localhost:27017",
    database_name="muxi_memory",
    embedding_provider=embedding_model
)
```

### User Memory Management

```python
# Add a memory for a specific user
await memobase.add_user_memory(
    user_id="user_123",
    message="My favorite color is blue and I prefer dark mode.",
    agent_id="assistant",
    importance=0.8
)

# Search a user's memory
results = await memobase.search_user_memory(
    user_id="user_123",
    query="What are the user's preferences?",
    limit=5
)

# Add a conversation memory for a user
await memobase.add_conversation_memory(
    user_id="user_123",
    conversation_id="conv_456",
    message="I need to book a flight to New York.",
    agent_id="travel_agent",
    importance=0.7
)

# Search within a specific conversation
results = await memobase.search_conversation_memory(
    user_id="user_123",
    conversation_id="conv_456",
    query="travel plans",
    limit=3
)
```

### User Context Memory

Store structured information about users:

```python
# Add user context information
await memobase.add_user_context_memory(
    user_id="user_123",
    knowledge={
        "name": "John Doe",
        "preferences": {
            "theme": "dark",
            "language": "English",
            "notifications": "enabled"
        },
        "location": "New York",
        "timezone": "America/New_York"
    },
    source="profile_update",
    importance=0.9
)

# Get user context
user_context = await memobase.get_user_context_memory(user_id="user_123")

# Update a specific field in user context
await memobase.update_user_context_memory(
    user_id="user_123",
    path="preferences.theme",
    value="light"
)

# Add to an array in user context
await memobase.update_user_context_memory(
    user_id="user_123",
    path="favorite_cities",
    value="Paris",
    operation="add_to_set"  # Add to array if not already present
)
```

### Automatic Information Extraction

Automatically extract and store user information from conversations:

```python
# Configure orchestrator with auto extraction
from muxi.core.orchestrator import Orchestrator

# Create orchestrator with Memobase and extraction
orchestrator = Orchestrator(
    memobase=memobase,
    extraction_model=OpenAIModel(model="gpt-4o"),
    auto_extract_user_info=True
)

# Extract information from a conversation
await memobase.extract_user_information(
    user_message="I live in Seattle and prefer to be contacted by email at john@example.com.",
    agent_response="I'll remember that you're in Seattle and will use your email for contact.",
    user_id="user_123",
    agent_id="assistant"
)

# The extracted information is automatically stored in the user's context memory
# and can be retrieved later:
user_context = await memobase.get_user_context_memory(user_id="user_123")
print(f"User location: {user_context.get('location')}")
print(f"User email: {user_context.get('email')}")
```

## Orchestrator Memory Integration

The Orchestrator provides unified access to all memory systems:

```python
from muxi.core.orchestrator import Orchestrator
from muxi.core.memory.buffer import BufferMemory
from muxi.core.memory.long_term import LongTermMemory
from muxi.core.memory.memobase import Memobase
from muxi.core.models.providers.openai import OpenAIModel

# Create model for embeddings
embedding_model = OpenAIModel(model="text-embedding-3-large")

# Create memory systems
buffer_memory = BufferMemory(
    max_size=10,
    buffer_multiplier=10,
    model=embedding_model
)

long_term_memory = LongTermMemory(
    connection_string="postgresql://user:password@localhost:5432/muxi_memory",
    model=embedding_model
)

memobase = Memobase(
    mongodb_uri="mongodb://localhost:27017",
    embedding_provider=embedding_model
)

# Create orchestrator with all memory systems
orchestrator = Orchestrator(
    buffer_memory=buffer_memory,
    long_term_memory=long_term_memory,
    memobase=memobase
)
```

### Combined Memory Operations

The Orchestrator provides unified methods for memory operations:

```python
# Add to buffer memory
await orchestrator.add_to_buffer_memory(
    message="The customer prefers a minimal interface with large fonts.",
    metadata={
        "role": "user",
        "topic": "design",
        "user_id": "user_123"
    }
)

# Add to long-term memory
await orchestrator.add_to_long_term_memory(
    content="The project deadline is July 15, 2024.",
    metadata={
        "category": "project_info",
        "importance": 0.9
    }
)

# Search across memory systems
# By default, searches buffer first, then long-term if needed
results = await orchestrator.search_memory(
    query="What are the project deadlines?",
    agent_id="project_manager",
    k=5,
    use_long_term=True  # Include long-term memory in search
)

# Clear memory for an agent
orchestrator.clear_memory(agent_id="assistant")

# Clear memory for a specific user
orchestrator.clear_memory(
    agent_id="assistant",
    user_id="user_123"
)
```

### Memory in Agent Conversations

Memory automatically enhances agent conversations:

```python
# Chat with memory enhancement
response = await orchestrator.chat(
    message="What were we discussing about the design?",
    agent_id="designer",
    user_id="user_123",
    enhance_with_memory=True  # Add relevant memory to context
)

# Memory retrieval happens automatically:
# 1. Recent messages are included from buffer memory
# 2. Relevant long-term memories are retrieved based on the query
# 3. User-specific information is included from Memobase
# All this context is added to the prompt sent to the model
```

## Smart Buffer Memory

Muxi Core implements a sophisticated buffer memory system that combines recency-based retrieval with semantic search:

### Architecture

```mermaid
graph TD
    Query[User Query] --> HasModel{Has Model?}
    HasModel -->|Yes| VectorSearch[Vector Search]
    HasModel -->|No| RecencySearch[Recency Search]
    VectorSearch --> CombineScores[Combine Semantic + Recency Scores]
    CombineScores --> FilterResults[Filter by Metadata]
    RecencySearch --> FilterResults
    FilterResults --> SortResults[Sort by Score]
    SortResults --> TopK[Return Top K Results]
```

### Implementation Details

The Smart Buffer Memory includes these key components:

1. **FAISS Integration**: The buffer uses FAISS (Facebook AI Similarity Search) for efficient vector storage and retrieval:

   ```python
   # FAISS index is initialized with the embedding dimension
   self.index = faiss.IndexFlatL2(self.dimension)
   ```

2. **Hybrid Retrieval**: The search method combines semantic relevance with recency bias:

   ```python
   # Calculation of the combined score
   semantic_score = 1.0 / (1.0 + float(distances[0][i]))
   recency_score = 1.0 - (buffer_idx / len(self.buffer))
   combined_score = (1 - recency_bias) * semantic_score + recency_bias * recency_score
   ```

3. **Context Window vs. Total Buffer Size**:

   ```python
   # Initialize with separate size parameters
   buffer = BufferMemory(
       max_size=10,             # Context window size (10 most recent messages)
       buffer_multiplier=10     # Total capacity multiplier (100 total capacity)
   )
   ```

4. **Graceful Degradation**: The system falls back to recency-based retrieval when no model is available:

   ```python
   # Fallback when no vector search is possible
   if not self.has_vector_search or not self.model:
       return self._recency_search(limit, filter_metadata)
   ```

### Configuration Recommendations

1. **Size Parameters**:
   - `max_size` (context window): 5-20 messages for most applications
   - `buffer_multiplier`: 5-20× depending on memory requirements

2. **Recency Bias Tuning**:
   - Human conversations: `recency_bias=0.5` (more recency)
   - Factual queries: `recency_bias=0.2` (more semantic)
   - General use: `recency_bias=0.3` (balanced)

## Memory System Tips & Best Practices

### Memory Selection Guidelines

```
Decision Tree for Memory Storage:

1. Is this recent context needed for the current conversation?
   → Use Buffer Memory

2. Is this important information that should be retained long-term?
   → Use Long-Term Memory

3. Is this user-specific information or preferences?
   → Use Memobase (User Context Memory)

4. Is this structured knowledge about specific entities?
   → Use Memobase (Structured Knowledge)
```

### Metadata Best Practices

```python
# Consistent metadata schemas improve retrieval quality

# User message metadata
user_message_metadata = {
    "role": "user",                    # Always include role
    "user_id": "user_123",             # Always include user_id when available
    "importance": 0.7,                 # Optional importance score (0-1)
    "topic": "account_settings",       # Optional topic categorization
    "conversation_id": "conv_456",     # Optional conversation grouping
    "timestamp": 1689423658            # Optional timestamp
}

# Assistant message metadata
assistant_message_metadata = {
    "role": "assistant",
    "agent_id": "customer_support",    # Include agent_id for assistant messages
    "user_id": "user_123",             # Maintain user context
    "importance": 0.6,
    "topic": "account_settings",
    "conversation_id": "conv_456",
    "timestamp": 1689423689
}

# Long-term memory metadata
long_term_metadata = {
    "category": "policy",              # Categorize memories
    "source": "knowledge_base",        # Track information sources
    "importance": 0.9,                 # Prioritize critical information
    "timestamp": 1689423700,
    "verified": True,                  # Mark verified information
    "expiration": None                 # Optional expiration date
}
```

### Memory System Performance

Tips for optimizing memory performance:

```python
# 1. Use appropriate buffer sizes based on your use case
buffer = BufferMemory(
    max_size=5,               # Smaller for simple assistants
    buffer_multiplier=10
)

# 2. Index only the most important information in long-term memory
await long_term_memory.add(
    content="Critical system information: API keys must be rotated every 90 days.",
    metadata={"importance": 0.9, "category": "security_policy"}
)

# 3. Use specific queries for better retrieval
results = await orchestrator.search_memory(
    query="What is our policy on API key rotation?",  # Specific query
    agent_id="security_agent"
)

# 4. Use appropriate filter metadata to narrow search
results = await memobase.search_user_memory(
    user_id="user_123",
    query="email preferences",
    filter_metadata={"topic": "notifications"}  # Narrows the search
)
```

## Coming Soon Features

Muxi Core's memory systems are continuously evolving, with several exciting features on the roadmap:

- **Memory Compression**: Automatic summarization and compression of memory items
- **Memory Forgetting**: Intelligent removal of less relevant information over time
- **Cross-User Memory**: Safely share relevant information across users
- **Memory Reflection**: Periodic analysis of memory to extract insights and patterns
- **Hierarchical Memory**: Multi-tiered memory architecture with different retention periods
- **Multi-Modal Memory**: Support for storing and retrieving images and other media
- **Memory Visualization**: Tools for visualizing and exploring memory contents
- **Memory Evaluation**: Metrics for assessing memory quality and relevance
- **Federated Memory**: Distributed memory systems across multiple instances
- **Self-Organizing Memory**: Automatic organization and categorization of memories
