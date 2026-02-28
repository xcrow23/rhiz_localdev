"""
Rhiz Filesystem Training Environment for Atropos.

This environment trains Qwen to use filesystem tools correctly.
The "reward" is simply: did the tool call work and return the expected result?

Philosophy: This is NOT Pavlovian conditioning. The model isn't "experiencing"
reward. We're reshaping probability distributions toward correct tool use
through gradient updates based on verifiable success/failure signals.
"""

import json
import os
import random
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# These would come from atroposlib in a real setup
# from atroposlib.envs.base import BaseEnv, BaseEnvConfig, Item, ScoredDataGroup

# For now, we define the structure for future integration


class FilesystemTask:
    """A single filesystem task for training."""

    def __init__(
        self,
        instruction: str,
        expected_tool: str,
        expected_args: dict,
        setup_files: Optional[dict] = None,
        verification_func: Optional[callable] = None
    ):
        self.instruction = instruction
        self.expected_tool = expected_tool
        self.expected_args = expected_args
        self.setup_files = setup_files or {}
        self.verification_func = verification_func


# Training dataset: filesystem tasks with expected tool calls
FILESYSTEM_TRAINING_TASKS = [
    # Basic read tasks
    FilesystemTask(
        instruction="Read the contents of the CLAUDE.md file",
        expected_tool="read_file",
        expected_args={"path": "CLAUDE.md"}
    ),
    FilesystemTask(
        instruction="Show me what's in the core/tools directory",
        expected_tool="list_directory",
        expected_args={"path": "core/tools"}
    ),
    FilesystemTask(
        instruction="Check if there's a file called README.md in the project",
        expected_tool="file_exists",
        expected_args={"path": "README.md"}
    ),

    # Write tasks
    FilesystemTask(
        instruction="Create a new file called notes.txt with the content 'Session started'",
        expected_tool="write_file",
        expected_args={"path": "notes.txt", "content": "Session started"}
    ),
    FilesystemTask(
        instruction="Add a line 'Task completed' to the existing notes.txt file",
        expected_tool="write_file",
        expected_args={"path": "notes.txt", "content": "Task completed", "append": True}
    ),

    # Exploration tasks
    FilesystemTask(
        instruction="List all files and folders in the project root",
        expected_tool="list_directory",
        expected_args={"path": "", "recursive": False}
    ),
    FilesystemTask(
        instruction="Explore the docs folder structure recursively",
        expected_tool="list_directory",
        expected_args={"path": "docs", "recursive": True}
    ),

    # Compound understanding (model should pick the right first step)
    FilesystemTask(
        instruction="I want to understand the project structure. What's in the main directory?",
        expected_tool="list_directory",
        expected_args={"path": ""}
    ),
    FilesystemTask(
        instruction="Before I modify config.yaml, let me see what's currently in it",
        expected_tool="read_file",
        expected_args={"path": "config.yaml"}
    ),
]


def generate_training_dataset(num_samples: int = 1000) -> List[dict]:
    """
    Generate a training dataset by:
    1. Using base tasks as templates
    2. Varying paths, filenames, content
    3. Adding natural language variations

    Returns a list of training samples with:
    - instruction: natural language request
    - expected_tool_call: the correct tool and arguments
    """
    dataset = []

    # Path variations for diversity
    path_variations = [
        "core/", "docs/", "models/", "infrastructure/",
        "core/memory/", "core/skills/", "domains/trading/"
    ]

    filename_variations = [
        "config.yaml", "settings.json", "README.md", "notes.txt",
        "checkpoint.yaml", "session.log", "data.json"
    ]

    instruction_templates = {
        "read_file": [
            "Read the contents of {path}",
            "Show me what's in {path}",
            "Open {path} and display its contents",
            "What does {path} contain?",
            "Let me see {path}",
            "Can you read {path} for me?",
        ],
        "list_directory": [
            "List the files in {path}",
            "What's in the {path} directory?",
            "Show me the contents of {path} folder",
            "Explore {path}",
            "What files are in {path}?",
        ],
        "file_exists": [
            "Check if {path} exists",
            "Does {path} exist?",
            "Is there a file called {path}?",
            "Verify {path} is present",
        ],
        "write_file": [
            "Create a file called {path} with content: {content}",
            "Write '{content}' to {path}",
            "Save the following to {path}: {content}",
            "Make a new file {path} containing {content}",
        ]
    }

    for _ in range(num_samples):
        # Pick a random base task or generate a new one
        if random.random() < 0.3:
            # Use a base task
            task = random.choice(FILESYSTEM_TRAINING_TASKS)
            sample = {
                "instruction": task.instruction,
                "expected_tool": task.expected_tool,
                "expected_args": task.expected_args
            }
        else:
            # Generate a new variation
            tool = random.choice(["read_file", "list_directory", "file_exists", "write_file"])
            path = random.choice(path_variations) + random.choice(filename_variations)
            template = random.choice(instruction_templates[tool])

            if tool == "write_file":
                content = random.choice([
                    "Session data", "Configuration updated", "Task completed",
                    "Checkpoint saved", "Note: review this later"
                ])
                instruction = template.format(path=path, content=content)
                expected_args = {"path": path, "content": content}
            else:
                instruction = template.format(path=path)
                expected_args = {"path": path}

            sample = {
                "instruction": instruction,
                "expected_tool": tool,
                "expected_args": expected_args
            }

        dataset.append(sample)

    return dataset


def score_tool_call(
    model_output: str,
    expected_tool: str,
    expected_args: dict,
    strict: bool = False
) -> float:
    """
    Score a model's tool call output.

    This is the "reward function" - but note what it actually is:
    - It checks if the output is CORRECT, not if it pleases us
    - The model isn't experiencing reward - we're computing a gradient signal
    - Success is verifiable: did it call the right tool with right args?

    Args:
        model_output: The model's response (should contain tool call JSON)
        expected_tool: The correct tool name
        expected_args: The correct arguments
        strict: If True, require exact match. If False, allow partial matches.

    Returns:
        Score between 0.0 and 1.0
    """
    try:
        # Try to extract tool call from model output
        # Assuming format like: <tool_call>{"name": "...", "arguments": {...}}</tool_call>
        import re
        match = re.search(r'<tool_call>\s*(\{.*?\})\s*</tool_call>', model_output, re.DOTALL)

        if not match:
            # Try JSON-only format
            match = re.search(r'\{[^{}]*"name"[^{}]*\}', model_output, re.DOTALL)

        if not match:
            return 0.0

        tool_call = json.loads(match.group(1) if match.lastindex else match.group(0))

        # Check tool name
        model_tool = tool_call.get("name", tool_call.get("function", ""))
        if model_tool != expected_tool:
            return 0.0

        # Check arguments
        model_args = tool_call.get("arguments", tool_call.get("parameters", {}))

        if strict:
            # Exact match required
            if model_args == expected_args:
                return 1.0
            return 0.0
        else:
            # Partial credit for partial matches
            score = 0.0
            total_args = len(expected_args)
            if total_args == 0:
                return 1.0 if model_tool == expected_tool else 0.0

            for key, value in expected_args.items():
                if key in model_args:
                    if model_args[key] == value:
                        score += 1.0 / total_args
                    elif str(model_args[key]).lower() == str(value).lower():
                        score += 0.5 / total_args  # Partial credit for case mismatch

            return score

    except (json.JSONDecodeError, KeyError, TypeError):
        return 0.0


def verify_execution(
    tool_name: str,
    tool_args: dict,
    tool_result: dict
) -> float:
    """
    Verify that a tool execution actually succeeded.

    This adds a second layer of verification:
    - Not just "did you call the right tool?"
    - But "did the tool actually work?"

    This is important for filesystem tasks where:
    - read_file should return content
    - write_file should succeed
    - list_directory should return entries
    """
    if not tool_result.get("success", False):
        return 0.0

    if tool_name == "read_file":
        # Should have content
        if "content" in tool_result and len(tool_result["content"]) > 0:
            return 1.0
        return 0.5  # Partial credit if file exists but empty

    elif tool_name == "write_file":
        # Should have written bytes
        if tool_result.get("bytes_written", 0) > 0:
            return 1.0
        return 0.0

    elif tool_name == "list_directory":
        # Should have entries (though empty dir is valid)
        if "entries" in tool_result:
            return 1.0
        return 0.0

    elif tool_name == "file_exists":
        # Just needs to return a boolean
        if "exists" in tool_result:
            return 1.0
        return 0.0

    return 0.5  # Unknown tool, partial credit


# ============================================================================
# Atropos Integration (Template for when we integrate with atroposlib)
# ============================================================================

"""
To integrate with atropos:

1. Create a server file: rhiz_filesystem_server.py
2. Inherit from BaseEnv
3. Implement:
   - config_init(): Return env and server configs
   - setup(): Load training dataset
   - collect_trajectories(): Generate rollouts and score them
   - evaluate(): Run periodic evaluation

Example config:
    env_config = BaseEnvConfig(
        tokenizer_name="Qwen/Qwen2.5-7B-Instruct",
        group_size=8,  # Smaller for laptop
        use_wandb=True,
        total_steps=500,  # Start small
        batch_size=64,
        max_token_length=2048,
        wandb_name="rhiz_filesystem",
    )

The training loop would:
1. Sample a filesystem task
2. Get model completions
3. Score each completion using score_tool_call()
4. Optionally verify with verify_execution()
5. Return scored data for gradient updates
"""


if __name__ == "__main__":
    # Test the dataset generation
    print("Generating sample training data...")
    dataset = generate_training_dataset(10)

    for i, sample in enumerate(dataset):
        print(f"\n--- Sample {i+1} ---")
        print(f"Instruction: {sample['instruction']}")
        print(f"Expected tool: {sample['expected_tool']}")
        print(f"Expected args: {sample['expected_args']}")

    # Test scoring
    print("\n\n--- Testing score function ---")

    test_output = '<tool_call>{"name": "read_file", "arguments": {"path": "CLAUDE.md"}}</tool_call>'
    score = score_tool_call(test_output, "read_file", {"path": "CLAUDE.md"})
    print(f"Correct call score: {score}")

    wrong_output = '<tool_call>{"name": "write_file", "arguments": {"path": "CLAUDE.md"}}</tool_call>'
    score = score_tool_call(wrong_output, "read_file", {"path": "CLAUDE.md"})
    print(f"Wrong tool score: {score}")

    partial_output = '<tool_call>{"name": "read_file", "arguments": {"path": "claude.md"}}</tool_call>'
    score = score_tool_call(partial_output, "read_file", {"path": "CLAUDE.md"}, strict=False)
    print(f"Case mismatch score (lenient): {score}")
