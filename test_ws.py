import websockets
import asyncio
import json

async def main():
    try:
        print("Connecting to ws://localhost:5050/ws...")
        async with websockets.connect("ws://localhost:5050/ws") as websocket:
            print("Connected! Sending subscription request...")
            await websocket.send(json.dumps({"type": "subscribe", "agent_id": "test_agent"}))
            response = await websocket.recv()
            print(f"Response: {response}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
