# Simplified API Key Authentication for MUXI API

Based on the revised approach for API key handling, here's the updated plan for implementing the dual API key authentication system (user and admin keys) at the MUXI Core level:

## Current State Analysis

1. **No Existing Authentication System**: The current codebase does not implement an API key authentication system for MUXI services. The existing API references in the code are primarily for external services like OpenAI.

2. **API Documentation Expectations**: According to the API documentation, authentication is expected to use Bearer tokens in the Authorization header, but this isn't implemented yet.

3. **API Server PRD Requirements**: The API Server PRD specifies a dual-key authentication system:
   - User/Interface Key: `sk_muxi_user_YOUR_KEY` (for client applications and chat interfaces)
   - Administrative Key: `sk_muxi_admin_YOUR_KEY` (for system management and configuration)

4. **Access Level Specification**: The PRD requires explicit access level specification using decorators, with all endpoints requiring at minimum a user key, and admin-specific endpoints requiring an admin key.

## Simplified Implementation Plan

### 1. Core-Level API Key Management

The simplified approach will handle API keys entirely in memory during runtime:

1. **Update Orchestrator and muxi Constructor**:
   - Add parameters to accept API keys at initialization time:
     ```python
     def __init__(self, user_api_key=None, admin_api_key=None, ...):
     ```
   - If keys are not provided, auto-generate temporary keys using `secrets` module
   - Store keys in memory for the lifecycle of the application
   - No persistent storage or key management infrastructure required

2. **Key Display on Initialization**:
   - When auto-generating keys, display them during startup (similar to Flask/FastAPI's server URL display)
   - Provide a clear visual distinction between user and admin keys
   - Add a warning that auto-generated keys are for development only

3. **Key Validation Function**:
   - Implement a simple method to validate keys against the in-memory stored keys
   - Return the key type (user/admin) for valid keys
   - Return None for invalid keys

### 2. Authentication Middleware Implementation

Implement lightweight authentication middleware for the API Server:

1. **Create Authentication Decorators**:
   - `@requires_user_key` - Ensure a valid user or admin key (default for all endpoints)
   - `@requires_admin_key` - Ensure a valid admin key only
   - Apply these decorators at the route level in FastAPI

2. **Error Handling**:
   - Define standardized authentication error responses
   - Implement informative error messages for authentication failures

### 3. Integration with Existing API Endpoints

Update the existing API endpoints to use the new authentication system:

1. **Apply Authentication to API Routes**:
   - Use the decorator approach for all API routes:

     ```python
     @app.get("/agents", tags=["Agents"], operation_id="list_agents")
     @requires_admin_key  # Developer endpoint requires admin key
     async def list_agents():
         # Implementation
     ```

   - Ensure all routes have at least `@requires_user_key` by default

2. **Orchestrator.run() Method**:
   - Add a new `run()` method to the Orchestrator class to match the functionality of `muxi.run()`
   - Display auto-generated API keys (if any) during this startup process

### 4. Testing and Documentation

1. **Unit Tests**:
   - Test API key validation logic
   - Test authentication decorators with different key types
   - Test access control with both valid and invalid keys

2. **Integration Tests**:
   - Test API endpoints with different authentication scenarios
   - Verify proper access control enforcement

3. **Documentation Updates**:
   - Update API documentation to reflect the simplified approach
   - Document recommended practices for providing API keys

## Implementation Locations

Here are the specific files that will need to be created or modified:

### Modified Files:
1. `packages/core/src/muxi/core/orchestrator.py` - Add API key parameters and `run()` method
2. `packages/server/src/muxi/api/app.py` - Apply authentication decorators to routes
3. `packages/muxi/__init__.py` - Update the `muxi` class constructor to accept API keys
4. `docs/reference/api.md` - Update API documentation

## Next Steps

1. Update the Orchestrator and muxi constructors to accept API keys
2. Implement key validation logic
3. Create the authentication decorators
4. Add the key display functionality to `run()` methods
5. Apply decorators to API routes
6. Update documentation

This simplified plan maintains the dual API key authentication system as specified in the PRD, but with a much lighter implementation that doesn't require persistent storage or complex key management. It places the responsibility for key management on the developers, which is appropriate for the current use cases.
