# MUXI Framework Technical Context

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

# Database Configuration
POSTGRES_DATABASE_URL=postgresql://user:password@localhost:5432/muxi
# Or use SQLite
USE_LONG_TERM_MEMORY=sqlite:///path/to/memory.db

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
     USE_LONG_TERM_MEMORY=sqlite:///path/to/memory.db
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
   - Agent memory requires state persistence
   - Consider distributed memory architecture for horizontal scaling
   - SQLite suitable for single-instance deployments
   - PostgreSQL recommended for multi-instance deployments

2. **External Rate Limits**:
   - LLM APIs impose rate limits
   - Implement rate limiting and queuing strategies
   - Consider implementing model fallbacks

3. **Database Scaling**:
   - Long-term memory requires database scaling strategies
   - Plan for sharding or read replicas as needed
   - SQLite is limited to single-node scaling

### Compatibility Requirements

1. **Python Version**: 3.10+ required (uses modern async features)
2. **PostgreSQL**: 13+ with pgvector extension
3. **SQLite**: 3.38+ with sqlite-vec
4. **Browser Support**: Modern browsers with WebSocket and SSE support
5. **Operating Systems**: Cross-platform (Linux, macOS, Windows)

## Dependencies

### Core Dependencies

```
fastapi>=0.101.0
uvicorn>=0.23.2
pydantic>=2.3.0
SQLAlchemy>=2.0.20
asyncpg>=0.28.0
pgvector>=0.2.1
sqlite-vec>=0.1.7
faiss-cpu>=1.7.4
httpx>=0.24.1
websockets>=11.0.3
rich>=13.5.2
python-dotenv>=1.0.0
pyyaml>=6.0.1
jinja2>=3.1.2
typer>=0.9.0
mcp-python-sdk>=0.1.0
openai>=1.3.0
tiktoken>=0.5.1
```

### Development Dependencies

```
pytest>=7.4.0
pytest-asyncio>=0.21.1
pytest-cov>=4.1.0
black>=23.7.0
flake8>=6.1.0
mypy>=1.5.1
pre-commit>=3.3.3
alembic>=1.11.3
sphinx>=7.1.2
sphinx-rtd-theme>=1.3.0
```

### Optional Dependencies

```
anthropic>=0.5.0    # For Anthropic LLM provider
google-generativeai>=0.2.0  # For Gemini LLM provider
pillow>=10.0.0     # For image processing
pytest-xdist>=3.3.1  # For parallel testing
```

## API Dependencies

The framework's REST API is defined according to the OpenAPI standard with the following endpoints:

- `/agents`: Agent management
- `/agents/{agent_id}/chat`: Agent chat
- `/agents/{agent_id}/memory`: Memory operations
- `/chat`: Orchestrator chat routing
- `/users/{user_id}/context_memory`: Context memory operations
- `/system/status`: System information

See `api.md` for the complete API specification.

## Deployment Considerations

### Server Requirements

- 2+ CPU cores
- 4+ GB RAM (8+ GB recommended for multiple agents)
- Fast SSD storage for database
- Good network connectivity for LLM API calls

### Container Deployment

Dockerization is supported with:
- Python base image
- PostgreSQL with pgvector as a separate service or SQLite with sqlite-vec for simpler deployments
- Volume mounts for configuration and persistent data

### Cloud Considerations

- Consider managed PostgreSQL services with vector support
- Implement proper API key rotation and management
- Use load balancers for high-availability deployments
- Consider serverless options for cost efficiency
- Use SQLite with sqlite-vec for serverless functions with size/memory constraints

## Future Technology Considerations

1. **Local LLM Support**: Integration with local LLM frameworks
2. **Multi-Modal Expansion**: Support for image, audio, and video processing
3. **Distributed Architecture**: Support for distributed agent deployments
4. **GPU Acceleration**: Support for GPU-accelerated vector operations
5. **Streaming HTTP Transport**: Support for upcoming MCP streaming HTTP transport
