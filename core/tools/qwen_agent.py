"""
Qwen Agent with filesystem tools via Ollama.
Provides a simple agent loop for Qwen 2.5 with tool calling.
"""

import json
import requests
from typing import Optional, Generator
from filesystem_tools import FILESYSTEM_TOOLS, execute_tool

OLLAMA_BASE_URL = "http://localhost:11434"
DEFAULT_MODEL = "qwen2.5-coder:7b"


class QwenAgent:
    """Simple agent loop for Qwen with filesystem access."""

    def __init__(self, model: str = DEFAULT_MODEL, system_prompt: Optional[str] = None):
        self.model = model
        self.system_prompt = system_prompt or self._default_system_prompt()
        self.messages = []
        self.tools = FILESYSTEM_TOOLS

    def _default_system_prompt(self) -> str:
        return """You are Qwen, an AI assistant working within the Rhiz project.
You have access to filesystem tools to read, write, and explore files.

Your capabilities:
- read_file: Read contents of files
- write_file: Write or append to files
- list_directory: List files and folders
- file_exists: Check if a path exists

You are sandboxed to the Rhiz_LocalDev directory for safety.

When asked to perform tasks involving files:
1. First check if paths exist using file_exists or list_directory
2. Read files before modifying them
3. Confirm actions with clear responses

Be helpful, accurate, and transparent about what you're doing."""

    def _call_ollama(self, messages: list, tools: Optional[list] = None) -> dict:
        """Make a request to Ollama API."""
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False
        }
        if tools:
            payload["tools"] = tools

        response = requests.post(
            f"{OLLAMA_BASE_URL}/api/chat",
            json=payload,
            timeout=120
        )
        response.raise_for_status()
        return response.json()

    def chat(self, user_message: str, max_tool_rounds: int = 5) -> str:
        """
        Send a message and get a response, handling tool calls automatically.

        Args:
            user_message: The user's input
            max_tool_rounds: Maximum number of tool call rounds to prevent infinite loops

        Returns:
            The final text response from the model
        """
        # Build message history
        messages = [{"role": "system", "content": self.system_prompt}]
        messages.extend(self.messages)
        messages.append({"role": "user", "content": user_message})

        tool_round = 0

        while tool_round < max_tool_rounds:
            # Call Ollama
            response = self._call_ollama(messages, self.tools)
            assistant_message = response.get("message", {})

            # Check for tool calls
            tool_calls = assistant_message.get("tool_calls", [])

            if not tool_calls:
                # No tool calls - we have a final response
                final_content = assistant_message.get("content", "")

                # Save to history
                self.messages.append({"role": "user", "content": user_message})
                self.messages.append({"role": "assistant", "content": final_content})

                return final_content

            # Process tool calls
            messages.append(assistant_message)

            for tool_call in tool_calls:
                function_name = tool_call.get("function", {}).get("name", "")
                arguments = tool_call.get("function", {}).get("arguments", {})

                # Parse arguments if they're a string
                if isinstance(arguments, str):
                    try:
                        arguments = json.loads(arguments)
                    except json.JSONDecodeError:
                        arguments = {}

                print(f"  [Tool: {function_name}({arguments})]")

                # Execute the tool
                result = execute_tool(function_name, arguments)
                print(f"  [Result: {result[:200]}...]" if len(result) > 200 else f"  [Result: {result}]")

                # Add tool result to messages
                messages.append({
                    "role": "tool",
                    "content": result
                })

            tool_round += 1

        return "Error: Maximum tool rounds exceeded"

    def reset(self):
        """Clear conversation history."""
        self.messages = []


def interactive_session():
    """Run an interactive chat session with Qwen."""
    print("=" * 60)
    print("Qwen Filesystem Agent")
    print("=" * 60)
    print(f"Model: {DEFAULT_MODEL}")
    print("Type 'quit' to exit, 'reset' to clear history")
    print("=" * 60)

    agent = QwenAgent()

    while True:
        try:
            user_input = input("\nYou: ").strip()

            if not user_input:
                continue
            if user_input.lower() == "quit":
                print("Goodbye!")
                break
            if user_input.lower() == "reset":
                agent.reset()
                print("Conversation history cleared.")
                continue

            print("\nQwen: ", end="", flush=True)
            response = agent.chat(user_input)
            print(response)

        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except requests.exceptions.ConnectionError:
            print("\nError: Cannot connect to Ollama. Is it running?")
            print("Start Ollama with: ollama serve")
        except Exception as e:
            print(f"\nError: {e}")


if __name__ == "__main__":
    interactive_session()
