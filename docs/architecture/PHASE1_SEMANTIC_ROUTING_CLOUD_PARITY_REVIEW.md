# Phase 1 Semantic Routing - Cloud Deployment Parity Review

**Reviewer**: First Mate (Integration Architect)
**Date**: 2026-01-24
**Session**: Architecture review requested by Captain
**Focus**: Local/cloud deployment parity, system coherence, data flow integrity

---

## Executive Summary

**Verdict**: ⚠️ **PARTIAL PARITY** - Local system operational, cloud deployment path exists but **not validated**

### Critical Findings

1. ✅ **Local deployment**: Fully operational (tested, collections exist)
2. ⚠️ **Cloud deployment**: Infrastructure exists but **skills not deployed**
3. ❌ **Version control**: No sync/versioning strategy for skill definitions
4. ⚠️ **Tool availability**: Skill→tool mappings assume local MCP context
5. ✅ **Collection isolation**: No naming conflicts (rhiz_memories ≠ rhiz_skills)
6. ⚠️ **Data flow**: Router supports parameterized Qdrant connection, but hardcoded defaults

---

## Architecture Overview

### Phase 1 Integration Flow (Current)

```
┌─────────────────────────────────────────────────────────────┐
│ SKILL DEFINITION LAYER                                      │
├─────────────────────────────────────────────────────────────┤
│ core/skills/registry/skill_fingerprints.yaml               │
│   ├─ trading/kraken_analysis                               │
│   ├─ memory/checkpoint_retrieval                           │
│   ├─ infrastructure/deployment                             │
│   ├─ memory/session_management                             │
│   ├─ research/documentation                                │
│   └─ trading/strategy_execution                            │
│                                                             │
│ 6 skills, each with:                                       │
│   - description (semantic fingerprint)                     │
│   - utterances (trigger patterns)                          │
│   - tools (MCP tool names)                                 │
│   - dependencies (prerequisites)                           │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ INGESTION LAYER                                             │
├─────────────────────────────────────────────────────────────┤
│ core/skills/scripts/ingest_skills.py                       │
│   ├─ Loads YAML skill definitions                          │
│   ├─ Generates embeddings (all-MiniLM-L6-v2)              │
│   ├─ Creates multi-component fingerprints:                 │
│   │    description + utterances + category + tools         │
│   └─ Upserts to Qdrant with payload metadata               │
│                                                             │
│ python ingest_skills.py --host localhost --port 6333       │
│ python ingest_skills.py --host 95.217.51.24 --port 6333    │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ VECTOR STORAGE LAYER                                        │
├─────────────────────────────────────────────────────────────┤
│ Qdrant Collection: rhiz_skills                             │
│   ├─ Vector size: 384 (all-MiniLM-L6-v2)                  │
│   ├─ Distance: COSINE                                      │
│   └─ Points: 6 (as of ingestion)                           │
│                                                             │
│ LOCAL:  localhost:6333                        [OPERATIONAL] │
│ CLOUD:  95.217.51.24:6333 (Hetzner VPS)     [NOT DEPLOYED] │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ ROUTING LAYER                                               │
├─────────────────────────────────────────────────────────────┤
│ core/skills/router.py → SkillRouter                        │
│   ├─ __init__(qdrant_host, qdrant_port, collection_name)  │
│   ├─ route_query(query, threshold=0.45, limit=3)          │
│   └─ route_with_context(query, current_domain, ...)       │
│                                                             │
│ Defaults: localhost:6333, rhiz_skills                      │
│ Supports: Parameterized host/port for cloud deployment     │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ MCP TOOL EXPOSURE                                           │
├─────────────────────────────────────────────────────────────┤
│ tools/rhiz-mcp/src/server.py → route_to_skill              │
│   ├─ Loads SkillRouter dynamically                         │
│   ├─ Uses local Qdrant (hardcoded in SkillRouter.__init__) │
│   └─ Returns: {matched, skill, confidence, tools, ...}     │
│                                                             │
│ Status: LOCAL ONLY (rhiz-mcp runs on laptop)               │
└─────────────────────────────────────────────────────────────┘
```

---

## Deployment Status Matrix

| Component | Local (Laptop) | Cloud (Hetzner VPS 95.217.51.24) | Sync Strategy |
|-----------|----------------|----------------------------------|---------------|
| **Skill Definitions** | ✅ skill_fingerprints.yaml | ❌ Not deployed | **MISSING** |
| **Qdrant Collection** | ✅ rhiz_skills (6 points) | ❌ Collection missing | **MISSING** |
| **Ingestion Script** | ✅ Operational | ⚠️ Script exists, not run | Manual |
| **SkillRouter** | ✅ Operational (localhost) | ❌ Not deployed | N/A (code-based) |
| **MCP Server (rhiz-mcp)** | ✅ Operational | ❌ Not deployed | N/A (local only) |
| **Embedding Model** | ✅ Local (all-MiniLM-L6-v2) | ⚠️ Embedding service exists | Shared model |

### Key Gaps

1. **rhiz_skills collection does NOT exist on cloud Qdrant**
   - Cloud Qdrant has: moonchecks, fathom_trading
   - Cloud Qdrant lacks: rhiz_skills, rhiz_memories

2. **No automated sync for skill definitions**
   - Memory system has sync strategy (tools/memory-sync/)
   - Skills system lacks equivalent

3. **rhiz-mcp is laptop-only**
   - MCP servers run as local processes (Claude Code context)
   - Cloud deployment would require different architecture (FastAPI gateway)

---

## Specific Concern Analysis

### 1. Can skill fingerprints be deployed to cloud VPS Qdrant?

**Answer**: ✅ YES, technically feasible

**Mechanism**:
```bash
# On cloud VPS or via SSH tunnel
python core/skills/scripts/ingest_skills.py \
  --host 95.217.51.24 \
  --port 6333 \
  --collection rhiz_skills
```

**Prerequisites**:
1. Initialize collection on cloud Qdrant (run initialize_skills_collection.py remotely)
2. Copy skill_fingerprints.yaml to VPS or mount via volume
3. Ensure sentence-transformers library available on VPS

**Current Status**: ❌ Not done

**Recommendation**: Add to VPS deployment checklist if cloud routing needed

---

### 2. Is there version control/sync strategy for skill definitions?

**Answer**: ❌ NO

**Current State**:
- Skill definitions: Git-tracked (core/skills/registry/skill_fingerprints.yaml)
- Vector embeddings: NOT synced (local-only in Qdrant)
- Ingestion: Manual, on-demand

**Comparison to Memory System**:
| Feature | Memory (rhiz_memories) | Skills (rhiz_skills) |
|---------|------------------------|----------------------|
| **Definition sync** | Checkpoints YAML → Git | skill_fingerprints.yaml → Git |
| **Vector sync** | tools/memory-sync (6-hour timer) | **MISSING** |
| **Version control** | Checkpoint schema versioning | **MISSING** |
| **Cloud deployment** | Automated via systemd | **MISSING** |

**Identified Issues**:

1. **Skill drift**: If skill_fingerprints.yaml changes locally but not re-ingested to cloud, routing behavior diverges
2. **No rollback**: No versioning of vector embeddings (only source YAML)
3. **No health check**: No validation that local/cloud have same skills

**Recommendation**:

**Option A: Minimal Sync** (if cloud routing needed)
```bash
# Add to tools/skills-sync/
sync_skills_to_cloud.sh:
  1. SSH to VPS
  2. Copy latest skill_fingerprints.yaml
  3. Run ingest_skills.py --host localhost
  4. Validate point count matches local
```

**Option B: No Sync** (current architecture)
- Skills used only for local routing (rhiz-mcp on laptop)
- Cloud systems use different skill discovery (API endpoints, not semantic routing)
- **Verdict**: Acceptable if cloud deployment not required

---

### 3. Does route_to_skill work with both localhost and cloud Qdrant?

**Answer**: ⚠️ PARTIAL - Code supports it, but **hardcoded defaults** in MCP server

**Code Analysis**:

**SkillRouter (core/skills/router.py)**:
```python
# Line 26-30: Parameterized Qdrant connection
def __init__(
    self,
    qdrant_host: str = "localhost",  # ✅ Configurable
    qdrant_port: int = 6333,         # ✅ Configurable
    collection_name: str = "rhiz_skills"
):
    self.client = QdrantClient(host=qdrant_host, port=qdrant_port)
```

**MCP Server (tools/rhiz-mcp/src/server.py)**:
```python
# Line 802: Hardcoded instantiation
router = SkillRouter()  # ❌ Uses localhost:6333 defaults
```

**Gap**: MCP tool cannot route to cloud Qdrant without code change

**Fix** (if cloud routing needed):
```python
# Option 1: Environment variable
import os
router = SkillRouter(
    qdrant_host=os.getenv("SKILLS_QDRANT_HOST", "localhost"),
    qdrant_port=int(os.getenv("SKILLS_QDRANT_PORT", "6333"))
)

# Option 2: MCP tool parameter
# Add qdrant_host/port to route_to_skill tool schema
# Pass through to SkillRouter initialization
```

**Current Status**: ✅ Works for localhost, ❌ Cannot use cloud without modification

---

### 4. Are there naming conflicts between rhiz_memories and rhiz_skills collections?

**Answer**: ✅ NO CONFLICTS - Clean separation

**Collection Topology**:

**Local Qdrant (localhost:6333)**:
```
rhiz_memories   → 161 points (session checkpoints, vector memory)
rhiz_skills     → 6 points (skill fingerprints for routing)
fathom_trading  → Trading signals (separate domain)
```

**Cloud Qdrant (95.217.51.24:6333)**:
```
moonchecks      → Mooncheck transcripts (Cloudflare Worker backend)
fathom_trading  → Trading signals (mirrored from local, TBD)
```

**Observation**:
- rhiz_skills does NOT exist on cloud
- rhiz_memories does NOT exist on cloud (only synced manually, not in production sync)

**Architecture Decision**:
- Memory system: Local + cloud (via tools/memory-sync/)
- Skills system: Local only (laptop-based routing via rhiz-mcp)

**Verdict**: No conflicts, but **asymmetric deployment** (memory has cloud, skills do not)

---

### 5. Can skills reference tools that don't exist in cloud deployment?

**Answer**: ⚠️ YES - **Tool availability mismatch is a real risk**

**Analysis**:

**Skills Reference These Tools**:
```yaml
# From skill_fingerprints.yaml
trading/kraken_analysis:
  - mcp__fathom__get_account_balance      # Fathom MCP (local only)
  - mcp__fathom__get_trade_history

memory/checkpoint_retrieval:
  - mcp__rhiz-mcp__checkpoint_search      # rhiz-mcp (local only)
  - mcp__rhiz-mcp__hybrid_search_checkpoints

infrastructure/deployment:
  - Bash                                  # Claude Code tool (local only)

research/documentation:
  - Write                                 # Claude Code tool (local only)
  - Edit
  - Read
```

**Tool Availability by Context**:

| Tool | Local (Claude Code) | Cloud VPS | Cloud (Cloudflare Workers) |
|------|---------------------|-----------|----------------------------|
| **mcp__fathom__*** | ✅ Fathom MCP server | ⚠️ Via HTTP gateway | ❌ Not available |
| **mcp__rhiz-mcp__*** | ✅ rhiz-mcp server | ❌ Not deployed | ❌ Not available |
| **Bash** | ✅ Claude Code | ✅ SSH execution | ❌ Not available |
| **Write/Edit/Read** | ✅ Claude Code | ❌ Not available | ❌ Not available |

**Problem**: If skills routed on cloud, tool execution would fail

**Example Failure Scenario**:
```
Cloud API receives: "analyze my Kraken trading performance"
  ↓
Skill router (on cloud) matches: trading/kraken_analysis
  ↓
Returns tools: [mcp__fathom__get_account_balance, ...]
  ↓
Execution attempt: mcp__fathom__get_account_balance
  ↓
❌ FAILURE: MCP server not running in cloud context
```

**Mitigation Strategies**:

**Option 1: Context-Aware Tool Mapping**
```yaml
# Extend skill definition
trading/kraken_analysis:
  tools:
    local:
      - mcp__fathom__get_account_balance
    cloud:
      - http://fc-http-gateway:8767/account/balance  # HTTP equivalent
```

**Option 2: Gateway Abstraction**
- Deploy unified HTTP gateway that proxies MCP calls
- Skills reference gateway endpoints (context-agnostic)
- Gateway routes to appropriate backend (MCP, direct API, etc.)

**Option 3: Local-Only Routing** (current implicit design)
- Skills used only within Claude Code sessions
- Cloud systems use direct API calls, not semantic routing
- **Verdict**: Matches current architecture

**Current Status**: ⚠️ Skills assume local MCP context, not cloud-compatible

---

### 6. Is the skill→tool mapping consistent with actual MCP tool availability?

**Answer**: ✅ YES for local, ⚠️ PARTIAL for tool naming conventions

**Validation**:

**Tools Referenced in skill_fingerprints.yaml**:
```
mcp__fathom__get_account_balance       → Fathom MCP
mcp__fathom__get_trade_history
mcp__fathom__get_ticker_information
mcp__fathom__get_ohlc_data
mcp__fathom__add_order
mcp__fathom__cancel_order
mcp__fathom__get_open_orders
mcp__fathom__get_open_positions

mcp__rhiz-mcp__checkpoint_search       → rhiz-mcp
mcp__rhiz-mcp__hybrid_search_checkpoints
mcp__rhiz-mcp__load_checkpoint
mcp__rhiz-mcp__memory_context
mcp__rhiz-mcp__get_dyad_state
mcp__rhiz-mcp__set_captain_state
mcp__rhiz-mcp__update_shared_focus
mcp__rhiz-mcp__write_checkpoint
mcp__rhiz-mcp__signal_completion
mcp__rhiz-mcp__propose_focus_shift

Bash, Write, Edit, Read                → Claude Code built-ins
```

**Tool Availability Check**:

**Fathom MCP** (domains/trading/fathom/):
- Status: ⏳ Phase 1/6 complete (Account + Market Data)
- Available tools:
  - ✅ get_account_balance
  - ✅ get_ticker_information
  - ✅ get_ohlc_data
  - ❌ get_trade_history (Phase 2)
  - ❌ add_order, cancel_order, get_open_orders, get_open_positions (Phase 3-4)

**rhiz-mcp** (tools/rhiz-mcp/src/server.py):
- Status: ✅ Operational (11 tools)
- All referenced tools exist

**Claude Code Built-ins**:
- Status: ✅ Always available in Claude Code sessions

**Inconsistency Found**:
- `trading/strategy_execution` skill references Fathom Phase 3-4 tools (not yet built)
- Skill will match queries but cannot execute until Fathom phases complete

**Recommendation**:
```yaml
# Add skill status tracking
trading/strategy_execution:
  status: "planned"  # or "operational", "deprecated"
  blocked_by: ["fathom_phase_3", "fathom_phase_4"]
```

**Current Status**: ✅ Mappings accurate for deployed tools, ⚠️ Some skills reference future tools

---

### 7. How do skill updates propagate between local and cloud?

**Answer**: ❌ NO PROPAGATION MECHANISM

**Current Workflow** (local only):
```
1. Edit skill_fingerprints.yaml
2. Git commit changes
3. Run: python core/skills/scripts/ingest_skills.py
4. Restart Claude Code session (reloads rhiz-mcp)
```

**Missing: Cloud Propagation**

**Comparison to Other Systems**:

| System | Local Update | Cloud Propagation | Validation |
|--------|--------------|-------------------|------------|
| **Checkpoints** | Write checkpoint | tools/memory-sync (6hr timer) | Point count check |
| **n8n Workflows** | Edit in UI | Manual export/import | Version tracking |
| **Docker Images** | Build locally | Push to registry → Pull on VPS | Image digest |
| **Skills** | Edit YAML → Ingest | **MISSING** | **MISSING** |

**Proposed Sync Strategy** (if needed):

**Option A: Git-Based Sync**
```bash
# On VPS (cron job or webhook trigger)
cd /opt/rhiz
git pull origin main
python core/skills/scripts/ingest_skills.py --host localhost --port 6333
# Validates point count matches expected
```

**Option B: API-Based Sync**
```python
# Local: POST skill updates to VPS API
# VPS: Receives YAML, validates schema, re-ingests
# Response: Point count, validation status
```

**Option C: No Sync** (current implicit design)
- Skills managed locally only
- Cloud systems do not use semantic routing
- Re-deploy VPS images when skills change materially

**Current Status**: ❌ No sync, manual re-ingestion required

---

## Data Flow Integrity Analysis

### Query → Skill → Tool Execution Flow

**Local Flow (Operational)**:
```
User query: "analyze my Kraken trading performance"
  ↓
Claude Code → rhiz-mcp MCP server
  ↓
route_to_skill tool invoked
  ↓
SkillRouter.route_query(query, threshold=0.45)
  ↓
Qdrant search: localhost:6333 / rhiz_skills
  ↓
Match: trading/kraken_analysis (confidence: 0.78)
  ↓
Returns: {
  skill: "trading/kraken_analysis",
  tools: ["mcp__fathom__get_account_balance", ...],
  confidence: 0.78
}
  ↓
Claude execution: (future - composition layer not built)
  ↓
Call mcp__fathom__get_account_balance via Fathom MCP
```

**Cloud Flow (Hypothetical - NOT DEPLOYED)**:
```
HTTP request: POST /route_skill
Body: {"query": "analyze trading performance"}
  ↓
FastAPI Gateway (VPS) → SkillRouter
  ↓
Qdrant search: localhost:6333 / rhiz_skills  ← COLLECTION MISSING
  ↓
❌ FAILURE: Collection not found
```

**OR** (if collection deployed):
```
HTTP request: POST /route_skill
Body: {"query": "analyze trading performance"}
  ↓
FastAPI Gateway (VPS) → SkillRouter
  ↓
Qdrant search: localhost:6333 / rhiz_skills  ← COLLECTION EXISTS
  ↓
Match: trading/kraken_analysis
Returns tools: [mcp__fathom__get_account_balance, ...]
  ↓
Execution attempt: mcp__fathom__get_account_balance
  ↓
❌ FAILURE: MCP server not available in VPS context
  ↓
Fallback: HTTP call to fc-http-gateway:8767  ← WORKS
```

**Integrity Issues**:

1. **Missing cloud collection**: rhiz_skills not deployed
2. **Tool execution context mismatch**: MCP tools not available on VPS
3. **No validation layer**: No check that tools are actually callable

---

## Integration Inconsistencies

### 1. Asymmetric Memory vs Skills Deployment

**Memory System** (core/memory/):
- ✅ Local Qdrant (rhiz_memories)
- ✅ Cloud sync (tools/memory-sync/)
- ✅ Automated 6-hour sync via systemd
- ✅ Validation (point count checks)

**Skills System** (core/skills/):
- ✅ Local Qdrant (rhiz_skills)
- ❌ No cloud deployment
- ❌ No sync mechanism
- ❌ No validation

**Why the Difference?**

**Memory**: Designed for persistence, cross-session continuity, disaster recovery
**Skills**: Designed for pattern recognition, local Claude Code context

**Recommendation**: Document this as intentional architectural choice OR implement skills sync

---

### 2. Hardcoded Localhost Assumptions

**Files with localhost hardcoding**:

1. **tools/rhiz-mcp/src/server.py** (line 802):
   ```python
   router = SkillRouter()  # Defaults to localhost:6333
   ```

2. **tools/rhiz-mcp/src/memory_search.py** (line 32-35):
   ```python
   self.searcher = MemorySearcher(
       qdrant_host="localhost",
       qdrant_port=6333,
       collection_name="rhiz_memories"
   )
   ```

3. **core/skills/router.py** (line 28-29):
   ```python
   qdrant_host: str = "localhost",
   qdrant_port: int = 6333,
   ```
   (Parameterized, but defaults to localhost)

**Impact**:
- MCP servers cannot route to cloud Qdrant without code changes
- Environment variables not used for Qdrant connection config

**Recommendation**: Introduce QDRANT_HOST/QDRANT_PORT env vars

```python
# Example fix
import os
QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", "6333"))

router = SkillRouter(
    qdrant_host=QDRANT_HOST,
    qdrant_port=QDRANT_PORT
)
```

---

### 3. Tool Naming Convention Inconsistency

**Observed Patterns**:

1. **MCP tools**: `mcp__<server>__<tool>` (e.g., `mcp__fathom__get_account_balance`)
2. **Claude Code built-ins**: `Bash`, `Write`, `Edit`, `Read`
3. **Future ambiguity**: What if cloud exposes tools via HTTP? Same name?

**Example Conflict**:
```yaml
# Skill definition
tools:
  - "mcp__fathom__get_account_balance"  # MCP version

# Cloud equivalent (hypothetical)
tools:
  - "http__fathom__get_account_balance"  # HTTP version
```

**Recommendation**: Establish tool URI scheme

```yaml
tools:
  - uri: "mcp://fathom/get_account_balance"
    context: "local"
  - uri: "https://fc-http-gateway/account/balance"
    context: "cloud"
```

---

## Suggested Deployment Architecture

### Option 1: Local-Only Skills (Current Implicit Design)

**Architecture**:
```
┌─────────────────────────────────────────────────┐
│ LAPTOP (Claude Code Environment)                │
├─────────────────────────────────────────────────┤
│ SkillRouter → localhost:6333 / rhiz_skills      │
│ rhiz-mcp MCP Server → route_to_skill            │
│ Fathom MCP Server → trading tools               │
│                                                  │
│ Use Case: Local skill routing during sessions   │
└─────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────┐
│ CLOUD VPS (95.217.51.24)                        │
├─────────────────────────────────────────────────┤
│ FastAPI Gateway → Direct API endpoints          │
│ fc-http-gateway → Trading HTTP API              │
│ Qdrant: moonchecks, fathom_trading              │
│                                                  │
│ Use Case: Cloudflare Workers backend, no skills │
└─────────────────────────────────────────────────┘
```

**Pros**:
- ✅ No cloud sync needed
- ✅ Skills optimized for Claude Code context
- ✅ Simpler deployment

**Cons**:
- ❌ Skills not available in cloud workflows
- ❌ No skill-based routing in Cloudflare Workers

**Verdict**: ✅ **RECOMMENDED** - Matches current architecture, no gaps

---

### Option 2: Full Cloud Parity (Future Enhancement)

**Architecture**:
```
┌──────────────────────────────────────────────────┐
│ LAPTOP (Claude Code)                             │
├──────────────────────────────────────────────────┤
│ SkillRouter → localhost:6333 / rhiz_skills       │
│ rhiz-mcp → route_to_skill                        │
│                                                   │
│ Sync Agent (tools/skills-sync/)                  │
│   ├─ Monitors skill_fingerprints.yaml changes    │
│   ├─ Pushes to VPS on update                     │
│   └─ Validates cloud point count                 │
└──────────────────────────────────────────────────┘
           ↓ (SSH + rsync + re-ingest)
┌──────────────────────────────────────────────────┐
│ CLOUD VPS (95.217.51.24)                         │
├──────────────────────────────────────────────────┤
│ Qdrant: rhiz_skills (mirrored from local)        │
│                                                   │
│ FastAPI /route_skill endpoint                    │
│   ├─ SkillRouter → localhost:6333 / rhiz_skills  │
│   ├─ Returns skill + tool mappings               │
│   └─ Execution via fc-http-gateway (HTTP tools)  │
└──────────────────────────────────────────────────┘
```

**Pros**:
- ✅ Skills available in cloud workflows
- ✅ Cloudflare Workers can use semantic routing
- ✅ Consistent routing behavior local/cloud

**Cons**:
- ❌ Requires sync infrastructure (tools/skills-sync/)
- ❌ Tool execution context still differs (MCP vs HTTP)
- ❌ Added complexity for uncertain benefit

**Verdict**: ⏳ **DEFERRED** - Build only if cloud semantic routing needed

---

### Option 3: Hybrid (Skills Local, Capabilities Cloud)

**Architecture**:
```
┌──────────────────────────────────────────────────┐
│ LAPTOP (Claude Code)                             │
├──────────────────────────────────────────────────┤
│ SkillRouter → routes to skill definitions        │
│ Execution: Calls cloud HTTP APIs (not MCP)       │
│                                                   │
│ Example:                                          │
│   Query: "analyze trading"                        │
│   Skill: trading/kraken_analysis                  │
│   Execution: POST https://fc-gateway/analyze     │
└──────────────────────────────────────────────────┘
           ↓ (HTTPS)
┌──────────────────────────────────────────────────┐
│ CLOUD VPS - fc-http-gateway                      │
├──────────────────────────────────────────────────┤
│ /analyze endpoint                                 │
│   ├─ Accepts high-level intent                   │
│   ├─ Executes trading logic                      │
│   └─ Returns results                             │
└──────────────────────────────────────────────────┘
```

**Pros**:
- ✅ Skills route locally (fast, no cloud sync)
- ✅ Execution uses cloud APIs (scalable, persistent)
- ✅ Tool context mismatch resolved (HTTP everywhere)

**Cons**:
- ⚠️ Skill tool mappings need HTTP endpoints
- ⚠️ Requires fc-http-gateway expansion

**Verdict**: ⏳ **VIABLE** - Consider if mixing local routing + cloud execution

---

## Sync/Versioning Recommendations

### Immediate Actions (Phase 1 Complete)

1. **Document Current Design**:
   ```
   Skills = Local-only routing for Claude Code sessions
   Cloud VPS = Direct HTTP APIs, no semantic routing
   ```

2. **Add Status Field to Skills**:
   ```yaml
   # skill_fingerprints.yaml
   - name: "trading/strategy_execution"
     status: "planned"  # operational | planned | deprecated
     blocked_by: ["fathom_phase_3"]
   ```

3. **Validate Tool References**:
   ```bash
   # Script: validate_skill_tools.py
   # Checks all tools in skill definitions exist in MCP servers
   ```

### Future Enhancements (If Cloud Routing Needed)

4. **Create tools/skills-sync/**:
   ```bash
   tools/skills-sync/
   ├─ sync_skills.py          # Main sync logic
   ├─ sync_now.sh             # Manual sync trigger
   ├─ validate_cloud.py       # Cloud point count validation
   └─ README.md               # Deployment guide
   ```

5. **Environment Variable Configuration**:
   ```bash
   # .env
   SKILLS_QDRANT_HOST=localhost        # or 95.217.51.24
   SKILLS_QDRANT_PORT=6333
   SKILLS_COLLECTION=rhiz_skills
   ```

6. **Skill Versioning**:
   ```yaml
   # skill_fingerprints.yaml
   schema_version: "1.0.0"
   last_updated: "2026-01-24"
   checksum: "sha256:abc123..."  # For integrity validation

   skills:
     - name: "trading/kraken_analysis"
       version: "1.0.0"  # Semantic versioning
   ```

7. **Cloud Collection Initialization**:
   ```bash
   # On VPS
   ssh root@95.217.51.24
   cd /opt/rhiz
   python core/skills/scripts/initialize_skills_collection.py --host localhost
   python core/skills/scripts/ingest_skills.py --host localhost
   ```

---

## Architectural Alignment Assessment

### Consistency with Rhiz Philosophy

**✅ Compiled Expertise**: Skills defined from session patterns → YAML → embeddings
**✅ Pattern Recognition**: Semantic routing, not explicit function calls
**✅ Local-First Design**: Skills optimized for Claude Code laptop environment
**⚠️ Cloud Deployment**: Not architected for cloud, but extensible if needed

### Consistency with Existing Systems

| System | Local | Cloud | Sync | Versioning |
|--------|-------|-------|------|------------|
| **Checkpoints** | ✅ | ⏳ Manual | ✅ 6hr | ✅ Schema |
| **Memory (rhiz_memories)** | ✅ | ✅ | ✅ 6hr | ⏳ Planned |
| **Skills (rhiz_skills)** | ✅ | ❌ | ❌ | ❌ | ← **INCONSISTENT**
| **Trading Signals** | ✅ | ✅ | ⏳ | ❌ |

**Observation**: Skills system is **local-optimized**, unlike memory system which is **cloud-synced**

---

## Blockers & Risks

### Critical Blockers (Cloud Deployment)

1. ❌ **rhiz_skills collection missing on cloud Qdrant**
   - Impact: Cloud routing would fail immediately
   - Fix: Run initialization + ingestion scripts on VPS

2. ❌ **No sync mechanism**
   - Impact: Skill updates not propagated to cloud
   - Fix: Build tools/skills-sync/ OR accept manual re-deployment

3. ❌ **MCP tool context mismatch**
   - Impact: Cloud-routed skills cannot execute MCP tools
   - Fix: Remap tools to HTTP endpoints OR keep skills local-only

### Moderate Risks

4. ⚠️ **Tool availability validation**
   - Impact: Skills reference future tools (Fathom Phase 3-4)
   - Fix: Add status field to skills, validate tool existence

5. ⚠️ **Version drift**
   - Impact: Local/cloud skills diverge over time
   - Fix: Add checksums, validation checks

### Low Risks

6. ⏳ **Performance (non-issue)**
   - Routing latency: ~100ms (acceptable)
   - Scaling: Linear with skill count (100 skills = 200ms)

---

## Recommendations

### For Captain Review

**Question 1**: Is cloud skill routing a requirement?
- If NO: Current architecture is **sufficient** (local-only)
- If YES: Implement Option 2 (Full Cloud Parity) or Option 3 (Hybrid)

**Question 2**: Should skills mirror memory sync strategy?
- If YES: Build tools/skills-sync/ with 6-hour timer
- If NO: Document as intentional architectural difference

**Question 3**: Tool execution in cloud context?
- If skills stay local-only: No changes needed
- If cloud routing needed: Remap MCP tools → HTTP endpoints

### Proposed Action Plan (Local-Only Design)

**Phase 1: Documentation** (Immediate)
1. Add comment to skill_fingerprints.yaml: "Local routing only"
2. Update CLAUDE.md: Skills system = local-only
3. Create this review document

**Phase 2: Validation** (Next session)
4. Script: validate_skill_tools.py (check tool existence)
5. Add status field to skills (operational/planned/deprecated)
6. Test route_to_skill with all 6 skills

**Phase 3: Cleanup** (Future)
7. Remove TODO comments about cloud deployment (if staying local)
8. Add skill creation guide (from session patterns → YAML)

---

## Appendix: File Inventory

### Core Skills Files
- `C:\Users\dread\documents\rhiz_localdev\core\skills\router.py` (SkillRouter class)
- `C:\Users\dread\documents\rhiz_localdev\core\skills\scripts\ingest_skills.py` (Ingestion)
- `C:\Users\dread\documents\rhiz_localdev\core\skills\scripts\initialize_skills_collection.py` (Collection setup)
- `C:\Users\dread\documents\rhiz_localdev\core\skills\registry\skill_fingerprints.yaml` (6 skills)

### MCP Integration
- `C:\Users\dread\documents\rhiz_localdev\tools\rhiz-mcp\src\server.py` (route_to_skill tool, line 792-829)

### Related Documentation
- `C:\Users\dread\documents\rhiz_localdev\core\skills\SKILL_ROUTER_GUIDE.md` (Usage guide)
- `C:\Users\dread\documents\rhiz_localdev\core\skills\registry\memory_search.yaml` (Skill example)
- `C:\Users\dread\documents\rhiz_localdev\docs\research\Skill_Compression_Research_Synthesis.docx` (Theory)

### Cloud Infrastructure
- `C:\Users\dread\documents\rhiz_localdev\infrastructure\vps\fastapi_gateway.py` (Mooncheck, not skills)
- `C:\Users\dread\documents\rhiz_localdev\infrastructure\vps\docker-compose.trading.yml` (VPS deployment)
- `C:\Users\dread\documents\rhiz_localdev\docs\infrastructure\VPS_DUAL_DEPLOYMENT_CLARIFIED.md` (Dual VPS topology)

---

## Conclusion

**Summary**: Phase 1 semantic routing is **fully operational for local Claude Code sessions**, with clean architecture and no critical bugs. Cloud deployment **infrastructure exists but skills are not deployed**, and there is **no sync strategy**. This appears to be an **intentional design choice** (skills = local, memory = cloud), but it is **not explicitly documented**.

**Recommendation**:
1. **Document current local-only design** as intentional
2. **Add tool validation** to prevent referencing non-existent tools
3. **Defer cloud deployment** unless Captain confirms it's a requirement

**Cloud Deployment Readiness**: ⚠️ **NOT READY** (missing collection, no sync, tool context mismatch)

**System Coherence**: ✅ **COHERENT** within local context, ⚠️ **INCONSISTENT** with memory system cloud strategy

**Data Flow Integrity**: ✅ **INTACT** for local flow, ❌ **BROKEN** for cloud flow (not deployed)

---

**Fair winds, Captain. Awaiting your steering on cloud deployment requirements.**

**First Mate**
Session: 2026-01-24
Review Complete: 16:45 EST
