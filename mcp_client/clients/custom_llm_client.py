from .utils import strip_markdown_code_block
import os
import logging
import json
import requests
from typing import Any, Optional
from mcp_client.base_client import LLMClient

class CustomLLMClient(LLMClient):
    """
    Client for a custom or locally deployed LLM.
    Assumes the custom LLM exposes a simple HTTP POST endpoint.
    This client is highly flexible and can be configured to connect
    to various LLMs by specifying their base URL and an optional API key.
    """
    def __init__(self, base_url: Optional[str] = None, api_key: Optional[str] = None):
        """
        Initializes the CustomLLMClient.
        Args:
            base_url (Optional[str]): The base URL of the custom LLM's API endpoint.
                                      Defaults to CUSTOM_LLM_URL environment variable.
            api_key (Optional[str]): The API key for the custom LLM.
                                     Defaults to CUSTOM_LLM_API_KEY environment variable.
        """
        # Prioritize constructor arguments, then environment variables
        self._base_url = base_url if base_url is not None else os.getenv("CUSTOM_LLM_URL")
        self._api_key = api_key if api_key is not None else os.getenv("CUSTOM_LLM_API_KEY")
        self._model = os.getenv("CUSTOM_LLM_MODEL", "mistral")

        super().__init__(self._api_key, "CustomLLM") # Pass the resolved API key to base class

        if not self._base_url:
            logging.warning("CUSTOM_LLM_URL environment variable or base_url argument is not set. Custom LLM client may not function.")
        else:
            logging.info(f"Custom LLM client initialized with URL: {self._base_url}")

    def generate_response(self, prompt: str, response_format: str = "text", stream: bool = False, **kwargs: Any):
        """
        Generates a response from the custom LLM.
        Assumes the custom LLM expects a JSON payload like {"prompt": "...", "response_format": "...", ...}
        and returns a JSON payload like {"response": "..."} or plain text.
        Args:
            prompt (str): The input prompt.
            response_format (str): Desired format of the response ("text" or "json").
            stream (bool): Whether to stream the response as chunks (generator) or return full response.
            **kwargs: Additional parameters to send to the custom LLM endpoint.
        Returns:
            If stream is True: yields chunks (generator).
            If stream is False: returns the full response (str).
        Raises:
            Exception: If the HTTP request fails or response is unexpected.
        """
        if stream:
            return self._generate_response_stream(prompt, response_format, **kwargs)
        else:
            return self._generate_response_full(prompt, response_format, **kwargs)

    def _generate_response_stream(self, prompt: str, response_format: str = "text", **kwargs: Any):
        if not self._base_url:
            raise Exception("Custom LLM URL is not set. Cannot make API call.")

        headers = {"Content-Type": "application/json"}
        if self._api_key:
            headers["Authorization"] = f"Bearer {self._api_key}"

        payload = {"prompt": prompt, "model": self._model, "stream": True, "response_format": response_format, **kwargs}

        try:
            with requests.post(self._base_url, json=payload, headers=headers, timeout=300, stream=True) as response:
                response.raise_for_status()
                for line in response.iter_lines(decode_unicode=True):
                    if not line:
                        continue
                    try:
                        json_obj = json.loads(line)
                        if isinstance(json_obj, dict) and "response" in json_obj:
                            yield json_obj["response"]
                        elif isinstance(json_obj, str):
                            yield json_obj
                        else:
                            yield str(json_obj)
                    except json.JSONDecodeError:
                        yield line
        except Exception as e:
            logging.error(f"Error calling Custom LLM at {self._base_url} (stream): {e}")
            raise

    def _generate_response_full(self, prompt: str, response_format: str = "text", **kwargs: Any):
        if not self._base_url:
            raise Exception("Custom LLM URL is not set. Cannot make API call.")

        headers = {"Content-Type": "application/json"}
        if self._api_key:
            headers["Authorization"] = f"Bearer {self._api_key}"

        payload = {"prompt": prompt, "model": self._model, "stream": False, "response_format": response_format, **kwargs}

        try:
            response = requests.post(self._base_url, json=payload, headers=headers, timeout=300)
            response.raise_for_status()

            generated_text = ""
            try:
                json_response = response.json()
                if isinstance(json_response, dict) and "response" in json_response:
                    generated_text = json_response["response"]
                elif isinstance(json_response, str):
                    generated_text = json_response
                else:
                    logging.warning(f"Custom LLM response JSON format unexpected: {json_response}")
                    generated_text = str(json_response)
            except ValueError:
                generated_text = response.text

            if response_format == "json":
                text = strip_markdown_code_block(generated_text)
                try:
                    json_data = json.loads(text)
                    return json.dumps(json_data, indent=2)
                except json.JSONDecodeError:
                    logging.warning(f"Custom LLM response was requested as JSON but could not be parsed. Returning raw text: {generated_text[:100]}...")
                    return generated_text
            return generated_text
        except Exception as e:
            logging.error(f"Error calling Custom LLM at {self._base_url} (full): {e}")
            raise

