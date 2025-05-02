# MUXI Framework Technical Context

This document outlines the technical context of the MUXI Framework, including technologies used, development setup, constraints, and dependencies.

## Core Technologies

The MUXI Framework is built using the following core technologies:

### Programming Languages

- **Python**: Primary language for MUXI Core and implementation of most framework features
- **TypeScript/JavaScript**: Used for MUXI Web UI and potentially some components of MUXI API
- **React**: Front-end library for MUXI Web UI

### Key Libraries and Frameworks

- **FastAPI**: Web framework for building MUXI API endpoints
- **FastAPI_MCP**: Extension for Model Context Protocol support
- **SQLAlchemy**: ORM for database interactions
- **Pydantic**: Data validation and settings management
- **Click/Typer**: CLI framework for MUXI CLI
- **HTTPX**: HTTP client for asynchronous requests
- **LangChain**: Building blocks for LLM applications
- **WebRTC**: For real-time media communication

### Databases & Storage

- **PostgreSQL**: Primary relational database
- **Vector Databases**:
  - Qdrant (Default)
  - Pinecone
  - ChromaDB
  - FAISS

### Deployment & Infrastructure

- **Docker**: Containerization of components
- **Docker Compose**: Local development and simple deployments
- **Kubernetes**: Production deployments and scaling (optional)

## System Components

The MUXI Framework is structured around several key components:

### MUXI Core

Core orchestration and agent management system:

- **Orchestrator**: Central component managing agents and memory
- **Agent System**: Implementation of agent capabilities
- **Memory Management**: Short-term and long-term memory systems
- **Knowledge Integration**: Domain knowledge integration
- **Tool Execution**: Handling tool connections and requests

### MUXI API

Communication interface providing multiple protocols:

- **REST API**: HTTP endpoints for standard request/response
- **SSE Endpoints**: Server-Sent Events for streaming
- **MCP Integration**: Model Context Protocol implementation
- **WebRTC Signaling**: Real-time media capabilities

### MUXI CLI

Command-line interface for MUXI interaction:

- **Command Structure**: Hierarchical commands
- **Profile System**: Configuration profiles
- **Output Formatting**: Multiple output formats (text, JSON, YAML)
- **Interactive Mode**: REPL-like environment for chat

### MUXI Web UI

Browser-based interface:

- **React Frontend**: SPA for managing MUXI
- **Chat Interface**: Real-time interaction with agents
- **Configuration UI**: Visual configuration
- **Analytics Dashboard**: Usage statistics

## Development Approach

### Repository Structure

The monorepo contains multiple packages:

- `packages/core`: MUXI Core implementation
- `packages/server`: MUXI API implementation
- `packages/cli`: MUXI CLI implementation
- `packages/web`: MUXI Web UI implementation
- `packages/muxi`: Meta-package that installs everything

### API Design

- RESTful endpoints with proper HTTP methods
- OpenAPI/Swagger documentation
- MCP (Model Context Protocol) compatibility
- SSE for streaming responses
- WebRTC for media exchange

### Testing Strategy

- Unit tests for core functionality
- Integration tests for component interaction
- End-to-end tests for user workflows
- Performance testing for scalability validation

### Deployment Options

- Single-machine deployment (all components)
- Network-distributed deployment (components on different servers)
- Cross-network deployment (components across different networks)

## Development Setup

### Environment Requirements

- Python 3.10+ installed
- PostgreSQL 13+ with pgvector extension or SQLite with vector support
- Node.js 18+ (for web UI development)

### Installation Process

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/muxi-framework.git
   cd muxi-framework
   ```

2. Run the development installation script:
   ```bash
   ./install_dev.sh
   ```

   This script:
   - Creates a virtual environment
   - Installs dependencies
   - Sets up development mode installation for all packages
   - Configures pre-commit hooks

3. Configure environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

### Key Environment Variables

```
# LLM API Keys
OPENAI_API_KEY=your_openai_key_here

# Memory Configuration (Orchestrator Level)
# Buffer memory size (integer)
BUFFER_MEMORY_SIZE=50

# Long-term memory options:
# For PostgreSQL (production/multi-user deployments)
LONG_TERM_MEMORY=postgresql://user:password@localhost:5432/muxi
# Or for SQLite (local/single-user deployments)
LONG_TERM_MEMORY=sqlite:///path/to/memory.db
# Or just enable with default SQLite in app's root directory
LONG_TERM_MEMORY=true

# MCP Configurations
MCP_WEATHER_API_KEY=your_weather_api_key
MCP_SEARCH_API_KEY=your_search_api_key

# Routing Configuration
ROUTING_LLM=openai
ROUTING_LLM_MODEL=gpt-4o-mini
ROUTING_LLM_TEMPERATURE=0.0

# Server Configuration
API_HOST=0.0.0.0
API_PORT=5050
API_KEY=your_api_key_here
```

### Database Setup

1. For PostgreSQL:
   - Install PostgreSQL and pgvector extension
   - Create a database:
     ```sql
     CREATE DATABASE muxi;
     ```
   - Run migrations:
     ```bash
     python -m alembic upgrade head
     ```

2. For SQLite:
   - Ensure sqlite-vec is installed:
     ```bash
     pip install sqlite-vec
     ```
   - Set appropriate environment variables to use SQLite:
     ```
     LONG_TERM_MEMORY=sqlite:///path/to/memory.db
     ```

### Running Tests

```bash
# Run all tests
python -m pytest

# Run specific test file
python -m pytest tests/test_agent.py

# Run with coverage
python -m pytest --cov=muxi
```

## Technical Constraints

### Performance Considerations

1. **Memory Usage**:
   - Vector embeddings can consume significant memory
   - Buffer memory size should be limited based on available resources
   - Consider using disk-based FAISS indexes for large vector collections

2. **Database Performance**:
   - Long-term memory operations can be I/O bound
   - Use connection pooling for database access
   - Consider read replicas for high-traffic deployments
   - SQLite with sqlite-vec has lower resource usage, suitable for local deployments
   - PostgreSQL with pgvector offers better scaling for large deployments

3. **LLM API Latency**:
   - External LLM API calls introduce latency
   - Implement request caching where appropriate
   - Consider response streaming to improve perceived performance

4. **Concurrency**:
   - Async I/O is used throughout for concurrent request handling
   - Be mindful of potential race conditions in shared state
   - Monitor event loop blocking operations
   - SQLite has concurrency limitations due to file locking

### Scalability Constraints

1. **Stateful Components**:
   - Orchestrator manages memory centrally for all agents
   - Memory is shared between agents through the orchestrator
   - SQLite is suitable for single-instance deployments
   - PostgreSQL with Memobase is recommended for multi-user and multi-instance deployments

2. **External Rate Limits**:
   - LLM APIs impose rate limits
   - Implement rate limiting and queuing strategies
   - Consider implementing model fallbacks

3. **Database Scaling**:
   - Long-term memory requires database scaling strategies
   - Plan for sharding or read replicas as needed

## Memory Architecture

The MUXI Framework uses an orchestrator-level memory architecture, where:

1. **Memory Management**: All memory systems (buffer and long-term) are initialized and managed at the orchestrator level, not at the agent level.

2. **Memory Types**:
   - **Buffer Memory**: Short-term memory for recent conversations, implemented with FAISS.
   - **Long-Term Memory**: Persistent storage with vector database support (PostgreSQL or SQLite).
   - **Memobase**: User-specific memory management for multi-user applications.

3. **Database Options**:
   - **PostgreSQL with pgvector**: Recommended for production and multi-user deployments.
   - **SQLite with sqlite-vec**: Ideal for local development and single-user deployments.

4. **Configuration**:
   - Memory is configured during initialization: `app = muxi(buffer_memory=50, long_term_memory="connection_string")`
   - Configuration files define agents in an array, with memory configured at the orchestrator level

5. **Multi-User Support**:
   - Multi-user capabilities through Memobase: `memobase = Memobase(long_term_memory=long_term)`
   - Each user has isolated memory space identified by user_id

## Dependencies

### Core Dependencies

```
