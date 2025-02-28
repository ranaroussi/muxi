"""
WebSocket module for real-time communication with AI agents.

This module provides WebSocket endpoints for real-time interaction with
agents created with the AI Agent Framework.
"""

import asyncio
import logging
import uuid
import json
import time
from typing import Dict, Set, Optional, Any

from fastapi import WebSocket, WebSocketDisconnect, FastAPI

from src.core.orchestrator import Orchestrator

# This will be set by register_websocket_routes
_orchestrator = None

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("websocket")


# Global connection tracking
connected_websockets: Dict[str, WebSocket] = {}
agent_connections: Dict[str, Set[str]] = {}
# Track last activity time for each connection
connection_last_activity: Dict[str, float] = {}
# Track user_id for each connection
connection_user_id: Dict[str, int] = {}


# Get agent function
async def get_agent(agent_id: str):
    """
    Get an agent from the orchestrator.
    This function should be implemented according to your agent system.
    """
    # Use the orchestrator passed from app.py
    if _orchestrator is None:
        raise RuntimeError("Orchestrator not initialized")
    return _orchestrator.get_agent(agent_id)


# Connection keepalive check
async def check_connection_timeouts():
    """
    Periodically check for timed out connections and clean them up.
    """
    while True:
        try:
            current_time = time.time()
            connections_to_close = []

            # Find connections that haven't had activity in 2 minutes
            for conn_id, last_activity in connection_last_activity.items():
                if current_time - last_activity > 120:  # 2 minutes timeout
                    logger.info(
                        f"Connection {conn_id} timed out after 2 minutes of inactivity"
                    )
                    connections_to_close.append(conn_id)

            # Close timed out connections
            for conn_id in connections_to_close:
                if conn_id in connected_websockets:
                    try:
                        await connected_websockets[conn_id].close(
                            code=1000,
                            reason="Connection timeout"
                        )
                    except Exception as e:
                        logger.error(
                            f"Error closing timed out connection {conn_id}: {str(e)}"
                        )

                    # Clean up connection tracking
                    del connected_websockets[conn_id]
                    del connection_last_activity[conn_id]

                    # Remove from agent connections
                    for agent_id, connections in agent_connections.items():
                        if conn_id in connections:
                            connections.remove(conn_id)
                            if not connections:
                                del agent_connections[agent_id]
                            break

            # Sleep for 30 seconds before checking again
            await asyncio.sleep(30)
        except Exception as e:
            logger.error(f"Error in connection timeout checker: {str(e)}")
            await asyncio.sleep(30)  # Sleep anyway to prevent tight loops on error


# Update the last activity time for a connection
def update_activity(connection_id: str):
    connection_last_activity[connection_id] = time.time()


# WebSocket connection handler
async def handle_websocket(websocket: WebSocket):
    """Handle WebSocket connections and messages."""
    connection_id = str(uuid.uuid4())

    try:
        # Accept the connection
        await websocket.accept()
        logger.info(f"WebSocket connection established: {connection_id}")

        # Add to connection tracking
        connected_websockets[connection_id] = websocket
        update_activity(connection_id)

        # Set default user_id
        connection_user_id[connection_id] = 0

        # First message should be a welcome message
        await websocket.send_json({
            "type": "connected",
            "connection_id": connection_id,
            "message": "Connected to AI Agent Framework"
        })

        # Process messages
        while True:
            # Wait for message
            message_text = await websocket.receive_text()
            update_activity(connection_id)

            try:
                # Parse message
                message = json.loads(message_text)
                message_type = message.get("type", "unknown")

                # Handle different message types
                if message_type == "ping":
                    # Ping message to keep connection alive
                    await websocket.send_json({
                        "type": "pong",
                        "timestamp": time.time()
                    })

                elif message_type == "set_user":
                    # Set user ID for this connection
                    user_id = message.get("user_id", 0)
                    connection_user_id[connection_id] = int(user_id)
                    logger.info(f"Set user ID for connection {connection_id}: {user_id}")
                    await websocket.send_json({
                        "type": "user_set",
                        "user_id": user_id
                    })

                elif message_type == "chat":
                    # Handle chat message
                    await handle_chat_message(
                        connection_id,
                        websocket,
                        message,
                        connection_user_id.get(connection_id, 0)
                    )

                elif message_type == "subscribe":
                    # Handle agent subscription
                    await handle_subscription(connection_id, websocket, message)

                elif message_type == "unsubscribe":
                    # Handle agent unsubscription
                    await handle_unsubscription(connection_id, websocket, message)

                elif message_type == "search_memory":
                    # Handle memory search
                    await handle_memory_search(
                        connection_id,
                        websocket,
                        message,
                        connection_user_id.get(connection_id, 0)
                    )

                else:
                    # Unknown message type
                    logger.warning(f"Unknown message type: {message_type}")
                    await websocket.send_json({
                        "type": "error",
                        "message": f"Unknown message type: {message_type}"
                    })

            except json.JSONDecodeError:
                # Invalid JSON
                logger.warning(f"Invalid JSON message: {message_text}")
                await websocket.send_json({
                    "type": "error",
                    "message": "Invalid JSON message"
                })

            except Exception as e:
                # Other errors
                logger.error(f"Error processing message: {str(e)}")
                await websocket.send_json({
                    "type": "error",
                    "message": f"Error processing message: {str(e)}"
                })

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected: {connection_id}")

    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
        try:
            await websocket.close(code=1011, reason=f"Internal error: {str(e)}")
        except:
            pass

    finally:
        # Clean up connection tracking
        if connection_id in connected_websockets:
            del connected_websockets[connection_id]

        if connection_id in connection_last_activity:
            del connection_last_activity[connection_id]

        if connection_id in connection_user_id:
            del connection_user_id[connection_id]

        # Remove from agent connections
        for agent_id, connections in list(agent_connections.items()):
            if connection_id in connections:
                connections.remove(connection_id)
                if not connections:
                    del agent_connections[agent_id]


def register_websocket_routes(app: FastAPI, orchestrator: Orchestrator):
    """
    Register WebSocket routes with the FastAPI application.

    Args:
        app: The FastAPI application
        orchestrator: The agent orchestrator
    """
    # Store the orchestrator reference globally
    global _orchestrator
    _orchestrator = orchestrator

    # Start the connection timeout checker task
    @app.on_event("startup")
    async def start_timeout_checker():
        asyncio.create_task(check_connection_timeouts())

    @app.websocket("/ws")
    async def websocket_endpoint(websocket: WebSocket):
        """
        WebSocket endpoint for real-time communication with agents.

        The client can send the following message types:
        - subscribe: Subscribe to an agent's messages
        - chat: Send a message to an agent
        - ping: Heartbeat to keep the connection alive

        The server will send the following message types:
        - response: A response from an agent
        - agent_thinking: Indicates an agent is processing
        - agent_done: Indicates an agent has finished processing
        - error: An error message
        - pong: Response to a ping
        - ping: Server-initiated heartbeat
        """
        await handle_websocket(websocket)


async def handle_chat_message(
    connection_id: str,
    websocket: WebSocket,
    message: Dict[str, Any],
    user_id: int = 0
):
    """Handle a chat message from a client."""
    agent_id = message.get("agent_id")
    content = message.get("message")

    logger.debug(
        f"handle_chat_message: connection_id={connection_id}, "
        f"agent_id={agent_id}, user_id={user_id}"
    )

    if not agent_id or not content:
        await websocket.send_json({
            "type": "error",
            "message": "Missing required fields: agent_id and message"
        })
        return

    try:
        # Get the agent
        agent = await get_agent(agent_id)
        if not agent:
            await websocket.send_json({
                "type": "error",
                "message": f"Agent '{agent_id}' not found"
            })
            return

        # Send thinking message
        await websocket.send_json({
            "type": "thinking",
            "agent_id": agent_id
        })

        # Process the message
        logger.debug(f"Calling agent.chat with user_id={user_id}")
        response = await agent.chat(content, user_id=user_id)

        # Send the response
        await websocket.send_json({
            "type": "message",
            "agent_id": agent_id,
            "user_id": user_id,
            "content": response,
            "timestamp": time.time()
        })

        # Broadcast to other connections subscribed to this agent
        if agent_id in agent_connections:
            for conn_id in agent_connections[agent_id]:
                if conn_id != connection_id and conn_id in connected_websockets:
                    try:
                        await connected_websockets[conn_id].send_json({
                            "type": "broadcast",
                            "agent_id": agent_id,
                            "user_id": user_id,
                            "message": content,
                            "response": response,
                            "timestamp": time.time()
                        })
                    except Exception as e:
                        logger.error(
                            f"Error broadcasting message to {conn_id}: {str(e)}"
                        )

    except Exception as e:
        logger.error(f"Error processing chat message: {str(e)}")
        await websocket.send_json({
            "type": "error",
            "message": f"Error processing message: {str(e)}"
        })


async def handle_memory_search(
    connection_id: str,
    websocket: WebSocket,
    message: Dict[str, Any],
    user_id: int = 0
):
    """Handle a memory search request from a client."""
    agent_id = message.get("agent_id")
    query = message.get("query")
    limit = message.get("limit", 5)
    use_long_term = message.get("use_long_term", True)

    logger.debug(
        f"handle_memory_search: connection_id={connection_id}, "
        f"agent_id={agent_id}, user_id={user_id}"
    )

    if not agent_id or not query:
        await websocket.send_json({
            "type": "error",
            "message": "Missing required fields: agent_id and query"
        })
        return

    try:
        # Get the agent
        agent = await get_agent(agent_id)
        if not agent:
            await websocket.send_json({
                "type": "error",
                "message": f"Agent '{agent_id}' not found"
            })
            return

        # Search memory
        logger.debug(f"Calling agent.search_memory with user_id={user_id}")
        memories = await agent.search_memory(
            query=query,
            k=limit,
            use_long_term=use_long_term,
            user_id=user_id
        )

        # Format the results
        formatted_results = []
        for memory in memories:
            # Handle different memory formats
            if "content" in memory:
                text = memory["content"]
            elif "text" in memory:
                text = memory["text"]
            else:
                text = str(memory)

            # Get metadata
            metadata = memory.get("metadata", {})

            # Get distance
            distance = memory.get("distance", 0.0)

            # Get source
            source = memory.get("source", "unknown")

            formatted_results.append({
                "text": text,
                "source": source,
                "distance": distance,
                "metadata": metadata
            })

        # Send the response
        await websocket.send_json({
            "type": "memory_results",
            "agent_id": agent_id,
            "user_id": user_id,
            "query": query,
            "results": formatted_results,
            "timestamp": time.time()
        })

    except Exception as e:
        logger.error(f"Error searching memory: {str(e)}")
        await websocket.send_json({
            "type": "error",
            "message": f"Error searching memory: {str(e)}"
        })


async def handle_subscription(
    connection_id: str,
    websocket: WebSocket,
    message: Dict[str, Any]
):
    """Handle a subscription request from a client."""
    agent_id = message.get("agent_id")

    if not agent_id:
        await websocket.send_json({
            "type": "error",
            "message": "Missing required field: agent_id"
        })
        return

    try:
        # Check if agent exists
        agent = await get_agent(agent_id)
        if not agent:
            await websocket.send_json({
                "type": "error",
                "message": f"Agent '{agent_id}' not found"
            })
            return

        # Add this connection to the agent's subscriptions
        if agent_id not in agent_connections:
            agent_connections[agent_id] = set()

        agent_connections[agent_id].add(connection_id)

        # Send confirmation
        await websocket.send_json({
            "type": "subscribed",
            "agent_id": agent_id,
            "message": f"Successfully subscribed to agent {agent_id}"
        })

        logger.info(f"Connection {connection_id} subscribed to agent {agent_id}")

    except Exception as e:
        logger.error(f"Error subscribing to agent: {str(e)}")
        await websocket.send_json({
            "type": "error",
            "message": f"Error subscribing to agent: {str(e)}"
        })


async def handle_unsubscription(
    connection_id: str,
    websocket: WebSocket,
    message: Dict[str, Any]
):
    """Handle an unsubscription request from a client."""
    agent_id = message.get("agent_id")

    if not agent_id:
        await websocket.send_json({
            "type": "error",
            "message": "Missing required field: agent_id"
        })
        return

    try:
        # Remove this connection from the agent's subscriptions
        if agent_id in agent_connections and connection_id in agent_connections[agent_id]:
            agent_connections[agent_id].remove(connection_id)

            # Clean up empty agent connections
            if not agent_connections[agent_id]:
                del agent_connections[agent_id]

            # Send confirmation
            await websocket.send_json({
                "type": "unsubscribed",
                "agent_id": agent_id,
                "message": f"Successfully unsubscribed from agent {agent_id}"
            })

            logger.info(
                f"Connection {connection_id} unsubscribed from agent {agent_id}"
            )
        else:
            await websocket.send_json({
                "type": "warning",
                "message": f"Not subscribed to agent {agent_id}"
            })

    except Exception as e:
        logger.error(f"Error unsubscribing from agent: {str(e)}")
        await websocket.send_json({
            "type": "error",
            "message": f"Error unsubscribing from agent: {str(e)}"
        })
