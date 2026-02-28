#!/usr/bin/env python3
"""
Bulk Index Checkpoints
Quick script to index all existing checkpoints into Qdrant vector memory.
"""

import sys
from pathlib import Path

# Add tools directory to path
RHIZ_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(RHIZ_ROOT / "tools" / "rhiz-mcp" / "src"))
sys.path.insert(0, str(RHIZ_ROOT / "core" / "memory" / "scripts"))

from ingest import CheckpointIngestor


def bulk_index_all_checkpoints():
    """Index all checkpoint files into Qdrant"""
    checkpoints_dir = RHIZ_ROOT / "core" / "memory" / "checkpoints"
    checkpoint_files = list(checkpoints_dir.glob("session_*.yaml"))

    print(f"Found {len(checkpoint_files)} checkpoint files")

    if not checkpoint_files:
        print("No checkpoints to index")
        return 0

    # Initialize ingester
    ingester = CheckpointIngestor(
        qdrant_host="localhost",
        qdrant_port=6333,
        collection_name="rhiz_memories"
    )

    indexed_count = 0
    skipped_count = 0

    for cp_file in checkpoint_files:
        try:
            ingester.ingest_checkpoint(cp_file)
            indexed_count += 1
            print(f"[OK] {cp_file.name}")
        except Exception as e:
            # Likely already indexed - skip silently
            if "already exists" in str(e).lower():
                skipped_count += 1
            else:
                print(f"[ERR] {cp_file.name}: {e}")

    print(f"\n[DONE] Indexed: {indexed_count}")
    if skipped_count > 0:
        print(f"[SKIP] Already indexed: {skipped_count}")

    return indexed_count


if __name__ == "__main__":
    try:
        count = bulk_index_all_checkpoints()
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
