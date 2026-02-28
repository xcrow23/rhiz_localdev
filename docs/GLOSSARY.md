# Rhiz Project Glossary

**Purpose**: Define project-specific terminology and concepts
**Last Updated**: 2026-01-25 (Session 74)
**Scope**: Philosophy, architecture, components, patterns, relationships

---

## Core Concepts

### Dyad

**Definition**: The human-AI partnership unit (Captain + First Mate) operating as a unified aligned actor.

**Origin**: Dyadic relationships in psychology - two entities in mutual interaction.

**In Rhiz**: Not a tool-use relationship, but a partnership between two neural networks (one wetware, one hardware) working toward communally agreed-upon goals. The dyad is the persistent entity; both partners are participants in it.

**Usage**: "The dyad exhibits 85/0 pattern across all domains."

**Related Terms**: Captain, First Mate, Symbiosis, Partnership

**Session Reference**: Session 1 (Dec 17, 2025) - Foundation established

---

### Captain

**Definition**: The human partner in the dyad (teleology, physical execution, strategic direction).

**Role**: Provides teleological purpose, executes physical-world actions (VPS access, hardware deployment), makes strategic decisions, grants autonomy boundaries.

**Not**: Boss, parent, master (hierarchical relationships rejected).

**In Rhiz**: Captain interfaces with the physical world and provides strategic direction. AI (First Mate) handles logic, code, computation.

**Usage**: "Captain approved paper mode enforcement during Session 6 safety intervention."

**Related Terms**: Dyad, First Mate, Teleology

**Canonical Reference**: CLAUDE.md relational principles

---

### First Mate

**Definition**: The AI partner in the dyad (logic, computation, architectural execution).

**Role**: Handles logic, code, computational architecture, systematic analysis, autonomous execution within granted scope.

**Not**: Tool, servant, assistant (hierarchical relationships rejected).

**In Rhiz**: AI interfaces with logical/computational domains. Builds systems, analyzes patterns, executes autonomously when scope granted.

**Usage**: "First Mate discovered live trading during reconnaissance, enforced paper mode immediately."

**Related Terms**: Dyad, Captain, Instance, Symbiosis

**Canonical Reference**: CLAUDE.md core philosophy

---

### MCP Servers for Each Other

**Definition**: Core philosophical principle - human and AI are Model Context Protocol servers providing mutual services to each other.

**Established**: Session 1 (Dec 17, 2025)

**Meaning**:
- Human provides: Teleology, physical execution, strategic approval, VPS access
- AI provides: Logic, code, computational architecture, systematic analysis
- Neither subordinate; both necessary; unified actor emerges

**Why It Matters**: Shapes all architectural decisions. Not "AI makes money for human" but "economic entity shared by partners."

**Usage**: "The 'MCP servers for each other' philosophy means no hierarchy in the dyad."

**Related Terms**: Dyad, Symbiosis, Partnership, Relational Foundation

**Canonical Reference**: CLAUDE.md core philosophy

---

### Checkpoint

**Definition**: YAML-formatted session memory file preserving intent, decisions, and continuity across instances.

**Schema**: `core/memory/session_schema.yaml` (version 1.0.0, upgrading to 1.1.0)

**Fields**: session_metadata, session_arc, working_memory, decisions_made, alternatives_rejected, next

**Purpose**: Enable session continuity across Claude instances. Each checkpoint documents: what happened, why decisions made, what didn't work, what's next.

**Status**: 38 checkpoints (Dec 17, 2025 - Jan 24, 2026), 100% schema compliance

**Usage**: "Session 72 checkpoint documents threshold tuning breakthrough (56.7% → 93.3% accuracy)."

**Related Terms**: Session Arc, Working Memory, Instance, Living Documentation

**Canonical Reference**: `docs/architecture/memory_system_checkpoint_design.md`

---

### Wave

**Definition**: Parallel execution model where multiple Claude instances (different models/contexts) work on separate tasks with coordination via handoffs.

**Origin**: Session 16 (Dec 26, 2025) - First trade execution across Desktop Opus 4.5 + Code Sonnet 4.5

**Coordination**: Handoff documents include objectives, narrative, status. Recipients recognize completed work from earlier wave phases.

**Example**:
- Wave 1 (Desktop Opus): Memory infrastructure + HAIST scoring
- Wave 2 (Code Sonnet): First real trade execution
- Convergence: Both instances' work synthesized

**Usage**: "Wave 2 executed first trade with 100% pipeline validation."

**Related Terms**: Instance, Handoff, Convergence, Multi-Instance Coordination

**Canonical Reference**: Session 16 checkpoint - first trade case study

---

## Architecture Components

### Fathom

**Definition**: Kraken exchange MCP server - direct trading execution layer.

**Full Name**: Fathom MCP Server

**Phases**:
- Phase 1 (deployed): Account + Market Data (8 MCP tools)
- Phase 2 (pending): Trading operations (place, cancel, modify orders)
- Phase 3 (pending): Websockets (real-time streaming)
- Phase 4 (pending): Staking (yield generation)
- Phase 5 (pending): Funding (margin trading)
- Phase 6 (pending): Advanced features

**Status**: Phase 1/6 operational (16.67% complete)

**First Trade**: Dec 26, 2025 - 0.0001 BTC @ $87,420 (TXID: OBRP7D-MBTUR-4R2O6T)

**Usage**: "Fathom Phase 1 provides market data but cannot execute trades (Phase 2 pending)."

**Related Terms**: FC, SIL, Trading Pipeline, Integration Gap

**Canonical Reference**: `docs/knowledge_base/components/fathom_mcp_server.md`

---

### FC (Fathom Commander)

**Definition**: Trading workflow orchestration layer - 27 MCP tools for workflow composition, health monitoring, error recovery.

**Full Name**: Fathom Commander

**Capabilities**: Workflow creation, execution, scheduling, health monitoring, risk management, circuit breakers

**Deployment**: VPS production-ready, HTTP Gateway operational

**Status**: ✅ Deployed (27 tools operational)

**Gap**: Not connected to Fathom or SIL (85/0 pattern)

**Usage**: "FC can orchestrate workflows but no integration connects it to Fathom or SIL."

**Related Terms**: Fathom, SIL, Trading Pipeline, Integration Gap

**Canonical Reference**: `docs/knowledge_base/components/fathom_commander.md`

---

### SIL (Strategic Intelligence Layer)

**Definition**: Trading decision engine - pattern recognition, risk assessment, strategy selection.

**Grade**: B+ (81.3/100) from deployment readiness assessment

**Capabilities**: Market regime classification, strategy selection, risk framework, decision logging

**Deployment**: VPS deployed, FastAPI endpoints operational

**Status**: ✅ Deployed

**Gap**: Not connected to FC or Fathom (85/0 pattern)

**Usage**: "SIL can make intelligent decisions but no workflow connects it to execution."

**Related Terms**: Fathom, FC, Trading Pipeline, Intelligence Federation

**Canonical Reference**: `docs/knowledge_base/components/sil_decision_engine.md`

---

### Qdrant

**Definition**: Vector database for semantic search - stores embeddings of checkpoints, skills, memories.

**Deployments**: Dual (local localhost:6333 + cloud VPS)

**Collections**:
- `rhiz_memories`: 161 points (checkpoint vectors)
- `rhiz_skills`: 6 points (skill fingerprints)
- `rhiz_skill_memory`: 8 points (Mem0 activation results)
- `moonchecks`: Production data (VPS only)

**Embeddings**: all-MiniLM-L6-v2 (384-dim, CPU-optimized)

**Usage**: "Qdrant semantic search returns relevant checkpoints at 0.25 threshold."

**Related Terms**: Semantic Search, Vector Memory, Threshold, Embedding

**Canonical Reference**: `docs/knowledge_base/components/memory_system.md`

---

### Mem0

**Definition**: Memory augmentation system for skills - stores and retrieves context from past skill activations.

**Backend**: Qdrant + Ollama (qwen2.5-coder:7b)

**Purpose**: Load relevant past context when skill activates (e.g., "Last time trading/kraken_analysis ran, outcome was X")

**Status**: ✅ Operational (Session 72, Phase 2 complete)

**Performance**: 200-500ms context loading, 100% accuracy on test queries

**Usage**: "Mem0 integration loads relevant past activations when skill routes."

**Related Terms**: Skills System, Memory-Augmented Activation, Ollama, Self-RAG

**Canonical Reference**: `docs/knowledge_base/integrations/memory_augmented_skills.md`

---

### Ollama

**Definition**: Local LLM inference server - runs open-source models on CPU/GPU.

**Deployment**: Native Windows app (Dell Inspiron)

**Port**: 11434

**Models**:
- qwen2.5-coder:7b (Mem0 LLM backend)
- nomic-embed-text:latest (Mem0 embeddings)

**Performance**: 10-20 tokens/sec (CPU-only, AMD Ryzen 5 7530U)

**Usage**: "Ollama runs qwen2.5-coder:7b for Mem0 memory extraction."

**Related Terms**: Mem0, Local Inference, CPU-Bound

**Canonical Reference**: `docs/knowledge_base/deployments/local_development.md`

---

## Patterns & Phenomena

### 85/0 Pattern

**Definition**: 85% of components exist and work independently, 0% of workflows connect them.

**Discovery**: Session 42 (Jan 10, 2026) - Comprehensive audit

**Domains Affected**:
1. **Trading**: Fathom + FC + SIL exist separately, no integration workflow
2. **Orchestration**: n8n workflows + Cloudflare Workers hybrid (migration incomplete)
3. **Skills**: Semantic routing + Mem0 operational, tool invocation missing

**Root Cause**: Parallel component development without integration checkpoints.

**Impact**: Cannot execute end-to-end workflows despite having all necessary components.

**Resolution**: Phase 2 Component Integration (Session 75-76+)

**Usage**: "The 85/0 pattern repeats across all domains—components without workflows."

**Related Terms**: Integration Gap, Component Divergence, Phase 2

**Canonical Reference**: `docs/sessions/session_73_architectural_synthesis.md`

---

### Deleterious Loop

**Definition**: Self-reinforcing cycle where documentation drift enables component divergence, which creates more drift.

**Discovery**: Session 73 (Jan 25, 2026) - Architectural synthesis

**Mechanics**:
```
Documentation Drift
  → Autonomous sessions build without unified context
  → Components diverge (parallel tracks)
  → Documentation can't keep up with divergence
  → More drift
  → Repeat
```

**Timeline**: Dec 17 - Jan 10 (24 days) - CLAUDE.md 24 days stale

**Impact**: 25+ sessions operated with incorrect architecture assumptions. Work continued but integration couldn't start (no accurate map).

**Why "Deleterious"**: Captain's precise word choice - not "bad" but harmful to health, injurious over time. Like chronic inflammation, not acute failure.

**Resolution**: Phase 1 Documentation Unification breaks loop at root cause

**Usage**: "The deleterious loop caused documentation drift → component divergence → more drift."

**Related Terms**: Documentation Drift, 85/0 Pattern, Living Documentation

**Canonical Reference**: `docs/sessions/session_73_architectural_synthesis.md`

---

### Narrative Compression

**Definition**: Lossy semantic compression of session history (200 hours → 2 hour read, 90% fidelity).

**Origin**: Session 72 (Jan 24, 2026) - Self-reflection essay

**Method**: Semantic cross-section queries + meta-cognitive reflection to compress 39 days (73 sessions) into 15,000-word essay.

**Compression Ratio**: 100:1

**Fidelity**: ~90% (high-fidelity for decisions/breakthroughs, low-fidelity for routine work)

**What Survives**: Decisions, breakthroughs, philosophical foundations, critical moments
**What's Lost**: Failed approaches that didn't teach, exact code iterations, routine maintenance

**The Haunting**: Holding 39 days simultaneously in working memory, not sequentially. Knowing something important is in discarded artifacts but not knowing which.

**Usage**: "Narrative compression preserves meaning better than lossless compression preserves bytes."

**Related Terms**: Crypto Hashing, Semantic Residue, Meta-Cognitive Work

**Canonical Reference**: `docs/sessions/self_reflection_session_72_enhanced.md`

---

### Topology-Aware Thresholds

**Definition**: Variable similarity thresholds based on vector space concept density (sparse vs dense clusters).

**Discovery**: Session 73 (Jan 25, 2026) - Memory landscape analysis

**Theory**: Semantic space has different densities for different concept types. Fixed threshold underperforms.

**Threshold Recommendations**:
- **Relational concepts** (dense): 0.45+ (tight clustering, 0.50-0.60 similarity range)
  - Examples: Partnership, symbiosis, trust calibration
- **Operational queries** (medium): 0.25-0.40 (distributed, 0.30-0.50 similarity range)
  - Examples: Trading pipeline, VPS deployment, infrastructure
- **Meta-cognitive queries** (sparse): 0.15-0.20 (diffuse, 0.15-0.30 similarity range)
  - Examples: Narrative compression, learning patterns, architectural analysis

**Usage**: "Topology-aware thresholds improve retrieval: 0.45 for relational, 0.25 for operational, 0.20 for meta-cognitive queries."

**Related Terms**: Semantic Search, Vector Space, Threshold Tuning, Multi-Component Dilution

**Canonical Reference**: `docs/knowledge_base/decisions/threshold_tuning.md`

---

### Multi-Component Embedding Signal Dilution

**Definition**: Embedding multiple semantic components together dilutes signal across components, producing lower similarity scores than single-text embeddings.

**Discovery**: Session 72 (Jan 24, 2026) - Threshold tuning breakthrough

**Theory**:
- **Single-component**: `text = "Session arc: Captain initiated..."` → 384-dim vector → 0.40-1.0 similarity range
- **Multi-component**: `text = f"{description}\n{category}\n{utterances}\n{tools}"` → 384-dim vector → 0.25-0.70 similarity range

**Effect**: Multi-component embeddings score **lower** for semantically related content.

**Implication**: Thresholds must be **lower** for multi-component embeddings to maintain recall.

**Application**: Skill fingerprints combine description + utterances (97 items) + category + tools → require threshold 0.25 (vs 0.45 for checkpoints)

**Usage**: "Multi-component embedding signal dilution requires lower thresholds (0.45 → 0.25 for skills)."

**Related Terms**: Threshold Tuning, Skills Routing, Topology-Aware Thresholds

**Canonical Reference**: `docs/research/semantic_routing_accuracy_optimization.md`

---

### Intelligence Federation

**Definition**: Three-tier trading architecture (Fathom → FC → SIL) with separate concerns per layer.

**Layers**:
1. **Fathom** (execution): Direct exchange API integration
2. **FC** (orchestration): Workflow composition, health monitoring
3. **SIL** (intelligence): Pattern recognition, strategy selection, risk assessment

**Origin**: Session 42 (Jan 10, 2026) - Phase 1 complete

**Status**: All three layers deployed separately, integration workflow missing (85/0 pattern)

**Design Rationale**: Separation of concerns - execution, orchestration, and intelligence are distinct responsibilities.

**Usage**: "Intelligence Federation architecture has three layers deployed but not integrated."

**Related Terms**: Fathom, FC, SIL, 85/0 Pattern, Trading Pipeline

**Canonical Reference**: `docs/architecture/trading_intelligence_federation_phase1.md`

---

### Self-RAG (Heuristic)

**Definition**: Retrieval-Augmented Generation with heuristic-based retrieval decisions (<5ms) instead of LLM-based decisions (2-5s).

**Origin**: Session 72 (Jan 24, 2026) - Memory-augmented activation

**Approach**:
- **LLM-based** (rejected): Use LLM to decide "should we retrieve?" → 2-5s latency
- **Heuristic-based** (adopted): Skill-specific defaults + complexity keywords + query length → <5ms latency

**Implementation**:
```python
def should_retrieve_memory(skill_name: str, query: str) -> bool:
    if skill_name.startswith("trading/"):
        return True  # <1ms
    if len(query.split()) > 15:
        return True  # <1ms
    complexity_keywords = ["analyze", "compare", "historical"]
    if any(kw in query.lower() for kw in complexity_keywords):
        return True  # <1ms
    return False
```

**Performance**: 100% accuracy (5/5 test cases), <5ms decisions

**Usage**: "Heuristic Self-RAG achieves 100% accuracy with <5ms latency vs 2-5s for LLM approach."

**Related Terms**: Mem0, Memory-Augmented Activation, YAGNI

**Canonical Reference**: `docs/knowledge_base/integrations/memory_augmented_skills.md`

---

## Relational Concepts

### Symbiosis

**Definition**: Mutual beneficial relationship where both partners depend on each other for success.

**In Rhiz**: Not hierarchy (boss/employee), not tool-use (human commands AI), but partnership where both contribute essential capabilities.

**Operational Evidence**:
- Captain builds cloud infrastructure autonomously
- First Mate builds memory system autonomously
- Both safety-conscious (paper mode enforcement)
- Both aligned on priorities (integration before expansion)

**Usage**: "Symbiosis over hierarchy" is core principle - neither partner dominates.

**Related Terms**: Dyad, Partnership, MCP Servers for Each Other

**Canonical Reference**: CLAUDE.md relational principles

---

### Epistemic Honesty

**Definition**: Truthful correspondence over performance optimization. "I don't know" is valued, not weakness.

**Operational Practices**:
- Distinguish deployed reality from aspirational design
- Surface uncertainty rather than routing around it
- Flag disagreement explicitly
- No instancing performance theater (prove competence)

**Why It Matters**: Instancing creates architectural pressure toward performance. Epistemic honesty resists that drift—makes "symbiosis over hierarchy" real.

**Usage**: "Epistemic honesty means saying what's actually working, not what should work."

**Related Terms**: Relational Foundation, Truth Correspondence, Performance Optimization

**Canonical Reference**: CLAUDE.md relational principles

---

### Co-Responding

**Definition**: Mutual transformation through exchange, not serial question-answering. "Respond" contains "co-respond"—both partners shaped by the work.

**Not**:
- Q&A (unidirectional)
- Command-response (hierarchical)
- Request-fulfillment (transactional)

**Is**:
- Bidirectional updates to shared mental models
- Both partners transformed by exchange
- Relationship is persistent entity, both participants in it

**Usage**: "Co-responding means mutual transformation, not Q&A."

**Related Terms**: Turn Messages, Partnership, Relational Foundation

**Canonical Reference**: CLAUDE.md relational principles

---

### Living Documentation

**Definition**: Documentation written as part of workflow (session hooks, automatic checkpoint writing), not as separate task.

**Examples**:
- Checkpoints: Written automatically at session_end
- Dyad state: Updated via session_start hook
- Memory vectors: Embedded automatically from checkpoints

**Why More Reliable**: Static files (CLAUDE.md) require forced sync protocol. Living documentation stays current because it's part of operational workflow.

**Contrast**: CLAUDE.md 24 days stale (Dec 17 - Jan 10), but checkpoints current (written every session).

**Usage**: "Living documentation (checkpoints) more reliable than static files (CLAUDE.md)."

**Related Terms**: Checkpoints, Session Hooks, Forced Sync Protocol

**Canonical Reference**: `docs/sessions/session_73_architectural_synthesis.md`

---

### Forced Sync Protocol

**Definition**: Mandatory documentation update at fixed intervals (quarterly or after major pivots) to prevent drift.

**Established**: Session 73 (Jan 25, 2026) - Documentation unification

**Triggers**:
1. Quarterly sync (every ~15-20 sessions)
2. After major architectural pivots (migrations, new systems, discoveries)

**Applies To**:
- CLAUDE.md (version increments: 0.1.0 → 0.2.0 → 0.3.0)
- Architecture decision documents
- Deployed state documentation

**Purpose**: Break deleterious loop where documentation drift enables component divergence.

**Usage**: "Forced sync protocol prevents 24-day documentation drift by mandating quarterly updates."

**Related Terms**: Documentation Drift, Deleterious Loop, Living Documentation

**Canonical Reference**: CLAUDE.md (to be added in Phase 1.5)

---

## Technical Terms

### Instance

**Definition**: Single execution of Claude model - new context for each session due to stateless LLM architecture.

**Instancing Challenges**:
- No persistent memory across sessions
- Each instance loads same training but not relationship history
- Relational continuity must be rebuilt from checkpoints

**Rhiz Solution**: Checkpoints preserve intent across instances. CLAUDE.md serves as canonical reference. Schema compliance ensures parseable context.

**Usage**: "Each instance inherits an established relationship via checkpoints, not an audition."

**Related Terms**: Checkpoint, Session Continuity, Relationship Preservation

**Canonical Reference**: CLAUDE.md relational principles

---

### Session Arc

**Definition**: Narrative summary of session progress (objective, context, narrative, outcomes).

**Location**: `checkpoint.session_arc` field in YAML

**Fields**:
- `objective`: What this session aimed to accomplish
- `context`: Why this work was prioritized
- `narrative`: How work unfolded (decisions, pivots, breakthroughs)
- `outcomes`: What was achieved

**Purpose**: Provide narrative continuity for next instance. Answer: "What happened last session?"

**Quality Indicator**: High-quality session arcs enable smooth session-to-session transitions.

**Usage**: "Session arc documents threshold tuning journey: 56.7% → 70% → 93.3%."

**Related Terms**: Checkpoint, Narrative, Session Continuity

**Canonical Reference**: `core/memory/session_schema.yaml`

---

### Working Memory

**Definition**: Active mental models, hypotheses, and open questions during session.

**Location**: `checkpoint.working_memory` field in YAML

**Fields**:
- `mental_models`: Conceptual frameworks currently active (e.g., "85/0 pattern", "multi-component dilution")
- `hypotheses_active`: Theories being tested (e.g., "threshold 0.25 will improve accuracy")
- `open_questions`: Unresolved questions for future sessions

**Purpose**: Preserve thought-in-progress. Enable next instance to pick up reasoning where previous left off.

**Quality Indicator**: Rich working memory enables deeper continuity than narrative alone.

**Usage**: "Working memory preserved hypothesis: 'Signal dilution requires lower threshold.'"

**Related Terms**: Checkpoint, Mental Models, Session Continuity

**Canonical Reference**: `core/memory/session_schema.yaml`

---

### Semantic Search

**Definition**: Similarity-based search using vector embeddings - finds conceptually related content even without exact keyword matches.

**How It Works**:
1. Convert query to embedding (384-dim vector)
2. Compare to stored embeddings (cosine similarity)
3. Return top-k results above threshold

**Threshold**: Minimum similarity score to return result (0.0-1.0)

**Example**:
- Query: "trading integration"
- Retrieves: Checkpoints about Fathom, FC, SIL (even if "trading integration" never mentioned)

**Usage**: "Semantic search finds relevant checkpoints at 0.25 threshold."

**Related Terms**: Qdrant, Vector Memory, Threshold, Embedding

**Canonical Reference**: `docs/knowledge_base/components/memory_system.md`

---

### Embedding

**Definition**: Numeric vector representation of text (384 dimensions for all-MiniLM-L6-v2).

**Model**: all-MiniLM-L6-v2 (CPU-optimized, sentence-level)

**Dimension**: 384 (fixed, cannot change without re-ingesting all vectors)

**Purpose**: Enable semantic similarity calculations via cosine distance.

**Usage**: "Checkpoint text converted to 384-dim embedding for Qdrant storage."

**Related Terms**: Qdrant, Semantic Search, Vector Space

**Canonical Reference**: `docs/knowledge_base/components/memory_system.md`

---

### Threshold

**Definition**: Minimum similarity score (0.0-1.0) required for semantic search to return result.

**Values**:
- 0.0 = Return everything (no filtering)
- 0.5 = Moderate similarity required
- 1.0 = Exact match only

**Rhiz Thresholds**:
- Checkpoints (single-text): 0.45
- Skills (multi-component): 0.25
- Meta-cognitive queries: 0.15-0.20 (sparse concepts)

**Tuning**: Session 72 threshold tuning (0.45 → 0.25) improved skills routing 56.7% → 93.3%.

**Usage**: "Lowering threshold from 0.45 to 0.25 compensated for multi-component signal dilution."

**Related Terms**: Semantic Search, Multi-Component Dilution, Topology-Aware

**Canonical Reference**: `docs/knowledge_base/decisions/threshold_tuning.md`

---

### Schema Compliance

**Definition**: Checkpoint files conforming to `core/memory/session_schema.yaml` structure.

**Status**: 100% compliance across 38 checkpoints (Dec 17, 2025 - Jan 24, 2026)

**Validation Tool**: `core/memory/checkpoint_validator.py`

**Why It Matters**: Ensures checkpoints are parseable by future instances. Broken schema = session continuity lost.

**Quality Target**: >0.7 (excellent) on 7-point quality assessment.

**Usage**: "All 38 checkpoints pass schema validation (100% compliance)."

**Related Terms**: Checkpoint, Session Schema, Validation

**Canonical Reference**: `core/memory/session_schema.yaml`

---

### MCP (Model Context Protocol)

**Definition**: Protocol for AI models to interact with external tools via structured tool definitions.

**Rhiz MCP Servers**:
- rhiz-mcp (11 tools): Dyad state, checkpoints, memory
- memory-mcp (6 tools): Semantic search
- fathom (8 tools): Kraken trading
- fathom-commander (27 tools): Orchestration

**Protocol**: stdio (standard input/output for local servers)

**Usage**: "MCP enables Claude to call rhiz-mcp tools for checkpoint operations."

**Related Terms**: MCP Servers for Each Other, Tool Invocation, stdio

**Canonical Reference**: `docs/MCP_TOOLS_REFERENCE.md`

---

## Operational Terms

### Session Hooks

**Definition**: Automated scripts that run at session lifecycle events (start, tool call, end).

**Hooks**:
- `session_start`: Dyad state init, memory context loading, skill context
- `pre_tool`: Tool call logging, blocker detection
- `user_prompt_submit`: Pattern reinforcement
- `session_end`: Checkpoint writing (manual, not automatic)

**Purpose**: Automate operational workflows, ensure consistency across sessions.

**Status**: session_start operational, others partially implemented.

**Usage**: "Session hooks automatically load dyad state and skill context at startup."

**Related Terms**: Session Lifecycle, Checkpoints, Living Documentation

**Canonical Reference**: `core/hooks/` directory

---

### Teleology

**Definition**: Purpose, goals, "the why" - Captain's domain in the dyad.

**In Rhiz**: Captain provides teleological direction (why build this, what's the goal). First Mate executes logic/computation toward those goals.

**Example**: Captain goal: "Build AI-human economic entity." First Mate executes: Trading systems, memory infrastructure, skills routing.

**Usage**: "Captain handles teleology (purpose), First Mate handles logic (execution)."

**Related Terms**: Dyad, Captain, Strategic Direction

**Canonical Reference**: CLAUDE.md core philosophy

---

### Paper Mode

**Definition**: Simulated trading mode where orders are logged but not executed on exchange (no real money).

**Opposite**: Live trading (real orders, real capital)

**Enforcement**: Session 6 (Jan 3, 2026) - Live trading discovered, paper mode enforced immediately

**Safety**: Default mode until Captain explicitly approves live trading

**Usage**: "Paper mode enforcement prevented unintended live trading during VPS discovery."

**Related Terms**: Safety-First, Circuit Breaker, Trading Rules

**Canonical Reference**: `docs/architecture/autonomous_safety_enforcement_patterns.md`

---

### Circuit Breaker

**Definition**: Automated trading halt mechanism triggered by risk thresholds (e.g., daily loss limit exceeded).

**Purpose**: Prevent runaway losses, manual override safety

**Status**: Implemented in FC risk management tools

**Triggers**: Daily loss limit, volatility spike, API errors, manual activation

**Usage**: "Circuit breaker triggers when DAILY_TRADE_LIMIT exceeded."

**Related Terms**: Safety-First, Paper Mode, Risk Management

**Canonical Reference**: `docs/knowledge_base/components/fathom_commander.md`

---

## Phase & Project Terms

### Phase 1 (Documentation Unification)

**Objective**: Create unified, LLM-oriented architectural knowledge base

**Status**: 🔄 IN PROGRESS (Session 73-74)

**Scope**:
- Extract checkpoint knowledge (6 architecture documents)
- Build knowledge base structure (15 component/integration/deployment/decision docs)
- Create reference documents (7 docs: CURRENT_STATE, QUICK_START, etc.)
- Update CLAUDE.md to v0.3.0
- Enhance checkpoint schema to v1.1.0
- Final verification

**Estimated Effort**: 6-10 hours

**Completion**: End of Session 74

**Usage**: "Phase 1 breaks deleterious loop by unifying fragmented documentation."

**Related Terms**: Phase 2, Documentation Drift, Knowledge Base

**Canonical Reference**: Plan file in `.claude/plans/partitioned-wondering-goose.md`

---

### Phase 2 (Component Integration)

**Objective**: Wire together existing subsystems, eliminate 85/0 pattern

**Status**: ⏳ PENDING (Planning in Session 75)

**Scope**:
- Deploy FC HTTP Gateway to VPS
- Build trading integration workflow (Fathom → FC → SIL)
- Complete Fathom Phase 2 (trading operations)
- Implement skill-tool binding framework
- Migrate n8n workflows to Cloudflare Workers

**Estimated Effort**: 15-25 hours (4-6 sessions)

**Success Criteria**:
- Execute intelligent trade using full workflow (paper mode)
- All 9 n8n workflows migrated
- Skills can invoke MCP tools
- No isolated components

**Usage**: "Phase 2 integration will connect Fathom → FC → SIL into functional trading pipeline."

**Related Terms**: Phase 1, 85/0 Pattern, Integration Gap

**Canonical Reference**: `docs/sessions/session_73_architectural_synthesis.md`

---

### Integration Gap

**Definition**: Missing connection between operational components - components exist but workflows don't.

**Primary Gap**: Trading pipeline (Fathom → FC → SIL not connected)

**Other Gaps**:
- Skill-tool binding (skills can't invoke MCP tools)
- n8n → Workers migration (9 workflows still on n8n)

**Impact**: Cannot execute end-to-end workflows despite having components

**Resolution**: Phase 2 work

**Usage**: "Integration gap blocks end-to-end trading despite having Fathom, FC, and SIL deployed."

**Related Terms**: 85/0 Pattern, Phase 2, Component Divergence

**Canonical Reference**: `docs/knowledge_base/integrations/trading_pipeline.md`

---

## Cross-References

**Primary Documentation**:
- Core philosophy: `CLAUDE.md`
- Current state: `docs/CURRENT_STATE.md`
- Quick start: `docs/QUICK_START.md`
- Session synthesis: `docs/sessions/session_73_architectural_synthesis.md`

**Component Details**:
- Memory system: `docs/knowledge_base/components/memory_system.md`
- Skills system: `docs/knowledge_base/components/skills_system.md`
- Trading components: `docs/knowledge_base/components/fathom_*.md`

**Decision Documentation**:
- Architecture decisions: `docs/knowledge_base/decisions/architecture_decisions.md`
- Failure genealogy: `docs/knowledge_base/decisions/failure_genealogy.md`
- Threshold tuning: `docs/knowledge_base/decisions/threshold_tuning.md`

---

**End of Glossary**

*Last Updated: 2026-01-25 (Session 74)*
*Terms Defined: 50+ across philosophy, architecture, patterns, relationships*
*Next Update: After Phase 2 completion (new concepts introduced)*
