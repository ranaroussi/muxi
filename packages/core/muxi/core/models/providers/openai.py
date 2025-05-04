# =============================================================================
# FRONTMATTER
# =============================================================================
# Title:        OpenAI Provider - Language Model Implementation
# Description:  OpenAI model provider implementation using their official API
# Role:         Provides concrete implementation of the BaseModel interface for OpenAI
# Usage:        Primary LLM provider for ChatGPT, GPT-4, and embedding models
# Author:       Muxi Framework Team
#
# The OpenAI provider module implements the BaseModel interface for OpenAI's
# language models. It provides:
#
# 1. Chat Completion Interface
#    - Implements the standard chat interface with OpenAI-specific parameters
#    - Supports latest models like GPT-4o, GPT-3.5-turbo, etc.
#    - Handles all parameter transformations for API compatibility
#
# 2. Embedding Generation
#    - Implements text embedding using models like text-embedding-3-small
#    - Provides both single and batch embedding generation
#    - Handles proper error handling and logging
#
# 3. MCP Integration
#    - Supports Model Control Protocol (MCP) messaging format
#    - Handles tool calls and tool responses
#    - Provides JSON mode support for structured outputs
#
# Typical usage:
#
#   # Create an OpenAI model instance
#   model = OpenAIModel(
#       model="gpt-4o",
#       temperature=0.7,
#       api_key="sk-..."  # Or use OPENAI_API_KEY env var
#   )
#
#   # Generate chat completion
#   response = await model.chat([
#       {"role": "system", "content": "You are a helpful assistant"},
#       {"role": "user", "content": "Tell me about AI"}
#   ])
#
#   # Generate embeddings
#   embedding = await model.embed("Text to embed")
#
# This provider serves as the reference implementation for other model providers,
# demonstrating how to properly implement the BaseModel interface.
# =============================================================================

import json
import os
from typing import Any, Dict, List, Optional, Union

from loguru import logger
from openai import AsyncOpenAI, APIError

from muxi.core.models.base import BaseModel
from muxi.core.mcp import MCPMessage, MCPToolCall


class OpenAIModel(BaseModel):
    """
    OpenAI model implementation.

    This class provides a complete implementation of the BaseModel interface
    for OpenAI's language models, supporting chat completions, embeddings,
    and structured output generation. It handles authentication, parameter
    transformation, and error handling specific to the OpenAI API.
    """

    def __init__(
        self,
        model: str = "gpt-4o",
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        api_key: Optional[str] = None,
        organization: Optional[str] = None,
        **kwargs,
    ):
        """
        Initialize an OpenAI model.

        Args:
            model: The model to use (e.g., "gpt-4o", "gpt-3.5-turbo"). Selects which
                OpenAI model will be used for completions. Default is gpt-4o.
            temperature: The temperature parameter for generation. Controls randomness
                where higher values (e.g., 0.8) produce more random outputs and lower
                values (e.g., 0.2) produce more deterministic outputs.
            max_tokens: Maximum tokens to generate in responses. Limits the length of
                the response. If None, uses OpenAI's default limits.
            api_key: OpenAI API key. If None, will attempt to load from the OPENAI_API_KEY
                environment variable.
            organization: OpenAI organization ID for multi-organization accounts. If None,
                will attempt to load from the OPENAI_ORGANIZATION environment variable.
            **kwargs: Additional model parameters passed directly to the OpenAI API.
        """
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens

        # Use provided API key or fall back to environment variable
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            logger.warning(
                "No OpenAI API key provided. Set OPENAI_API_KEY environment variable "
                "or pass api_key to OpenAIModel."
            )

        # Use provided organization or fall back to environment variable
        self.organization = organization or os.environ.get("OPENAI_ORGANIZATION")

        # Store additional parameters
        self.additional_params = kwargs

        # Initialize client
        self.client = AsyncOpenAI(api_key=self.api_key, organization=self.organization)

    async def chat(
        self,
        messages: List[Dict[str, Any]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        top_p: Optional[float] = None,
        frequency_penalty: Optional[float] = None,
        presence_penalty: Optional[float] = None,
        stop: Optional[Union[str, List[str]]] = None,
        **kwargs: Any,
    ) -> str:
        """
        Generate a chat completion using OpenAI's API.

        This method sends the conversation history to OpenAI and returns the
        model's response. It handles parameter preparation, API errors, and
        response extraction.

        Args:
            messages: A list of messages in the conversation. Each message should be
                a dictionary with 'role' (system/user/assistant) and 'content' keys.
            temperature: Controls randomness. Overrides the instance setting when provided.
            max_tokens: The maximum number of tokens to generate. Overrides the instance
                setting when provided.
            top_p: An alternative to sampling with temperature, called nucleus sampling.
                Sets a probability threshold for token selection.
            frequency_penalty: Penalize new tokens based on their frequency in the text so far.
                Values range from -2.0 to 2.0.
            presence_penalty: Penalize new tokens based on their presence in the text so far.
                Values range from -2.0 to 2.0.
            stop: Sequences where the API will stop generating further tokens.
                Can be a string or list of strings.
            **kwargs: Additional provider-specific parameters passed directly to the API.

        Returns:
            The generated text response as a string.

        Raises:
            APIError: If the OpenAI API returns an error.
            Exception: For any other errors that occur during the API call.
        """
        try:
            # Create completion parameters
            params = {
                "model": self.model,
                "messages": messages,
                "temperature": temperature if temperature is not None else self.temperature,
                **self.additional_params,
            }

            # Add optional parameters if provided
            if max_tokens is not None:
                params["max_tokens"] = max_tokens
            elif self.max_tokens is not None:
                params["max_tokens"] = self.max_tokens

            if top_p is not None:
                params["top_p"] = top_p

            if frequency_penalty is not None:
                params["frequency_penalty"] = frequency_penalty

            if presence_penalty is not None:
                params["presence_penalty"] = presence_penalty

            if stop is not None:
                params["stop"] = stop

            # Add any additional kwargs
            params.update(kwargs)

            # Call OpenAI API
            response = await self.client.chat.completions.create(**params)

            # Extract and return content
            return response.choices[0].message.content or ""

        except APIError as e:
            logger.error(f"OpenAI API error: {str(e)}")
            raise e
        except Exception as e:
            logger.error(f"Error calling OpenAI: {str(e)}")
            raise e

    async def generate_embeddings(
        self, texts: List[str], model: Optional[str] = None, **kwargs: Any
    ) -> List[List[float]]:
        """
        Generate embeddings for multiple texts using OpenAI's embedding API.

        This method handles batch processing of embeddings, which is more efficient
        than making individual calls for each text.

        Args:
            texts: List of text strings to generate embeddings for. Each string
                will be converted into a vector representation.
            model: Optional embedding model to use. If None, defaults to
                "text-embedding-3-small".
            **kwargs: Additional model-specific parameters passed directly to
                the embedding API.

        Returns:
            List of embedding vectors, where each vector is a list of floats.
            The list has the same length as the input texts list.

        Raises:
            APIError: If the OpenAI API returns an error.
            Exception: For any other errors during embedding generation.
        """
        try:
            # Use provided model or default to text-embedding-3-small
            embedding_model = model or "text-embedding-3-small"

            # Call OpenAI API
            response = await self.client.embeddings.create(
                model=embedding_model, input=texts, **kwargs
            )

            # Extract and return embeddings
            return [item.embedding for item in response.data]

        except APIError as e:
            logger.error(f"OpenAI API error: {str(e)}")
            raise e
        except Exception as e:
            logger.error(f"Error generating embeddings: {str(e)}")
            raise e

    async def generate(self, messages: List[Any]) -> Any:
        """
        Generate a response from the language model using the provided MCP messages.

        This method handles the Model Control Protocol (MCP) message format,
        converting between MCP messages and OpenAI's format, including support
        for tool calls.

        Args:
            messages: A list of MCPMessage objects representing the conversation history.
                These will be converted to OpenAI's format before making the API call.

        Returns:
            An MCPMessage object representing the model's response, including any
            tool calls requested by the model.
        """
        # Convert MCP messages to OpenAI format
        openai_messages = []
        for message in messages:
            if message.role == "tool":
                # Handle tool responses
                openai_messages.append(
                    {
                        "role": "tool",
                        "content": message.content,
                        "tool_call_id": message.tool_call_id,
                    }
                )
            elif message.role == "system":
                # Handle system messages
                openai_messages.append({"role": "system", "content": message.content})
            else:
                # Handle user and assistant messages, including tool calls
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

        # Extract any tool calls from the response
        if hasattr(choice, "tool_calls") and choice.tool_calls:
            for tool_call in choice.tool_calls:
                if tool_call.type == "function":
                    try:
                        # Parse the arguments JSON string
                        args = json.loads(tool_call.function.arguments)
                    except json.JSONDecodeError:
                        logger.warning(f"Failed to parse arguments: {tool_call.function.arguments}")
                        args = {}

                    # Create MCPToolCall object
                    tool_calls.append(
                        MCPToolCall(
                            tool_name=tool_call.function.name,
                            tool_id=tool_call.id,
                            tool_args=args,
                        )
                    )

        # Return as MCPMessage
        return MCPMessage(
            role="assistant",
            content=choice.content,
            tool_calls=tool_calls,
        )

    async def generate_json(self, prompt: str, schema: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a structured JSON response from the language model.

        This method uses OpenAI's JSON mode to produce responses that adhere to
        a specific JSON schema, ensuring the output can be reliably parsed.

        Args:
            prompt: The user prompt to send to the language model. This should be
                phrased to elicit a response that matches the schema.
            schema: JSON schema to use for generating structured output. This defines
                the structure and types the model should adhere to.

        Returns:
            A dictionary with the parsed JSON response that conforms to the provided schema.

        Raises:
            JSONDecodeError: If the response cannot be parsed as valid JSON.
        """
        # Make API call with JSON response format
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            response_format={"type": "json_object", "schema": schema},
        )

        # Extract and parse the JSON content
        content = response.choices[0].message.content
        return json.loads(content)

    async def embed(self, text: str, **kwargs: Any) -> List[float]:
        """
        Generate an embedding for a single text string.

        This method is a simplified interface for generating embeddings for a single
        text, as opposed to the batch processing in generate_embeddings.

        Args:
            text: The text to embed. This string will be converted to a vector
                representation by the embedding model.
            **kwargs: Additional provider-specific parameters passed directly to
                the embedding API.

        Returns:
            A list of floats representing the embedding vector for the input text.
        """
        # Call the embedding API for a single text
        response = await self.client.embeddings.create(model="text-embedding-3-small", input=text)
        return response.data[0].embedding
