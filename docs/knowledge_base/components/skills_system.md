---
component: skills-system
status: operational
completion: 93.3%
routing_accuracy: 93.3%
deployed_at: session_72_20260124
depends_on:
  - qdrant_localhost: operational
  - mem0: operational
  - ollama: operational_qwen25coder
blocks:
  - skill_tool_binding: not_implemented
  - meta_skill_routing: needs_separate_threshold
integration_endpoints:
  - endpoint: semantic_router
    threshold: 0.25
    accuracy: 93.3%
    status: operational
  - endpoint: mem0_backend
    collection: rhiz_skill_memory
    vectors: 8
    status: operational
related_components:
  - memory_system: memory_augmented_activation_complete
  - rhiz_mcp: route_to_skill_tool_operational
failure_history:
  - approach: threshold_0_45_for_skills
    failed_at: session_71
    reason: multi_component_signal_dilution
    pivot: threshold_0_25
    outcome: 56_7_to_93_3_percent_accuracy
semantic_cluster: skills_domain
vector_density: medium
threshold_recommendation: 0.25
last_updated: 2026-01-25
---

# Skills System

**Component Type**: Semantic Routing & Activation Layer
**Architecture**: Qdrant fingerprints + Mem0 context + Self-RAG pattern
**Status**: Production-ready (93.3% routing accuracy, Phase 2 complete)

---

## Purpose

Enables **compiled expertise** through pattern recognition rather than context payload:

1. **Semantic routing** (query → skill matching via embeddings)
2. **Memory-augmented activation** (load relevant past context)
3. **Self-RAG** (heuristic retrieval decisions <5ms)
4. **Skill primitives** (reusable micro-functions)

**Design Philosophy**: Skills activate like muscle memory—fast pattern matching, not slow deliberation.

---

## Architecture

### Skill Activation Flow

```
User Query
    ↓
Semantic Routing (threshold 0.25)
    ↓
Skill Matched (93.3% accuracy)
    ↓
Self-RAG Decision (<5ms)
    ↓
Mem0 Context Load (200-500ms)
    ↓
Skill Activation + Primitives
    ↓
[MISSING: Tool Invocation - skill can't call MCP tools directly]
```

### Skill Fingerprint (Multi-Component Embedding)

```yaml
skill:
  name: trading/kraken_analysis
  description: "Analyzes market conditions for Kraken trading pairs"
  category: trading
  utterances:
    - "analyze market conditions"
    - "check trading position"
    - "what's my BTC balance"
    # ... 97 total across 6 skills
  tools:
    - get_account_balance
    - get_ticker
    - analyze_market_data
  primitives:
    - fetch_balance
    - calculate_position_size
    - check_circuit_breaker
```

**Embedded Together** → 384-dim vector → Stored in `rhiz_skills` collection

---

## Threshold Tuning Breakthrough (Session 72)

### Problem: Multi-Component Signal Dilution

**Initial Performance** (threshold 0.45):
- Accuracy: 56.7% (17/30 test cases)
- Issue: Skill fingerprints dilute signal across description + utterances + category + tools

**Discovery**: Multi-component embeddings score lower (0.25-0.70 range) vs single-text (0.40-1.0)

**Solution**: Lower threshold to 0.25

**Result**:
- Accuracy: **93.3% (28/30 correct)**
- False positives: 0
- Domain categories: 100% except ambiguous edge cases

**Learning**: Threshold must match vector topology. Skills (multi-component) need 0.25, checkpoints (single-text) need 0.45.

See: `docs/research/semantic_routing_accuracy_optimization.md`

---

## Active Skills (6 total)

| Skill | Utterances | Accuracy | Status |
|-------|-----------|----------|--------|
| trading/kraken_analysis | 25 | 100% | ✅ Operational |
| memory/session_management | 18 | 100% | ✅ Operational |
| memory/checkpoint_retrieval | 15 | 100% | ✅ Operational |
| research/documentation | 12 | 100% | ✅ Operational |
| infrastructure/deployment | 14 | 88.9% | ✅ Operational |
| infrastructure/troubleshooting | 13 | 92.3% | ✅ Operational |

**Total Utterances**: 97 (expanded from 45 during threshold tuning)

---

## Mem0 Integration (Phase 2)

### Configuration

```python
config = {
    "vector_store": {
        "provider": "qdrant",
        "config": {
            "collection_name": "rhiz_skill_memory",
            "host": "localhost",
            "port": 6333,
            "embedding_model_dims": 384  # Critical: match all-MiniLM-L6-v2
        }
    },
    "llm": {
        "provider": "ollama",
        "config": {
            "model": "qwen2.5-coder:7b",  # Captain's hardware guidance
            "temperature": 0.1
        }
    }
}
```

### Performance Metrics

- **Storage**: 2-3 seconds (LLM extraction overhead)
- **Search**: 200-500ms (acceptable for session start)
- **Initialization**: 500ms

**Trade-off**: Ollama slower than OpenAI API, but local, free, no external dependency.

---

## Self-RAG Pattern

### Heuristic Rules (not LLM-based)

```python
def should_retrieve_memory(skill_name: str, query: str) -> bool:
    # Skill-specific defaults
    if skill_name.startswith("trading/"):
        return True  # Trading always retrieves
    if skill_name.startswith("execution/"):
        return False  # Execution doesn't need context

    # Complexity heuristics
    if len(query.split()) > 15:
        return True

    complexity_keywords = ["analyze", "compare", "historical", "pattern"]
    if any(kw in query.lower() for kw in complexity_keywords):
        return True

    return False
```

**Result**: <5ms decision time, 100% accuracy (5/5 test cases)

**Rejected Alternative**: LLM-based Self-RAG (2-5s latency) - YAGNI for current use case

---

## Known Gaps

### Gap 1: Skill-Tool Binding (Missing)

**Issue**: Skills can activate with context but cannot invoke MCP tools directly

**Current Workaround**: Claude Code manually calls tools after skill activation

**Future**: Direct skill → tool invocation framework

### Gap 2: Meta-Skill Routing (Needs Separate Threshold)

**Issue**: Meta-queries ("how does the system work?") need threshold 0.15-0.20, not 0.25

**Impact**: Meta-cognitive queries may not match correctly

**Resolution**: Create "meta" skill category with lower threshold

---

## Cross-References

**Source Code**:
- `core/skills/` - Skill system
- `core/skills/registry/` - Skill definitions
- `core/skills/router.py` - Semantic routing (threshold 0.25)

**Related Documentation**:
- `docs/research/semantic_routing_accuracy_optimization.md` - Threshold tuning breakthrough
- `core/skills/SKILL_ROUTER_GUIDE.md` - Operational guide

---

**End of Component Documentation**

*Last Updated: 2026-01-25 (Session 74)*
*Status: Production-ready, 93.3% accuracy, tool binding gap*
