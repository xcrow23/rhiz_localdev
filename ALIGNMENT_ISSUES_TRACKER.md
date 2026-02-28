# RHIZ ALIGNMENT ISSUES - PRIORITIZED TRACKER
**Generated**: 2026-01-10 (Session 39)
**Total Issues**: 47
**Critical**: 12 | **High**: 8 | **Medium**: 17 | **Low**: 10

---

## CRITICAL ISSUES (P0 - Must Fix This Week)

### ~~C1: Missing FastAPI Gateway Source Code~~ ✅ FALSE POSITIVE
**Resolution**: File exists at `infrastructure/vps/fastapi_gateway.py` (verified 2026-01-10)
**Status**: ✅ RESOLVED

### ~~C2: Missing Embedding Service Code~~ ✅ FALSE POSITIVE
**Resolution**: File exists at `infrastructure/vps/embedding_service.py` (verified 2026-01-10)
**Status**: ✅ RESOLVED

### ~~C3: Missing Core Memory Search Module~~ ✅ FALSE POSITIVE
**Resolution**: File exists at `core/memory/scripts/search.py` (verified 2026-01-10)
**Status**: ✅ RESOLVED

### ~~C4: Missing Core Memory Embeddings Module~~ ✅ FALSE POSITIVE
**Resolution**: File exists at `core/memory/scripts/embeddings.py` (verified 2026-01-10)
**Status**: ✅ RESOLVED

### ~~C5: Missing dyad.md State File~~ ✅ FALSE POSITIVE
**Resolution**: File exists at `core/daemon/dyad.md`, updated by session_start hook (verified 2026-01-10)
**Status**: ✅ RESOLVED

### C6: Cloudflare API Authentication Failure
**Impact**: Workers deployment blocked for checkpoint API
**Affected Files**:
- `infrastructure/cloudflare/checkpoint-api/DEPLOYMENT_STEPS.md:29` (token verification failed)
- `.mcp.json` (hostinger-api MCP likely uses same invalid tokens)
**Action**: Execute `wrangler login` interactive auth OR regenerate API tokens
**Effort**: 30 minutes
**Owner**: Captain (requires Cloudflare dashboard access)
**Status**: 🔴 BLOCKING

### ~~C7: Missing Cloudflare Schema SQL~~ ✅ FALSE POSITIVE
**Resolution**: File exists at `infrastructure/cloudflare/checkpoint-api/schema.sql` (verified 2026-01-10)
- Comprehensive D1 schema with graduated context layers, HAIST scoring
**Status**: ✅ RESOLVED

### ~~C8: Missing Cloudflare wrangler.toml~~ ✅ FALSE POSITIVE
**Resolution**: File exists at `infrastructure/cloudflare/checkpoint-api/wrangler.toml` (verified 2026-01-10)
**Status**: ✅ RESOLVED

### ~~C9: CLAUDE.md Severely Outdated~~ ✅ COMPLETED
**Resolution**: Comprehensively updated CLAUDE.md with current architecture (2026-01-10)
- Added daemon, hooks, telos, patterns, VPS, Cloudflare sections
- Documented n8n → Cloudflare Workers migration
- Corrected Hummingbot → Fathom architecture
- Updated version 0.1.0 → 0.2.0, last updated Dec 17 → Jan 10
**Status**: ✅ RESOLVED

### ~~C10: Skill Router Dependencies Not Installed~~ ✅ COMPLETED
**Resolution**: Created `core/skills/router/requirements.txt` with dependencies (2026-01-10)
- sentence-transformers, PyYAML, numpy
- Includes optional performance optimizations
**Status**: ✅ RESOLVED (installation pending)

### ~~C11: memory-mcp Not in .mcp.json~~ ✅ COMPLETED
**Resolution**: Added memory-mcp server configuration to .mcp.json (2026-01-10)
- Command: python with server.py path
- Env: QDRANT_HOST, QDRANT_PORT, COLLECTION_NAME
**Status**: ✅ RESOLVED

### ~~C12: VPS Identity Crisis~~ ✅ RESOLVED
**Resolution**: Created `docs/infrastructure/VPS_DUAL_DEPLOYMENT_CLARIFIED.md` (2026-01-10)
- Documented dual VPS topology: Hostinger (72.62.81.128) for legacy trading, Hetzner (95.217.51.24) for Cloudflare Workers support
- NOT a migration - intentional dual deployment for separation of concerns
**Impact**: Deployment confusion, unclear service ownership
**Affected Files**:
- `docs/architecture/cloud_deployment_topology.md` (claims 72.62.81.128)
- `docs/infrastructure/VPS_INTEGRATION_REVIEW_20260110.md` (shows 95.217.51.24)
- `docs/architecture/deployment_summary_20260103.md` (references 72.62.81.128)
**Action**: Clarify if same VPS or two instances, update all docs consistently
**Effort**: 1 hour (investigation + doc updates)
**Owner**: Captain (requires VPS access verification)
**Status**: 🔴 CRITICAL INCONSISTENCY

---

## HIGH-PRIORITY ISSUES (P1 - Address Within 2 Weeks)

### H1: Trading Domain Fragmentation
**Score**: 62/100
**Affected Components**:
- `domains/trading/fathom/` (Phase 1/6 complete, foundation only)
- `domains/trading/fathom_commander/` (27 tools, isolated)
- `domains/trading/strategic_intelligence/` (deployed but not connected to FC)
**Action**: Document integration architecture, implement SIL→FC→Fathom path
**Effort**: 6-8 hours
**Owner**: Captain (architecture) + First Mate (implementation)
**Status**: 🟠 ARCHITECTURAL

### H2: Infrastructure Documentation Drift
**Score**: 68/100
**Affected Files**:
- `docs/architecture/cloud_deployment_topology.md` (pre-VPS migration)
- `docs/architecture/strategic_intelligence_layer.md` (45% accuracy - design vs reality gap)
- `docs/architecture/vectorized_memory_architecture.md` (75% - doesn't account for dual Qdrant)
**Action**: Create VPS_INFRASTRUCTURE_20260110_FINAL.md, update cloud_deployment_topology.md
**Effort**: 3-4 hours
**Owner**: First Mate
**Status**: 🟠 DOCUMENTATION

### H3: Memory System Journal Stale
**Score**: 86.5/100 overall, journal.md at 20%
**Affected Files**:
- `core/memory/journal.md` (last entry Dec 25, now Jan 10 = 16 days behind)
**Action**: Update with Dec 26 - Jan 10 sessions, implement auto-update via session_end hook
**Effort**: 1 hour manual + 2 hours automation
**Owner**: First Mate
**Status**: 🟠 MAINTENANCE

### H4: Schema Version Inconsistency
**Affected Files**:
- 18 of 29 checkpoints missing explicit `schema_version` field
- `core/memory/session_schema.yaml` defines v1.0.0 but many don't declare
**Action**: Add `schema_version: 1.0.0` to all pre-Jan-2 checkpoints
**Effort**: 30 minutes (bulk edit)
**Owner**: First Mate
**Status**: 🟠 STANDARDIZATION

### H5: Export/Migration Scripts Hardcoded Paths
**Affected Files**:
- `import_memory.py:6` (hardcoded `/docker/rhiz/memory_export.json`)
- `migrate_memory.py:12-13` (hardcoded localhost:6333 and 72.62.81.128:6333)
- `export_memory.sh:3` (hardcoded `/mnt/c/Users/dread/...`)
**Action**: Parameterize via environment variables or CLI args
**Effort**: 1-2 hours
**Owner**: First Mate
**Status**: 🟠 MAINTAINABILITY

### H6: n8n Workflows Failing (Cloudflare Migration Incomplete)
**Affected Files**:
- 10 Fathom Commander workflows in `domains/trading/fathom_commander/n8n/` (502 errors)
- 3 SIL workflows in `domains/trading/strategic_intelligence/n8n_workflows/` (may be failing)
- `docs/architecture/deployment_summary_20260103.md` (documents 502 Bad Gateway for all workflows)
**Action**: Complete Cloudflare Workers migration OR deploy Fathom Commander to fix n8n
**Effort**: 4-6 hours
**Owner**: Captain (architecture decision) + First Mate (implementation)
**Status**: 🟠 OPERATIONAL

### H7: Telos Document Incomplete
**Score**: 70% template, 30% content
**Affected Files**:
- `core/telos/rhiz_telos.md:192` (marked "Awaiting Captain data")
- Sections P1-P3, M1-M2, K1-K7 unfilled
**Action**: Captain completes problems, mission, KPIs (1-2 hour session)
**Effort**: 1-2 hours (Captain) + 30 min (First Mate for KPI extraction)
**Owner**: Captain
**Status**: 🟠 FOUNDATIONAL

### H8: root/.gitignore - Add Cleanup Patterns
**Affected Files**:
- `.gitignore:225` (comprehensive but missing malformed file patterns)
**Action**: Add patterns for `=*.*`, `nul`, `User*` temp files
**Effort**: 5 minutes
**Owner**: First Mate
**Status**: 🟠 HYGIENE

---

## MEDIUM-PRIORITY ISSUES (P2 - Next Month)

### M1: Consolidate Documentation Directories
**Affected**:
- `docs/infrastructure/` (5 files) → merge to `docs/architecture/`
- `docs/specifications/` (1 file) → merge to `docs/architecture/`
- `docs/evaluation/` (1 YAML + scores/) → create `docs/metrics/` or consolidate
- `docs/handoffs/` (1 file) → merge to `docs/sessions/`
**Effort**: 2 hours
**Status**: 🟡 ORGANIZATION

### M2: External Repository Pruning
**Affected**:
- `external/pytorch-main` (211 MB) - Archive to cold storage
- `external/tensorflow-master` (451 MB) - Archive
- `external/langflow-main` (170 MB) - Archive
- `external/ai-through-symbiosis-master` (2.1 GB) - Extract summary, archive
**Effort**: 2 hours (archiving) + 2 hours (summary extraction)
**Status**: 🟡 DISK SPACE

### M3: Gifts_From_Alex Organization
**Affected**:
- `Gifts_From_Alex/` (2.7 GB, no manifest)
**Action**: Create README.md, reorganize into research_foundations/ + reference_repos/
**Effort**: 1 hour
**Status**: 🟡 ORGANIZATION

### M4: Create Operational Runbook
**Missing**: Daily health check procedures, troubleshooting, rollback
**Action**: Create `docs/guides/OPERATIONAL_RUNBOOK.md`
**Effort**: 3 hours
**Status**: 🟡 DOCUMENTATION

### M5: Pattern Usage Metrics Low
**Issue**: pattern_usage_count: 2, decision_trace: 3 uses across 39 sessions
**Affected**: `core/daemon/dyad.md:metrics`
**Action**: Review if patterns implicitly used, add logging/hooks to auto-track
**Effort**: 2 hours
**Status**: 🟡 OBSERVABILITY

### M6: session_open vs. session_handshake Redundancy
**Affected**:
- `core/patterns/dyad/session_handshake.md` (v1.0.0)
- `core/patterns/dyad/session_open.md` (v2.0.0, tool-integrated)
**Action**: Clarify canonical version, deprecate or consolidate
**Effort**: 30 minutes
**Status**: 🟡 CLARITY

### M7: core/daemon/mcp-server/ Empty Directory
**Affected**: `core/daemon/mcp-server/` (0 files, no README)
**Action**: Add README explaining purpose OR remove if not needed
**Effort**: 15 minutes
**Status**: 🟡 DOCUMENTATION

### M8: memory-mcp requirements.txt Missing pydantic
**Affected**: `tools/memory-mcp/requirements.txt` (MCP requires pydantic but not listed)
**Action**: Add `pydantic>=2.12.0` to requirements
**Effort**: 5 minutes
**Status**: 🟡 DEPENDENCIES

### M9: MCP Version Mismatch
**Issue**: rhiz-mcp uses mcp>=1.25.0, memory-mcp uses mcp>=0.9.0
**Affected**:
- `tools/rhiz-mcp/requirements.txt:1`
- `tools/memory-mcp/requirements.txt:1`
**Action**: Standardize on mcp==1.25.0
**Effort**: 5 minutes
**Status**: 🟡 CONSISTENCY

### M10: Checkpoint Directory May Not Exist
**Affected**: `core/memory/checkpoints/` (created on first write but parent dirs might not exist)
**Action**: Add directory creation to checkpoint_manager.py or init script
**Effort**: 15 minutes
**Status**: 🟡 ROBUSTNESS

### M11: No Session Hooks Implemented
**Expected**:
- `core/hooks/session_start.py` (auto-load context)
- `core/hooks/session_end.py` (auto-save checkpoint)
**Status**: Directories exist, no code
**Action**: Implement session lifecycle automation
**Effort**: 3-4 hours
**Status**: 🟡 AUTOMATION

### M12: Mooncheck Workflow Iterations (9 versions)
**Affected**: `docs/blog/mooncheck_*.json` (9 files, only 1 production)
**Action**: Archive 8 dev iterations to `docs/archive/mooncheck_iterations_dev/`
**Effort**: 15 minutes
**Status**: 🟡 CLEANUP

### M13: SKILL_ROUTER_GUIDE.md Minor Discrepancies
**Affected**:
- Line 81-82: Uses `/mnt/c/` path (WSL) instead of `C:\` (Windows)
- Line 236: Says "(Load skill for patterns)" but actual patterns exist
**Action**: Update paths to Windows-native, expand portfolio_assessment docs
**Effort**: 30 minutes
**Status**: 🟡 DOCUMENTATION

### M14: Hummingbot References in Old Docs
**Affected**:
- `docs/sessions/aar_20251226_christmas_continuation.md`
- `docs/sessions/first_mate_autonomous_observations_20251221.md`
- `docs/architecture/INFRASTRUCTURE_EXPANSION.md`
**Action**: Add deprecation notices, clarify Fathom replaced Hummingbot
**Effort**: 1 hour
**Status**: 🟡 CLEANUP

### M15: Strategic Intelligence Layer Implementation Gap
**Issue**: strategic_intelligence_layer.md describes as "ready for implementation" but code exists
**Affected**: `docs/architecture/strategic_intelligence_layer.md` (45% accuracy)
**Action**: Add implementation status section, mark designed vs. implemented
**Effort**: 1 hour
**Status**: 🟡 ACCURACY

### M16: Dual Qdrant Collections Not Documented
**Issue**: `rhiz_memories` vs. `moonchecks` collections not explained
**Affected**: `docs/architecture/vectorized_memory_architecture.md`
**Action**: Document collection fragmentation strategy
**Effort**: 30 minutes
**Status**: 🟡 ARCHITECTURE

### M17: Future_Roadmap.md Outdated
**Affected**: `docs/research/Future_Roadmap.md` (last updated Dec 15)
**Action**: Update with Wave 3-4 completion status, revise timeline
**Effort**: 1-2 hours
**Status**: 🟡 STRATEGIC

---

## LOW-PRIORITY ISSUES (P3 - Nice to Have)

### L1: Root Directory Cleanup
**Affected**: `=2.2.0`, `nul`, `scroll_request.json` (malformed artifacts)
**Effort**: 2 minutes
**Status**: 🟢 TRIVIAL

### L2: Temp Workflow JSON Files
**Affected**: `UsersdreadAppDataLocalTemp*.json` (2 files with malformed names)
**Action**: Move to docs/archive or delete
**Effort**: 5 minutes
**Status**: 🟢 CLEANUP

### L3: memory_export.json Assessment
**Affected**: `memory_export.json` (153 KB, likely legacy)
**Action**: Verify if in use, delete if not
**Effort**: 10 minutes
**Status**: 🟢 CLEANUP

### L4: venv Size Documentation
**Issue**: 7.2 GB venv (mostly torch) but not explained
**Action**: Add note to CLAUDE.md or README about expected size
**Effort**: 5 minutes
**Status**: 🟢 DOCUMENTATION

### L5: empty scroll_request.json Reference
**Affected**: `export_memory.sh:3` (references scroll_request.json which is empty)
**Action**: Fix script or remove file
**Effort**: 10 minutes
**Status**: 🟢 CONSISTENCY

### L6: Claude_Grooves Integration Documentation
**Affected**: Music project in Rhiz repo but not explained in CLAUDE.md
**Action**: Add Claude_Grooves/README.md, update CLAUDE.md with note
**Effort**: 30 minutes
**Status**: 🟢 CLARITY

### L7: permaculture-ai-cloudflare Misplacement
**Affected**: Separate .git repo inside rhiz_localdev (nested repo conflict)
**Action**: Move to separate directory outside Rhiz
**Effort**: 15 minutes
**Status**: 🟢 STRUCTURE

### L8: Timestamp Format Inconsistency (2 checkpoints)
**Affected**: 2 checkpoints use `YYYY-MM-DD ~HH:MM CST` instead of ISO 8601
**Action**: Normalize to ISO format
**Effort**: 15 minutes
**Status**: 🟢 STANDARDIZATION

### L9: Captain State Last Active 4 Days Ago
**Issue**: dyad.md shows Captain last active 2026-01-06, now Jan 10 (4-day gap)
**Action**: Update after this session, track expected cadence
**Effort**: Auto-updated
**Status**: 🟢 MONITORING

### L10: Research Directory Population
**Issue**: `docs/research/` expected to have more content based on volume of research
**Action**: Verify all research docs present, add missing if needed
**Effort**: 30 minutes
**Status**: 🟢 VERIFICATION

---

## SUMMARY STATISTICS

| Priority | Count | Est. Total Effort |
|----------|-------|-------------------|
| P0 Critical | 12 | 15-20 hours |
| P1 High | 8 | 18-24 hours |
| P2 Medium | 17 | 22-28 hours |
| P3 Low | 10 | 3-4 hours |
| **TOTAL** | **47** | **58-76 hours** |

---

## ISSUE OWNERSHIP BREAKDOWN

| Owner | Critical | High | Medium | Low | Total |
|-------|----------|------|--------|-----|-------|
| First Mate | 8 | 4 | 13 | 8 | 33 |
| Captain | 3 | 2 | 1 | 0 | 6 |
| Either | 1 | 2 | 3 | 2 | 8 |

---

## RECOMMENDED EXECUTION ORDER

### BATCH 1 (Day 1, ~4 hours)
- C5: Initialize dyad.md (15 min)
- C10: Install skill router dependencies (30 min)
- C11: Add memory-mcp to .mcp.json (15 min)
- L1: Clean root directory artifacts (2 min)
- C9: Update CLAUDE.md (2-3 hours)

### BATCH 2 (Day 2, ~6 hours)
- C3: Implement search.py (3-4 hours)
- C4: Implement embeddings.py (2-3 hours)

### BATCH 3 (Day 3, ~6 hours)
- C1: Restore/recreate fastapi_gateway.py (2-3 hours)
- C2: Restore/recreate embedding_service.py (1-2 hours)
- C7: Create Cloudflare schema.sql (1 hour)
- C8: Create wrangler.toml (30 min)

### BATCH 4 (Week 2, Captain Session, ~3 hours)
- C6: Fix Cloudflare auth (30 min)
- C12: Clarify VPS identity (1 hour)
- H7: Complete Telos (1-2 hours)

### BATCH 5 (Week 2, ~8 hours)
- H2: Update infrastructure docs (3-4 hours)
- H3: Update memory journal (1 hour + 2 hours automation)
- H1: Document trading integration (planning session, 2 hours)

---

**Last Updated**: 2026-01-10T22:00:00Z
**Next Review**: 2026-01-17 (after Week 1 batch completion)
