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
│  CLI/API/Web  │──────│   Tools   │
└───────────────┘      └───────────┘
```

### Core Components

1. **Model Context Protocol (MCP)**: Standardized communication layer with LLMs
   - Provides consistent interfaces for different LLM providers
   - Handles message formatting and processing

2. **Memory System**: Stores conversation history and knowledge
   - Buffer memory for short-term context
   - Long-term memory for persistent storage
   - Memobase for multi-user support
   - Domain knowledge for structured information

3. **Tool System**: Extends agent capabilities
   - Provides a registry for tools
   - Handles tool execution and results

4. **Agents**: Core entities that combine LLMs with memory and tools
   - Process user messages
   - Generate responses
   - Execute tools when needed

5. **Orchestrator**: Manages multiple agents
   - Routes messages to appropriate agents
   - Facilitates inter-agent communication
   - Manages agent lifecycle

6. **Interfaces**: Multiple ways to interact with the framework
   - CLI for terminal-based interactions
   - API for programmatic access
   - Web UI for visual interaction
   - WebSocket for real-time communication

## Evolution to Service-Oriented Architecture

The MUXI framework is evolving towards a more flexible, service-oriented approach that enables distributed deployment while maintaining simplicity and ease of use.

### Target Architecture

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
│         │         ┌──────────────┐                  │
│         └───────> │ Orchestrator │                  │
│                   └──────┬───────┘                  │
│         ┌────────────────┼────────────────┐         │
│         │                │                │         │
│         ▼                ▼                ▼         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │
│  │   Agent 1   │  │   Agent 2   │  │   Agent N   │  │
│  │ (from YAML) │  │ (from JSON) │  │ (from YAML) │  │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  │
│         │                │                │         │
│         └────────┬───────┴────────┬───────┘         │
│                  │                │                 │
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
│  │ Weather API │  │ Search Tool │  │ Custom Tool │  │
│  └─────────────┘  └─────────────┘  └─────────────┘  │
└─────────────────────────────────────────────────────┘
```

### Key Architectural Changes

1. **Client-Server Model**
   - Separate client and server components
   - Local and remote operation with the same API
   - Flexible authentication mechanisms
   - Connection management utilities

2. **Modular Packaging**
   - Core package with minimal dependencies
   - Server package with full capabilities
   - CLI package for remote connections
   - Web package for browser-based access

3. **Hybrid Communication Protocol**
   - HTTP for standard API requests
   - SSE (Server-Sent Events) for streaming responses
     - Real-time token-by-token streaming
     - Automatic connection closure after response completion
   - WebSockets for multi-modal capabilities (Omni features)
     - Bi-directional communication for audio/video
     - Available through `app.open_socket()` API

4. **Authentication Implementation**
   - API key authentication
   - Auto-generated keys with one-time display
   - Environment variable configuration

5. **MCP Server Unification**
   - Tool system based on MCP servers
   - Adapters for local Python tools
   - Service discovery mechanisms
   - Deployment utilities

### Client Usage

```python
# Local usage (unchanged)
app = muxi()

# Remote usage
app = muxi(
    server_url="http://server-ip:5050",
    api_key="your_api_key"
)

# Streaming responses via SSE
for chunk in app.chat("Tell me a story", stream=True):
    print(chunk, end="", flush=True)

# Multi-modal capabilities via WebSockets
socket = app.open_socket()
await socket.send_message("Process this image", images=["path/to/image.jpg"])
await socket.close()
```

## Implementation Strategy

The evolution to the service-oriented architecture will be implemented in phases:

1. **Core Architecture Refactoring**
   - Separate local mode from server mode
   - Implement authentication framework
   - Create client-side connector

2. **MCP Server Unification**
   - Refactor tool system to MCP-based approach
   - Update configuration schemas
   - Create tool adapters

3. **Client Applications**
   - Update CLI interface
   - Modify web app for standalone use
   - Create client libraries

4. **Packaging and Distribution**
   - Restructure for modular packaging
   - Set up CI/CD for package publishing
   - Create package-specific documentation

For a detailed implementation roadmap, see [ARCHITECTURE_EVOLUTION.md](../ARCHITECTURE_EVOLUTION.md) and the [roadmap](roadmap.md).
