---
layout: default
title: Overview & Key Concepts
parent: Introduction
nav_order: 1
permalink: /intro/overview/
---

# Overview & Key Concepts

## What You'll Learn
- What the MUXI Framework is and what problems it solves
- The key components of the framework
- How these components work together
- Core architectural principles

## Prerequisites
- None - this is a starting point for all users

## MUXI Framework Overview

MUXI is an extensible framework for building AI agents with real-time communication capabilities, memory persistence, and MCP server integration. It simplifies the process of creating sophisticated AI systems by providing a modular, well-structured foundation.

{: .warning }
> This project is a work in progress and is not yet ready for production use. The framework is actively being developed with new features being added regularly. Please refer to the [roadmap](/development/roadmap) for information about the current state of the project and where it's headed.

## Key Features

- **Multi-Agent Orchestration**: Create and manage multiple AI agents with different capabilities
- **Intelligent Message Routing**: Automatically select the most appropriate agent based on message content
- **Model Context Protocol (MCP)**: Connect to external services via standardized MCP servers
- **Standardized LLM Communication**: Use a consistent protocol across different LLM providers
- **Memory Systems**: Short-term buffer memory and long-term persistent memory
- **Multi-User Support**: Memobase provides user-specific memory partitioning for multi-tenant applications
- **Domain Knowledge**: Store and retrieve structured information to personalize agent responses
- **Real-Time Communication**: WebSocket support for instant messaging
- **REST API**: Comprehensive API for managing agents, MCP servers, and conversations
- **Command Line Interface**: Rich terminal-based interface for creating and interacting with agents
- **Flexible Configuration**: Define agents using YAML or JSON with minimal code

## Core Architecture

MUXI follows a modular design where specialized components work together to enable complex agent behaviors:

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
│  │   Agent 1   │  │   Agent 2   │  │   Agent N   │-------│  Domain   │
│  │    (YAML)   │  │    (JSON)   │  │    (YAML)   │  │    │ Knowledge │
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
│              MCP Servers (via Command/SSE)          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │
│  │   Weather   │  │  Web Search │  │     ....    │  │
│  └─────────────┘  └─────────────┘  └─────────────┘  │
└─────────────────────────────────────────────────────┘
```

## Key Components

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
- **Memobase**: Multi-user aware memory system that partitions by user ID

### 6. LLM Providers
The framework supports multiple LLM providers:

- OpenAI (GPT models)
- Anthropic (Claude models)
- Local models via Ollama
- Expandable to additional providers

## How Everything Works Together

1. **Client Requests**: Enter through one of the interfaces (REST, WebSocket, CLI, Web App)
2. **Server Processing**: The server layer validates and routes requests to the Orchestrator
3. **Orchestration**: The Orchestrator identifies the target agent and forwards the message
4. **Agent Processing**:
   - The agent retrieves relevant context from memory
   - Formulates a prompt for the LLM
   - Sends the prompt to the LLM provider
5. **LLM Interaction**:
   - The LLM processes the prompt and generates a response
   - If MCP requests are needed, they are identified and extracted
6. **MCP Server Execution**:
   - MCP requests are routed to the appropriate servers
   - Servers execute with the provided parameters
   - Results are returned to the agent
7. **Response Formulation**:
   - The agent incorporates results if applicable
   - Formulates the final response
8. **Memory Updates**:
   - The conversation is stored in buffer memory
   - Important information is persisted to long-term memory
9. **Client Response**: The response is returned to the client through the original interface

## What Makes MUXI Different?

MUXI sets itself apart from other frameworks by:

1. **Simplicity First**: MUXI abstracts away the complexity of text splitting, embeddings, and prompt engineering, letting you focus on building great agents
2. **Truly Multi-Agent**: Built from the ground up with multi-agent orchestration in mind
3. **Standardized External Services**: The MCP provides a clean, standard way to integrate external services
4. **Multi-User by Design**: User-specific memory partitioning is built into the core architecture
5. **Hybrid Communication**: Support for both request-response and real-time communication patterns

## Advanced Topics

For a deeper understanding of each component, explore these technical deep dives:

- [Agent Fundamentals](/technical/agents/fundamentals)
- [Memory Systems](/technical/memory/buffer)
- [MCP Fundamentals](/technical/mcp/fundamentals)
- [Orchestration](/technical/agents/orchestration)

## What's Next

- [Why MUXI?](/intro/why-muxi) - Learn why MUXI is the right choice for your AI projects
- [Quick Start Guide](/intro/quick-start) - Get up and running with MUXI
- [Architecture](/intro/architecture) - Dive deeper into the framework's architecture
