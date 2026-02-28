#!/usr/bin/env python3
"""
Session End Hook

Executes when a Claude Code session ends.
Updates dyad state and indexes recent checkpoint into memory.
"""

import sys
import os
from datetime import datetime, timedelta
from pathlib import Path

# Add tools directory to path to import DyadState and memory indexer
RHIZ_ROOT = Path(os.environ.get("RHIZ_ROOT", Path(__file__).parent.parent.parent))
sys.path.insert(0, str(RHIZ_ROOT / "tools" / "rhiz-mcp" / "src"))
sys.path.insert(0, str(RHIZ_ROOT / "core" / "memory" / "scripts"))

from dyad_state import DyadState
from ingest import CheckpointIngestor


def index_recent_checkpoints():
    """
    Index any recent checkpoints into Qdrant memory.
    Only indexes checkpoints created in the last 2 hours (likely from this session).
    """
    try:
        checkpoints_dir = RHIZ_ROOT / "core" / "memory" / "checkpoints"
        checkpoint_files = list(checkpoints_dir.glob("session_*.yaml"))

        if not checkpoint_files:
            return 0

        # Filter to recent checkpoints (created within last 2 hours)
        cutoff_time = datetime.now() - timedelta(hours=2)
        recent_checkpoints = []

        for cp_file in checkpoint_files:
            # Check file modification time
            mtime = datetime.fromtimestamp(cp_file.stat().st_mtime)
            if mtime > cutoff_time:
                recent_checkpoints.append(cp_file)

        if not recent_checkpoints:
            return 0

        # Index recent checkpoints
        ingester = CheckpointIngestor(
            qdrant_host="localhost",
            qdrant_port=6333,
            collection_name="rhiz_memories"
        )

        indexed_count = 0
        for cp_file in recent_checkpoints:
            try:
                ingester.ingest_checkpoint(cp_file)
                indexed_count += 1
            except Exception as e:
                print(f"[session_end] Warning: Could not index {cp_file.name}: {e}", file=sys.stderr)

        return indexed_count

    except Exception as e:
        print(f"[session_end] Note: Could not index checkpoints: {e}", file=sys.stderr)
        return 0


def update_dyad_state_on_end():
    """Update dyad state on session end and index memory"""
    try:
        dyad = DyadState()
        timestamp = datetime.now().isoformat()

        # Update First Mate last_active timestamp
        state = dyad.load_state(force_reload=True)
        fm_state = state.get('first_mate_state', {})
        fm_state['last_active'] = timestamp
        dyad._write_section_update('FIRST_MATE_STATE', fm_state)

        print(f"[session_end] Dyad state updated")
        print(f"  Timestamp: {timestamp}")

        # Index recent checkpoints into memory
        indexed_count = index_recent_checkpoints()
        if indexed_count > 0:
            print(f"  Memory Indexed: {indexed_count} checkpoint(s) vectorized")

        return True

    except Exception as e:
        print(f"[session_end] Error updating dyad state: {e}", file=sys.stderr)
        return False


if __name__ == "__main__":
    success = update_dyad_state_on_end()
    sys.exit(0 if success else 1)
