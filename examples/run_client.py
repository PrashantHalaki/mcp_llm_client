import os
import json
import logging
from dotenv import load_dotenv # Make sure to install python-dotenv: pip install python-dotenv

# Load environment variables from .env file (if present)
load_dotenv()

# Configure logging for this example script
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from mcp_client import MCPClient

def run_example():
    """
    Demonstrates the usage of the MCPClient for text and JSON response generation.
    """
    print("🚀 Initializing MCP Client...")
    # Initialize MCPClient. It will read LLM_PRIORITY from environment.
    # If LLM_PRIORITY is not set, it defaults to "gemini,chatgpt,perplexity,custom".
    mcp_client = MCPClient(priority_order=os.getenv("LLM_PRIORITY"))
    print("✅ MCP Client initialized.")

    # --- Example 1: Basic Text Generation ---
    print("\n--- Example 1: Basic Text Generation ---")
    text_prompt = "Explain the concept of photosynthesis in simple terms."
    logging.info(f"Sending text prompt: '{text_prompt}'")

    response_text, client_name = mcp_client.generate_response(text_prompt, response_format="text")

    if response_text:
        print(f"\n✨ Response from {client_name} (Text):")
        print(response_text)
        print("-" * 50)
    else:
        print("\n❌ Failed to get a text response from any LLM client.")
        print("-" * 50)

    # --- Example 2: JSON Response Generation ---
    print("\n--- Example 2: JSON Response Generation ---")
    json_prompt = "List three famous landmarks in London. Provide the response as a JSON object where the key is 'landmarks' and the value is an array of strings."
    logging.info(f"Sending JSON prompt: '{json_prompt}'")

    response_json, client_name_json = mcp_client.generate_response(json_prompt, response_format="json")

    if response_json:
        print(f"\n✨ Response from {client_name_json} (JSON):")
        try:
            # Attempt to pretty-print the JSON string
            parsed_json = json.loads(response_json)
            print(json.dumps(parsed_json, indent=2))
        except json.JSONDecodeError:
            print(f"Warning: Could not parse response as JSON. Raw response:\n{response_json}")
        print("-" * 50)
    else:
        print("\n❌ Failed to get a JSON response from any LLM client.")
        print("-" * 50)

    # --- Example 3: Text Generation with Additional Parameters (e.g., creativity) ---
    print("\n--- Example 3: Text Generation with Additional Parameters ---")
    creative_prompt = "Write a short, whimsical story about a squirrel who learns to fly."
    logging.info(f"Sending creative prompt (with temperature=0.8): '{creative_prompt}'")

    # Pass temperature to make the response more creative (if supported by the LLM)
    response_creative, client_name_creative = mcp_client.generate_response(
        creative_prompt, response_format="text", temperature=0.8
    )

    if response_creative:
        print(f"\n✨ Response from {client_name_creative} (Text, Creative):")
        print(response_creative)
        print("-" * 50)
    else:
        print("\n❌ Failed to get a creative response from any LLM client.")
        print("-" * 50)

    # --- Example 4: Testing Custom LLM (if configured and prioritized) ---
    print("\n--- Example 4: Testing Custom LLM (if configured) ---")
    custom_llm_prompt = "What is your current model?"
    logging.info(f"Sending prompt to custom LLM: '{custom_llm_prompt}'")

    response_custom, client_name_custom = mcp_client.generate_response(custom_llm_prompt, response_format="text")

    if response_custom:
        print(f"\n✨ Response from {client_name_custom}:")
        print(response_custom)
        print("-" * 50)
    else:
        print("\n❌ Failed to get a response from the custom LLM (or it's not prioritized/configured).")
        print("-" * 50)


if __name__ == "__main__":
    run_example()

