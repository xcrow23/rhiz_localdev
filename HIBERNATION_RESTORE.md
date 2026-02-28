# Rhiz Hibernation Restoration Guide

**Use this when**: Returning from hibernation to active development
**Expected Time**: 30-45 minutes (without optional archive restoration)
**Prerequisites**: VPS access, local Docker, Python 3.11+

---

## Pre-Restoration Checklist

Before starting, verify you have:
- [ ] **VPS access** via SSH or Hostinger MCP tools
- [ ] **Local Docker running** (`docker --version` shows installed version)
- [ ] **Python 3.11+** installed (`python --version`)
- [ ] **Git status clean** (no uncommitted hibernation changes)
- [ ] **Read HIBERNATION_STATE.md** for context on what was paused

**Optional** (if you archived during hibernation):
- [ ] Archive files accessible (`backups\Gifts_From_Alex_hibernation_archive.tar.gz`)
- [ ] OneDrive backup location accessible (for Claude_Grooves if moved)

---

## Restoration Sequence (7 Steps)

### Step 1: Verify Local Qdrant (2-3 min)

**Goal**: Ensure local vector memory is accessible

```bash
# Start Qdrant if not running
docker-compose up -d qdrant

# Verify health
curl http://localhost:6333/health

# Expected: "healthy" status

# Check collections
curl http://localhost:6333/collections/rhiz_memories
curl http://localhost:6333/collections/rhiz_skills
curl http://localhost:6333/collections/rhiz_skill_memory
```

**Expected Results**:
- `rhiz_memories`: 161+ points (compare to hibernation entry count)
- `rhiz_skills`: 6 points (skill fingerprints)
- `rhiz_skill_memory`: 8+ points (Mem0 activation results)

**Troubleshooting**:
- If Qdrant not running: Check Docker daemon (`docker ps`)
- If collections missing: Check Docker volumes (`docker volume ls | grep qdrant`)
- If data persisted: Qdrant stores data in `./qdrant_data` locally

---

### Step 2: Load Hibernation Checkpoint (2 min)

**Goal**: Restore session context from hibernation entry

**Via rhiz-mcp** (recommended):
```
# Using MCP tool from Claude Code or direct invocation
load_checkpoint session_20260131_hibernation_entry.yaml
```

**Or manual read**:
```bash
cat core/memory/checkpoints/session_20260131_hibernation_entry.yaml
```

**Review Key Sections**:
- `session_arc`: Hibernation context (why paused, what's active)
- `next.on_resumption`: Actionable items for resumption
- `component_state`: System health at hibernation entry
- `working_memory.current_state`: What was operational

**Note Values** (for comparison):
- `component_state.memory_system.local_qdrant.collections`: Baseline vector counts
- `component_state.trading_infrastructure`: Phase 1/6 status
- `component_state.skills_system.routing_accuracy`: 93.3% baseline

---

### Step 3: Review VPS Signal Collection (10-15 min)

**Goal**: Understand what signals VPS collected during hibernation

**Check VPS Qdrant**:
```bash
# Via Hostinger MCP or direct curl
curl http://72.62.81.128:6333/collections/moonchecks

# Compare vector count to hibernation baseline (0 vectors)
# Growth = signals collected during hibernation
```

**Expected**: Vector count > 0 if mooncheck Worker ran during hibernation

**Check VPS Container Status**:
```bash
# Via Hostinger MCP: VPS_getProjectListV1 with virtualMachineId: 1206808
# Or via SSH/curl if available

# Verify running containers:
# - Qdrant (rhiz_trading project)
# - Fathom MCP, Fathom Commander
# - n8n workflows
# - SIL API
```

**Document Findings** (for resumption checkpoint):
- Moonchecks vector count growth
- Any container failures or restarts
- VPS resource usage (if accessible)
- n8n workflow execution logs (observation mode only)

**Known Issues to Check**:
- FastAPI Gateway: Was unhealthy at hibernation entry
- SIL API: Was unhealthy at hibernation entry
- nginx container: Was created but not started (not critical)

---

### Step 4: Restore Archives IF NEEDED (15-20 min)

**Only if you archived storage during hibernation prep. If you skipped archival, skip this step.**

#### 4a. Restore Gifts_From_Alex (if archived)

```powershell
# Verify archive exists
Test-Path "backups\Gifts_From_Alex_hibernation_archive.tar.gz"

# Extract archive
tar -xzf "backups\Gifts_From_Alex_hibernation_archive.tar.gz"

# Verify extraction (spot check)
Test-Path "Gifts_From_Alex\ai-through-symbiosis-master"
```

**Expected**: ~3.3 GB uncompressed from ~500 MB archive

#### 4b. Restore external/ (if archived)

```powershell
tar -xzf "backups\external_hibernation_archive.tar.gz"
Test-Path "external\anthropic-docs"
```

**Expected**: ~75 MB uncompressed from ~20 MB archive

#### 4c. Move Claude_Grooves back (if moved)

```powershell
# From OneDrive or external storage
Move-Item "C:\Users\dread\OneDrive\Rhiz_Backups\Claude_Grooves_hibernation" "Claude_Grooves"

# Or from external drive
# Move-Item "E:\Rhiz_Backups\Claude_Grooves_hibernation" "Claude_Grooves"
```

**Expected**: 138 MB restored

---

### Step 5: Regenerate Virtual Environments (10-15 min)

**Only if venvs were deleted during hibernation. If you kept them, skip this step.**

#### 5a. Main venv (root directory)

```powershell
# Create venv
python -m venv venv

# Activate (Windows)
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Verify installation
pip list | Select-String -Pattern "qdrant-client|pyyaml|sentence-transformers"
```

**Expected**: ~6 GB venv, ~5-10 min install time

#### 5b. rhiz-mcp venv

```powershell
cd tools\rhiz-mcp

# Create venv
python -m venv venv

# Activate
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Verify MCP server imports
python -c "from server import *; print('MCP server imports OK')"

cd ..\..
```

**Expected**: ~1 GB venv, ~3-5 min install time

**Troubleshooting**:
- If `python` not found: Check PATH, may need `python3` or full path
- If install fails: Check internet connection, try `pip install --upgrade pip` first
- If dependencies conflict: Delete venv, recreate, install fresh

---

### Step 6: Test MCP Servers (5 min)

**Goal**: Verify MCP infrastructure functional

**Via Claude Code CLI or rhiz-mcp invocation**:

```bash
# Test rhiz-mcp tools
get_dyad_state
# Expected: Shows Captain state, First Mate state, shared focus

get_captain_state
# Expected: Returns Captain's current focus/mode

memory_context
# Expected: Returns relevant hibernation-related memories

checkpoint_search query="hibernation"
# Expected: Finds session_20260131_hibernation_entry.yaml

# Test memory-mcp tools
memory_search query="hibernation" limit=5
# Expected: Returns semantic matches for "hibernation"

memory_stats
# Expected: Shows collection stats (rhiz_memories: 161+ points)

memory_health_check
# Expected: Returns health score and status
```

**Troubleshooting**:
- If tools not found: Verify `.mcp.json` paths, check venv activation
- If Qdrant connection fails: Verify Qdrant running (`docker ps | grep qdrant`)
- If memory context empty: Check rhiz_memories collection exists

---

### Step 7: Update System State (5 min)

**Goal**: Document resumption in new checkpoint

**Create Resumption Checkpoint**:

File: `core/memory/checkpoints/session_[DATE]_hibernation_exit.yaml`

**Key Content**:
```yaml
checkpoint:
  created: "[TIMESTAMP]"
  session_topic: "Hibernation Exit - Resumption to Active Development"
  system_health_score: [ASSESS AFTER REVIEW]
  architectural_phase: "Active Development - Post-Hibernation"

session_arc: |
  Resuming from hibernation after [DURATION]:

  **Hibernation Summary**:
  - Duration: [START] to [END]
  - VPS signal collection: [MOONCHECKS COUNT] vectors collected
  - Local memory preserved: [CHECKPOINTS], [VECTORS] across collections
  - No data loss, clean hydration

  **Resumption Priorities**:
  - [REVIEW VPS FINDINGS]
  - [ADDRESS ANY DRIFT OR GAPS]
  - [RESUME PHASE 2 INTEGRATION]

next:
  immediate:
    - "Review VPS container health (FastAPI Gateway, SIL API unhealthy at hibernation)"
    - "Address moonchecks signal quality"
    - "Resume Phase 2 Component Integration when ready"
```

**Verification**:
```bash
# Validate checkpoint YAML
python -c "import yaml; yaml.safe_load(open('core/memory/checkpoints/session_[DATE]_hibernation_exit.yaml'))"
```

---

## Post-Restoration: Resume Phase 2

**When ready to continue development**:

### Phase 2 Priorities (from pre-hibernation state):

1. **Review CURRENT_STATE.md**: Update component status, note any drift
2. **Phase 2 Integration Planning**: Connect Fathom → FC → SIL workflow
3. **Skill-tool binding**: Decide on framework approach
4. **n8n → Cloudflare Workers migration**: Resume 9 pending workflows
5. **Address VPS issues**: FastAPI Gateway unhealthy, SIL API unhealthy

### Integration Gaps to Address (85/0 pattern):

| Gap | Status Pre-Hibernation | Priority |
|-----|------------------------|----------|
| Fathom Phase 2-6 | Not deployed | HIGH (blocks trading execution) |
| FC HTTP Gateway | Deployed on VPS, local pending | MEDIUM |
| Skill-tool binding | Framework missing | MEDIUM |
| n8n → Workers | 9 workflows pending | LOW |

### See Architecture Docs:

- `docs/architecture/` - Design decisions, ADRs
- `docs/CURRENT_STATE.md` - Component status, next priorities
- `HIBERNATION_STATE.md` - What was paused, what's active

---

## Troubleshooting

### Qdrant Collections Missing

**Symptom**: `curl http://localhost:6333/collections` returns empty or missing collections

**Diagnosis**:
```bash
# Check if Qdrant data persisted
docker volume ls | grep qdrant

# Check local data directory
ls ./qdrant_data
```

**Solutions**:
1. **If volume exists**: Restart Qdrant container (`docker-compose restart qdrant`)
2. **If data directory exists**: Check Qdrant logs (`docker logs qdrant`)
3. **If data lost**: Restore from backup (see Emergency Rollback below)

---

### MCP Servers Not Starting

**Symptom**: Tools not found or import errors

**Diagnosis**:
```bash
# Verify .mcp.json paths
cat .mcp.json

# Check Python paths
where python
python --version

# Test manual import
cd tools\rhiz-mcp
python -c "from server import *"
```

**Solutions**:
1. **If venv missing**: Regenerate venv (Step 5)
2. **If paths wrong**: Update `.mcp.json` with correct absolute paths
3. **If dependencies missing**: Reinstall (`pip install -r requirements.txt`)

---

### Archives Not Found

**Symptom**: Backup files missing from `backups/` directory

**Solutions**:
1. **Check OneDrive**: `C:\Users\dread\OneDrive\Rhiz_Backups\`
2. **Check external drive**: `E:\Rhiz_Backups\` (if used)
3. **Can skip if not needed**: External repos can be re-cloned
   ```bash
   cd external
   git clone https://github.com/anthropics/anthropic-docs.git
   ```

---

### VPS Unreachable

**Symptom**: `curl http://72.62.81.128:6333` fails or times out

**Diagnosis**:
```bash
# Check VPS running
# Via Hostinger MCP: VPS_getVirtualMachinesV1
# Expected: state="running"

# Check network connectivity
ping 72.62.81.128

# Check SSH access (if available)
ssh root@72.62.81.128
```

**Solutions**:
1. **If VPS stopped**: Start via Hostinger dashboard or MCP tools
2. **If network issue**: Check local firewall, VPN settings
3. **If SSH key invalid**: Regenerate SSH keys via Hostinger dashboard
4. **Can defer**: VPS signal collection is optional, proceed with local restoration

---

### Moonchecks Collection Empty

**Symptom**: `curl http://72.62.81.128:6333/collections/moonchecks` shows 0 vectors

**Explanation**: This is expected if:
- Mooncheck Worker didn't run during hibernation (cron schedule)
- Worker encountered errors (check Cloudflare Workers logs)
- n8n workflows paused (check n8n execution history)

**Not a failure**: VPS was in observation mode, signals optional. Proceed with resumption.

---

### FastAPI Gateway or SIL API Unhealthy

**Symptom**: VPS containers show "unhealthy" status

**Known Issue**: Both were unhealthy at hibernation entry (2026-01-31)

**Diagnosis**:
```bash
# Via Hostinger MCP or SSH
docker logs fastapi-gateway
docker logs rhiz-sil-api

# Check health check endpoints
curl http://72.62.81.128:8080/health  # FastAPI Gateway
curl http://72.62.81.128:8001/health  # SIL API (NOT 8000)
```

**Solutions**:
1. **If port mismatch**: SIL uses port 8001, not 8000 (common issue)
2. **If dependency missing**: Restart containers (`docker-compose restart`)
3. **If config error**: Review container logs for specific error
4. **Can defer**: Not blocking local development resumption

---

## Emergency Rollback

**If restoration fails critically**:

### Fallback Checkpoint

Load last known good checkpoint before hibernation:

```bash
# Via rhiz-mcp
load_checkpoint session_20260124_phase2_complete.yaml

# This checkpoint predates hibernation, no corrupted state
```

### Minimal Restoration

If full restoration fails, minimal working state:

1. **Qdrant local**: Must be running (`docker-compose up -d qdrant`)
2. **Checkpoints**: Must be readable (39 YAML files in `core/memory/checkpoints/`)
3. **MCP servers**: Can regenerate venv if needed

**Document Issue**:
Create emergency checkpoint documenting what failed and current state:

```yaml
checkpoint:
  session_topic: "Emergency Restoration - [ISSUE DESCRIPTION]"

session_arc: |
  Restoration from hibernation encountered critical issue:
  [DESCRIBE WHAT FAILED]

  Current state: [MINIMAL WORKING STATE]
  Blocked on: [SPECIFIC ISSUE]

next:
  immediate:
    - "[SPECIFIC RECOVERY ACTION]"
    - "Review HIBERNATION_RESTORE.md troubleshooting"
```

### Memory Persistence is Robust

Even in worst case:
- ✅ Checkpoints stored as YAML files (not lost)
- ✅ Qdrant data persists in Docker volumes (survives restarts)
- ✅ Critical configs preserved (`.env`, `.mcp.json`)
- ✅ Code intact in `core/`, `domains/`, `tools/`

**Data loss risk**: VERY LOW. Restoration is recoverable.

---

## Verification Checklist

Before considering restoration complete:

- [ ] Local Qdrant healthy (3 collections accessible)
- [ ] Hibernation checkpoint loaded successfully
- [ ] VPS status reviewed (moonchecks count documented)
- [ ] Archives restored (if archived)
- [ ] Venvs regenerated (if deleted)
- [ ] MCP servers responding (get_dyad_state, memory_context work)
- [ ] Resumption checkpoint created
- [ ] CURRENT_STATE.md reviewed for accuracy

**Expected Total Time**: 30-45 minutes (if no archival restoration)

**Critical Path**: Qdrant → Checkpoint → VPS signals → MCP servers

---

## Success Criteria

Restoration successful when:
- ✅ All memory systems accessible (checkpoints + Qdrant)
- ✅ MCP servers functional (11 rhiz-mcp tools, 6 memory-mcp tools)
- ✅ VPS status documented (moonchecks growth, container health)
- ✅ Resumption checkpoint created with context
- ✅ No critical blockers to Phase 2 resumption

**Next**: Resume active development at Captain's discretion.

---

**Document Version**: 1.0.0
**Last Updated**: 2026-01-31
**Maintenance**: Review quarterly or after major infrastructure changes
