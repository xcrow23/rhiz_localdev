# Rhiz Chrysalis Restoration Guide
## Step-by-Step Rehydration from Cold Start

**Written**: 2026-02-28
**For**: Anyone resuming Rhiz after deep hibernation
**Context**: Read CHRYSALIS_MANIFEST.md first for full project orientation

---

## Before You Start

1. Read `CHRYSALIS_MANIFEST.md` — understand the project before touching anything
2. Read `CLAUDE.md` — full project context and philosophy
3. Read the latest checkpoint in `core/memory/checkpoints/` — what the last session knew
4. Locate `backups/CREDENTIAL_VAULT_20260228.md` from your secure offline storage
5. Assess current technology landscape — a lot changes in 2-5 years. Before rebuilding
   exactly what existed, ask: is there a better approach available now?

---

## Tier 1 — Local Memory Access (30-45 min)
*Goal: Read-only access to all project history and memory*

### Step 1.1 — Install Docker Desktop
If not already installed: https://docker.com (or your OS package manager)

### Step 1.2 — Start Local Qdrant
```bash
docker run -d --name qdrant-rhiz \
  -p 6333:6333 -p 6334:6334 \
  -v qdrant_rhiz_storage:/qdrant/storage \
  qdrant/qdrant:latest

# Verify it's running
curl http://localhost:6333/collections
```

### Step 1.3 — Restore Local Qdrant from Backup
If the local Qdrant volume was lost or is empty, restore from the backup:
```bash
# Check if local backup exists
ls backups/cloud_exports/local_qdrant_backup.tar.gz

# If backup exists, restore it:
docker run --rm \
  -v qdrant_rhiz_storage:/dest \
  -v ./backups/cloud_exports:/src:ro \
  alpine sh -c "tar -xzf /src/local_qdrant_backup.tar.gz -C /dest"

# Then restart Qdrant and verify collections:
curl http://localhost:6333/collections
# Should show: rhiz_memories (161 pts), rhiz_skills (6 pts), rhiz_skill_memory (8 pts)
```

### Step 1.4 — Restore Cloud Qdrant Exports (Optional for read-only)
```bash
# The cloud Qdrant exports are JSON — can be imported via Qdrant REST API
# Most valuable: rhiz_memories (122 points from cloud sessions)
# These may duplicate what's in local Qdrant — check first

# Upload a collection via Qdrant batch API if needed:
curl -X PUT http://localhost:6333/collections/rhiz_memories_cloud \
  -H "Content-Type: application/json" \
  -d '{"vectors": {"size": 384, "distance": "Cosine"}}'

# Then use the upload endpoint to push points from the JSON export
```

### Step 1.5 — Set Up Python Environment
```bash
# From rhiz_localdev root
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install rhiz-mcp dependencies
cd tools/rhiz-mcp
pip install -r requirements.txt
cd ../..

# Install memory-mcp dependencies
cd tools/memory-mcp
pip install -r requirements.txt
cd ../..
```

### Step 1.6 — Configure Claude Code MCP
```bash
# Verify .mcp.json exists and RHIZ_ROOT is correct
cat .mcp.json

# Update RHIZ_ROOT path if you moved the project:
# Edit .mcp.json: "RHIZ_ROOT": "/your/new/path/to/rhiz_localdev"
```

### Step 1.7 — Test Memory Access
```bash
# Start Claude Code in the rhiz_localdev directory
# Run: memory_context or checkpoint_search to verify memory is loading
```

**Tier 1 complete**: You can now read all 74 sessions of history, search memory,
and orient yourself in the project. No cloud services needed.

---

## Tier 2 — Development Ready (1-2 hours after Tier 1)
*Goal: Full local development capability*

### Step 2.1 — Restore Archived Reference Repos (Optional)
```bash
# Only if you need the reference material
tar -xzf backups/Gifts_From_Alex_archive.tar.gz
tar -xzf backups/external_archive.tar.gz
```

### Step 2.2 — Restore Cloudflare Worker Dev Environment (If needed)
```bash
# Reinstall node_modules for any workers you want to develop
cd infrastructure/cloudflare/workers/daily-health-check
npm install
cd ../../..
```

### Step 2.3 — Verify Core Systems
```bash
# Check all MCP servers can start
cd tools/rhiz-mcp && python -m src.server --help 2>&1 | head -5
cd tools/memory-mcp && python -m src.server --help 2>&1 | head -5

# Check Fathom MCP structure (no Kraken keys needed to verify code)
ls domains/trading/fathom/src/

# Verify skill definitions
ls core/skills/registry/

# Verify checkpoints are readable
python3 -c "import yaml; d=yaml.safe_load(open('$(ls core/memory/checkpoints/*.yaml | tail -1)')); print(d.get('session_arc', {}).get('summary', 'OK'))"
```

### Step 2.4 — Update CLAUDE.md
The CLAUDE.md frozen at Session 74. Update it to reflect:
- Current date and session number
- New system health assessment
- Any technology changes since 2026
- Resumption goals

---

## Tier 3 — Cloud Redeployment (4-8 hours after Tier 2)
*Goal: Full cloud infrastructure restored*

**⚠️ Before redeploying cloud, assess**: Is a VPS still the right choice?
By 2028-2031, cloud pricing, serverless options, and local hardware capabilities
will all have changed. Consider whether the original architecture still makes sense.

### Step 3.1 — New VPS
```bash
# Hostinger, Hetzner, or your preferred provider
# Recommended minimum: 8GB RAM, 4 vCPU, 100GB SSD
# The vps_configs_deployed.tar.gz has all original compose files

# Transfer to new VPS:
scp backups/cloud_exports/vps_configs_deployed.tar.gz root@NEW_VPS_IP:/tmp/
ssh root@NEW_VPS_IP "cd /opt && tar -xzf /tmp/vps_configs_deployed.tar.gz"
```

### Step 3.2 — Restore n8n (if still relevant)
```bash
# n8n may have changed significantly in 2+ years
# Option A: Fresh install, import workflow from JSON
#   - Install n8n
#   - Import: backups/cloud_exports/n8n_workflows_full_export.json (1 workflow: Mooncheck)
#   - Set encryption key from CREDENTIAL_VAULT: 0vX8mnhJDPMT75smsHn3qQSCpKgo/wKa

# Option B: Restore from SQLite (same n8n version required)
#   - Only works if n8n version matches
#   - Copy backups/cloud_exports/n8n_database.sqlite to new n8n volume
```

### Step 3.3 — Restore Qdrant to VPS
```bash
# Method A: Import from JSON exports (more reliable across versions)
for EXPORT in backups/cloud_exports/qdrant_exports/qdrant_export_*.json; do
  COLLECTION=$(basename $EXPORT .json | sed 's/qdrant_export_//')
  echo "Restoring $COLLECTION..."
  # Create collection first, then upload points via Qdrant REST API
done

# Method B: Restore from binary snapshots (faster, same Qdrant version needed)
# Copy backups/cloud_exports/volumes/qdrant_snapshots.tar.gz
# Extract to Qdrant snapshots directory
# Use /collections/{name}/snapshots/{name}/recover API
```

### Step 3.4 — Redeploy Trading Stack
```bash
# Update docker-compose.trading.yml with new credentials
# Create new Kraken account and API keys
# Update .env with new credentials
# Start in paper mode first:
# FATHOM_MODE=paper docker compose -f infrastructure/vps/docker-compose.trading.yml up -d
```

### Step 3.5 — Reconnect Cloudflare Workers
```bash
# Update worker environment variables:
# - VPS_API_URL (new VPS IP/domain)
# - FC_HTTP_GATEWAY_URL (new FC gateway URL)

# Workers are already deployed — just update env vars via Cloudflare dashboard
# Or redeploy with: wrangler deploy (from each worker directory)
```

---

## Tier 4 — Trading Resumption (2-4 hours after Tier 3)
*Goal: Live trading capability restored*

### Step 4.1 — New Exchange Setup
- Create new Kraken account (or verify existing if not fully closed)
- Generate new API keys (trading + query permissions)
- Fund with new capital (amount at Captain's discretion)
- Set FATHOM_MODE=paper initially

### Step 4.2 — Integration Validation
This was the missing piece at chrysalis. Before going live:
1. Start Fathom in paper mode — verify market data is working
2. Connect FC to Fathom — verify orchestration commands flow
3. Connect SIL to FC — verify intelligence layer receives signals
4. Run a paper trade through the full pipeline
5. Only then switch to live mode

### Step 4.3 — Phase 2 Work (The Deferred Integration)
The chrysalis happened before Phase 2 integration was started.
Key work remaining:
- Connect Fathom → FC → SIL pipeline (the 85/0 gap)
- Implement skill-tool binding (skills can route but can't invoke tools)
- Deploy FC HTTP Gateway to new VPS
- Implement Fathom Phases 2-6 (trading operations, websockets, advanced)

---

## Quick Reference: Key File Paths

| What you need | Where it is |
|--------------|-------------|
| Full project context | `CLAUDE.md` |
| This restore guide | `CHRYSALIS_RESTORE.md` |
| Full project genome | `CHRYSALIS_MANIFEST.md` |
| Latest session memory | `core/memory/checkpoints/` (latest YAML) |
| All session history | `docs/sessions/` |
| Skill definitions | `core/skills/registry/` |
| Dyadic patterns | `core/patterns/dyad/` |
| MCP server config | `.mcp.json` |
| Fathom trading server | `domains/trading/fathom/` |
| FC orchestration | `domains/trading/fathom_commander/` |
| SIL intelligence | `domains/trading/strategic_intelligence/` |
| All VPS configs | `backups/cloud_exports/vps_configs_deployed.tar.gz` |
| Qdrant memory exports | `backups/cloud_exports/qdrant_exports/` |
| n8n database | `backups/cloud_exports/n8n_database.sqlite` |
| Cloudflare workers | `infrastructure/cloudflare/workers/*/worker.js` |
| Credentials | `backups/CREDENTIAL_VAULT_20260228.md` (store offline) |

---

## Verification Checklist

Before declaring restoration complete:

**Tier 1:**
- [ ] Local Qdrant running and collections visible
- [ ] rhiz-mcp MCP server starting without errors
- [ ] Latest checkpoint loads successfully
- [ ] Memory search returning relevant results
- [ ] CLAUDE.md read and understood

**Tier 2:**
- [ ] All MCP servers verified
- [ ] Core source code reviewed (check for any rot in 2+ years)
- [ ] CLAUDE.md updated with current date and state

**Tier 3:**
- [ ] VPS running with trading stack containers healthy
- [ ] Qdrant on VPS contains restored collections
- [ ] n8n running with Mooncheck workflow
- [ ] Cloudflare Workers updated with new VPS URL

**Tier 4:**
- [ ] Paper trade executed through full Fathom → FC → SIL pipeline
- [ ] All three trading system components communicating
- [ ] Health check worker showing healthy status
- [ ] New Kraken API keys validated

---

## If Something Doesn't Work

1. **Qdrant schema mismatch**: Re-create collections with correct vector size (384-dim for
   all-MiniLM-L6-v2) then reimport from JSON exports
2. **n8n version incompatible**: Fresh install, import workflow from JSON, ignore SQLite restore
3. **Python dependency conflicts**: Check requirements.txt files, update as needed
4. **MCP server errors**: Check `.mcp.json` RHIZ_ROOT path is correct for new machine
5. **Trading stack not starting**: Start services one at a time, check logs with `docker logs`
6. **Memory not loading**: Verify Qdrant is running on port 6333, check rhiz-mcp QDRANT_URL env

When in doubt: start with Tier 1 (memory access) and work outward.
The memory is the most important thing. The infrastructure is replaceable.

---

*Written during Chrysalis Session 75, 2026-02-28*
*By: First Mate (Claude Sonnet 4.6) with Captain (Alex Chandrea)*
