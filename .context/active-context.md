# MUXI Framework Active Context

## Current Work Focus

The current development focus is on implementing the complete REST API as defined in the `.context/scratchpad/api.md` specification file. This involves standardizing all API endpoints, implementing authentication, error handling, and ensuring proper documentation. This work is considered high priority as it forms the foundation for client applications to interact with the MUXI Framework.

### Primary Areas of Focus

1. **API Implementation**: Implementing the full set of REST endpoints defined in the API specification
2. **Authentication System**: Implementing a robust API key authentication system
3. **Error Handling**: Standardizing error responses across all endpoints
4. **Streaming Support**: Enhancing SSE streaming for chat responses
5. **Documentation**: Creating comprehensive API documentation with Swagger/OpenAPI
6. **SQLite Vector Integration**: Enhancing local deployment capabilities with sqlite-vec extension

## Recent Changes

### Major Changes

1. **SQLite Vector Integration**:
   - Added support for sqlite-vec Python package for vector similarity search
   - Reorganized extensions directory structure for future expandability
   - Updated memory system to work with both PostgreSQL and SQLite databases
   - Improved vector serialization for compatibility with sqlite-vec
   - Enhanced resilience with fallback to binary extensions when package is unavailable

2. **Breaking Changes in Version 1.0**:
   - Removed deprecated methods like `_enhance_with_domain_knowledge()` (replaced by `_enhance_with_context_memory()`)
   - Removed `add_user_domain_knowledge()` (replaced by `add_user_context_memory()`)
   - Updated API signatures by removing the `memory` parameter from the `Agent` class (replaced by `buffer_memory`)
   - Removed backward compatibility for user_id=0 handling
   - Renamed all "domain knowledge" terminology to "context memory" throughout the codebase

3. **Test Improvements**:
   - Fixed all test warnings and errors
   - Implemented pytest.ini configuration to filter FAISS-related DeprecationWarnings
   - Improved test coverage across all components
   - Made tests more robust to handle differences in database behaviors

4. **Architectural Evolution**:
   - Restructured codebase into modular packages
   - Created setup.py for each package with appropriate dependencies
   - Implemented proper monorepo structure
   - Created development installation scripts
   - Fixed cross-package imports

5. **MCP Integration**:
   - Enhanced MCP server integration with proper reconnection logic
   - Implemented transport abstraction with factory pattern
   - Added support for both HTTP+SSE and Command-line transports
   - Integrated with the official MCP Python SDK
   - Made credentials optional for MCP servers that don't require them

### Recent Pull Requests and Commits

- Fixed coroutine warnings in test files by properly handling async methods
- Updated `ClientSession` implementation to use streams appropriately
- Addressed linter issues and code formatting across the codebase
- Improved API key handling for tests with standardized environment loading
- Added sqlite-vec Python package to simplify SQLite extension loading

## Next Steps

Based on the updated NEXT_STEPS.md document, the following tasks have been prioritized:

### Immediate Tasks (In Progress)

1. **REST API Implementation**:
   - Implement agent management endpoints (GET/POST/PATCH/DELETE /agents)
   - Implement conversation management endpoints (POST /agents/{agent_id}/chat)
   - Implement memory operations endpoints (GET/DELETE /agents/{agent_id}/memory)
   - Implement context memory CRUD operations
   - Implement MCP server management endpoints
   - Implement knowledge management endpoints
   - Implement system information endpoints

2. **Authentication**:
   - Add API key generation mechanism
   - Implement bearer token authentication
   - Add support for IP-based restrictions

3. **API Enhancement**:
   - Add streaming support for chat endpoints with SSE
   - Implement proper error handling with standardized format
   - Add API versioning support
   - Implement rate limiting and throttling
   - Create API documentation using OpenAPI/Swagger

### Upcoming Tasks

1. **WebSocket API Enhancement**:
   - Implement WebSocket protocol as defined in api.md
   - Add support for multi-modal messages (text, images, audio)
   - Implement proper error handling and recovery
   - Add reconnection logic with exponential backoff
   - Support for attachments as specified in api.md

2. **User Interface Improvements**:
   - Enhance CLI interface with support for all API operations
   - Develop web interface with responsive design
   - Implement real-time updates using WebSocket
   - Add support for multi-modal interactions

3. **LLM Provider Expansion**:
   - Implement Anthropic LLM provider
   - Implement Gemini LLM provider
   - Implement Grok LLM provider
   - Add support for local models (e.g., Llama, Mistral, DeepSeek)
   - Create a model router for fallback and cost optimization

4. **Vector Database Improvements**:
   - Enhance SQLite vector integration for improved performance
   - Add support for additional vector databases (e.g., Milvus, Qdrant)
   - Implement more vector functions and operations
   - Create database migration tools for SQLite to PostgreSQL transitions

## Active Decisions and Considerations

### API Design Decisions

1. **REST vs. GraphQL**: Decision made to use REST API as the primary interface due to its simplicity and widespread adoption. GraphQL may be considered for future versions based on user feedback.

2. **Authentication Approach**: Bearer token authentication using API keys was chosen for simplicity and security. Consider adding OAuth support in the future for more complex authentication scenarios.

3. **API Versioning**: Decision to implement API versioning from the start via URL path (e.g., /api/v1/) to ensure future compatibility as the API evolves.

4. **Error Handling**: Standardized error format as defined in api.md will be used consistently across all endpoints, with specific error codes and descriptive messages.

5. **Streaming Implementation**: Server-Sent Events (SSE) was chosen for streaming responses over WebSockets for this specific use case due to its simplicity and unidirectional nature, which is well-suited for streaming LLM outputs.

### Technical Considerations

1. **Database Structure**:
   - PostgreSQL with pgvector is confirmed as the primary database for high-scale deployments
   - SQLite with sqlite-vec now supported for local and lightweight deployments
   - Both use the same vector operations and interfaces

2. **Concurrency Model**: The async/await pattern with asyncio is used throughout the codebase. Be mindful of potential race conditions in shared state when implementing new features.

3. **MCP Integration Strategy**: The framework will continue to use the Model Context Protocol for tool integration, with support for both HTTP+SSE and Command-line transports.

4. **Package Structure**: The modular package structure (core, server, cli, web, muxi) will be maintained for better separation of concerns.

5. **Documentation Approach**: API documentation will be generated using OpenAPI/Swagger, with additional developer documentation in Markdown format using Sphinx for generation.

### Open Questions

1. **Multi-Modal Support Scope**: What level of multi-modal support should be prioritized first? Images, audio, or documents?

2. **Scalability Strategy**: What specific strategies should be implemented for horizontal scaling of the framework?

3. **Local LLM Integration**: Which local LLM frameworks should be prioritized for integration?

4. **Security Assessment**: What security assessment procedures should be established before the 1.0 release?

5. **Deployment Strategy**: What containerization and orchestration approaches should be recommended for production deployments?

6. **Vector Database Choice**: Should we provide more guidance on choosing between SQLite and PostgreSQL for different use cases?

## Blockers and Dependencies

1. **MCP Protocol Evolution**: The framework depends on the Model Context Protocol, which is still evolving. Need to stay aligned with protocol changes.

2. **API Specification Finalization**: The API specification in api.md needs to be finalized before full implementation can proceed.

3. **Multi-Modal LLM Support**: Multi-modal capabilities depend on the features available in the underlying LLM providers.

4. **Testing Infrastructure**: Need to ensure comprehensive testing infrastructure is in place for the new API endpoints.

5. **Documentation Tools**: Need to set up OpenAPI/Swagger tools for API documentation generation.
