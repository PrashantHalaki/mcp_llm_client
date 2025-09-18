from .utils import strip_markdown_code_block
import os
import logging
import json
from typing import Any
from mcp_client.base_client import LLMClient

class GeminiClient(LLMClient):
    """
    Client for Google Gemini LLM.
    Requires 'google-generativeai' library.
    """
    def __init__(self):
        super().__init__(os.getenv("GEMINI_API_KEY"), "Gemini")
        try:
            import google.generativeai as genai
            if self._api_key:
                genai.configure(api_key=self._api_key)
            self._model = genai.GenerativeModel(os.getenv("GEMINI_MODEL", "gemini-2.0-flash"))
            self._generativeConfig = genai.GenerationConfig
            logging.info("Gemini client initialized.")
        except ImportError:
            logging.error("google-generativeai library not found. Please install it: pip install google-generativeai")
            self._model = None
        except Exception as e:
            logging.error(f"Failed to configure Gemini client: {e}")
            self._model = None

    def generate_response(self, prompt: str, response_format: str = "text", stream: bool = False, **kwargs: Any):
        """
        Generates a response using the Gemini LLM.
        Args:
            prompt (str): The input prompt.
            response_format (str): Desired format of the response ("text" or "json").
            stream (bool): Whether to stream the response as chunks (generator) or return full response.
            **kwargs: Additional parameters for Gemini API (e.g., generation_config).
        Returns:
            If stream is True: yields chunks (generator).
            If stream is False: returns the full response (str).
        Raises:
            Exception: If the API call fails or model is not initialized.
        """
        creative_config = None
        config_keys = {"max_output_tokens", "temperature", "top_p", "top_k", "stop_sequences", "candidate_count"}
        if kwargs and any(key in config_keys for key in kwargs):
            config_kwargs = {k: v for k, v in kwargs.items() if k in config_keys}
            if config_kwargs:
                creative_config = self._generativeConfig(**config_kwargs)
        if stream:
            return self._generate_response_stream(prompt, response_format, creative_config)
        else:
            return self._generate_response_full(prompt, response_format, creative_config)

    def _generate_response_stream(self, prompt: str, response_format: str = "text", creative_config: Any = None):
        if not self._model:
            raise Exception("Gemini model not initialized.")
        if not self._api_key:
            raise Exception("Gemini API key is missing.")

        modified_prompt = prompt
        if response_format == "json":
            modified_prompt = f"{prompt}\n\nPlease provide the response in JSON format."

        try:
            for chunk in self._model.generate_content(modified_prompt, stream=True, generation_config=creative_config):
                if hasattr(chunk, "text"):
                    yield chunk.text
                elif getattr(chunk, "candidates", None) and chunk.candidates[0].content.parts:
                    yield chunk.candidates[0].content.parts[0].text
        except Exception as e:
            logging.error(f"Error calling Gemini API (stream): {e}")
            raise

    def _generate_response_full(self, prompt: str, response_format: str = "text", creative_config: Any = None):
        if not self._model:
            raise Exception("Gemini model not initialized.")
        if not self._api_key:
            raise Exception("Gemini API key is missing.")

        modified_prompt = prompt
        if response_format == "json":
            modified_prompt = f"{prompt}\n\nPlease provide the response in JSON format."

        try:
            response = self._model.generate_content(modified_prompt, generation_config=creative_config)
            generated_text = ""
            if hasattr(response, 'text'):
                generated_text = response.text
            elif response.candidates and response.candidates[0].content.parts:
                generated_text = response.candidates[0].content.parts[0].text
            else:
                raise Exception("Gemini response did not contain expected text.")

            if response_format == "json":
                text = strip_markdown_code_block(generated_text)
                try:
                    json_data = json.loads(text)
                    return json.dumps(json_data, indent=2)
                except json.JSONDecodeError:
                    logging.warning(f"Gemini response was requested as JSON but could not be parsed. Returning raw text: {generated_text[:100]}...")
                    return generated_text
            print("generated_text", generated_text)
            return generated_text
        except Exception as e:
            logging.error(f"Error calling Gemini API (full): {e}")
            raise

