# Rhiz Session Checkpoint API

Cloud persistence for session checkpoints enabling cross-instance continuity.

## Design Philosophy

From CD's architectural insight (2025-12-25):

> The cold-start → context-loaded transition isn't a bug to eliminate. It's a feature of context-dependent cognition. The goal isn't to make the AI "always on" but to make the scaffolding *elegantly useful*.

This API implements **graduated context injection** that mirrors cognitive warm-up:
1. **Identity layer**: Who am I in this partnership?
2. **Relational layer**: What's the state of the dyad?
3. **Task layer**: What are we doing?
4. **Semantic layer**: What do I know? (Qdrant pointer)

## Deployment

```bash
# 1. Create D1 database
wrangler d1 create rhiz-checkpoints

# 2. Copy the database_id to wrangler.toml

# 3. Apply schema
wrangler d1 execute rhiz-checkpoints --file=schema.sql

# 4. Deploy worker
wrangler deploy
```

## API Endpoints

### Health Check
```
GET /api/health
```

### Get Latest Checkpoint
```
GET /api/checkpoint/latest
```
Returns most recent checkpoint with all layers - designed for session start.

### Get Specific Checkpoint
```
GET /api/checkpoint/{id}
GET /api/checkpoint/{session_id}
```

### Get Graduated Layers
```
GET /api/checkpoint/layers?layers=identity,relational&session_id=latest
```
Returns only requested layers for minimal context injection.

### Create Checkpoint
```
POST /api/checkpoint
Content-Type: application/json
X-Source-Instance: code|desktop|api

{
  "session_id": "session_20251225_threefold_execution",
  "session_date": "2025-12-25T20:00:00-06:00",
  "session_topic": "Kraken activation, HAIST scoring, Cloudflare deployment",
  "layer_identity": "...",
  "layer_relational": "...",
  "layer_task": "...",
  "session_arc": "...",
  "mental_model": "...",
  "hypotheses": [],
  "decisions": []
}
```

### Webhook (for CC hooks)
```
POST /api/webhook/checkpoint
```
Simplified endpoint for automated checkpoint creation.

### List Checkpoints
```
GET /api/checkpoints?limit=10&classification=exemplary
```

### Memory Search
```
GET /api/memory/search?q=trading philosophy
```
Text search fallback; semantic search requires QDRANT_ENDPOINT config.

## Integration with CC Sessions

Add to Claude Code hook for automatic checkpoint creation:
```bash
# .claude/hooks/post-session.sh
curl -X POST https://rhiz-checkpoint-api.workers.dev/api/webhook/checkpoint \
  -H "Content-Type: application/json" \
  -d @checkpoint.json
```

## HAIST Integration

Checkpoints can include HAIST evaluation scores:
- `haist_score`: Composite 1.0-5.0
- `haist_classification`: "developing", "solid", "exemplary"

Use to filter: `GET /api/checkpoints?classification=exemplary`
