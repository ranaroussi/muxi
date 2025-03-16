---
layout: default
title: Architecture
parent: Getting Started
has_children: false
nav_order: 3
permalink: /architecture/
---
# Architecture

The MUXI framework consists of several core components that work together to provide a flexible and powerful agent-based system.

## Architecture Diagram

```mermaid
%%{init: {"theme":"light", "flowchart": {"defaultRenderer": "elk"}} }%%
flowchart TB
    subgraph Interfaces["Interfaces"]
        REST["REST&nbsp;API"]
        WS["&nbsp;WebSocket&nbsp;"]
        APP["&nbsp;Web&nbsp;App&nbsp;"]
        CLI["&nbsp;CLI&nbsp;"]
    end
    subgraph MS["Memory"]
        Buffer["FAISS&nbsp;(ST)"]
        PGSQL["PGVector&nbsp;(LT)"]
        MBASE["Memobase"]
    end
    subgraph LE["LLM Engines"]
        LLM["Open AI"]
        Grok["Anthropic"]
        Ollama["Ollama"]
    end
    subgraph Tools["Tools"]
        BuiltIn["Built-in<br>Files,&nbsp;Search,&nbsp;etc."]
        Custom["Custom<br>User&nbsp;Generated"]
    end
    subgraph MUXI["<b><big>MUXI</big></b>"]
        Server["Server"]
        Orchestrator["Orchestrator"]
        Agent["Agent&nbsp;1"]
        Agent2["Agent&nbsp;N"]
        AgentN["Agent&nbsp;2"]
        MCP["MCP&nbsp;Handler"]
        MS
        LE
        Tools
    end
    REST --> Server
    WS --> Server
    APP --> Server
    CLI --> Server
    Server -- &nbsp;Forwards Request&nbsp; --> Orchestrator
    Orchestrator -- &nbsp;Routes&nbsp; --> Agent & Agent2 & AgentN
    Agent -- Uses --> LLM
    Agent -- &nbsp; &nbsp; &nbsp;Execute&nbsp; &nbsp; &nbsp; --> Tools
    Agent -- &nbsp;Accesses&nbsp; --> MS
    LLM <-- &nbsp;Communicates&nbsp; --> MCP
    LLM <-- &nbsp;Executes&nbsp; --> Tools
    MCP -- &nbsp;Executes&nbsp; --> MCP2[MCP&nbsp;Servers]
    PGSQL -- &nbsp;Profiles&nbsp; --- MBASE

    %% style APP fill:#ff6602,color:#fff,stroke:#e0085f
    style LLM fill:#bfb,stroke:#4f8f00
    style Server fill:#bfb,stroke:#4f8f00
    style Orchestrator fill:#bfb,stroke:#4f8f00
    style Agent fill:#bfb,stroke:#4f8f00
    style MCP fill:#bfb,stroke:#4f8f00
    style MUXI fill:#fff,stroke:#4f8f00,stroke-width:2px,stroke-dasharray:5
    style MS fill:#fff,stroke:#808080,stroke-dasharray:5
    style LE fill:#fff,stroke:#808080,stroke-dasharray:5
```

## Component Descriptions

### User Interfaces
- **REST API**: HTTP endpoints for agent management and communication
- **WebSocket**: Real-time bidirectional communication for streaming responses
- **Web App**: Browser-based interface for interacting with agents
- **CLI**: Command-line interface for local agent interaction

### Core Framework
- **Server**: Handles incoming requests from different interfaces
- **Orchestrator**: Manages multiple agents and their interactions
- **Agents**: Autonomous entities that process requests using models, memory, and tools
- **MCP Handler**: Model Context Protocol for standardized communication with LLM providers

### Memory Systems
- **FAISS (ST)**: Short-term buffer memory using vector embeddings
- **PGVector (LT)**: Long-term persistent memory using PostgreSQL with vector extensions
- **Memobase**: User-aware memory partitioning for multi-tenant applications

### LLM Engines
- **OpenAI**: Integration with OpenAI models (GPT-4, etc.)
- **Anthropic**: Integration with Anthropic models (Claude, etc.)
- **Ollama**: Support for local models via Ollama

### Tools
- **Built-in Tools**: File operations, web search, calculator, etc.
- **Custom Tools**: User-created tools to extend agent capabilities

## Data Flow

1. User requests come in through one of the interfaces (REST, WebSocket, Web App, CLI)
2. Server forwards requests to the Orchestrator
3. Orchestrator directs requests to the appropriate Agent
4. Agent processes requests using:
   - LLM for generating responses
   - Memory for context and persistence
   - Tools for performing actions
5. MCP Handler standardizes communication between the framework and LLM providers
6. Responses are sent back through the original interface
