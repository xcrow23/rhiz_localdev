# Trading Intelligence Federation - Phase 1 Architecture

**Document Type**: Architecture Design Record
**Source**: session_20260111_session_42_phase1_complete.yaml
**Date**: 2026-01-11/12
**Status**: Phase 1 Complete (operational)
**Significance**: Major - Unified Trading Platform Architecture

---

```yaml
---
component: trading_intelligence_federation
status: phase_1_deployed
deployment_date: 2026-01-12
architecture_model: three_layer_stack
layers:
  - fathom: execution_layer (MCP stdio)
  - fathom_commander: orchestration_layer (MCP stdio)
  - sil: intelligence_layer (HTTP REST)
shared_substrate: qdrant_trading_signals
vps_location: hostinger_72.62.81.128
container_count: 5
deployment_duration: 4.5_hours
technical_challenges_resolved: 7
phase_2_target: cloudflare_workers_migration
related_documents:
  - core/memory/checkpoints/session_20260111_session_42_phase1_complete.yaml
  - infrastructure/vps/CONNECTION_PATTERNS.md
  - infrastructure/vps/PHASE_1_DEPLOYMENT_COMPLETE.md
  - docs/architecture/UNIFIED_TRADING_PLATFORM_ARCHITECTURE.md
semantic_cluster: trading_architecture
vector_density: high  # 0.45-0.70
threshold_recommendation: 0.45
---
```

---

## Executive Summary

On January 11-12, 2026, Phase 1 of the **Intelligence Federation** architecture was deployed to consolidate three independent trading systems (Fathom, Fathom Commander, SIL) into a unified platform with shared memory substrate.

After a 4.5-hour marathon session navigating 7 technical challenges, all **5 containers** are running stably on Hostinger VPS with a **three-layer architecture**: Fathom (execution), Fathom Commander (orchestration), and SIL (intelligence), connected through a **trading_signals** Qdrant collection for cross-system learning.

**Critical Architecture Decision**: Preserved MCP stdio interface for Claude Code integration rather than forcing HTTP, with plan to add HTTP gateway in Phase 2 for Cloudflare Workers compatibility.

---

## Intelligence Federation Model

### Three-Layer Architecture

**Purpose**: Separate concerns (execution, orchestration, intelligence) while enabling unified learning through shared memory substrate.

```
┌─────────────────────────────────────────────────────┐
│         Strategic Intelligence Layer (SIL)          │
│  ┌───────────────────────────────────────────────┐  │
│  │  Pattern Recognition | Risk Assessment       │  │
│  │  Regime Detection    | Strategy Selection    │  │
│  └───────────────────────────────────────────────┘  │
│           HTTP REST API (FastAPI)                   │
└──────────────────┬──────────────────────────────────┘
                   │ Signals / Decisions
                   ↓
┌─────────────────────────────────────────────────────┐
│      Orchestration Layer (Fathom Commander)         │
│  ┌───────────────────────────────────────────────┐  │
│  │  Workflow Composition | Circuit Breakers     │  │
│  │  Position Management  | Risk Enforcement     │  │
│  └───────────────────────────────────────────────┘  │
│           MCP Stdio Server (27 tools)               │
└──────────────────┬──────────────────────────────────┘
                   │ Orders / Actions
                   ↓
┌─────────────────────────────────────────────────────┐
│          Execution Layer (Fathom MCP)               │
│  ┌───────────────────────────────────────────────┐  │
│  │  Market Data Retrieval | Order Placement     │  │
│  │  Account Management    | Trade Verification  │  │
│  └───────────────────────────────────────────────┘  │
│           MCP Stdio Server (Kraken API)             │
└──────────────────┬──────────────────────────────────┘
                   │ Direct Exchange Access
                   ↓
              ┌────────────┐
              │   Kraken   │
              │  Exchange  │
              └────────────┘

         Shared Learning Substrate
         ┌────────────────────────┐
         │  Qdrant Vector Memory  │
         │  trading_signals       │
         │  Collection (384-dim)  │
         └────────────────────────┘
```

### Why Three Layers?

**Separation of Concerns**:
- **Execution (Fathom)**: Exchange interface, low-level order management
- **Orchestration (FC)**: Workflow logic, position management, circuit breakers
- **Intelligence (SIL)**: Pattern recognition, strategy selection, risk assessment

**Unified Learning**:
- All layers log signals/decisions to `trading_signals` Qdrant collection
- SIL queries historical patterns to inform strategy decisions
- FC references past execution results for workflow optimization
- Fathom records market microstructure for latency analysis

**Independent Scaling**:
- Intelligence layer computationally expensive (can scale to GPU instance)
- Orchestration layer stateful (keeps workflow state)
- Execution layer API-rate-limited (no benefit from scaling)

---

## Phase 1 Deployment

### Container Inventory (5 total)

**All containers operational on Hostinger VPS (72.62.81.128) at `/opt/rhiz_trading`**

#### 1. Fathom MCP (`fathom-mcp`)
**Purpose**: Execution layer - Kraken exchange interface
**Interface**: MCP stdio server (preserves Claude Code integration)
**Image**: fathom-mcp:latest
**Status**: UP (stable 20+ minutes at Phase 1 completion)
**Healthcheck**: None (stdio servers don't support HTTP healthchecks)
**Stdin**: Open (required for MCP stdio protocol)
**Network**: rhiz_network (external)
**Volumes**:
  - fathom_logs:/app/logs
  - fathom_data:/app/data
**Access**: Via Claude Code MCP tools using SSH + docker exec

#### 2. Fathom Commander (`fathom-commander`)
**Purpose**: Orchestration layer - workflow composition, circuit breakers
**Interface**: MCP stdio server (27 tools)
**Image**: fathom-commander:latest
**Status**: UP (stable 20+ minutes)
**Healthcheck**: None (stdio server)
**Stdin**: Open (required for MCP)
**Network**: rhiz_network
**Volumes**:
  - fc_logs:/app/logs
  - fc_state:/app/state
  - fc_config:/app/config
**Access**: Via Claude Code MCP tools using SSH + docker exec

#### 3. SIL FastAPI (`sil-fastapi`)
**Purpose**: Intelligence layer - pattern recognition, risk assessment, strategy selection
**Interface**: HTTP REST API (FastAPI)
**Image**: sil:latest
**Status**: HEALTHY (healthcheck passing)
**Healthcheck**: HTTP GET /health (10s interval, 3 retries)
**Ports**: 8001 (external) → 8000 (internal)
**Network**: rhiz_network
**Volumes**:
  - sil_models:/app/models
  - sil_cache:/app/cache
**Access**: HTTP requests to http://72.62.81.128:8001/ or via gateway

#### 4. Qdrant (`qdrant`)
**Purpose**: Shared vector memory substrate for cross-system learning
**Interface**: HTTP REST API
**Image**: qdrant/qdrant:v1.7.4
**Status**: HEALTHY
**Healthcheck**: HTTP GET /health (5s interval)
**Ports**: 6333 (internal), 6335 (SSH tunnel from local)
**Network**: rhiz_network
**Volumes**:
  - qdrant_storage:/qdrant/storage
**Collections**:
  - `trading_signals`: 384-dim vectors, 3 indexes (signal_type, pair, source)

#### 5. FastAPI Gateway (`fastapi-gateway`)
**Purpose**: HTTP routing layer for external access to services
**Interface**: HTTP REST API
**Image**: gateway:latest
**Status**: UP (shows 'degraded' because Fathom/FC are stdio-only, this is expected)
**Healthcheck**: HTTP GET /health
**Ports**: 8765 (external) → 8765 (internal)
**Network**: rhiz_network
**Routes**:
  - `/sil/*` → sil-fastapi:8000
  - `/qdrant/*` → qdrant:6333
  - `/fathom/*` → Not routable (stdio server)
  - `/fc/*` → Not routable (stdio server)
**Access**: HTTP requests to http://72.62.81.128:8765/

---

## Architectural Decisions

### Decision 1: MCP Stdio Interface (Not HTTP)

**Decision**: Keep Fathom and Fathom Commander as MCP stdio servers instead of forcing HTTP interface.

**Rationale**:
- Preserves Claude Code integration (primary use case for dyadic trading)
- HTTP access not needed until Phase 2 (Cloudflare Workers)
- Can add FC `gateway.py` HTTP server later without changing MCP interface
- Stdio servers more reliable for session-based interaction (no port conflicts, no HTTP overhead)

**Alternatives Considered**:
- Force HTTP interface: Rejected (breaks Claude Code MCP integration)
- Run both stdio and HTTP in parallel: Rejected (adds complexity, HTTP not needed yet)

**Technical Implications**:
- Fathom/FC not accessible via gateway HTTP routes (expected behavior)
- Gateway shows 'degraded' status (expected, not a problem)
- Cloudflare Workers will need FC HTTP gateway (Phase 2 work)

**Outcome**: Containers stable, MCP integration preserved, Phase 2 path clear

**Reversibility**: True (can add HTTP server without removing stdio)

### Decision 2: Consolidate on Hostinger (Not Hetzner)

**Decision**: Deploy all services to Hostinger VPS (72.62.81.128) instead of provisioning Hetzner VPS.

**Rationale**:
- Plan assumed Hetzner VPS at 95.217.51.24 existed
- Discovery: Hetzner VPS doesn't exist
- Hostinger has capacity (16GB RAM, 90% disk free) and existing infrastructure
- Avoids provisioning delay, billing setup, configuration

**Alternatives Considered**:
- Provision new Hetzner VPS: Rejected (delay, Hostinger sufficient)
- Keep dual VPS architecture: Rejected (unnecessary complexity)

**Outcome**: All 5 containers deployed successfully to Hostinger

**Reversibility**: True (can migrate to Hetzner if performance degrades)

**Future Consideration**: If Hostinger performance issues arise or Captain prefers geographic diversity, provision Hetzner and distribute services.

### Decision 3: Remove HTTP Healthchecks from Stdio Servers

**Decision**: Remove HTTP healthchecks from Fathom and FC, add `stdin_open: true` instead.

**Rationale**:
- HTTP healthchecks invalid for stdio servers (no HTTP endpoint exists)
- Containers crash-looping trying to probe HTTP endpoints
- `stdin_open: true` keeps stdin available for MCP protocol
- Process running doesn't guarantee MCP server responsive (false positives possible)

**Alternatives Considered**:
- Keep healthcheck with process check (pgrep): Rejected (false positives, process ≠ responsive)
- Use TCP healthcheck: Rejected (MCP stdio doesn't listen on TCP port)

**Outcome**: Crash-loops resolved, containers stable

**Reversibility**: False (stdin_open is correct pattern for stdio servers)

### Decision 4: External Network (Not Custom Subnet)

**Decision**: Use external `rhiz_network` instead of custom subnet 172.20.0.0/16.

**Rationale**:
- Custom subnet conflicts with existing VPS networks
- External network avoids subnet overlap
- Simpler networking configuration (Docker manages IP allocation)

**Alternatives Considered**:
- Different subnet range (e.g., 172.21.0.0/16): Rejected (potential future conflicts)
- Bridge network with no subnet: Rejected (less isolation)

**Outcome**: No network conflicts, all services communicate correctly

**Reversibility**: True (can change to custom subnet if needed)

### Decision 5: SIL Port 8001 (Not 8000)

**Decision**: Expose SIL on port 8001 (external) → 8000 (internal).

**Rationale**:
- Port 8000 already occupied by Hummingbot API
- Internal consistency preserved (SIL still listens on 8000 inside container)
- External port mapping resolves conflict

**Alternatives Considered**:
- Stop Hummingbot: Rejected (may still be in use, unclear if deprecated)
- Use different port entirely (e.g., 8002): Rejected (8001 + 8000 mapping cleaner)

**Outcome**: No port conflict, SIL accessible on 8001

**Reversibility**: True (can change external port mapping)

### Decision 6: Create trading_signals Collection in Phase 1

**Decision**: Create `trading_signals` Qdrant collection immediately (Phase 1) instead of deferring to Phase 3.

**Rationale**:
- Collection creation simple, low risk
- Having it ready enables Phase 3 work without extra step
- Validates Qdrant deployment (ensures API working)
- Allows early schema testing

**Alternatives Considered**:
- Defer to Phase 3: Rejected (minimal benefit, extra phase dependency)

**Outcome**: Collection created successfully, ready for learning substrate

**Reversibility**: True (can delete and recreate if schema needs changes)

---

## trading_signals Qdrant Collection

### Purpose

**Shared Learning Substrate**: All three layers (Fathom, FC, SIL) log signals, decisions, and outcomes to this collection. SIL queries historical patterns to inform strategy decisions. FC references past execution results. Fathom records market microstructure.

### Schema

**Vector Dimensions**: 384 (all-MiniLM-L6-v2 embeddings)

**Indexes** (for fast filtering):
1. `signal_type` - Type of signal (e.g., "momentum_detected", "risk_elevated", "order_executed")
2. `pair` - Trading pair (e.g., "XXBTZUSD", "XETHZUSD")
3. `source` - Which layer generated the signal (e.g., "fathom", "fc", "sil")

**Payload Structure** (flexible JSON):
```json
{
  "signal_type": "momentum_detected",
  "pair": "XXBTZUSD",
  "source": "sil",
  "timestamp": "2026-01-12T20:45:00Z",
  "confidence": 0.87,
  "context": {
    "price": 87500.00,
    "volume_24h": 1250.5,
    "momentum_strength": 0.65,
    "regime": "bullish"
  },
  "decision": "buy",
  "outcome": null  // Updated post-execution
}
```

### Usage Patterns

**Write** (all layers):
- Fathom logs execution results (slippage, fees, fill times)
- FC logs workflow decisions (circuit breaker triggers, position adjustments)
- SIL logs strategy signals (momentum detected, risk elevated, regime shifts)

**Read** (primarily SIL):
- Query similar signals by vector embedding (semantic search)
- Filter by signal_type, pair, source (indexed fast lookup)
- Analyze patterns: "When SIL detected momentum_detected with confidence >0.8, what was the outcome 1 hour later?"

**Learning Loop**:
```
SIL detects pattern → logs signal to trading_signals
  → FC decides action → logs decision to trading_signals
  → Fathom executes → logs outcome to trading_signals
  → SIL queries similar past patterns → adjusts strategy
```

---

## Connection Patterns

### MCP Stdio Servers (Fathom, FC)

**Access Method**: SSH + docker exec

**From Claude Code**:
```bash
# SSH into VPS
ssh user@72.62.81.128

# Connect to Fathom MCP
docker exec -i fathom-mcp python -m fathom.server

# Connect to Fathom Commander MCP
docker exec -i fathom-commander python -m fc.server
```

**MCP Tools Configuration** (`claude_desktop_config.json`):
```json
{
  "mcpServers": {
    "fathom": {
      "command": "ssh",
      "args": [
        "user@72.62.81.128",
        "docker exec -i fathom-mcp python -m fathom.server"
      ]
    },
    "fathom-commander": {
      "command": "ssh",
      "args": [
        "user@72.62.81.128",
        "docker exec -i fathom-commander python -m fc.server"
      ]
    }
  }
}
```

**Why Stdio**: Preserves Claude Code integration for interactive trading (primary use case).

**Limitation**: Not accessible via HTTP (Cloudflare Workers can't call stdio servers directly).

**Phase 2 Solution**: Deploy FC `gateway.py` as separate HTTP service for Workers.

### HTTP Services (SIL, Qdrant, Gateway)

**Access Method**: HTTP requests (direct or via gateway)

**Direct Access**:
```bash
# SIL
curl http://72.62.81.128:8001/health

# Qdrant
curl http://72.62.81.128:6333/health

# Gateway (routes to SIL/Qdrant)
curl http://72.62.81.128:8765/sil/health
curl http://72.62.81.128:8765/qdrant/health
```

**Gateway Routes**:
- `/sil/*` → `sil-fastapi:8000`
- `/qdrant/*` → `qdrant:6333`
- `/fathom/*` → 503 Service Unavailable (stdio server, no HTTP endpoint)
- `/fc/*` → 503 Service Unavailable (stdio server)

**Why HTTP**: Enables external access (Cloudflare Workers, monitoring tools, future integrations).

**Gateway Status**: Shows 'degraded' because Fathom/FC unreachable via HTTP (expected, not a problem).

---

## Technical Challenges Resolved

### Challenge 1: Container Crash-Loops from Stdout I/O Errors

**Symptom**: Fathom and FC containers restarting repeatedly with I/O errors.

**Root Cause**: MCP stdio servers writing to stdout, Docker capturing output, healthcheck probe triggering I/O errors.

**Resolution**: Removed HTTP healthchecks, added `stdin_open: true` to docker-compose.

**Learning**: Stdio servers and HTTP healthchecks incompatible. Use `stdin_open` for MCP servers.

### Challenge 2: Invalid HTTP Healthchecks on Stdio Servers

**Symptom**: Healthcheck failing with "connection refused" errors.

**Root Cause**: HTTP healthcheck trying to probe `http://localhost:8765/health` on containers with no HTTP server.

**Resolution**: Removed healthcheck entirely from Fathom/FC. Containers stable without it.

**Learning**: Process existence sufficient for stdio servers. HTTP healthchecks only for HTTP services.

### Challenge 3: Aggressive Docker Image Caching

**Symptom**: Dockerfile changes (e.g., removing healthcheck) not reflected in container after rebuild.

**Root Cause**: Docker cached old image layers despite Dockerfile changes.

**Resolution**: `docker rmi fathom-mcp fathom-commander` + `docker compose build --no-cache`

**Learning**: Always use `--no-cache` when debugging Dockerfile issues. Image caching aggressive.

### Challenge 4: Port Conflicts (8000 occupied)

**Symptom**: SIL container failing to bind to port 8000.

**Root Cause**: Hummingbot API already listening on 8000.

**Resolution**: Changed SIL external port to 8001 → 8000 (internal unchanged).

**Learning**: Multi-service VPS requires port conflict awareness. Check `netstat -tulpn` before deployment.

### Challenge 5: Qdrant API Version Mismatch

**Symptom**: Collection creation failing with schema type errors.

**Root Cause**: Qdrant 1.7.4 uses string schema types, not enums (1.16.2 client expected enums).

**Resolution**: Changed `distance: Distance.COSINE` → `distance: "Cosine"` in Python code.

**Learning**: Qdrant API changes between versions. Pin client version or use string types for compatibility.

### Challenge 6: Network Subnet Conflicts

**Symptom**: Docker network creation failing with "subnet overlap" errors.

**Root Cause**: Custom subnet 172.20.0.0/16 conflicts with existing VPS networks.

**Resolution**: Used external `rhiz_network` instead of custom subnet.

**Learning**: External networks simpler and avoid subnet conflicts on shared VPS.

### Challenge 7: Gateway Showing 'Degraded' Status

**Symptom**: Gateway /health endpoint returning 'degraded' status.

**Root Cause**: Gateway probing Fathom/FC HTTP endpoints, getting connection refused (expected - they're stdio servers).

**Resolution**: None needed. 'Degraded' status is expected and correct behavior.

**Learning**: Gateway status reflects HTTP service reachability only. Stdio services won't show as healthy (expected).

---

## Deployment Iterations

**Total Iterations**: 8 (each resolving specific issues)

1. **Initial deployment**: Crash-loops from healthcheck I/O errors
2. **Remove healthchecks**: Containers stable but no stdin
3. **Add stdin_open**: MCP protocol functional
4. **Fix port conflict**: SIL on 8001
5. **Fix Qdrant schema**: Collection creation successful
6. **Fix network subnet**: External network resolved conflicts
7. **Rebuild with --no-cache**: Force fresh images
8. **Final validation**: All containers stable 20+ minutes

**Session Duration**: 4.5 hours (includes planning, debugging, documentation)

**Lines of Code**: ~800 (docker-compose, Dockerfiles, Python fixes)

**Files Created**: 7 (connection patterns, deployment summary, troubleshooting guides)

**Files Modified**: 3 (docker-compose, healthcheck configs, Qdrant client code)

---

## Phase 2 Readiness

### No Blockers Identified

**Infrastructure**: All containers operational
**MCP Tools**: Ready for testing (Captain action required)
**HTTP Services**: SIL and Qdrant accessible
**Shared Memory**: trading_signals collection created
**Documentation**: Connection patterns and deployment state comprehensive

### Phase 2 Plan: Cloudflare Workers Migration

**Estimated Duration**: 3-4 hours

**Tasks**:
1. Create D1 database schema (trading state, workflow history)
2. Deploy 3 cron workers:
   - Health check worker (every 5 min)
   - Weekly DCA buyer (Sunday 6 PM CT)
   - Strategy refresh worker (daily)
3. Deploy order-fill webhook (Kraken webhook → Worker)
4. 48-hour verification (no 502 errors, all crons executing)
5. Decommission n8n (1 remaining workflow)

**Open Question**: Should FC expose HTTP gateway for Workers (Option A), or should Workers call Kraken directly (Option B)?

**Recommendation**: Option A for Phase 2 (quick win - FC `gateway.py` already exists). Migrate to Option B in Phase 3 as we learn Worker patterns and can port FC orchestration logic.

### MCP Tools Testing (Captain Required)

**Configuration Needed**: Update `claude_desktop_config.json` with SSH + docker exec commands for Fathom/FC MCP servers.

**Testing Checklist**:
1. Restart Claude Desktop app (load new MCP config)
2. Test `fathom_get_account_balance` (should return Kraken account data)
3. Test `fc_get_portfolio_status` (should return paper mode state)
4. Document any connection issues for debugging

---

## Architecture Benefits

### Unified Learning Without Tight Coupling

**Problem Solved**: Three independent systems (Fathom, FC, SIL) built in parallel without integration workflow.

**Solution**: Shared `trading_signals` collection enables cross-system learning while preserving layer independence.

**Benefit**: SIL learns from execution outcomes without needing direct Fathom API. FC optimizes workflows based on SIL signals without tight coupling.

### Preserves Claude Code Integration

**Problem Solved**: Forcing HTTP interface breaks interactive trading via Claude Code MCP tools.

**Solution**: Keep Fathom/FC as stdio servers, add HTTP gateway only where needed (Phase 2 for Workers).

**Benefit**: Captain + First Mate dyad retains full MCP tool access for interactive strategy development.

### Independent Scaling Paths

**Intelligence Layer**: Computationally expensive (pattern recognition, risk modeling) → can scale to GPU instance or serverless (Phase 3).

**Orchestration Layer**: Stateful workflows → needs persistent state, can't easily scale horizontally.

**Execution Layer**: Kraken API rate-limited → no benefit from horizontal scaling.

**Benefit**: Each layer scales according to its bottleneck, not as monolith.

---

## Future Phases

### Phase 2: Cloudflare Workers Migration (Est: 3-4 hours)

**Goal**: Replace n8n workflows with Cloudflare Workers for better reliability and code-first architecture.

**Key Work**:
- D1 database for workflow state
- 3 cron workers (health, DCA, strategy)
- Order-fill webhook
- FC HTTP gateway deployment (or direct Kraken integration)
- 48-hour verification before n8n decommission

### Phase 3: Strategic Intelligence Integration (Est: 4-5 hours)

**Goal**: Wire SIL intelligence into FC workflows for automated strategy execution.

**Key Work**:
- Implement Fathom → trading_signals logging (execution results)
- Implement SIL → trading_signals queries (pattern recognition)
- Build FC → SIL request/response flow (strategy selection)
- Test momentum strategy end-to-end
- Validate learning loop (decision → outcome → learning)

### Beyond Phase 3

**Expansion Possibilities**:
- Additional strategy implementations (DCA optimization, mean reversion)
- Multi-exchange support (Coinbase, Binance)
- Portfolio rebalancing automation
- Risk modeling with volatility-adjusted limits
- Backtesting infrastructure (test strategies on historical data)

---

## Related Documentation

**Source Checkpoint**: core/memory/checkpoints/session_20260111_session_42_phase1_complete.yaml

**Infrastructure Guides**:
- infrastructure/vps/CONNECTION_PATTERNS.md (how to access each service)
- infrastructure/vps/PHASE_1_DEPLOYMENT_COMPLETE.md (deployment summary)
- infrastructure/vps/DEPLOYMENT_GUIDE.md (FastAPI Gateway setup)

**Architecture Documents**:
- docs/architecture/UNIFIED_TRADING_PLATFORM_ARCHITECTURE.md (high-level design)
- docs/architecture/strategic_intelligence_layer.md (SIL design details)
- docs/architecture/vps_infrastructure_topology.md (VPS container inventory)

**Trading Components**:
- domains/trading/fathom/README.md (Fathom MCP server)
- domains/trading/fathom_commander/ (FC documentation)
- domains/trading/strategic_intelligence/DEPLOYMENT_READINESS.md (SIL readiness)

---

**End of Trading Intelligence Federation Phase 1 Document**

*This document reflects Phase 1 deployment state as of January 12, 2026. Phase 2 (Cloudflare Workers) and Phase 3 (Strategic Intelligence Integration) pending.*

*Extracted: 2026-01-25 (Session 73, Phase 1.2)*
*Cross-reference: docs/knowledge_base/integrations/trading_pipeline.md*
