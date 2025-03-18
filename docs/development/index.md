---
layout: default
title: Development
nav_order: 7
has_children: true
permalink: /development
---

# Development

Welcome to the development section of the MUXI Framework documentation. This section is designed for contributors and developers who want to understand how the framework is built and how to contribute to its development.

## Architecture Migration

The MUXI Framework has successfully completed its migration to a modular, package-based architecture. This transition involved:

1. Reorganizing from a monolithic structure to a modular, package-based architecture
2. Migrating imports from `src.*` to `muxi.core.*`, `muxi.cli.*`, etc.
3. Creating independent packages that can be installed separately
4. Establishing clear boundaries between subsystems

The modular design enhances maintainability and facilitates future development by:
- Allowing independent versioning of components
- Providing clearer boundaries between subsystems
- Enabling more focused testing
- Supporting separate deployments when needed

## Contributing

We welcome contributions to the MUXI Framework! Whether you're fixing bugs, adding features, or improving documentation, your help is appreciated.

Before contributing, please read our [Contributing Guidelines](./contributing) to understand our development process, coding standards, and how to submit pull requests.

## Codebase Organization

The MUXI Framework is organized into several packages:

- `core`: Core functionality including models, memory, tools, and orchestration
- `cli`: Command-line interface for using MUXI
- `server`: REST API and WebSocket server
- `web`: Web interface for interacting with MUXI
- `clients`: Client libraries for various languages

For more details, see our [Codebase Organization](./codebase) page.

## Testing

Testing is crucial for maintaining the stability and reliability of the MUXI Framework. We use a combination of unit tests, integration tests, and end-to-end tests.

For more information on our testing approach, see our [Testing Strategies](./testing) page.

## Changelog

For a detailed list of changes made to the MUXI Framework, see our [Changelog](./changelog).

## About This Section

The Development section provides guidelines, best practices, and resources for developers who want to contribute to MUXI. It covers everything from setting up a development environment to understanding the codebase structure and contributing code.

## What's In This Section

- [Contributing Guidelines](/development/contributing) - How to contribute to the project
- [Testing Strategies](/development/testing) - Testing approach and best practices
- [Codebase Organization](/development/codebase) - Detailed insight into the codebase structure
- [Changelog](/development/changelog) - Record of changes and versions

## Prerequisites

Before diving into development, it's recommended that you:

- Have a good understanding of the MUXI Framework's core concepts
- Be familiar with Python, FastAPI, and modern web development
- Understand basic Git workflow and GitHub collaboration
- Have experience with testing frameworks like pytest

## Getting Started with Development

1. Set up your development environment following the [Contributing Guidelines](/development/contributing)
2. Understand the [Codebase Organization](/development/codebase)
3. Learn the [Testing Strategies](/development/testing) to ensure your contributions maintain quality
4. Check the [Changelog](/development/changelog) to understand recent changes

## Key Development Principles

MUXI development follows these core principles:

- **Modularity**: Components should be loosely coupled and highly cohesive
- **Testability**: All code should be testable and tested
- **Documentation**: Code should be well-documented with docstrings and comments
- **Backward Compatibility**: Breaking changes should be minimized and clearly documented
- **Performance**: Code should be efficient and scalable

## Related Resources

For API documentation and technical details, refer to the [Reference](/reference/) section. For deep dives into the technical architecture, see the [Technical Deep Dives](/technical/) section.
