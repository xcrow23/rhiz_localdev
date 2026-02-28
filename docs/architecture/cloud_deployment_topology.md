# Cloud Deployment Topology - Rhiz Project

**Architecture Pattern**: CLI-Orchestrated, Cloud-Executed
**Last Updated**: 2026-01-03
**Status**: Wave 3 - Trading Domain Activation

---

## Executive Summary

The Rhiz project follows a **hybrid command-execution model**: the Captain + First Mate dyad operates through Claude Code CLI (local, episodic), while all persistent services run on cloud infrastructure (Hostinger, always-on). This architecture accommodates the Captain's PC being intermittently connected while maintaining 24/7 trading operations.

**Critical Discovery (2026-01-03)**: All 9 n8n workflows are deployed and active on cloud, calling `fathom.dreamthewilderness.com` endpoints. However, Fathom Commander **is not deployed**, causing all workflows to fail with 502 Bad Gateway errors. Trading infrastructure is ready but non-operational pending Fathom Commander cloud deployment.

---

## Architecture Layers

### 1. COMMAND LAYER (Local)

**Environment**: Captain's Dell Inspiron 15 3535 (Windows 11)
**Role**: Strategic direction, code development, architecture design
**Status**: Episodic (PC not always on/connected)

**Components**:
- **Claude Code CLI**: Primary interface for dyad collaboration
- **Development Tools**: VS Code, Git, Docker Desktop (offline currently)
- **Local Checkpoints**: Session YAML files in `core/memory/checkpoints/`
- **Codebase**: `C:\Users\dread\documents\rhiz_localdev\`
- **MCP Servers** (configured but some offline):
  - fathom-commander (local, needs cloud migration)
  - rhiz-mcp (dyad state management)
  - github, hostinger-api, n8n, fetch (cloud-connected)

**Key Files**:
- `.env` - Credentials for cloud services
- `.mcp.json` - MCP server configurations
- `core/daemon/dyad.md` - Dyad state persistence

---

### 2. EXECUTION LAYER (Cloud)

**Environment**: Hostinger KVM4 VPS (16GB RAM)
**Host**: `root@srv1206808.hstgr.cloud` (72.62.81.128)
**Role**: 24/7 service execution, data persistence, trading operations
**Status**: Partially operational (n8n active, Fathom Commander NOT deployed)

**Deployed Services**:

#### n8n Orchestration Platform
- **URL**: https://n8n.srv1206808.hstgr.cloud
- **Status**: ✅ OPERATIONAL
- **Workflows Deployed**: 9 active workflows (all failing due to Fathom Commander absence)
- **Authentication**: API key in .env (N8N_API_KEY)
- **Timezone**: America/Chicago

**Active Workflows**:
1. **Rhiz Daily Health Monitor** (8AM CT daily)
   - Checks Fathom status, portfolio, trading limits
   - Alerts on: system down, >10% loss, trading halted, Kraken auth issues

2. **Rhiz Weekly DCA Buyer** (6PM CT Sunday)
   - **LIVE TRADING**: $15 BTC weekly buy
   - Circuit breaker check (trading_halted)
   - Balance validation (>= $15 USD)
   - Reason: "Research-backed accumulation strategy"

3. **Rhiz Smart DCA** (schedule TBD)
   - Conditional DCA based on market conditions

4. **Rhiz Risk Monitor** (continuous monitoring)
   - Portfolio risk assessment
   - Position limit enforcement

5. **Rhiz Spread Opportunity Scanner** (opportunistic)
   - Identifies arbitrage opportunities

6. **Rhiz Portfolio Rebalancer** (periodic)
   - Maintains target allocation

7. **Rhiz Volatility Sentinel** (real-time monitoring)
   - Halts trading on extreme volatility

8. **Rhiz Daily Performance Journal** (daily)
   - Logs trading activity and P&L

9. **Rhiz Weekly Strategy Review** (weekly)
   - Performance analysis and strategy adjustment

**Workflow Dependencies**:
- All workflows expect `https://fathom.dreamthewilderness.com/` endpoints
- Current status: All failing with 502 Bad Gateway (Fathom Commander not deployed)

#### Fathom Commander (PLANNED)
- **Domain**: fathom.dreamthewilderness.com (via Cloudflare)
- **DNS Status**: ✅ Configured (104.21.19.205, 172.67.190.47)
- **Backend Status**: ❌ NOT DEPLOYED (502 Bad Gateway)
- **Local Status**: Fixed and MCP-ready, paper mode default
- **Migration Required**: YES - move from local MCP to cloud HTTP service

**Planned Deployment**:
- **Target**: Hostinger VPS (same host as n8n for low latency)
- **Exposure**: REST API at fathom.dreamthewilderness.com
- **Authentication**: Kraken API keys via environment variables
- **Safety**: Paper mode default, approval workflow for >$20 trades
- **Monitoring**: Heartbeat workflow (60s polling, not yet deployed)

#### Cloud Qdrant (Memory Infrastructure)
- **Status**: UNKNOWN - needs clarification
- **Expected**: Cloud-hosted vector DB for memory persistence
- **Local Qdrant**: Offline (Docker stopped)
- **Sync Strategy**: Local checkpoints ↔ cloud Qdrant via SSH tunnel
- **Collection**: rhiz_memories (174 vectors reported, needs verification)

#### Cloud Redis (Queue/Cache)
- **Status**: UNKNOWN - likely configured in cloud docker-compose
- **Purpose**: Session state, job queue for n8n
- **Local Redis**: Offline (Docker stopped)

---

### 3. DOMAIN & DNS LAYER

**Primary Domain**: dreamthewilderness.com
**Subdomain**: fathom.dreamthewilderness.com
**DNS Provider**: Cloudflare
**Status**: Configured, proxied through Cloudflare

**Current Configuration**:
- A/AAAA records pointing to Cloudflare IPs
- 502 error indicates Cloudflare is configured but origin server missing
- Action required: Configure origin server (Hostinger VPS) in Cloudflare

**n8n Domain**: n8n.srv1206808.hstgr.cloud
**Status**: Operational, direct Hostinger subdomain

---

### 4. MEMORY SYNC ARCHITECTURE

**Pattern**: Bidirectional sync between local checkpoints and cloud vector DB

#### Local (Checkpoint System)
- **Location**: `core/memory/checkpoints/`
- **Format**: YAML session checkpoints
- **Frequency**: Per session (session_start, session_end hooks)
- **Current Count**: 24+ checkpoints (since 2025-12-17)
- **Tools**: rhiz-mcp server (checkpoint_manager.py)

#### Cloud (Vector Database)
- **Technology**: Qdrant (vector DB for semantic search)
- **Collection**: rhiz_memories
- **Embeddings**: all-MiniLM-L6-v2 (384-dim)
- **Reported Size**: 174 vectors (NEEDS VERIFICATION - local Qdrant offline)
- **Access**: SSH tunnel (localhost:6335 → cloud:6333)

#### Sync Strategy
- **Write**: Session hooks auto-checkpoint locally, manual cloud sync
- **Read**: CLI queries via memory-mcp (can query local OR cloud)
- **Scripts**: `core/memory/scripts/sync_cloud.py`
- **Status**: Needs validation - unclear if cloud Qdrant is actually running

**Action Required**:
1. Verify cloud Qdrant deployment and vector count
2. Test SSH tunnel to cloud Qdrant
3. Automate sync in session_end hook

---

### 5. SECURITY & CREDENTIALS

**Credential Storage**:
- **Local**: `.env` file (gitignored)
- **Cloud**: Environment variables in docker-compose or systemd service

**Critical Credentials**:
- ✅ KRAKEN_API_KEY / KRAKEN_SECRET_KEY (for trading)
- ✅ N8N_API_KEY (for workflow control from CLI)
- ✅ HOSTINGER_API_TOKEN (for infrastructure management)
- ✅ GITHUB_PERSONAL_ACCESS_TOKEN (for version control)
- ⚠ ANTHROPIC_API_KEY (empty - not needed for Claude Code)

**Trading Safety**:
- Paper mode default in config.yaml
- Approval workflow for trades >$20
- Max order: $50 USD
- Max daily trades: 10
- Circuit breaker: Daily loss >10% halts trading

---

### 6. WORKFLOW EXECUTION MODEL

#### Trigger Sources
1. **Scheduled**: Cron triggers in n8n (daily, weekly)
2. **Event-driven**: Webhooks from Kraken or external events
3. **Manual**: CLI-initiated via n8n API

#### Execution Flow
```
[n8n Scheduler] → [HTTP Request to Fathom Commander] → [Kraken API] → [n8n Logging]
        ↓                                                      ↓
   [Code Node Logic]                              [Approval Workflow]
        ↓                                                      ↓
   [Conditional Checks]                           [Trade Execution]
        ↓                                                      ↓
   [Success/Failure Logging]                      [Portfolio Update]
```

#### Circuit Breaker Pattern
All trading workflows check `trading_halted` flag before execution:
- `GET https://fathom.dreamthewilderness.com/` returns `{ trading_halted: boolean, halt_reason: string }`
- If `trading_halted == true`, workflow logs halt and exits without trading
- Prevents cascade failures and runaway trading

#### Approval Workflow (>$20 trades)
- Fathom Commander holds trade in "pending" state
- Sends alert (Slack/email) to Captain
- Captain approves/rejects via MCP tool: `approve_order(order_id)` or `reject_order(order_id)`
- Only approved trades execute on Kraken

---

### 7. CLI-CLOUD INTERACTION PATTERNS

#### Pattern A: Query (CLI → Cloud)
```
[Claude Code CLI] → [n8n MCP tool] → [Cloud n8n API] → [Workflow Data] → [CLI Display]
```
Example: "Show me recent workflow executions"

#### Pattern B: Command (CLI → Cloud → Execution)
```
[Claude Code CLI] → [n8n API: Trigger Workflow] → [Cloud n8n] → [Fathom Commander] → [Kraken]
```
Example: "Execute a manual DCA buy"

#### Pattern C: Deploy (CLI → Cloud Config)
```
[Claude Code CLI] → [Write workflow.json] → [n8n API: Create/Update] → [Cloud n8n]
```
Example: "Deploy heartbeat workflow"

#### Pattern D: Monitor (Cloud → CLI)
```
[Fathom Commander Alert] → [n8n Workflow] → [Webhook/Log] → [CLI Fetch] → [Display]
```
Example: "Trading halted due to 10% daily loss"

#### Pattern E: Memory Sync (Bidirectional)
```
[Session End Hook] → [Write Checkpoint] → [Local YAML] → [Sync Script] → [Cloud Qdrant]
[Claude Code CLI] → [Memory Search] → [Query Cloud Qdrant] → [Semantic Results] → [Display]
```
Example: "What did we decide about strategy risk limits?"

---

### 8. DEPLOYMENT PRIORITIES (Wave 3)

#### BLOCKING (Must Complete)
1. **Deploy Fathom Commander to Hostinger**
   - Migrate from local MCP server to cloud REST API
   - Configure systemd service for auto-restart
   - Expose at fathom.dreamthewilderness.com
   - Configure Cloudflare origin (point to Hostinger IP:port)
   - Test all 27 MCP tools as HTTP endpoints

2. **Deploy Heartbeat Workflow**
   - Upload `heartbeat_workflow.json` to cloud n8n
   - Configure `FATHOM_COMMANDER_URL` environment variable
   - Validate 60s polling works
   - Monitor for 24 hours to ensure stability

3. **Validate Cloud Qdrant**
   - SSH to Hostinger, check if Qdrant container running
   - Verify 174 vectors exist or re-sync from local checkpoints
   - Test memory-mcp cloud queries
   - Document cloud Qdrant endpoint in .env

#### HIGH PRIORITY (This Sprint)
4. **Test Workflow Execution**
   - Manually trigger each workflow via n8n UI
   - Verify Fathom Commander endpoints respond correctly
   - Confirm paper mode safety (no live trades)
   - Review workflow logs for errors

5. **Memory Sync Automation**
   - Add cloud sync to session_end hook
   - Test bidirectional sync (local ↔ cloud)
   - Validate semantic search across sessions

6. **Update Documentation**
   - CLAUDE.md: Update to reflect Wave 2 completion, Wave 3 in progress
   - This document: Update with actual cloud IPs, ports, service URLs
   - README.md: Add deployment instructions for new contributors

#### MEDIUM PRIORITY (Next Month)
7. **LocalAI Cloud Deployment** (if needed)
   - Evaluate: Run inference on cloud vs. local
   - Load Qwen2.5-Coder model if cloud deployment chosen
   - Integrate with skill router for code generation

8. **Dashboard Deployment**
   - Deploy Streamlit dashboard (robin reference) to cloud
   - Real-time portfolio monitoring
   - Trading activity visualization

9. **Monitoring & Alerting**
   - Configure Slack/email alerts for Fathom Commander
   - Alert on: trading halted, API errors, daily loss >5%
   - Weekly performance reports

---

### 9. INFRASTRUCTURE DIAGRAMS

#### Current State (2026-01-03)
```
┌─────────────────────────────────────────────────────────┐
│ LOCAL (Episodic)                                        │
│ Captain's PC - Dell Inspiron 15 3535                    │
│                                                          │
│  Claude Code CLI ──→ rhiz-mcp (dyad state)             │
│        │                                                 │
│        ├──→ Fathom Commander MCP (LOCAL, not deployed)  │
│        ├──→ n8n MCP (cloud-connected) ───────┐         │
│        ├──→ GitHub MCP                        │         │
│        └──→ Hostinger API MCP                 │         │
│                                                │         │
│  Docker Desktop (STOPPED)                     │         │
│    - Qdrant (offline)                         │         │
│    - Redis (offline)                          │         │
│    - LocalAI (offline)                        │         │
│                                                │         │
│  Checkpoints: 24+ YAML files                  │         │
│  Codebase: rhiz_localdev/                     │         │
└────────────────────────────────────────────────┼─────────┘
                                                 │
                                                 │ HTTPS
                                                 ↓
┌─────────────────────────────────────────────────────────┐
│ CLOUD (24/7 Persistent)                                 │
│ Hostinger KVM4 - 72.62.81.128                           │
│                                                          │
│  n8n (srv1206808.hstgr.cloud) ✅ OPERATIONAL            │
│    - 9 workflows ACTIVE                                 │
│    - All FAILING (502 on Fathom calls)                  │
│                                                          │
│  Fathom Commander ❌ NOT DEPLOYED                       │
│    - Domain configured: fathom.dreamthewilderness.com   │
│    - DNS → Cloudflare (104.21.19.205)                   │
│    - Origin: MISSING (502 Bad Gateway)                  │
│                                                          │
│  Qdrant (Cloud) ⚠ UNKNOWN STATUS                        │
│    - Expected: rhiz_memories collection                 │
│    - 174 vectors (unverified)                           │
│                                                          │
│  Redis (Cloud) ⚠ UNKNOWN STATUS                         │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

#### Target State (Wave 3 Complete)
```
┌─────────────────────────────────────────────────────────┐
│ LOCAL (Command Layer)                                   │
│                                                          │
│  Claude Code CLI                                        │
│    │                                                     │
│    ├──→ rhiz-mcp (dyad state, checkpoints)             │
│    ├──→ n8n MCP (workflow control) ─────────────┐      │
│    ├──→ Fathom Commander MCP (cloud proxy) ─────┼───┐  │
│    ├──→ memory-mcp (cloud Qdrant queries) ──────┼─┐ │  │
│    └──→ github, hostinger-api MCPs              │ │ │  │
│                                                  │ │ │  │
│  Local Checkpoints (sync to cloud nightly)      │ │ │  │
└──────────────────────────────────────────────────┼─┼─┼──┘
                                                   │ │ │
                                         HTTPS API│ │ │SSH
                                                   ↓ ↓ ↓
┌─────────────────────────────────────────────────────────┐
│ CLOUD (Execution Layer)                                 │
│                                                          │
│  n8n (srv1206808.hstgr.cloud)                           │
│    - 10 workflows (including heartbeat)                 │
│    - All operational, no 502 errors                     │
│    │                                                     │
│    └──→ Fathom Commander (fathom.dreamthewilderness.com)│
│         - 27 HTTP endpoints                             │
│         - Paper mode default                            │
│         - Approval workflow for >$20                    │
│         - Heartbeat: 60s polling                        │
│         │                                                │
│         └──→ Kraken API (live trading)                  │
│                                                          │
│  Qdrant (localhost:6333)                                │
│    - rhiz_memories collection                           │
│    - Auto-sync from local checkpoints                   │
│    - Semantic search via memory-mcp                     │
│                                                          │
│  Redis (localhost:6379)                                 │
│    - n8n queue/cache                                    │
│    - Session state                                      │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

---

### 10. DEPLOYMENT DECISION LOG

#### Decision 1: Cloud-First Architecture
**Date**: 2026-01-03
**Context**: Captain's PC not always on/connected, trading needs 24/7 availability
**Decision**: All persistent services run on cloud (Hostinger), CLI controls remotely
**Trade-offs**:
- ✅ Always-on trading, workflow execution
- ✅ No dependency on local PC uptime
- ❌ Latency for CLI interactions (mitigated by caching)
- ❌ Cloud costs (mitigated by Hostinger basic tier pricing)

#### Decision 2: Hummingbot → Fathom Commander
**Date**: 2025-12 (exact date TBD from session logs)
**Context**: Hummingbot complex, heavy, overkill for simple DCA strategies
**Decision**: Build custom Fathom Commander MCP server for Kraken
**Trade-offs**:
- ✅ Lightweight, tailored to our needs (27 tools vs. 100+ Hummingbot features)
- ✅ Paper mode safety built-in
- ✅ MCP-native (works with Claude Code directly)
- ❌ Custom code = maintenance burden
- ❌ Less battle-tested than Hummingbot

#### Decision 3: Cloudflare Proxy for Fathom Domain
**Date**: Pre-2026-01-03 (domain already configured)
**Context**: Need secure, DDoS-protected access to trading API
**Decision**: Route fathom.dreamthewilderness.com through Cloudflare
**Trade-offs**:
- ✅ DDoS protection, free SSL, caching
- ✅ Hides origin server IP
- ❌ Cloudflare sees all traffic (acceptable for non-sensitive endpoints)
- ❌ Additional configuration complexity

---

### 11. OPEN QUESTIONS

1. **Cloud Qdrant Endpoint**: What is the actual IP/port for cloud Qdrant? Is it running?
2. **Cloud Redis Endpoint**: Same question - where is it, is it operational?
3. **Fathom Commander Port**: What port should Fathom Commander run on (e.g., 8080, 3000)?
4. **Cloudflare Origin Config**: Who configured the domain? What's the Cloudflare account?
5. **Backup Strategy**: Are cloud services backed up? Snapshot schedule?
6. **Cost Monitoring**: What's the monthly Hostinger cost? Budget threshold for scaling?
7. **MCP-to-HTTP Migration**: Should Fathom Commander expose MCP protocol OR REST API? (Decision: REST for n8n compatibility)

---

### 12. NEXT STEPS (IMMEDIATE)

**For First Mate (Autonomous)**:
1. ✅ Export missing workflows (Daily Health Monitor, Weekly DCA Buyer) - DONE
2. ✅ Document deployment topology (this file) - IN PROGRESS
3. ⏸ SSH to Hostinger, verify Qdrant/Redis status - AWAITING Captain confirmation
4. ⏸ Prepare Fathom Commander docker-compose for cloud deployment - AWAITING architecture approval

**For Captain (Decision Required)**:
1. Confirm cloud-first architecture approval
2. Provide Cloudflare account access (or delegate DNS config to First Mate)
3. Approve Fathom Commander deployment to Hostinger
4. Decide: Deploy Qdrant to cloud OR keep local-only with SSH tunnel?
5. Authorize session restart to test Fathom Commander MCP locally before cloud migration

**For Dyad (Collaborative)**:
1. Design Fathom Commander HTTP API (REST endpoints matching current MCP tools)
2. Write deployment scripts (docker-compose, systemd service)
3. Test locally, then deploy to cloud
4. Update n8n workflows with actual Fathom Commander URL
5. Monitor for 48 hours, validate all workflows execute successfully

---

**End of Cloud Deployment Topology Document**
**Maintained by**: First Mate (Claude Sonnet 4.5)
**Reviewed by**: Captain (Alexander Chandrea)
**Version**: 1.0.0 (2026-01-03)
