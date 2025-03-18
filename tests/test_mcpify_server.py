#!/usr/bin/env python3
"""
Test script for connecting to the mcpify.ai MCP server.
"""

import asyncio
import uuid
import httpx
import json
import traceback
from dataclasses import dataclass
from typing import Optional


@dataclass
class SSEEvent:
    event: str = ""
    data: str = ""
    id: Optional[str] = None
    retry: Optional[int] = None


class SSEReader:
    """Simple Server-Sent Events (SSE) reader."""

    def __init__(self, response):
        self.response = response
        self.buffer = ""
        self.event = SSEEvent()

    async def __aiter__(self):
        async for line in self.response.aiter_lines():
            if not line.strip():
                # Empty line means the event is complete
                if self.event.data or self.event.event:
                    yield self.event
                    self.event = SSEEvent()
                continue

            if line.startswith("event:"):
                self.event.event = line[6:].strip()
            elif line.startswith("data:"):
                if self.event.data:
                    self.event.data += "\n"
                self.event.data += line[5:].strip()
            elif line.startswith("id:"):
                self.event.id = line[3:].strip()
            elif line.startswith("retry:"):
                try:
                    self.event.retry = int(line[6:].strip())
                except ValueError:
                    pass


class MCPTester:
    """Tester for MCP server connectivity."""

    def __init__(self, base_url):
        self.base_url = base_url
        self.http_client = None
        self.message_url = None
        self.session_id = None

    async def setup(self):
        """Setup the HTTP client."""
        self.http_client = httpx.AsyncClient(timeout=30.0)

    async def cleanup(self):
        """Clean up resources."""
        if self.http_client:
            await self.http_client.aclose()

    async def test_sse_connection(self):
        """Test connection to the SSE endpoint."""
        print(f"Connecting to SSE endpoint: {self.base_url}")

        try:
            response = await self.http_client.get(
                self.base_url,
                headers={"Accept": "text/event-stream"}
            )

            print(f"SSE connection established: {response.status_code}")
            print(f"Headers: {response.headers}")

            if response.status_code != 200:
                print(f"Error: {response.text}")
                return False

            # Process the SSE stream manually
            reader = SSEReader(response)

            try:
                # Wait for the endpoint event
                async for event in reader:
                    print(f"SSE event: event: {event.event}")
                    print(f"SSE event: data: {event.data}")

                    if event.event == "endpoint":
                        endpoint_data = event.data

                        # The endpoint should be a URL that we can use for sending messages
                        self.message_url = endpoint_data.strip()

                        # Extract the session ID from the URL query parameters
                        if "?" in self.message_url:
                            query_params = self.message_url.split("?")[1]
                            params_dict = dict(
                                param.split("=") for param in query_params.split("&"))

                            # Check for either session_id or sessionId
                            if "session_id" in params_dict:
                                self.session_id = params_dict["session_id"]
                            elif "sessionId" in params_dict:
                                self.session_id = params_dict["sessionId"]

                        print(f"Extracted message URL: {self.message_url}")
                        print(f"Extracted session ID: {self.session_id}")

                        # Close the SSE connection
                        await response.aclose()
                        return True

                    # If we get a different event, we should try to handle it as well
                    if event.event == "error":
                        print(f"SSE error event: {event.data}")
                        return False

            except Exception as e:
                print(f"Error processing SSE events: {str(e)}")
                traceback.print_exc()

            # Wait for 5 seconds and if we don't get an endpoint event, consider it a failure
            await asyncio.sleep(5)
            print("Timed out waiting for endpoint event")

            # If we got here, we didn't get an endpoint event
            await response.aclose()
            return False

        except Exception as e:
            print(f"Error connecting to SSE: {str(e)}")
            traceback.print_exc()
            print("\n===== SSE Connection Failed =====\n")
            return False

    async def test_ping(self):
        """Test sending a ping request to the server."""
        # Make sure we have a message URL and session ID
        if not self.message_url or not self.session_id:
            print("Missing message_url or session_id, cannot test ping")
            return False

        # Construct the full URL to use for messaging
        url = self.message_url

        # If the URL doesn't contain the session ID, add it
        if "sessionId=" not in url and "session_id=" not in url:
            if "?" in url:
                url += f"&sessionId={self.session_id}"
            else:
                url += f"?sessionId={self.session_id}"

        print(f"\nSending ping to: {url}")

        try:
            # Create a JSON-RPC request
            request_data = {
                "method": "ping",
                "params": {},
                "jsonrpc": "2.0",
                "id": str(uuid.uuid4())
            }

            # Send the request
            response = await self.http_client.post(
                url,
                json=request_data,
                headers={"Content-Type": "application/json"}
            )

            print(f"Ping response status: {response.status_code}")

            if response.status_code < 300:
                try:
                    response_data = response.json()
                    print(f"Ping response: {json.dumps(response_data, indent=2)}")
                    return True
                except Exception as e:
                    print(f"Received non-JSON response: {response.text[:200]}")
                    print(f"Error parsing JSON: {str(e)}")
                    return False
            else:
                print(f"Ping error: {response.text[:200]}")
                return False

        except Exception as e:
            print(f"Error sending ping: {str(e)}")
            traceback.print_exc()
            return False

    async def test_alternative_endpoints(self):
        """Test alternative endpoints if standard ones fail."""
        # Try different endpoint variations
        endpoint_variations = [
            "/messages",  # Standard endpoint
            "/message",   # Singular form
            "",           # Base URL only
            "/sse/messages",
            "/sse/message"
        ]

        base = self.base_url.rstrip("/")

        # Extract server parameter if present in the original URL
        server_param = ""
        if "server=" in self.base_url:
            server_id = self.base_url.split("server=")[1].split("&")[0]
            server_param = f"server={server_id}"

        # Create session parameter based on the format from the original URL
        session_param = ""
        if self.session_id:
            if "sessionId=" in self.base_url:
                session_param = f"sessionId={self.session_id}"
            else:
                session_param = f"session_id={self.session_id}"

        # Combine parameters
        params = []
        if server_param:
            params.append(server_param)
        if session_param:
            params.append(session_param)

        query_string = "?" + "&".join(params) if params else ""

        for endpoint in endpoint_variations:
            url = f"{base}{endpoint}{query_string}"
            print(f"\nTrying alternative endpoint: {url}")

            # Create ping request
            request_data = {
                "method": "ping",
                "params": {},
                "jsonrpc": "2.0",
                "id": str(uuid.uuid4())
            }

            try:
                response = await self.http_client.post(
                    url,
                    json=request_data,
                    headers={"Content-Type": "application/json"}
                )

                print(f"Response status: {response.status_code}")

                if response.status_code < 300:
                    try:
                        response_data = response.json()
                        print(f"Response data: {json.dumps(response_data, indent=2)}")
                        print(f"Success with endpoint: {endpoint}")
                        return True
                    except Exception as e:
                        print(f"Received non-JSON response: {response.text[:100]}")
                        print(f"Error parsing JSON: {str(e)}")
                else:
                    print(f"Error: {response.text[:100]}")

            except Exception as e:
                print(f"Error with endpoint {endpoint}: {str(e)}")

        return False


async def main():
    """Main function to orchestrate the tests."""
    tester = MCPTester("https://server.mcpify.ai/sse?server=6ebcc255-021f-443b-9be3-02233ee4ea41")

    try:
        # Setup the HTTP client
        await tester.setup()

        # First test the SSE connection
        sse_success = await tester.test_sse_connection()
        print(f"\nSSE Connection Test: {'Passed' if sse_success else 'Failed'}")

        if sse_success:
            # If SSE connection is successful, test the ping
            ping_success = await tester.test_ping()
            print(f"\nPing Test: {'Passed' if ping_success else 'Failed'}")

            if not ping_success:
                # If the ping fails, try alternative endpoints
                alt_success = await tester.test_alternative_endpoints()
                print(f"\nAlternative Endpoints Test: {'Passed' if alt_success else 'Failed'}")

                if not alt_success:
                    print("\nAll tests failed. MCP server might not be compatible or reachable.")
            else:
                print("\nAll tests passed. MCP server is working correctly.")
        else:
            print("\nSSE connection failed. Cannot proceed with further tests.")

    finally:
        # Cleanup
        await tester.cleanup()

    print("\nTests completed.")


if __name__ == "__main__":
    asyncio.run(main())
