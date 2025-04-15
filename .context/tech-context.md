# MUXI Framework Technical Context

This document outlines the technical context of the MUXI Framework, including technologies used, development setup, constraints, and dependencies.

## Technologies Used

### Programming Languages

- **Python**: Primary development language (3.10+)
- **JavaScript**: Used for web UI components

### Core Libraries & Frameworks

- **FastAPI**: Web framework for API development
- **asyncio**: Asynchronous I/O library for Python
- **SQLAlchemy**: ORM for database interactions
- **FAISS**: Vector similarity search for buffer memory
- **pgvector**: PostgreSQL extension for vector operations
- **sqlite-vec**: SQLite extension for vector similarity search
- **pydantic**: Data validation and settings management
- **websockets**: WebSocket protocol implementation
- **httpx**: HTTP client for Python with async support
- **rich**: Terminal formatting and UI

### LLM Integration

- **OpenAI API**: Primary LLM provider
- (Planned) Anthropic, Gemini, Grok, and local model integrations

### MCP Integration

- **Model Context Protocol (MCP)**: Standard for tool integration
- **MCP Python SDK**: Official Python SDK for MCP

### Database

- **PostgreSQL**: Primary database for long-term memory
- **pgvector**: PostgreSQL extension for vector operations
- **SQLite**: Alternative database for long-term memory in local deployments
- **sqlite-vec**: SQLite extension for vector similarity search

### Web Technologies

- **Server-Sent Events (SSE)**: For streaming responses
- **WebSockets**: For bidirectional communication
- **HTML/CSS/JavaScript**: For web UI

### Developer Tools

- **pytest**: Testing framework
- **black**: Code formatting
- **flake8**: Linting
- **mypy**: Type checking
- **alembic**: Database migrations
- **sphinx**: Documentation generation

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
