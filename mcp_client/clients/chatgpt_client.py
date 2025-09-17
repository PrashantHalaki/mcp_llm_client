from .utils import strip_markdown_code_block
import os
import logging
import json
from typing import Any
from mcp_client.base_client import LLMClient

class ChatGPTClient(LLMClient):
    """
    Client for OpenAI ChatGPT LLM.
    Requires 'openai' library.
    """
    def __init__(self):
        super().__init__(os.getenv("OPENAI_API_KEY"), "ChatGPT")
        try:
            from openai import OpenAI
            if self._api_key:
                self._client = OpenAI(api_key=self._api_key)
                logging.info("ChatGPT client initialized.")
            else:
                self._client = None
        except ImportError:
            logging.error("openai library not found. Please install it: pip install openai")
            self._client = None
        except Exception as e:
            logging.error(f"Failed to configure ChatGPT client: {e}")
            self._client = None

    def generate_response(self, prompt: str, response_format: str = "text", stream: bool = False, **kwargs: Any):
        """
        Generates a response using the ChatGPT LLM.
        Args:
            prompt (str): The input prompt.
            response_format (str): Desired format of the response ("text" or "json").
            stream (bool): Whether to stream the response as chunks (generator) or return full response.
            **kwargs: Additional parameters for OpenAI API (e.g., model, temperature).
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
            raise Exception("ChatGPT client not initialized.")
        if not self._api_key:
            raise Exception("ChatGPT API key is missing.")

        messages = [{"role": "user", "content": prompt}]
        model = kwargs.pop("model", os.getenv("OPENAI_MODEL", "gpt-40"))
        openai_response_format = {"type": "text"}
        if response_format == "json":
            messages[0]["content"] = f"{prompt}\n\nPlease provide the response in JSON format."
        try:
            response_iter = self._client.chat.completions.create(
                model=model,
                messages=messages,
                response_format=openai_response_format,
                stream=True,
                **kwargs
            )
            for chunk in response_iter:
                content = None
                if hasattr(chunk.choices[0], "delta") and hasattr(chunk.choices[0].delta, "content"):
                    content = chunk.choices[0].delta.content
                elif hasattr(chunk.choices[0], "message") and hasattr(chunk.choices[0].message, "content"):
                    content = chunk.choices[0].message.content
                if content:
                    yield content
        except Exception as e:
            logging.error(f"Error calling ChatGPT API (stream): {e}")
            raise

    def _generate_response_full(self, prompt: str, response_format: str = "text", **kwargs: Any):
        if not self._client:
            raise Exception("ChatGPT client not initialized.")
        if not self._api_key:
            raise Exception("ChatGPT API key is missing.")

        messages = [{"role": "user", "content": prompt}]
        model = kwargs.pop("model", os.getenv("OPENAI_MODEL", "gpt-40"))
        openai_response_format = {"type": "text"}
        if response_format == "json":
            messages[0]["content"] = f"{prompt}\n\nPlease provide the response in JSON format."
        try:
            response = self._client.chat.completions.create(
                model=model,
                messages=messages,
                response_format=openai_response_format,
                **kwargs
            )
            generated_text = response.choices[0].message.content

            if response_format == "json":
                text = strip_markdown_code_block(generated_text)
                try:
                    json_data = json.loads(text)
                    return json.dumps(json_data, indent=2)
                except json.JSONDecodeError:
                    logging.warning(f"ChatGPT response was requested as JSON but could not be parsed. Returning raw text: {generated_text[:100]}...")
                    return generated_text
            return generated_text
        except Exception as e:
            logging.error(f"Error calling ChatGPT API (full): {e}")
            raise

