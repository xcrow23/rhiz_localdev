# Rhiz Memory Hybrid Search Architecture

**Version:** 1.0
**Date:** 2026-01-24
**Status:** Production-ready

## Overview

Rhiz memory system implements **hybrid search** - a "doubled up searching" approach combining semantic vector similarity with structured keyword filtering for maximum precision and recall.

## Problem Statement

### Initial Issues

1. **Score Threshold Mismatch**
   - Default thresholds: 0.5 (general search), 0.6 (auto-context)
   - all-MiniLM-L6-v2 actual scores: 0.25-0.47 for relevant matches
   - Result: All searches returned 0 results despite valid data

2. **Limited Search Precision**
   - Pure semantic search lacks precise domain/topic filtering
   - Couldn't answer queries like "show all trading decisions" or "find infrastructure blockers"
   - No way to filter by patterns used, technical stack, or decision types

3. **Hardware Constraints**
   - CPU-bound laptop (Dell Inspiron 15 3535, no GPU)
   - Must use lightweight embedding model (all-MiniLM-L6-v2, 384-dim)
   - Cannot switch to larger models that produce higher similarity scores

## Solution Architecture

### 1. Threshold Tuning

**Empirical Analysis:**
```
Query: "trading SIL infrastructure deployment"
Top results with threshold=0.0:
  0.470 - session_20260103_infrastructure_operational.yaml
  0.371 - session_20251226_wave2_first_trade.yaml
  0.343 - session_20251226_bridge_continuation.yaml
  0.313 - session_20260106_memory_automation_complete.yaml
```

**Decision:**
- General search: `score_threshold = 0.25` (was 0.5)
- Auto-context retrieval: `score_threshold = 0.30` (was 0.6)

**Rationale:**
- Matches empirical score distribution from all-MiniLM-L6-v2
- Preserves precision (0.25 eliminates noise) while enabling recall
- 0.30 for auto-context maintains higher bar for session startup

### 2. Frontmatter Metadata Schema

**Location:** `core/memory/frontmatter_schema.yaml`

**Key Fields:**
```yaml
frontmatter:
  domains: ["trading", "infrastructure", "memory"]     # Domain tags
  keywords: ["qdrant", "vector-search", "threshold"]  # Semantic keywords
  session_type:
    primary: "build"                                   # Session classification
    secondary: ["debug", "research"]
  technical_stack:
    languages: ["python", "yaml"]
    frameworks: ["qdrant", "fastapi"]
    services: ["cloudflare-workers", "vps"]
    tools: ["mcp-server", "docker"]
  patterns_used:                                       # Dyadic patterns
    - pattern_name: "context_alignment"
      usage_note: "Optional context"
  blockers_resolved:                                   # Blocker types
    - type: "configuration"
      description: "Brief description"
  decision_types: ["architectural", "technical"]       # Decision categories
  discoveries: ["Finding or insight"]                  # Key learnings
  completeness:
    status: "complete"                                 # Session outcome
  notable:
    is_notable: true                                   # Flag exemplary sessions
    reason: "Why notable"
```

**Design Principles:**
- Optional (backward compatible)
- Human-writable + auto-generatable
- Structured for Qdrant payload filtering
- Extensible for future metadata

### 3. Enhanced Ingestion

**File:** `core/memory/scripts/ingest.py`

**Metadata Extraction:**
```python
# Extract frontmatter (backward compatible)
frontmatter = checkpoint.get("frontmatter", {})

# Flatten to Qdrant payload fields
metadata["domains"] = frontmatter.get("domains", [])
metadata["keywords"] = frontmatter.get("keywords", [])
metadata["patterns_used"] = [...]
metadata["decision_types"] = frontmatter.get("decision_types", [])
# ... etc
```

**Backward Compatibility:**
- Existing checkpoints without frontmatter get empty arrays `[]`
- Search works on all checkpoints (filters just don't match old ones)
- No breaking changes to schema

### 4. Hybrid Search Implementation

**File:** `core/memory/scripts/search.py`

**Method Signature:**
```python
def hybrid_search(
    self,
    query: str,                              # Semantic search
    limit: int = 5,
    score_threshold: float = 0.25,
    # Keyword filters
    domains: Optional[List[str]] = None,
    keywords: Optional[List[str]] = None,
    patterns: Optional[List[str]] = None,
    decision_types: Optional[List[str]] = None,
    session_type: Optional[str] = None,
    is_notable: Optional[bool] = None
) -> List[Dict]:
```

**Filter Logic:**
```python
# Build Qdrant filters (AND logic)
filter_conditions = []

if domains:
    filter_conditions.append(
        FieldCondition(key="domains", match=MatchAny(any=domains))
    )

if keywords:
    filter_conditions.append(
        FieldCondition(key="keywords", match=MatchAny(any=keywords))
    )

# Combine with semantic search
search_filter = Filter(must=filter_conditions) if filter_conditions else None
results = client.query_points(
    collection_name=self.collection_name,
    query=query_vector,
    query_filter=search_filter,
    ...
)
```

**Combination Strategy:**
1. Generate embedding for semantic query
2. Build keyword filters (MatchAny for arrays, MatchValue for scalars)
3. Combine filters with AND logic (all must match)
4. Execute Qdrant query with both vector + filter
5. Return results meeting both semantic AND keyword criteria

### 5. MCP Tool Exposure

**File:** `tools/rhiz-mcp/src/server.py`

**New Tool:** `hybrid_search_checkpoints`

```json
{
  "name": "hybrid_search_checkpoints",
  "description": "Hybrid semantic + keyword search with frontmatter filtering",
  "inputSchema": {
    "query": "string (required)",
    "limit": "number",
    "domains": "array<string>",
    "keywords": "array<string>",
    "patterns": "array<string>",
    "threshold": "number"
  }
}
```

**Usage:**
```python
# Via MCP tool
result = mcp_client.call_tool(
    "hybrid_search_checkpoints",
    query="memory system architecture",
    domains=["infrastructure"],
    keywords=["qdrant", "vector-search"],
    limit=5
)
```

## Usage Examples

### Example 1: Semantic Search Only
```python
from search import MemorySearcher

searcher = MemorySearcher()
results = searcher.search(
    query="trading strategy decisions",
    limit=5
)
# Returns all checkpoints semantically similar to query
```

### Example 2: Domain Filtering
```python
results = searcher.hybrid_search(
    query="deployment",
    domains=["infrastructure"],
    limit=5
)
# Returns only infrastructure-domain checkpoints about deployment
```

### Example 3: Multi-Filter Precision
```python
results = searcher.hybrid_search(
    query="API integration",
    domains=["trading"],
    keywords=["kraken"],
    patterns=["context_alignment"],
    decision_types=["architectural"],
    limit=3
)
# Returns trading sessions about Kraken API with architectural decisions
# that used context_alignment pattern
```

### Example 4: Find Notable Sessions
```python
results = searcher.hybrid_search(
    query="architecture design",
    is_notable=True,
    limit=5
)
# Returns only sessions flagged as notable/exemplary
```

### Example 5: Technical Stack Search
```python
# Note: Currently requires using search() with payload inspection
# Future enhancement: Add tech_stack filter to hybrid_search
results = searcher.hybrid_search(
    query="cloud deployment",
    keywords=["cloudflare-workers", "fastapi"],
    limit=5
)
```

## Performance Characteristics

### Qdrant Collection Stats
- **Points:** 118+ checkpoints (growing)
- **Vectors:** 384-dim (all-MiniLM-L6-v2)
- **Indexing:** Brute-force for <10k points (fast enough)
- **Latency:** <100ms per search on local instance

### Score Distribution (all-MiniLM-L6-v2)
- **High relevance:** 0.35 - 0.47
- **Medium relevance:** 0.25 - 0.35
- **Low relevance:** <0.25 (filtered)

### Precision vs Recall Trade-offs
- **Pure semantic (threshold=0.25):** High recall, moderate precision
- **Hybrid (semantic + 1 filter):** Balanced recall/precision
- **Hybrid (semantic + 3+ filters):** High precision, lower recall

## Design Decisions

### 1. Why Not Larger Embedding Model?
**Decision:** Stick with all-MiniLM-L6-v2
**Rationale:**
- CPU-bound hardware (no GPU)
- 384-dim optimal for resource constraints
- Hybrid approach compensates for lower similarity scores
- Model switch would require re-embedding all checkpoints

**Trade-off:** Lower similarity scores vs resource efficiency

### 2. Why Frontmatter vs Separate Metadata Files?
**Decision:** YAML frontmatter section in checkpoint
**Rationale:**
- Single-file simplicity (no file coordination)
- Human-readable and editable
- Backward compatible (optional section)
- Easy to version control alongside checkpoint content

**Trade-off:** Larger checkpoint files vs architectural simplicity

### 3. Why MatchAny vs MatchAll for Keyword Arrays?
**Decision:** MatchAny (OR logic within array)
**Rationale:**
- `keywords: ["qdrant", "vector-search"]` means "has qdrant OR vector-search"
- More permissive for recall
- User can specify multiple filters for precision (domains AND keywords)

**Trade-off:** Individual array OR logic vs strict AND logic

### 4. Why Separate hybrid_search() Method?
**Decision:** New method, not replace search()
**Rationale:**
- Preserves simple semantic-only search
- Hybrid is opt-in for when precision matters
- Clearer API (explicit about filtering)

**Trade-off:** Two methods vs single overloaded method

## Future Enhancements

### 1. Auto-Generate Frontmatter
```python
# Use LLM to extract metadata from checkpoint content
def auto_generate_frontmatter(checkpoint: dict) -> dict:
    # Extract keywords from session_arc, decisions, artifacts
    # Classify session_type from progress narrative
    # Identify patterns from relational_state
    return frontmatter
```

### 2. Temporal Filtering
```python
results = searcher.hybrid_search(
    query="infrastructure work",
    date_range=("2026-01-01", "2026-01-31"),
    limit=5
)
```

### 3. Technical Stack Filtering
```python
results = searcher.hybrid_search(
    query="deployment",
    languages=["python"],
    frameworks=["fastapi"],
    services=["cloudflare-workers"]
)
```

### 4. Session Graph Traversal
```python
# Use related_sessions field to build session dependency graph
# Enable "show me all sessions related to SIL deployment"
```

### 5. Keyword Expansion
```python
# Expand "qdrant" to include "vector-database", "similarity-search"
# Use embedding similarity on keywords themselves
```

## Implementation Checklist

- [x] Analyze score threshold mismatch
- [x] Design frontmatter schema
- [x] Update session_schema.yaml
- [x] Enhance ingest.py for frontmatter extraction
- [x] Implement hybrid_search() in search.py
- [x] Add hybrid_search_checkpoints() to memory_search.py
- [x] Expose tool in rhiz-mcp server.py
- [x] Create checkpoint template
- [x] Test with sample frontmatter checkpoint
- [x] Validate filtering precision
- [x] Document architecture and usage
- [ ] Re-ingest existing checkpoints (optional)
- [ ] Auto-generate frontmatter (future)

## Testing Results

### Threshold Fix Validation
```
Query: "trading SIL deployment"
Before (threshold=0.5): 0 results
After (threshold=0.25): 5 results (0.39-0.44 scores)
✅ PASS
```

### Frontmatter Ingestion
```
Checkpoint: session_20260124_memory_hybrid_search.yaml
Frontmatter: domains=["infrastructure","memory"], keywords=[6 items]
Ingested: 3 memory points
✅ PASS
```

### Hybrid Search Filtering
```
Query: "memory system"
Filters: domains=["infrastructure"], keywords=["qdrant"]
Results: 3 (all match filters)
✅ PASS
```

### Filter Exclusion
```
Query: "memory system"
Filters: domains=["trading"], keywords=["kraken"]
Results: 0 (correct exclusion)
✅ PASS
```

## Maintenance Notes

### Threshold Tuning Process
1. Run empirical query: `searcher.search(query, threshold=0.0, limit=20)`
2. Analyze score distribution
3. Set threshold at ~10th percentile of relevant matches
4. Update constants in `search.py` and `memory_search.py`

### Adding New Frontmatter Fields
1. Update `frontmatter_schema.yaml`
2. Add extraction logic in `ingest.py` metadata section
3. Add filter parameter to `hybrid_search()` if needed
4. Update MCP tool schema in `server.py`
5. Document in this file

### Re-Ingesting Checkpoints
```bash
cd core/memory/scripts
python ingest.py ../checkpoints/
```
- Qdrant upserts by ID, so re-ingestion updates existing points
- Safe to run multiple times
- Consider adding auto-frontmatter generation before re-ingestion

## References

- **Frontmatter Schema:** `core/memory/frontmatter_schema.yaml`
- **Checkpoint Template:** `core/memory/checkpoint_template_with_frontmatter.yaml`
- **Ingestion Code:** `core/memory/scripts/ingest.py`
- **Search Code:** `core/memory/scripts/search.py`
- **MCP Server:** `tools/rhiz-mcp/src/server.py`
- **Qdrant Docs:** https://qdrant.tech/documentation/concepts/filtering/

---

**Author:** First Mate (Claude Sonnet 4.5)
**Session:** session_20260124_memory_hybrid_search
**Reviewed by:** Captain (pending)
