"""Test rhiz-mcp components on Windows"""
import os
import sys
from pathlib import Path

# Set up environment
os.environ['RHIZ_ROOT'] = r'C:\Users\dread\Documents\Rhiz_LocalDev'

# Test imports
print("Testing imports...")
try:
    from src.dyad_state import DyadState
    from src.checkpoint_manager import CheckpointManager
    print("[OK] Imports successful")
except ImportError as e:
    print(f"[FAIL] Import failed: {e}")
    sys.exit(1)

# Test DyadState path resolution
print("\nTesting DyadState path resolution...")
dyad = DyadState()
print(f"  Dyad path: {dyad.state_path}")
print(f"  Path exists: {dyad.state_path.exists()}")

if dyad.state_path.exists():
    try:
        state = dyad.load_state()
        print(f"[OK] Dyad state loaded")
        print(f"  Sections: {list(state.keys())}")
    except Exception as e:
        print(f"[FAIL] Failed to load dyad state: {e}")
else:
    print("[INFO] Dyad state file doesn't exist yet - this is OK for fresh setup")

# Test CheckpointManager path resolution
print("\nTesting CheckpointManager path resolution...")
checkpoint_mgr = CheckpointManager()
print(f"  Checkpoint dir: {checkpoint_mgr.checkpoint_dir}")
print(f"  Dir exists: {checkpoint_mgr.checkpoint_dir.exists()}")

try:
    checkpoints = checkpoint_mgr.list_checkpoints(limit=3)
    print(f"[OK] Checkpoint manager working")
    print(f"  Found {len(checkpoints)} checkpoints")
    if checkpoints:
        print(f"  Most recent: {checkpoints[0]['filename']}")
except Exception as e:
    print(f"[FAIL] Failed to list checkpoints: {e}")

# Test server can be imported
print("\nTesting server module...")
try:
    from src import server
    print("[OK] Server module imports successfully")
    print(f"  Server name: {server.app.name}")
except Exception as e:
    print(f"[FAIL] Server import failed: {e}")

print("\n=== All Windows compatibility tests complete ===")
