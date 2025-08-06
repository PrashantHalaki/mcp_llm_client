# Multi-Client Proxy (MCP) LLM Client

The Multi-Client Proxy (MCP) LLM Client is a robust and flexible Python library designed to streamline your interactions with various Large Language Models (LLMs). It provides a unified interface to popular LLMs like Google Gemini, OpenAI ChatGPT, and Perplexity AI, with a built-in failover mechanism based on your defined priority. Additionally, it offers a versatile "Custom LLM" client, allowing you to seamlessly integrate any other LLM, whether it's a locally deployed model or another third-party service, by simply providing its API endpoint and key.

This client is built with production-grade considerations in mind, emphasizing modularity, secure API key management via environment variables, and comprehensive error handling.

## ✨ Features

- Multi-LLM Support: Connects to Google Gemini, OpenAI ChatGPT, Perplexity AI, and any custom LLM.
- Priority-Based Failover: Define a custom priority order for LLM providers. If a primary service fails or is unreachable, the client automatically attempts the next one in your list.
- Configurable Response Format: Request responses in plain text or structured JSON format, allowing for flexible integration into various applications.
- Secure API Key Management: All sensitive API keys are loaded securely from environment variables, ensuring your credentials are not hardcoded.
- Extensible Architecture: Designed with an abstract base class (LLMClient), making it easy to add support for new LLM providers in the future.
- Production-Grade Code: Features modular design, comprehensive error handling, and informative logging for better maintainability and debugging.
- Custom LLM Integration: A generic client to interact with any LLM that exposes an HTTP API, perfect for local models or less common third-party services.

## 📁 Folder Structure

The project is organized into a clear and logical folder structure:

```
.
├── README.md
├── examples/
│ └── run_client.py
├── mcp_client/
│ ├── clients/
│ │ ├── __init__.py
│ │ ├── gemini_client.py # Google Gemini client implementation
│ │ ├── chatgpt_client.py # OpenAI ChatGPT client implementation
│ │ ├── perplexity_client.py # Perplexity AI client implementation
│ │ └── custom_llm_client.py # Generic client for any custom/local LLM
│ ├── __init__.py
│ ├── base_client.py # Abstract Base Class for all LLM clients
│ └── manager.py # Main Multi-Client Proxy logic and example usage
├── .env.example # Example file for environment variables
├── requirements.txt # Python dependencies
├── LICENSE # MIT License file
└── .gitignore # Git ignore file for common exclusions
```

## 🚀 Getting Started

Follow these steps to set up and run the MCP LLM Client.

**_Prerequisites_**

- Python 3.8+
- `pip` (Python package installer)

**_Installation Steps_**

**1. Clone the repository:**

```bash
git clone https://github.com/PrashantHalaki/mcp_llm_client.git
cd mcp-llm-client
```

**2. Install dependencies:**

The project uses google-generativeai, openai, and requests. You can install them using the provided requirements.txt file:

```bash
pip install -r requirements.txt
```

### Configuration

API keys and LLM priority are managed via environment variables for security and flexibility.

**1. Required API Keys**

```bash
GEMINI_API_KEY="YOUR_GOOGLE_GEMINI_API_KEY"
OPENAI_API_KEY="YOUR_OPENAI_API_KEY"
PERPLEXITY_API_KEY="YOUR_PERPLEXITY_API_KEY"
```

**2. Optional: Environment Variables**

```bash
CUSTOM_LLM_URL="http://localhost:5000/generate" # Replace with your custom LLM's API endpoint
CUSTOM_LLM_API_KEY="YOUR_OPTIONAL_CUSTOM_LLM_API_KEY" # Only if your custom LLM requires one
GEMINI_MODEL="YOUR_GEMINI_MODEL" # Only if you want to use model other than gemini-1.5-flash
OPENAI_MODEL="YOUR_OPEN_AI_MODEL" # Only if you want to use model other than gpt-3.5-turbo
PERPLEXITY_MODEL="YOUR_PERPLEXITY_MODEL" # Only if you want to use model other than sonar-pro
```

**3. Define the priority order for LLM clients (comma-separated, case-insensitive)**

**Available clients:** gemini, chatgpt, perplexity, custom

**Example:** gemini,chatgpt,custom,perplexity (Gemini first, then ChatGPT, etc.)

```bash
LLM_PRIORITY="gemini,chatgpt,custom,perplexity"
```

**LLM_PRIORITY:** This variable dictates the order in which the MCP client attempts to connect to the LLMs. If the first one fails, it moves to the next. If this variable is not set, the default order is gemini,chatgpt,perplexity,custom.

If an API key for a specific service is not set, that client will issue a warning and might not function, but the MCPClient will still attempt to use the next available client in the priority list.

### Load environment variables (optional, but recommended for local development):

While the client directly reads from os.getenv(), for local development, you might want to use a library like python-dotenv to automatically load variables from your .env file.

```bash
pip install python-dotenv
```

Then, at the top of your manager.py (or any entry point), add:

```python
from dotenv import load_dotenv
load_dotenv() # This will load variables from .env file
```

## 💡 Usage

The manager.py file contains an example of how to instantiate and use the MCPClient.

**1. Basic Text Generation**

```python
from mcp_client import MCPClient
import os

# Initialize MCPClient. It will read LLM_PRIORITY from environment.

# If LLM_PRIORITY is not set, it defaults to "gemini,chatgpt,perplexity,custom".

mcp_client = MCPClient(priority_order=os.getenv("LLM_PRIORITY"))

prompt = "What is the capital of France?"
response_text, client_name = mcp_client.generate_response(prompt, response_format="text")

if response_text:
print(f"Response from {client_name}:")
print(response_text)
else:
print("Failed to get a response from any LLM client.")
```

**2. JSON Response Generation**

You can request structured JSON output. The client will instruct the LLM to return JSON, and for compatible models (like certain ChatGPT versions), it will use native JSON mode.

```python
from mcp_client import MCPClient
import os
import json

mcp_client = MCPClient(priority_order=os.getenv("LLM_PRIORITY"))

json_prompt = "Tell me about the Eiffel Tower. Provide the response as a JSON object with keys 'name', 'location', 'height_meters', and 'fun_fact'."
response_json, client_name_json = mcp_client.generate_response(json_prompt, response_format="json")

if response_json:
print(f"Response from {client_name_json} (JSON):")
try: # For pretty printing the JSON string
parsed_json = json.loads(response_json)
print(json.dumps(parsed_json, indent=2))
except json.JSONDecodeError:
print(response_json) # Print raw if parsing failed
else:
print("Failed to get a JSON response from any LLM client.")
```

**3. Passing Additional Parameters**

You can pass additional keyword arguments (\*\*kwargs) to the underlying LLM API calls. For example, to control creativity with temperature:

```python
from mcp_client import MCPClient
import os

mcp_client = MCPClient(priority_order=os.getenv("LLM_PRIORITY"))

poem_prompt = "Write a short poem about a cat."

# Pass temperature to make the response more creative

response_poem, client_name_poem = mcp_client.generate_response(poem_prompt, response_format="text", temperature=0.7)

if response_poem:
print(f"Response from {client_name_poem}:")
print(response_poem)
else:
print("Failed to get a response for the poem from any LLM client.")
```

## 🤝 Contributing

Contributions are welcome! If you have suggestions for improvements, bug fixes, or new features, please open an issue or submit a pull request.

Please read our [CONTRIBUTING.md](./CONTRIBUTING.md) guide before making any changes.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](./LICENSE) file for details.

## 🔗 Credits

Built with ❤️ by [Prashant Halaki](https://github.com/PrashantHalaki)
