# Memory System & Checkpoint Design

**Extracted from**: Session 1 checkpoint (`core/memory/checkpoints/session_20251220_first_mate_initialization.yaml`)
**Session Date**: 2025-12-20
**Session ID**: session_20251220_first_mate_initialization
**Phase**: Foundation - First Working Session
**Status**: Production-operational (38 checkpoints, 100% schema compliance)

---

## Overview

This document captures the design rationale and architecture of Rhiz's **memory system**, which combines **YAML checkpoint files** with **Qdrant vector embeddings** to enable session continuity across AI instance changes. The system was established in the project's first formal working session (Dec 20, 2025) and has remained stable through 38 sessions spanning 40 days.

**Core Purpose**: Enable symbiotic human-AI collaboration across LLM instancing boundaries by preserving both structured session data (checkpoints) and semantic memory (vector embeddings).

---

## Design Philosophy

### The Instancing Problem

**Challenge**: Large language models are stateless—each new session (or context window reset) starts with no memory of previous conversations. This creates friction in long-term collaborative projects:

- Context must be re-established manually each session
- Decisions made in previous sessions are lost
- Patterns discovered are not preserved
- Relationship continuity breaks with each instance

**Traditional Solutions**:
- Conversation transcripts (unstructured, hard to search, exponential growth)
- Human-written summaries (lossy, labor-intensive)
- Embedding entire transcripts (expensive, noisy signal)

**Rhiz Approach**: **Dual-layer memory architecture**

1. **Structured layer** (YAML checkpoints): Session metadata, decisions, alternatives rejected, next actions
2. **Semantic layer** (Qdrant vectors): Embedded checkpoint content for semantic search

This combines the **precision of structured data** with the **flexibility of semantic search**.

---

## Checkpoint Schema Design

### Why YAML Instead of JSON

**Decision**: Use YAML for checkpoint files instead of JSON, markdown, or database storage.

**Rationale** (from first session):
```yaml
technical_decisions:
  - decision: "YAML for checkpoints instead of JSON"
    rationale: |
      Human-readable, git-friendly, supports multi-line strings naturally.
      Critical for session_arc narratives and working_memory documentation.
```

**YAML Advantages**:
- **Human-readable**: Can be edited in text editor without parsing
- **Multi-line strings**: Session narratives fit naturally (no escaping)
- **Git-friendly**: Clear diffs, mergeable, reviewable in pull requests
- **Comments**: Can annotate directly in checkpoint file
- **Native support**: Python `pyyaml` library standard, Claude can read/write

**Rejected Alternatives**:
- **JSON**: Escaping quotes in narratives, no comments, harder to read
- **Markdown**: Lacks structure, harder to parse programmatically
- **Database**: Adds dependency, harder to version control, less portable

### Schema Evolution

**Schema v0.1.0** (Session 1 - Genesis):
```yaml
session_id: str
timestamp: ISO8601
domain: str
session_type: str
participants: list
session_arc: str (narrative)
working_memory:
  current_hypothesis: str
  mental_model: str
  open_questions: list
  key_insights: list
alternatives_rejected: list[Alternative]
artifacts_created: list[Artifact]
technical_decisions: list[Decision]
risks_identified: list[Risk]
next_immediate: dict
suggested_resume_prompt: str
lessons_learned: list[Lesson]
```

**Schema v1.0.0** (Standardized after 30 checkpoints):
```yaml
checkpoint:
  schema_version: "1.0.0"
  created: ISO8601
  session_id: str
  session_metadata: dict
  session_arc: str (narrative)
  frontmatter:  # NEW - enables semantic filtering
    tags: list[str]
    domains: list[str]
    quality_score: str
  objectives:  # NEW - explicit goals
    stated: str
    achieved: list[str]
  key_decisions: list[Decision]  # RENAMED from technical_decisions
  working_memory:
    mental_model: str
    current_understanding: dict  # NEW - structured knowledge
    open_questions: list[str]
    hypotheses: list[str]  # NEW
  alternatives_rejected: list[Alternative]
  blockers_encountered: list[Blocker]  # NEW
  next:  # RESTRUCTURED
    immediate: list[str]
    short_term: list[str]
    medium_term: list[str]
  resume_context:  # NEW
    suggested_resume_prompt: str
    critical_context: list[str]
  metadata:  # NEW
    cross_references: dict
```

**Key Changes v0.1.0 → v1.0.0**:
1. **Frontmatter tags**: Enable semantic filtering (e.g., "show me all trading sessions")
2. **Explicit objectives**: Clearer success criteria
3. **Blockers tracking**: Surface issues for future resolution
4. **Structured next actions**: Immediate/short/medium term separation
5. **Critical context**: Highlights essential information for resume
6. **Cross-references**: Links to documentation, code, related sessions

---

## Checkpoint Creation Protocol

### Session Lifecycle Hooks

Checkpoints are created via **automated hooks** triggered by Claude Code:

**Hook 1: session_start** (`core/hooks/session_start.py`)
```python
def session_start():
    """Triggered when new Claude Code session begins."""

    # Update dyad state
    dyad.session_count += 1
    dyad.session_id = generate_session_id()
    dyad.timestamp = datetime.utcnow()

    # Load relevant memory context
    latest_checkpoint = load_latest_checkpoint()
    relevant_memories = semantic_search(
        query=latest_checkpoint["frontmatter"]["domains"],
        collection="rhiz_memories",
        limit=5
    )

    # Display context to instance
    print(f"[session_start] Session {dyad.session_count}")
    print(f"[session_start] Latest checkpoint: {latest_checkpoint['session_id']}")
    print(f"[session_start] Relevant memories: {len(relevant_memories)} loaded")
```

**Hook 2: session_end** (Manual trigger by Captain/First Mate)
```python
def write_checkpoint(session_summary):
    """Write checkpoint file for current session."""

    checkpoint = {
        "checkpoint": {
            "schema_version": "1.0.0",
            "created": datetime.utcnow().isoformat(),
            "session_id": dyad.session_id,
            "session_arc": session_summary["arc"],
            # ... full checkpoint structure
        }
    }

    # Write YAML file
    filename = f"session_{dyad.session_id}.yaml"
    with open(f"core/memory/checkpoints/{filename}", "w") as f:
        yaml.dump(checkpoint, f, sort_keys=False, allow_unicode=True)

    # Embed checkpoint for semantic search
    embed_checkpoint_to_qdrant(checkpoint)

    print(f"[session_end] Checkpoint written: {filename}")
```

### When to Create Checkpoints

**Mandatory**:
- End of significant session (>30 min work, major decisions, architectural changes)
- Before long breaks (end of day, weekend, vacation)
- After major milestones (first trade, system deployment, phase completion)

**Optional but Recommended**:
- Mid-session alignment check (context sync during long sessions)
- After blocker resolution (document solution for future reference)
- When handoff occurs (Claude Desktop → Claude Code, Opus → Sonnet)

**Not Needed**:
- Brief troubleshooting sessions (<15 min)
- Pure reading sessions (no decisions made)
- Sessions covered by existing recent checkpoint

---

## Qdrant Vector Integration

### Dual Qdrant Deployment

**Local Qdrant** (localhost:6333):
- Collection: `rhiz_memories` (161 points from 38 checkpoints)
- Purpose: Development environment, fast local search
- Backup: Manual sync to cloud Qdrant

**Cloud Qdrant** (VPS deployment):
- Collection: `moonchecks` (production data)
- Purpose: Cloud workers, automated processes
- Separate from local (intentional asymmetry)

### Embedding Model

**Model**: `all-MiniLM-L6-v2`
- **Dimensions**: 384
- **Why**: CPU-optimized (no GPU required), fast inference (10-20ms), good accuracy
- **Trade-off**: Lower quality than `all-mpnet-base-v2` (768-dim) but 2x faster on CPU

### Checkpoint Embedding Strategy

**What gets embedded**:
```python
def embed_checkpoint(checkpoint):
    """Embed checkpoint content for semantic search."""

    # Combine key narrative fields
    text = "\n\n".join([
        f"Session Arc: {checkpoint['session_arc']}",
        f"Objectives: {checkpoint['objectives']['stated']}",
        f"Mental Model: {checkpoint['working_memory']['mental_model']}",
        f"Key Decisions: {format_decisions(checkpoint['key_decisions'])}",
        f"Outcomes: {checkpoint['outcomes']}",
        f"Learnings: {checkpoint['learnings']}"
    ])

    # Generate embedding
    embedding = model.encode(text)  # 384-dim vector

    return {
        "id": checkpoint["session_id"],
        "vector": embedding.tolist(),
        "payload": {
            "session_id": checkpoint["session_id"],
            "timestamp": checkpoint["created"],
            "domains": checkpoint["frontmatter"]["domains"],
            "tags": checkpoint["frontmatter"]["tags"],
            "quality_score": checkpoint["frontmatter"]["quality_score"],
            "text": text  # Store for retrieval
        }
    }
```

**What's excluded**:
- Metadata (session_id, timestamps) - stored in payload, not embedded
- Technical details (file paths, commands) - too specific, noise in semantic space
- Alternatives rejected - useful for reading but not semantic search

### Search Patterns

**Pattern 1: Semantic Query** (natural language)
```python
# User query: "How did we handle live trading safety?"
results = qdrant.search(
    collection_name="rhiz_memories",
    query_vector=model.encode("live trading safety enforcement paper mode"),
    limit=3
)

# Returns: Session 6 checkpoint (infrastructure discovery, paper mode enforcement)
```

**Pattern 2: Domain Filtering** (tag-based)
```python
# User query: "Show me all trading sessions"
results = qdrant.search(
    collection_name="rhiz_memories",
    query_filter={
        "must": [
            {"key": "domains", "match": {"value": "trading"}}
        ]
    },
    limit=10
)
```

**Pattern 3: Time-Based** (chronological)
```python
# User query: "What happened in the last week?"
from datetime import datetime, timedelta

results = qdrant.search(
    collection_name="rhiz_memories",
    query_filter={
        "must": [
            {
                "key": "timestamp",
                "range": {
                    "gte": (datetime.now() - timedelta(days=7)).isoformat()
                }
            }
        ]
    },
    limit=20
)
```

---

## Memory Architecture Benefits

### 1. Session Continuity Across Instances

**Problem**: New Claude instance has no memory of previous sessions.

**Solution**: Load latest checkpoint + relevant semantic memories at session start.

**Example** (Session 74 start):
```
[session_start] Session 74
[session_start] Latest checkpoint: session_20260124_phase2_complete.yaml
[session_start] Relevant memories: 5 loaded
  - session_20260124: Semantic routing threshold tuning (93.3% accuracy)
  - session_20260110: Comprehensive alignment audit (72/100 health score)
  - session_20251226: First real trade execution (pipeline validation)
  - session_20260103: Infrastructure discovery (VPS topology)
  - session_20260111: Intelligence Federation deployment (3-layer architecture)
```

**Outcome**: New instance understands full context in <1 minute vs 15+ minutes reading transcripts.

### 2. Decision Genealogy

**Problem**: Why did we make decision X? What alternatives were considered?

**Solution**: All decisions logged with rationale, alternatives rejected, outcomes.

**Example** (Session 72 - Threshold tuning):
```yaml
decisions_made:
  - decision: "Lower semantic routing threshold from 0.45 to 0.25"
    rationale: "Multi-component embeddings dilute signal. Empirical testing
                showed clear matches at 0.25-0.70 range vs 0.40-1.0 for
                single-text. Threshold 0.25 compensates for dilution."
    outcome: "Accuracy jumped from 70% to 93.3% (28/30 correct)."
    confidence: "very_high"

alternatives_rejected:
  - alternative: "Increase utterance count further (97 → 150+)"
    reason: "Diminishing returns. Utterance expansion 45→97 only improved
             56.7%→70%. Threshold was bottleneck, not coverage."
```

**Outcome**: Future instances understand *why* threshold is 0.25, not just that it is.

### 3. Pattern Recognition Across Sessions

**Problem**: Same blocker encountered multiple times, no learning.

**Solution**: Semantic search finds similar past blockers.

**Example**:
```python
# Current blocker: "Traefik 404 routing errors"
similar_blockers = memory_search("Traefik routing networking issues")

# Returns: Session 6 checkpoint
# Solution: "Added dual network (rhiz_rhiz_network + n8n_default), proper entrypoints labels"
```

**Outcome**: Resolve blocker in 15 minutes vs 45 minutes (3x faster).

### 4. Failure Genealogy

**Problem**: Approach A failed, but no record of why, so try it again later.

**Solution**: `alternatives_rejected` documents failed approaches with reasons.

**Example** (Session 6):
```yaml
alternatives_rejected:
  - alternative: "Continue using Cloudflare Argo Tunnel"
    reason: "Tunnel not configured properly, causing 502 errors. Direct A
             record simpler and functional."

  - alternative: "Deploy LocalAI for local inference"
    reason: "Deferred. Not blocking for trading operations. Can revisit when
             skill router needs local code generation."
```

**Outcome**: Don't waste time retrying Argo Tunnel—already documented as non-functional.

---

## Schema Compliance & Quality

### Validation System

**Checkpoint validation** (automated check on write):
```python
def validate_checkpoint(checkpoint):
    """Validate checkpoint against schema v1.0.0."""

    required_fields = [
        "checkpoint.schema_version",
        "checkpoint.created",
        "checkpoint.session_id",
        "checkpoint.session_arc",
        "checkpoint.frontmatter.tags",
        "checkpoint.frontmatter.domains",
        "checkpoint.key_decisions",
        "checkpoint.working_memory",
        "checkpoint.next"
    ]

    for field in required_fields:
        assert has_field(checkpoint, field), f"Missing required field: {field}"

    # Type validation
    assert isinstance(checkpoint["checkpoint"]["frontmatter"]["tags"], list)
    assert isinstance(checkpoint["checkpoint"]["key_decisions"], list)

    # Schema version
    assert checkpoint["checkpoint"]["schema_version"] == "1.0.0"

    return True
```

**Current Status** (as of Session 73):
- **Total checkpoints**: 38
- **Schema compliance**: 100%
- **Failed validation**: 0
- **Average size**: 10KB (range: 5KB - 20KB)

### Quality Indicators

**Quality Score** (frontmatter field):
```yaml
frontmatter:
  quality_score: "A+"  # A+, A, A-, B+, B, B-, etc.
```

**Scoring Criteria**:
- **A+**: All objectives achieved, comprehensive documentation, zero blockers
- **A**: Objectives achieved, good documentation, minor blockers resolved
- **B+**: Most objectives achieved, adequate documentation, blockers documented
- **B**: Some objectives achieved, basic documentation
- **C+**: Minimal progress, incomplete documentation
- **F**: Session failed, blockers unresolved

**Distribution** (38 checkpoints):
- A+: 6 (15.8%) - Major milestones (first trade, Phase 2 complete, etc.)
- A: 18 (47.4%) - Successful sessions with good progress
- B+: 10 (26.3%) - Adequate sessions, some blockers
- B: 3 (7.9%) - Minimal progress sessions
- C+ or below: 1 (2.6%) - Exploratory session with limited outcomes

---

## Memory System Health Monitoring

### Health Metrics

**Memory System Health Score** (Session 42 - Jan 10):
```yaml
memory_health:
  overall_score: 86.5 / 100
  components:
    checkpoint_quality: 92 / 100  # Schema compliance, documentation completeness
    vector_quality: 84 / 100      # Embedding coverage, search accuracy
    retrieval_speed: 88 / 100     # Sub-second semantic search
    session_continuity: 82 / 100  # Context loading effectiveness
```

**Degradation Detection**:
```python
def detect_memory_degradation():
    """Monitor for memory system quality issues."""

    issues = []

    # Check checkpoint staleness
    latest = load_latest_checkpoint()
    days_since = (datetime.now() - latest["created"]).days
    if days_since > 7:
        issues.append(f"Checkpoint staleness: {days_since} days (target: <7)")

    # Check vector coverage
    checkpoint_count = count_checkpoints()
    vector_count = count_vectors("rhiz_memories")
    coverage = vector_count / checkpoint_count
    if coverage < 0.9:
        issues.append(f"Vector coverage: {coverage:.1%} (target: >90%)")

    # Check search quality
    test_queries = [
        "first trade execution",
        "infrastructure deployment",
        "threshold tuning accuracy"
    ]
    avg_precision = test_semantic_search(test_queries)
    if avg_precision < 0.8:
        issues.append(f"Search precision: {avg_precision:.1%} (target: >80%)")

    return issues
```

---

## Integration with Skill System

### Memory-Augmented Activation (Session 72)

**Pattern**: Skills load relevant memories at session start.

**Implementation**:
```python
# core/hooks/session_start.py

def load_skill_context_memory():
    """Load skill context from Mem0 based on latest checkpoint."""

    # Infer domains from latest checkpoint
    latest = load_latest_checkpoint()
    domains = latest["frontmatter"]["domains"]

    # Map domains to skills
    skills = {
        "trading": ["trading/kraken_analysis"],
        "memory": ["memory/session_management"],
        "infrastructure": ["infrastructure/deployment"]
    }

    # Load memories for active domains
    for domain in domains:
        if domain in skills:
            for skill_name in skills[domain]:
                memories = mem0_search(skill_name, limit=3)
                load_into_context(skill_name, memories)

    return f"Loaded {len(domains)} domain contexts"
```

**Outcome**: Skills activate with relevant past context (e.g., trading skill remembers circuit breaker preferences from Session 16).

---

## Storage & Performance

### Filesystem Organization

```
core/memory/checkpoints/
├── session_20251220_first_mate_initialization.yaml  (5KB)
├── session_20251226_wave2_first_trade.yaml          (12KB)
├── session_20260103_infrastructure_operational.yaml (15KB)
├── session_20260110_comprehensive_audit_wave.yaml   (18KB)
├── session_20260124_phase2_complete.yaml            (10KB)
└── ... (33 more checkpoints)

Total: 380KB (38 files)
Average: 10KB per checkpoint
```

**Growth Rate**: ~1 checkpoint per 1.05 days (38 checkpoints / 40 days) = ~350 checkpoints/year = ~3.5MB/year

**Scalability**: Not a concern. At current rate, 1000 checkpoints = ~10MB (years of work).

### Qdrant Performance

**Collection Stats** (`rhiz_memories`):
- **Vectors**: 161 points (38 checkpoints × ~4.2 chunks per checkpoint)
- **Index**: HNSW (fast approximate search)
- **Search latency**: 10-50ms (localhost)
- **Storage**: ~2MB (161 vectors × 384 dims × 4 bytes + metadata)

**Search Performance** (10 test queries):
- **Precision**: 88% (correct checkpoint in top-3 results)
- **Recall**: 94% (relevant checkpoints found)
- **Speed**: 23ms average (range: 10-45ms)

---

## Lessons Learned

### From 38 Sessions of Production Use

**1. YAML was the right choice**
- Git diffs are clean and reviewable
- Humans can read/edit checkpoints directly
- Multi-line narratives don't need escaping
- No regrets about JSON rejection

**2. Schema v1.0.0 addressed real gaps**
- `frontmatter.tags` enables filtering ("show me trading sessions")
- `blockers_encountered` surfaces patterns (Traefik networking appeared 3x)
- `critical_context` highlights essentials for resume
- No need for schema v2.0.0 yet

**3. 100% schema compliance is achievable**
- Automated validation on write prevents drift
- Template checkpoint file helps consistency
- Clear schema documentation (session_schema.yaml) as reference

**4. Checkpoint staleness detection matters**
- Jan 10 audit revealed 24-day CLAUDE.md staleness
- Forced sync protocol now established (quarterly or after pivots)
- Memory health score includes staleness metric

**5. Semantic search quality depends on content**
- Good: Session narratives, decisions, learnings (semantic signal)
- Poor: File paths, command outputs (literal matches better)
- Threshold tuning essential (0.45 for checkpoints, 0.25 for multi-component skills)

---

## Future Enhancements

### Schema v1.1.0 Additions (Planned - Phase 1.6)

**State Assertions**:
```yaml
session_metadata:
  system_health_score: float  # 0-100
  architectural_phase: str
```

**Cross-References**:
```yaml
session_arc:
  formalized_in: list[str]  # Paths to docs extracting this checkpoint's knowledge
  related_sessions: list[str]
```

**Component State**:
```yaml
component_state:
  deployments_changed: list[str]
  integrations_added: list[str]
  gaps_identified: list[str]
```

**Failure Genealogy**:
```yaml
failures:
  - approach: str
    failed_at: str
    reason: str
    pivot: str
    outcome: str
```

### Compression & Archival

**Current Strategy**: Keep all checkpoints indefinitely (380KB not a concern).

**Future** (if exceeds ~500MB):
- **Quarterly compression**: tar.gz old quarters (2025_q4.tar.gz)
- **Selective archival**: Move non-critical checkpoints to separate repo (rhiz_archive)
- **Narrative summaries**: Extract 10-page summary per quarter for quick reading

**No deletion**: All checkpoints preserved for failure genealogy and model training.

---

## Cross-References

**Source Checkpoint**:
- `core/memory/checkpoints/session_20251220_first_mate_initialization.yaml` (426 lines) - Genesis session establishing checkpoint pattern

**Related Documentation**:
- `core/memory/MEMORY_SYSTEM_GUIDE.md` - Operational guide for memory system usage
- `core/memory/session_schema.yaml` - Canonical schema definition (v1.0.0)
- `docs/sessions/session_72_self_reflection_enhanced.md` - Narrative compression essay exploring memory architecture

**Code Artifacts**:
- `core/hooks/session_start.py` - Session initialization hook (loads context)
- `core/hooks/session_end.py` - Checkpoint writing hook
- `tools/rhiz-mcp/checkpoint_search.py` - Semantic checkpoint search tool
- `tools/memory-mcp/` - Memory MCP server (Qdrant integration)

**Integration Points**:
- Skills system - Memory-augmented activation (Session 72)
- Strategic Intelligence Layer (SIL) - Decision history for pattern recognition
- Trading pipeline - Execution logging to memory (Session 16)

---

**End of Document**

*Extracted Session 74 (2026-01-25) as part of Phase 1.2: Extract Checkpoint Knowledge*
*This document preserves the memory system design rationale for future instances and architectural evolution.*
