#!/usr/bin/env python3
"""
Direct test script for the mcpify.ai server using simple HTTP requests.
"""

import asyncio
import httpx
import json
import uuid


async def test_mcpify_server():
    """Test connecting to the mcpify.ai server directly."""
    server_url = "https://server.mcpify.ai/sse?server=6ebcc255-021f-443b-9be3-02233ee4ea41"
    server_base = "https://server.mcpify.ai"

    print(f"Connecting to: {server_url}")

    # Create a client with longer timeout
    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            # Initialize SSE connection
            headers = {
                "Accept": "text/event-stream",
                "Cache-Control": "no-cache",
                "Connection": "keep-alive"
            }

            # Connect to SSE endpoint
            async with client.stream('GET', server_url, headers=headers) as response:
                print(f"SSE connection established: {response.status_code}")
                print(f"Response headers: {response.headers}")

                if response.status_code != 200:
                    print(f"Failed to connect: {response.text}")
                    return

                message_url = None
                session_id = None

                # Process SSE events to get the endpoint URL
                async for line in response.aiter_lines():
                    print(f"SSE event: {line}")

                    if line.startswith("data:"):
                        data = line[5:].strip()
                        print(f"Extracted data: {data}")

                        if "/messages" in data or "/message" in data:
                            message_path = data
                            print(f"Found message path: {message_path}")

                            # Make sure the message path begins with a slash
                            if not message_path.startswith("/"):
                                message_path = "/" + message_path

                            # Create full URL
                            message_url = server_base + message_path
                            print(f"Full message URL: {message_url}")

                            # Extract session ID from the URL
                            if "?" in message_path:
                                query = message_path.split("?")[1]
                                params = dict(p.split("=") for p in query.split("&"))

                                if "sessionId" in params:
                                    session_id = params["sessionId"]
                                elif "session_id" in params:
                                    session_id = params["session_id"]

                                print(f"Extracted session ID: {session_id}")
                                break

                    # Let's not wait too long
                    if message_url:
                        break

                # If we got a message URL and session ID, try sending a ping
                if message_url and session_id:
                    print("\n=== Testing Ping Request ===")

                    # Create JSON-RPC request
                    request_data = {
                        "jsonrpc": "2.0",
                        "method": "ping",
                        "params": {},
                        "id": str(uuid.uuid4())
                    }

                    print(f"Sending ping to: {message_url}")

                    try:
                        ping_response = await client.post(
                            message_url,
                            json=request_data,
                            headers={"Content-Type": "application/json"}
                        )

                        print(f"Ping response status: {ping_response.status_code}")

                        if ping_response.status_code < 300:
                            try:
                                response_data = ping_response.json()
                                print(f"Ping response: {json.dumps(response_data, indent=2)}")
                                print("\n=== Ping successful! ===")
                            except Exception as e:
                                print(f"Received non-JSON response: {ping_response.text[:200]}")
                                print(f"Error parsing JSON: {str(e)}")
                        else:
                            print(f"Ping failed with status {ping_response.status_code}: "
                                  f"{ping_response.text[:200]}")
                    except Exception as e:
                        print(f"Exception during ping: {str(e)}")

                # Test the get_weather function
                if message_url and session_id:
                    print("\n=== Testing get_current_weather Function ===")

                    # Create JSON-RPC request for weather
                    weather_request = {
                        "jsonrpc": "2.0",
                        "method": "get_current_weather",
                        "params": {
                            "location": "San Francisco",
                            "apiKey": "sample_key"  # This is a placeholder
                        },
                        "id": str(uuid.uuid4())
                    }

                    print(f"Sending weather request to: {message_url}")

                    try:
                        weather_response = await client.post(
                            message_url,
                            json=weather_request,
                            headers={"Content-Type": "application/json"}
                        )

                        print(f"Weather response status: {weather_response.status_code}")

                        if weather_response.status_code < 300:
                            try:
                                response_data = weather_response.json()
                                print(f"Weather response: {json.dumps(response_data, indent=2)}")
                            except Exception as e:
                                print(f"Received non-JSON response: {weather_response.text[:200]}")
                                print(f"Error parsing JSON: {str(e)}")
                        else:
                            print(f"Weather request failed: {weather_response.text[:200]}")
                    except Exception as e:
                        print(f"Exception during weather request: {str(e)}")

        except httpx.ReadTimeout:
            print("Connection timed out while waiting for SSE events")
        except Exception as e:
            print(f"Unexpected error: {str(e)}")


if __name__ == "__main__":
    asyncio.run(test_mcpify_server())
