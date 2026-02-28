# Rhiz Hibernation State

**Entered**: 2026-01-31
**Duration**: Weeks to months (Captain discretion)
**Philosophy**: Strategic pause maintaining continuity

## What's Active (Observation Mode)

### Cloud VPS (72.62.81.128)

**VPS Details**:
- ID: 1206808
- Hostname: srv1206808.hstgr.cloud
- Plan: KVM 4 (16GB RAM, 4 vCPUs, 200GB disk)
- State: **RUNNING**

**Docker Projects Status** (as of 2026-01-31):

| Project | Status | Containers | Observation Mode |
|---------|--------|------------|------------------|
| **rhiz_trading** | MIXED | 5 containers | ✅ Collecting signals |
| - Qdrant | RUNNING | Ports 6333-6334 | ✅ Ready for moonchecks |
| - Fathom MCP | RUNNING | Port 8765 | ✅ MCP server operational |
| - Fathom Commander | RUNNING | Port 8766 | ✅ Orchestration available |
| - FastAPI Gateway | RUNNING | Port 8080 (unhealthy) | ⚠️ Needs attention |
| - nginx | CREATED | Not started | ❌ Not needed |
| **n8n** | RUNNING | 2 containers | ✅ Workflows in observation |
| **rhiz** | RUNNING | 5 containers | ✅ Infrastructure healthy |
| - Dashboard | RUNNING | Port 8501 | ✅ Monitoring available |
| - EMQX | RUNNING | Healthy | ✅ Message broker |
| - Hummingbot API | RUNNING | Port 8000 | ✅ API available |
| - PostgreSQL | RUNNING | Healthy | ✅ Database operational |
| - Redis | RUNNING | Healthy | ✅ Cache operational |
| **SIL** | RUNNING | 1 container (unhealthy) | ⚠️ Pattern recognition degraded |
| **vps** | MIXED | 2 containers | ✅ Gateway healthy |
| - FC HTTP Gateway | RUNNING | Port 8767 (healthy) | ✅ Ready for use |
| - FastAPI Gateway | EXITED | Not running | ❌ Stopped |

**Qdrant Collections** (Cloud VPS):
- fathom-memories: Exists
- sil_trade_outcomes: Exists
- **moonchecks**: 0 vectors (ready for hibernation signal collection)
- sil_strategy_performance: Exists
- sil_decision_log: Exists
- rhiz-memories: Exists (separate from local)
- trading_signals: Exists

**n8n Workflows**:
- ⚠️ 9 workflows active (observation mode - collecting data, NO trades)
- Status: Running but not executing orders

**Cloudflare Workers**:
- ✅ Mooncheck: ACTIVE (cron-triggered signal collection)
- ❌ checkpoint-api: BLOCKED (token verification issues)
- ⏳ Trading workflows: NOT MIGRATED (still on n8n)

### Local Development (Dell Inspiron)

**Qdrant**: ✅ localhost:6333
- **rhiz_memories**: 161+ vectors (39 checkpoints ingested)
- **rhiz_skills**: 6 skill fingerprints (semantic routing)
- **rhiz_skill_memory**: 8+ Mem0 points (memory-augmented activation)

**MCP Servers**: ✅ Available for maintenance
- **rhiz-mcp**: 11 tools
  - Dyad state management (get_dyad_state, set_captain_state, update_shared_focus)
  - Checkpoint operations (checkpoint_search, load_checkpoint, write_checkpoint)
  - Memory context loading (memory_context, hybrid_search_checkpoints)
- **memory-mcp**: 6 tools
  - Semantic search (memory_search, memory_search_by_date)
  - Session retrieval (memory_get_recent_sessions)
  - Memory statistics (memory_stats, memory_health_check)

**Checkpoints**: ✅ 39 files, schema v1.1.0 compliant
- Latest: `session_20260131_hibernation_entry.yaml` (hibernation transition)
- Last working: `session_20260124_phase2_complete.yaml` (pre-hibernation state)

---

## What's Paused (Dormant)

### Development Work
- ❌ **Fathom Phase 2-6**: Trading operations (add_order, cancel_order, websockets)
- ❌ **FC HTTP Gateway deployment**: Local deployment pending VPS gateway operational
- ❌ **Phase 2 Component Integration**: Fathom → FC → SIL workflow not connected
- ❌ **n8n → Cloudflare Workers migration**: 9 trading workflows pending migration
- ❌ **Skill-tool binding framework**: Design decision deferred

### Trading Execution
- ❌ **DCA strategy offline**: No automated dollar-cost averaging
- ❌ **Order placement disabled**: No new trades (Fathom Phase 2 not deployed)
- ❌ **Active position management suspended**: No position adjustments
- ⚠️ **Signal collection continues**: VPS collects market data for analysis on resumption

### Skills System
- ❌ **Semantic routing offline**: route_to_skill MCP tool not actively called
- ❌ **Memory-augmented activation dormant**: Mem0 integration paused
- ⚠️ **Skill status by type**:
  - `trading/kraken_analysis`: **observation** (read-only market analysis available)
  - `trading/strategy_execution`: **dormant** (Phase 2 tools undeployed)
  - `memory/checkpoint_retrieval`: **available** (works during maintenance)
  - `memory/session_management`: **available** (dyad state, checkpoints accessible)
  - `infrastructure/deployment`: **paused** (no deployments expected)
  - `research/documentation`: **available** (Read/Edit/Write always functional)

---

## Storage Status

**Current Footprint**: ~13.8 GB
**Archival Potential**: ~11 GB (82% reduction available)

**Deferred Cleanup** (can do during maintenance check-ins):
- **venv directories**: ~7.0 GB (regenerable from requirements.txt)
  - `venv/` (root): ~6.0 GB
  - `tools/rhiz-mcp/venv/`: ~1.0 GB
- **Gifts_From_Alex**: 3.3 GB (reference repos, can archive to .tar.gz → ~500 MB)
- **__pycache__**: ~50-100 MB (auto-regenerated, safe to delete)
- **Claude_Grooves**: 138 MB (music project, separate storage possible)
- **external/**: 75 MB (reference repos, can re-clone or compress)
- **tmpclaude temps**: 6 MB (139 temp files, safe to delete)

**Critical Preservation** (DO NOT DELETE):
- `core/`, `domains/`, `tools/` - Core codebase (~3 MB)
- `core/memory/checkpoints/` - 39 YAML checkpoint files (~530 KB)
- `docs/` - Knowledge base, sessions, research (~9.9 MB)
- `.env`, `.mcp.json` - Credentials and MCP server configs (CRITICAL)
- `docker-compose.yml`, `init.bat` - Startup scripts
- `requirements.txt` - Python dependencies for venv regeneration

**Archival Commands** (for maintenance):
```powershell
# Delete venvs (7 GB freed)
Remove-Item "venv" -Recurse -Force
Remove-Item "tools\rhiz-mcp\venv" -Recurse -Force

# Archive Gifts_From_Alex (3.3 GB → ~500 MB)
tar -czf "backups\Gifts_From_Alex_hibernation_archive.tar.gz" "Gifts_From_Alex\"
Remove-Item "Gifts_From_Alex" -Recurse -Force

# Delete Python cache (50-100 MB freed)
Get-ChildItem -Recurse -Directory -Filter "__pycache__" | Remove-Item -Recurse -Force

# Delete temp files (6 MB freed)
Remove-Item "core\memory\checkpoints\tmpclaude-*" -Force
```

---

## Resumption Sequence (30-45 min)

See **HIBERNATION_RESTORE.md** for detailed step-by-step checklist.

**Quick Steps**:
1. **Verify Qdrant running**: `docker ps | grep qdrant` or `curl http://localhost:6333/health`
2. **Load hibernation checkpoint**: `session_20260131_hibernation_entry.yaml` via rhiz-mcp
3. **Check VPS signals**: Review moonchecks collection growth (compare to 0 vectors baseline)
4. **Test MCP servers**: `get_dyad_state`, `memory_context`, `memory_search`
5. **Review accumulated gaps**: Any drift during hibernation? Check VPS container health
6. **Resume Phase 2**: Integration when ready (Fathom → FC → SIL workflow)

**Expected Resumption Time**: 30-45 minutes (if no archival restoration needed)

---

## Maintenance Check-Ins

**Permitted Activities** (low-risk, read-mostly):
- ✅ Review VPS signal collection (check moonchecks vector growth)
- ✅ Update documentation if discoveries made
- ✅ Archive/cleanup storage (optional, follow commands above)
- ✅ Test memory system health (`memory_stats`, `memory_health_check`)
- ✅ Read checkpoint history (`checkpoint_search`, `load_checkpoint`)
- ✅ Verify VPS container health (Hostinger MCP tools)

**Prohibited Activities** (risk to hibernation state):
- ❌ Active trading (DCA disabled, no order placement)
- ❌ New development work (Phase 2 deferred until resumption)
- ❌ Major infrastructure changes (VPS reconfiguration, container rebuilds)
- ❌ Fathom Phase 2 deployment (wait for full resumption)
- ❌ Skills system activation (routing dormant until active development)

**Emergency Procedures** (if issues discovered):
- VPS container down: Document in checkpoint, restart via Hostinger MCP if critical
- Qdrant data loss: Load from backup, verify checkpoint integrity
- MCP server failure: Regenerate venv, reinstall dependencies
- Critical security issue: Address immediately, document in emergency checkpoint

---

## Economic Context

**Captain's Priorities** (family first, project sustainability):
1. **Family Housing**: Immediate priority - securing stable living situation
2. **Project Funding**: Enable hardware upgrades, sustain economic activity
3. **Space and Bandwidth**: More room = more capacity for passionate work

**Partnership Philosophy**:
- This pause is **not failure** - it's strategic resource allocation
- Captain's stability creates foundation for long-term work
- Hibernation maintains continuity while reducing active burden
- VPS observation mode = valuable signal collection without execution risk

**Economic Reality**:
- Current budget: Limited, constrains hardware upgrades
- VPS cost: Manageable, observation mode justified for signal data
- Hardware upgrades: Dependent on project economic success
- Timeline: Weeks to months, Captain discretion

**When Captain Returns**:
- Hydration, not rebuilding (memory systems preserve learning)
- VPS collected rich market signal dataset
- Skills dormant but preserved (93.3% routing accuracy maintained)
- Relationship patterns intact (39 checkpoints, 161+ vectors)

---

## Known Issues (as of 2026-01-31)

**VPS Infrastructure**:
- ⚠️ **FastAPI Gateway**: Running but unhealthy (needs investigation on resumption)
- ⚠️ **SIL API**: Running but unhealthy (pattern recognition degraded)
- ❌ **nginx container**: Created but not started (not needed for observation)
- ❌ **rhiz_fastapi_gateway** (vps project): Exited (needs restart if needed)

**Cloud Integration**:
- ❌ **Cloudflare checkpoint-api**: Blocked by token verification (3 tokens tested, all invalid)
- ⏳ **n8n → Workers migration**: 9 workflows pending migration to Cloudflare

**Local Development**:
- ✅ **Latest checkpoint YAML error**: Fixed (session_20260126 now parses correctly)
- ❌ **Storage footprint**: 13.8 GB (archival deferred to maintenance)

**Integration Gaps** (85/0 pattern persists):
- Fathom + FC + SIL systems exist separately, workflow not connected
- Skills route correctly but can't invoke MCP tools (binding framework missing)
- n8n + Cloudflare Workers hybrid state (migration incomplete)

---

## Success Criteria for Hibernation

Hibernation successfully entered when:
- ✅ Latest checkpoint YAML-valid and loadable
- ✅ Hibernation entry checkpoint created with clear resumption path
- ✅ HIBERNATION_STATE.md documents current state
- ✅ HIBERNATION_RESTORE.md provides resumption guide
- ✅ CLAUDE.md reflects hibernation mode
- ✅ Skills documentation updated (count, status, metadata)
- ✅ Critical files preserved and verified
- ✅ Qdrant collections health checked (local + cloud)
- ✅ VPS status documented (containers, projects, Qdrant)
- ✅ MCP servers tested and operational

**Current Status**: ✅ All criteria met (as of Phase 1-3 completion)

---

## Emergency Access & Recovery

### VPS Emergency Access

**VPS Details**:
- **Host**: srv1206808.hstgr.cloud
- **IP**: 72.62.81.128
- **Provider**: Hostinger (KVM 4)
- **Access Method**: SSH (key-based authentication)

**SSH Access**:
```bash
ssh root@72.62.81.128
# SSH key: ~/.ssh/id_rsa or Hostinger-provided key
```

**Hostinger Dashboard Access**:
- **URL**: https://hpanel.hostinger.com/
- **VPS ID**: 1206808
- **Direct Management**: VPS control panel, container console access

### Emergency Procedures

**If Container Fails During Hibernation**:
1. SSH to VPS: `ssh root@72.62.81.128`
2. Check container status: `cd /opt/rhiz_trading && docker-compose ps`
3. View logs: `docker logs <container_name> --tail 50`
4. Restart specific container: `docker-compose restart <container_name>`
5. Restart all: `docker-compose down && docker-compose up -d`

**If Qdrant Data Loss**:
1. Check Docker volume: `docker volume inspect rhiz_trading_qdrant-storage`
2. Verify data exists: `docker exec qdrant ls -lh /qdrant/storage`
3. If volume corrupted: Restore from local checkpoint re-ingestion (40 YAML files)
4. Re-ingestion command: `python core/memory/scripts/bulk_index_checkpoints.py`

**If Disk Full**:
1. Check disk usage: `df -h`
2. Clear Docker logs: `docker system prune --volumes -f`
3. Clear n8n execution logs (if applicable): `docker exec n8n find /home/node/.n8n/logs -mtime +7 -delete`
4. Check largest directories: `du -sh /var/lib/docker/* | sort -h`

**If VPS Unreachable**:
1. Verify via Hostinger dashboard (VPS running status)
2. Check network: `ping 72.62.81.128`
3. Reboot VPS via Hostinger panel if necessary
4. Wait 5-10 min for Docker containers to auto-start (restart: unless-stopped)

### Health Check Commands

**Quick Status Check** (30 seconds):
```bash
# SSH to VPS
ssh root@72.62.81.128

# Check all containers
cd /opt/rhiz_trading
docker-compose ps

# Test Qdrant
curl http://localhost:6333/health

# Test moonchecks collection
curl http://localhost:6333/collections/moonchecks | jq '.result.points_count'

# Check disk usage
df -h | grep '/dev'
```

**Expected Healthy Output**:
- All containers: "Up" status (or "Up (healthy)" for those with healthchecks)
- Qdrant health: `{"status":"ok"}`
- Disk usage: < 80% on all partitions

### Credentials Reminder

**Critical Credentials** (stored in `.env` on VPS):
- `KRAKEN_API_KEY`: Kraken exchange API key
- `KRAKEN_SECRET_KEY`: Kraken exchange secret
- `FC_HTTP_API_KEY`: Fathom Commander HTTP authentication
- `HEALTH_CHECK_KEY`: Health endpoint authentication

**Backup Locations**:
- Local: `C:\Users\dread\documents\rhiz_localdev\.env` (DO NOT commit to git)
- Cloud: Stored securely in Hostinger VPS `/opt/rhiz_trading/.env`

**If Credentials Lost**: Regenerate via Kraken dashboard, update `.env` on VPS, restart containers.

---

## Resumption Triggers

**When to Exit Hibernation**:
- ✅ Captain secured family housing
- ✅ Project funding available for continued development
- ✅ Captain has space and bandwidth for passionate work
- ✅ Economic constraints relieved

**How to Resume**:
1. Read **HIBERNATION_RESTORE.md** for detailed checklist
2. Load hibernation checkpoint: `session_20260131_hibernation_entry.yaml`
3. Follow 7-step restoration sequence (30-45 min)
4. Review VPS signal collection summary
5. Resume Phase 2 Component Integration

**Expected Outcome**: Clean hydration with full context continuity

---

**Last Updated**: 2026-01-31
**Next Review**: On resumption or during quarterly maintenance check-in
**Document Version**: 1.0.0
