from .utils import strip_markdown_code_block
import os
import logging
import json

# Ensure debug logs are printed for this module
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

    def generate_response(
        self,
        prompt: str,
        response_format: str = "text",
        stream: bool = False,
        **kwargs: Any
    ) -> str | Any:  # str for text, dict for json, Any for stream (generator)
        """
        Generates a response using the Perplexity LLM.
        Args:
            prompt (str): The input prompt.
            response_format (str): Desired format of the response ("text" or "json").
            stream (bool): Whether to stream the response as chunks (generator) or return full response.
            **kwargs: Additional parameters for Perplexity API (e.g., model, temperature).
        Returns:
            If stream is True: yields chunks (generator).
            If stream is False: returns the full response (str).
        Raises:
            Exception: If the API call fails or client is not initialized.
        """
        if stream:
            return self._generate_response_stream(prompt, response_format, **kwargs)
        else:
            return self._generate_response_full(prompt, response_format, **kwargs)

    def _generate_response_stream(self, prompt: str, response_format: str = "text", **kwargs: Any):
        if not self._client:
            raise Exception("Perplexity client not initialized.")
        if not self._api_key:
            raise Exception("Perplexity API key is missing.")

        messages = [{"role": "user", "content": prompt}]
        model = kwargs.pop("model", os.getenv("PERPLEXITY_MODEL", "sonar-pro"))

        if response_format == "json":
            messages[0]["content"] = f"{prompt}\n\nPlease provide the response in JSON format."

        try:
            print(f"[PerplexityClient] Streaming response from model: {model}")
            response_iter = self._client.chat.completions.create(
                model=model,
                messages=messages,
                stream=True,
                **kwargs
            )
            for chunk in response_iter:
                logging.debug(f"[PerplexityClient][stream=True] Raw chunk: {repr(chunk)}")
                content = None
                if hasattr(chunk.choices[0], "delta") and hasattr(chunk.choices[0].delta, "content"):
                    content = chunk.choices[0].delta.content
                    logging.debug(f"[PerplexityClient][stream=True] Extracted delta.content: {repr(content)}")
                elif hasattr(chunk.choices[0], "message") and hasattr(chunk.choices[0].message, "content"):
                    content = chunk.choices[0].message.content
                    logging.debug(f"[PerplexityClient][stream=True] Extracted message.content: {repr(content)}")
                if content:
                    yield content
        except Exception as e:
            logging.error(f"Error calling Perplexity API: {e}")
            raise

    def _generate_response_full(self, prompt: str, response_format: str = "text", **kwargs: Any):
        if not self._client:
            raise Exception("Perplexity client not initialized.")
        if not self._api_key:
            raise Exception("Perplexity API key is missing.")

        messages = [{"role": "user", "content": prompt}]
        model = kwargs.pop("model", os.getenv("PERPLEXITY_MODEL", "sonar-pro"))

        if response_format == "json":
            messages[0]["content"] = f"{prompt}\n\nPlease provide the response in JSON format."

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

