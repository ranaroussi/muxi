# Interface-Level User ID Generation PRD

## Overview

This document outlines the implementation plan for automatic user ID generation at the interface level in the MUXI Framework. This feature will ensure that even when explicit user IDs aren't provided, meaningful user identification can be established to enable personalization and memory features.

## Problem Statement

Currently, the MUXI Framework uses a default user ID of 0 when no explicit user ID is provided. This approach:

1. Prevents proper personalization when user ID isn't explicitly passed
2. Limits the use of key features like automatic context extraction and long-term memory for anonymous sessions
3. Creates a shared context for all anonymous users, potentially causing privacy concerns
4. Doesn't take advantage of interface-specific identifiers that could differentiate users

## Solution: Interface-Level User ID Generation

We will implement an automatic user ID generation system at each interface level that:

1. Creates persistent, unique user IDs based on available client information
2. Uses different strategies depending on interface type (REST API, WebSocket, CLI)
3. Maintains consistent user identity across multiple sessions when possible
4. Provides fallback mechanisms when ideal identification isn't available
5. Allows explicit overriding with developer-provided user IDs

## Goals and Non-Goals

### Goals

- Create interface-specific user ID generation strategies
- Support persistent identification across sessions when possible
- Make memory features available to all users, even without explicit IDs
- Prevent the mixing of user data in shared context
- Enable developers to override automatic IDs when needed

### Non-Goals

- Implement full user authentication/authorization (separate concern)
- Build complex user profiling or tracking
- Create a single universal identification strategy across all interfaces
- Persist user IDs between different interface types (e.g., WebSocket vs REST)

## Implementation Plan

### 1. Core Components

#### UserIdentifier Interface

We will create a standard interface that each implementation must follow:

```python
class UserIdentifier:
    """Interface for user identification strategies."""

    async def get_user_id(self, request_or_context):
        """
        Generate or retrieve a user ID based on request information.

        Args:
            request_or_context: Interface-specific request/context object

        Returns:
            int: A unique user ID (non-zero)
        """
        raise NotImplementedError()
```

#### REST API Implementation

For HTTP/REST API interfaces:

```python
class RestUserIdentifier(UserIdentifier):
    """User identification for REST API."""

    def __init__(self, session_cookie_name="muxi_session"):
        self.session_cookie_name = session_cookie_name
        self.session_secret = os.getenv("SESSION_SECRET", "muxi_default_secret")

    async def get_user_id(self, request):
        """Generate user ID from HTTP request."""
        # Priority 1: Check header for explicit ID
        explicit_id = request.headers.get("X-User-ID")
        if explicit_id and explicit_id.isdigit() and int(explicit_id) > 0:
            return int(explicit_id)

        # Priority 2: Check for session cookie
        session_id = request.cookies.get(self.session_cookie_name)
        if session_id:
            # Validate and extract user ID from session
            try:
                decoded = jwt.decode(
                    session_id,
                    self.session_secret,
                    algorithms=["HS256"]
                )
                if "user_id" in decoded and decoded["user_id"] > 0:
                    return decoded["user_id"]
            except:
                # Invalid session, will create new one
                pass

        # Priority 3: Generate ID based on client fingerprint
        fingerprint = self._generate_fingerprint(request)

        # Create new session
        user_id = self._hash_to_int(fingerprint)

        # Set session cookie in response
        response = request.context.get("response")
        if response:
            session_data = {
                "user_id": user_id,
                "created": int(time.time()),
                "exp": int(time.time() + 30 * 24 * 60 * 60)  # 30 days
            }
            session_token = jwt.encode(
                session_data,
                self.session_secret,
                algorithm="HS256"
            )
            response.set_cookie(
                self.session_cookie_name,
                session_token,
                httponly=True,
                max_age=30 * 24 * 60 * 60,
                samesite="lax"
            )

        return user_id

    def _generate_fingerprint(self, request):
        """Generate a unique fingerprint from request data."""
        components = [
            request.client.host if hasattr(request.client, "host") else "unknown",
            request.headers.get("user-agent", "unknown"),
            # Add other identifying factors that don't change often
        ]
        return "|".join(components)

    def _hash_to_int(self, data):
        """Convert hash to integer ID (non-zero)."""
        hash_value = int(hashlib.sha256(data.encode()).hexdigest(), 16) % (2**31 - 1)
        return max(1, hash_value)  # Ensure never returns 0
```

#### WebSocket Implementation

For WebSocket connections:

```python
class WebSocketUserIdentifier(UserIdentifier):
    """User identification for WebSocket connections."""

    def __init__(self):
        self.session_secret = os.getenv("SESSION_SECRET", "muxi_default_secret")

    async def get_user_id(self, websocket):
        """Generate user ID from WebSocket connection."""
        # Priority 1: Check query params for explicit ID
        query_params = websocket.query_params
        explicit_id = query_params.get("user_id")
        if explicit_id and explicit_id.isdigit() and int(explicit_id) > 0:
            return int(explicit_id)

        # Priority 2: Check headers/cookies (implementation depends on WS library)
        session_id = self._extract_session_cookie(websocket)
        if session_id:
            try:
                decoded = jwt.decode(
                    session_id,
                    self.session_secret,
                    algorithms=["HS256"]
                )
                if "user_id" in decoded and decoded["user_id"] > 0:
                    return decoded["user_id"]
            except:
                pass

        # Priority 3: Generate ID based on connection info
        fingerprint = self._generate_fingerprint(websocket)
        return self._hash_to_int(fingerprint)

    def _extract_session_cookie(self, websocket):
        """Extract session cookie from websocket headers."""
        # Implementation depends on WebSocket library used
        # Example for FastAPI/Starlette:
        cookies = websocket.headers.get("cookie", "")
        for cookie in cookies.split(";"):
            if cookie.strip().startswith("muxi_session="):
                return cookie.split("=", 1)[1].strip()
        return None

    def _generate_fingerprint(self, websocket):
        """Generate a unique fingerprint from WebSocket connection."""
        components = [
            websocket.client.host if hasattr(websocket.client, "host") else "unknown",
            websocket.headers.get("user-agent", "unknown"),
        ]
        return "|".join(components)

    def _hash_to_int(self, data):
        """Convert hash to integer ID (non-zero)."""
        hash_value = int(hashlib.sha256(data.encode()).hexdigest(), 16) % (2**31 - 1)
        return max(1, hash_value)  # Ensure never returns 0
```

#### CLI Implementation

For Command Line Interface:

```python
class CLIUserIdentifier(UserIdentifier):
    """User identification for CLI applications."""

    def __init__(self, storage_path=None):
        # Store user ID in local file
        self.storage_path = storage_path or os.path.expanduser("~/.muxi/user_id")

    async def get_user_id(self, context=None):
        """Generate or retrieve user ID for CLI."""
        # Create directory if needed
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)

        # Check for existing ID
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, "r") as f:
                    stored_id = int(f.read().strip())
                    if stored_id > 0:
                        return stored_id
            except:
                # Fall through to generate new ID if reading fails
                pass

        # Generate new ID based on system info
        user_id = self._generate_system_based_id()

        # Store for future use
        try:
            with open(self.storage_path, "w") as f:
                f.write(str(user_id))
        except:
            # If writing fails, still return the ID
            pass

        return user_id

    def _generate_system_based_id(self):
        """Generate ID based on system information."""
        components = [
            platform.node(),  # Computer network name
            getpass.getuser(),  # Username
            str(uuid.getnode()),  # MAC address as integer
        ]
        fingerprint = "|".join(components)

        # Generate consistent hash
        hash_val = int(hashlib.sha256(fingerprint.encode()).hexdigest(), 16) % (2**31 - 1)
        return max(1, hash_val)  # Ensure never zero
```

### 2. Integration with Interface Handlers

#### REST API Integration

Update the REST API router:

```python
class MuxiAPIRouter:
    def __init__(self, orchestrator, config=None):
        self.orchestrator = orchestrator
        self.config = config or {}
        self.user_identifier = RestUserIdentifier(
            session_cookie_name=self.config.get("session_cookie_name", "muxi_session")
        )

    async def chat_endpoint(self, request):
        """Handle chat requests."""
        # Generate or retrieve user ID
        user_id = await self.user_identifier.get_user_id(request)

        # Extract request data
        data = await request.json()
        message = data.get("message")
        agent_id = data.get("agent_id", "default")

        # Get agent
        agent = self.orchestrator.get_agent(agent_id)

        # Process message with proper user ID
        response = await agent.process_message(message, user_id=user_id)

        return {"response": response.content}

    # Other endpoints with similar pattern...
```

#### WebSocket Integration

Update the WebSocket handler:

```python
class MuxiWebSocketHandler:
    def __init__(self, orchestrator, config=None):
        self.orchestrator = orchestrator
        self.config = config or {}
        self.user_identifier = WebSocketUserIdentifier()

    async def handle_connection(self, websocket):
        """Handle WebSocket connection."""
        # Generate or retrieve user ID
        user_id = await self.user_identifier.get_user_id(websocket)

        # Store user_id in connection context
        websocket.user_id = user_id

        await self._connection_handler(websocket)

    async def _connection_handler(self, websocket):
        """Process WebSocket messages."""
        try:
            async for message in websocket:
                # Parse message
                data = json.loads(message)

                # Get agent
                agent_id = data.get("agent_id", "default")
                agent = self.orchestrator.get_agent(agent_id)

                # Process with proper user ID
                response = await agent.process_message(
                    data.get("message"),
                    user_id=websocket.user_id
                )

                # Send response
                await websocket.send(json.dumps({
                    "response": response.content
                }))
        except Exception as e:
            # Handle errors
            pass
```

### 3. Long-Term Memory Integration

Ensure that the long-term memory systems check the user ID before storing or retrieving information:

```python
class LongTermMemory:
    # Existing implementation...

    async def store(self, data, user_id=None, **kwargs):
        """Store information in long-term memory."""
        # Skip storage for anonymous/system user
        if user_id == 0:
            return

        # Proceed with storage for identified users
        # Rest of implementation...

    async def retrieve(self, query, user_id=None, **kwargs):
        """Retrieve information from long-term memory."""
        # For anonymous/system user, return empty results
        if user_id == 0:
            return []

        # Proceed with retrieval for identified users
        # Rest of implementation...
```

### 4. Configuration Options

Update the main MUXI facade to support configuring user identification:

```python
def muxi(
    buffer_memory=None,
    long_term_memory=None,
    is_multi_user=False,
    auto_extract_context=False,
    extraction_model=None,
    extraction_confidence=0.7,
    extraction_interval=1,
    user_id_config=None,  # New configuration parameter
    # Other existing parameters...
):
    """Initialize the MUXI Framework."""
    # User ID configuration defaults
    user_id_config = user_id_config or {}

    # Create orchestrator
    orchestrator = Orchestrator(
        buffer_memory=buffer_memory,
        long_term_memory=long_term_memory,
        is_multi_user=is_multi_user,
        auto_extract_context=auto_extract_context,
        extraction_model=extraction_model,
        extraction_confidence=extraction_confidence,
        extraction_interval=extraction_interval,
    )

    # Create facade with config
    facade = MuxiFacade(orchestrator)

    # Configure API with user ID settings if needed
    if hasattr(facade, "configure_api"):
        facade.configure_api(user_id_config=user_id_config)

    # Rest of implementation...

    return facade
```

## Usage Examples

### Basic REST API with Session-Based User IDs

```python
from muxi import muxi
import os

# Initialize MUXI with automatic user ID generation
app = muxi(
    buffer_memory=100,
    long_term_memory="sqlite:///memory.db",
    is_multi_user=True,
    auto_extract_context=True,
    user_id_config={
        "session_cookie_name": "my_app_session",
        "session_max_age": 90 * 24 * 60 * 60,  # 90 days
    }
)

# Add an agent
app.add_agent(
    agent_id="assistant",
    model={
        "provider": "openai",
        "model": "gpt-4o",
        "api_key": os.getenv("OPENAI_API_KEY")
    }
)

# Create FastAPI app
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware

api_app = FastAPI()

# Configure CORS
api_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@api_app.post("/chat")
async def chat(request: Request):
    # Response object needed for setting cookies
    response = Response()
    request.context = {"response": response}

    # Process request (user ID is automatically handled)
    result = await app.api_router.chat_endpoint(request)

    # Return response with content and any cookies set by user ID system
    return response.body(result)
```

### WebSocket with Auth Token

```python
from muxi import muxi
import os

# Initialize MUXI
app = muxi(
    buffer_memory=100,
    long_term_memory="postgresql://user:pass@localhost:5432/db",
    is_multi_user=True,
    auto_extract_context=True,
)

# Add agent
app.add_agent(
    agent_id="assistant",
    model={
        "provider": "anthropic",
        "model": "claude-3-opus-20240229",
        "api_key": os.getenv("ANTHROPIC_API_KEY")
    }
)

# Setup WebSocket server
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import uvicorn

ws_app = FastAPI()

@ws_app.websocket("/chat/{agent_id}")
async def websocket_endpoint(websocket: WebSocket, agent_id: str):
    await websocket.accept()

    # User ID will be automatically generated or retrieved
    # from query parameters, cookies, or connection fingerprint
    await app.ws_handler.handle_connection(websocket)
```

### CLI Application with System-Based ID

```python
from muxi import muxi
import os
import asyncio

# Initialize MUXI for CLI
app = muxi(
    buffer_memory=100,
    long_term_memory="sqlite:///memory.db",
    is_multi_user=True,
    auto_extract_context=True,
    user_id_config={
        "cli_storage_path": "~/.config/my_cli_app/user_id"
    }
)

# Add agent
app.add_agent(
    agent_id="assistant",
    model={
        "provider": "openai",
        "model": "gpt-3.5-turbo",
        "api_key": os.getenv("OPENAI_API_KEY")
    }
)

# Simple CLI
async def main():
    # Get CLI agent
    agent = app.get_agent("assistant")

    # CLI handler will automatically generate and use consistent user ID
    user_id = await app.cli_handler.user_identifier.get_user_id()

    print("Welcome to MUXI CLI!")

    while True:
        message = input("> ")
        if message.lower() in ["exit", "quit"]:
            break

        response = await agent.process_message(message, user_id=user_id)
        print(f"\n{response.content}\n")

if __name__ == "__main__":
    asyncio.run(main())
```

## Technical Considerations

### 1. Privacy and Security

- **Data Isolation**: Ensure complete isolation between different users
- **Session Security**: Use secure, HTTP-only cookies with appropriate SameSite policy
- **Client Fingerprinting**: Only use stable, non-privacy-invasive properties for fingerprinting
- **Transparency**: Make it clear to users how/why identification happens

### 2. Persistence Considerations

- **Session Duration**: Configure appropriate session lifetimes
- **Stable Fingerprinting**: Use attributes unlikely to change frequently
- **Graceful Degradation**: Have fallback strategies when ideal identifiers aren't available

### 3. Multi-Environment Support

- **Interface-Specific**: Each interface type needs a specific implementation
- **Framework Agnostic**: Support various web frameworks (FastAPI, Flask, Django)
- **CLI Flexibility**: Support different CLI environments

### 4. Rate Limiting and Abuse Prevention

- **Interface-Level Limits**: Implement per-user rate limiting based on generated IDs
- **Anti-Abuse**: Detect and prevent abuse of the identification system

## Implementation Timeline

1. **Phase 1: Core Interface Implementations** (2-3 days)
   - Implement the UserIdentifier interface
   - Create REST API identifier implementation
   - Create WebSocket identifier implementation
   - Create CLI identifier implementation
   - Add basic tests

2. **Phase 2: Integration** (2-3 days)
   - Integrate with existing interface handlers
   - Update long-term memory systems
   - Add configuration options
   - Test end-to-end flows

3. **Phase 3: Documentation & Examples** (1-2 days)
   - Update documentation
   - Create usage examples
   - Add best practices guide

## Success Metrics

- **Consistency**: 95%+ consistent identification across sessions for the same user
- **Uniqueness**: Less than 0.1% collision rate between different users
- **Performance**: Less than 5ms overhead for ID generation/lookup
- **Seamless**: Developers not explicitly setting user IDs should see memory features working automatically

## API Reference

### Configuration Options

```python
user_id_config = {
    # REST API settings
    "session_cookie_name": "muxi_session",  # Name of session cookie
    "session_max_age": 30 * 24 * 60 * 60,   # Session lifetime in seconds
    "session_secret": "your-secret",         # Secret for signing session tokens

    # CLI settings
    "cli_storage_path": "~/.muxi/user_id",   # Where to store CLI user ID

    # General settings
    "disable_fingerprinting": False,         # Disable fingerprinting fallback
}
```

## Future Enhancements

1. **Cross-Interface Identity**: Link identities across different interfaces
2. **Anonymous Mode**: Explicit setting to use user_id=0 and disable tracking
3. **OAuth Integration**: Connect with OAuth providers for more stable identification
4. **Identification Quality Metrics**: Score confidence in user identification
5. **Progressive Enhancement**: Start with generic ID, refine as more information becomes available
6. **Privacy Controls**: Allow users to reset or clear their generated ID

## Conclusion

Interface-level user ID generation ensures MUXI can provide personalized experiences and utilize memory features without requiring developers to explicitly generate and track user IDs. This system strikes a balance between seamless developer experience, appropriate privacy considerations, and enabling the framework's full personalization capabilities.

The implementation focuses on flexible, interface-specific strategies that work within the constraints of each environment while maintaining consistent user experiences.
