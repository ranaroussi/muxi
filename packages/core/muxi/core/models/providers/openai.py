"""
OpenAI model provider for the MUXI Framework.

This module provides an implementation of the BaseModel interface for OpenAI models.
"""

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

    This class provides an implementation of the BaseModel interface for OpenAI models.
    """

    def __init__(
        self,
        model: str = "gpt-4o",
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        api_key: Optional[str] = None,
        organization: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize an OpenAI model.

        Args:
            model: The model to use (e.g., "gpt-4o", "gpt-3.5-turbo")
            temperature: The temperature parameter for generation
            max_tokens: Maximum tokens to generate
            api_key: OpenAI API key (defaults to environment variable)
            organization: OpenAI organization ID (defaults to environment variable)
            **kwargs: Additional model parameters
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
        self.client = AsyncOpenAI(
            api_key=self.api_key,
            organization=self.organization
        )

    async def chat(
        self,
        messages: List[Dict[str, Any]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> str:
        """
        Generate a chat response from the model.

        Args:
            messages: A list of message objects with role and content
            temperature: Optional temperature parameter (overrides model default)
            max_tokens: Optional maximum tokens to generate (overrides model default)
            **kwargs: Additional model-specific parameters

        Returns:
            The model's response as a string
        """
        try:
            # Create completion parameters
            params = {
                "model": self.model,
                "messages": messages,
                "temperature": temperature if temperature is not None else self.temperature,
                **self.additional_params,
                **kwargs
            }

            # Add max_tokens if provided
            if max_tokens is not None:
                params["max_tokens"] = max_tokens
            elif self.max_tokens is not None:
                params["max_tokens"] = self.max_tokens

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
        self,
        texts: List[str],
        model: Optional[str] = None,
        **kwargs
    ) -> List[List[float]]:
        """
        Generate embeddings for a list of texts.

        Args:
            texts: List of texts to generate embeddings for
            model: Optional embedding model to use
            **kwargs: Additional model-specific parameters

        Returns:
            List of embedding vectors (one per input text)
        """
        try:
            # Use provided model or default to text-embedding-3-small
            embedding_model = model or "text-embedding-3-small"

            # Call OpenAI API
            response = await self.client.embeddings.create(
                model=embedding_model,
                input=texts,
                **kwargs
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

    async def generate_embeddings(self, texts: List[str], **kwargs: Any) -> List[List[float]]:
        """
        Generate embeddings for a list of texts.

        Args:
            texts: List of texts to generate embeddings for.
            **kwargs: Additional provider-specific parameters.

        Returns:
            A list of embeddings, each as a list of floats.
        """
        model = kwargs.get("model", "text-embedding-3-small")
        response = await self.client.embeddings.create(model=model, input=texts)
        return [item.embedding for item in response.data]

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

        # Use the client without await - the client handles async internally
        response = self.client.chat.completions.create(
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
