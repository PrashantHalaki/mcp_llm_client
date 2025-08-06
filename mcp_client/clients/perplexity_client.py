import os
import logging
import json
from typing import Any
from mcp_client.base_client import LLMClient

class PerplexityClient(LLMClient):
    """
    Client for Perplexity LLM.
    Uses OpenAI-compatible API. Requires 'openai' library.
    """
    def __init__(self):
        super().__init__(os.getenv("PERPLEXITY_API_KEY"), "Perplexity")
        try:
            from openai import OpenAI
            if self._api_key:
                # Perplexity uses the OpenAI client but with their base_url
                self._client = OpenAI(api_key=self._api_key, base_url=os.getenv("PERPLEXITY_LLM_URL", "https://api.perplexity.ai"))
                logging.info("Perplexity client initialized.")
            else:
                self._client = None
        except ImportError:
            logging.error("openai library not found. Please install it: pip install openai")
            self._client = None
        except Exception as e:
            logging.error(f"Failed to configure Perplexity client: {e}")
            self._client = None

    def generate_response(self, prompt: str, response_format: str = "text", **kwargs: Any) -> str:
        """
        Generates a response using the Perplexity LLM.
        Args:
            prompt (str): The input prompt.
            response_format (str): Desired format of the response ("text" or "json").
            **kwargs: Additional parameters for Perplexity API (e.g., model, temperature).
        Returns:
            str: The generated text, or a JSON string if requested and complied.
        Raises:
            Exception: If the API call fails or client is not initialized.
        """
        if not self._client:
            raise Exception("Perplexity client not initialized.")
        if not self._api_key:
            raise Exception("Perplexity API key is missing.")

        messages = [{"role": "user", "content": prompt}]
        # Default model for Perplexity if not provided in kwargs
        model = kwargs.pop("model", os.getenv("PERPLEXITY_MODEL", "sonar-pro")) # A common Perplexity online model

        if response_format == "json":
            # Instruct the LLM to return JSON. Perplexity's API is OpenAI-compatible,
            # so prompt engineering is the primary way to get JSON unless a specific model
            # supports a native JSON mode.
            messages[0]["content"] = f"{prompt}\n\nPlease provide the response in JSON format."
            # Perplexity models generally respond well to prompt-based JSON requests.
            # No native `response_format` parameter in their OpenAI-compatible API currently.

        try:
            response = self._client.chat.completions.create(
                model=model,
                messages=messages,
                **kwargs
            )
            generated_text = response.choices[0].message.content

            if response_format == "json":
                try:
                    json_data = json.loads(generated_text)
                    return json.dumps(json_data, indent=2)
                except json.JSONDecodeError:
                    logging.warning(f"Perplexity response was requested as JSON but could not be parsed. Returning raw text: {generated_text[:100]}...")
                    return generated_text
            return generated_text
        except Exception as e:
            logging.error(f"Error calling Perplexity API: {e}")
            raise

