# Agent-Level Knowledge Base PRD

## Overview

This document outlines the addition of agent-specific domain knowledge capabilities to the MUXI Framework, providing lightweight RAG (Retrieval-Augmented Generation) capabilities at the agent level. This feature will enable agents to access specialized information sources, allowing them to provide more accurate, contextual, and helpful responses in their areas of expertise.

## Problem Statement

Currently, MUXI supports domain knowledge at the user level, which allows for personalization based on user-specific data. However, agents lack dedicated knowledge bases that align with their specialized roles and expertise. This limitation means that agents rely solely on their pre-trained knowledge, which may be outdated or insufficient for specific domains.

## Scope and Design Rationale

MUXI is designed primarily as an agent routing system where MCP servers handle specialized, computation-heavy tasks. After careful consideration, we've decided to implement a lightweight, focused approach to agent knowledge:

1. **File-based knowledge only** - To maintain simplicity and minimize dependencies, we'll only support text-based file sources (markdown, txt, docx, pdf).
2. **In-memory vector store** - We'll leverage FAISS (already a dependency) for efficient in-memory vector storage, avoiding the need for additional database dependencies.
3. **Embedding persistence** - To optimize costs, embeddings will be persisted locally using pickle files, regenerated only when files change.
4. **Clear separation of concerns** - For complex RAG needs with large knowledge bases (thousands of files or gigabytes of text), users should implement dedicated MCP servers rather than overloading MUXI's core functionality.
5. **No additional embedding dependencies** - We'll use each agent's configured model for generating embeddings, avoiding the need for additional embedding-specific dependencies or services.

This focused approach aligns with MUXI's philosophy of maintaining clean, simple APIs while providing essential functionality.

## Goals

1. Enable agents to have specialized knowledge bases in their domains of expertise
2. Maintain MUXI's elegant design philosophy and clean API
3. Support common document formats (markdown, txt, docx, pdf)
4. Provide flexible configuration through both declarative and programmatic approaches
5. Implement automatic, context-aware knowledge retrieval
6. Allow fine-grained control over knowledge usage during queries
7. Minimize embedding API costs through persistent storage
8. Use the agent's existing model provider for embeddings to avoid new dependencies

## Non-Goals

1. Replacing or modifying the existing user-level domain knowledge system
2. Creating a full-featured RAG system (this should be handled by dedicated MCP servers)
3. Supporting database or API knowledge sources
4. Handling extremely large knowledge bases (thousands of files or gigabytes of text)
5. Implementing complex knowledge graph capabilities
6. Adding new embedding-specific dependencies

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
  - path: "./knowledge/investment_basics.md"
    description: "Basic investment concepts and terminology"
  - path: "./knowledge/portfolio_strategies.pdf"
    description: "Portfolio construction strategies"
  - path: "./knowledge/retirement_planning.docx"
    description: "Retirement planning guidelines"
```

### Knowledge Source Types

**File Knowledge**

- Documents in various formats (markdown, txt, docx, pdf)
- Chunked and indexed for retrieval
- Local files only for simplicity and security

### Programmatic API

```python
import os
from muxi.core.agent import Agent
from muxi.core.knowledge import FileKnowledge
from muxi.core.models.openai import OpenAIModel

# Create knowledge sources
investment_basics = FileKnowledge(
    path="./knowledge/investment_basics.md",
    description="Basic investment concepts and terminology"
)

portfolio_strategies = FileKnowledge(
    path="./knowledge/portfolio_strategies.pdf",
    description: "Portfolio construction strategies"
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
    knowledge=[investment_basics, portfolio_strategies]
)
```

### Knowledge Management

Functions for managing agent knowledge:

```python
# Add knowledge to an existing agent
app.add_agent_knowledge("financial_advisor", new_knowledge_file)

# List knowledge sources
knowledge_sources = app.list_agent_knowledge("financial_advisor")

# Remove knowledge
app.remove_agent_knowledge("financial_advisor", "portfolio_strategies.pdf")
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
        "relevance_threshold": 0.85
    }
)
```

## Technical Implementation

### Embedding Generation Strategy

Every model provider in MUXI will implement an embedding generation method:

```python
# Add to model base class
class BaseModel:
    # ... existing code ...

    def generate_embeddings(self, texts):
        """Generate embeddings using this model"""
        raise NotImplementedError("This model does not support embeddings")

# OpenAI implementation
class OpenAIModel(BaseModel):
    # ... existing code ...

    def generate_embeddings(self, texts):
        # Use the OpenAI embeddings endpoint
        return self.client.embeddings.create(
            input=texts,
            model="text-embedding-3-small"
        ).data

# Anthropic implementation
class AnthropicModel(BaseModel):
    # ... existing code ...

    def generate_embeddings(self, texts):
        # Use Anthropic's embedding endpoint
        return self.client.embeddings.create(
            input=texts,
            model="claude-3-embedding"
        ).data
```

This approach uses each agent's already configured model for both chat and embeddings, avoiding the need for additional embedding-specific dependencies or services. It provides consistency and simplicity in the architecture.

### Knowledge Base Implementation

```python
class AgentKnowledge:
    def __init__(self, agent, cache_dir=".cache/knowledge_embeddings"):
        self.agent = agent
        self.cache_dir = cache_dir
        self.embedding_file = f"{cache_dir}/{agent.agent_id}_embeddings.pickle"
        self.metadata_file = f"{cache_dir}/{agent.agent_id}_metadata.pickle"

        # Create cache directory if it doesn't exist
        os.makedirs(cache_dir, exist_ok=True)

        # Try to load cached embeddings
        if self._load_cached_embeddings():
            print(f"Loaded cached embeddings for agent {agent.agent_id}")
        else:
            # Initialize fresh index
            self.index = faiss.IndexFlatL2(1536)  # Standard dimension for most embedding models
            self.documents = []

    def _load_cached_embeddings(self):
        """Load cached embeddings if they exist and are valid"""
        try:
            if os.path.exists(self.embedding_file) and os.path.exists(self.metadata_file):
                with open(self.embedding_file, 'rb') as f:
                    self.index = pickle.load(f)

                with open(self.metadata_file, 'rb') as f:
                    self.documents = pickle.load(f)

                # Validate that index and documents are consistent
                if self.index.ntotal == len(self.documents):
                    return True
            return False
        except Exception as e:
            print(f"Error loading cached embeddings: {e}")
            return False

    def _save_embeddings(self):
        """Save embeddings and metadata to disk"""
        with open(self.embedding_file, 'wb') as f:
            pickle.dump(self.index, f)

        with open(self.metadata_file, 'wb') as f:
            pickle.dump(self.documents, f)

    def add_file(self, file_path, description=None):
        # Get file modification time
        file_mtime = os.path.getmtime(file_path)

        # Check if we already have this file with the same modification time
        for doc in self.documents:
            if doc.get("source") == file_path and doc.get("mtime") == file_mtime:
                # File already processed and hasn't changed
                return 0

        # Load and chunk the file based on type (md, txt, pdf, docx)
        chunks = self._load_and_chunk_file(file_path)

        # Generate embeddings using the agent's model
        embeddings = self._generate_embeddings(chunks)

        # Add to FAISS index
        self.index.add(embeddings)

        # Add modification time to metadata
        for i, chunk in enumerate(chunks):
            self.documents.append({
                "content": chunk,
                "source": file_path,
                "description": description,
                "mtime": file_mtime
            })

        # Save updated embeddings
        self._save_embeddings()

        return len(chunks)

    def _generate_embeddings(self, chunks):
        """Generate embeddings using the agent's model"""
        return self.agent.model.generate_embeddings(chunks)

    def search(self, query, top_k=5):
        # Generate query embedding using the agent's model
        query_embedding = self.agent.model.generate_embeddings([query])[0]

        # Search FAISS index
        distances, indices = self.index.search(query_embedding, top_k)

        # Return relevant documents
        results = []
        for i, idx in enumerate(indices[0]):
            if idx < len(self.documents) and idx >= 0:
                doc = self.documents[idx]
                results.append({
                    "content": doc["content"],
                    "source": doc["source"],
                    "description": doc["description"],
                    "relevance": float(1.0 - distances[0][i])
                })

        return results
```

### Prompt Construction

Knowledge retrieval will be integrated into the prompt construction process:

1. When a user message is received, a retrieval query is formulated
2. Relevant knowledge is fetched from the agent's knowledge sources using the agent's model for embedding generation
3. The retrieved information is incorporated into the context window
4. The enhanced context is sent to the LLM for response generation

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
  - path: "./knowledge/medical_guidelines.md"
    description: "Medical guidelines and procedures"
  - path: "./knowledge/drug_information.pdf"
    description: "Pharmaceutical information and dosages"
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
5. **Embedding Quality**: Compare embedding quality across different model providers

## Implementation Plan

### Phase 1: Core Implementation

1. Extend model base class with embedding generation methods
2. Implement embedding generation for each provider (OpenAI, Anthropic, etc.)
3. Create knowledge base class for file handling
4. Implement embedding persistence using pickle files
5. Implement knowledge configuration in agent schema
6. Modify prompt construction to include knowledge retrieval

### Phase 2: Knowledge Management

1. Implement knowledge management APIs
2. Add knowledge source validation and error handling
3. Add file modification detection to avoid unnecessary re-embedding

### Phase 3: Advanced Features

1. Add query-time knowledge controls
2. Improve chunking strategies for different document types
3. Add basic analytics for knowledge usage
4. Add fallback options when a model provider doesn't support embeddings

## Conclusion

Adding agent-level knowledge bases to MUXI will significantly enhance the capabilities of specialized agents, allowing them to provide more accurate, contextual, and domain-specific responses. By focusing specifically on file-based knowledge, leveraging FAISS for in-memory vector storage, and using the agent's existing model for embedding generation, we maintain MUXI's design philosophy while expanding its potential use cases in specialized domains.

This lightweight approach ensures that MUXI remains focused on its core strength as an agent routing system, while still providing essential knowledge capabilities for agents without introducing additional dependencies.
