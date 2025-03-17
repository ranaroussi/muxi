---
layout: default
title: Release Notes
nav_order: 8
permalink: /release-notes/
---

# Release Notes

## v0.2.0 (March 2025) - Architecture Migration

The MUXI Framework v0.2.0 marks a significant milestone with the completion of our architectural migration to a modular, package-based structure. This release focuses on improving the framework's architecture, maintainability, and extensibility rather than adding new features.

### Major Changes

- **Modular Package Structure**: Reorganized from a monolithic structure to a modular, package-based architecture
- **Import Path Migration**: Changed imports from `src.*` to `muxi.core.*`, `muxi.cli.*`, etc.
- **Independent Packages**: Created separately installable packages for core functionality, CLI, server, and web interface
- **Clearer Subsystem Boundaries**: Established well-defined interfaces between subsystems

### Benefits of the New Architecture

- **Independent Versioning**: Components can be versioned independently
- **Clearer Module Boundaries**: Better separation of concerns with well-defined interfaces
- **Focused Testing**: Tests can target specific packages
- **Flexible Deployment**: Support for installing only needed components
- **Enhanced Maintainability**: Easier to understand and modify codebase

### Breaking Changes

- Import paths have changed from `src.*` to `muxi.core.*`, etc.
- Configuration files now use the new package structure
- Extensions and custom components need to be updated to the new import structure

### Migration Guide

To upgrade from v0.1.x to v0.2.0:

1. Update your Python package: `pip install -U muxi`
2. Update any custom code to use the new import paths:
   - Replace `from src.core...` with `from muxi.core...`
   - Replace `from src.models...` with `from muxi.core.models...`
   - Replace `from src.memory...` with `from muxi.core.memory...`
3. For web UI support, install the web module: `pip install muxi-web`
4. For server deployments, install the server module: `pip install muxi-server`

### What's Next

With this architectural foundation in place, future releases will focus on:

- Enhanced multi-agent coordination
- Expanded tool capabilities
- Improved memory systems
- More sophisticated domain knowledge management
- Additional model providers and support for local models

Stay tuned for these exciting developments in upcoming releases!
