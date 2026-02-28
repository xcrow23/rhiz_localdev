#!/bin/bash
# Sync local Qdrant memories to cloud
# This is the main sync script to run manually

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
SYNC_SCRIPT="$PROJECT_ROOT/core/memory/scripts/sync_cloud.py"

echo "========================================"
echo "Rhiz Memory Cloud Sync"
echo "========================================"
echo "Local -> Cloud synchronization"
echo ""

# Check if sync script exists
if [ ! -f "$SYNC_SCRIPT" ]; then
    echo "Error: Sync script not found at $SYNC_SCRIPT"
    exit 1
fi

# Check Python dependencies
echo "Checking dependencies..."
python3 -c "from qdrant_client import QdrantClient" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "Error: qdrant-client not installed"
    echo ""
    echo "Install with:"
    echo "  pip3 install qdrant-client"
    exit 1
fi

# Check local Qdrant
echo "Checking local Qdrant..."
curl -s http://localhost:6333/collections/rhiz_memories >/dev/null
if [ $? -ne 0 ]; then
    echo "Error: Local Qdrant not accessible on localhost:6333"
    echo ""
    echo "Start with:"
    echo "  docker-compose up -d qdrant"
    exit 1
fi

echo "✓ All checks passed"
echo ""

# Run sync with automatic tunnel
echo "Starting sync (with automatic SSH tunnel)..."
python3 "$SYNC_SCRIPT" --tunnel

SYNC_EXIT=$?

if [ $SYNC_EXIT -eq 0 ]; then
    echo ""
    echo "========================================"
    echo "✓ Sync completed successfully!"
    echo "========================================"

    # Log the sync
    echo "$(date '+%Y-%m-%d %H:%M:%S') - Sync completed" >> "$SCRIPT_DIR/sync.log"
else
    echo ""
    echo "========================================"
    echo "✗ Sync failed (exit code: $SYNC_EXIT)"
    echo "========================================"

    # Log the failure
    echo "$(date '+%Y-%m-%d %H:%M:%S') - Sync failed (exit: $SYNC_EXIT)" >> "$SCRIPT_DIR/sync.log"
fi

exit $SYNC_EXIT
