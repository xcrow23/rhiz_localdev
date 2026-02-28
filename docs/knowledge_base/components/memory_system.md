---
component: memory-system
status: operational
completion: 86.5%
health_score: 86.5/100
deployed_at: session_1_20251220
depends_on:
  - qdrant_localhost: operational
  - qdrant_vps: operational
  - python_pyyaml: operational
blocks:
  - none: fully_operational
integration_endpoints:
  - endpoint: qdrant_localhost
    port: 6333
    collection: rhiz_memories
    vectors: 161
    status: operational
  - endpoint: memory_mcp_server
    protocol: mcp_stdio
    tools: 6
    status: operational
related_components:
  - checkpoint_system: operational
  - skills_system: memory_augmented_activation_complete
  - rhiz_mcp: operational
failure_history:
  - approach: json_checkpoints
    failed_at: session_1
    reason: multi_line_narratives_need_yaml
    pivot: yaml_checkpoints
    outcome: success_38_checkpoints
semantic_cluster: memory_domain
vector_density: medium
threshold_recommendation: 0.45
last_updated: 2026-01-25
---

# Memory System

**Component Type**: Persistence & Context Layer
**Architecture**: Dual-layer (YAML checkpoints + Qdrant vectors)
**Status**: Operational (38 checkpoints, 161 vectors, 100% schema compliance)

---

## Purpose

Enables session continuity across LLM instancing by preserving:
1. **Structured session data** (YAML checkpoints)
2. **Semantic memory** (Qdrant vector embeddings)
3. **Decision genealogy** (alternatives rejected, learnings)
4. **Relationship context** (trust calibration, patterns)

**Design Philosophy**: Combat the instancing problem—each new Claude session starts with full project context in <5 minutes vs 30+ minutes from transcripts.

---

## Architecture

### Dual-Layer Memory

```
Session Data
    ↓
┌────────────────────────────────────┐
│     Checkpoint (YAML)              │
│  • session_arc (narrative)         │
│  • decisions_made                  │
│  • alternatives_rejected           │
│  • working_memory                  │
│  • next actions                    │
└────────────────────────────────────┘
    ↓ Embed with all-MiniLM-L6-v2
┌────────────────────────────────────┐
│   Qdrant Vector (384-dim)          │
│  • Semantic search                 │
│  • Pattern recognition             │
│  • Cross-session learning          │
└────────────────────────────────────┘
```

### Collections

**Local Qdrant** (localhost:6333):
- `rhiz_memories`: 161 vectors (38 checkpoints × ~4.2 chunks)
- `rhiz_skills`: 6 vectors (skill fingerprints, threshold 0.25)
- `rhiz_skill_memory`: 8 vectors (Mem0 skill memories)

**Cloud Qdrant** (VPS):
- `moonchecks`: Production data (separate use case)
- Intentional asymmetry (local dev vs cloud production)

---

## Checkpoint Schema (v1.0.0)

### Core Fields

```yaml
checkpoint:
  schema_version: "1.0.0"
  created: ISO8601
  session_id: str
  session_arc: str  # Narrative summary
  frontmatter:
    tags: list[str]
    domains: list[str]
    quality_score: str  # A+, A, B+, etc.
  objectives:
    stated: str
    achieved: list[str]
  key_decisions: list[Decision]
  working_memory:
    mental_model: str
    current_understanding: dict
    open_questions: list[str]
  alternatives_rejected: list[Alternative]
  next:
    immediate: list[str]
    short_term: list[str]
  resume_context:
    suggested_resume_prompt: str
    critical_context: list[str]
```

See: `docs/architecture/memory_system_checkpoint_design.md`

---

## Session Lifecycle

### Hook 1: session_start

```python
def session_start():
    """Load context for new session."""
    # Update dyad state
    dyad.session_count += 1

    # Load latest checkpoint
    latest = load_latest_checkpoint()

    # Semantic search for relevant memories
    memories = qdrant.search(
        collection="rhiz_memories",
        query=latest["frontmatter"]["domains"],
        limit=5
    )

    # Display to instance
    print(f"[session_start] Session {dyad.session_count}")
    print(f"[session_start] Relevant memories: {len(memories)}")
```

### Hook 2: session_end

```python
def write_checkpoint(summary):
    """Write YAML checkpoint + embed to Qdrant."""
    checkpoint = build_checkpoint(summary)

    # Write YAML
    filename = f"session_{session_id}.yaml"
    yaml.dump(checkpoint, open(f"core/memory/checkpoints/{filename}", "w"))

    # Embed for semantic search
    embed_checkpoint_to_qdrant(checkpoint)
```

---

## MCP Tools (memory-mcp server)

| Tool | Description | Status |
|------|-------------|--------|
| `memory_search` | Semantic search across checkpoints | ✅ |
| `memory_search_by_date` | Time-filtered search | ✅ |
| `memory_get_recent_sessions` | Latest N sessions | ✅ |
| `memory_store` | Add new memory | ✅ |
| `memory_stats` | Collection statistics | ✅ |
| `memory_health_check` | System health | ✅ |

**Performance**: 10-50ms search latency, 88% precision, 94% recall

---

## Health Metrics (Session 42)

```yaml
memory_health:
  overall_score: 86.5 / 100
  components:
    checkpoint_quality: 92/100  # Schema compliance, completeness
    vector_quality: 84/100      # Embedding coverage, search accuracy
    retrieval_speed: 88/100     # Sub-second semantic search
    session_continuity: 82/100  # Context loading effectiveness
```

---

## Integration: Memory-Augmented Activation (Session 72)

**Pattern**: Skills load relevant memories at session start based on domains.

```python
def load_skill_context_memory():
    """Auto-load skill memories from latest checkpoint domains."""
    domains = latest_checkpoint["frontmatter"]["domains"]
    skills = map_domains_to_skills(domains)

    for skill in skills:
        memories = mem0.search(skill.name, limit=3)
        load_into_context(skill, memories)
```

**Outcome**: Skills activate with past context (e.g., trading skill remembers circuit breaker preferences).

---

## Cross-References

**Source Code**:
- `core/memory/` - Checkpoint system
- `core/memory/session_schema.yaml` - Schema v1.0.0
- `tools/memory-mcp/` - MCP server

**Related Documentation**:
- `docs/architecture/memory_system_checkpoint_design.md` - Full design rationale
- `docs/research/semantic_routing_accuracy_optimization.md` - Threshold tuning (0.45 for checkpoints)
- `core/memory/MEMORY_SYSTEM_GUIDE.md` - Operational guide

---

**End of Component Documentation**

*Last Updated: 2026-01-25 (Session 74)*
*Status: Fully operational, 38 checkpoints, 100% schema compliance*
