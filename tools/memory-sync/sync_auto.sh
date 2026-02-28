#!/bin/bash
# Automated sync script for cron/systemd
# Syncs local Qdrant to cloud on a schedule

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
SYNC_SCRIPT="$PROJECT_ROOT/core/memory/scripts/sync_cloud.py"
LOG_FILE="$SCRIPT_DIR/sync_auto.log"
VENV="$PROJECT_ROOT/venv"

# Function to log with timestamp
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log "========================================"
log "Automated Memory Sync Started"
log "========================================"

# Check if local Qdrant is running
if ! curl -s http://localhost:6333/collections/rhiz_memories >/dev/null 2>&1; then
    log "ERROR: Local Qdrant not accessible"
    log "Skipping sync - Qdrant may be offline"
    exit 1
fi

# Get current point count
LOCAL_COUNT=$(curl -s http://localhost:6333/collections/rhiz_memories | grep -o '"points_count":[0-9]*' | grep -o '[0-9]*')
log "Local Qdrant: $LOCAL_COUNT points"

# Activate venv and run sync
source "$VENV/bin/activate"
python3 "$SYNC_SCRIPT" --tunnel 2>&1 | while read line; do
    log "$line"
done

SYNC_EXIT=${PIPESTATUS[0]}

if [ $SYNC_EXIT -eq 0 ]; then
    log "✓ Automated sync completed successfully"
else
    log "✗ Automated sync failed (exit code: $SYNC_EXIT)"
fi

log "========================================"
log ""

exit $SYNC_EXIT
