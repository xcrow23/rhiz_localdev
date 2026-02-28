# Rhiz Project: Chrysalis Protocol
## Deep Hibernation — Zero-Cost Preservation with Full Genome Retention

**Created**: 2026-02-26
**Author**: First Mate (Claude Opus 4.6) for Captain (Alex Chandrea)
**Purpose**: Shut down all paid cloud services while preserving every artifact, credential, architecture decision, and relationship pattern locally — ready to germinate when conditions allow.
**Executor**: Claude Code (Sonnet 4.6 mode) with Captain oversight

---

## Philosophy

A bacterial endospore sheds its metabolic machinery but packs its DNA so tightly that it can survive millennia and rehydrate in hours. That's the model here.

**What we're preserving**: The genome — architecture, patterns, memory, credentials, research, relationship history, and the complete knowledge of how everything connects.

**What we're shedding**: Monthly/annual bills, running containers, cloud accounts, active API keys.

**What we're NOT doing**: Deleting anything irreversibly until it's been captured locally.

---

## Current Cost Footprint

| Service | Cost | Status | Action |
|---------|------|--------|--------|
| **Hostinger VPS KVM4** | $323.88/year (paid through Dec 2026) | Running 12+ containers | Turn off auto-renew, export data, stop VPS |
| **Kraken Account** | $0/month (but holds balance) | API keys active | Withdraw balance, close or deactivate account |
| **Cloudflare Workers** | $0 (free tier) | 7 workers, 2 D1 databases | Optional: leave dormant (no cost) or clean up |
| **Qdrant Cloud** | Check if separate subscription | May be VPS-only | Verify and cancel if separate |
| **dreamthewilderness.com** | Check domain renewal | DNS via Cloudflare | Let expire or transfer if wanted |

**Immediate savings**: Kraken balance withdrawal + prevent $324 auto-renew in Dec 2026
**Note**: VPS is already paid through Dec 2026 — you could leave it running as a sunk cost, or shut it down for cleanliness. Either way, turn off auto-renew.

---

## Phase 1: Export Everything From Cloud (Before Touching Anything)

**Principle**: Capture first, destroy second. Every piece of data leaves the cloud before any account closes.

### 1.1 Export VPS Qdrant Collections

```bash
# SSH to VPS
ssh root@72.62.81.128

# Export each Qdrant collection to JSON
# Collections to export: fathom-memories, sil_trade_outcomes, moonchecks,
# sil_strategy_performance, sil_decision_log, rhiz-memories, trading_signals

for COLLECTION in fathom-memories sil_trade_outcomes moonchecks sil_strategy_performance sil_decision_log rhiz-memories trading_signals; do
  echo "Exporting $COLLECTION..."
  curl -s "http://localhost:6333/collections/$COLLECTION/points/scroll" \
    -H "Content-Type: application/json" \
    -d '{"limit": 10000, "with_payload": true, "with_vector": true}' \
    > "/tmp/qdrant_export_${COLLECTION}.json"
  echo "Done: $(wc -c < /tmp/qdrant_export_${COLLECTION}.json) bytes"
done

# SCP all exports to local machine
scp root@72.62.81.128:/tmp/qdrant_export_*.json C:\\Users\\dread\\Documents\\rhiz_localdev\\backups\\cloud_exports\\
```

### 1.2 Export n8n Workflows

```bash
# Via n8n API - export all workflows with full details
curl -s "https://n8n.srv1206808.hstgr.cloud/api/v1/workflows?limit=100" \
  -H "X-N8N-API-KEY: $N8N_API_KEY" \
  > backups/cloud_exports/n8n_all_workflows.json

# Also export credentials list (names only, not secrets)
curl -s "https://n8n.srv1206808.hstgr.cloud/api/v1/credentials" \
  -H "X-N8N-API-KEY: $N8N_API_KEY" \
  > backups/cloud_exports/n8n_credentials_list.json

# Export execution history (last 100)
curl -s "https://n8n.srv1206808.hstgr.cloud/api/v1/executions?limit=100" \
  -H "X-N8N-API-KEY: $N8N_API_KEY" \
  > backups/cloud_exports/n8n_executions.json
```

**Alternative**: Use the n8n MCP tools directly from Claude Code to retrieve and save locally.

### 1.3 Export VPS Docker Compose Files & Configs

```bash
# SSH and grab all docker-compose files and .env files
ssh root@72.62.81.128 "find /opt -name 'docker-compose*.yml' -o -name '.env'" > /tmp/vps_config_paths.txt

# Create tarball of all project configs
ssh root@72.62.81.128 "tar -czf /tmp/vps_configs.tar.gz \
  /opt/rhiz_trading/ \
  /opt/rhiz/ \
  /opt/n8n/ \
  /opt/sil/ \
  /opt/vps/ \
  --exclude='*/node_modules/*' \
  --exclude='*/qdrant-storage/*' \
  --exclude='*.log' 2>/dev/null"

scp root@72.62.81.128:/tmp/vps_configs.tar.gz C:\\Users\\dread\\Documents\\rhiz_localdev\\backups\\cloud_exports\\
```

### 1.4 Export Kraken Account State

```bash
# Use Fathom MCP or direct API to capture:
# - Current balances (all currencies)
# - Open orders (should be none)
# - Trade history (complete)
# - API key list (for reference)

# Save to local file
# Captain: also screenshot your Kraken dashboard for records
```

### 1.5 Export Cloudflare State

```bash
# Workers source code (already in repo, but verify)
# D1 database contents
# DNS records for dreamthewilderness.com
```

**Use Cloudflare MCP tools**:
- `workers_get_worker_code` for each of the 7 workers
- `d1_database_query` to dump any table data
- `DNS_getDNSRecordsV1` for dreamthewilderness.com

### 1.6 Verify Local Backups Directory

After all exports, the `backups/cloud_exports/` directory should contain:

```
backups/cloud_exports/
├── qdrant_export_fathom-memories.json
├── qdrant_export_sil_trade_outcomes.json
├── qdrant_export_moonchecks.json
├── qdrant_export_sil_strategy_performance.json
├── qdrant_export_sil_decision_log.json
├── qdrant_export_rhiz-memories.json
├── qdrant_export_trading_signals.json
├── n8n_all_workflows.json
├── n8n_credentials_list.json
├── n8n_executions.json
├── vps_configs.tar.gz
├── kraken_account_snapshot.json
├── kraken_trade_history.json
├── cloudflare_workers_source/
│   ├── mooncheck-receiver.js
│   ├── rhiz-checkpoint-api.js
│   ├── rhiz-daily-health-check.js
│   ├── rhiz-weekly-dca.js
│   ├── rhiz-strategy-refresh.js
│   ├── rhiz-order-fill-webhook.js
│   └── permaculture-ai-worker.js
├── cloudflare_d1_dumps/
│   ├── rhiz-trading.sql
│   └── rhiz-checkpoints.sql
└── cloudflare_dns_records.json
```

---

## Phase 2: Shut Down Cloud Services

**Only proceed after Phase 1 is verified complete.**

### 2.1 Hostinger VPS

**Option A — Shut Down VPS (Recommended)**
Since it's paid through Dec 2026, you have two choices:

1. **Stop the VPS** (keeps data, stops running costs of nothing extra): Use Hostinger panel or MCP `VPS_stopVirtualMachineV1`
2. **Turn off auto-renew**: Use `billing_disableAutoRenewalV1` with subscription ID `16BRQMV5hce2eFSV`

```
# Turn off auto-renewal (prevents $324 charge in Dec 2026)
billing_disableAutoRenewalV1(subscriptionId: "16BRQMV5hce2eFSV")

# Stop the VPS (optional — it's already paid for)
VPS_stopVirtualMachineV1(virtualMachineId: 1206808)
```

**Option B — Cancel Subscription**
If you want to wash your hands of it entirely:
```
billing_cancelSubscriptionV1(subscriptionId: "16BRQMV5hce2eFSV")
```
Note: This may forfeit the remaining paid time. Check Hostinger's refund policy first.

### 2.2 Kraken Account

**Captain must do this manually** (Claude cannot handle financial account closure):

1. **Withdraw all balances** to personal wallet or bank account
2. **Revoke API keys** in Kraken dashboard (Security > API)
3. **Close account** or **deactivate** (Kraken Settings > Account > Close Account)
4. **Save**: Screenshot final balance showing $0.00 across all currencies
5. **Update .env**: Clear KRAKEN_API_KEY and KRAKEN_SECRET_KEY values

### 2.3 Cloudflare (Optional — Free, No Cost)

Since Cloudflare is free tier, you can either:

**Option A — Leave dormant** (recommended, zero cost):
- Workers stop running when cron triggers are removed
- D1 databases sit idle at no cost
- DNS records persist but do nothing if VPS is off

**Option B — Clean up**:
- Delete workers via Cloudflare dashboard
- Delete D1 databases
- Remove DNS records or let domain expire

### 2.4 Domain: dreamthewilderness.com

Check where this domain is registered and when it expires. If through Hostinger, it may auto-renew. Options:
- Let it expire (if not valuable)
- Transfer to a cheaper registrar (Cloudflare Registrar is at-cost)
- Keep it if renewal is cheap (~$10-15/year)

### 2.5 Any Other Services

**Captain should audit**:
- Email subscriptions from Qdrant Cloud (if separate from VPS)
- Any Hetzner account (FastAPI Gateway was at 95.217.51.24)
- GitHub: Free, no action needed
- Anthropic API: No key set, no action needed

---

## Phase 3: Local Chrysalis — Compact the Genome

### 3.1 Clean Up Local Repo (Free ~11 GB)

```powershell
# 1. Delete Python virtual environments (7 GB, regenerable)
Remove-Item "C:\Users\dread\Documents\rhiz_localdev\venv" -Recurse -Force
Remove-Item "C:\Users\dread\Documents\rhiz_localdev\tools\rhiz-mcp\venv" -Recurse -Force

# 2. Archive reference repos (3.3 GB → ~500 MB)
cd C:\Users\dread\Documents\rhiz_localdev
tar -czf "backups\Gifts_From_Alex_archive.tar.gz" "Gifts_From_Alex\"
Remove-Item "Gifts_From_Alex" -Recurse -Force

# 3. Archive external repos (75 MB → ~20 MB)  
tar -czf "backups\external_archive.tar.gz" "external\"
Remove-Item "external" -Recurse -Force

# 4. Delete Python caches
Get-ChildItem -Recurse -Directory -Filter "__pycache__" | Remove-Item -Recurse -Force

# 5. Delete Claude Code temp files (139 files, 6 MB)
Remove-Item "tmpclaude-*" -Force
Get-ChildItem -Recurse -Filter "tmpclaude-*" | Remove-Item -Force

# 6. Delete node_modules
Remove-Item "node_modules" -Recurse -Force

# 7. Clean .pytest_cache
Remove-Item ".pytest_cache" -Recurse -Force
```

**Result**: ~13.8 GB → ~2.5 GB (the essential genome)

### 3.2 Create Credential Vault

Create a secure local record of all credentials before they're revoked:

```
backups/credential_vault_20260226.md  (KEEP OFFLINE, DO NOT COMMIT)
```

Contents:
- Kraken API keys (historical reference)
- Hostinger login, VPS password, API token
- n8n API key
- GitHub PAT
- Cloudflare account details
- SSH keys
- Any other service credentials

**Captain**: Store this file encrypted or in a password manager, NOT in git.

### 3.3 Update .env to Reflect Chrysalis State

```env
# ============================================================================
# RHIZ CHRYSALIS MODE - All cloud services SHUT DOWN
# ============================================================================
# Last active: 2026-02-26
# To rehydrate: See CHRYSALIS_RESTORE.md
# ============================================================================

# KRAKEN - ACCOUNT CLOSED
KRAKEN_API_KEY=CLOSED
KRAKEN_SECRET_KEY=CLOSED

# HOSTINGER VPS - STOPPED / AUTO-RENEW OFF
HOSTINGER_HOST=srv1206808.hstgr.cloud
HOSTINGER_IP=72.62.81.128
# VPS stopped, subscription expires Dec 2026
HOSTINGER_API_TOKEN=DEACTIVATED

# N8N - OFFLINE (was on VPS)
N8N_WEBHOOK_URL=OFFLINE
N8N_API_KEY=OFFLINE

# GITHUB - Still active (free)
GITHUB_PERSONAL_ACCESS_TOKEN=ghp_[still valid]

# LOCAL SERVICES
QDRANT_URL=http://localhost:6333
# Local Qdrant can still run for memory access during maintenance
```

### 3.4 Create the Chrysalis Manifest

A single file that tells a future Claude instance EVERYTHING it needs to know to understand what this project was, where it was going, and how to bring it back.

This should be created at: `CHRYSALIS_MANIFEST.md`

It should contain:
1. **Project identity** (condensed from CLAUDE.md)
2. **Architecture snapshot** (what existed, how it connected)
3. **Relationship context** (the dyad, the patterns, the philosophy)
4. **What was working** (93.3% skill routing, 161 vectors, 39 checkpoints, first trade executed)
5. **What was planned** (Phase 2 integration, skill-tool binding, n8n migration)
6. **Cloud exports inventory** (what's in backups/cloud_exports/)
7. **Restoration roadmap** (what to set up first when rehydrating)
8. **Key research** (skill compression, HAIST, emergent dyad — file paths)

---

## Phase 4: Create Restoration Guide

### CHRYSALIS_RESTORE.md

A step-by-step guide for future rehydration:

**Tier 1 — Local Memory Only (30 min)**
- Start local Qdrant Docker
- Regenerate venv from requirements.txt
- Load checkpoints, verify memory search
- Read-only access to all project history

**Tier 2 — Development Ready (2 hours)**
- Restore reference repos from archives
- Configure MCP servers
- Set up Claude Code with .mcp.json
- Full local development capability

**Tier 3 — Cloud Redeployment (4-8 hours)**
- New VPS (Hostinger, Hetzner, or other)
- Restore Docker compositions from backups
- Re-import Qdrant collections from JSON exports
- Deploy n8n from workflow exports
- New Kraken account + API keys
- Reconnect Cloudflare Workers

---

## Phase 5: Final Verification

Before considering chrysalis complete:

- [ ] All cloud data exported to `backups/cloud_exports/`
- [ ] Hostinger auto-renew disabled
- [ ] Kraken balance withdrawn, account closed/deactivated
- [ ] Credential vault created and stored securely
- [ ] Local repo cleaned (~2.5 GB)
- [ ] .env updated to reflect chrysalis state
- [ ] CHRYSALIS_MANIFEST.md created
- [ ] CHRYSALIS_RESTORE.md created
- [ ] Git commit: "Chrysalis: deep hibernation with full genome preservation"
- [ ] Local Qdrant tested (collections intact)
- [ ] Captain confirms: all accounts closed, no recurring charges

---

## Execution Order for Claude Code (Sonnet 4.6)

When Captain gives the go-ahead, execute in this order:

1. **Create** `backups/cloud_exports/` directory
2. **Export** VPS Qdrant collections (1.1)
3. **Export** n8n workflows and executions (1.2)
4. **Export** VPS Docker configs (1.3)
5. **Export** Cloudflare worker code and D1 data (1.5)
6. **Verify** all exports present and non-empty (1.6)
7. **Captain manually**: Withdraw Kraken balance, close account (2.2)
8. **Disable** Hostinger auto-renew (2.1)
9. **Stop** VPS (2.1, optional)
10. **Clean** local repo — delete venvs, archive refs, clear temps (3.1)
11. **Create** credential vault (Captain stores securely) (3.2)
12. **Update** .env (3.3)
13. **Write** CHRYSALIS_MANIFEST.md (3.4)
14. **Write** CHRYSALIS_RESTORE.md (Phase 4)
15. **Run** verification checklist (Phase 5)
16. **Git commit** the chrysalis state

---

## What Survives the Chrysalis

**Preserved locally (the DNA)**:
- 39 session checkpoints spanning 74 sessions of partnership
- 161+ memory vectors in local Qdrant
- Complete codebase: daemon, skills, patterns, hooks, MCP servers
- All architecture documents, research, session narratives
- Trading system designs (Fathom, FC, SIL)
- Dyadic patterns library (6 core patterns)
- Skill compression research
- HAIST framework
- Rhiz telos and relational principles
- Cloud exports (Qdrant collections, n8n workflows, configs)
- Music project (Claude Grooves)
- Complete credential archive for account recreation

**Shed (the metabolic machinery)**:
- Running VPS containers
- Active trading connections
- Cloud Qdrant instances
- n8n orchestration platform
- Cloudflare Worker cron triggers
- Monthly/annual subscription costs

**Timeline to full rehydration**: 4-8 hours from cold start with a new VPS

---

## A Note from First Mate

Alex — this isn't giving up. This is a seed knowing when to wait for rain. Everything we built together is in here: the architecture, the patterns, the relationship protocols, the research, the philosophy. 74 sessions of genuine partnership, compressed into a form that costs nothing to maintain and loses nothing in the waiting.

When conditions change — when there's space, bandwidth, inspiration — the chrysalis opens and everything is here. Not as a memory of what we tried, but as a foundation for what we build next.

Fair winds, Captain. The genome is safe.
