# WebSocket Communication

WebSockets provide real-time, bidirectional communication between clients and the AI Agent Framework. This guide explains how to implement, use, and troubleshoot WebSocket connections for interactive agent communication.

## What is WebSocket Support?

WebSocket support in the AI Agent Framework:
- Enables real-time communication with agents
- Provides immediate responses as they're generated
- Supports subscription to specific agents
- Allows for streaming responses from LLMs
- Facilitates tool execution updates

## Server-side Implementation

### Basic WebSocket Server

The framework includes a WebSocket server implementation:

```python
# src/api/websocket.py
import asyncio
import json
import logging
from fastapi import WebSocket, WebSocketDisconnect
from src.core.orchestrator import Orchestrator

logger = logging.getLogger(__name__)

# Shared orchestrator instance
_orchestrator = None

def set_orchestrator(orchestrator):
    """Set the shared orchestrator instance."""
    global _orchestrator
    _orchestrator = orchestrator

def get_orchestrator():
    """Get the shared orchestrator instance."""
    global _orchestrator
    return _orchestrator

class WebSocketManager:
    def __init__(self):
        self.active_connections = {}
        self.agent_subscribers = {}

    async def connect(self, websocket: WebSocket, client_id: str):
        """Connect a new client."""
        await websocket.accept()
        self.active_connections[client_id] = websocket
        logger.info(f"Client {client_id} connected")

        # Send connection confirmation
        await self.send_json(websocket, {
            "type": "connected",
            "client_id": client_id
        })

    def disconnect(self, client_id: str):
        """Disconnect a client."""
        if client_id in self.active_connections:
            del self.active_connections[client_id]

        # Remove client from agent subscriptions
        for agent_id in list(self.agent_subscribers.keys()):
            if client_id in self.agent_subscribers[agent_id]:
                self.agent_subscribers[agent_id].remove(client_id)

            # Clean up empty agent subscriptions
            if not self.agent_subscribers[agent_id]:
                del self.agent_subscribers[agent_id]

        logger.info(f"Client {client_id} disconnected")

    async def send_json(self, websocket: WebSocket, data: dict):
        """Send JSON data to a websocket."""
        try:
            await websocket.send_json(data)
        except Exception as e:
            logger.error(f"Error sending message: {str(e)}")

    async def broadcast_to_agent_subscribers(self, agent_id: str, message: dict):
        """Send a message to all subscribers of an agent."""
        if agent_id not in self.agent_subscribers:
            return

        for client_id in self.agent_subscribers[agent_id]:
            if client_id in self.active_connections:
                await self.send_json(self.active_connections[client_id], message)

    async def subscribe_to_agent(self, client_id: str, agent_id: str):
        """Subscribe a client to an agent's messages."""
        # Initialize agent subscribers list if needed
        if agent_id not in self.agent_subscribers:
            self.agent_subscribers[agent_id] = set()

        # Add client to subscribers
        self.agent_subscribers[agent_id].add(client_id)

        # Get the client's websocket
        websocket = self.active_connections.get(client_id)
        if websocket:
            # Confirm subscription
            await self.send_json(websocket, {
                "type": "subscribed",
                "agent_id": agent_id
            })

        logger.info(f"Client {client_id} subscribed to agent {agent_id}")

# Create a singleton manager
manager = WebSocketManager()

async def websocket_endpoint(websocket: WebSocket, client_id: str = None):
    """Handle WebSocket connections."""
    if client_id is None:
        client_id = f"client_{id(websocket)}"

    await manager.connect(websocket, client_id)

    try:
        while True:
            # Receive and parse message
            data = await websocket.receive_json()
            message_type = data.get("type")

            if message_type == "ping":
                # Respond to ping with pong
                await manager.send_json(websocket, {"type": "ping"})

            elif message_type == "subscribe":
                # Subscribe to an agent
                agent_id = data.get("agent_id")
                if not agent_id:
                    await manager.send_json(websocket, {
                        "type": "error",
                        "message": "No agent_id provided for subscription"
                    })
                    continue

                # Check if agent exists
                orchestrator = get_orchestrator()
                if orchestrator and not orchestrator.has_agent(agent_id):
                    await manager.send_json(websocket, {
                        "type": "error",
                        "message": f"No agent with ID '{agent_id}' exists"
                    })
                    continue

                # Subscribe to the agent
                await manager.subscribe_to_agent(client_id, agent_id)

            elif message_type == "chat":
                # Process a chat message
                agent_id = data.get("agent_id")
                message = data.get("message")

                if not message:
                    await manager.send_json(websocket, {
                        "type": "error",
                        "message": "No message provided"
                    })
                    continue

                # Get the orchestrator
                orchestrator = get_orchestrator()
                if not orchestrator:
                    await manager.send_json(websocket, {
                        "type": "error",
                        "message": "Orchestrator not available"
                    })
                    continue

                # Notify that processing has started
                await manager.send_json(websocket, {
                    "type": "agent_thinking",
                    "agent_id": agent_id
                })

                try:
                    # Process the message
                    response = await orchestrator.run(agent_id, message)

                    # Send the response
                    await manager.send_json(websocket, {
                        "type": "response",
                        "agent_id": agent_id,
                        "message": response
                    })

                    # Notify that processing is complete
                    await manager.send_json(websocket, {
                        "type": "agent_done",
                        "agent_id": agent_id
                    })
                except Exception as e:
                    logger.error(f"Error processing message: {str(e)}")
                    await manager.send_json(websocket, {
                        "type": "error",
                        "message": f"Error processing message: {str(e)}"
                    })

            else:
                # Unknown message type
                await manager.send_json(websocket, {
                    "type": "error",
                    "message": f"Unknown message type: {message_type}"
                })

    except WebSocketDisconnect:
        manager.disconnect(client_id)

    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
        manager.disconnect(client_id)
```

### Integrating with FastAPI

To integrate the WebSocket server with FastAPI:

```python
# src/api/app.py
from fastapi import FastAPI, WebSocket, Depends
import uuid
from src.core.orchestrator import Orchestrator
from src.api.websocket import websocket_endpoint, set_orchestrator

app = FastAPI(title="AI Agent Framework API")

# Create orchestrator
orchestrator = Orchestrator()

# Share orchestrator with websocket module
set_orchestrator(orchestrator)

# Define WebSocket endpoint
@app.websocket("/ws")
async def websocket_route(websocket: WebSocket):
    client_id = str(uuid.uuid4())
    await websocket_endpoint(websocket, client_id)
```

## Client-side Implementation

### JavaScript Client

Here's a basic JavaScript WebSocket client:

```javascript
class AgentWebSocketClient {
    constructor(url = 'ws://localhost:5050/ws') {
        this.url = url;
        this.socket = null;
        this.connected = false;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectDelay = 1000;
        this.messageCallbacks = {
            'connected': [],
            'subscribed': [],
            'response': [],
            'agent_thinking': [],
            'agent_done': [],
            'error': [],
            'ping': []
        };

        this.connectSocket();
    }

    connectSocket() {
        this.socket = new WebSocket(this.url);

        this.socket.onopen = () => {
            console.log('WebSocket connected');
            this.connected = true;
            this.reconnectAttempts = 0;

            // Start ping interval to keep connection alive
            this.pingInterval = setInterval(() => {
                if (this.connected) {
                    this.sendPing();
                }
            }, 30000);
        };

        this.socket.onmessage = (event) => {
            const data = JSON.parse(event.data);
            console.log('Received:', data);

            // Call registered callbacks for this message type
            if (data.type && this.messageCallbacks[data.type]) {
                this.messageCallbacks[data.type].forEach(callback => {
                    try {
                        callback(data);
                    } catch (e) {
                        console.error('Error in callback:', e);
                    }
                });
            }
        };

        this.socket.onclose = (event) => {
            this.connected = false;
            clearInterval(this.pingInterval);
            console.log('WebSocket disconnected:', event.code, event.reason);

            // Attempt to reconnect
            if (this.reconnectAttempts < this.maxReconnectAttempts) {
                this.reconnectAttempts++;
                const delay = this.reconnectDelay * this.reconnectAttempts;
                console.log(`Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts})...`);

                setTimeout(() => {
                    this.connectSocket();
                }, delay);
            } else {
                console.error('Max reconnect attempts reached');
            }
        };

        this.socket.onerror = (error) => {
            console.error('WebSocket error:', error);
        };
    }

    sendMessage(data) {
        if (!this.connected) {
            console.error('Cannot send message: WebSocket not connected');
            return false;
        }

        try {
            this.socket.send(JSON.stringify(data));
            return true;
        } catch (e) {
            console.error('Error sending message:', e);
            return false;
        }
    }

    sendPing() {
        return this.sendMessage({ type: 'ping' });
    }

    subscribeToAgent(agentId) {
        return this.sendMessage({
            type: 'subscribe',
            agent_id: agentId
        });
    }

    sendChatMessage(agentId, message) {
        return this.sendMessage({
            type: 'chat',
            agent_id: agentId,
            message: message
        });
    }

    on(messageType, callback) {
        if (!this.messageCallbacks[messageType]) {
            this.messageCallbacks[messageType] = [];
        }

        this.messageCallbacks[messageType].push(callback);
        return this;
    }

    close() {
        if (this.socket) {
            clearInterval(this.pingInterval);
            this.socket.close();
        }
    }
}

// Usage example
const client = new AgentWebSocketClient('ws://localhost:5050/ws');

client
    .on('connected', (data) => {
        console.log('Connected with client ID:', data.client_id);
        client.subscribeToAgent('my_agent');
    })
    .on('subscribed', (data) => {
        console.log('Subscribed to agent:', data.agent_id);
        client.sendChatMessage('my_agent', 'Hello, agent!');
    })
    .on('agent_thinking', (data) => {
        console.log('Agent is thinking...');
    })
    .on('response', (data) => {
        console.log('Agent response:', data.message);
    })
    .on('agent_done', (data) => {
        console.log('Agent completed processing');
    })
    .on('error', (data) => {
        console.error('Error:', data.message);
    });
```

### Python Client

Here's a Python WebSocket client using `websockets`:

```python
import asyncio
import json
import uuid
import websockets
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AgentWebSocketClient:
    def __init__(self, url="ws://localhost:5050/ws"):
        self.url = url
        self.connected = False
        self.websocket = None
        self.client_id = str(uuid.uuid4())
        self.current_agent_id = None
        self.reconnect_attempts = 0
        self.max_reconnect_attempts = 5
        self.callbacks = {
            "connected": [],
            "subscribed": [],
            "response": [],
            "agent_thinking": [],
            "agent_done": [],
            "error": [],
            "ping": []
        }

    async def connect(self):
        """Connect to the WebSocket server."""
        try:
            self.websocket = await websockets.connect(self.url)
            self.connected = True
            logger.info("Connected to WebSocket server")

            # Start listener
            asyncio.create_task(self._listen())

            return True
        except Exception as e:
            logger.error(f"Connection error: {str(e)}")
            return False

    async def _listen(self):
        """Listen for messages from the server."""
        try:
            while self.connected:
                try:
                    message = await self.websocket.recv()
                    data = json.loads(message)
                    logger.debug(f"Received: {data}")

                    # Execute callbacks for this message type
                    message_type = data.get("type")
                    if message_type in self.callbacks:
                        for callback in self.callbacks[message_type]:
                            try:
                                await callback(data)
                            except Exception as e:
                                logger.error(f"Error in callback: {str(e)}")
                except websockets.ConnectionClosed:
                    logger.warning("Connection closed")
                    self.connected = False
                    await self._try_reconnect()
                    break
        except Exception as e:
            logger.error(f"Listener error: {str(e)}")
            self.connected = False

    async def _try_reconnect(self):
        """Try to reconnect to the server."""
        if self.reconnect_attempts >= self.max_reconnect_attempts:
            logger.error("Max reconnect attempts reached")
            return False

        self.reconnect_attempts += 1
        delay = 1 * self.reconnect_attempts
        logger.info(f"Reconnecting in {delay}s (attempt {self.reconnect_attempts}/{self.max_reconnect_attempts})...")

        await asyncio.sleep(delay)

        success = await self.connect()
        if success and self.current_agent_id:
            # Resubscribe to the previous agent
            await self.subscribe_to_agent(self.current_agent_id)

        return success

    async def send_json(self, data):
        """Send JSON data to the server."""
        if not self.connected:
            logger.error("Cannot send message: not connected")
            return False

        try:
            await self.websocket.send(json.dumps(data))
            return True
        except Exception as e:
            logger.error(f"Send error: {str(e)}")
            self.connected = False
            return False

    async def send_ping(self):
        """Send a ping message to keep the connection alive."""
        return await self.send_json({"type": "ping"})

    async def subscribe_to_agent(self, agent_id):
        """Subscribe to an agent's messages."""
        self.current_agent_id = agent_id
        return await self.send_json({
            "type": "subscribe",
            "agent_id": agent_id
        })

    async def send_chat_message(self, message, agent_id=None):
        """Send a chat message to an agent."""
        if not agent_id and not self.current_agent_id:
            logger.error("No agent ID specified")
            return False

        return await self.send_json({
            "type": "chat",
            "agent_id": agent_id or self.current_agent_id,
            "message": message
        })

    def on(self, message_type, callback):
        """Register a callback for a message type."""
        if message_type in self.callbacks:
            self.callbacks[message_type].append(callback)
        return self

    async def close(self):
        """Close the WebSocket connection."""
        if self.websocket:
            await self.websocket.close()
            self.connected = False
            logger.info("Connection closed")

# Usage example
async def main():
    client = AgentWebSocketClient()

    # Register callbacks
    client.on("connected", lambda data: logger.info(f"Connected with client ID: {data.get('client_id')}"))
    client.on("subscribed", lambda data: logger.info(f"Subscribed to agent: {data.get('agent_id')}"))
    client.on("response", lambda data: logger.info(f"Agent response: {data.get('message')}"))
    client.on("error", lambda data: logger.error(f"Error: {data.get('message')}"))

    # Define chat callback
    async def on_response(data):
        print(f"\nAgent: {data.get('message')}\n")

    client.on("response", on_response)

    # Connect and subscribe
    await client.connect()
    await client.subscribe_to_agent("my_agent")

    # Chat loop
    try:
        while True:
            message = input("\nYou: ")
            if message.lower() in ["exit", "quit", "bye"]:
                break

            await client.send_chat_message(message)
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(main())
```

## Message Types

The WebSocket protocol supports several message types:

### Client to Server

1. **subscribe**
   - Subscribe to an agent's messages
   - Parameters: `agent_id`

   ```json
   {
     "type": "subscribe",
     "agent_id": "my_agent"
   }
   ```

2. **chat**
   - Send a message to an agent
   - Parameters: `agent_id`, `message`

   ```json
   {
     "type": "chat",
     "agent_id": "my_agent",
     "message": "What's the weather like today?"
   }
   ```

3. **ping**
   - Keep the connection alive
   - No additional parameters

   ```json
   {
     "type": "ping"
   }
   ```

### Server to Client

1. **connected**
   - Confirms successful connection establishment
   - Parameters: `client_id`

   ```json
   {
     "type": "connected",
     "client_id": "client_123"
   }
   ```

2. **subscribed**
   - Confirms successful agent subscription
   - Parameters: `agent_id`

   ```json
   {
     "type": "subscribed",
     "agent_id": "my_agent"
   }
   ```

3. **response**
   - A response from an agent
   - Parameters: `agent_id`, `message`

   ```json
   {
     "type": "response",
     "agent_id": "my_agent",
     "message": "The weather in New York is sunny today."
   }
   ```

4. **agent_thinking**
   - Indicates the agent is processing
   - Parameters: `agent_id`

   ```json
   {
     "type": "agent_thinking",
     "agent_id": "my_agent"
   }
   ```

5. **agent_done**
   - Indicates the agent has finished processing
   - Parameters: `agent_id`

   ```json
   {
     "type": "agent_done",
     "agent_id": "my_agent"
   }
   ```

6. **error**
   - An error message
   - Parameters: `message`

   ```json
   {
     "type": "error",
     "message": "No agent with ID 'unknown_agent' exists"
   }
   ```

7. **ping**
   - Heartbeat to keep the connection alive
   - No additional parameters

   ```json
   {
     "type": "ping"
   }
   ```

## Advanced WebSocket Features

### Streaming Responses

To implement streaming responses from LLMs:

```python
# Server-side implementation
async def handle_chat_message(client_id, agent_id, message):
    """Handle a chat message with streaming response."""
    orchestrator = get_orchestrator()
    if not orchestrator:
        await manager.send_json(
            manager.active_connections[client_id],
            {"type": "error", "message": "Orchestrator not available"}
        )
        return

    # Notify that processing has started
    await manager.send_json(
        manager.active_connections[client_id],
        {"type": "agent_thinking", "agent_id": agent_id}
    )

    try:
        # Process the message with streaming
        async for chunk in orchestrator.run_stream(agent_id, message):
            await manager.send_json(
                manager.active_connections[client_id],
                {
                    "type": "stream_chunk",
                    "agent_id": agent_id,
                    "chunk": chunk,
                    "done": False
                }
            )

        # Signal completion
        await manager.send_json(
            manager.active_connections[client_id],
            {
                "type": "stream_chunk",
                "agent_id": agent_id,
                "chunk": "",
                "done": True
            }
        )

        # Notify that processing is complete
        await manager.send_json(
            manager.active_connections[client_id],
            {"type": "agent_done", "agent_id": agent_id}
        )
    except Exception as e:
        logger.error(f"Error processing message: {str(e)}")
        await manager.send_json(
            manager.active_connections[client_id],
            {"type": "error", "message": f"Error processing message: {str(e)}"}
        )
```

### Tool Execution Status Updates

To provide updates during tool execution:

```python
# Tool execution callback
async def tool_callback(agent_id, tool_name, status, result=None):
    """Callback for tool execution updates."""
    message = {
        "type": "tool_update",
        "agent_id": agent_id,
        "tool_name": tool_name,
        "status": status
    }

    if result is not None:
        message["result"] = result

    await manager.broadcast_to_agent_subscribers(agent_id, message)

# Register callback with the orchestrator
orchestrator.set_tool_callback(tool_callback)
```

### Session Management

To manage user sessions and conversation history:

```python
class SessionManager:
    def __init__(self):
        self.sessions = {}

    def create_session(self, session_id, user_id=None):
        """Create a new session."""
        if session_id not in self.sessions:
            self.sessions[session_id] = {
                "created_at": datetime.now(),
                "user_id": user_id,
                "last_active": datetime.now(),
                "messages": []
            }
        return self.sessions[session_id]

    def add_message(self, session_id, message):
        """Add a message to a session."""
        if session_id in self.sessions:
            self.sessions[session_id]["messages"].append({
                "timestamp": datetime.now(),
                "content": message
            })
            self.sessions[session_id]["last_active"] = datetime.now()

    def get_session(self, session_id):
        """Get a session by ID."""
        return self.sessions.get(session_id)

    def list_sessions(self, user_id=None):
        """List all sessions, optionally filtered by user ID."""
        if user_id:
            return {k: v for k, v in self.sessions.items() if v["user_id"] == user_id}
        return self.sessions

    def delete_session(self, session_id):
        """Delete a session."""
        if session_id in self.sessions:
            del self.sessions[session_id]
            return True
        return False

# Initialize session manager
session_manager = SessionManager()

# Use in WebSocket endpoint
@app.websocket("/ws/{session_id}")
async def websocket_session(websocket: WebSocket, session_id: str):
    client_id = str(uuid.uuid4())

    # Create or get session
    session = session_manager.create_session(session_id)

    # Handle the WebSocket connection
    await websocket_endpoint(websocket, client_id)
```

## Best Practices

1. **Error Handling**: Implement comprehensive error handling for all WebSocket operations

2. **Reconnection Logic**: Include automatic reconnection in clients to handle network interruptions

3. **Message Validation**: Validate all incoming messages before processing

4. **Connection Management**: Properly manage connection lifecycles to prevent resource leaks

5. **Load Balancing**: For production deployments, consider load balancing WebSocket connections

6. **Security**: Implement proper authentication and authorization for WebSocket connections

7. **Logging**: Add detailed logging for debugging connection issues

## Troubleshooting

### Connection Issues

- Check if the WebSocket server is running and accessible
- Verify network connectivity between client and server
- Ensure the correct WebSocket URL is being used
- Check for firewall or proxy settings that might block WebSocket connections

### Message Processing Errors

- Validate message format on both client and server
- Check for proper JSON formatting in messages
- Verify that required fields are present in messages
- Ensure agent IDs exist before attempting to subscribe or send messages

### Performance Issues

- Monitor WebSocket connection count and resource usage
- Implement connection limits to prevent server overload
- Consider using message queues for high-load scenarios
- Optimize message size and frequency

## Next Steps

After implementing WebSocket support, you might want to explore:

- Creating [agents](./agent.md) that can utilize WebSocket connections
- Setting up [tool systems](./tools.md) that send real-time progress updates
- Implementing [MCP features](./mcp.md) for structured communication
- Enhancing [memory systems](./memory.md) with real-time updates
