#!/usr/bin/env python
"""
Simple WebSocket client to test connection to the AI Agent Framework.
"""

import asyncio
import json
import websockets

async def main():
    uri = "ws://localhost:5050/ws"
    print(f"Connecting to {uri}...")

    try:
        async with websockets.connect(uri) as websocket:
            print("Connected to WebSocket server.")

            # Subscribe to the agent we created
            print("Subscribing to agent test_agent1...")
            await websocket.send(json.dumps({
                "type": "subscribe",
                "agent_id": "test_agent1"
            }))

            # Wait for the subscription response
            response = await websocket.recv()
            print(f"Received: {response}")

            # Send a test message
            print("Sending a test message...")
            await websocket.send(json.dumps({
                "type": "chat",
                "message": "Hello, agent!",
                "agent_id": "test_agent1"
            }))

            # Keep receiving messages until we get an agent_done message
            done = False
            while not done:
                response = await websocket.recv()
                data = json.loads(response)
                print(f"Received: {data}")

                if data.get("type") == "agent_done":
                    done = True

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
