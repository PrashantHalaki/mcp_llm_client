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

        super().__init__(self._api_key, "CustomLLM") # Pass the resolved API key to base class

        if not self._base_url:
            logging.warning("CUSTOM_LLM_URL environment variable or base_url argument is not set. Custom LLM client may not function.")
        else:
            logging.info(f"Custom LLM client initialized with URL: {self._base_url}")

    def generate_response(self, prompt: str, response_format: str = "text", **kwargs: Any) -> str:
        """
        Generates a response from the custom LLM.
        Assumes the custom LLM expects a JSON payload like {"prompt": "...", "response_format": "...", ...}
        and returns a JSON payload like {"response": "..."} or plain text.
        Args:
            prompt (str): The input prompt.
            response_format (str): Desired format of the response ("text" or "json").
            **kwargs: Additional parameters to send to the custom LLM endpoint.
        Returns:
            str: The generated text, or a JSON string if requested and complied.
        Raises:
            Exception: If the HTTP request fails or response is unexpected.
        """
        if not self._base_url:
            raise Exception("Custom LLM URL is not set. Cannot make API call.")

        headers = {"Content-Type": "application/json"}
        if self._api_key:
            # Assuming a common API key header, e.g., for bearer token or custom header
            # You might need to adjust this based on your custom LLM's authentication method.
            headers["Authorization"] = f"Bearer {self._api_key}"
            # Or for other custom headers: headers["X-Api-Key"] = self._api_key

        # Pass the response_format to the custom LLM.
        # Your custom LLM implementation should handle this parameter.
        payload = {"prompt": prompt, "response_format": response_format, **kwargs}

        try:
            response = requests.post(self._base_url, json=payload, headers=headers, timeout=300)
            response.raise_for_status() # Raise an exception for HTTP errors (4xx or 5xx)

            generated_text = ""
            try:
                # Try to parse as JSON first, as custom LLMs often return structured data
                json_response = response.json()
                if isinstance(json_response, dict) and "response" in json_response:
                    generated_text = json_response["response"]
                elif isinstance(json_response, str):
                    generated_text = json_response
                else:
                    logging.warning(f"Custom LLM response JSON format unexpected: {json_response}")
                    generated_text = str(json_response)
            except ValueError:
                # If not JSON, return raw text
                generated_text = response.text

            if response_format == "json":
                try:
                    json_data = json.loads(generated_text)
                    return json.dumps(json_data, indent=2)
                except json.JSONDecodeError:
                    logging.warning(f"Custom LLM response was requested as JSON but could not be parsed. Returning raw text: {generated_text[:100]}...")
                    return generated_text
            return generated_text

        except requests.exceptions.Timeout:
            logging.error(f"Custom LLM request timed out after 300 seconds for URL: {self._base_url}")
            raise
        except requests.exceptions.ConnectionError:
            logging.error(f"Custom LLM connection error for URL: {self._base_url}")
            raise
        except requests.exceptions.HTTPError as e:
            logging.error(f"Custom LLM HTTP error {e.response.status_code} for URL: {self._base_url}: {e.response.text}")
            raise
        except Exception as e:
            logging.error(f"Error calling Custom LLM at {self._base_url}: {e}")
            raise

