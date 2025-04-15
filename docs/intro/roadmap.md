---
title: Roadmap
nav_order: 12
parent: Introduction
---

# MUXI Framework Roadmap

> **Note**: This roadmap is subject to change based on community feedback and project priorities.

## Current State

MUXI Framework is currently in active development. The core feature roadmap is outlined below.

## Version 0.1.0 (Released)

- ✅ Core agent system
- ✅ Basic memory systems (short-term buffer)
- ✅ OpenAI integration
- ✅ Command line interface
- ✅ MCP Client integration (HTTP+SSE)
- ✅ MCP Client integration (Command)

## Version 0.2.0 (Released)

- ✅ Modular package structure
- ✅ Improved import paths
- ✅ Enhanced CLI
- ✅ Stability improvements

## Version 0.3.0 (Released)

- ✅ Memory architecture migration (agent memory ➔ orchestrator memory) [Breaking Change]
  - ✅ Orchestrator-level memory management
  - ✅ Memory sharing between agents
  - ✅ Simplified configuration and usage
- ✅ Agent-level knowledge base
- ✅ Enhanced knowledge API
- ✅ Long-term memory systems
  - ✅ PostgreSQL with pgvector support
  - ✅ SQLite with sqlite-vec support
- ✅ Multi-user memory support
- ✅ User context memory
- ✅ MCP server capabilities
  - ✅ SSE-based server endpoint for MCP host integration
  - ✅ Tool discovery from agent capabilities
  - ✅ Authentication shared with REST API

## Version 0.4.0 (In Development)

- 🔄 API Implementations
  - 🔄 REST API for agent interactions
  - 🔄 WebSocket API for streaming responses
- 🔄 CLI Enhancements
  - 🔄 Interactive mode improvements
  - 🔄 Configuration management
- 🔄 Web UI (Basic implementation)
  - 🔄 Chat interface
  - 🔄 Agent management

## Version 0.5.0 (Planned)

- 📅 A2A (Agent-to-Agent) Communication
  - 📅 Structured message format
  - 📅 Capability registration and discovery
  - 📅 Task delegation
  - 📅 Context sharing
  - 📅 Security and authentication
- 📅 Multi-modal support
  - 📅 Image understanding
  - 📅 Audio processing
- 📅 MCP Server Enhancements
  - 📅 Non-SSE client compatibility bridge
  - 📅 Enhanced security
- 📅 LLM Provider Expansion
  - 📅 Claude/Anthropic
  - 📅 LLama models
  - 📅 Google Gemini
  - 📅 Local models

## Future Roadmap

- 📅 Language-Specific SDKs
  - 📅 TypeScript/JavaScript
  - 📅 Go
  - 📅 Python
  - 📅 Java/Kotlin
- 📅 Enhanced tools and capabilities
  - 📅 Advanced task delegation
  - 📅 Autonomous planning
  - 📅 Advanced RAG techniques
- 📅 Integration with external systems
  - 📅 Database connectors
  - 📅 Web API integrations
  - 📅 Enterprise systems
- 📅 Advanced Multi-Agent Systems
  - 📅 Agent swarms
  - 📅 Custom agent roles
  - 📅 Hierarchical agent structures
  - 📅 Collaborative problem-solving
- 📅 Observability and monitoring
  - 📅 Telemetry
  - 📅 Performance metrics
  - 📅 Debugging tools
- 📅 Community plugins
  - 📅 Plugin architecture
  - 📅 Plugin marketplace
  - 📅 Plugin management

## Legend

- ✅ Completed
- 🔄 In Progress
- 📅 Planned
