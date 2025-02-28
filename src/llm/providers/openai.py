"""
OpenAILLM LLM provider implementation.
"""

import json
from typing import Dict, List, Optional, Any, Union, AsyncGenerator

import openai
from openai import AsyncOpenAI
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type
)

from src.config import config
from src.llm.base import BaseLLM


class OpenAILLM(BaseLLM):
    """
    OpenAILLM LLM provider implementation.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gpt-4",
        embedding_model: str = "text-embedding-3-small",
        temperature: float = 0.7,
        max_tokens: int = 1000,
    ):
        """
        Initialize the OpenAILLM LLM provider.

        Args:
            api_key: OpenAILLM API key. If not provided, it will be loaded from
                environment variables.
            model: The model to use for text generation.
            embedding_model: The model to use for embeddings.
            temperature: Controls randomness in the output.
            max_tokens: Maximum number of tokens to generate.
        """
        self.api_key = api_key or config.llm.openai_api_key
        if not self.api_key:
            raise ValueError(
                "OpenAILLM API key is required. "
                "Please provide it or set the OPENAI_API_KEY environment "
                "variable."
            )

        self.client = AsyncOpenAI(api_key=self.api_key)
        self.model = model
        self.embedding_model = embedding_model
        self.temperature = temperature
        self.max_tokens = max_tokens

    @retry(
        retry=retry_if_exception_type(
            (openai.RateLimitError, openai.APITimeoutError)
        ),
        wait=wait_exponential(multiplier=1, min=4, max=60),
        stop=stop_after_attempt(5)
    )
    async def generate(
        self,
        prompt: str,
        system_message: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        stop_sequences: Optional[List[str]] = None,
        **kwargs: Any
    ) -> str:
        """
        Generate a response from the LLM based on the prompt.

        Args:
            prompt: The user prompt to send to the LLM.
            system_message: Optional system message to set context.
            temperature: Controls randomness in the output.
            max_tokens: Maximum number of tokens to generate.
            stop_sequences: List of sequences where the API will stop
                generating.
            **kwargs: Additional provider-specific parameters.

        Returns:
            The generated text response.
        """
        messages = []
        if system_message:
            messages.append({"role": "system", "content": system_message})
        messages.append({"role": "user", "content": prompt})

        response = await self.client.chat.completions.create(
            model=kwargs.get("model", self.model),
            messages=messages,
            temperature=temperature or self.temperature,
            max_tokens=max_tokens or self.max_tokens,
            stop=stop_sequences,
            **{k: v for k, v in kwargs.items() if k != "model"}
        )

        return response.choices[0].message.content

    @retry(
        retry=retry_if_exception_type(
            (openai.RateLimitError, openai.APITimeoutError)
        ),
        wait=wait_exponential(multiplier=1, min=4, max=60),
        stop=stop_after_attempt(5)
    )
    async def generate_with_json(
        self,
        prompt: str,
        json_schema: Dict[str, Any],
        system_message: Optional[str] = None,
        temperature: Optional[float] = None,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """
        Generate a response from the LLM and parse it as JSON.

        Args:
            prompt: The user prompt to send to the LLM.
            json_schema: The JSON schema that the response should conform to.
            system_message: Optional system message to set context.
            temperature: Controls randomness in the output.
            **kwargs: Additional provider-specific parameters.

        Returns:
            The generated response parsed as a JSON object.
        """
        if not system_message:
            system_message = (
                "You are a helpful assistant that responds with JSON. "
                "Your response must be valid JSON that conforms to the "
                "provided schema."
            )

        # Add schema information to the system message
        system_message = (
            f"{system_message}\n\nJSON Schema: {json.dumps(json_schema)}"
        )

        response = await self.client.chat.completions.create(
            model=kwargs.get("model", self.model),
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt}
            ],
            temperature=temperature or self.temperature,
            response_format={"type": "json_object"},
            **{k: v for k, v in kwargs.items() if k != "model"}
        )

        content = response.choices[0].message.content
        return json.loads(content)

    @retry(
        retry=retry_if_exception_type(
            (openai.RateLimitError, openai.APITimeoutError)
        ),
        wait=wait_exponential(multiplier=1, min=4, max=60),
        stop=stop_after_attempt(5)
    )
    async def embed(
        self,
        text: Union[str, List[str]],
        **kwargs: Any
    ) -> Union[List[float], List[List[float]]]:
        """
        Generate embeddings for the given text.

        Args:
            text: The text to embed. Can be a single string or a list of
                strings.
            **kwargs: Additional provider-specific parameters.

        Returns:
            The embeddings as a list of floats (for a single text) or
            a list of list of floats (for multiple texts).
        """
        model = kwargs.get("model", self.embedding_model)

        # Handle both single string and list of strings
        is_single = isinstance(text, str)
        texts = [text] if is_single else text

        response = await self.client.embeddings.create(
            model=model,
            input=texts,
            **{k: v for k, v in kwargs.items() if k != "model"}
        )

        embeddings = [item.embedding for item in response.data]

        # Return a single embedding if input was a single string
        return embeddings[0] if is_single else embeddings

    @retry(
        retry=retry_if_exception_type(
            (openai.RateLimitError, openai.APITimeoutError)
        ),
        wait=wait_exponential(multiplier=1, min=4, max=60),
        stop=stop_after_attempt(5)
    )
    async def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs: Any
    ) -> str:
        """
        Generate a response based on a conversation history.

        Args:
            messages: List of message dictionaries with 'role' and 'content'
                keys. Roles can be 'system', 'user', or 'assistant'.
            temperature: Controls randomness in the output.
            max_tokens: Maximum number of tokens to generate.
            **kwargs: Additional provider-specific parameters.

        Returns:
            The generated text response.
        """
        response = await self.client.chat.completions.create(
            model=kwargs.get("model", self.model),
            messages=messages,
            temperature=temperature or self.temperature,
            max_tokens=max_tokens or self.max_tokens,
            **{k: v for k, v in kwargs.items() if k != "model"}
        )

        return response.choices[0].message.content

    @retry(
        retry=retry_if_exception_type(
            (openai.RateLimitError, openai.APITimeoutError)
        ),
        wait=wait_exponential(multiplier=1, min=4, max=60),
        stop=stop_after_attempt(5)
    )
    async def stream_chat(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs: Any
    ) -> AsyncGenerator[str, None]:
        """
        Stream a response based on a conversation history.

        Args:
            messages: List of message dictionaries with 'role' and 'content'
                keys. Roles can be 'system', 'user', or 'assistant'.
            temperature: Controls randomness in the output.
            max_tokens: Maximum number of tokens to generate.
            **kwargs: Additional provider-specific parameters.

        Returns:
            An async generator that yields chunks of the response as they're
            generated.
        """
        stream = await self.client.chat.completions.create(
            model=kwargs.get("model", self.model),
            messages=messages,
            temperature=temperature or self.temperature,
            max_tokens=max_tokens or self.max_tokens,
            stream=True,
            **{k: v for k, v in kwargs.items() if k != "model"}
        )

        async for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
