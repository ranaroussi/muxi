# Agent-Level Knowledge Base PRD

## Overview

This document outlines the addition of agent-specific domain knowledge capabilities to the MUXI Framework, providing RAG (Retrieval-Augmented Generation) capabilities at the agent level. This feature will enable agents to access specialized information sources, allowing them to provide more accurate, contextual, and helpful responses in their areas of expertise.

## Problem Statement

Currently, MUXI supports domain knowledge at the user level, which allows for personalization based on user-specific data. However, agents lack dedicated knowledge bases that align with their specialized roles and expertise. This limitation means that agents rely solely on their pre-trained knowledge, which may be outdated or insufficient for specific domains.

## Goals

1. Enable agents to have specialized knowledge bases in their domains of expertise
2. Maintain MUXI's elegant design philosophy and clean API
3. Support multiple knowledge source types (files, databases, vector stores)
4. Provide flexible configuration through both declarative and programmatic approaches
5. Implement automatic, context-aware knowledge retrieval
6. Allow fine-grained control over knowledge usage during queries

## Non-Goals

1. Replacing or modifying the existing user-level domain knowledge system
2. Creating a general-purpose document management system
3. Implementing complex knowledge graph capabilities (future enhancement)

## Feature Specification

### Agent Knowledge Configuration

Extend agent configuration to include a `knowledge` property that defines knowledge sources:

```yaml
agent_id: financial_advisor
description: "Financial advisor with expertise in investment strategies"
model:
  provider: openai
  api_key: "${OPENAI_API_KEY}"
  model: gpt-4o
system_message: "You are a helpful financial advisor."
knowledge:
  - source: "file"
    path: "./knowledge/investment_basics.md"
    description: "Basic investment concepts and terminology"
  - source: "database"
    connection: "${DATABASE_URL}"
    collection: "financial_regulations"
    description: "Current financial regulations and compliance info"
  - source: "vector_store"
    path: "./embeddings/market_data"
    embedding_model: "text-embedding-3-small"
    description: "Historical market data and trends"
```

### Knowledge Source Types

1. **File Knowledge**
   - Documents in various formats (MD, PDF, TXT)
   - Chunked and indexed for retrieval
   - Supports local and remote (S3, etc.) files

2. **Database Knowledge**
   - Structured data from SQL or NoSQL databases
   - Vector-enabled databases (PostgreSQL with pgvector)
   - Configurable queries and filters

3. **Vector Store Knowledge**
   - Pre-embedded knowledge bases
   - Support for different embedding models
   - Optimized for semantic similarity search

4. **API Knowledge**
   - Dynamic knowledge from external APIs
   - Configurable authentication and endpoints
   - Response mapping and transformation

### Programmatic API

```python
from muxi.core.agent import Agent
from muxi.core.knowledge import FileKnowledge, DatabaseKnowledge, VectorStoreKnowledge

# Create knowledge sources
investment_basics = FileKnowledge(
    path="./knowledge/investment_basics.md",
    description="Basic investment concepts and terminology"
)

financial_regulations = DatabaseKnowledge(
    connection=os.getenv("DATABASE_URL"),
    collection="financial_regulations",
    description="Current financial regulations and compliance info"
)

market_data = VectorStoreKnowledge(
    path="./embeddings/market_data",
    embedding_model="text-embedding-3-small",
    description="Historical market data and trends"
)

# Create agent with knowledge
agent = Agent(
    agent_id="financial_advisor",
    description="Financial advisor with expertise in investment strategies",
    model=OpenAIModel(
        api_key=os.getenv("OPENAI_API_KEY"),
        model="gpt-4o"
    ),
    system_message="You are a helpful financial advisor.",
    knowledge=[investment_basics, financial_regulations, market_data]
)
```

### Knowledge Management

Functions for managing agent knowledge:

```python
# Add knowledge to an existing agent
app.add_agent_knowledge("financial_advisor", new_knowledge_source)

# Update knowledge
app.update_agent_knowledge("financial_advisor", "financial_regulations", new_connection_string)

# List knowledge sources
knowledge_sources = app.list_agent_knowledge("financial_advisor")

# Remove knowledge
app.remove_agent_knowledge("financial_advisor", "market_data")
```

### Query-Time Controls

Provide parameters to control knowledge retrieval during chat:

```python
# Control search parameters in a chat request
response = app.chat(
    "financial_advisor",
    "What investment strategy would you recommend for retirement?",
    knowledge_options={
        "max_results": 5,
        "relevance_threshold": 0.85,
        "sources": ["investment_basics", "financial_regulations"]  # Only use these sources
    }
)
```

## Technical Implementation

### Knowledge Base Class Hierarchy

```
KnowledgeBase (abstract base class)
├── FileKnowledge
│   ├── MDFileKnowledge
│   ├── PDFFileKnowledge
│   └── CustomFileKnowledge
├── DatabaseKnowledge
│   ├── SQLKnowledge
│   ├── NoSQLKnowledge
│   └── CustomDBKnowledge
├── VectorStoreKnowledge
│   ├── FAISSKnowledge
│   ├── ChromaDBKnowledge
│   └── CustomVectorKnowledge
└── APIKnowledge
    ├── RESTAPIKnowledge
    ├── GraphQLKnowledge
    └── CustomAPIKnowledge
```

### Prompt Construction

Knowledge retrieval will be integrated into the prompt construction process:

1. When a user message is received, a retrieval query is formulated
2. Relevant knowledge is fetched from the agent's knowledge sources
3. The retrieved information is incorporated into the context window
4. The enhanced context is sent to the LLM for response generation

### Caching Strategy

To optimize performance:

1. Implement a tiered caching system for knowledge retrieval
2. Cache search results for similar queries
3. Use LRU (Least Recently Used) cache eviction policy
4. Provide configuration options for cache size and TTL

## User Experience

### Declarative Configuration

Users will be able to define agent knowledge through YAML/JSON:

```yaml
# configs/expert_agent.yaml
agent_id: medical_expert
description: "Medical assistant with specialized healthcare knowledge"
model:
  provider: openai
  api_key: "${OPENAI_API_KEY}"
  model: gpt-4o
knowledge:
  - source: "file"
    path: "./knowledge/medical_guidelines.md"
  - source: "vector_store"
    path: "./embeddings/drug_information"
    embedding_model: "text-embedding-3-small"
```

### Using Knowledge-Enhanced Agents

```python
from muxi import muxi
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize MUXI
app = muxi()

# Add agent from configuration
app.add_agent_from_file("configs/expert_agent.yaml")

# Chat with the agent - knowledge retrieval happens automatically
response = app.chat("medical_expert", "What are the side effects of ibuprofen?")
print(response)
```

## Metrics and Evaluation

To measure the effectiveness of agent knowledge:

1. **Relevance Score**: Measure the relevance of retrieved knowledge
2. **Factual Accuracy**: Compare agent responses with knowledge sources
3. **Response Time**: Monitor impact on response generation time
4. **Knowledge Usage**: Track which knowledge sources are most utilized

## Implementation Plan

### Phase 1: Core Implementation

1. Create knowledge base abstract class and basic implementations
2. Implement knowledge configuration in agent schema
3. Modify prompt construction to include knowledge retrieval

### Phase 2: Knowledge Management

1. Implement knowledge management APIs
2. Add knowledge source validation and error handling
3. Create knowledge indexing and updating mechanisms

### Phase 3: Advanced Features

1. Add query-time knowledge controls
2. Implement caching system
3. Create knowledge source analytics

## Conclusion

Adding agent-level knowledge bases to MUXI will significantly enhance the capabilities of specialized agents, allowing them to provide more accurate, contextual, and domain-specific responses. This feature maintains MUXI's design philosophy while expanding its potential use cases in specialized domains.
