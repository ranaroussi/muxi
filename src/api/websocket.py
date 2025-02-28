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
from typing import Dict, Set

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
    await websocket.accept()
    connection_id = str(uuid.uuid4())
    # Add dict for tracking tool calls
    active_tool_calls = {}

    connected_websockets[connection_id] = websocket
    connection_last_activity[connection_id] = time.time()  # Initialize last activity time
    subscribed_agent = None

    logger.info(f"WebSocket connection established: {connection_id}")

    # Send welcome message with a small delay to prevent immediate client disconnects
    try:
        # Wait for 0.5 seconds before sending welcome message to give client time to stabilize
        await asyncio.sleep(0.5)

        # Send a welcome message to confirm connection is working properly
        # This is important for client-side validation that the connection succeeded
        await websocket.send_json({
            "type": "connected",
            "connection_id": connection_id,
            "message": "WebSocket connection established"
        })
        logger.info(f"Welcome message sent to {connection_id}")

        # Give a little more time for client to process the welcome message
        await asyncio.sleep(0.2)
    except Exception as e:
        logger.error(f"Error sending welcome message: {str(e)}")
        # If we can't send the welcome message, the connection might be bad
        # Try to close it and exit the handler
        try:
            await websocket.close(
                code=1011,
                reason="Failed to establish connection properly"
            )
        except Exception as e:
            logger.error(f"Error closing WebSocket after welcome message failure: {str(e)}")
        return

    try:
        while True:
            try:
                # Update last activity time
                update_activity(connection_id)

                # Receive message with a timeout
                message = await asyncio.wait_for(
                    websocket.receive_text(),
                    timeout=120  # 2 minute timeout
                )

                data = json.loads(message)
                message_type = data.get("type")
                logger.info(
                    f"Received message type: {message_type} from {connection_id}"
                )

                # Handle ping message for heartbeat
                if message_type == "ping":
                    # Immediately respond with a pong
                    try:
                        await websocket.send_json({
                            "type": "pong",
                            "timestamp": time.time()
                        })
                        logger.debug(f"Sent pong to {connection_id}")
                        continue
                    except Exception as e:
                        logger.error(f"Error sending pong: {str(e)}")
                        # If we can't send a pong, the connection might be bad
                        break

                if message_type == "subscribe":
                    agent_id = data.get("agent_id")
                    if not agent_id:
                        await websocket.send_json({
                            "type": "error",
                            "message": "No agent_id provided for subscription"
                        })
                        continue

                    try:
                        # Check if agent exists
                        agent = await get_agent(agent_id)
                        if not agent:
                            await websocket.send_json({
                                "type": "error",
                                "message": f"No agent with ID '{agent_id}' exists"
                            })
                            continue

                        # Subscribe to agent
                        subscribed_agent = agent_id
                        agent_connections[agent_id] = agent_connections.get(agent_id, set())
                        agent_connections[agent_id].add(connection_id)

                        await websocket.send_json({
                            "type": "subscribed",
                            "agent_id": agent_id,
                            "message": f"Successfully subscribed to agent: {agent_id}"
                        })
                        logger.info(f"Client {connection_id} subscribed to agent: {agent_id}")
                    except Exception as e:
                        logger.error(f"Error subscribing to agent: {str(e)}")
                        await websocket.send_json({
                            "type": "error",
                            "message": f"Error subscribing to agent: {str(e)}"
                        })

                elif message_type == "chat":
                    if not subscribed_agent:
                        await websocket.send_json({
                            "type": "error",
                            "message": "You must subscribe to an agent first"
                        })
                        continue

                    user_message = data.get("message")
                    tool_call_id = data.get("tool_call_id")

                    if not user_message:
                        await websocket.send_json({
                            "type": "error",
                            "message": "No message provided",
                            "tool_call_id": tool_call_id
                        })
                        continue

                    # Store the tool call ID to track it
                    if tool_call_id:
                        active_tool_calls[tool_call_id] = {
                            "timestamp": time.time(),
                            "message": user_message,
                            "agent_id": subscribed_agent
                        }

                    # Process the message
                    try:
                        await websocket.send_json({
                            "type": "agent_thinking",
                            "agent_id": subscribed_agent,
                            "tool_call_id": tool_call_id
                        })

                        # Get agent and process message
                        agent = await get_agent(subscribed_agent)
                        if not agent:
                            await websocket.send_json({
                                "type": "error",
                                "message": f"Agent '{subscribed_agent}' no longer exists",
                                "tool_call_id": tool_call_id
                            })
                            continue

                        # Initialize tools_used (we'll try to get this from agent later)
                        tools_used = []

                        # Process the message with the agent - remove the callback parameter
                        response = await agent.process_message(user_message)

                        # Convert MCPMessage to string if needed
                        response_content = str(response)
                        if hasattr(response, 'content'):
                            response_content = response.content
                        elif hasattr(response, 'message'):
                            response_content = response.message

                        # Remove from active calls if successful
                        if tool_call_id and tool_call_id in active_tool_calls:
                            del active_tool_calls[tool_call_id]

                        await websocket.send_json({
                            "type": "response",
                            "agent_id": subscribed_agent,
                            "message": response_content,  # Using the extracted content
                            "tools_used": tools_used,  # For now, this will be empty
                            "tool_call_id": tool_call_id
                        })

                        await websocket.send_json({
                            "type": "agent_done",
                            "agent_id": subscribed_agent,
                            "tool_call_id": tool_call_id
                        })

                    except Exception as e:
                        logger.error(f"Error processing message: {str(e)}")
                        await websocket.send_json({
                            "type": "error",
                            "message": f"Error processing message: {str(e)}",
                            "tool_call_id": tool_call_id
                        })

                        # Remove from active calls if error occurs
                        if tool_call_id and tool_call_id in active_tool_calls:
                            del active_tool_calls[tool_call_id]

                else:
                    logger.warning(f"Unknown message type: {message_type}")
                    await websocket.send_json({
                        "type": "error",
                        "message": f"Unknown message type: {message_type}"
                    })

            except asyncio.TimeoutError:
                # Connection has been idle too long, send a ping to check if it's still alive
                try:
                    logger.info(f"Connection {connection_id} idle, sending ping")
                    await websocket.send_json({
                        "type": "ping",
                        "timestamp": time.time()
                    })
                    update_activity(connection_id)
                except Exception:
                    logger.info(f"Connection {connection_id} appears dead, closing")
                    break

            except json.JSONDecodeError:
                logger.error("Invalid JSON received")
                await websocket.send_json({
                    "type": "error",
                    "message": "Invalid JSON format"
                })

            except WebSocketDisconnect:
                logger.info(f"WebSocket disconnected: {connection_id}")
                break

            except Exception as e:
                logger.error(f"Error handling message: {str(e)}")
                try:
                    await websocket.send_json({
                        "type": "error",
                        "message": f"Server error: {str(e)}"
                    })
                except:
                    # If we can't send to the websocket, it's probably closed
                    break

    except WebSocketDisconnect:
        # Handle normal disconnection
        logger.info(f"WebSocket disconnected: {connection_id}")

    except Exception as e:
        # Handle unexpected errors
        logger.error(f"Unexpected error in websocket handler: {str(e)}")

    finally:
        # Clean up on disconnect
        if connection_id in connected_websockets:
            del connected_websockets[connection_id]

        if connection_id in connection_last_activity:
            del connection_last_activity[connection_id]

        if subscribed_agent and subscribed_agent in agent_connections:
            agent_connections[subscribed_agent].discard(connection_id)
            if not agent_connections[subscribed_agent]:
                del agent_connections[subscribed_agent]

        # Clean up any pending tool calls from this connection
        tool_calls_to_remove = []
        for tool_id, details in active_tool_calls.items():
            if details.get("agent_id") == subscribed_agent:
                tool_calls_to_remove.append(tool_id)

        for tool_id in tool_calls_to_remove:
            if tool_id in active_tool_calls:
                del active_tool_calls[tool_id]

        logger.info(f"WebSocket connection closed: {connection_id}")


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
