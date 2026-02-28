import os
from pathlib import Path

rhiz_root = os.environ.get("RHIZ_ROOT", "NOT_SET")
print(f"RHIZ_ROOT env: '{rhiz_root}'")
print(f"RHIZ_ROOT length: {len(rhiz_root)}")
print(f"RHIZ_ROOT repr: {repr(rhiz_root)}")

if rhiz_root != "NOT_SET":
    root_path = Path(rhiz_root)
    print(f"\nPath object: {root_path}")
    print(f"Path exists: {root_path.exists()}")

    checkpoint_dir = root_path / "core" / "memory" / "checkpoints"
    print(f"\nCheckpoint dir: {checkpoint_dir}")
    print(f"Checkpoint dir exists: {checkpoint_dir.exists()}")
