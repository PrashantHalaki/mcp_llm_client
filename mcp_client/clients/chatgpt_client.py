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

    def generate_response(self, prompt: str, response_format: str = "text", **kwargs: Any) -> str:
        """
        Generates a response using the ChatGPT LLM.
        Args:
            prompt (str): The input prompt.
            response_format (str): Desired format of the response ("text" or "json").
            **kwargs: Additional parameters for OpenAI API (e.g., model, temperature).
        Returns:
            str: The generated text, or a JSON string if requested and complied.
        Raises:
            Exception: If the API call fails or client is not initialized.
        """
        if not self._client:
            raise Exception("ChatGPT client not initialized.")
        if not self._api_key:
            raise Exception("ChatGPT API key is missing.")

        messages = [{"role": "user", "content": prompt}]
        # Default model for ChatGPT if not provided in kwargs
        model = kwargs.pop("model", os.getenv("OPENAI_MODEL", "gpt-40"))

        openai_response_format = {"type": "text"} # Default
        if response_format == "json":
            # For newer OpenAI models (like gpt-4-turbo, gpt-3.5-turbo-1106),
            # you can use the response_format parameter.
            # For older models, you'd rely on prompt engineering.
            # We'll add a prompt instruction for broader compatibility.
            messages[0]["content"] = f"{prompt}\n\nPlease provide the response in JSON format."
            
        try:
            response = self._client.chat.completions.create(
                model=model,
                messages=messages,
                response_format=openai_response_format, # Pass the response_format parameter
                **kwargs
            )
            generated_text = response.choices[0].message.content

            if response_format == "json":
                try:
                    json_data = json.loads(generated_text)
                    return json.dumps(json_data, indent=2)
                except json.JSONDecodeError:
                    logging.warning(f"ChatGPT response was requested as JSON but could not be parsed. Returning raw text: {generated_text[:100]}...")
                    return generated_text
            return generated_text
        except Exception as e:
            logging.error(f"Error calling ChatGPT API: {e}")
            raise

