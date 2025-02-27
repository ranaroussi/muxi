"""
Base LLM interface that defines the contract for all LLM providers.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Union


class BaseLLM(ABC):
    """
    Abstract base class for LLM providers.
    All LLM implementations must inherit from this class.
    """

    @abstractmethod
    async def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        top_p: Optional[float] = None,
        frequency_penalty: Optional[float] = None,
        presence_penalty: Optional[float] = None,
        stop: Optional[Union[str, List[str]]] = None,
        **kwargs: Any
    ) -> str:
        """
        Generate a chat completion.

        Args:
            messages: A list of messages in the conversation.
            temperature: Controls randomness. Higher values like 0.8 will make the output more random,
                while lower values like 0.2 will make it more focused and deterministic.
            max_tokens: The maximum number of tokens to generate.
            top_p: An alternative to sampling with temperature, called nucleus sampling.
            frequency_penalty: Number between -2.0 and 2.0. Positive values penalize new tokens
                based on their existing frequency in the text so far.
            presence_penalty: Number between -2.0 and 2.0. Positive values penalize new tokens
                based on whether they appear in the text so far.
            stop: Up to 4 sequences where the API will stop generating further tokens.
            **kwargs: Additional provider-specific parameters.

        Returns:
            The generated text.
        """
        pass

    @abstractmethod
    async def embed(self, text: str, **kwargs: Any) -> List[float]:
        """
        Generate embeddings for the provided text.

        Args:
            text: The text to embed.
            **kwargs: Additional provider-specific parameters.

        Returns:
            The embeddings as a list of floats.
        """
        pass
