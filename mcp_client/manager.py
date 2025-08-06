import os
import logging
from typing import List, Optional, Tuple, Dict, Any

# Import all specific LLM clients
from mcp_client.base_client import LLMClient
from .clients import GeminiClient, ChatGPTClient, PerplexityClient, CustomLLMClient

# Set up basic logging for the main module
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class MCPClient:
    """
    Multi-Client Proxy (MCP) for LLMs.
    Manages multiple LLM clients and provides failover based on priority.
    """
    def __init__(self, priority_order: Optional[str] = None):
        """
        Initializes the MCPClient with a specified priority order.
        Args:
            priority_order (Optional[str]): A comma-separated string of LLM client names
                                             (e.g., "gemini,chatgpt,perplexity,custom").
                                             If None, defaults to "gemini,chatgpt,perplexity,custom".
        """
        # The CustomLLMClient is now instantiated without arguments here,
        # relying on environment variables (CUSTOM_LLM_URL, CUSTOM_LLM_API_KEY).
        # If you need to pass specific URLs/keys at runtime, you would modify
        # this instantiation.
        self._available_clients: Dict[str, LLMClient] = {
            "gemini": GeminiClient(),
            "chatgpt": ChatGPTClient(),
            "perplexity": PerplexityClient(),
            "custom": CustomLLMClient() # Changed from LocalLLMClient
        }
        self._clients: List[LLMClient] = []

        if priority_order:
            self._set_priority(priority_order)
        else:
            # Default priority if not specified
            logging.info("No LLM_PRIORITY specified, using default order: Gemini, ChatGPT, Perplexity, CustomLLM.")
            self._clients = [
                self._available_clients["gemini"],
                self._available_clients["chatgpt"],
                self._available_clients["perplexity"],
                self._available_clients["custom"] # Changed from "local"
            ]

    def _set_priority(self, priority_order_str: str):
        """
        Sets the priority of LLM clients based on the input string.
        Args:
            priority_order_str (str): Comma-separated string of client names.
        """
        ordered_client_names = [name.strip().lower() for name in priority_order_str.split(',')]
        for name in ordered_client_names:
            if name in self._available_clients:
                self._clients.append(self._available_clients[name])
            else:
                logging.warning(f"Unknown LLM client '{name}' specified in priority order. Skipping.")
        if not self._clients:
            logging.error("No valid LLM clients configured based on the provided priority order. "
                          "Please check LLM_PRIORITY environment variable.")

    def generate_response(self, prompt: str, response_format: str = "text", **kwargs: Any) -> Tuple[Optional[str], Optional[str]]:
        """
        Generates a response using the first available LLM client based on priority.
        If a client fails, it attempts the next one in the priority list.
        Args:
            prompt (str): The input prompt for the LLM.
            response_format (str): Desired format of the response ("text" or "json").
            **kwargs: Additional parameters to pass to the LLM's generate_response method.
        Returns:
            Tuple[Optional[str], Optional[str]]: A tuple containing the generated response
                                                  and the name of the client that provided it.
                                                  Returns (None, None) if all clients fail.
        """
        if response_format not in ["text", "json"]:
            logging.error(f"Invalid response_format: '{response_format}'. Must be 'text' or 'json'.")
            return None, None

        if not self._clients:
            logging.error("No LLM clients are configured. Cannot generate response.")
            return None, None

        for client in self._clients:
            logging.info(f"Attempting to generate response with {client.client_name}...")
            try:
                response = client.generate_response(prompt, response_format=response_format, **kwargs)
                logging.info(f"Successfully generated response using {client.client_name}.")
                return response, client.client_name
            except Exception as e:
                logging.error(f"Failed to get response from {client.client_name}: {e}")
                continue # Try the next client

        logging.error("All configured LLM clients failed to generate a response.")
        return None, None

# --- Example Usage ---
if __name__ == "__main__":
    # IMPORTANT: Set these environment variables before running the script.
    # Example (in your shell or .env file):
    # export GEMINI_API_KEY="YOUR_GEMINI_API_KEY"
    # export OPENAI_API_KEY="YOUR_OPENAI_API_KEY"
    # export PERPLEXITY_API_KEY="YOUR_PERPLEXITY_API_KEY"
    # export CUSTOM_LLM_URL="http://localhost:5000/generate" # Replace with your custom LLM endpoint
    # export CUSTOM_LLM_API_KEY="YOUR_CUSTOM_LLM_API_KEY_HERE" # Optional, if your custom LLM needs an API key
    # export LLM_PRIORITY="gemini,chatgpt,custom,perplexity" # Define your preferred order, using "custom"

    # Initialize MCPClient. It will read LLM_PRIORITY from environment.
    # If LLM_PRIORITY is not set, it defaults to "gemini,chatgpt,perplexity,custom".
    mcp_client = MCPClient(priority_order=os.getenv("LLM_PRIORITY"))

    print("\n--- Testing Text Response ---")
    test_prompt_text = "What is the capital of France?"
    logging.info(f"\nSending prompt (text format): '{test_prompt_text}'")

    response_text, client_name = mcp_client.generate_response(test_prompt_text, response_format="text")

    if response_text:
        print(f"\n--- Response from {client_name} (Text) ---")
        print(response_text)
        print("----------------------------------")
    else:
        print("\nFailed to get a text response from any LLM client.")

    print("\n--- Testing JSON Response ---")
    test_prompt_json = "Tell me about the Eiffel Tower. Provide the response as a JSON object with keys 'name', 'location', 'height_meters', and 'fun_fact'."
    logging.info(f"\nSending prompt (JSON format): '{test_prompt_json}'")

    response_json, client_name_json = mcp_client.generate_response(test_prompt_json, response_format="json")

    if response_json:
        print(f"\n--- Response from {client_name_json} (JSON) ---")
        print(response_json)
        print("----------------------------------")
    else:
        print("\nFailed to get a JSON response from any LLM client.")

    print("\n--- Testing another Text Response with kwargs ---")
    test_prompt_poem = "Write a short poem about a cat."
    logging.info(f"\nSending prompt (text format, with temperature): '{test_prompt_poem}'")

    # Example of passing kwargs (e.g., temperature for creativity)
    response_poem, client_name_poem = mcp_client.generate_response(test_prompt_poem, response_format="text", temperature=0.7)

    if response_poem:
        print(f"\n--- Response from {client_name_poem} (Text) ---")
        print(response_poem)
        print("----------------------------------")
    else:
        print("\nFailed to get a response for the poem from any LLM client.")

