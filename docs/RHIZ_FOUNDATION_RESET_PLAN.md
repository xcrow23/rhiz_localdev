# Rhiz Foundation Reset - Implementation Plan
**Created**: 2026-02-08
**Session**: 82
**Status**: Ready for execution
**Estimated Total Time**: 8-12 hours across 3 phases

---

## Executive Summary

This plan addresses three converging issues in the Rhiz project:
1. **Memory system** has become "crippling prosthesis" instead of "elixir-like hydration"
2. **Documentation debt** creating "misdirection" through volume and complexity
3. **Environment misalignment** between Windows PowerShell (local) and Ubuntu (VPS)

The solution: **Phased reconstruction** applying compressed expertise principles, aggressive archival, and WSL2 environment parity.

---

## Design Principles (from Compressed Expertise Architecture)

### 1. **Chunking & Compilation Over Exhaustive Retrieval**
- Expertise becomes automatic through compressed patterns
- Don't store every detail - compile reliable patterns into reusable forms
- "Much of the ethereal in-between states should stay in session, not enshrined in checkpoints"

### 2. **Multi-Layer Memory Architecture**
- **Working Memory**: Current session (CURRENT_STATE.md + active checkpoint only)
- **Episodic Memory**: Limited checkpoint set by relevance + proximity (NOT full search)
- **Semantic Memory**: CLAUDE.md (principles, patterns, decisions - compressed)
- **Procedural Memory**: Skills (dormant but preserved for post-hibernation)

### 3. **Content-Based Compression, Not Temporal**
- Checkpoints created when **significant state change** occurs, not time intervals
- Temporal reasoning avoided (noted as "your kryptonite")
- Relevance + proximity determine what loads, not recency alone

### 4. **Arrows, Straight Shots, Compression**
- Direct, model-accessible documentation
- No verbose in-between states in permanent storage
- "Only components of the ship and necessary storage"

### 5. **Just-In-Time Knowledge Delivery**
- Information precisely when needed, not dumped all at once
- New session loads minimal context, expands on-demand
- Cognitive load minimized for both human and AI

---

## Phase 1: Documentation & Memory Reset (Tonight, 2-3 hours)

### Objective
Shed accumulated debt, restore clean mental model, implement compressed expertise architecture.

### 1.1 Aggressive Archival (45 min)

**Archive Structure** (create once, reuse forever):
```
C:\Users\dread\Documents\
├─ Rhiz_LocalDev\               # Active working directory
│   ├─ core/                     # Ship components (keep)
│   ├─ domains/                  # Ship components (keep)
│   ├─ infrastructure/           # Ship components (keep)
│   ├─ tools/                    # Ship components (keep)
│   ├─ docs/                     # Minimal current docs (keep)
│   └─ [slim configs]            # .mcp.json, .env, etc
│
└─ Rhiz_Archives\               # Deep storage (no deletions)
    ├─ archive_20260208_foundation_reset/
    │   ├─ external/             # Reference repos
    │   ├─ Gifts_From_Alex/      # Captain's gift content
    │   ├─ Claude_Grooves/       # Music project (separate scope)
    │   ├─ old_experiments/      # Deprecated attempts
    │   ├─ verbose_docs/         # Old architecture docs
    │   ├─ old_checkpoints/      # All 39 current checkpoints
    │   └─ deprecated_configs/   # Old .env variants, etc
```

**What Gets Archived** (move, don't delete):
- `external/` - All reference repos (LocalAI, claude-experimental, etc) - 2-3 GB
- `Gifts_From_Alex/` - Gift content (not current project work) - ~1 GB
- `Claude_Grooves/` - Parallel music project - ~500 MB
- `docs/architecture/` OLD files - Keep only last 5 major docs
- `docs/sessions/` - Move all except Session 72-74 syntheses
- `core/memory/checkpoints/` - Move all 39, replace with new system
- All but ONE `.env` file (keep `.env.production` only)
- Deprecated `docker-compose` variants (keep only `docker-compose.trading.yml`)
- Old Python venvs in tools/ (will rebuild in WSL2)

**Archival Commands**:
```bash
# Create archive root
mkdir C:\Users\dread\Documents\Rhiz_Archives
mkdir C:\Users\dread\Documents\Rhiz_Archives\archive_20260208_foundation_reset

# Move large directories
cd C:\Users\dread\Documents\Rhiz_LocalDev
move external ..\Rhiz_Archives\archive_20260208_foundation_reset\
move Gifts_From_Alex ..\Rhiz_Archives\archive_20260208_foundation_reset\
move Claude_Grooves ..\Rhiz_Archives\archive_20260208_foundation_reset\

# Archive old docs (selective)
cd docs
mkdir ..\..\Rhiz_Archives\archive_20260208_foundation_reset\verbose_docs
move architecture\PHASE_*.md ..\..\Rhiz_Archives\archive_20260208_foundation_reset\verbose_docs\
move sessions\session_*.md ..\..\Rhiz_Archives\archive_20260208_foundation_reset\verbose_docs\
# Keep only Session 72, 73, 74 synthesis docs

# Archive all checkpoints
cd ..\core\memory
move checkpoints ..\..\..\..\Rhiz_Archives\archive_20260208_foundation_reset\old_checkpoints
mkdir checkpoints  # Fresh start
```

**Expected Space Freed**: ~8-10 GB locally

---

### 1.2 New Memory Architecture (60 min)

**Core Principle**: Content-based compression, not exhaustive search.

#### Working Memory (Always Loaded)
Single file: `CURRENT_STATE.md` (50-100 lines max)

**Template**:
```markdown
# Rhiz Current State
**Updated**: 2026-02-08
**Health**: Hibernation Mode (Observation State)
**Session**: 82

## What's Running (VPS)
- Fathom MCP (Phase 1/6 - Account + Market Data)
- Fathom Commander (27 tools, paper mode)
- FC HTTP Gateway (port 8767, authenticated)
- SIL FastAPI (B+ grade, operational)
- Qdrant (moonchecks collection growing)
- 5 Cloudflare Workers (health, DCA paused, webhooks)

## What Works
- VPS trading stack (operational, signals collecting)
- Local Claude Code + MCP (rhiz-mcp, memory-mcp)
- Checkpoint system (schema v1.1.0)
- Skills routing (93.3% accuracy, dormant during hibernation)

## What's Broken/Pending
- Fathom Phase 2-6 (trading execution not implemented)
- Skill-tool binding framework (design deferred)
- n8n → Workers migration (9 workflows pending)
- FC integration with SIL (not connected)

## What's Hibernating
- Active development (Captain securing family housing + funding)
- Trading execution (DCA offline, no new orders)
- Skills activation (semantic routing paused)

## Next on Resumption
1. Load this file + latest checkpoint
2. Verify Qdrant health (local + cloud)
3. Review VPS signal collection during hibernation
4. Resume Phase 2 Component Integration
```

---

#### Episodic Memory (Limited Checkpoint Set)

**New Checkpoint Strategy**:
- **NOT** time-based intervals
- **NOT** vector search across all checkpoints
- **YES** content-based compression
- **YES** limited set by relevance + proximity

**Checkpoint Triggers** (create new checkpoint when):
1. Major architectural pivot (infrastructure change, new system deployed)
2. Phase completion (Wave complete, milestone reached)
3. Significant learning (new pattern discovered, approach validated/rejected)
4. Hibernation boundaries (entering/exiting observation mode)
5. Integration between systems (first time A successfully talks to B)

**Loading Strategy**:
```python
def load_checkpoint_context():
    """Load minimal relevant checkpoint set, not full history"""
    checkpoints_to_load = [
        "latest_checkpoint.yaml",           # Always load (proximity)
        "hibernation_entry.yaml",           # Resumption context
        "last_major_milestone.yaml",        # Architectural reference
        # MAX 3 checkpoints loaded per session
    ]
    # Do NOT vector search across all 39 checkpoints
    # Do NOT load full history
    # Only load what's directly relevant to current work
```

**Checkpoint Content** (compressed, 50-100 lines):
```yaml
checkpoint:
  session_topic: "Short phrase (5-10 words)"

  what_changed:
    - "Deployed FC HTTP Gateway with authentication"
    - "Fixed Traefik routing (dual network pattern)"
    - "Enforced paper mode (was live trading)"

  key_decisions:
    - decision: "Use paper mode default"
      rationale: "Safety over speed"
      alternatives_rejected: ["live mode with approval workflow"]

  outcomes:
    - "VPS operational at https://fathom.dreamthewilderness.com"
    - "9 n8n workflows active"
    - "$50.68 BTC portfolio from 2 test trades"

  next_immediate:
    - "Monitor 48-hour verification"
    - "Begin Phase 3 integration"

  open_questions:
    - "Should DCA run before manual FC gateway test?"

# NO verbose session_arc narratives
# NO 300-line developmental stories
# Arrows, straight shots, compressions only
```

---

#### Semantic Memory (CLAUDE.md Compression)

**Current Issue**: CLAUDE.md is 3000+ lines, too verbose.

**Compression Target**: 800-1200 lines, structured for fast scanning.

**New Structure**:
```markdown
# CLAUDE.md

## Project Identity (50 lines)
- What Rhiz is (human-AI symbiotic dev)
- Core philosophy (symbiosis over hierarchy)
- Goals (12-month, 24-month horizons)

## Architecture Map (100 lines)
- Directory structure (concise tree)
- Key components (what, not why)
- Data flows (arrows, not paragraphs)

## Hardware Context (50 lines)
- Local: Dell Inspiron specs
- Cloud: Hostinger VPS specs
- Constraints: Budget-limited

## Active Systems (150 lines)
### Trading Stack
- Fathom (Phase 1/6, 8 tools, status)
- FC (27 tools, paper mode, status)
- SIL (B+ grade, status)

### Memory System
- Checkpoints (content-based, 3 max load)
- Qdrant (localhost:6333, collections)
- MCP servers (rhiz-mcp, memory-mcp)

### Skills System
- 6 skills defined
- 93.3% routing accuracy
- Dormant during hibernation

## Deployment Model (100 lines)
- Local dev (WSL2 primary after Phase 2)
- Cloud production (VPS containers)
- Deploy workflow (one-command script)

## Working Agreements (100 lines)
- Decisions logged with reasoning
- Failures documented thoroughly
- Captain handles teleology + physical execution
- AI handles logic + computational execution

## Relational Principles (150 lines)
- Epistemic honesty
- Persistence architecture
- Co-responding vs transactional
- Long-term vision

## Current State (100 lines)
- What's running, what works, what's broken
- Recent milestones (last 3-5 major)
- Known gaps
- Hibernation status

## Forced Sync Protocol (50 lines)
- Quarterly updates (~15-20 sessions)
- After major pivots
- Version increments
```

**Total**: ~850 lines (vs current 3000+)

**Archival of removed content**: Old CLAUDE.md → `Rhiz_Archives/archive_20260208_foundation_reset/CLAUDE.md.verbose`

---

#### Procedural Memory (Skills - Already Exists)

**Status**: Dormant during hibernation, preserved for resumption.

**Action**: None needed now. Post-hibernation, skills resume with memory augmentation.

---

### 1.3 Create Minimal Documentation Set (45 min)

**Keep These Files** (model-accessible, compressed):
1. **CLAUDE.md** - Rewritten to 800-1200 lines (compress tonight)
2. **CURRENT_STATE.md** - Created tonight (50-100 lines)
3. **QUICKSTART.md** - 5-minute onboarding (already exists, verify accuracy)
4. **Latest checkpoint** - `session_82_foundation_reset.yaml` (created tonight)
5. **HIBERNATION_STATE.md** - Keep (resumption reference)
6. **HIBERNATION_RESTORE.md** - Keep (operational procedure)

**Archive These** (move to `Rhiz_Archives/archive_20260208_foundation_reset/verbose_docs/`):
- All `docs/architecture/PHASE_*.md` (except last 2)
- All `docs/sessions/session_*.md` (except 72-74 syntheses)
- Old architecture decision docs (pre-Session 42)
- Journey logs (historical narrative, not operational reference)
- Research syntheses (compress key insights into CLAUDE.md)

**Delete Nothing** - Archives preserved for librarian sessions.

---

### 1.4 Test Hydration (30 min)

**Success Criteria**: New Claude instance understands project in <5 minutes.

**Test Protocol**:
1. Open fresh Claude Desktop session (Opus 4.6)
2. Load ONLY:
   - CURRENT_STATE.md
   - Latest checkpoint (session_82_foundation_reset.yaml)
   - CLAUDE.md (compressed version)
3. Ask: "What is Rhiz? What's currently running? What should I work on next?"
4. Evaluate response:
   - ✅ Accurate understanding of architecture
   - ✅ Knows what's operational vs hibernating
   - ✅ Identifies next steps correctly
   - ❌ Grasps for details (needs more context)
   - ❌ Misrepresents current state (doc out of sync)

**If test fails**: Iterate on compression until hydration succeeds.

---

## Phase 2: WSL2 Environment Migration (Tomorrow, 3-4 hours)

### Objective
Establish Ubuntu environment parity between local (WSL2) and cloud (VPS), enabling frictionless dev→production workflow.

### 2.1 WSL2 Qualitative Advantages (Why This Matters)

**Problem**: Windows PowerShell → Ubuntu VPS translation is painful.
- Different command syntax (PowerShell cmdlets vs bash utilities)
- Path separators (`\` vs `/`)
- Docker behavior differences (Docker Desktop vs native Linux)
- Scripts fail when ported
- "Something has been a bit off"

**Solution**: WSL2 provides native Ubuntu environment on Windows laptop.

**Advantages**:

1. **Perfect Environment Parity**
   - Same bash commands locally and on VPS
   - Same Docker behavior (Linux containers natively)
   - Scripts run identically in both environments
   - No translation layer, no surprises

2. **MCP Server Compatibility**
   - Previous WSL2 trial had "complete MCP failure"
   - Root cause likely: Windows filesystem mounted in WSL2 (`/mnt/c/...`)
   - Solution: Move rhiz_localdev to WSL2 native filesystem (`~/rhiz_localdev`)
   - Native Python environment, native file permissions
   - Qdrant connection via localhost works correctly

3. **Faster Docker Performance**
   - Docker Desktop on Windows adds virtualization overhead
   - Native Linux Docker in WSL2 is faster
   - Volume mounts perform better (no filesystem translation)

4. **Cleaner Development Experience**
   - One environment to learn (Ubuntu bash)
   - AI operates in same environment as VPS (no context switching)
   - SSH, tmux, vim/nano all native
   - Git, Python, Node all Linux-native versions

5. **Reversible**
   - Keep Windows PowerShell setup archived
   - Can switch back if WSL2 doesn't work
   - Low risk, high potential reward

**Captain's Question Answered**: YES, large qualitative advantages. WSL2 eliminates environment translation friction entirely.

---

### 2.2 WSL2 Migration Steps

#### Step 1: Verify WSL2 Installation (5 min)
```powershell
# In PowerShell
wsl --list --verbose
# Should show Ubuntu distribution with VERSION 2
```

If not WSL2, upgrade:
```powershell
wsl --set-version Ubuntu 2
```

---

#### Step 2: Move rhiz_localdev to WSL2 Native Filesystem (15 min)

**Critical**: Do NOT use `/mnt/c/...` - this was previous MCP failure cause.

```bash
# In WSL2 Ubuntu terminal
cd ~
git clone <rhiz_repo_url> ~/rhiz_localdev
# Now at /home/dread/rhiz_localdev (native Linux filesystem)
```

**Copy essential configs** (not entire Windows directory):
```bash
# From Windows to WSL2 (selective copy)
cp /mnt/c/Users/dread/Documents/Rhiz_LocalDev/.env ~/rhiz_localdev/.env
cp /mnt/c/Users/dread/Documents/Rhiz_LocalDev/.mcp.json ~/rhiz_localdev/.mcp.json
# Copy ONLY current operational files, not archives
```

---

#### Step 3: Install Claude Code (Linux Build) (10 min)

**Previous issue**: Likely Windows build invoked from WSL2, causing PowerShell command confusion.

**Solution**: Install Linux native build.

```bash
# In WSL2 Ubuntu terminal
curl -fsSL https://install.claude.ai | sh
# This installs Linux x86_64 build

# Verify installation
which claude
# Should show: /home/dread/.local/bin/claude (or similar Linux path)

claude --version
```

---

#### Step 4: Install Docker (Native Linux, Not Docker Desktop) (15 min)

**Previous issue**: Docker Desktop behavior differs from native Linux Docker.

**Solution**: Install Docker natively in WSL2.

```bash
# In WSL2
# Official Docker installation for Ubuntu
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add user to docker group (avoid sudo)
sudo usermod -aG docker $USER

# Log out and back in (or newgrp docker)
exit
# Reopen WSL2 terminal

# Verify Docker works
docker run hello-world
```

---

#### Step 5: Set Up Qdrant (Native Linux Container) (10 min)

**Previous issue**: Qdrant connection failures likely due to Windows/WSL2 networking quirks.

**Solution**: Run Qdrant natively in WSL2 Docker.

```bash
# In WSL2
cd ~/rhiz_localdev

# Start Qdrant (dev instance, separate from VPS)
docker run -d \
  --name qdrant_local \
  -p 6333:6333 \
  -v ~/qdrant_storage:/qdrant/storage \
  qdrant/qdrant:v1.7.4

# Verify connection
curl http://localhost:6333/collections
# Should return JSON with collections list (may be empty initially)
```

---

#### Step 6: Install MCP Servers (WSL2 Native) (30 min)

**Previous issue**: "Complete MCP failure" likely due to:
- Windows Python paths in `.mcp.json`
- Windows filesystem permissions on `/mnt/c/...`
- Environment variable issues

**Solution**: Reinstall MCP servers in WSL2 with native paths.

```bash
# In WSL2
cd ~/rhiz_localdev

# Install Python (if not present)
sudo apt update
sudo apt install python3 python3-pip python3-venv -y

# rhiz-mcp
cd tools/rhiz-mcp
python3 -m venv venv
source venv/bin/activate
pip install -e .
deactivate

# memory-mcp
cd ../memory-mcp
python3 -m venv venv
source venv/bin/activate
pip install -e .
deactivate

# Return to project root
cd ~/rhiz_localdev
```

**Update `.mcp.json`** (WSL2 native paths):
```json
{
  "mcpServers": {
    "rhiz-mcp": {
      "command": "/home/dread/rhiz_localdev/tools/rhiz-mcp/venv/bin/python",
      "args": ["-m", "rhiz_mcp"],
      "env": {
        "RHIZ_ROOT": "/home/dread/rhiz_localdev",
        "QDRANT_URL": "http://localhost:6333"
      }
    },
    "memory-mcp": {
      "command": "/home/dread/rhiz_localdev/tools/memory-mcp/venv/bin/python",
      "args": ["-m", "memory_mcp"],
      "env": {
        "QDRANT_URL": "http://localhost:6333",
        "COLLECTION_NAME": "rhiz_memories"
      }
    }
  }
}
```

---

#### Step 7: Test Claude Code + MCP Integration (20 min)

**Critical test**: This is where previous attempt failed.

```bash
# In WSL2
cd ~/rhiz_localdev
claude

# Once Claude Code starts:
# Test 1: Verify MCP servers loaded
/mcp list
# Should show: rhiz-mcp, memory-mcp (and status)

# Test 2: Call rhiz-mcp tool
# (In Claude conversation)
"Call get_dyad_state MCP tool"
# Should return current dyad state, not error

# Test 3: Call memory-mcp tool
"Search memory for 'VPS deployment'"
# Should search Qdrant, return results (or empty if no vectors yet)

# Test 4: File operations
"Read CURRENT_STATE.md"
# Should successfully read file from WSL2 filesystem
```

**If tests pass**: WSL2 migration successful, MCP working.

**If tests fail**: Debug specific failure:
- MCP server won't start → Check Python paths, venv activation
- Qdrant connection fails → Check Docker container running, port 6333
- File read fails → Check file permissions, RHIZ_ROOT env var

---

#### Step 8: VPS SSH from WSL2 (10 min)

**Verify**: Can access VPS from WSL2 same as from Windows.

```bash
# In WSL2
ssh root@72.62.81.128
# Should connect successfully

# Test Docker access
docker ps
# Should show trading containers running

# Test FC HTTP Gateway
curl http://localhost:8767/health
# Should return health status

# Exit VPS
exit
```

**Captain's Termius App**: Can also use from Windows, connects to VPS regardless of local environment.

---

### 2.3 Gradual Migration (1 week)

**Don't switch entirely overnight.** Use both environments during transition.

**Week 1 Strategy**:
- Days 1-2: Test WSL2 environment, verify all tools work
- Days 3-4: Do new development work in WSL2
- Days 5-7: If stable, make WSL2 primary
- Keep Windows setup archived for fallback

**Success Criteria**:
- MCP servers work reliably
- Scripts run without modification
- Docker behaves identically to VPS
- No environment translation friction

---

## Phase 3: Cloud Deployment Model (Post-Migration, 2-3 hours)

### Objective
One-command deploy from dev (WSL2) → production (VPS).

### 3.1 Deployment Script Architecture

**Pattern**: GitOps-style workflow with automated testing and rollback.

**Script**: `scripts/deploy_to_vps.sh`

```bash
#!/bin/bash
# Deploy from WSL2 dev to VPS production
set -e  # Exit on error

VPS_HOST="root@72.62.81.128"
VPS_DIR="/opt/rhiz_trading"
BACKUP_DIR="/opt/rhiz_trading_backup_$(date +%Y%m%d_%H%M%S)"

echo "=== Rhiz VPS Deployment ==="

# 1. Run local tests
echo "[1/7] Running local tests..."
cd ~/rhiz_localdev
# pytest tests/ (when tests exist)

# 2. Git status check
echo "[2/7] Checking git status..."
if [[ -n $(git status -s) ]]; then
  echo "WARNING: Uncommitted changes. Commit first?"
  read -p "Continue anyway? (y/n) " -n 1 -r
  echo
  if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    exit 1
  fi
fi

# 3. Backup current VPS deployment
echo "[3/7] Backing up current VPS deployment..."
ssh $VPS_HOST "cp -r $VPS_DIR $BACKUP_DIR"

# 4. Sync code to VPS
echo "[4/7] Syncing code to VPS..."
rsync -avz --exclude 'venv' --exclude '__pycache__' --exclude '.git' \
  --exclude 'archive_*' --exclude 'qdrant_storage' \
  ~/rhiz_localdev/ $VPS_HOST:$VPS_DIR/

# 5. Rebuild containers (if needed)
echo "[5/7] Rebuilding containers..."
ssh $VPS_HOST << 'ENDSSH'
  cd /opt/rhiz_trading
  docker-compose -f docker-compose.trading.yml build --no-cache
  docker-compose -f docker-compose.trading.yml up -d
ENDSSH

# 6. Health check
echo "[6/7] Verifying deployment health..."
sleep 10  # Wait for containers to start

# Check FC HTTP Gateway
HEALTH=$(curl -s http://72.62.81.128:8767/health || echo "FAILED")
if [[ $HEALTH == *"healthy"* ]]; then
  echo "✅ FC HTTP Gateway: Healthy"
else
  echo "❌ FC HTTP Gateway: FAILED"
  echo "Rolling back..."
  ssh $VPS_HOST "cd /opt/rhiz_trading && docker-compose down && cp -r $BACKUP_DIR/* $VPS_DIR/ && docker-compose up -d"
  exit 1
fi

# Check Qdrant
QDRANT=$(curl -s http://72.62.81.128:6333/collections || echo "FAILED")
if [[ $QDRANT == *"collections"* ]]; then
  echo "✅ Qdrant: Healthy"
else
  echo "❌ Qdrant: FAILED"
  # Continue anyway (non-critical for trading)
fi

# 7. Done
echo "[7/7] Deployment complete!"
echo "Backup available at: $VPS_HOST:$BACKUP_DIR"
echo "To rollback: ssh $VPS_HOST 'cd /opt/rhiz_trading && docker-compose down && cp -r $BACKUP_DIR/* /opt/rhiz_trading/ && docker-compose up -d'"
```

**Usage**:
```bash
# In WSL2
cd ~/rhiz_localdev
./scripts/deploy_to_vps.sh
```

---

### 3.2 Live Signal Capture Model

**Current**: VPS collecting moonchecks (iOS shortcut → mooncheck Worker → Qdrant)

**Expand to**:
1. **Trading signals** - Market data, pattern detection (SIL)
2. **System health** - Container status, resource usage (Cloudflare health Worker)
3. **Decision logs** - Why trades executed, pattern matching (FC logs → Qdrant)

**Architecture**:
```
VPS Production:
  ├─ Fathom MCP → Market data → Qdrant (trading_signals collection)
  ├─ SIL FastAPI → Pattern detection → Qdrant (sil_patterns collection)
  ├─ FC HTTP Gateway → Decision logs → Qdrant (fc_decisions collection)
  └─ Cloudflare Workers → Health metrics → D1 database

WSL2 Dev:
  ├─ Query Qdrant collections (analysis, backtesting)
  ├─ Develop new strategies
  ├─ Deploy via deploy_to_vps.sh
```

**Post-hibernation work**: Connect signal capture to strategy development loop.

---

## Phase 1 Execution Checklist (Tonight)

Use this checklist to track Phase 1 progress:

- [ ] **1.1 Aggressive Archival** (45 min)
  - [ ] Create `C:\Users\dread\Documents\Rhiz_Archives\archive_20260208_foundation_reset\`
  - [ ] Move `external/` (2-3 GB)
  - [ ] Move `Gifts_From_Alex/` (~1 GB)
  - [ ] Move `Claude_Grooves/` (~500 MB)
  - [ ] Archive old `docs/architecture/` (selective)
  - [ ] Archive old `docs/sessions/` (keep 72-74 only)
  - [ ] Move all 39 checkpoints to archive
  - [ ] Clean up duplicate configs (.env variants)
  - [ ] Verify ~8-10 GB freed

- [ ] **1.2 New Memory Architecture** (60 min)
  - [ ] Create `CURRENT_STATE.md` (50-100 lines)
  - [ ] Create checkpoint template (50-100 lines max)
  - [ ] Document loading strategy (3 checkpoint max)
  - [ ] Compress CLAUDE.md (3000 → 800-1200 lines)
  - [ ] Archive old CLAUDE.md to `Rhiz_Archives/`

- [ ] **1.3 Minimal Documentation Set** (45 min)
  - [ ] Verify QUICKSTART.md accuracy
  - [ ] Create `session_82_foundation_reset.yaml` checkpoint
  - [ ] Verify HIBERNATION_STATE.md current
  - [ ] Verify HIBERNATION_RESTORE.md current
  - [ ] Archive verbose docs (all but last 2-3 per category)

- [ ] **1.4 Test Hydration** (30 min)
  - [ ] Open fresh Claude Desktop (Opus 4.6)
  - [ ] Load CURRENT_STATE.md + checkpoint + CLAUDE.md
  - [ ] Ask: "What is Rhiz? What's running? What next?"
  - [ ] Evaluate response accuracy
  - [ ] Iterate if test fails

**Total Phase 1 Time**: 2-3 hours

---

## Phase 2 Execution Checklist (Tomorrow)

- [ ] **2.1 Verify WSL2** (5 min)
  - [ ] Run `wsl --list --verbose`
  - [ ] Confirm Ubuntu VERSION 2
  - [ ] Upgrade if needed

- [ ] **2.2 Move rhiz_localdev to WSL2 Native** (15 min)
  - [ ] Clone fresh to `~/rhiz_localdev` (NOT `/mnt/c/...`)
  - [ ] Copy `.env` and `.mcp.json` only
  - [ ] Verify native filesystem location

- [ ] **2.3 Install Claude Code (Linux)** (10 min)
  - [ ] Run official Linux install script
  - [ ] Verify `which claude` shows Linux path
  - [ ] Check version

- [ ] **2.4 Install Docker Native** (15 min)
  - [ ] Run Docker install script
  - [ ] Add user to docker group
  - [ ] Test `docker run hello-world`

- [ ] **2.5 Set Up Qdrant** (10 min)
  - [ ] Start Qdrant container on port 6333
  - [ ] Test `curl http://localhost:6333/collections`

- [ ] **2.6 Install MCP Servers** (30 min)
  - [ ] Install Python 3 + venv
  - [ ] Create venv for rhiz-mcp
  - [ ] Create venv for memory-mcp
  - [ ] Update `.mcp.json` with WSL2 native paths

- [ ] **2.7 Test Claude Code + MCP** (20 min)
  - [ ] Start `claude` in WSL2
  - [ ] Test `/mcp list`
  - [ ] Call `get_dyad_state`
  - [ ] Call memory search
  - [ ] Read CURRENT_STATE.md

- [ ] **2.8 Test VPS SSH** (10 min)
  - [ ] SSH from WSL2 to VPS
  - [ ] Test Docker commands
  - [ ] Test curl to FC HTTP Gateway

**Total Phase 2 Time**: 3-4 hours

---

## Phase 3 Execution Checklist (Post-Migration)

- [ ] **3.1 Create Deployment Script** (60 min)
  - [ ] Write `scripts/deploy_to_vps.sh`
  - [ ] Add local test step
  - [ ] Add git status check
  - [ ] Add VPS backup step
  - [ ] Add rsync sync
  - [ ] Add container rebuild
  - [ ] Add health checks
  - [ ] Add rollback on failure
  - [ ] Make executable (`chmod +x`)

- [ ] **3.2 Test Deployment** (30 min)
  - [ ] Make trivial change locally
  - [ ] Run `./scripts/deploy_to_vps.sh`
  - [ ] Verify change on VPS
  - [ ] Verify containers healthy

- [ ] **3.3 Expand Signal Capture** (60 min)
  - [ ] Design trading_signals collection schema
  - [ ] Connect Fathom → Qdrant (market data)
  - [ ] Connect SIL → Qdrant (patterns)
  - [ ] Connect FC → Qdrant (decisions)
  - [ ] Test query from WSL2

**Total Phase 3 Time**: 2-3 hours

---

## Success Metrics

### Phase 1 Success (Memory & Docs)
- ✅ Local storage reduced by 8-10 GB
- ✅ New Claude instance understands project in <5 min
- ✅ CLAUDE.md compressed to 800-1200 lines
- ✅ Checkpoint loading takes <10 seconds
- ✅ No "misdirection" feeling when navigating docs

### Phase 2 Success (WSL2 Environment)
- ✅ MCP servers work reliably (no "complete failure")
- ✅ Scripts written in WSL2 work on VPS without changes
- ✅ Docker behavior matches VPS (no surprises)
- ✅ No environment translation friction
- ✅ Can develop offline in WSL2

### Phase 3 Success (Deployment Model)
- ✅ One-command deploy from WSL2 → VPS
- ✅ Automated health checks catch failures
- ✅ Rollback works if deployment fails
- ✅ Live signal capture growing Qdrant collections
- ✅ VPS collects valuable data during hibernation

---

## Risk Mitigation

### Risk 1: Phase 1 archival breaks something
**Mitigation**: Don't delete anything, only move. Can restore from archive.

### Risk 2: WSL2 MCP fails again
**Mitigation**: Detailed troubleshooting steps in plan. If still fails, fall back to Windows + improved docs.

### Risk 3: VPS deployment script breaks production
**Mitigation**: Script creates backup before deploy, includes rollback command.

### Risk 4: Time estimates too optimistic
**Mitigation**: Phases are independent. Can pause between phases, resume later.

---

## Handoff to Opus 4.6 (Optional)

If Captain wants Opus 4.6 to review this plan and suggest improvements:

**Prompt for Opus 4.6**:
```
I'm working on the Rhiz project (human-AI symbiotic trading system). We're experiencing:
1. Memory system becoming "crippling prosthesis" instead of helpful
2. Documentation debt causing misdirection
3. Windows/Ubuntu environment friction

I've created a 3-phase plan to address these issues:
- Phase 1: Documentation/memory reset (aggressive archival, compressed expertise architecture)
- Phase 2: WSL2 migration (environment parity)
- Phase 3: Cloud deployment model (one-command deploy)

Please review the attached plan (RHIZ_FOUNDATION_RESET_PLAN.md) and provide:
1. Potential issues or failure modes I haven't considered
2. Optimizations to reduce time/complexity
3. Alternative approaches that might be better
4. Specific risks in WSL2 MCP migration (previously failed)
5. Suggestions for memory architecture (content-based compression)

Context: This is a production trading system with VPS running 24/7 during hibernation. We need to preserve signal collection while improving foundations.
```

---

## Next Session Opening (After Phase 1 Complete)

**Prompt for new session**:
```
Welcome back, First Mate. Foundation reset Phase 1 complete.

Load:
- CURRENT_STATE.md
- session_82_foundation_reset.yaml
- RHIZ_FOUNDATION_RESET_PLAN.md

Status:
- Documentation debt cleared (archives created, CLAUDE.md compressed)
- New memory architecture implemented (content-based, 3 checkpoint max)
- Ready for Phase 2: WSL2 migration

Next: Begin WSL2 environment setup per Phase 2 checklist.
```

---

## Appendix A: Compressed Expertise Principles Summary

From `docs/research/architecture_compressed_expertise_research_doc.md`:

1. **Chunking & Compilation**: Expertise becomes automatic patterns, not exhaustive detail
2. **Multi-Layer Memory**: Working (session), Episodic (limited checkpoints), Semantic (CLAUDE.md), Procedural (skills)
3. **Content-Based Compression**: Triggers on significant state change, not time
4. **Just-In-Time Delivery**: Load minimal context, expand on-demand
5. **Abstraction Hierarchy**: Higher levels (why) more transferable than lower (how)
6. **Cognitive Load Minimization**: Reduce noise, maximize signal

---

## Appendix B: File Structure After Phase 1

```
C:\Users\dread\Documents\
├─ Rhiz_LocalDev\                      # ~3-5 GB (down from ~13.8 GB)
│   ├─ core/
│   │   ├─ memory/
│   │   │   ├─ checkpoints/            # Fresh start (empty until Phase 1 complete)
│   │   │   └─ session_schema.yaml
│   │   ├─ skills/                     # Preserved (dormant)
│   │   ├─ daemon/                     # Preserved
│   │   ├─ hooks/                      # Preserved
│   │   └─ patterns/                   # Preserved
│   ├─ domains/
│   │   └─ trading/                    # Preserved (Fathom, FC, SIL)
│   ├─ infrastructure/
│   │   ├─ vps/                        # Preserved (deploy configs)
│   │   ├─ cloudflare/                 # Preserved (Workers)
│   │   └─ docker/                     # Preserved
│   ├─ tools/
│   │   ├─ rhiz-mcp/                   # Preserved (will rebuild venv in WSL2)
│   │   └─ memory-mcp/                 # Preserved
│   ├─ docs/
│   │   ├─ CURRENT_STATE.md            # NEW (50-100 lines)
│   │   ├─ CLAUDE.md                   # COMPRESSED (800-1200 lines)
│   │   ├─ QUICKSTART.md               # Preserved
│   │   ├─ HIBERNATION_STATE.md        # Preserved
│   │   ├─ HIBERNATION_RESTORE.md      # Preserved
│   │   ├─ RHIZ_FOUNDATION_RESET_PLAN.md  # NEW (this document)
│   │   ├─ architecture/               # Minimal (last 2-3 docs only)
│   │   ├─ sessions/                   # Minimal (Session 72-74 only)
│   │   └─ research/                   # Preserved (compressed_expertise paper)
│   ├─ scripts/
│   │   └─ deploy_to_vps.sh            # NEW (Phase 3)
│   ├─ .env                            # ONE file only
│   ├─ .mcp.json                       # ONE file only
│   └─ docker-compose.trading.yml      # ONE file only
│
└─ Rhiz_Archives\                      # ~8-10 GB
    └─ archive_20260208_foundation_reset/
        ├─ external/                   # Reference repos
        ├─ Gifts_From_Alex/            # Gift content
        ├─ Claude_Grooves/             # Music project
        ├─ verbose_docs/               # Old architecture docs
        ├─ old_checkpoints/            # All 39 checkpoints
        ├─ deprecated_configs/         # Old .env variants
        └─ CLAUDE.md.verbose           # Original 3000+ line version
```

---

## Appendix C: WSL2 File Structure After Phase 2

```
/home/dread/
├─ rhiz_localdev/                      # WSL2 native (NOT /mnt/c/...)
│   ├─ [same structure as Windows, but native Linux]
│   ├─ .mcp.json                       # WSL2 paths
│   └─ tools/
│       ├─ rhiz-mcp/
│       │   └─ venv/                   # Linux native Python venv
│       └─ memory-mcp/
│           └─ venv/                   # Linux native Python venv
│
└─ qdrant_storage/                     # Qdrant data (separate from VPS)
```

---

**End of Plan**

**Status**: Ready for execution
**Next Step**: Begin Phase 1 archival tonight
**Questions**: See Captain's answers in session discussion
**Rollover**: Use this document to brief next session after Phase 1 complete
