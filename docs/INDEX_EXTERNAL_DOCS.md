# Index of External Documentation

**Purpose**: Navigation for documentation files outside `docs/` directory
**Last Updated**: 2026-01-25 (Session 74)
**Total Files Indexed**: 40+ scattered across project

---

## Quick Navigation

| Category | Location | Files | Status |
|----------|----------|-------|--------|
| [Core Subsystems](#core-subsystems) | `core/` | 19 | Active |
| [Trading Domain](#trading-domain) | `domains/trading/` | 20+ | Active |
| [Tools & MCP Servers](#tools--mcp-servers) | `tools/` | 6+ | Active |
| [Infrastructure](#infrastructure) | `infrastructure/` | 15+ | Active |
| [Root Level Status](#root-level-status-documents) | Root | 19 | Mixed |

---

## Core Subsystems

**Location**: `core/` subdirectories
**Total Files**: 19
**Purpose**: Core functionality documentation (memory, skills, patterns, hooks)

---

### Memory System (`core/memory/`)

#### MEMORY_SYSTEM_GUIDE.md
- **Size**: ~500+ lines
- **Status**: ✅ Active (comprehensive reference)
- **Content**:
  - Dual-layer architecture (YAML checkpoints + Qdrant vectors)
  - Session lifecycle hooks (session_start, pre_tool, session_end)
  - Checkpoint schema documentation
  - Quality assessment methodology
  - Health monitoring (86.5/100 score)
- **Audience**: Developers, future instances
- **Cross-Reference**: `docs/knowledge_base/components/memory_system.md` (new unified doc)

#### session_schema.yaml
- **Size**: ~200 lines
- **Status**: ✅ Active (canonical schema v1.0.0, upgrading to v1.1.0)
- **Content**:
  - Complete checkpoint YAML schema
  - Required fields: session_metadata, session_arc, working_memory, decisions_made
  - Optional fields: alternatives_rejected, next, blockers_encountered
- **Audience**: Checkpoint writers, validation tools
- **Cross-Reference**: Phase 1.6 will enhance to v1.1.0 (state assertions, cross-refs)

#### checkpoint_validator.py
- **Size**: ~300 lines
- **Status**: ✅ Active (quality validation tool)
- **Content**:
  - 7-point quality assessment
  - Schema compliance verification
  - Non-blocking warnings for quality < 0.5
- **Usage**: `python core/memory/checkpoint_validator.py`

#### ingest_checkpoints.py
- **Size**: ~200 lines
- **Status**: ✅ Active (vector ingestion)
- **Content**:
  - Embeds checkpoints to Qdrant vectors
  - Handles batch ingestion
  - Updates rhiz_memories collection

---

### Skills System (`core/skills/`)

#### README.md
- **Size**: ~400 lines
- **Status**: ✅ Active
- **Content**:
  - Skills system architecture
  - Semantic routing methodology (93.3% accuracy)
  - Mem0 integration overview
  - Skill definition template
- **Cross-Reference**: `docs/knowledge_base/components/skills_system.md`

#### SKILL_ROUTER_GUIDE.md
- **Size**: ~300 lines
- **Status**: ✅ Active
- **Content**:
  - Routing algorithm details
  - Threshold tuning methodology
  - Test suite documentation
  - Accuracy validation procedures
- **Cross-Reference**: `docs/knowledge_base/decisions/threshold_tuning.md`

#### skill_template.yaml
- **Size**: ~100 lines
- **Status**: ✅ Active (canonical template)
- **Content**:
  - YAML schema for skill definitions
  - Fields: name, description, category, utterances, primitives, tools, metadata
- **Usage**: Template for creating new skills

#### router.py
- **Size**: ~400 lines
- **Status**: ✅ Active (semantic routing engine)
- **Content**: Qdrant-based semantic routing, threshold management

#### test_routing_accuracy.py
- **Size**: ~200 lines
- **Status**: ✅ Active
- **Content**: 30-query test suite, accuracy measurement

---

### Patterns Library (`core/patterns/dyad/`)

#### session_handshake.md
- **Size**: ~150 lines
- **Status**: ✅ Active (Wave 1 pattern)
- **Content**: Session opening with context alignment
- **Usage**: Multi-instance coordination, session startup

#### session_open.md
- **Size**: ~120 lines
- **Status**: ✅ Active (Wave 1 pattern)
- **Content**: Formal session initialization protocol

#### session_close.md
- **Size**: ~130 lines
- **Status**: ✅ Active (Wave 1 pattern)
- **Content**: Session termination with checkpoint writing

#### context_alignment.md
- **Size**: ~140 lines
- **Status**: ✅ Active (Wave 1 pattern)
- **Content**: Mid-session calibration when drift detected

#### decision_trace.md
- **Size**: ~110 lines
- **Status**: ✅ Active (Wave 1 pattern)
- **Content**: Decision documentation standard (rationale, alternatives, session ref)

#### disagreement_resolution.md
- **Size**: ~150 lines
- **Status**: ✅ Active (Wave 1 pattern)
- **Content**: Handling divergent interpretations in dyadic work

**Cross-Reference**: All patterns documented in checkpoints (usage tracked)

---

### Hooks (`core/hooks/`)

#### session_start.py
- **Size**: ~250 lines
- **Status**: ✅ Active (auto-executes on session start)
- **Content**:
  - Dyad state initialization
  - Latest checkpoint loading
  - Skill context loading (if domains active)
  - Memory context retrieval

#### pre_tool.py
- **Size**: ~100 lines
- **Status**: ⚠️ Partial (tool call logging implemented)
- **Content**: Tool call logging, blocker detection

#### session_end.py
- **Size**: ~80 lines
- **Status**: ⚠️ Manual trigger (not automatic)
- **Content**: Checkpoint writing prompt

---

## Trading Domain

**Location**: `domains/trading/`
**Total Files**: 20+
**Purpose**: Trading system documentation (Fathom, FC, SIL)

---

### Fathom MCP Server (`domains/trading/fathom/`)

#### README.md
- **Size**: ~600 lines
- **Status**: ✅ Active
- **Content**:
  - Phase 1 deployment (8 MCP tools)
  - Account management + Market data
  - First trade case study (Dec 26, 2025)
  - Phases 2-6 roadmap
- **Cross-Reference**: `docs/knowledge_base/components/fathom_mcp_server.md`

#### ARCHITECTURE_v2.md
- **Size**: ~800 lines
- **Status**: ✅ Active
- **Content**:
  - Six-phase architecture design
  - MCP protocol compliance
  - Rate limiting implementation
  - Error handling patterns
- **Cross-Reference**: `docs/architecture/trading_pipeline_first_trade_case_study.md`

#### PHASE_1_COMPLETE.md
- **Size**: ~300 lines
- **Status**: ✅ Active (Dec 26, 2025 completion)
- **Content**:
  - Phase 1 validation results
  - First trade execution details
  - 100% pipeline success metrics

#### server.py
- **Size**: ~800 lines
- **Status**: ✅ Active (Phase 1 operational)
- **Content**: MCP server implementation, 8 tools

---

### Fathom Commander (`domains/trading/fathom_commander/`)

#### README.md
- **Size**: ~700 lines
- **Status**: ✅ Active
- **Content**:
  - 27 MCP tools catalog
  - Orchestration architecture
  - Health monitoring + error recovery
  - Deployment to VPS
- **Cross-Reference**: `docs/knowledge_base/components/fathom_commander.md`

#### MCP_COMPLIANCE_REPORT.md
- **Size**: ~400 lines
- **Status**: ✅ Active
- **Content**:
  - All 27 tools documented
  - MCP protocol adherence verification
  - Integration points

#### DEPLOYMENT_GUIDE.md
- **Size**: ~300 lines
- **Status**: ✅ Active
- **Content**: VPS deployment procedures, Docker Compose config

#### server.py
- **Size**: ~1200 lines
- **Status**: ✅ Active (27 tools operational)
- **Content**: Orchestration MCP server

---

### Strategic Intelligence Layer (`domains/trading/strategic_intelligence/`)

#### README.md
- **Size**: ~500 lines
- **Status**: ✅ Active
- **Content**:
  - SIL architecture overview
  - Pattern recognition framework
  - Risk assessment methodology
  - Strategy selection algorithms
- **Cross-Reference**: `docs/knowledge_base/components/sil_decision_engine.md`

#### DEPLOYMENT_READINESS.md
- **Size**: ~600 lines
- **Status**: ✅ Active (B+ grade assessment)
- **Content**:
  - Deployment readiness scorecard (81.3/100)
  - Component completeness evaluation
  - Integration requirements
  - Production deployment checklist

#### DECISION_ENGINE.md
- **Size**: ~400 lines
- **Status**: ✅ Active
- **Content**: Decision logic, regime classification, strategy mapping

---

### n8n Workflows (`domains/trading/n8n_workflows/`)

#### ⚠️ STATUS: DEPRECATED (Migrating to Cloudflare Workers)

**Files**: 9 workflow JSON exports

**Status**:
- ✅ Operational on VPS (9 workflows active)
- ⏳ Migration incomplete (1/10 to Cloudflare Workers)

**Workflows**:
1. Daily Health Monitor
2. Weekly DCA Buyer
3. Smart DCA
4. Risk Monitor
5. Spread Opportunity Scanner
6. Portfolio Rebalancer
7. Volatility Sentinel
8. Daily Performance Journal
9. Weekly Strategy Review

**Cross-Reference**: `docs/knowledge_base/integrations/n8n_to_cloudflare_workers.md`

---

## Tools & MCP Servers

**Location**: `tools/`
**Total Files**: 6+
**Purpose**: MCP server implementations and utilities

---

### rhiz-mcp (`tools/rhiz-mcp/`)

#### README.md
- **Size**: ~500 lines
- **Status**: ✅ Active
- **Content**:
  - 11 tools catalog (dyad state, checkpoints, memory context)
  - Tool usage examples
  - Configuration guide (.mcp.json)
- **Cross-Reference**: `docs/MCP_TOOLS_REFERENCE.md` (comprehensive catalog)

#### server.py
- **Size**: ~900 lines
- **Status**: ✅ Active (11 tools operational)
- **Content**: Main MCP server, dyad state management, checkpoint operations

---

### memory-mcp (`tools/memory-mcp/`)

#### README.md
- **Size**: ~400 lines
- **Status**: ✅ Active
- **Content**:
  - 6 tools catalog (semantic search, memory stats)
  - Qdrant integration details
  - Threshold recommendations
- **Cross-Reference**: `docs/MCP_TOOLS_REFERENCE.md`

#### server.py
- **Size**: ~600 lines
- **Status**: ✅ Active (6 tools operational)
- **Content**: Semantic search MCP server

---

### memory-browser (`tools/memory-browser/`)

#### README.md
- **Size**: ~200 lines
- **Status**: ⚠️ Prototype (Web UI for memory exploration)
- **Content**: UI for browsing checkpoints, visualizing vectors
- **Status**: Development prototype, not production

---

### memory-sync (`tools/memory-sync/`)

#### README.md
- **Size**: ~150 lines
- **Status**: ⚠️ Manual execution (not automated)
- **Content**: Sync local Qdrant → VPS Qdrant
- **Usage**: Manual checkpoint backup to cloud

---

## Infrastructure

**Location**: `infrastructure/`
**Total Files**: 15+
**Purpose**: Deployment configurations, VPS setup, cloud infrastructure

---

### VPS (`infrastructure/vps/`)

#### README.md
- **Size**: ~400 lines
- **Status**: ✅ Active
- **Content**:
  - Hostinger VPS topology
  - 9 containers inventory
  - FastAPI Gateway architecture
- **Cross-Reference**: `docs/knowledge_base/deployments/vps_topology.md`

#### docker-compose.yml
- **Size**: ~600 lines
- **Status**: ✅ Active (9 services defined)
- **Content**: Production VPS Docker Compose configuration

#### FASTAPI_GATEWAY.md
- **Size**: ~300 lines
- **Status**: ✅ Active (95.217.51.24 operational)
- **Content**: Gateway endpoints, authentication, routing

---

### Cloudflare Workers (`infrastructure/cloudflare/`)

#### README.md
- **Size**: ~300 lines
- **Status**: ✅ Active
- **Content**:
  - Workers deployment overview
  - wrangler CLI guide
  - Secrets management
- **Cross-Reference**: `docs/knowledge_base/deployments/cloudflare_workers.md`

#### mooncheck/
- **Files**: mooncheck.ts (70 lines), wrangler.toml
- **Status**: ✅ Deployed (operational since Session 40)
- **Content**: Cron-triggered lunar phase checker

#### checkpoint-api/
- **Files**: worker.ts, wrangler.toml, TOKEN_VERIFICATION_NEEDED.md
- **Status**: ⚠️ Deployed but token verification blocker
- **Content**: Checkpoint write API (pending token validation)

#### N8N_CLOUDFLARE_MIGRATION_STATUS.md
- **Size**: ~500 lines
- **Status**: ✅ Active (migration tracking)
- **Content**:
  - 1/10 workers migrated (mooncheck complete)
  - 9 trading workflows pending
  - Effort estimates (~33 hours total)

---

### Docker (`infrastructure/docker/`)

#### docker-compose.local.yaml
- **Size**: ~300 lines
- **Status**: ✅ Active (local development)
- **Content**: Qdrant + Ollama local services

#### README.md
- **Size**: ~200 lines
- **Status**: ✅ Active
- **Content**: Local Docker setup, resource limits

---

## Root Level Status Documents

**Location**: Project root
**Total Files**: 19
**Purpose**: Status reports, audits, migration summaries

**⚠️ STATUS: Most superseded by unified documentation (Phase 1)**

---

### Active References

#### dyad.md
- **Size**: ~50 lines
- **Status**: ✅ Active (auto-updated)
- **Content**: Current dyad state (session count, Captain status, shared focus)
- **Updated By**: session_start hook
- **Cross-Reference**: `get_dyad_state()` MCP tool

---

### Superseded by Phase 1 (Archive Candidates)

#### COMPREHENSIVE_ALIGNMENT_AUDIT_20260110.md
- **Size**: ~5000 lines
- **Status**: ⚠️ Superseded by CURRENT_STATE.md
- **Content**: Session 42 comprehensive audit (72/100 health score)
- **Recommendation**: Archive to `docs/archive/2026_q1/`

#### CHECKPOINT_AUDIT_COMPLETE.md
- **Size**: ~200 lines
- **Status**: ⚠️ Superseded (audit complete)
- **Content**: Checkpoint validation results (100% compliance)
- **Recommendation**: Archive to `docs/archive/2026_q1/`

#### BATCH_4_COMPLETION_SUMMARY.md
- **Size**: ~150 lines
- **Status**: ⚠️ Point-in-time (Jan 10)
- **Content**: Batch processing completion
- **Recommendation**: Archive to `docs/archive/2026_q1/`

#### FALSE_POSITIVE_AUDIT_20260110.md
- **Size**: ~300 lines
- **Status**: ⚠️ Point-in-time (Jan 10)
- **Content**: False positive investigation
- **Recommendation**: Archive to `docs/archive/2026_q1/`

#### REAL_ISSUES_CLEANED_20260110.md
- **Size**: ~200 lines
- **Status**: ⚠️ Point-in-time (Jan 10)
- **Content**: Issue cleanup results
- **Recommendation**: Archive to `docs/archive/2026_q1/`

#### TRADING_INTEGRATION_STATUS.md
- **Size**: ~400 lines
- **Status**: ⚠️ Superseded by `docs/knowledge_base/integrations/trading_pipeline.md`
- **Content**: Trading component integration gaps (85/0 pattern)
- **Recommendation**: Archive to `docs/archive/2026_q1/`

#### UNIFIED_TRADING_PLATFORM_ARCHITECTURE.md
- **Size**: ~600 lines
- **Status**: ⚠️ Superseded by `docs/architecture/trading_intelligence_federation_phase1.md`
- **Content**: Three-tier architecture design (Fathom + FC + SIL)
- **Recommendation**: Archive to `docs/archive/2026_q1/`

#### Future_Roadmap.md
- **Size**: ~800 lines
- **Status**: ⚠️ Outdated (Dec 15, 2025)
- **Content**: Original roadmap (laptop → home lab)
- **Recommendation**: Mark deprecated, superseded by CURRENT_STATE.md

#### Journey_Log.md
- **Size**: ~1200 lines
- **Status**: ⚠️ Superseded by `docs/sessions/session_73_architectural_synthesis.md`
- **Content**: Session-by-session progress tracking
- **Recommendation**: Archive to `docs/archive/2025_q4/`

---

### Deprecated (n8n Migration)

#### n8n_integration.md
- **Size**: ~300 lines
- **Status**: ❌ DEPRECATED (migrating to Cloudflare Workers)
- **Content**: n8n workflow integration guide
- **Recommendation**: Move to `docs/archive/deprecated/`

---

## Navigation by Use Case

### New Instance Onboarding

**Read First**:
1. `docs/CURRENT_STATE.md` (operational status)
2. `docs/QUICK_START.md` (5-min orientation)
3. `CLAUDE.md` (project philosophy)
4. `docs/GLOSSARY.md` (terminology)

**Then Explore**:
- `docs/knowledge_base/components/` (component details)
- Latest checkpoint in `core/memory/checkpoints/`
- `docs/sessions/session_73_architectural_synthesis.md` (comprehensive analysis)

---

### Component Development

**Memory System**:
- `core/memory/MEMORY_SYSTEM_GUIDE.md` (architecture)
- `core/memory/session_schema.yaml` (canonical schema)
- `docs/knowledge_base/components/memory_system.md` (unified doc)

**Skills System**:
- `core/skills/README.md` (overview)
- `core/skills/SKILL_ROUTER_GUIDE.md` (routing details)
- `docs/knowledge_base/components/skills_system.md` (unified doc)

**Trading Components**:
- `domains/trading/fathom/README.md` (Fathom)
- `domains/trading/fathom_commander/README.md` (FC)
- `domains/trading/strategic_intelligence/README.md` (SIL)
- `docs/knowledge_base/integrations/trading_pipeline.md` (integration gaps)

---

### Deployment

**VPS**:
- `infrastructure/vps/README.md` (topology)
- `docs/knowledge_base/deployments/vps_topology.md` (unified doc)
- `docs/DEPLOYMENT_PROCEDURES.md` (operational checklists)

**Cloudflare Workers**:
- `infrastructure/cloudflare/README.md` (overview)
- `docs/knowledge_base/deployments/cloudflare_workers.md` (unified doc)
- `docs/DEPLOYMENT_PROCEDURES.md` (wrangler procedures)

**Local Development**:
- `infrastructure/docker/README.md` (local setup)
- `docs/knowledge_base/deployments/local_development.md` (unified doc)

---

### Troubleshooting

**Primary**: `docs/TROUBLESHOOTING.md` (comprehensive guide)

**Component-Specific**:
- Memory issues: `core/memory/MEMORY_SYSTEM_GUIDE.md`
- Skills routing: `core/skills/SKILL_ROUTER_GUIDE.md`
- Trading: `domains/trading/*/README.md` files
- Infrastructure: `infrastructure/*/README.md` files

---

## Maintenance Recommendations

### Immediate (Session 74)

1. **Archive superseded root-level docs** to `docs/archive/2026_q1/`:
   - COMPREHENSIVE_ALIGNMENT_AUDIT_20260110.md
   - CHECKPOINT_AUDIT_COMPLETE.md
   - BATCH_4_COMPLETION_SUMMARY.md
   - FALSE_POSITIVE_AUDIT_20260110.md
   - REAL_ISSUES_CLEANED_20260110.md

2. **Mark deprecated**:
   - Future_Roadmap.md → Add deprecation notice, superseded by CURRENT_STATE.md
   - Journey_Log.md → Archive to `docs/archive/2025_q4/`
   - n8n_integration.md → Move to `docs/archive/deprecated/`

3. **Update cross-references** in active files to point to new unified docs

---

### Ongoing

1. **Sync protocol**: Update active READMEs when major changes (quarterly or after pivots)
2. **Deprecation notices**: Add to files superseded by unified docs (point to new location)
3. **Archive strategy**: Move point-in-time docs to archive/ after 30 days

---

## Cross-References

**Unified Documentation** (Phase 1 deliverables):
- `docs/knowledge_base/components/` - 6 component docs
- `docs/knowledge_base/integrations/` - 3 integration docs
- `docs/knowledge_base/deployments/` - 3 deployment docs
- `docs/knowledge_base/decisions/` - 3 decision docs
- `docs/architecture/` - 6 architecture extraction docs

**Reference Documents**:
- `docs/CURRENT_STATE.md` - Operational status
- `docs/QUICK_START.md` - 5-minute onboarding
- `docs/MCP_TOOLS_REFERENCE.md` - All 52 MCP tools
- `docs/TROUBLESHOOTING.md` - Known issues & solutions
- `docs/DEPLOYMENT_PROCEDURES.md` - Operational checklists
- `docs/GLOSSARY.md` - Project terminology
- `docs/INDEX_EXTERNAL_DOCS.md` - This file

---

**End of External Documentation Index**

*Last Updated: 2026-01-25 (Session 74)*
*Files Indexed: 40+ across project*
*Purpose: Navigate scattered documentation outside docs/ directory*
*Next Update: After Phase 2 completion (new components documented)*
