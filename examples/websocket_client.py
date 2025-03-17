#!/usr/bin/env python
"""
Example WebSocket client for the MUXI Framework.

This script demonstrates how to use the WebSocket API to communicate with agents
in real-time.
"""

import asyncio
import json
import sys
from urllib.parse import urljoin

import websockets


class WebSocketClient:
    """Simple WebSocket client for interacting with the MUXI Framework."""

    def __init__(self, base_url="ws://localhost:5050"):
        """
        Initialize the WebSocket client.

        Args:
            base_url: Base URL of the API server
        """
        self.base_url = base_url
        self.ws = None
        self.agent_id = None

    async def connect(self):
        """Connect to the WebSocket endpoint."""
        ws_url = urljoin(self.base_url, "ws")
        self.ws = await websockets.connect(ws_url)
        print(f"Connected to {ws_url}")

    async def subscribe_to_agent(self, agent_id):
        """
        Subscribe to an agent.

        Args:
            agent_id: ID of the agent to subscribe to
        """
        self.agent_id = agent_id
        await self.ws.send(json.dumps({"type": "subscribe", "agent_id": agent_id}))
        response = await self.ws.recv()
        return json.loads(response)

    async def set_user(self, user_id):
        """
        Set the user ID for this connection.

        Args:
            user_id: User ID for multi-user agents
        """
        await self.ws.send(json.dumps({"type": "set_user", "user_id": user_id}))
        response = await self.ws.recv()
        return json.loads(response)

    async def send_message(self, message, agent_id=None):
        """
        Send a message to an agent.

        Args:
            message: Message to send
            agent_id: ID of the agent to send to (uses subscribed agent if None)
        """
        if not agent_id and not self.agent_id:
            raise ValueError("No agent specified and not subscribed to any agent")

        await self.ws.send(
            json.dumps({"type": "chat", "message": message, "agent_id": agent_id or self.agent_id})
        )

    async def receive_messages(self):
        """
        Receive and handle messages from the WebSocket.

        This is a persistent loop that handles incoming messages.
        """
        while True:
            try:
                response = await self.ws.recv()
                data = json.loads(response)

                # Handle different message types
                if data.get("type") == "message":
                    print(f"\nAgent: {data.get('content', '')}")
                    if data.get("tools_used"):
                        print(f"Tools used: {', '.join(data['tools_used'])}")

                elif data.get("type") == "tool_start":
                    print(f"\nUsing tool: {data.get('tool_name', '')}", flush=True)

                elif data.get("type") == "tool_end":
                    print(f"\nTool result: {data.get('result', '')}", flush=True)

                elif data.get("type") == "error":
                    print(f"\nError: {data.get('message', '')}")

                elif data.get("type") == "subscribed":
                    print(f"\nSubscribed to agent: {data.get('agent_id', '')}")

                else:
                    print(f"\nReceived: {data}")

            except websockets.exceptions.ConnectionClosed:
                print("\nConnection closed")
                break

            except Exception as e:
                print(f"\nError: {str(e)}")

    async def interactive_chat(self):
        """Start an interactive chat session with the agent."""
        # Start message receiver in the background
        receiver_task = asyncio.create_task(self.receive_messages())

        try:
            print("Enter messages to send to the agent (Ctrl+C to exit):")
            print("Special commands:")
            print("  /user <user_id>  - Set user ID (for multi-user agents)")
            print("  /agent <agent_id> - Switch to a different agent")
            print("  /exit - Exit the chat")

            while True:
                # Use asyncio to read from stdin without blocking
                line = await asyncio.get_event_loop().run_in_executor(
                    None, lambda: sys.stdin.readline().strip()
                )

                if not line:
                    continue

                # Check for commands
                if line.lower() in ["/exit", "/quit", "/bye"]:
                    break

                elif line.startswith("/user "):
                    user_id = line[6:].strip()
                    await self.set_user(user_id)
                    print(f"Set user ID to: {user_id}")
                    continue

                elif line.startswith("/agent "):
                    agent_id = line[7:].strip()
                    await self.subscribe_to_agent(agent_id)
                    print(f"Switched to agent: {agent_id}")
                    continue

                # Send message to agent
                await self.send_message(line)

        except KeyboardInterrupt:
            print("\nExiting...")

        finally:
            # Cancel receiver task
            receiver_task.cancel()

            # Close WebSocket connection
            if self.ws:
                await self.ws.close()


async def main():
    """Run the example WebSocket client."""
    # Parse command line arguments
    import argparse

    parser = argparse.ArgumentParser(description="WebSocket client example")
    parser.add_argument(
        "--url", default="ws://localhost:5050", help="WebSocket URL (default: ws://localhost:5050)"
    )
    parser.add_argument(
        "--agent", default="assistant", help="Agent ID to connect to (default: assistant)"
    )
    parser.add_argument(
        "--user", default=None, help="User ID for multi-user agents (default: None)"
    )
    args = parser.parse_args()

    # Create client
    client = WebSocketClient(args.url)

    try:
        # Connect to WebSocket
        await client.connect()

        # Subscribe to agent
        await client.subscribe_to_agent(args.agent)

        # Set user ID if provided
        if args.user:
            await client.set_user(args.user)

        # Start interactive chat
        await client.interactive_chat()

    except Exception as e:
        print(f"Error: {str(e)}")


if __name__ == "__main__":
    asyncio.run(main())
