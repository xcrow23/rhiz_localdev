"""
Filesystem tools for Qwen via Ollama tool calling.
Provides read, write, list, and explore capabilities.
"""

import os
import json
from pathlib import Path
from typing import Optional

# Sandboxed root - Qwen can only access files within this directory
# Cross-platform: detect if running on Windows or WSL
import platform
if platform.system() == "Windows":
    SANDBOX_ROOT = Path(r"C:\Users\dread\Documents\Rhiz_LocalDev")
else:
    SANDBOX_ROOT = Path("/mnt/c/Users/dread/Documents/Rhiz_LocalDev")


def _validate_path(path: str) -> Path:
    """Ensure path is within sandbox."""
    resolved = (SANDBOX_ROOT / path).resolve()
    if not str(resolved).startswith(str(SANDBOX_ROOT.resolve())):
        raise PermissionError(f"Access denied: {path} is outside sandbox")
    return resolved


# Tool definitions for Ollama
FILESYSTEM_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read the contents of a file. Returns the file content as text.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Relative path to the file within the Rhiz project"
                    },
                    "max_lines": {
                        "type": "integer",
                        "description": "Maximum number of lines to read (default: 200)",
                        "default": 200
                    }
                },
                "required": ["path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Write content to a file. Creates the file if it doesn't exist.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Relative path to the file within the Rhiz project"
                    },
                    "content": {
                        "type": "string",
                        "description": "Content to write to the file"
                    },
                    "append": {
                        "type": "boolean",
                        "description": "If true, append to existing file instead of overwriting",
                        "default": False
                    }
                },
                "required": ["path", "content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_directory",
            "description": "List files and directories in a given path.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Relative path to the directory (default: root)",
                        "default": ""
                    },
                    "recursive": {
                        "type": "boolean",
                        "description": "If true, list recursively up to 2 levels deep",
                        "default": False
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "file_exists",
            "description": "Check if a file or directory exists.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Relative path to check"
                    }
                },
                "required": ["path"]
            }
        }
    }
]


def read_file(path: str, max_lines: int = 200) -> dict:
    """Read file contents."""
    try:
        full_path = _validate_path(path)
        if not full_path.exists():
            return {"success": False, "error": f"File not found: {path}"}
        if not full_path.is_file():
            return {"success": False, "error": f"Not a file: {path}"}

        with open(full_path, 'r', encoding='utf-8', errors='replace') as f:
            lines = f.readlines()[:max_lines]
            content = ''.join(lines)
            truncated = len(lines) >= max_lines

        return {
            "success": True,
            "content": content,
            "lines": len(lines),
            "truncated": truncated,
            "path": str(path)
        }
    except PermissionError as e:
        return {"success": False, "error": str(e)}
    except Exception as e:
        return {"success": False, "error": f"Error reading file: {e}"}


def write_file(path: str, content: str, append: bool = False) -> dict:
    """Write content to file."""
    try:
        full_path = _validate_path(path)

        # Create parent directories if needed
        full_path.parent.mkdir(parents=True, exist_ok=True)

        mode = 'a' if append else 'w'
        with open(full_path, mode, encoding='utf-8') as f:
            f.write(content)

        return {
            "success": True,
            "path": str(path),
            "bytes_written": len(content.encode('utf-8')),
            "action": "appended" if append else "written"
        }
    except PermissionError as e:
        return {"success": False, "error": str(e)}
    except Exception as e:
        return {"success": False, "error": f"Error writing file: {e}"}


def list_directory(path: str = "", recursive: bool = False) -> dict:
    """List directory contents."""
    try:
        full_path = _validate_path(path) if path else SANDBOX_ROOT
        if not full_path.exists():
            return {"success": False, "error": f"Directory not found: {path}"}
        if not full_path.is_dir():
            return {"success": False, "error": f"Not a directory: {path}"}

        entries = []

        if recursive:
            for item in full_path.rglob("*"):
                # Limit depth to 2 levels
                rel_path = item.relative_to(full_path)
                if len(rel_path.parts) <= 2:
                    entries.append({
                        "name": str(rel_path),
                        "type": "directory" if item.is_dir() else "file",
                        "size": item.stat().st_size if item.is_file() else None
                    })
        else:
            for item in full_path.iterdir():
                entries.append({
                    "name": item.name,
                    "type": "directory" if item.is_dir() else "file",
                    "size": item.stat().st_size if item.is_file() else None
                })

        # Sort: directories first, then files
        entries.sort(key=lambda x: (x["type"] != "directory", x["name"]))

        return {
            "success": True,
            "path": str(path) or ".",
            "count": len(entries),
            "entries": entries[:100]  # Limit to 100 entries
        }
    except PermissionError as e:
        return {"success": False, "error": str(e)}
    except Exception as e:
        return {"success": False, "error": f"Error listing directory: {e}"}


def file_exists(path: str) -> dict:
    """Check if file/directory exists."""
    try:
        full_path = _validate_path(path)
        exists = full_path.exists()
        return {
            "success": True,
            "exists": exists,
            "path": str(path),
            "type": "directory" if full_path.is_dir() else "file" if full_path.is_file() else None
        }
    except PermissionError as e:
        return {"success": False, "error": str(e)}
    except Exception as e:
        return {"success": False, "error": f"Error checking path: {e}"}


# Tool dispatcher
TOOL_FUNCTIONS = {
    "read_file": read_file,
    "write_file": write_file,
    "list_directory": list_directory,
    "file_exists": file_exists
}


def execute_tool(tool_name: str, arguments: dict) -> str:
    """Execute a tool and return JSON result."""
    if tool_name not in TOOL_FUNCTIONS:
        return json.dumps({"success": False, "error": f"Unknown tool: {tool_name}"})

    result = TOOL_FUNCTIONS[tool_name](**arguments)
    return json.dumps(result, indent=2)


if __name__ == "__main__":
    # Test the tools
    print("Testing filesystem tools...")
    print(execute_tool("list_directory", {"path": "", "recursive": False}))
    print(execute_tool("file_exists", {"path": "CLAUDE.md"}))
