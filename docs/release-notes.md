---
layout: default
title: Release Notes
nav_order: 10
permalink: /release-notes
---

# MUXI Framework Release Notes

This document provides a summary of changes, new features, and fixes in each release of the MUXI Framework.

## Upcoming Releases

### v0.5.0 (Planned Q2 2025) - Enhanced Communication and Advanced Features

The MUXI Framework v0.5.0 will focus on advanced communication capabilities, expanded LLM provider support, and performance optimizations.

#### Major Features

- **Advanced Agent-to-Agent (A2A) Communication**:
  - Capability discovery mechanism
  - Task delegation between agents
  - Context sharing with proper isolation
  - Conversation lifecycle management
  - External agent integration
  - Security and authentication

- **Multi-Modal Support**:
  - File attachment support in WebSocket API
  - Image processing capabilities
  - Document handling (PDF, Office documents)
  - Audio processing integration

- **MCP Server Enhancements**:
  - SSE-based MCP server implementation
  - Automatic tool discovery from agent capabilities
  - NPX bridge package for non-SSE clients
  - Streaming response handling
  - Authentication shared with REST API

- **LLM Provider Expansion**:
  - Anthropic LLM provider implementation
  - Gemini LLM provider implementation
  - Grok LLM provider implementation
  - Support for local models (Llama, Mistral, DeepSeek)
  - Model router for fallback and cost optimization

### v0.4.0 (Planned Q1 2025) - API-First Framework

The MUXI Framework v0.4.0 will introduce comprehensive API implementations as outlined in the API specification document, with a focus on making the framework accessible through multiple interfaces.

#### Major Features

- **REST API Implementation**:
  - Standard REST API endpoints (agent, conversation, memory management)
  - Authentication with API keys
  - Streaming support for chat endpoints with SSE
  - Proper error handling with standardized format
  - API versioning support
  - Rate limiting and throttling
  - API documentation using OpenAPI/Swagger

- **WebSocket API Implementation**:
  - WebSocket protocol for real-time communication
  - Support for multi-modal messages (text, images, audio)
  - Proper error handling and recovery mechanisms
  - Reconnection logic with exponential backoff
  - Support for attachments as specified in API documentation

- **MCP Server Implementation**:
  - HTTP+SSE-based MCP server implementation
  - Simplified credential management
  - Authentication that integrates with API keys
  - Tool discovery mechanism
  - Robust error handling and recovery

- **CLI Enhancements**:
  - Support for all API operations
  - Improved user experience with better formatting
  - Configuration management commands
  - Multi-modal interaction support

- **Web UI Development**:
  - Responsive design for mobile and desktop
  - Real-time updates using WebSocket
  - Agent management dashboard
  - Configuration interface

## Current Release

### v0.3.0 (March 2025) - Context Knowledge & Memory Modernization

The MUXI Framework v0.3.0 brought significant improvements to knowledge capabilities, enhancing agents with specialized context knowledge. It also included a major architectural change in how memory is managed throughout the framework.

#### Major Features

- **Memory Architecture Migration**:
  - **Breaking Change**: Moved memory management from agent level to orchestrator level
  - Consolidated memory initialization in the orchestrator constructor
  - Updated configuration format to specify memory at the top level, not per agent
  - Removed `setup_memory()` methods, memory is now provided during initialization
  - Memory is now shared efficiently between agents
  - Simplified multi-user memory management
  - Significantly reduced memory duplication and improved performance
  - Enabled more complex memory sharing patterns between agents

- **Agent-Level Knowledge Base**:
  - File-based knowledge sources with automatic embedding generation
  - Efficient in-memory vector storage using FAISS
  - Persistent caching of embeddings for cost optimization
  - Dynamic embedding dimension detection based on the agent's model

- **Enhanced Knowledge API**:
  - Add and remove knowledge sources programmatically
  - Search knowledge with relevance controls
  - List and manage knowledge sources

- **Declarative Knowledge Configuration**:
  - Specify file paths and descriptions
  - Automatic loading and embedding on agent initialization

- **MCP Server Enhancements**:
  - Made credentials optional for MCP servers
  - Better documentation on MCP server configuration
  - Updated examples to demonstrate credential-optional usage patterns

### v0.2.0 (February 2025) - Architecture Migration

The MUXI Framework v0.2.0 marked a significant milestone with the completion of our architectural migration to a modular, package-based structure.

#### Major Features

- **Modular Package Structure**:
  - Reorganized from a monolithic structure to a modular, package-based architecture
  - Changed imports from `src.*` to `muxi.core.*`, `muxi.cli.*`, etc.
  - Created separately installable packages for core functionality, CLI, server, and web interface
  - Established well-defined interfaces between subsystems

### v0.1.0 (January 2025) - Foundation Release

The initial release of the MUXI Framework established the core architecture and essential functionality.

#### Major Features

- **Core Agent System**:
  - Basic agent functionality with LLM integration
  - System message handling
  - Message processing pipeline

- **Memory Systems**:
  - Buffer memory using FAISS for short-term context
  - Long-term memory using PostgreSQL with pgvector
  - Context memory for user-specific structured information

- **MCP Integration**:
  - MCP handler for communication with external services
  - Multiple transport types (HTTP+SSE, Command-line)
  - Tool call processing and response handling

- **Orchestrator**:
  - Multi-agent management
  - Intelligent message routing
  - Agent description handling

- **Command Line Interface**:
  - Terminal-based user interface
  - Agent interaction commands
  - Server management
