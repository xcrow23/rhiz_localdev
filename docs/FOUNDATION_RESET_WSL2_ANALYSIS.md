# Foundation Reset Plan + WSL2 Handoff Analysis
**Created**: 2026-02-08, Session 82
**Purpose**: Blend WSL2 technical deep dive with Foundation Reset Plan

---

## Executive Summary

The WSL2 handoff document **confirms the Foundation Reset Plan's core direction** while revealing:
1. **Critical configuration details** that prevent MCP failure
2. **Built-in Claude Code features** that may replace custom memory architecture
3. **Mature MCP memory server ecosystem** as alternative to custom checkpoints
4. **Specific bugs and workarounds** for WSL2 + Claude Code

**Key Decision Point**: Do we build custom checkpoint compression, or adopt Claude Code's built-in session memory + MCP memory servers?

---

## Convergence Analysis: What Aligns

### ✅ Native Filesystem Requirement (CONFIRMED)
**Foundation Reset Plan**: Move rhiz_localdev to `~/rhiz_localdev` (NOT `/mnt/c/`)

**WSL2 Handoff**:
> "The official recommendation is unambiguous: keep projects on the native Linux filesystem (`~/projects/`), where `.mcp.json` detection works reliably... Files accessed via `/mnt/c/` suffer up to 20x slower performance."

**Verdict**: Plan is CORRECT. This is non-negotiable.

---

### ✅ Native Docker Engine Preference (CONFIRMED)
**Foundation Reset Plan**: Install Docker natively in WSL2 (not Docker Desktop)

**WSL2 Handoff**:
> "For AI development workflows involving MCP servers and vector databases, native Docker is the stronger choice. The direct networking simplifies container-to-host communication — critical when Qdrant needs to be reachable from Claude Code and MCP servers."

**Verdict**: Plan is CORRECT. Zero licensing, lighter footprint, transparent networking.

---

### ✅ MCP Failures Are Fixable (CONFIRMED)
**Foundation Reset Plan**: Previous MCP failure likely due to Windows filesystem access

**WSL2 Handoff**:
> "MCP server failures on WSL2 stem primarily from stdio pipe bugs in Claude Code itself, path translation issues when working from `/mnt/c/`, and NAT networking isolation — not from fundamental architectural incompatibility."

**Verdict**: Plan is CORRECT. Not architectural issue, specific config problems.

---

### ✅ Environment Parity Benefits (CONFIRMED)
**Foundation Reset Plan**: WSL2 eliminates Windows/Linux translation friction

**WSL2 Handoff**:
> "Claude Code in WSL2... tool compatibility is effectively 100% versus roughly 70% on native Windows."

**Verdict**: Large qualitative advantage confirmed.

---

## Critical Additions: What the Plan Missed

### 🚨 CRITICAL 1: Claude Code Version Bugs

**WSL2 Handoff**:
> "A widely-reported bug in v1.0.43 (July 2025) caused Claude Code to successfully start MCP servers but fail to expose their tools... A separate bug in v1.0.57 caused Claude Code to hang on startup entirely on WSL2/Ubuntu with NVM."

**Action Required**: Add version check to Phase 2 plan.

```bash
# In WSL2 after installing Claude Code
claude --version
# Avoid v1.0.43, v1.0.57 if possible
# Use latest stable (check release notes for WSL2 compatibility)
```

---

### 🚨 CRITICAL 2: Python stdout Hazard

**WSL2 Handoff**:
> "Any package that prints to stdout (such as `python-dotenv` v17+ emitting load messages) corrupts the JSON-RPC stream and causes immediate failure... The fix is strict — all server logging must go to stderr, never stdout."

**Action Required**: Audit rhiz-mcp and memory-mcp for stdout prints.

```bash
# Check MCP server code for stdout usage
cd ~/rhiz_localdev/tools/rhiz-mcp
grep -r "print(" src/
grep -r "sys.stdout" src/

# If python-dotenv is used, pin to v16.x or configure to silent mode
pip install "python-dotenv<17.0.0"
```

**Risk**: This could be the ACTUAL cause of "complete MCP failure" in previous WSL2 trial.

---

### 🚨 CRITICAL 3: WSL2 Networking Configuration

**WSL2 Handoff**:
> "Enable mirrored networking in `.wslconfig`"

**Action Required**: Create/update `.wslconfig` in Windows user directory.

**File**: `C:\Users\dread\.wslconfig`
```ini
[wsl2]
# Mirrored networking (Windows 11 22H2+)
networkingMode = mirrored

# Memory limits (adjust based on laptop RAM)
memory = 8GB
autoMemoryReclaim = gradual

# DNS tunneling (fixes corporate VPN issues)
dnsTunneling = true
```

**After creating**: `wsl --shutdown` and restart WSL2 to apply.

---

### 🚨 CRITICAL 4: Claude in Chrome Crash

**WSL2 Handoff**:
> "The 'Claude in Chrome' feature, when enabled on the Windows side, causes Claude Code to crash on WSL2 startup — the workaround is `claude --no-chrome`."

**Action Required**: Always launch with `--no-chrome` flag in WSL2.

```bash
# Add alias to ~/.bashrc
echo "alias claude='claude --no-chrome'" >> ~/.bashrc
source ~/.bashrc
```

---

### 🚨 CRITICAL 5: Qdrant Version Pinning

**WSL2 Handoff**:
> "Snapshots can only be restored to instances running the **same Qdrant minor version**."

**Action Required**: Match Qdrant versions between local WSL2 and VPS.

```bash
# Check VPS Qdrant version
ssh root@72.62.81.128 "docker exec qdrant curl -s http://localhost:6333/collections | jq -r '.version'"
# Example output: 1.7.4

# Install SAME version in WSL2
docker run -d \
  --name qdrant_local \
  -p 6333:6333 \
  -v ~/qdrant_storage:/qdrant/storage \
  qdrant/qdrant:v1.7.4  # MUST MATCH VPS
```

**Sync Strategy**: Use Python `migrate()` function (easier than snapshots)

```python
from qdrant_client import QdrantClient
from qdrant_client.migrate import migrate

source = QdrantClient(url="http://localhost:6333")  # WSL2
dest = QdrantClient(url="http://72.62.81.128:6333", api_key="key")  # VPS
migrate(source, dest, collection_names=["rhiz_memories"],
        recreate_on_collision=True, batch_size=100)
```

---

## Game-Changer: Claude Code Built-In Memory

### What the WSL2 Handoff Reveals

**WSL2 Handoff**:
> "Claude Code's built-in memory system... implements a 4-tier hierarchy: enterprise policy, project memory (`CLAUDE.md`), project rules (`.claude/rules/`), and user memory (`~/.claude/CLAUDE.md`). The newer **Session Memory feature** automatically extracts summaries — first after ~10,000 tokens, then every ~5,000 tokens or 3 tool calls — storing them as markdown at `~/.claude/session-memory/`. New sessions receive relevant past summaries automatically. The `/compact` command summarizes the current conversation and starts fresh with that summary preloaded."

**This Changes Everything About Memory Architecture.**

---

### Current Foundation Reset Plan (Custom Checkpoints)

**Proposed**:
- Content-based checkpoint triggers (manual or semi-automated)
- YAML checkpoint files (50-100 lines)
- Load 3 checkpoints max per session
- Custom compression logic

**Problems**:
1. Reinventing what Claude Code now does natively
2. Maintenance burden (Captain writes checkpoints manually)
3. Doesn't leverage built-in `/compact` command
4. No automatic summarization (requires manual effort)

---

### Alternative: Leverage Built-In Session Memory

**Use Claude Code's native features**:

1. **Session Memory** (automatic)
   - Extracts summaries every ~5k tokens or 3 tool calls
   - Stored at `~/.claude/session-memory/`
   - Auto-loaded into new sessions
   - **Zero manual effort**

2. **`/compact` command** (on-demand)
   - Summarizes current conversation
   - Starts fresh with summary preloaded
   - **Replaces manual checkpoint creation**

3. **CLAUDE.md** (project memory)
   - Static knowledge (principles, architecture, current state)
   - Compressed to 800-1200 lines (as planned)

4. **MCP Memory Server** (structured memory)
   - Use existing `@modelcontextprotocol/server-memory` OR
   - Memento MCP (Neo4j + semantic retrieval) OR
   - mcp-memory-service (knowledge graph + cloud sync)

**Benefits**:
- ✅ **Automatic** (no manual checkpoint writing)
- ✅ **Built-in** (leverages Claude Code features)
- ✅ **Incremental** (rolling summary, not full re-summarization)
- ✅ **Mature ecosystem** (MCP memory servers actively maintained)

---

### Hybrid Approach (RECOMMENDED)

**Blend built-in + minimal custom**:

1. **Working Memory** (automatic)
   - Use Claude Code Session Memory
   - Auto-summarization every ~5k tokens
   - `/compact` when session gets unwieldy

2. **Semantic Memory** (compressed)
   - CLAUDE.md (800-1200 lines, static knowledge)
   - CURRENT_STATE.md (50-100 lines, operational status)
   - Updated only on major pivots (quarterly forced sync)

3. **Episodic Memory** (structured)
   - MCP memory server (choose one):
     - **Option A**: Use official `@modelcontextprotocol/server-memory` (JSONL knowledge graph)
     - **Option B**: Use Memento MCP (Neo4j backend, semantic retrieval)
     - **Option C**: Use existing memory-mcp (Qdrant-based, already built)
   - Store critical decisions, architectural changes, integration milestones
   - Query via MCP tools when needed

4. **Archival Memory** (deep storage)
   - Keep checkpoint files in `Rhiz_Archives/` as written narrative
   - NOT loaded into sessions (librarian work only)
   - Preserves journey history without burdening active context

**This approach**:
- Uses Claude Code's built-in automation
- Minimizes manual checkpoint writing
- Preserves important memories in structured form
- Archives full history without loading it all

---

## Revised Memory Architecture Decision

### Option A: Custom Checkpoints (Original Plan)
**Pros**: Full control, custom format, content-based triggers
**Cons**: Reinvents Claude Code features, manual effort, maintenance burden

### Option B: Built-In Only (Pure Claude Code)
**Pros**: Zero manual work, automatic, mature
**Cons**: Less control, may not capture specific Rhiz patterns

### Option C: Hybrid (RECOMMENDED)
**Pros**: Best of both worlds, leverages automation, preserves critical memories
**Cons**: Slightly more complex architecture

**Captain's Call Needed**: Which memory architecture?

---

## Factory.ai Incremental Compression Pattern

**WSL2 Handoff**:
> "Factory.ai's incremental compression approach... maintain a **persistent rolling summary** and only summarize newly-dropped spans, merging them into the existing summary. This keeps compression cost constant per event. Their framework preserves four critical categories: session intent, high-level play-by-play, artifact trail, breadcrumbs."

**Rhiz Application**:
Instead of creating new checkpoint each session, maintain ONE rolling summary:

**File**: `ROLLING_SUMMARY.md`
```markdown
# Rhiz Rolling Summary
**Last Updated**: 2026-02-08

## Session Intent (Current Goals)
- Complete foundation reset (archival, memory redesign, WSL2 migration)
- Restore "elixir-like hydration" to memory system
- Eliminate Windows/Linux translation friction

## High-Level Play-by-Play (Recent Actions)
- Session 82: Analyzed WSL2 handoff, designed foundation reset plan
- Session 74: Completed Phase 1 Documentation Unification
- Session 72: Completed Phase 2 Memory-Augmented Activation (93.3% routing accuracy)
- Session 42: Deployed Intelligence Federation (8-hour marathon)

## Artifact Trail (Key Files Modified)
- RHIZ_FOUNDATION_RESET_PLAN.md (created)
- CLAUDE.md (to be compressed 3000 → 800 lines)
- CURRENT_STATE.md (to be created)

## Breadcrumbs (Important Locations)
- VPS trading stack: /opt/rhiz_trading
- MCP servers: tools/rhiz-mcp, tools/memory-mcp
- Skills: core/skills/registry/ (6 skills, dormant)
```

**Update Strategy**:
- After each session, append NEW developments only
- Use `/compact` to compress when file grows >500 lines
- Result: Single evolving document, not 39+ checkpoints

---

## Focus Architecture (Agent-Directed Checkpointing)

**WSL2 Handoff**:
> "The Focus architecture (arXiv, January 2026): agents declare investigation boundaries with `start_focus`/`complete_focus` primitives, compress completed explorations into high-level learnings, and delete raw logs. This achieved **18–57% token savings**."

**Rhiz Application**:
MCP tool for focus boundaries:

```python
# In rhiz-mcp
@mcp_tool()
def start_focus(focus_name: str, objective: str):
    """Declare start of focused investigation"""
    # Log start time, objective
    # Begin capturing actions in temporary buffer

@mcp_tool()
def complete_focus(focus_name: str, learnings: list[str]):
    """Complete focus, compress to learnings"""
    # Compress temporary buffer to high-level learnings
    # Delete detailed logs
    # Store compressed result in ROLLING_SUMMARY.md
```

**Usage**:
```
User: "Investigate why MCP failed in previous WSL2 trial"

AI: Starting focused investigation...
[calls start_focus("mcp_wsl2_failure", "Root cause analysis of previous MCP failure")]

... investigation work ...

AI: Completing investigation with learnings:
[calls complete_focus("mcp_wsl2_failure", [
  "Python stdout from python-dotenv corrupts JSON-RPC stream",
  "Windows filesystem /mnt/c/ causes .mcp.json detection failures",
  "Claude Code v1.0.43/v1.0.57 had WSL2-specific bugs"
])]
```

**Result**: Detailed exploration NOT permanently stored, only compressed learnings.

---

## Revised Phase 2 Plan: WSL2 Migration (With New Intelligence)

### Updated Checklist

- [ ] **2.0 Pre-Migration Setup** (15 min) — **NEW**
  - [ ] Create `.wslconfig` in `C:\Users\dread\` with mirrored networking
  - [ ] Run `wsl --shutdown` and restart WSL2
  - [ ] Check VPS Qdrant version: `ssh root@72.62.81.128 "docker exec qdrant curl -s http://localhost:6333/collections | jq -r '.version'"`
  - [ ] Note version for local installation

- [ ] **2.1 Verify WSL2** (5 min) — unchanged
  - [ ] Run `wsl --list --verbose`
  - [ ] Confirm Ubuntu VERSION 2

- [ ] **2.2 Move rhiz_localdev to WSL2 Native** (15 min) — unchanged
  - [ ] Clone fresh to `~/rhiz_localdev` (NOT `/mnt/c/...`)
  - [ ] Copy `.env` and `.mcp.json` only

- [ ] **2.3 Install Claude Code (Linux)** (10 min) — **UPDATED**
  - [ ] Run: `curl -fsSL https://claude.ai/install.sh | bash`
  - [ ] Check version: `claude --version` (avoid v1.0.43, v1.0.57)
  - [ ] Add alias: `echo "alias claude='claude --no-chrome'" >> ~/.bashrc`
  - [ ] Test: `claude --no-chrome` (should start without crash)

- [ ] **2.4 Install Docker Native** (15 min) — unchanged

- [ ] **2.5 Set Up Qdrant** (10 min) — **UPDATED**
  - [ ] Use SAME version as VPS (checked in step 2.0)
  - [ ] Start container: `docker run -d --name qdrant_local -p 6333:6333 -v ~/qdrant_storage:/qdrant/storage qdrant/qdrant:vX.X.X`
  - [ ] Test: `curl http://localhost:6333/collections`

- [ ] **2.6 Install MCP Servers** (45 min) — **UPDATED**
  - [ ] Install Python 3 + venv
  - [ ] **Audit for stdout prints**: `grep -r "print(" tools/*/src/`
  - [ ] **Check python-dotenv version**: If present, pin to <17.0.0
  - [ ] Create venv for rhiz-mcp
  - [ ] Create venv for memory-mcp
  - [ ] Update `.mcp.json` with WSL2 native paths
  - [ ] **Add MCP_TIMEOUT env var** if needed: `export MCP_TIMEOUT=60000`

- [ ] **2.7 Test Claude Code + MCP** (30 min) — **UPDATED**
  - [ ] Start: `claude --no-chrome`
  - [ ] Test `/mcp list` (should show rhiz-mcp, memory-mcp)
  - [ ] Test `get_dyad_state` (should return state, NOT timeout)
  - [ ] Test memory search
  - [ ] **Test `/compact`** (Claude Code built-in compression)
  - [ ] Check session memory: `ls ~/.claude/session-memory/`

- [ ] **2.8 Test VPS SSH + Qdrant Sync** (20 min) — **UPDATED**
  - [ ] SSH from WSL2 to VPS
  - [ ] Test Docker commands
  - [ ] **Test Python migrate()**: Sync test collection from local to VPS
  - [ ] Verify sync worked on VPS Qdrant

**Total Phase 2 Time**: 3.5-4.5 hours (slightly longer due to new checks)

---

## What Gets Rejected from Original Plan

### ❌ REJECT: Heavy Custom Checkpoint System
**Original Plan**: Content-based checkpoint triggers, YAML files, 3 checkpoint max load, custom compression

**Why Reject**: Claude Code's built-in session memory + `/compact` does this better, with zero manual effort.

**Replace With**: Hybrid approach (built-in + MCP memory server + rolling summary)

---

### ❌ REJECT: Vector Search Across All Checkpoints
**Original Plan**: Already rejected this (good)

**WSL2 Handoff Confirms**:
> "Factory.ai's incremental compression... maintain a persistent rolling summary and only summarize newly-dropped spans"

**Keep**: Limited episodic memory via MCP memory server for structured queries

---

### ❌ REJECT: Time-Based Checkpoint Triggers
**Original Plan**: Already rejected this (Captain noted "temporal is your kryptonite")

**WSL2 Handoff Confirms**: Focus architecture uses investigation boundaries, NOT time

**Replace With**: Agent-directed focus boundaries (`start_focus`/`complete_focus`)

---

## What Gets Kept from Original Plan

### ✅ KEEP: Aggressive Archival (Phase 1)
**Status**: Unchanged, still critical

**Action**: Move 8-10 GB to `Rhiz_Archives/`, preserve but don't load

---

### ✅ KEEP: CLAUDE.md Compression
**Status**: Unchanged, still needed

**Action**: Compress 3000 → 800-1200 lines, arrows not paragraphs

---

### ✅ KEEP: CURRENT_STATE.md
**Status**: Unchanged, operational reference

**Action**: Create 50-100 line file for fast operational status

---

### ✅ KEEP: WSL2 Migration (Phase 2)
**Status**: Enhanced with new technical details

**Action**: Follow updated Phase 2 checklist with `.wslconfig`, version checks, stdout audits

---

### ✅ KEEP: Cloud Deployment Script (Phase 3)
**Status**: Unchanged, still needed

**Action**: One-command deploy with health checks and rollback

---

## Decision Matrix: Memory Architecture Options

| Feature | Custom Checkpoints | Built-In Only | Hybrid (Recommended) |
|---------|-------------------|---------------|---------------------|
| Manual effort | High | Zero | Low |
| Automation | Limited | Full | Mostly automated |
| Customization | Full | Limited | Moderate |
| Maintenance burden | High | Zero | Low |
| Rhiz-specific patterns | Yes | No | Yes (via MCP) |
| Leverages Claude Code features | No | Yes | Yes |
| Preserves journey history | Yes | Limited | Yes (archives) |
| Token efficiency | Moderate | High | High |
| Learning curve | Low | Minimal | Moderate |
| **Recommended** | ❌ | ⚠️ | ✅ |

---

## Recommended Path Forward

### Phase 1: Documentation Reset (Tonight, 2-3 hours)
**UNCHANGED** from original plan:
1. Aggressive archival (8-10 GB)
2. Compress CLAUDE.md (3000 → 800 lines)
3. Create CURRENT_STATE.md (50-100 lines)
4. Test hydration

**ADD TO PHASE 1**:
5. Create ROLLING_SUMMARY.md (initial state, ~200 lines)
6. Move all 39 checkpoints to archive (preserve but don't load)

---

### Phase 2: WSL2 Migration (Tomorrow, 3.5-4.5 hours)
**ENHANCED** with WSL2 handoff intelligence:
1. Create `.wslconfig` with mirrored networking
2. Check VPS Qdrant version (for version pinning)
3. Install Claude Code (avoid buggy versions)
4. **Audit MCP servers for stdout prints** (critical!)
5. Test built-in `/compact` command
6. Test Python `migrate()` for Qdrant sync

---

### Phase 3: Memory System Finalization (Day 3, 2-3 hours)
**NEW PHASE** (split from Phase 3):
1. Choose MCP memory server:
   - Option A: Use existing memory-mcp (already built)
   - Option B: Add Memento MCP (Neo4j + semantic retrieval)
   - Option C: Add official `@modelcontextprotocol/server-memory`
2. Implement `start_focus`/`complete_focus` tools in rhiz-mcp
3. Test rolling summary workflow
4. Migrate critical memories from old checkpoints to MCP memory server

---

### Phase 4: Cloud Deployment Model (Day 4, 2-3 hours)
**UNCHANGED** from original Phase 3:
1. Create `deploy_to_vps.sh` script
2. Test deployment
3. Expand signal capture (trading_signals, sil_patterns, fc_decisions)

---

## Questions for Captain

### Q1: Memory Architecture Choice
Which approach for memory system?
- **Option A**: Custom checkpoints (original plan, full control but manual)
- **Option B**: Built-in only (zero effort but less customization)
- **Option C**: Hybrid (recommended - automated + structured memories via MCP)

### Q2: MCP Memory Server
If choosing hybrid, which MCP memory server?
- **Option A**: Existing memory-mcp (already built, Qdrant-based)
- **Option B**: Memento MCP (Neo4j, more sophisticated)
- **Option C**: Official `@modelcontextprotocol/server-memory` (JSONL, simple)

### Q3: Checkpoint Migration
What to do with existing 39 checkpoints?
- **Option A**: Archive and don't migrate (fresh start)
- **Option B**: Extract key learnings into MCP memory server (preserve critical knowledge)
- **Option C**: Keep as-is in archive for librarian sessions

### Q4: Phase 1 Execution
Ready to start Phase 1 tonight (archival + compression)?
- **Yes**: Proceed with original Phase 1 + add ROLLING_SUMMARY.md
- **No**: Want Opus 4.6 review first

### Q5: Focus Architecture
Implement `start_focus`/`complete_focus` MCP tools?
- **Yes**: Add to rhiz-mcp (enables agent-directed checkpointing)
- **No**: Defer to post-hibernation (not urgent)

---

## Summary: What This Analysis Changes

### CONFIRMS ✅
- Native filesystem requirement (`~/rhiz_localdev`)
- Native Docker Engine preference
- WSL2 environment parity benefits
- Aggressive archival strategy
- CLAUDE.md compression
- One-command cloud deployment

### ENHANCES 🔧
- Phase 2 WSL2 migration (adds critical config steps)
- Qdrant sync strategy (Python `migrate()` function)
- MCP debugging (stdout hazard, version bugs)

### REPLACES 🔄
- Custom checkpoint system → Hybrid (built-in + MCP memory server)
- Manual checkpoint writing → `/compact` + rolling summary
- Vector search → MCP memory server structured queries

### ADDS ➕
- `.wslconfig` configuration
- Claude Code version checking
- Python stdout audit
- Session memory exploration
- Focus architecture primitives
- Factory.ai incremental compression pattern

---

**Next Step**: Captain decides on memory architecture (Q1-Q5), then we execute Phase 1 tonight.
