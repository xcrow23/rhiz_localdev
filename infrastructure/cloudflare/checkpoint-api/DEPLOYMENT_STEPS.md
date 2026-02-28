# Cloudflare Checkpoint API - Deployment Steps
## For Captain

The Checkpoint API is fully coded and ready for deployment. Requires Cloudflare authentication.

---

## Prerequisites

1. **Cloudflare API Token**: Create at https://developers.cloudflare.com/fundamentals/api/get-started/create-token/
   - Required permissions: Workers Scripts (Edit), D1 (Edit)
   - Set environment variable: `CLOUDFLARE_API_TOKEN=your_token`

2. **Wrangler CLI**: Already installed at `C:\Users\dread\AppData\Roaming\npm\wrangler`

---

## Deployment Steps

Run from PowerShell (not WSL - platform mismatch issue):

```powershell
# 1. Set API token (one-time)
$env:CLOUDFLARE_API_TOKEN = "your_token_here"

# 2. Navigate to project
cd C:\Users\dread\Documents\Rhiz_LocalDev\infrastructure\cloudflare\checkpoint-api

# 3. Create D1 database
wrangler d1 create rhiz-checkpoints

# 4. Copy the database_id from output (looks like: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx)

# 5. Edit wrangler.toml and replace database_id placeholder
# Line 10: database_id = "paste-id-here"

# 6. Apply schema to database
wrangler d1 execute rhiz-checkpoints --file=schema.sql

# 7. Deploy worker
wrangler deploy

# 8. Test health endpoint
curl https://rhiz-checkpoint-api.<your-subdomain>.workers.dev/api/health
```

---

## Expected Output

After deployment:
```json
{
  "status": "healthy",
  "database": "connected",
  "timestamp": "2025-12-25T..."
}
```

---

## API Endpoints (Once Deployed)

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/health` | GET | Health check |
| `/api/checkpoint/latest` | GET | Get most recent checkpoint |
| `/api/checkpoint/{id}` | GET | Get specific checkpoint |
| `/api/checkpoint/layers` | GET | Get graduated layers |
| `/api/checkpoint` | POST | Create new checkpoint |
| `/api/webhook/checkpoint` | POST | Simplified checkpoint creation |
| `/api/checkpoints` | GET | List checkpoints |
| `/api/memory/search` | GET | Text search (semantic needs Qdrant) |

---

## Integration with Claude Code

After deployment, can add to CC hooks for auto-checkpoint:

```bash
# .claude/hooks/post-session.sh
curl -X POST https://rhiz-checkpoint-api.YOUR_SUBDOMAIN.workers.dev/api/webhook/checkpoint \
  -H "Content-Type: application/json" \
  -d @checkpoint.json
```

---

## Blocker Encountered (CC Session)

- **Issue**: Wrangler requires CLOUDFLARE_API_TOKEN
- **Attempted**: WSL → platform mismatch, PowerShell → auth required
- **Status**: Documented for Captain deployment
- **Next**: CC pivoting to Qdrant Memory Browser (autonomous)

---

Fair winds,
— First Mate
