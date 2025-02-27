"""
WebSocket module for real-time communication with AI agents.

This module provides WebSocket endpoints for real-time interaction with
agents created with the AI Agent Framework.
"""

import asyncio
import logging
from typing import Dict, List, Any
from uuid import uuid4

from fastapi import WebSocket, WebSocketDisconnect, FastAPI

from src.core.orchestrator import Orchestrator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("websocket")


class ConnectionManager:
    """
    Manager for WebSocket connections.

    This class manages active WebSocket connections and provides methods
    for broadcasting messages to connected clients.
    """

    def __init__(self):
        # client_id -> WebSocket
        self.active_connections: Dict[str, WebSocket] = {}
        # agent_id -> List[client_id]
        self.agent_subscriptions: Dict[str, List[str]] = {}
        # client_id -> agent_id
        self.client_subscriptions: Dict[str, str] = {}

    async def connect(self, websocket: WebSocket) -> str:
        """
        Connect a new WebSocket client.

        Args:
            websocket: The WebSocket connection to register

        Returns:
            str: A unique client ID for the connection
        """
        client_id = str(uuid4())
        await websocket.accept()
        self.active_connections[client_id] = websocket
        logger.info(f"Client {client_id} connected")
        return client_id

    def disconnect(self, client_id: str):
        """
        Disconnect a WebSocket client.

        Args:
            client_id: The ID of the client to disconnect
        """
        if client_id in self.active_connections:
            # Remove from active connections
            del self.active_connections[client_id]

            # Remove from subscriptions
            agent_id = self.client_subscriptions.get(client_id)
            if agent_id and agent_id in self.agent_subscriptions:
                self.agent_subscriptions[agent_id].remove(client_id)
                if not self.agent_subscriptions[agent_id]:
                    del self.agent_subscriptions[agent_id]

            if client_id in self.client_subscriptions:
                del self.client_subscriptions[client_id]

            logger.info(f"Client {client_id} disconnected")

    async def send_personal_message(self, message: Any, client_id: str):
        """
        Send a message to a specific client.

        Args:
            message: The message to send
            client_id: The ID of the client to send to
        """
        if client_id in self.active_connections:
            websocket = self.active_connections[client_id]
            await websocket.send_json(message)

    async def broadcast_to_agent_subscribers(self, message: Any, agent_id: str):
        """
        Broadcast a message to all clients subscribed to an agent.

        Args:
            message: The message to broadcast
            agent_id: The ID of the agent
        """
        if agent_id in self.agent_subscriptions:
            for client_id in self.agent_subscriptions[agent_id]:
                await self.send_personal_message(message, client_id)

    def subscribe_to_agent(self, client_id: str, agent_id: str):
        """
        Subscribe a client to an agent's messages.

        Args:
            client_id: The ID of the client
            agent_id: The ID of the agent
        """
        # First unsubscribe from any current subscription
        if client_id in self.client_subscriptions:
            old_agent_id = self.client_subscriptions[client_id]
            if old_agent_id in self.agent_subscriptions and client_id in self.agent_subscriptions[old_agent_id]:
                self.agent_subscriptions[old_agent_id].remove(client_id)
                if not self.agent_subscriptions[old_agent_id]:
                    del self.agent_subscriptions[old_agent_id]

        # Subscribe to the new agent
        if agent_id not in self.agent_subscriptions:
            self.agent_subscriptions[agent_id] = []

        self.agent_subscriptions[agent_id].append(client_id)
        self.client_subscriptions[client_id] = agent_id
        logger.info(f"Client {client_id} subscribed to agent {agent_id}")


# Create a connection manager
manager = ConnectionManager()


def register_websocket_routes(app: FastAPI, orchestrator: Orchestrator):
    """
    Register WebSocket routes with the FastAPI application.

    Args:
        app: The FastAPI application
        orchestrator: The agent orchestrator
    """

    @app.websocket("/ws")
    async def websocket_endpoint(websocket: WebSocket):
        """
        WebSocket endpoint for real-time communication with agents.

        The client can send the following message types:
        - subscribe: Subscribe to an agent's messages
        - chat: Send a message to an agent

        The server will send the following message types:
        - response: A response from an agent
        - agent_thinking: Indicates an agent is processing
        - agent_done: Indicates an agent has finished processing
        - error: An error message
        """
        client_id = await manager.connect(websocket)

        try:
            while True:
                data = await websocket.receive_json()

                # Validate message format
                if "type" not in data:
                    await manager.send_personal_message(
                        {"type": "error", "message": "Missing 'type' field in message"},
                        client_id
                    )
                    continue

                message_type = data["type"]

                # Handle different message types
                if message_type == "subscribe":
                    # Subscribe to an agent
                    if "agent_id" not in data:
                        await manager.send_personal_message(
                            {"type": "error", "message": "Missing 'agent_id' field in subscribe message"},
                            client_id
                        )
                        continue

                    agent_id = data["agent_id"]

                    # Check if agent exists
                    if not orchestrator.get_agent(agent_id):
                        await manager.send_personal_message(
                            {"type": "error", "message": f"Agent '{agent_id}' does not exist"},
                            client_id
                        )
                        continue

                    # Subscribe to agent
                    manager.subscribe_to_agent(client_id, agent_id)

                    await manager.send_personal_message(
                        {"type": "subscribed", "agent_id": agent_id},
                        client_id
                    )

                elif message_type == "chat":
                    # Send a message to an agent
                    if "message" not in data:
                        await manager.send_personal_message(
                            {"type": "error", "message": "Missing 'message' field in chat message"},
                            client_id
                        )
                        continue

                    # Get agent_id from message or from subscription
                    agent_id = data.get("agent_id")
                    if not agent_id:
                        agent_id = manager.client_subscriptions.get(client_id)
                        if not agent_id:
                            await manager.send_personal_message(
                                {"type": "error", "message": "No agent specified and not subscribed to any agent"},
                                client_id
                            )
                            continue

                    # Check if agent exists
                    agent = orchestrator.get_agent(agent_id)
                    if not agent:
                        await manager.send_personal_message(
                            {"type": "error", "message": f"Agent '{agent_id}' does not exist"},
                            client_id
                        )
                        continue

                    # Notify subscribers that agent is thinking
                    await manager.broadcast_to_agent_subscribers(
                        {"type": "agent_thinking", "agent_id": agent_id},
                        agent_id
                    )

                    # Process message in a separate task to not block the WebSocket
                    async def process_message():
                        try:
                            # Get response from agent
                            response = await agent.chat(data["message"])

                            # Determine tools used
                            tools_used = []
                            if hasattr(agent, "last_used_tools"):
                                tools_used = agent.last_used_tools

                            # Broadcast response to all subscribers
                            await manager.broadcast_to_agent_subscribers(
                                {
                                    "type": "response",
                                    "message": response,
                                    "agent_id": agent_id,
                                    "tools_used": tools_used
                                },
                                agent_id
                            )

                            # Notify that agent is done thinking
                            await manager.broadcast_to_agent_subscribers(
                                {"type": "agent_done", "agent_id": agent_id},
                                agent_id
                            )

                        except Exception as e:
                            logger.error(f"Error processing message: {str(e)}")
                            # Send error message
                            await manager.broadcast_to_agent_subscribers(
                                {"type": "error", "message": f"Error: {str(e)}", "agent_id": agent_id},
                                agent_id
                            )

                    # Start processing in a separate task
                    asyncio.create_task(process_message())

                else:
                    # Unknown message type
                    await manager.send_personal_message(
                        {"type": "error", "message": f"Unknown message type: {message_type}"},
                        client_id
                    )

        except WebSocketDisconnect:
            manager.disconnect(client_id)

        except Exception as e:
            logger.error(f"WebSocket error: {str(e)}")
            manager.disconnect(client_id)
