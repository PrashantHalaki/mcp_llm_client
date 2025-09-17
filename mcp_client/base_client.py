import os
import logging
from abc import ABC, abstractmethod
from typing import Optional, Any

# Set up basic logging for all modules
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class LLMClient(ABC):
    """
    Abstract Base Class for all LLM clients.
    Defines the common interface for generating responses and handling API keys.
    """
    def __init__(self, api_key: Optional[str], client_name: str):
        self._api_key = api_key
        self._client_name = client_name
        self._validate_api_key(client_name, api_key)

    @property
    def client_name(self) -> str:
        """Returns the name of the LLM client."""
        return self._client_name

    def _validate_api_key(self, client_name: str, api_key_value: Optional[str]):
        """
        Validates if an API key is provided.
        Logs a warning if the API key is missing.
        """
        if not api_key_value:
            logging.warning(f"API key for {client_name} is not set. This client may not function.")

    @abstractmethod
    def generate_response(self, prompt: str, response_format: str = "text", stream: bool = False, **kwargs: Any):
        """
        Abstract method to generate a response from the LLM.
        Must be implemented by concrete client classes.

        Args:
            prompt (str): The input prompt for the LLM.
            response_format (str): Desired format of the response ("text" or "json").
            stream (bool): Whether to stream the response as chunks (generator) or return full response.
            **kwargs: Additional parameters specific to the LLM API.

        Returns:
            If stream is True: yields chunks (generator).
            If stream is False: returns the full response (str).

        Raises:
            Exception: If there's an error during response generation.
        """
        pass

