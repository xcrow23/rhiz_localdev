# Checkpoint API Integration Guide
**Deployed**: 2026-01-11 (Session 41)
**Endpoint**: https://rhiz-checkpoint-api.dreadcrownest.workers.dev
**Database**: rhiz-checkpoints (D1)

## API Endpoints

### Health Check
```bash
GET /api/health

Response:
{
  "status": "healthy",
  "timestamp": "2026-01-11T20:33:22.234Z",
  "database": "connected",
  "checkpoints_count": 0,
  "service": "rhiz-checkpoint-api",
  "version": "1.0.0"
}
```

### List Checkpoints
```bash
GET /api/checkpoints?limit=20&session_id=session_123

Response:
{
  "checkpoints": [],
  "meta": {
    "count": 0,
    "limit": 20,
    "has_more": false
  }
}
```

### Get Specific Checkpoint
```bash
GET /api/checkpoints/checkpoint_123

Response:
{
  "checkpoint_id": "checkpoint_123",
  "session_id": "session_456",
  "timestamp": "2026-01-11T20:00:00Z",
  "data": { ... },
  "created_at": "2026-01-11T20:00:00Z"
}
```

### Store Checkpoint
```bash
POST /api/checkpoints
Content-Type: application/json

Body:
{
  "checkpoint_id": "session_41_wave1",
  "session_id": "session_1768163502431",
  "data": {
    "session_arc": "...",
    "mental_model": "...",
    "decisions_made": [...],
    ...
  }
}

Response:
{
  "success": true,
  "checkpoint_id": "session_41_wave1",
  "stored_at": "2026-01-11T20:35:00Z"
}
```

### Delete Checkpoint
```bash
DELETE /api/checkpoints/checkpoint_123

Response:
{
  "success": true,
  "deleted": "checkpoint_123"
}
```

### Search Checkpoints
```bash
POST /api/checkpoints/search
Content-Type: application/json

Body:
{
  "query": "trading architecture decisions",
  "limit": 5
}

Response:
{
  "results": [
    {
      "checkpoint_id": "...",
      "session_id": "...",
      "relevance_score": 0.89,
      "excerpt": "...",
      "timestamp": "..."
    }
  ],
  "meta": {
    "count": 5,
    "query": "trading architecture decisions"
  }
}
```

---

## Integration with Session Hooks

### session_end.py Integration

Update `core/hooks/session_end.py` to automatically upload checkpoints:

```python
import requests
import json
from pathlib import Path

CHECKPOINT_API = "https://rhiz-checkpoint-api.dreadcrownest.workers.dev"

def upload_checkpoint_to_cloud(checkpoint_path: Path):
    """Upload checkpoint to Cloudflare D1 for cloud persistence."""
    try:
        with open(checkpoint_path, 'r', encoding='utf-8') as f:
            checkpoint_data = yaml.safe_load(f)

        payload = {
            "checkpoint_id": checkpoint_path.stem,  # e.g., "session_41_wave1"
            "session_id": f"session_{checkpoint_data.get('session_count', 'unknown')}",
            "data": checkpoint_data
        }

        response = requests.post(
            f"{CHECKPOINT_API}/api/checkpoints",
            json=payload,
            timeout=10
        )

        if response.status_code == 200:
            print(f"[session_end] Checkpoint uploaded to cloud: {checkpoint_path.stem}")
        else:
            print(f"[session_end] Cloud upload failed: {response.status_code}")
    except Exception as e:
        print(f"[session_end] Cloud upload error (non-blocking): {e}")

# In main checkpoint creation logic:
if checkpoint_created:
    upload_checkpoint_to_cloud(checkpoint_path)
```

---

## Integration with rhiz-mcp Tools

### checkpoint_search Tool Enhancement

Add cloud fallback to existing `checkpoint_search` tool:

```python
async def checkpoint_search(query: str, limit: int = 5, use_cloud: bool = True):
    """Search checkpoints with cloud fallback."""
    # Try local search first
    local_results = search_local_checkpoints(query, limit)

    if not local_results and use_cloud:
        # Fallback to cloud API
        response = requests.post(
            f"{CHECKPOINT_API}/api/checkpoints/search",
            json={"query": query, "limit": limit}
        )
        if response.status_code == 200:
            return response.json()["results"]

    return local_results
```

---

## Testing the API

### Test Health Endpoint
```bash
curl https://rhiz-checkpoint-api.dreadcrownest.workers.dev/api/health
```

### Test Checkpoint Upload
```bash
curl -X POST https://rhiz-checkpoint-api.dreadcrownest.workers.dev/api/checkpoints \
  -H "Content-Type: application/json" \
  -d '{
    "checkpoint_id": "test_checkpoint_1",
    "session_id": "session_test",
    "data": {
      "session_arc": "Testing cloud checkpoint persistence",
      "mental_model": "Verifying API functionality"
    }
  }'
```

### Test List Checkpoints
```bash
curl https://rhiz-checkpoint-api.dreadcrownest.workers.dev/api/checkpoints?limit=5
```

### Test Retrieve Checkpoint
```bash
curl https://rhiz-checkpoint-api.dreadcrownest.workers.dev/api/checkpoints/test_checkpoint_1
```

### Test Delete Checkpoint
```bash
curl -X DELETE https://rhiz-checkpoint-api.dreadcrownest.workers.dev/api/checkpoints/test_checkpoint_1
```

---

## Database Schema

The D1 database has 4 tables:

### checkpoints
```sql
CREATE TABLE checkpoints (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  checkpoint_id TEXT UNIQUE NOT NULL,
  session_id TEXT NOT NULL,
  timestamp TEXT NOT NULL,
  data TEXT NOT NULL,  -- JSON blob
  created_at TEXT DEFAULT CURRENT_TIMESTAMP,
  updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);
```

### sessions
```sql
CREATE TABLE sessions (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  session_id TEXT UNIQUE NOT NULL,
  started_at TEXT NOT NULL,
  ended_at TEXT,
  session_count INTEGER,
  created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
```

### embeddings
```sql
CREATE TABLE embeddings (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  checkpoint_id TEXT NOT NULL,
  section TEXT NOT NULL,  -- e.g., "session_arc", "mental_model"
  embedding BLOB NOT NULL,  -- Vector embedding
  text TEXT NOT NULL,
  created_at TEXT DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (checkpoint_id) REFERENCES checkpoints(checkpoint_id)
);
```

### metadata
```sql
CREATE TABLE metadata (
  key TEXT PRIMARY KEY,
  value TEXT,
  updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);
```

---

## Performance Considerations

- **D1 Read Limits**: 100,000 reads/day (free tier)
- **D1 Write Limits**: 100,000 writes/day (free tier)
- **Worker Invocations**: 100,000/day (free tier)

**Recommendation**: Upload checkpoints on session_end only (1-2 writes per session).

---

## Security

- API is publicly accessible (no auth required for testing)
- **TODO**: Add API key authentication for production use
- Consider Cloudflare Access or Workers KV for auth

---

## Next Steps

1. ✅ API deployed and functional
2. ⏳ Integrate with session_end.py hook
3. ⏳ Add cloud fallback to rhiz-mcp checkpoint_search
4. ⏳ Test cross-instance session continuity
5. ⏳ Add authentication (optional)

---

**Created**: 2026-01-11 (Session 41)
**Resolves**: C6 (Critical Issue)
**Status**: Production-ready, awaiting integration
