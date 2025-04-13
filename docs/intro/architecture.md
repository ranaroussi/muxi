---
layout: default
title: Architecture
parent: Introduction
nav_order: 4
permalink: /intro/architecture
---

# Architecture

## What You'll Learn
- The architectural principles of the MUXI Framework
- The modular package structure
- The service-oriented approach
- How the different components interact

## Prerequisites
- Basic understanding of software architecture concepts
- Familiarity with the [Overview](/intro/overview) (recommended)

## Architecture Overview

MUXI is designed with a modular, extensible architecture that allows for flexibility in deployment and usage. The framework follows a service-oriented approach, allowing components to be deployed together or separately.

```
┌───────────────────┐
│      Clients      │
│   (CLI/Web/SDK)   │
└─────────┬─────────┘
          │
          │ (API/SSE/WS)
          │
┌─────────│───────────────────────────────────────────┐
│         │    MUXI Server (Local/Remote)             │
│         │                                           │
│         │        ┌───────────────┐                  │
│         └───────>│  Orchestrator │                  │
│                  └───────┬───────┘                  │
│         ┌────────────────┼────────────────┐         │
│         │                │                │         │
│         ▼                ▼                ▼         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │    ┌───────────┐
│  │   Agent 1   │  │   Agent 2   │  │   Agent N   │-------│ Knowledge │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  │    └───────────┘
│         ↓                ↓                ↓         │
│         └────────┬───────┴────────┬───────┘         │
│                  ↓                :                 │
│           ┌──────┴──────┐  ┌──────┴──────┐          │
│           │ MCP Handler │  │   Memory    │          │
│           └──────┬──────┘  └─────────────┘          │
└──────────────────│──────────────────────────────────┘
                   │
                   │ (HTTP)
                   ▼
┌─────────────────────────────────────────────────────┐
│                    MCP Servers                      │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │
│  │   Weather   │  │  Web Search │  │     ....    │  │
│  └─────────────┘  └─────────────┘  └─────────────┘  │
└─────────────────────────────────────────────────────┘
```

## Core Components

### 1. Server Layer

The Server layer is the entry point for all external communication with the framework:

- **REST API**: Endpoints for agent management, chat operations, and memory interactions
- **WebSocket Server**: Real-time, bidirectional communication for streaming responses
- **Web App**: Frontend interface for visual interaction
- **CLI**: Command-line interface for text-based interaction

### 2. Orchestrator

The Orchestrator is the central coordinator that:

- Manages the lifecycle of all agents in the system
- Routes messages to the appropriate agent
- Handles agent creation, configuration, and removal
- Provides a unified interface for all client applications

### 3. Agents

Agents are the intelligent entities that process information and produce responses:

- Integrate with a specific LLM provider
- Maintain their own memory systems
- Access MCP servers for extended capabilities
- Process messages according to their system instructions

### 4. Model Context Protocol (MCP)

The MCP is a standardized communication layer between agents and external services:

- Provides a consistent interface for integrating external functionality
- Handles specialized message formatting
- Manages request/response parsing and serialization
- Supports function execution and result handling

### 5. Memory Systems

MUXI includes a sophisticated memory architecture:

- **Buffer Memory**: Short-term contextual memory for conversation flow
- **Long-Term Memory**: Persistent storage of important information
  - **PostgreSQL with pgvector**: For production and multi-user applications
  - **SQLite with sqlite-vec**: For local development and single-user applications
- **Memobase**: Multi-user aware memory system that partitions by user ID

### 6. MCP Servers

MCP Servers provide extended functionality to agents:

- Implement standardized MCP protocol
- Can be deployed separately from the main application
- Provide specialized services like weather data, web search, etc.
- Can be implemented in any language that supports HTTP

## Modular Package Structure

The MUXI framework is organized into a modular monorepo structure with multiple packages:

```
muxi-framework/
├── packages/
│   ├── core/          # Core components: agents, memory, MCP interface
│   ├── server/        # REST API and WebSocket server
│   ├── cli/           # Command-line interface
│   ├── web/           # Web user interface
│   └── muxi/          # Meta-package that integrates all components
└── tests/             # Test suite for all components
```

### Package Descriptions

#### Core Package (`muxi-core`)
The foundation of the framework:
- Contains Agent, Memory, and MCP implementations
- Has minimal dependencies for lightweight usage
- Provides MCP handler implementation for connecting to MCP servers

#### Server Package (`muxi-server`)
Handles all communication with clients:
- Implements the REST API server for agent interaction
- Includes WebSocket server for real-time communication
- Handles request routing and middleware
- Manages API authentication

#### CLI Package (`muxi-cli`)
Command-line interface for the framework:
- Provides interactive terminal-based chat interface
- Implements agent management and server commands
- Includes utilities for generating MCP server templates

#### Web Package (`muxi-web`)
The web interface for the framework:
- Contains the frontend user interface built with React
- Implements WebSocket client for real-time communication
- Provides agent configuration UI

#### Meta Package (`muxi`)
Ties everything together:
- Integrates core, server, and CLI packages
- Provides a unified API for the whole framework
- Simplifies installation and usage

## Service-Oriented Approach

MUXI follows a service-oriented architecture that enables:

### 1. Client-Server Model
- Separate client and server components
- Local and remote operation with the same API
- Flexible authentication mechanisms
- Connection management utilities

### 2. Hybrid Communication Protocol
- HTTP for standard API requests
- SSE (Server-Sent Events) for streaming responses
  - Real-time token-by-token streaming
  - Automatic connection closure after response completion
- WebSockets for advanced bi-directional capabilities
  - Bi-directional communication for complex interactions
  - Available through `app.open_socket()` API

### 3. Authentication
- API key authentication
- Auto-generated keys with one-time display
- Environment variable configuration

### 4. Database Options
- PostgreSQL with pgvector for production and multi-user environments
  - Scalable vector storage and retrieval
  - Advanced indexing for large datasets
  - Concurrent access handling
- SQLite with sqlite-vec for development and single-user applications
  - Simplified deployment with file-based storage
  - Cross-platform compatibility
  - Uses the sqlite-vec Python package for vector operations

### 5. MCP Server Integration
- All external functionality provided through standardized MCP servers
- Consistent interface for interacting with external services
- Service discovery mechanisms
- Deployment utilities

## Usage Examples

### Local Mode
```python
# Local usage with unified API
from muxi import muxi

app = muxi()

# Add an agent from a configuration file
app.add_agent("weather", "agents/weather_agent.yaml")

# Chat with the agent
response = app.chat("What's the weather in New York?")
print(response)
```

### Server Mode
```python
# Start in server mode
from muxi import muxi

app = muxi()
app.add_agent("assistant", "agents/assistant.yaml")
app.run(host="0.0.0.0", port=5050)
```

### Client Mode
```python
# Connect to a remote server
from muxi.client import MuxiClient

client = MuxiClient(url="http://my-server.com:5050", api_key="your-api-key")
response = client.chat("What's the weather in New York?")
print(response)
```

## Advanced Topics

For deeper exploration of the architecture:

- [Orchestrator](/technical/agents/orchestration) - Learn about the orchestration system
- [MCP Fundamentals](/technical/mcp/fundamentals) - Understand the Model Context Protocol
- [Package Structure](/reference/package) - Detailed package organization

## What's Next

- [Installation](/intro/installation) - Install MUXI and set up your environment
- [Simple Agents](/agents/simple) - Create your first agent
- [Server Deployment](/clients/server) - Deploy MUXI as a server
