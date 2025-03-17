---
layout: home
title: Home
nav_order: 1
permalink: /
---

# MUXI Framework Documentation

Welcome to the official documentation for MUXI, an extensible framework for building AI agents with real-time communication capabilities, memory persistence, and MCP server integration.

{: .warning }
> This project is a work in progress and is not yet ready for production use. The framework is actively being developed with new features being added regularly. Please refer to the [roadmap](./development/roadmap) for information about the current state of the project and where it's headed.

## Documentation Structure

Our documentation is organized to serve both newcomers and experienced developers:

### [Introduction](./intro/)
Start here to understand the MUXI Framework, its core concepts, and how to get started:
- [Overview & Key Concepts](./intro/overview)
- [Why MUXI?](./intro/why-muxi)
- [Quick Start Guide](./intro/quick-start)
- [Architecture](./intro/architecture)
- [Installation](./intro/installation)

### [Building Agents](./agents/)
Learn how to create and configure agents for different purposes:
- [Simple Agents](./agents/simple)
- [Multi-Agent Systems](./agents/multi-agent)
- [Adding Memory](./agents/memory)
- [Agent Configuration](./agents/configuration)

### [Extending Capabilities](./extend/)
Enhance your agents with external services and domain knowledge:
- [Using MCP Servers](./extend/using-mcp)
- [Creating Custom MCP Servers](./extend/custom-mcp)
- [Domain Knowledge Integration](./extend/domain-knowledge)
- [Multi-Modal Support](./extend/multi-modal)

### [Interfaces & Clients](./clients/)
Discover the different ways to interact with MUXI:
- [Command-Line Interface](./clients/cli)
- [Server Deployment](./clients/server)
- [Web Dashboard](./clients/web)
- [WebSocket Communication](./clients/websocket)

### [Technical Deep Dives](./technical/)
Detailed information for developers who want to understand the framework at a deeper level:
- [Agents & Models](./technical/agents/)
- [Memory System](./technical/memory/)
- [MCP System](./technical/mcp/)
- [Communication](./technical/communication/)

### [Reference](./reference/)
Detailed reference material:
- [API Documentation](./reference/api)
- [Configuration Options](./reference/configuration)
- [Package Structure](./reference/package)
- [Examples Library](./reference/examples)

### [Development](./development/)
Information for contributors and developers:
- [Contributing Guidelines](./development/contributing)
- [Testing Strategies](./development/testing)
- [Codebase Organization](./development/codebase)
- [Changelog](./development/changelog)

## Key Features

- **Multi-Agent Orchestration**: Create and manage multiple AI agents with different capabilities
- **Intelligent Message Routing**: Automatically select the most appropriate agent based on message content
- **Model Context Protocol (MCP)**: Connect to external services via standardized MCP servers
- **Memory Systems**: Short-term buffer memory and long-term persistent memory
- **Multi-User Support**: Memobase provides user-specific memory partitioning
- **Domain Knowledge**: Store and retrieve structured information to personalize agent responses
- **Real-Time Communication**: WebSocket support for streaming responses
- **Flexible Configuration**: Define agents using YAML or JSON with minimal code

## Getting Started

The fastest way to get started with MUXI is to follow our [Quick Start Guide](./intro/quick-start).

## Community & Support

- [GitHub Repository](https://github.com/ranaroussi/muxi)
- [Issue Tracker](https://github.com/ranaroussi/muxi/issues)

## License

This project is licensed under a dual licensing model to balance open-source collaboration with sustainable business practices.

During the development phase, the software is licensed under the **Creative Commons Attribution-NonCommercial-NoDerivatives 4.0 (CC BY-NC-ND 4.0)** license.
