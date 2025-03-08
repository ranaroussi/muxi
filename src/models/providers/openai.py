"""
OpenAIModel language model provider implementation.

This module provides an implementation of the BaseModel interface for
the OpenAI API.
"""

import json
import os
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Union

import openai
from loguru import logger

from src.config import config
from src.models.base import BaseModel


@dataclass
class MCPToolCall:
    """Tool call information for MCP messages."""

    tool_name: str
    tool_id: str
    tool_args: Dict[str, Any]


class OpenAIModel(BaseModel):
    """OpenAIModel language model provider implementation."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gpt-4o",
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ):
        """
        Initialize the OpenAIModel language model provider.

        Args:
            api_key: OpenAI API key, defaults to environment variable
            model: Model name to use (default: gpt-4o)
            temperature: Sampling temperature (default: 0.7)
            max_tokens: Maximum tokens in response (default: None)
        """
        # Initialize client
        self.api_key = api_key or config.model.openai_api_key
        if not self.api_key:
            self.api_key = os.getenv("OPENAI_API_KEY")
            if not self.api_key:
                logger.warning("No OpenAI API key provided. Using with Azure or a mock client.")

        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.client = openai.Client(api_key=self.api_key)

    async def generate(self, messages: List[Any]) -> Any:
        """
        Generate a response from the language model using the provided messages.

        Args:
            messages: A list of MCPMessage objects

        Returns:
            An MCPMessage object representing the model's response
        """
        # Convert MCP messages to OpenAI format
        openai_messages = []
        for message in messages:
            if message.role == "tool":
                openai_messages.append(
                    {
                        "role": "tool",
                        "content": message.content,
                        "tool_call_id": message.tool_call_id,
                    }
                )
            elif message.role == "system":
                openai_messages.append({"role": "system", "content": message.content})
            else:
                msg_data = {"role": message.role, "content": message.content}
                if message.tool_calls:
                    msg_data["tool_calls"] = [
                        {
                            "id": tc.tool_id,
                            "type": "function",
                            "function": {
                                "name": tc.tool_name,
                                "arguments": json.dumps(tc.tool_args),
                            },
                        }
                        for tc in message.tool_calls
                    ]
                openai_messages.append(msg_data)

        # Make API call
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=openai_messages,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
        )

        # Parse response
        choice = response.choices[0].message
        tool_calls = []

        if hasattr(choice, "tool_calls") and choice.tool_calls:
            for tool_call in choice.tool_calls:
                if tool_call.type == "function":
                    try:
                        args = json.loads(tool_call.function.arguments)
                    except json.JSONDecodeError:
                        logger.warning(f"Failed to parse arguments: {tool_call.function.arguments}")
                        args = {}

                    tool_calls.append(
                        MCPToolCall(
                            tool_name=tool_call.function.name,
                            tool_id=tool_call.id,
                            tool_args=args,
                        )
                    )

        # Import here to avoid circular imports
        from src.core.mcp import MCPMessage

        return MCPMessage(
            role="assistant",
            content=choice.content,
            tool_calls=tool_calls,
        )

    async def generate_json(self, prompt: str, schema: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a response from the language model and parse it as JSON.

        Args:
            prompt: The user prompt to send to the language model.
            schema: JSON schema to use for generating structured output

        Returns:
            A dictionary with the parsed JSON response
        """
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            response_format={"type": "json_object", "schema": schema},
        )

        content = response.choices[0].message.content
        return json.loads(content)

    async def embed(self, text: str, **kwargs: Any) -> List[float]:
        """
        Generate an embedding for the given text.

        Args:
            text: The text to embed
            **kwargs: Additional provider-specific parameters.

        Returns:
            A list of floats representing the embedding vector
        """
        response = await self.client.embeddings.create(model="text-embedding-3-small", input=text)
        return response.data[0].embedding

    async def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        top_p: Optional[float] = None,
        frequency_penalty: Optional[float] = None,
        presence_penalty: Optional[float] = None,
        stop: Optional[Union[str, List[str]]] = None,
        **kwargs: Any,
    ) -> str:
        """
        Generate a chat completion.

        Args:
            messages: A list of messages in the conversation.
            temperature: Controls randomness.
            max_tokens: The maximum number of tokens to generate.
            top_p: An alternative to sampling with temperature.
            frequency_penalty: Penalize new tokens based on frequency.
            presence_penalty: Penalize new tokens based on presence.
            stop: Sequences where the API will stop generating further tokens.
            **kwargs: Additional provider-specific parameters.

        Returns:
            The generated text response.
        """
        # Use specified parameters or fall back to instance defaults
        temp = temperature if temperature is not None else self.temperature
        max_tok = max_tokens if max_tokens is not None else self.max_tokens

        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temp,
            max_tokens=max_tok,
            top_p=top_p,
            frequency_penalty=frequency_penalty,
            presence_penalty=presence_penalty,
            stop=stop,
            **kwargs,
        )

        return response.choices[0].message.content
