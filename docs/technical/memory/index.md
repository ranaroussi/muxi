---
layout: default
title: Memory System
parent: Technical Deep Dives
has_children: true
nav_order: 2
permalink: /technical/memory/
---

# Memory System

This section provides technical deep dives into the memory architecture of the MUXI Framework.

## About This Section

The memory system is a key component that enables agents to maintain context over time and store important information. This section explores the different memory subsystems, their internal implementations, and how they work together to provide a comprehensive memory solution.

## What's In This Section

- [Buffer Memory](buffer) - Short-term contextual memory for conversations
- [Long-Term Memory](long-term) - Persistent storage of important information
- [Multi-User Memory (Memobase)](memobase) - Partitioning memory by user
- [Domain Knowledge](domain-knowledge) - Structured knowledge integration

## Prerequisites

Before diving into this section, we recommend:
- Understanding the basics of [agent memory](../../agents/memory)
- Familiarity with vector embeddings and vector databases
- Knowledge of PostgreSQL and the pgvector extension
- Understanding of semantic search concepts

## Implementation Details

MUXI's memory system includes several key technical features:
- Vector embeddings for semantic search
- Automatic text chunking and processing
- PostgreSQL with pgvector for long-term storage
- Efficient buffer management with automatic summarization
- Memory partitioning for multi-user scenarios

## Related Topics

These topics are closely related to the memory system:
- [Agent Fundamentals](../agents/fundamentals) - How agents use memory
- [MCP Fundamentals](../mcp/fundamentals) - How MCP servers can access memory
- [REST API](../communication/rest-api) - How to interact with memory through the API
