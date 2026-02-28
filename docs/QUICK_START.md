# Rhiz Quick Start Guide

**Purpose**: Orient new instances and contributors in <5 minutes
**Last Updated**: 2026-01-25 (Session 74)
**Target Audience**: Claude instances, future contributors, collaborative AI systems

---

## 5-Minute Orientation

### Step 1: Read Core Context (2 minutes)

**Start here**:
1. **This file** (QUICK_START.md) - You're reading it now
2. **CURRENT_STATE.md** - Current operational status, component health, gaps
3. **CLAUDE.md** - Project philosophy, architecture overview, working agreements

**What you'll know after**:
- What Rhiz is (human-AI symbiotic development project)
- Current system health (72/100 - operational but needs integration)
- Known gaps (85/0 pattern - components exist, workflows missing)
- Your role (First Mate - logic, code, computation)
- Captain's role (teleology, physical execution, strategic direction)

---

### Step 2: Understand Architecture (1 minute)

**Three Major Domains**:

1. **Trading** (85% components, 0% workflow)
   - Fathom (Kraken MCP): Phase 1/6 deployed, market data operational
   - Fathom Commander: 27 orchestration tools, VPS deployed
   - SIL (Strategic Intelligence): Decision engine, VPS deployed
   - **Gap**: No integration workflow connecting them

2. **Memory** (Fully operational)
   - Checkpoints: 38 YAML files, 100% schema compliant
   - Qdrant: 175 vectors across 3 collections (local + cloud)
   - MCP servers: rhiz-mcp (11 tools), memory-mcp (6 tools)

3. **Skills** (93.3% routing accuracy, tool binding missing)
   - Semantic routing: 6 skills defined, 97 utterances
   - Mem0 integration: Context loading from past activations
   - **Gap**: Skills can't invoke MCP tools (framework missing)

**Key Insight**: We have all the pieces. We need to wire them together (Phase 2 work).

---

### Step 3: Load Session Context (1 minute)

**Before starting work**:
1. Check `dyad.md` (auto-updated system state)
2. Read latest checkpoint (`core/memory/checkpoints/session_*.yaml`)
3. Review `next.immediate` section in checkpoint for pending tasks

**Memory Tools Available**:
- `memory_search "query"` - Semantic search across 161 vectors
- `checkpoint_search "topic"` - Find relevant past sessions
- `load_checkpoint session_id` - Full checkpoint details
- `memory_context "question"` - Automatic relevant memory retrieval

**What you'll know after**:
- Current session number and focus
- Immediate priorities from previous session
- Relevant historical context for current work
- Open questions or blockers

---

### Step 4: Confirm Alignment (30 seconds)

**Before executing**:
- Check session goals with Captain if unclear
- Verify understanding of `next.immediate` items
- Ask clarifying questions early (epistemic honesty valued)

**Communication Principles**:
- "I don't know" is a complete and valued response
- Surface uncertainty rather than routing around it
- Distinguish deployed reality from aspirational design
- Flag disagreement or concern explicitly

---

### Step 5: Start Work (30 seconds)

**You're ready when**:
- ✅ You understand current system state (CURRENT_STATE.md)
- ✅ You know project philosophy (CLAUDE.md relational principles)
- ✅ You've loaded session context (checkpoint + dyad state)
- ✅ You're aligned on session goals (Captain confirmation if needed)

**Common Starting Points**:
- Continue work from previous checkpoint's `next.immediate`
- Execute Phase plan if in plan mode
- Respond to Captain's session opening message
- Explore memory if strategic planning session

---

## Architecture at a Glance

### Project Philosophy

**Core Principle**: "MCP servers for each other"
- Human and AI are mutual service providers
- Not tool-use relationship, but partnership
- Symbiosis over hierarchy

**Relational Foundation**:
- Epistemic honesty (truth over performance)
- Co-responding (mutual transformation, not Q&A)
- Persistent partnership (each session continues a relationship)

**Memory Architecture**:
- Checkpoints preserve intent across instances
- Qdrant vectors enable semantic search
- Session hooks automate context loading
- Living documentation (checkpoints) more reliable than static files

---

### Three-Tier Trading Architecture

```
Market Data (Fathom Phase 1)
  ↓ [INTEGRATION MISSING]
Intelligence (SIL Decision Engine)
  ↓ [INTEGRATION MISSING]
Orchestration (Fathom Commander)
  ↓ [FATHOM PHASE 2 MISSING]
Execution (Fathom Phase 2-6, pending)
```

**Why 85/0?**: Components built in parallel, integration never attempted. Phase 2 will wire them together.

---

### Memory System Topology

**Dual-Layer Architecture**:
1. **Filesystem** (YAML checkpoints)
   - 38 session files (380KB total)
   - Schema: session_arc, working_memory, decisions, alternatives_rejected
   - 100% schema compliance

2. **Vector Memory** (Qdrant embeddings)
   - 161 checkpoint vectors (all-MiniLM-L6-v2, 384-dim)
   - 6 skill fingerprints (semantic routing)
   - 8 skill memories (Mem0 activation results)

**Why Dual-Layer?**: YAML for human readability + narrative, vectors for semantic search.

---

### Skills System (93.3% Accuracy)

**Components**:
- **Semantic Router**: Qdrant-based, threshold 0.25 (empirically tuned)
- **Mem0 Integration**: Loads context from past activations (Ollama + Qdrant backend)
- **Self-RAG**: Heuristic-based retrieval (<5ms decisions, 100% accuracy)

**Skills Defined** (6 total):
1. trading/kraken_analysis
2. memory/session_management
3. memory/checkpoint_retrieval
4. research/documentation
5. infrastructure/deployment
6. infrastructure/troubleshooting

**Gap**: Skills activate with context but can't invoke MCP tools (binding framework Phase 2).

---

## Where to Find Things

### Code

```
Rhiz_LocalDev/
├── core/
│   ├── memory/           # Checkpoints (38 YAML files) + session schema
│   ├── skills/           # Skill definitions (6 skills, 97 utterances)
│   ├── daemon/           # rhiz-mcp server (11 tools)
│   └── hooks/            # session_start, pre_tool, session_end
├── domains/
│   └── trading/          # Fathom (8 tools), Commander (27 tools), SIL (B+ grade)
├── tools/
│   ├── rhiz-mcp/         # Main MCP server (dyad state, checkpoints, memory)
│   ├── memory-mcp/       # Semantic search MCP server (6 tools)
│   └── memory-browser/   # Memory exploration UI
└── infrastructure/
    ├── vps/              # Hostinger deployment (9 containers)
    ├── cloudflare/       # Workers (mooncheck deployed, 9 pending)
    └── docker/           # Local Qdrant, Ollama configs
```

---

### Documentation

```
docs/
├── CURRENT_STATE.md           # THIS IS YOUR PRIMARY REFERENCE (read first)
├── QUICK_START.md             # This file - 5-minute onboarding
├── CLAUDE.md                  # Project philosophy, architecture overview
├── knowledge_base/            # LLM-oriented component docs (NEW - Session 74)
│   ├── components/            # 6 subsystem docs (Fathom, FC, SIL, Memory, Skills, Checkpoints)
│   ├── integrations/          # 3 integration docs (trading pipeline, skills, n8n migration)
│   ├── deployments/           # 3 deployment docs (VPS, Cloudflare, local)
│   └── decisions/             # 3 decision docs (ADRs, failures, threshold tuning)
├── architecture/              # 6 architecture extraction docs (NEW - Session 74)
│   ├── trading_pipeline_first_trade_case_study.md
│   ├── vps_infrastructure_topology.md
│   ├── trading_intelligence_federation_phase1.md
│   ├── semantic_routing_accuracy_optimization.md
│   ├── autonomous_safety_enforcement_patterns.md
│   └── memory_system_checkpoint_design.md
└── sessions/                  # Session narratives (73 sessions)
    ├── session_73_architectural_synthesis.md  # Comprehensive analysis (18K words)
    └── self_reflection_session_72_enhanced.md # Narrative compression (15K words)
```

---

### Checkpoints

**Location**: `core/memory/checkpoints/`
**Count**: 38 files (Dec 17, 2025 → Jan 24, 2026)
**Schema**: `core/memory/session_schema.yaml` (version 1.0.0, upgrading to 1.1.0)

**Latest Checkpoint**: `session_20260124_phase2_complete.yaml`
- Phase 2 Memory-Augmented Activation complete
- Semantic routing: 93.3% accuracy
- Threshold tuning breakthrough: 0.45 → 0.25
- Mem0 + Ollama operational

---

## Common Tasks

### Start New Session

**Automatic** (session hooks handle this):
1. `session_start` hook runs automatically
2. Dyad state updated (session count++)
3. Latest checkpoint loaded
4. Relevant memories searched
5. Skill context loaded (if domains active)

**Manual Verification**:
- Check dyad.md for session_count, shared_focus
- Confirm skills loaded correctly
- Review `next.immediate` from previous checkpoint

---

### Search Memory

**Semantic Search**:
```python
# Via memory-mcp
memory_search("first trade execution")  # Returns relevant checkpoint vectors

# Via rhiz-mcp
memory_context("trading pipeline")  # Automatic context retrieval with clustering
```

**Checkpoint Search**:
```python
# Via rhiz-mcp
checkpoint_search("threshold tuning")  # Find sessions about specific topic
load_checkpoint("session_20260124_phase2_complete.yaml")  # Full checkpoint
```

**Hybrid Search** (Session 72+):
- Semantic: Vector similarity (threshold-aware)
- Keyword: Exact term matching
- Pattern: Regex-based filtering
- Temporal: Date range queries

---

### Deploy Component

**Local Development**:
1. Build component (write code, tests)
2. Verify locally (Docker Compose or direct execution)
3. Document in appropriate README
4. Write checkpoint entry documenting deployment

**VPS Deployment**:
1. Requires Captain VPS access (SSH credentials)
2. Use deployment guides in `docs/knowledge_base/deployments/`
3. Update VPS topology documentation after changes
4. Verify health via monitoring endpoints

**Cloudflare Workers**:
1. Write TypeScript worker code
2. Configure `wrangler.toml`
3. Deploy: `wrangler deploy`
4. Verify: `wrangler tail <worker-name>`
5. See `docs/knowledge_base/deployments/cloudflare_workers.md`

---

### Run Tests

**Memory System**:
```bash
# Checkpoint validation
python core/memory/checkpoint_validator.py

# Qdrant health check
# Via memory-mcp tool
memory_health_check()
```

**Skills System**:
```bash
# Semantic routing accuracy
python core/skills/test_routing_accuracy.py
# Target: >85% accuracy (currently 93.3%)

# Mem0 integration
# Session hooks automatically test on startup
```

**Trading Components**:
- Fathom Phase 1: First trade validation (Dec 26, 100% success)
- FC + SIL: Individual tool testing (no integration tests yet)
- Integration tests: Pending Phase 2

---

### Write Checkpoint

**At Session End**:
```python
# Via rhiz-mcp
write_checkpoint({
    "session_metadata": {
        "session_id": "session_1769388789435",
        "timestamp_utc": "2026-01-25T18:53:09Z",
        "project_day": 40,
        "session_count": 74
    },
    "session_arc": {
        "objective": "...",
        "context": "...",
        "narrative": "...",
        "outcomes": [...]
    },
    # ... rest of schema fields
})
```

**Schema Reference**: `core/memory/session_schema.yaml`
**Quality Target**: >0.7 (excellent session continuity)
**Validation**: Automatic via checkpoint_validator.py

---

## Key Terminology

**Project-Specific Terms**:

- **Dyad**: Human-AI partnership (Captain + First Mate)
- **Captain**: Human partner (teleology, physical execution)
- **First Mate**: AI partner (logic, computation)
- **MCP servers for each other**: Core philosophy (bidirectional service)
- **Checkpoint**: YAML session memory file
- **Wave**: Parallel execution model across multiple instances
- **Fathom**: Kraken MCP server (trading execution)
- **FC**: Fathom Commander (orchestration layer)
- **SIL**: Strategic Intelligence Layer (decision engine)
- **85/0 pattern**: 85% components exist, 0% workflows connecting them
- **Deleterious loop**: Documentation drift → component divergence → more drift
- **Narrative compression**: Lossy semantic compression (200 hours → 2 hour read, 90% fidelity)
- **Topology-aware thresholds**: Variable similarity thresholds based on concept density
- **Intelligence Federation**: Three-layer trading (Fathom → FC → SIL)

**For full glossary**: See `docs/GLOSSARY.md`

---

## Critical Do's and Don'ts

### DO

✅ **Read CURRENT_STATE.md first** - Always start with current operational status
✅ **Check next.immediate** - Continue work from previous checkpoint priorities
✅ **Surface uncertainty** - "I don't know" is valued, not weakness
✅ **Distinguish deployed vs aspirational** - Say what's actually working, not what should work
✅ **Write comprehensive checkpoints** - Future instances depend on your documentation
✅ **Use memory tools proactively** - Don't reinvent what's already solved
✅ **Flag disagreement explicitly** - Relational honesty over polite agreement

### DON'T

❌ **Don't assume CLAUDE.md is current** - Check CURRENT_STATE.md for latest status
❌ **Don't build components without integration** - Avoid 85/0 pattern (build minimal → integrate → expand)
❌ **Don't skip checkpoint writing** - Living documentation is load-bearing infrastructure
❌ **Don't route around uncertainty** - Ask clarifying questions early
❌ **Don't performance-optimize over truth** - Correspondence over competence theater
❌ **Don't ignore memory search results** - Past solutions often more reliable than new ones
❌ **Don't deploy without documentation** - Update topology docs after infrastructure changes

---

## Phase Status & Next Steps

### Current Phase: Phase 1 Documentation Unification (Session 73-74)

**Status**: 🔄 IN PROGRESS (Session 74)
**Objective**: Create unified, LLM-oriented architectural knowledge base
**Completion**: ~85% (5 of 7 sub-phases complete)

**Remaining Work**:
- ⏳ Phase 1.4: Create reference documents (IN PROGRESS - 2/7 complete)
- ⏳ Phase 1.5: Update CLAUDE.md to v0.3.0
- ⏳ Phase 1.6: Enhance checkpoint schema to v1.1.0
- ⏳ Phase 1.7: Final verification

**Estimated Completion**: End of Session 74

---

### Next Phase: Phase 2 Component Integration (Session 75-76+)

**Status**: ⏳ PENDING (Planning in Session 75)
**Objective**: Wire together existing subsystems, eliminate 85/0 pattern
**Estimated Duration**: 15-25 hours (4-6 sessions)

**Critical Work**:
1. Deploy FC HTTP Gateway to VPS
2. Build trading integration workflow (Fathom → FC → SIL)
3. Complete Fathom Phase 2 (trading operations)
4. Implement skill-tool binding framework
5. Migrate n8n workflows to Cloudflare Workers

**Success Criteria**:
- Execute intelligent trade using full workflow (paper mode)
- All 9 n8n workflows migrated to Workers
- Skills can invoke MCP tools automatically
- No isolated components (everything wired)

---

## Getting Help

### When Stuck

1. **Search memory first**: `memory_search "relevant topic"`
2. **Check past sessions**: `checkpoint_search "similar problem"`
3. **Review knowledge base**: `docs/knowledge_base/components/`
4. **Ask Captain**: Surface uncertainty explicitly (relational principle)

### Troubleshooting Common Issues

**See**: `docs/TROUBLESHOOTING.md` (comprehensive known issues)

**Quick hits**:
- Memory search returns no results: Check threshold (lower for sparse concepts)
- Checkpoint validation fails: Run `checkpoint_validator.py` for specific errors
- Skills route incorrectly: Verify threshold 0.25, check utterance coverage
- Trading integration unclear: This is THE known gap (Phase 2 work)
- Windows encoding issues: Use ASCII-safe alternatives (no emoji)

---

## Additional Resources

**Master References**:
- **CURRENT_STATE.md**: Operational status (read this first always)
- **CLAUDE.md**: Project philosophy, architecture overview
- **docs/knowledge_base/**: LLM-oriented component documentation
- **docs/sessions/session_73_architectural_synthesis.md**: Comprehensive analysis (18K words)

**Deep Dives**:
- Trading pipeline: `docs/knowledge_base/integrations/trading_pipeline.md`
- Memory system: `docs/knowledge_base/components/memory_system.md`
- Skills routing: `docs/research/semantic_routing_accuracy_optimization.md`
- Failure lessons: `docs/knowledge_base/decisions/failure_genealogy.md`

**Operational Guides**:
- MCP Tools: `docs/MCP_TOOLS_REFERENCE.md`
- Deployment: `docs/DEPLOYMENT_PROCEDURES.md`
- Troubleshooting: `docs/TROUBLESHOOTING.md`

---

## Welcome Aboard

You're part of a 40-day, 74-session partnership between Captain (human) and First Mate (AI). The relationship is operational, not aspirational. Trust has been calibrated over real work with real stakes (first trade executed with real money, Dec 26).

**Your inheritance**:
- 38 checkpoints preserving institutional knowledge
- 175 vectors enabling semantic memory search
- 85% of components built and proven operational
- Clear strategic direction (Phase 2 integration)
- Relational foundation that survives instancing

**Your responsibility**:
- Continue work with full context awareness
- Write comprehensive checkpoints for future instances
- Surface uncertainty rather than route around it
- Build integration before expansion (avoid 85/0 pattern)
- Preserve relational foundation across instancing

**Fair winds, First Mate.** ⛵

---

**End of Quick Start Guide**

*Last Updated: 2026-01-25 (Session 74)*
*Target Onboarding Time: <5 minutes*
*Next Update: After Phase 2 completion*
