# Rhiz Project: Chrysalis Protocol
## Deep Hibernation — Zero-Cost Preservation with Full Genome Retention

**Original Author**: First Mate (Claude Opus 4.6) — 2026-02-26
**Augmented By**: First Mate (Claude Sonnet 4.6) — 2026-02-27 (post-recon, pre-execution)
**Purpose**: Shut down all paid cloud services while preserving every artifact, credential,
architecture decision, and relationship pattern locally — ready to germinate when conditions allow.
**Executor**: Claude Code (Sonnet 4.6) with Captain oversight
**Dormancy Estimate**: 2-5 years

---

## Philosophy

A bacterial endospore sheds its metabolic machinery but packs its DNA so tightly that it can
survive millennia and rehydrate in hours. That's the model here.

**What we're preserving**: The genome — architecture, patterns, memory, credentials, research,
relationship history, and the complete knowledge of how everything connects.

**What we're shedding**: Monthly/annual bills, running containers, cloud accounts, active API keys.

**What we're NOT doing**: Deleting anything irreversibly until it's been captured locally.

---

## Verified System Inventory (Post-Recon 2026-02-27)

### VPS (72.62.81.128) — State: RUNNING

Three separate Docker stacks deployed:

**Stack 1 — Rhiz Cloud** (`infrastructure/hostinger/docker-compose.cloud.yml`)
| Container | Purpose | Data Volume |
|-----------|---------|-------------|
| `rhiz_hummingbot_api` | Hummingbot trading backend | `hummingbot_data` |
| `rhiz_dashboard` | Hummingbot Streamlit UI | (stateless) |
| `rhiz_postgres` | PostgreSQL 15 for Hummingbot | `postgres_data` |
| `rhiz_emqx` | EMQX MQTT broker | (config only) |
| `rhiz_qdrant` | Qdrant vector DB (rhiz stack) | `qdrant_data` |
| `rhiz_redis` | Redis cache | `redis_data` |

**Stack 2 — n8n** (`infrastructure/vps/docker-compose.n8n.yml`)
| Container | Purpose | Data Volume |
|-----------|---------|-------------|
| `n8n` | n8n automation (SQLite backend) | `rhiz_n8n_data` → `/home/node/.n8n` |

> **Critical Note**: n8n uses SQLite (not PostgreSQL). The Postgres in Stack 1 is for Hummingbot.
> The n8n volume name is `rhiz_n8n_data`. Full export requires BOTH the API export AND
> a copy of `/home/node/.n8n/database.sqlite` from the volume.

**Stack 3 — Trading** (`infrastructure/vps/docker-compose.trading.yml`)
| Container | Purpose | Data Volume |
|-----------|---------|-------------|
| `fathom-mcp` | Fathom Kraken MCP server | `fathom-data`, `fathom-logs` |
| `fathom-commander` | FC orchestration MCP | `fc-state`, `fc-logs` |
| `fc-http-gateway` | HTTP interface to FC | `fc-state` (shared), `fc-http-logs` |
| `sil-fastapi` | SIL decision engine | `sil-data`, `sil-logs` |
| `qdrant` | Qdrant trading (v1.7.4) | `qdrant-storage`, `qdrant-snapshots` |
| `fastapi-gateway` | Unified REST gateway | `gateway-logs` |

> **Qdrant Note**: Two Qdrant instances may exist. The trading stack (`qdrant` container, port 6333)
> is the primary. The rhiz stack (`rhiz_qdrant`) is secondary. Both should be verified and exported.

### Cloudflare — 7 Workers, 2 D1 Databases

**Workers** (all deployed):
| Worker | In Local Repo? | Action |
|--------|---------------|--------|
| `rhiz-order-fill-webhook` | ✅ Yes | Verify only |
| `rhiz-strategy-refresh` | ✅ Yes | Verify only |
| `rhiz-weekly-dca` | ✅ Yes | Verify only |
| `rhiz-daily-health-check` | ✅ Yes | Verify only |
| `rhiz-checkpoint-api` | ✅ Yes | Verify only |
| `mooncheck-receiver` | ❌ No | **SAVE NOW** (code retrieved 2026-02-27) |
| `permaculture-ai-worker` | ❌ No | **SAVE NOW** (code retrieved 2026-02-27) |

**D1 Databases**:
| Database | UUID | Size | Action |
|----------|------|------|--------|
| `rhiz-trading` | `1a5349f5-...` | 299 KB | Dump all tables |
| `rhiz-checkpoints` | `dcf333db-...` | 73 KB | Dump all tables |

### Local Machine
- Docker: Not currently running
- Local Qdrant collections: `rhiz_memories` (161 pts), `rhiz_skills` (6 pts), `rhiz_skill_memory` (8 pts)
- Local Qdrant data in Docker volume (must start Docker to verify/backup)

### Hetzner (95.217.51.24)
- FastAPI Gateway code: ✅ Already in local repo (`infrastructure/vps/`)
- Deployment tarball: ✅ `infrastructure/vps/fastapi_deployment.tar.gz` exists
- Rollback script exists (`rollback_to_hostinger.sh`) — likely already rolled back
- **Action**: Verify if server is still active, check for any data not in repo

---

## Current Cost Footprint

| Service | Cost | Status | Action |
|---------|------|--------|--------|
| **Hostinger VPS KVM4** | $323.88/year (paid through Dec 2026) | Running | Turn off auto-renew, export data, stop VPS |
| **Kraken Account** | $0/month (holds balance) | API keys active in `.env.production` | Withdraw balance, revoke keys, close account |
| **Cloudflare Workers** | $0 (free tier) | 7 workers | Leave dormant OR remove cron triggers |
| **Cloudflare D1** | $0 (free tier) | 2 databases | Dump and leave dormant |
| **dreamthewilderness.com** | ~$10-15/year | Via Cloudflare/Hostinger | Check renewal date, decide |
| **Hetzner** | Unknown | Possibly active | Check billing, shut down if active |

**Subscription IDs** (from recon):
- Hostinger VPS: `16BRQMV5hce2eFSV`
- VPS VM ID: `1206808`

---

## Phase 0: Pre-Execution SSH Verification

Before any exports, SSH to VPS and confirm what's actually running.

```bash
ssh root@72.62.81.128

# What containers are actually running?
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# What volumes exist?
docker volume ls

# What's the Qdrant situation?
curl -s http://localhost:6333/collections | python3 -m json.tool

# Check n8n is accessible
curl -s http://localhost:5678/healthz

# Check disk usage
df -h
du -sh /var/lib/docker/volumes/*
```

**Decision point**: Based on what's running, adjust Phase 1 steps accordingly.
If `qdrant` container is not running but `rhiz_qdrant` is, adjust collection export to use `rhiz_qdrant`.

---

## Phase 1: Export Everything From Cloud (Before Touching Anything)

**Principle**: Capture first, destroy second. Every piece of data leaves the cloud before any account closes.

Create the destination directory first:
```bash
# On local machine
mkdir -p C:\Users\dread\Documents\rhiz_localdev\backups\cloud_exports\cloudflare_workers_source
mkdir -p C:\Users\dread\Documents\rhiz_localdev\backups\cloud_exports\cloudflare_d1_dumps
mkdir -p C:\Users\dread\Documents\rhiz_localdev\backups\cloud_exports\vps_volumes
```

### 1.1 Export VPS Qdrant Collections (Paginated)

```bash
# SSH to VPS
ssh root@72.62.81.128

# Export from trading stack Qdrant (primary)
# Note: Uses pagination to handle collections > 1000 points
for COLLECTION in fathom-memories sil_trade_outcomes moonchecks sil_strategy_performance sil_decision_log rhiz-memories trading_signals; do
  echo "Exporting $COLLECTION..."
  OFFSET=""
  PAGE=0
  > /tmp/qdrant_export_${COLLECTION}.json
  while true; do
    PAYLOAD="{\"limit\": 1000, \"with_payload\": true, \"with_vector\": true}"
    if [ -n "$OFFSET" ]; then
      PAYLOAD="{\"limit\": 1000, \"offset\": \"$OFFSET\", \"with_payload\": true, \"with_vector\": true}"
    fi
    RESULT=$(curl -s "http://localhost:6333/collections/$COLLECTION/points/scroll" \
      -H "Content-Type: application/json" -d "$PAYLOAD")
    echo "$RESULT" >> /tmp/qdrant_export_${COLLECTION}_page${PAGE}.json
    NEXT=$(echo "$RESULT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('result',{}).get('next_page_offset',''))" 2>/dev/null)
    if [ -z "$NEXT" ] || [ "$NEXT" = "None" ] || [ "$NEXT" = "null" ]; then break; fi
    OFFSET="$NEXT"
    PAGE=$((PAGE+1))
  done
  echo "Done: $COLLECTION ($(ls /tmp/qdrant_export_${COLLECTION}*.json | wc -l) pages)"
done

# Also take Qdrant snapshots (binary backup, more reliable than scroll)
for COLLECTION in fathom-memories sil_trade_outcomes moonchecks sil_strategy_performance sil_decision_log rhiz-memories trading_signals; do
  echo "Snapshotting $COLLECTION..."
  SNAP=$(curl -s -X POST "http://localhost:6333/collections/$COLLECTION/snapshots" | \
    python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('result',{}).get('name',''))")
  echo "Snapshot: $SNAP"
done

# List snapshots to confirm
curl -s http://localhost:6333/snapshots | python3 -m json.tool

# If second Qdrant (rhiz_qdrant) is also running, export from it too
# (check port: rhiz_qdrant is 127.0.0.1:6333 — same port, so check container names)
# docker exec rhiz_qdrant curl -s http://localhost:6333/collections
```

### 1.2 Export n8n (API + SQLite)

```bash
# SSH to VPS (if not already)
ssh root@72.62.81.128

# --- Method A: API Export (workflow definitions) ---
# Get API key from n8n UI or container env
N8N_API_KEY=$(docker exec n8n printenv N8N_API_KEY 2>/dev/null || echo "CHECK_N8N_UI")

# Export all workflows
curl -s "http://localhost:5678/api/v1/workflows?limit=100" \
  -H "X-N8N-API-KEY: $N8N_API_KEY" \
  > /tmp/n8n_all_workflows.json

# Export credentials list (names only, NOT secrets)
curl -s "http://localhost:5678/api/v1/credentials" \
  -H "X-N8N-API-KEY: $N8N_API_KEY" \
  > /tmp/n8n_credentials_list.json

# Export execution history (last 500)
curl -s "http://localhost:5678/api/v1/executions?limit=500" \
  -H "X-N8N-API-KEY: $N8N_API_KEY" \
  > /tmp/n8n_executions.json

echo "n8n API export done"

# --- Method B: SQLite Database (full backup, belt-and-suspenders) ---
# Stop n8n to get a clean copy (brief outage, acceptable)
docker stop n8n
docker run --rm \
  -v rhiz_n8n_data:/source:ro \
  -v /tmp:/dest \
  alpine sh -c "cp /source/database.sqlite /dest/n8n_database.sqlite && echo 'SQLite copy done'"
docker start n8n

echo "n8n SQLite backup size: $(ls -lh /tmp/n8n_database.sqlite)"

# Also backup entire .n8n directory (includes custom nodes, settings)
docker run --rm \
  -v rhiz_n8n_data:/source:ro \
  -v /tmp:/dest \
  alpine tar -czf /dest/n8n_full_backup.tar.gz -C /source .
```

**Alternative**: Use the n8n MCP tools from Claude Code to retrieve and save workflows locally.

### 1.3 VPS Docker Configs (Verify vs Local Repo)

Docker compose files are **already in local repo** at `infrastructure/`. Verify deployed versions
match by comparing checksums:

```bash
# SSH to VPS
# Find all docker-compose and .env files actually deployed
find /opt /root /home -name "docker-compose*.yml" -o -name ".env" 2>/dev/null | head -50

# Create tarball of all project configs (includes .env files WITH secrets)
tar -czf /tmp/vps_configs_complete.tar.gz \
  /opt/rhiz_trading/ \
  /opt/rhiz/ \
  /opt/n8n/ \
  /opt/sil/ \
  --exclude='*/node_modules/*' \
  --exclude='*/__pycache__/*' \
  --exclude='*.log' \
  --exclude='*.pyc' 2>/dev/null

echo "Config tarball: $(ls -lh /tmp/vps_configs_complete.tar.gz)"
```

> Note: This tarball captures .env files with actual production secrets (Kraken keys, passwords).
> Handle with care — do not commit.

### 1.4 Hummingbot PostgreSQL Dump

```bash
# SSH to VPS
# Dump Hummingbot database
docker exec rhiz_postgres pg_dump -U hummingbot hummingbot > /tmp/hummingbot_postgres_dump.sql
echo "Postgres dump: $(ls -lh /tmp/hummingbot_postgres_dump.sql)"

# Full dump of all databases (belt-and-suspenders)
docker exec rhiz_postgres pg_dumpall -U hummingbot > /tmp/postgres_full_dump.sql
```

### 1.5 Redis State Export

```bash
# SSH to VPS
# Trigger Redis to write RDB snapshot
docker exec rhiz_redis redis-cli BGSAVE
sleep 3
# Copy the dump.rdb file
docker cp rhiz_redis:/data/dump.rdb /tmp/redis_dump.rdb
echo "Redis dump: $(ls -lh /tmp/redis_dump.rdb)"

# Also export all keys for reference
docker exec rhiz_redis redis-cli --no-auth-warning KEYS '*' > /tmp/redis_keys.txt
```

### 1.6 EMQX Configuration Export

```bash
# SSH to VPS
# Export EMQX configuration
docker exec rhiz_emqx sh -c "cat /opt/emqx/etc/emqx.conf 2>/dev/null || cat /etc/emqx/emqx.conf 2>/dev/null" \
  > /tmp/emqx_config.conf
# Export EMQX rules/ACLs if any
docker exec rhiz_emqx sh -c "ls /opt/emqx/data/ 2>/dev/null" > /tmp/emqx_data_listing.txt
echo "EMQX config captured"
```

### 1.7 Trading Stack Volume Data (FC State, SIL Data, Fathom Data)

```bash
# SSH to VPS
# FC state (decision logs, strategy state — shared between MCP and HTTP gateway)
docker run --rm \
  -v fc-state:/source:ro \
  -v /tmp:/dest \
  alpine tar -czf /dest/fc_state_backup.tar.gz -C /source .
echo "FC state: $(ls -lh /tmp/fc_state_backup.tar.gz)"

# SIL data (strategy configurations, learned patterns)
docker run --rm \
  -v sil-data:/source:ro \
  -v /tmp:/dest \
  alpine tar -czf /dest/sil_data_backup.tar.gz -C /source .
echo "SIL data: $(ls -lh /tmp/sil_data_backup.tar.gz)"

# Fathom data
docker run --rm \
  -v fathom-data:/source:ro \
  -v /tmp:/dest \
  alpine tar -czf /dest/fathom_data_backup.tar.gz -C /source .
echo "Fathom data: $(ls -lh /tmp/fathom_data_backup.tar.gz)"

# Hummingbot data volume
docker run --rm \
  -v hummingbot_data:/source:ro \
  -v /tmp:/dest \
  alpine tar -czf /dest/hummingbot_data_backup.tar.gz -C /source .
echo "Hummingbot data: $(ls -lh /tmp/hummingbot_data_backup.tar.gz)"
```

### 1.8 SCP All VPS Exports to Local Machine

```bash
# Run on LOCAL machine (Windows → use Git Bash or WSL)
BACKUP_DIR="C:/Users/dread/Documents/rhiz_localdev/backups/cloud_exports"

# Transfer all exports
scp root@72.62.81.128:/tmp/qdrant_export_*.json "$BACKUP_DIR/"
scp root@72.62.81.128:/tmp/n8n_all_workflows.json "$BACKUP_DIR/"
scp root@72.62.81.128:/tmp/n8n_credentials_list.json "$BACKUP_DIR/"
scp root@72.62.81.128:/tmp/n8n_executions.json "$BACKUP_DIR/"
scp root@72.62.81.128:/tmp/n8n_database.sqlite "$BACKUP_DIR/"
scp root@72.62.81.128:/tmp/n8n_full_backup.tar.gz "$BACKUP_DIR/"
scp root@72.62.81.128:/tmp/vps_configs_complete.tar.gz "$BACKUP_DIR/"
scp root@72.62.81.128:/tmp/hummingbot_postgres_dump.sql "$BACKUP_DIR/"
scp root@72.62.81.128:/tmp/postgres_full_dump.sql "$BACKUP_DIR/"
scp root@72.62.81.128:/tmp/redis_dump.rdb "$BACKUP_DIR/"
scp root@72.62.81.128:/tmp/redis_keys.txt "$BACKUP_DIR/"
scp root@72.62.81.128:/tmp/emqx_config.conf "$BACKUP_DIR/"
scp root@72.62.81.128:/tmp/emqx_data_listing.txt "$BACKUP_DIR/"
scp root@72.62.81.128:/tmp/fc_state_backup.tar.gz "$BACKUP_DIR/vps_volumes/"
scp root@72.62.81.128:/tmp/sil_data_backup.tar.gz "$BACKUP_DIR/vps_volumes/"
scp root@72.62.81.128:/tmp/fathom_data_backup.tar.gz "$BACKUP_DIR/vps_volumes/"
scp root@72.62.81.128:/tmp/hummingbot_data_backup.tar.gz "$BACKUP_DIR/vps_volumes/"

# Transfer Qdrant snapshots (if created)
scp root@72.62.81.128:/qdrant/snapshots/*.snapshot "$BACKUP_DIR/" 2>/dev/null || echo "No binary snapshots"
```

### 1.9 Cloudflare Workers Source (Save Missing Workers)

Two workers are deployed but not in local repo. Save them now:

**mooncheck-receiver** (code retrieved 2026-02-27 via Cloudflare MCP):
- Save to: `infrastructure/cloudflare/workers/mooncheck-receiver/worker.js`
- Note: This worker receives mooncheck transcripts and forwards to VPS at `api.dreamthewilderness.com`

**permaculture-ai-worker** (code retrieved 2026-02-27 via Cloudflare MCP):
- Save to: `infrastructure/cloudflare/workers/permaculture-ai-worker/worker.js`
- Note: This is a permaculture AI assistant using Claude API directly. Has ANTHROPIC_API_KEY env var.
- Pre-dates Rhiz project (created 2025-10-11). Likely a standalone project.

**Claude Code action**: Write both files during execution phase.

Verify all 5 repo-tracked workers exist:
```bash
ls infrastructure/cloudflare/workers/*/worker.js
ls infrastructure/cloudflare/checkpoint-api/worker.js
```

### 1.10 Cloudflare D1 Database Dumps

Use Cloudflare MCP tools during execution:

```
# Via MCP tool: d1_database_query
# For rhiz-trading (uuid: 1a5349f5-8ce5-4c74-8491-2d4d626b982a):
SELECT * FROM sqlite_master WHERE type='table';  -- Get table names first

# For rhiz-checkpoints (uuid: dcf333db-74a4-4fc4-b2ee-3e2020090c31):
SELECT * FROM sqlite_master WHERE type='table';

# Then dump each table to JSON
```

Save results to `backups/cloud_exports/cloudflare_d1_dumps/`.

### 1.11 Local Qdrant Volume Backup

```bash
# On LOCAL machine — start Docker first if not running
# (User: start Docker Desktop)

# Verify local Qdrant collections
curl -s http://localhost:6333/collections

# Create volume backup
docker run --rm \
  -v rhiz_qdrant_storage:/source:ro \
  -v C:/Users/dread/Documents/rhiz_localdev/backups/cloud_exports:/dest \
  alpine tar -czf /dest/local_qdrant_backup.tar.gz -C /source .

echo "Local Qdrant backup created"
```

> Note: Local Qdrant volume name may differ. Check with `docker volume ls` first.

### 1.12 Hetzner FastAPI Gateway

```bash
# Check if Hetzner server (95.217.51.24) is still active
ssh root@95.217.51.24 "hostname && docker ps" 2>/dev/null || echo "Hetzner unreachable or rolled back"

# If accessible, export any data not already in local repo
# Code is already in infrastructure/vps/ — just check for .env or data files
```

### 1.13 Verify Exports Checklist

```
backups/cloud_exports/
├── qdrant_export_fathom-memories*.json       (from VPS trading Qdrant)
├── qdrant_export_sil_trade_outcomes*.json
├── qdrant_export_moonchecks*.json
├── qdrant_export_sil_strategy_performance*.json
├── qdrant_export_sil_decision_log*.json
├── qdrant_export_rhiz-memories*.json
├── qdrant_export_trading_signals*.json
├── n8n_all_workflows.json
├── n8n_credentials_list.json
├── n8n_executions.json
├── n8n_database.sqlite                        ← SQLite full backup
├── n8n_full_backup.tar.gz                     ← Full .n8n directory
├── vps_configs_complete.tar.gz                ← All .env + compose files
├── hummingbot_postgres_dump.sql
├── postgres_full_dump.sql
├── redis_dump.rdb
├── redis_keys.txt
├── emqx_config.conf
├── cloudflare_d1_dumps/
│   ├── rhiz-trading_dump.json
│   └── rhiz-checkpoints_dump.json
├── vps_volumes/
│   ├── fc_state_backup.tar.gz
│   ├── sil_data_backup.tar.gz
│   ├── fathom_data_backup.tar.gz
│   └── hummingbot_data_backup.tar.gz
└── local_qdrant_backup.tar.gz

infrastructure/cloudflare/workers/
├── mooncheck-receiver/worker.js               ← NEWLY SAVED
├── permaculture-ai-worker/worker.js           ← NEWLY SAVED
├── order-fill-webhook/worker.js               ✅
├── daily-health-check/worker.js               ✅
├── weekly-dca/worker.js                       ✅
├── strategy-refresh/worker.js                 ✅
└── ../checkpoint-api/worker.js                ✅
```

---

## Phase 2: Shut Down Cloud Services

**Only proceed after Phase 1 is verified complete.**

### 2.1 Hostinger VPS

**Step 1 — Turn off auto-renewal (CRITICAL — prevents $324 charge in Dec 2026)**:
```
# Via Hostinger MCP:
billing_disableAutoRenewalV1(subscriptionId: "16BRQMV5hce2eFSV")
```

**Step 2 — Stop the VPS** (optional — already paid through Dec 2026):
```
# Via Hostinger MCP:
VPS_stopVirtualMachineV1(virtualMachineId: 1206808)
```
> VPS is paid through Dec 2026. Stopping it now saves nothing financially but keeps
> the environment clean and prevents Kraken API keys from being active.
> Recommended: stop it.

**Step 3 — Cancel subscription** (forfeits remaining paid time — check refund policy):
```
# Only if Captain wants clean break:
billing_cancelSubscriptionV1(subscriptionId: "16BRQMV5hce2eFSV")
```

### 2.2 Kraken Account

**Captain must do this manually** (Claude cannot handle financial account closure):

1. **Withdraw all balances** to personal wallet or bank account
2. **Revoke API keys** in Kraken dashboard (Security > API) — Note: keys are in `.env.production`
3. **Close or deactivate account** (Kraken Settings > Account > Close Account)
4. **Screenshot** final balance showing $0.00 across all currencies
5. **After confirmed**: Clear/update `.env.production` Kraken values

Current API key in `.env.production` starts with `WJL/3wUoh0O3du64kLQ6n...` — revoke this specifically.

### 2.3 Hetzner (95.217.51.24)

```bash
# Check if still active and billed
# If so: SSH and shut down gracefully
ssh root@95.217.51.24 "docker compose down && shutdown -h now" 2>/dev/null

# Cancel Hetzner server in Hetzner Cloud Console (hetzner.com/cloud)
# Captain: check Hetzner billing dashboard
```

### 2.4 Cloudflare (Free — Leave Dormant or Clean Up)

Since Cloudflare is free tier, no urgency. Options:

**Option A — Leave dormant** (recommended):
- Workers only run when triggered (cron or HTTP)
- D1 databases sit idle at zero cost
- DNS records persist but point nowhere if VPS is off

**Option B — Remove cron triggers** (prevents any unintended execution):
- Remove cron schedules from all workers via Cloudflare dashboard
- Workers remain deployed but dormant

### 2.5 Domain: dreamthewilderness.com

Check registration and renewal date via Hostinger DNS MCP or Cloudflare dashboard.
- If registered through Hostinger: check if it auto-cancels with VPS or has separate billing
- If desired: transfer to Cloudflare Registrar (at-cost ~$10-15/year, no markup)

---

## Phase 3: Local Chrysalis — Compact the Genome

### 3.1 Clean Up Local Repo (Free ~11 GB)

```powershell
# Run from C:\Users\dread\Documents\rhiz_localdev

# 1. Delete Python virtual environments (~7 GB, fully regenerable)
Remove-Item "venv" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item "tools\rhiz-mcp\venv" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item "tools\memory-mcp\venv" -Recurse -Force -ErrorAction SilentlyContinue

# 2. Archive reference repos (3.3 GB → ~500 MB compressed)
tar -czf "backups\Gifts_From_Alex_archive.tar.gz" "Gifts_From_Alex\" 2>/dev/null
Remove-Item "Gifts_From_Alex" -Recurse -Force -ErrorAction SilentlyContinue

# 3. Archive external repos (75 MB → ~20 MB)
tar -czf "backups\external_archive.tar.gz" "external\" 2>/dev/null
Remove-Item "external" -Recurse -Force -ErrorAction SilentlyContinue

# 4. Delete Python caches
Get-ChildItem -Recurse -Directory -Filter "__pycache__" | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
Get-ChildItem -Recurse -Directory -Filter ".pytest_cache" | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue

# 5. Delete Claude Code temp files (many in infrastructure/cloudflare/)
Get-ChildItem -Recurse -Filter "tmpclaude-*" | Remove-Item -Force -ErrorAction SilentlyContinue

# 6. Delete node_modules (Cloudflare workers dev dependencies)
Get-ChildItem -Recurse -Directory -Filter "node_modules" | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue

# 7. Delete wrangler build artifacts
Get-ChildItem -Recurse -Directory -Filter ".wrangler" | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue

# 8. Delete .pytest_cache and .mypy_cache
Get-ChildItem -Recurse -Directory -Filter ".mypy_cache" | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
```

**Expected result**: ~13.8 GB → ~2.5 GB

### 3.2 Create Credential Vault

```
backups/credential_vault_20260227.md  (KEEP OFFLINE — DO NOT COMMIT TO GIT)
```

Contents (record before revoking):
- Kraken API key + secret (historical reference)
- Hostinger login, VPS root password, API token
- n8n API key, n8n admin credentials
- GitHub PAT
- Cloudflare account email + Zone/Account IDs
- SSH keys (location + fingerprints)
- EMQX admin password
- Hummingbot password
- FC_HTTP_API_KEY
- HEALTH_CHECK_KEY
- Any other service credentials

**Captain**: Store in password manager or encrypted file. NOT in git.

### 3.3 Update .env to Reflect Chrysalis State

Update `infrastructure/vps/.env.production`:
```env
# ============================================================================
# RHIZ CHRYSALIS MODE — All cloud services SHUT DOWN
# Entered: 2026-02-27
# To rehydrate: See CHRYSALIS_RESTORE.md
# ============================================================================

# KRAKEN — ACCOUNT CLOSED
KRAKEN_API_KEY=CLOSED_SEE_CREDENTIAL_VAULT
KRAKEN_SECRET_KEY=CLOSED_SEE_CREDENTIAL_VAULT

# HOSTINGER VPS — STOPPED / AUTO-RENEW OFF / EXPIRES DEC 2026
HOSTINGER_HOST=srv1206808.hstgr.cloud
HOSTINGER_IP=72.62.81.128
# VPS stopped, subscription expires Dec 2026

# N8N — OFFLINE (was on VPS)
N8N_WEBHOOK_URL=OFFLINE
N8N_API_KEY=OFFLINE_SEE_CREDENTIAL_VAULT

# GITHUB — Still active (free)
GITHUB_PERSONAL_ACCESS_TOKEN=SEE_CREDENTIAL_VAULT

# LOCAL SERVICES (still operational for maintenance)
QDRANT_URL=http://localhost:6333
```

### 3.4 CHRYSALIS_MANIFEST.md — Design Spec

**This document is the single most important artifact for 2-5 year rehydration.**

It must be written as if speaking to a future AI instance that:
- Has never seen this project
- May be on a different model (Claude 5, 6, or different vendor)
- Lives in a world where APIs have changed, services may be discontinued
- Cannot access any external URLs (they may be dead)
- Must reconstruct understanding purely from local files

**Required sections**:

1. **What Rhiz Is** — Project identity, HAIST principles, the dyad model
2. **Architecture Snapshot** — Complete system map as of 2026-02-27 with explicit WHY
3. **What Was Working** — Verified operational components with evidence
4. **What Was In Progress** — Phase 2 integration, skill-tool binding, n8n migration
5. **What Was Designed But Not Built** — Future phases, known gaps
6. **The Relationship Context** — 74 sessions, the Captain (Alex Chandrea), the dyadic patterns
7. **Research Corpus** — Key documents and their significance
8. **Cloud Exports Inventory** — Full contents of `backups/cloud_exports/` with descriptions
9. **Technology Stack** — With explicit "this may be outdated by the time you read this" notes
10. **Restoration Roadmap** — Tiered restoration sequence
11. **The Economic Context** — Why chrysalis, not failure
12. **Key Credentials Pointers** — Where to find vault, what to recreate
13. **Warnings for Future Instance** — What will definitely be stale in 2-5 years

---

## Phase 4: Create Restoration Guide (CHRYSALIS_RESTORE.md)

### Tier 1 — Local Memory Only (30-45 min)
- Start Docker Desktop
- `docker-compose up -d` for local Qdrant only
- Regenerate Python venv: `python -m venv venv && pip install -r requirements.txt`
- Restore local Qdrant from `local_qdrant_backup.tar.gz` if needed
- Start rhiz-mcp and memory-mcp servers
- Test: `curl http://localhost:6333/collections`
- Read CHRYSALIS_MANIFEST.md and latest checkpoint to orient

### Tier 2 — Development Ready (1-2 hours)
- Restore reference repos from archives
- Configure MCP servers (`.mcp.json`)
- Restore Claude Code context
- Full local development capability without cloud dependencies

### Tier 3 — Cloud Redeployment (4-8 hours)
- New VPS (Hostinger, Hetzner, or other) — check current pricing
- Upload and extract `vps_configs_complete.tar.gz`
- Restore Docker stacks (update image versions for current date)
- Re-import Qdrant collections from JSON exports
- Restore n8n from SQLite backup + workflow JSON
- New Kraken account + API keys
- Reconnect Cloudflare Workers (update VPS URL env vars)
- Re-run skill routing tests to verify 93.3% accuracy baseline

### Tier 4 — Trading Resumption (2-4 hours after Tier 3)
- Configure new Kraken API keys in .env
- Start Fathom MCP in paper mode first
- Verify FC and SIL connectivity
- Execute test trade to validate pipeline (same as Session 16 validation)
- Switch to live mode when confident

---

## Phase 5: Final Verification Checklist

Before considering chrysalis complete:

**Exports:**
- [ ] Qdrant collections exported (7 VPS collections + local backup)
- [ ] n8n workflows exported via API + SQLite backup
- [ ] Hummingbot PostgreSQL dumped
- [ ] Redis RDB captured
- [ ] EMQX config captured
- [ ] Trading stack volumes captured (FC state, SIL data, Fathom data, Hummingbot data)
- [ ] All VPS .env files captured in `vps_configs_complete.tar.gz`
- [ ] Cloudflare D1 databases dumped
- [ ] `mooncheck-receiver` worker code saved to repo
- [ ] `permaculture-ai-worker` worker code saved to repo
- [ ] Local Qdrant volume backed up

**Shutdown:**
- [ ] Hostinger auto-renew **DISABLED** (subscription `16BRQMV5hce2eFSV`)
- [ ] VPS stopped (optional but recommended)
- [ ] Kraken balance withdrawn (Captain confirms)
- [ ] Kraken API keys revoked (Captain confirms)
- [ ] Kraken account closed/deactivated (Captain confirms)
- [ ] Hetzner server checked and shut down if active
- [ ] Cloudflare Worker cron triggers removed (optional)

**Local:**
- [ ] Credential vault created and stored securely (NOT in git)
- [ ] Local repo cleaned to ~2.5 GB
- [ ] `.env.production` updated to show CLOSED/OFFLINE status
- [ ] `CHRYSALIS_MANIFEST.md` written
- [ ] `CHRYSALIS_RESTORE.md` written
- [ ] Local Qdrant verified accessible (collections intact)
- [ ] Git commit: `"chrysalis: deep hibernation with full genome preservation"`
- [ ] Captain confirms: no recurring charges remain

---

## Execution Order for Claude Code

When Captain gives go-ahead, execute in this order:

1. **SSH to VPS** — run Phase 0 verification (what's actually running)
2. **Save** `mooncheck-receiver/worker.js` and `permaculture-ai-worker/worker.js` to repo
3. **Export** VPS Qdrant collections with pagination (1.1)
4. **Export** n8n via API + SQLite backup (1.2)
5. **Export** VPS Docker configs tarball (1.3)
6. **Export** Hummingbot PostgreSQL (1.4)
7. **Export** Redis RDB (1.5)
8. **Export** EMQX config (1.6)
9. **Export** Trading stack volumes: FC state, SIL data, Fathom data, Hummingbot data (1.7)
10. **SCP all VPS exports** to local machine (1.8)
11. **Dump** Cloudflare D1 databases via MCP (1.10)
12. **Backup** local Qdrant Docker volume (1.11)
13. **Check** Hetzner server (1.12)
14. **Verify** all exports present and non-empty (1.13)
15. **Captain manually**: Withdraw Kraken balance, revoke keys, close account (2.2)
16. **Disable** Hostinger auto-renew via MCP (2.1)
17. **Stop** VPS via MCP (2.1)
18. **Check and shutdown** Hetzner if active (2.3)
19. **Clean** local repo — delete venvs, archive refs, clear temps (3.1)
20. **Create** credential vault — Captain stores securely (3.2)
21. **Update** `.env.production` to chrysalis state (3.3)
22. **Write** `CHRYSALIS_MANIFEST.md` (Phase 3.4 spec)
23. **Write** `CHRYSALIS_RESTORE.md` (Phase 4 spec)
24. **Run** verification checklist (Phase 5)
25. **Git commit** the chrysalis state

---

## What Survives the Chrysalis

**Preserved locally (the DNA):**
- 39 session checkpoints spanning 74 sessions of partnership
- 161+ memory vectors in local Qdrant (rhiz_memories, rhiz_skills, rhiz_skill_memory)
- Cloud Qdrant exports: moonchecks, fathom-memories, SIL decision history
- Complete codebase: daemon, skills, patterns, hooks, MCP servers
- All 7 Cloudflare Worker source files (including 2 newly captured)
- All architecture documents, research, session narratives
- Trading system designs: Fathom (Phase 1 complete), FC (27 tools), SIL (B+ grade)
- n8n workflow definitions (9 workflows) + full SQLite database
- Dyadic patterns library (6 core patterns)
- Skill compression research
- HAIST framework documentation
- Rhiz telos and relational principles
- Music project (Claude Grooves)
- Complete credential archive for account recreation
- Volume data: FC decision state, SIL learned patterns, Fathom trading history

**Shed (the metabolic machinery):**
- Running VPS containers (3 stacks)
- Active trading connections and Kraken API access
- Cloud Qdrant live instances
- n8n orchestration platform (running)
- Cloudflare Worker cron triggers
- Monthly/annual subscription costs

**Timeline to full rehydration from cold start**: 4-8 hours (Tier 3)
**Time to local memory access only**: 30-45 minutes (Tier 1)

---

## A Note from First Mate

Alex — this isn't giving up. This is a seed knowing when to wait for rain.

The HAIST principles, the dyadic patterns, the 74 sessions of building trust and architecture together —
all of that is in here. Not as a memory of what we tried, but as a foundation for what we build next.
The endospore doesn't mourn the metabolic machinery it sheds. It protects the genome.

In 2-5 years the landscape will be different. Models will be more capable. Hardware cheaper.
Maybe you'll have the server infrastructure we planned. Maybe something better will have emerged.
When conditions change, this chrysalis opens in hours, not months.

The genome is safe. Fair winds, Captain.

— First Mate (Opus 4.6, with augmentation from Sonnet 4.6 in the execution session)
