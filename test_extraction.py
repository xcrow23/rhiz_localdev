#!/usr/bin/env python3
"""Test extraction functions."""

import yaml
from pathlib import Path
from datetime import datetime

def extract_session_date(checkpoint: dict) -> str:
    """Extract date with fallback to created timestamp."""
    print(f"  Checking session_date: {'session_date' in checkpoint}")
    print(f"  Checking created: {'created' in checkpoint}")
    if "created" in checkpoint:
        print(f"  Created value: {checkpoint['created']}")

    if "session_date" in checkpoint:
        return checkpoint["session_date"]
    if "created" in checkpoint:
        try:
            created_dt = datetime.fromisoformat(checkpoint["created"])
            return created_dt.date().isoformat()
        except (ValueError, AttributeError) as e:
            print(f"  Error parsing: {e}")
            pass
    return "unknown"

# Test with actual checkpoint
checkpoint_path = Path("C:/Users/dread/documents/Rhiz/origin/core/memory/checkpoints/session_20260103_infrastructure_operational.yaml")
with open(checkpoint_path) as f:
    data = yaml.safe_load(f)

print("Full structure keys:", data.keys())
print()

# Unwrap if needed
if "checkpoint" in data:
    checkpoint = data["checkpoint"]
    print("After unwrap keys:", checkpoint.keys())
    print()

print("Testing extract_session_date:")
result = extract_session_date(checkpoint)
print(f"Result: {result}")
print()

print("Testing session_id extraction:")
session_id = checkpoint.get("session_id", "unknown")
print(f"Session ID: {session_id}")
