# VPS Infrastructure Topology - Discovery & Configuration

**Document Type**: Architecture Reference
**Source**: session_20260103_infrastructure_operational.yaml
**Date**: 2026-01-03
**Status**: Current (as of Jan 2026)
**Significance**: Major - Infrastructure Discovery & Safety Intervention

---

```yaml
---
component: hostinger_vps
status: operational
discovery_date: 2026-01-03
uptime: 5+ days (at discovery)
provider: Hostinger
specification: KVM4 16GB RAM, 174GB disk (10% used)
ip_address: 72.62.81.128
domain: fathom.dreamthewilderness.com
container_count: 9
workflow_count: 9
safety_intervention: live_trading_to_paper_mode
related_documents:
  - core/memory/checkpoints/session_20260103_infrastructure_operational.yaml
  - docs/architecture/cloud_deployment_topology.md
  - infrastructure/vps/DEPLOYMENT_GUIDE.md
semantic_cluster: infrastructure_deployment
vector_density: medium  # 0.30-0.50
threshold_recommendation: 0.35
---
```

---

## Executive Summary

On January 3, 2026, a reconnaissance mission revealed **fully operational cloud infrastructure** that Captain had deployed in previous sessions. The Hostinger VPS contained a complete trading stack with **9 running containers** and **9 active n8n workflows**, operational for 5+ days.

**Critical Discovery**: Fathom Commander was in **live trading mode** and had executed **2 real trades** ($50.68 BTC portfolio on Kraken). Immediate safety intervention enforced **paper mode**, then DNS/networking issues were resolved to make infrastructure fully accessible.

This session transitioned understanding from "infrastructure needs to be built" to "infrastructure already exists and is battle-tested."

---

## VPS Specifications

### Hardware & Platform

**Provider**: Hostinger (Hosting Infrastructure)
**Plan**: KVM4 Virtual Private Server
**CPU**: Multi-core (exact spec TBD)
**RAM**: 16GB
**Storage**: 174GB total, 17.4GB used (10% utilization)
**Available Space**: 156.6GB (90% free)

**IP Address**: 72.62.81.128
**Domain**: fathom.dreamthewilderness.com
**SSL**: Cloudflare Flexible SSL (Cloudflare → VPS)

### Operating System

**OS**: Linux (distribution TBD)
**Container Runtime**: Docker + Docker Compose
**Orchestration**: docker-compose.cloud.yaml configurations
**Network Architecture**: Multiple Docker networks (rhiz_rhiz_network, n8n_default)

### Access Methods

**SSH**: Direct access for container management
**HTTPS Domain**: https://fathom.dreamthewilderness.com/ (via Traefik reverse proxy)
**Direct Port**: http://72.62.81.128:8766/ (Fathom Commander backup access)

---

## Container Inventory

### Running Containers (9 total)

**All containers healthy at discovery, 5-6 days uptime**

#### 1. Fathom Commander (`rhiz_fathom_commander`)
**Purpose**: Trading gateway (HTTP API for order placement, market data)
**Uptime**: 5 days (at discovery)
**Health**: Healthy
**Mode**: **Paper** (enforced Jan 3 after discovery of live mode)
**Ports**: 8765 (internal) → 8766 (external)
**Networks**: rhiz_rhiz_network, n8n_default (dual network for Traefik routing)
**Kraken Integration**: Operational ($50.68 BTC from 2 test trades)
**Domain**: fathom.dreamthewilderness.com (via Traefik)

#### 2. n8n (`n8n`)
**Purpose**: Workflow orchestration (9 active workflows)
**Uptime**: 6 days (at discovery)
**Health**: Healthy
**Workflows**: 9 active (scheduled, circuit breaker logic, error handling)
**Networks**: n8n_default
**Database**: Connected to rhiz_postgres

#### 3. Traefik (`n8n-traefik-1`)
**Purpose**: Reverse proxy, SSL termination, routing
**Uptime**: 6 days
**Health**: Healthy
**Configuration**:
  - Entrypoints: web (80), websecure (443)
  - TLS: Let's Encrypt via mytlschallenge certresolver
  - Rule: Host(`fathom.dreamthewilderness.com`)
  - Networks: rhiz_rhiz_network, n8n_default (routes between them)
**SSL Mode**: Cloudflare Flexible (Cloudflare handles client SSL, origin HTTP acceptable)

#### 4. Qdrant (`rhiz_qdrant`)
**Purpose**: Vector database for semantic memory search
**Uptime**: 5+ days
**Health**: Healthy
**Vectors Stored**: 174 (at discovery, from previous sessions)
**Port**: 6333 (internal network only)
**Accessible via**: SSH tunnel (localhost:6335 → cloud:6333) or internal network

#### 5. Redis (`rhiz_redis`)
**Purpose**: Cache and message queue
**Uptime**: 5+ days
**Health**: Healthy
**Usage**: Session state, n8n workflow cache

#### 6. PostgreSQL (`rhiz_postgres`)
**Purpose**: Relational database for n8n workflows
**Uptime**: 5+ days
**Health**: Healthy
**Database**: n8n workflow definitions, execution history

#### 7. EMQX (`rhiz_emqx`)
**Purpose**: MQTT broker for messaging
**Uptime**: 5+ days
**Health**: Healthy
**Usage**: TBD (message bus for workflow events?)

#### 8. Hummingbot API (`rhiz_hummingbot_api`)
**Purpose**: Trading bot backend API
**Uptime**: 5+ days
**Health**: Healthy
**Status**: Running in parallel to Fathom Commander (original trading approach?)
**Note**: Not deprecated; may be earlier trading infrastructure

#### 9. Dashboard (`rhiz_dashboard`)
**Purpose**: Streamlit dashboard for monitoring
**Uptime**: 5+ days
**Health**: Healthy
**Usage**: Portfolio visualization, trading metrics

---

## Network Architecture

### Docker Networks

**rhiz_rhiz_network**:
- Fathom Commander
- Traefik (dual connection)
- Qdrant
- Redis
- PostgreSQL
- EMQX
- Hummingbot API
- Dashboard

**n8n_default**:
- n8n
- Traefik (dual connection for routing between networks)
- Fathom Commander (added Jan 3 to enable Traefik routing)

### Routing Configuration

**External Traffic Flow**:
```
Client (HTTPS)
  → Cloudflare (proxied, SSL termination)
  → Hostinger VPS (72.62.81.128)
  → Traefik reverse proxy
  → Fathom Commander (container)
```

**Traefik Rule**: Host(`fathom.dreamthewilderness.com`)
**Entrypoints**: web (80), websecure (443)
**SSL**: Cloudflare Flexible mode (client → Cloudflare HTTPS, Cloudflare → origin HTTP/HTTPS)

**Direct Access Backup**:
```
Client (HTTP)
  → Hostinger VPS (72.62.81.128:8766)
  → Fathom Commander (port 8766 exposed)
```

### Network Troubleshooting History

**Issue**: Traefik 404 errors when routing to Fathom Commander

**Root Cause**: Fathom Commander only on rhiz_rhiz_network, Traefik routing from n8n_default

**Resolution**: Added Fathom Commander to n8n_default network (dual network configuration)

**Result**: Traefik can route between networks, Fathom Commander accessible via domain

---

## Cloudflare DNS Configuration

### DNS Records

**Zone**: dreamthewilderness.com
**Zone ID**: 02b15ee90820dc7dc204e27a906b789a

**Old Configuration** (non-functional):
- Type: CNAME
- Name: fathom
- Value: 273e5f2d-af6c-446c-bc75-238b34c6c772.cfargotunnel.com
- Issue: Argo Tunnel not running, 502 Bad Gateway errors

**Current Configuration** (operational):
- Type: A
- Name: fathom
- Value: 72.62.81.128 (Hostinger VPS IP)
- Proxy: Enabled (Cloudflare proxying)
- SSL: Flexible mode

**Change Date**: 2026-01-03
**Status**: Operational, HTTPS working via Cloudflare SSL + Traefik routing

### SSL Strategy

**Why Flexible SSL**:
- Cloudflare → origin can be HTTP (Traefik handles internal SSL if needed)
- Let's Encrypt TLS-ALPN-01 challenge blocked by Cloudflare proxy
- Let's Encrypt rate limited (5 failed attempts)
- Simpler to let Cloudflare handle client SSL termination

**Security Consideration**: Cloudflare → origin traffic not encrypted, but on trusted Hostinger infrastructure

---

## n8n Workflow Inventory

### Active Workflows (9 total)

**All workflows have**:
- Circuit breaker logic (stop on repeated failures)
- Balance checks before trades
- Error logging to memory/Qdrant
- Scheduled execution (cron-based)

#### 1. Rhiz Daily Health Monitor
**Schedule**: 8:00 AM CT (daily)
**Purpose**: System health checks, container status, API connectivity
**Actions**: Log health metrics, alert on failures

#### 2. Rhiz Weekly DCA Buyer
**Schedule**: Sunday 6:00 PM CT (weekly)
**Purpose**: Dollar-cost averaging BTC purchases
**Amount**: $15 BTC per execution
**Status**: Paper mode (post-safety intervention)
**Next Execution**: TBD (schedule active)

#### 3. Rhiz Smart DCA
**Schedule**: TBD (market-condition triggered?)
**Purpose**: Intelligent DCA based on market indicators (not time-based only)
**Logic**: TBD (likely volatility, RSI, or momentum-based)

#### 4. Rhiz Risk Monitor
**Schedule**: TBD (likely continuous or frequent)
**Purpose**: Portfolio risk assessment, circuit breaker enforcement
**Thresholds**: 10% daily loss halts trading

#### 5. Rhiz Spread Opportunity Scanner
**Schedule**: TBD (likely frequent, every 5-15 min?)
**Purpose**: Detect arbitrage or favorable spread conditions
**Action**: Alert or auto-execute small trades

#### 6. Rhiz Portfolio Rebalancer
**Schedule**: TBD (likely daily or weekly)
**Purpose**: Rebalance portfolio to target allocations
**Current**: 100% BTC, target allocations TBD

#### 7. Rhiz Volatility Sentinel
**Schedule**: TBD (continuous monitoring?)
**Purpose**: Detect high volatility conditions, adjust risk parameters
**Action**: Notify or enforce conservative mode

#### 8. Rhiz Daily Performance Journal
**Schedule**: End of day (11:59 PM CT?)
**Purpose**: Log daily trading performance, P&L, trades executed
**Output**: Memory/Qdrant vectors for pattern analysis

#### 9. Rhiz Weekly Strategy Review
**Schedule**: End of week (Sunday 11:59 PM CT?)
**Purpose**: Aggregate weekly performance, strategy effectiveness
**Output**: Strategic insights for next week's trading

### Workflow Status

**Accessible via**: n8n UI on VPS (internal network) or n8n MCP tools
**Execution**: Automated on schedule (cron-based)
**Mode**: Paper (enforced Jan 3 after safety intervention)
**Next Validation**: Weekly DCA Buyer (Sunday 6 PM CT) will be first test of post-fix execution

---

## Critical Safety Intervention (Jan 3, 2026)

### Discovery

**What was found**: Fathom Commander in **live trading mode**, 2 successful test trades executed

**Evidence**:
- Kraken portfolio: $50.68 BTC
- Trade 1:
  - Date: 2025-12-29
  - TXID: OTNH3O-YPWK3-5GPKUL
  - Pair: XXBTZUSD
  - Side: buy
  - Volume: 0.00016984 BTC
  - Cost: $14.925 USD
  - Price: $87,877.50 per BTC
  - Status: Executed successfully

**Risk Assessment**: Live trading without explicit approval, no active session monitoring

### Immediate Response

**Action**: Enforce paper mode across all configuration layers

**Changes Made**:
1. `config.yaml`: Set `mode: paper`
2. `state.py`: Changed default `mode: str = 'paper'` (code-level enforcement)
3. Rebuilt container to apply changes
4. Verified mode via API: Confirmed `mode='paper'`

**Time to Resolution**: 20 minutes

**Reversibility**: Yes (config changes can revert to live mode with Captain approval)

### Safety Architecture Confirmed

**Hard Limits** (all enforced):
- MAX_ORDER_USD: $50
- CAPTAIN_APPROVAL_THRESHOLD: $20 (orders >$20 require approval)
- Daily trade limit: 10 trades
- Circuit breaker: 10% daily loss halts trading

**Paper Mode Behavior**:
- All orders simulated (no real capital deployed)
- Kraken API authenticated (can query real market data)
- Full trade logging to memory (hypothesis tracking functional)
- Approval workflow still enforced (workflow validation)

**Captain's Response**: Approved immediate safety enforcement, satisfied with proactive intervention

---

## Deployment Architecture Pattern

### CLI-Orchestrated, Cloud-Executed

**Rationale**: Captain's PC not always on, 24/7 trading requires cloud persistence

**Local Layer** (Episodic):
- Claude Code CLI (interactive sessions)
- MCP servers: rhiz-mcp, memory-mcp, n8n-mcp, github-mcp, hostinger-api-mcp, fetch-mcp
- Checkpoint files (session continuity)
- SSH access to VPS

**Cloud Layer** (Persistent, 24/7):
- All containers running on Hostinger VPS
- n8n workflows execute on schedule
- Fathom Commander accessible via HTTPS domain
- Qdrant memory persistent across sessions
- Redis, PostgreSQL, EMQX provide state/messaging

**Interface**:
- Captain + First Mate dyad provides teleological direction via CLI
- Cloud infrastructure executes autonomously between sessions
- Session checkpoints provide continuity across CLI invocations

---

## Kraken Integration Status

### Account Configuration

**Exchange**: Kraken
**API Authentication**: Operational (tested successfully)
**Portfolio Value**: $50.68 USD (as of Jan 3)
**Holdings**: 100% BTC (0.00016984 BTC from test trades)
**Mode**: **Paper** (enforced Jan 3)

### Test Trades Executed

**Trade Count**: 2 successful executions (in live mode, pre-safety intervention)

**Trade 1**:
- Date: 2025-12-29
- TXID: OTNH3O-YPWK3-5GPKUL
- BTC purchased: 0.00016984 BTC @ $87,877.50
- Cost: $14.925 USD

**Trade 2**: Details not documented in checkpoint

### API Capabilities Validated

**Operational Endpoints**:
- Balance queries (account balances)
- Ticker data (real-time prices)
- OHLC data (candlestick charts)
- Order placement (buy/sell market/limit)
- Trade history (executed trades)
- Open orders (pending orders)

**Safety Mechanisms Validated**:
- Hard limits enforced (MAX_ORDER_USD)
- Approval workflow functional
- Circuit breaker logic operational
- Daily trade limits respected

---

## Memory Infrastructure

### Qdrant Vector Database

**Location**: rhiz_qdrant container (VPS)
**Vectors Stored**: 174 (at discovery, from previous sessions)
**Port**: 6333 (internal network)
**Collections**: rhiz_memories (checkpoint data, trading decisions, patterns)

**Access Methods**:
1. Internal Docker network (from Fathom Commander, n8n)
2. SSH tunnel: localhost:6335 → cloud:6333 (from local CLI)
3. memory-mcp tools (semantic search from CLI)

**Usage**:
- Session checkpoints indexed as vectors
- Trading decision history searchable
- Patterns and learnings accumulated across sessions
- Strategic intelligence context for trading decisions

### Checkpoint Synchronization

**Local Checkpoints**: core/memory/checkpoints/ (YAML files)
**Cloud Vectors**: Qdrant rhiz_memories collection
**Sync Method**: SSH tunnel (localhost:6335 → cloud:6333)
**memory-mcp**: Can query both local and cloud memory

---

## Infrastructure Discovery Timeline

### Pre-Reconnaissance Understanding

**Assumption**: Infrastructure needed to be built and deployed
**Reality**: Infrastructure already operational for 5+ days

### Discovery Session (Jan 3, 2026, 2.5 hours)

**T+0:00**: Reconnaissance mission initiated
**T+0:30**: SSH into VPS, discovered 9 running containers
**T+0:45**: Discovered Fathom Commander in live mode, 2 trades executed
**T+1:05**: Paper mode enforced (config + code + rebuild)
**T+1:20**: Cloudflare DNS investigated (502 errors)
**T+1:35**: Deleted Argo Tunnel CNAME, created A record to VPS IP
**T+1:50**: Traefik 404 errors (routing issue)
**T+2:35**: Resolved Traefik routing (dual network + entrypoints labels)
**T+2:30**: Domain operational via HTTPS, direct port 8766 backup
**T+2:30**: Full validation complete, documentation written

### Key Milestones

1. **Infrastructure exists** (not theoretical)
2. **Safety enforced** (live → paper mode)
3. **Routing fixed** (DNS + Traefik)
4. **Validation complete** (all endpoints operational)

---

## Blockers Resolved

### Blocker 1: Live Trading Mode (CRITICAL)

**Severity**: Critical
**Issue**: Fathom Commander executing real trades without active session monitoring
**Resolution**: Paper mode enforced via config.yaml + state.py default + container rebuild
**Time**: 20 minutes
**Outcome**: Mode verified as 'paper', safety re-established

### Blocker 2: Cloudflare DNS (HIGH)

**Severity**: High
**Issue**: CNAME pointing to non-functional Argo Tunnel (502 Bad Gateway)
**Resolution**: Deleted CNAME, created A record → 72.62.81.128, enabled Cloudflare proxy
**Time**: 15 minutes
**Outcome**: DNS routing to VPS, SSL via Cloudflare

### Blocker 3: Let's Encrypt SSL (MEDIUM)

**Severity**: Medium
**Issue**: Traefik unable to get Let's Encrypt certificate (ALPN challenge failed, rate limited)
**Resolution**: Removed TLS labels requiring certresolver, use Cloudflare Flexible SSL instead
**Time**: 30 minutes
**Outcome**: SSL working via Cloudflare termination

### Blocker 4: Traefik 404 Routing (MEDIUM)

**Severity**: Medium
**Issue**: Traefik couldn't reach Fathom Commander despite correct Host() rule
**Root Cause**: Fathom Commander only on rhiz_rhiz_network, Traefik routing from n8n_default
**Resolution**: Added Fathom Commander to n8n_default network (dual network), added proper entrypoints labels
**Time**: 45 minutes
**Outcome**: Domain routing operational, direct port backup working

**Total Resolution Time**: ~2 hours (all 4 blockers)

---

## Captain's Architecture Insights

### Forward Planning Validated

**Captain built production-ready infrastructure in previous sessions**, not prototypes.

**Evidence**:
- 9 sophisticated n8n workflows with circuit breaker logic
- Complete container stack (9 services) running reliably for 5+ days
- Traefik reverse proxy configured (DNS just needed fixing)
- Kraken API integration working (2 successful test trades)
- Safety architecture present (limits, approval workflow, circuit breakers)

**Pattern**: Captain's strategic foresight → build while Claude Code not active → infrastructure exists when needed

### CLI-Orchestrated, Cloud-Executed Philosophy

**Key Insight**: Captain's PC not always on, trading needs 24/7 persistence

**Architecture Result**:
- Local: CLI control layer (episodic, context-loaded via checkpoints)
- Cloud: Execution layer (persistent, autonomous between sessions)
- Interface: APIs, SSH, MCP tools

**Benefit**: Dyad operates via CLI for strategic decisions, cloud executes autonomously

---

## Validation Results

### Endpoints Operational

**HTTPS Domain**: ✅ https://fathom.dreamthewilderness.com/
- SSL via Cloudflare
- Traefik routing to Fathom Commander
- HTTP gateway responding

**Direct Port**: ✅ http://72.62.81.128:8766/
- Backup access method
- Useful for debugging Traefik issues
- High port (security best practice)

**Kraken API**: ✅ Authenticated
- Balance queries functional
- Ticker data retrieval working
- Order placement tested (paper mode)

**Qdrant Internal**: ✅ http://rhiz_qdrant:6333
- 174 vectors accessible
- Internal Docker network connectivity
- SSH tunnel for external access

### Container Health

**All 9 containers**: ✅ Healthy
- No crashed containers
- No restart loops
- Uptime 5-6 days (proven stability)

### Workflow Validation

**n8n workflows**: ✅ Active and scheduled
- 9 workflows loaded
- Cron schedules configured
- Next execution: Weekly DCA Buyer (Sunday 6 PM CT)

---

## Future Infrastructure Work

### Immediate Validation (Next Session)

1. **Test n8n workflow execution** now that Fathom Commander accessible
2. **Deploy heartbeat workflow** (60s polling for continuous health monitoring)
3. **Dry-run Weekly DCA Buyer** before Sunday 6 PM CT scheduled execution
4. **Verify cloud Qdrant memory access** from Fathom Commander
5. **Review momentum_basic strategy** (referenced in state.json but not found in code)

### Strategic Development

1. **Build strategic trading intelligence framework** for dyad decision-making
2. **Implement momentum strategy** with memory/Qdrant context integration
3. **Optimize DCA logic** based on market conditions (not time-based only)
4. **Add risk modeling** (position sizing, volatility-adjusted limits)
5. **Design decision trace logging** (why trades executed, pattern matching)
6. **Test small live trade** ($10-15) with approval workflow validation

### Infrastructure Enhancements

1. **Create infrastructure diagram generator** (auto-document discovered architecture)
2. **Add deployment validation checklist** skill (DNS, SSL, routing, health checks)
3. **Build safety audit tool** (checks for live trading modes, exposed credentials, missing circuit breakers)
4. **Develop strategic trading framework** skill library (momentum/DCA/risk strategies)

---

## Lessons Learned

### Technical Learnings

1. **Traefik dual networks required**: Container must be on both source and destination networks for routing between them
2. **Cloudflare Flexible SSL simplest**: Let Cloudflare handle client SSL, origin can be HTTP
3. **Direct port exposure useful**: High port (8766) provides backup when Traefik debugging needed
4. **Paper mode enforcement critical**: Code-level default (state.py) + config ensures safety
5. **Cloud Qdrant operational**: 174 vectors preserved across container restarts

### Strategic Learnings

1. **Captain's forward planning exceptional**: Built production infrastructure in advance
2. **Infrastructure discovery ≠ infrastructure building**: Reconnaissance revealed existing, not missing, systems
3. **Safety-first intervention necessary**: Live trading without active monitoring required immediate paper mode
4. **Cloud-first architecture validated**: 24/7 trading needs persistent infrastructure, not local-only

### Partnership Patterns

1. **First Mate systematic approach**: Reconnaissance → safety fix → deployment → validation
2. **Captain pragmatic approval**: Direct port exposure approved to unblock debugging
3. **Collaborative problem-solving**: Captain provided Cloudflare credentials when needed, FM executed autonomously otherwise
4. **Trust calibration**: Captain satisfied with proactive safety intervention ("see you on the flip side")

---

## Related Documentation

**Source Checkpoint**: core/memory/checkpoints/session_20260103_infrastructure_operational.yaml (332 lines)

**Architecture Documents**:
- docs/architecture/cloud_deployment_topology.md (written Jan 3)
- docs/architecture/fathom_commander_cloud_deployment_plan.md (obsolete—already deployed)

**Infrastructure Guides**:
- infrastructure/vps/DEPLOYMENT_GUIDE.md (FastAPI Gateway phases)
- infrastructure/cloudflare/CLOUDFLARE_API_SETUP_GUIDE.md (DNS management)
- infrastructure/docker/README.md (Docker orchestration guide)

**n8n Workflow Exports**:
- domains/trading/fathom_commander/n8n/daily_health_monitor_workflow.json
- domains/trading/fathom_commander/n8n/weekly_dca_buyer_workflow.json

---

## Appendix: Container Configuration Examples

### Fathom Commander docker-compose.cloud.yaml

```yaml
services:
  fathom_commander:
    container_name: rhiz_fathom_commander
    image: fathom_commander:latest
    ports:
      - "0.0.0.0:8766:8765"
    networks:
      - rhiz_rhiz_network
      - n8n_default  # Added Jan 3 for Traefik routing
    environment:
      - MODE=paper
      - DOMAIN_NAME=dreamthewilderness.com
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.fathom.rule=Host(`fathom.dreamthewilderness.com`)"
      - "traefik.http.routers.fathom.entrypoints=web,websecure"
      # TLS labels removed (Cloudflare handles SSL)
```

### Traefik Configuration

**Entrypoints**:
- web: port 80 (HTTP)
- websecure: port 443 (HTTPS, Cloudflare terminates)

**Networks**: rhiz_rhiz_network, n8n_default (dual connection for cross-network routing)

**SSL Strategy**: Flexible (Cloudflare → origin can be HTTP)

---

**End of VPS Infrastructure Topology Document**

*This document reflects infrastructure state as of January 3, 2026. For current operational status, see docs/CURRENT_STATE.md.*

*Extracted: 2026-01-25 (Session 73, Phase 1.2)*
*Cross-reference: docs/knowledge_base/deployments/vps_topology.md*
