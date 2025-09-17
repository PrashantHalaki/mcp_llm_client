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
        if not self._model:
            raise Exception("Gemini model not initialized.")
        if not self._api_key:
            raise Exception("Gemini API key is missing.")

        modified_prompt = prompt
        if response_format == "json":
            # Instruct the LLM to return JSON. You might need to refine this prompt
            # based on the specific JSON structure you expect.
            modified_prompt = f"{prompt}\n\nPlease provide the response in JSON format."
            # Gemini's `response_mime_type` can be used for structured output,
            # but it requires a specific schema. For a generic "json" request,
            # prompting is more flexible if a specific schema isn't defined.
            # If you need strict JSON schema, you'd add `response_schema` to `generation_config`.
            # For simplicity here, we'll rely on prompt engineering for generic JSON.

        try:
            if stream and hasattr(self._model, "generate_content_stream"):
                # Gemini streaming API (if available)
                for chunk in self._model.generate_content_stream(modified_prompt, **kwargs):
                    # Each chunk may have .text or .candidates[0].content.parts[0].text
                    if hasattr(chunk, "text"):
                        yield chunk.text
                    elif getattr(chunk, "candidates", None) and chunk.candidates[0].content.parts:
                        yield chunk.candidates[0].content.parts[0].text
            else:
                response = self._model.generate_content(modified_prompt, **kwargs)
                generated_text = ""
                if hasattr(response, 'text'):
                    generated_text = response.text
                elif response.candidates and response.candidates[0].content.parts:
                    generated_text = response.candidates[0].content.parts[0].text
                else:
                    raise Exception("Gemini response did not contain expected text.")

                if response_format == "json":
                    try:
                        json_data = json.loads(generated_text)
                        return json.dumps(json_data, indent=2)
                    except json.JSONDecodeError:
                        logging.warning(f"Gemini response was requested as JSON but could not be parsed. Returning raw text: {generated_text[:100]}...")
                        return generated_text
                return generated_text
        except Exception as e:
            logging.error(f"Error calling Gemini API: {e}")
            raise

