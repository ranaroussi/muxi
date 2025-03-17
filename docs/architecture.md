---
layout: default
title: Architecture
parent: Core Concepts
has_children: false
nav_order: 1
---

# MUXI Architecture

The MUXI framework is designed with a modular, extensible architecture that allows for flexibility in deployment and usage. This document outlines the current architecture and the evolution towards a more service-oriented approach.

## Current Architecture

MUXI is built around several core components that work together to provide a complete AI agent framework:

```
┌───────────────┐      ┌───────────┐      ┌───────────┐
│  Application  │──────│  Agents   │──────│    LLM    │
└───────┬───────┘      └─────┬─────┘      └───────────┘
        │                    │
        │              ┌─────┴─────┐
        │              │  Memory   │
        │              └─────┬─────┘
┌───────┴───────┐      ┌─────┴─────┐
│  CLI/API/Web  │──────│ MCP Server│
└───────────────┘      └───────────┘
```

### Core Components

1. **Model Context Protocol (MCP)**: Standardized communication layer
   - Provides consistent interfaces for LLM interaction
   - Connects to external MCP servers for extended functionality
   - Handles message formatting and processing

2. **Memory System**: Stores conversation history and knowledge
   - Buffer memory for short-term context
   - Long-term memory for persistent storage
   - Memobase for multi-user support
   - Domain knowledge for structured information

3. **MCP Servers**: External services that extend agent capabilities
   - Implement the standardized MCP protocol
   - Provide specialized functionality (weather, finance, web search, etc.)
   - Run as separate services with their own lifecycle

4. **Agents**: Core entities that combine LLMs with memory and MCP server connections
   - Process user messages
   - Generate responses
   - Connect to MCP servers for extended capabilities

5. **Orchestrator**: Manages multiple agents
   - Routes messages to appropriate agents
   - Facilitates inter-agent communication
   - Manages agent lifecycle

6. **Interfaces**: Multiple ways to interact with the framework
   - CLI for terminal-based interactions
   - API for programmatic access
   - Web UI for visual interaction
   - WebSocket for real-time communication

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

1. **Core Package (`muxi-core`)**
   - Contains foundational components like Agent, Memory, and MCP
   - Has minimal dependencies for lightweight usage
   - Provides MCP handler implementation for connecting to MCP servers

2. **Server Package (`muxi-server`)**
   - Implements the REST API server for agent interaction
   - Includes WebSocket server for real-time communication
   - Handles request routing and middleware
   - Manages API authentication

3. **CLI Package (`muxi-cli`)**
   - Provides command-line interface for interacting with agents
   - Includes interactive terminal-based chat interface
   - Implements agent management and server commands
   - Includes utilities for generating MCP server templates

4. **Web Package (`muxi-web`)**
   - Contains the frontend user interface built with React
   - Implements WebSocket client for real-time communication
   - Provides agent configuration UI

5. **Meta Package (`muxi`)**
   - Integrates core, server, and CLI packages
   - Provides a unified API for the whole framework
   - Simplifies installation and usage

## Service-Oriented Architecture

The MUXI framework is a flexible, service-oriented approach that enables distributed deployment while maintaining simplicity and ease of use.

### Architecture

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
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │
│  │   Agent 1   │  │   Agent 2   │  │   Agent N   │  │
│  │    (YAML)   │  │    (JSON)   │  │    (YAML)   │  │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  │
│         ↓                ↓                ↓         │
│         └────────┬───────┴────────┬───────┘         │
│                  ↓                :                 │
│           ┌──────┴──────┐  ┌──────┴──────┐          │
│           │ MCP Handler │  │   Memory    │          │
│           └──────┬──────┘  └─────────────┘          │
└──────────────────│──────────────────────────────────┘
                   │
                   │ (gRPC/HTTP)
                   ▼
┌─────────────────────────────────────────────────────┐
│              MCP Servers (via Command/SSE)          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │
│  │   Weather   │  │  Web Search │  │     ....    │  │
│  └─────────────┘  └─────────────┘  └─────────────┘  │
└─────────────────────────────────────────────────────┘
```

### Key Architectural Changes

1. **Client-Server Model**
   - Separate client and server components
   - Local and remote operation with the same API
   - Flexible authentication mechanisms
   - Connection management utilities

2. **Hybrid Communication Protocol**
   - HTTP for standard API requests
   - SSE (Server-Sent Events) for streaming responses
     - Real-time token-by-token streaming
     - Automatic connection closure after response completion
   - WebSockets for multi-modal capabilities (Omni features)
     - Bi-directional communication for audio/video
     - Available through `app.open_socket()` API

3. **Authentication Implementation**
   - API key authentication
   - Auto-generated keys with one-time display
   - Environment variable configuration

4. **MCP Server Unification**
   - All external functionality provided through standardized MCP servers
   - Consistent interface for interacting with external services
   - Service discovery mechanisms
   - Deployment utilities

### Client Usage

```python
# Local usage with unified API
from muxi import muxi

app = muxi()

# Chat with a specific agent
response = await app.chat("What's the weather in New York?", agent_id="weather")
print(response)

# Start the server
app.run()
```

## Implementation Strategy

The evolution to the service-oriented architecture has been implemented in phases:

1. **Core Architecture Refactoring**
   - Separate local mode from server mode
   - Implement authentication framework
   - Create client-side connector

2. **MCP Server Implementation**
   - Fully transition to MCP-based approach for all external functionality
   - Update configuration schemas to support MCP servers
   - Remove legacy tool system

3. **Client Applications**
   - Update CLI interface
   - Modify web app for standalone use
   - Create client libraries

4. **Packaging and Distribution**
   - Restructure for modular packaging
   - Set up CI/CD for package publishing
   - Create package-specific documentation

For a detailed implementation roadmap, see the [roadmap](roadmap.md).
