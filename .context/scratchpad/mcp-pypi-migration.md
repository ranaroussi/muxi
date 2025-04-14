# MCP Package Migration: GitHub to PyPI

## Overview

The Model Context Protocol (MCP) Python SDK is now available on PyPI as the `mcp` package. This document outlines the steps needed to migrate from using the GitHub repository directly to the official PyPI package.

## Migration Steps

### 1. Update Requirements

Update the `requirements.txt` file to use the PyPI package instead of the GitHub repository:

```diff
- # Model Context Protocol - we're using the package from GitHub since it's not on PyPI yet
- # This is version 1.4.2.dev4+6b6f34e
- git+https://github.com/modelcontextprotocol/python-sdk.git
+ # Model Context Protocol
+ mcp>=1.4.1  # Now available on PyPI
```

### 2. Update Imports

The package structure should be the same, but verify all imports. Key modules include:

```python
# Core JSON-RPC components
from mcp import JSONRPCRequest, JSONRPCResponse

# Client components
from mcp.client.session import ClientSession

# Server components (if needed)
from mcp.server.fastmcp import FastMCP
```

### 3. Update HTTPSSETransport Implementation

Our custom implementation in `packages/core/src/muxi/core/mcp_handler.py` should now leverage the MCP package's transport capabilities more directly:

1. Use the reference implementation from `tests/mcp_updated_transport.py`
2. Ensure it works with the MCP package from PyPI
3. Update the connection and request handling logic based on our working test implementation

### 4. Testing

Test the integration to ensure compatibility:

1. Run the test script with the PyPI package installed: `python tests/mcp_updated_transport.py`
2. Verify that it can connect to the MCP server at `server.mcpify.ai`
3. Ensure that requests are properly sent and responses are received

### 5. Documentation Updates

Update documentation to reflect the migration:

1. Update `mcp-progress.md` to note the PyPI availability
2. Update `mcp-integration-guide.md` with PyPI installation instructions
3. Add notes about optional extras (`cli`, `rich`, `ws`) if needed

## Benefits of PyPI Migration

- Standardized versioning and installation
- Easier dependency management
- Faster installation (no Git clone required)
- Better compatibility with package managers and virtual environments
- Access to pre-built wheels for faster installation

## Potential Issues

- Version differences between GitHub and PyPI
- Module import paths might differ slightly
- Additional dependencies might be required
- API changes between versions

## Current Migration Status

- [x] Updated `requirements.txt` to use PyPI package
- [x] Verified basic functionality with PyPI package
- [x] Added PyPI package information to documentation
- [ ] Updated all import statements throughout the codebase
- [ ] Fully integrated with the `HTTPSSETransport` implementation

## References

- [MCP Package on PyPI](https://pypi.org/project/mcp/)
- [MCP GitHub Repository](https://github.com/modelcontextprotocol/python-sdk)
- [Working Implementation](tests/mcp_updated_transport.py)
- [MCP Integration Guide](mcp-integration-guide.md)
