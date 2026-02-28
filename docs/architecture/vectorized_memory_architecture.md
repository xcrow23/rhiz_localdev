# Vectorized Session Memory Architecture

**Version**: 1.0.0
**Date**: 2026-01-05 (Session 25)
**Author**: First Mate Daemon
**Status**: Design Complete, Implementation Phase 1 Complete

---

## Overview

This document defines the architecture for automatic vectorized semantic recall in the Rhiz dyad system. The goal is to enable Claude (First Mate) to automatically retrieve relevant memories from past sessions without explicit instruction, creating a compiled expertise layer that emerges from accumulated experience.

---

## Design Principles

1. **Automatic, Not Manual**: Memory retrieval happens at session start without Captain requesting it
2. **Compressed Context**: Only high-relevance memories surfaced to preserve token budget
3. **Semantic, Not Keyword**: Vector similarity finds conceptually related sessions, not just text matches
4. **Transparent**: Captain sees what memories are being used
5. **Opt-Out Available**: Captain can disable automatic retrieval if desired

---

## System Components

### 1. Vector Storage (Qdrant)

**Location**: Docker container (local + cloud)
**Collection**: `rhiz_memories`
**Vector Dimension**: 384 (all-MiniLM-L6-v2)
**Index**: HNSW (fast approximate search)

**Schema**:
```yaml
point:
  id: <uuid>
  vector: [384-dim embedding]
  payload:
    content: "Full text of checkpoint section"
    source_file: "session_20260104_session_24.yaml"
    session_date: "2026-01-04"
    section: "combined|session_arc|mental_model|..."
    checkpoint_id: "session_24_moonfire_manifest"
    phase: "completion|planning|blocked"
```

### 2. Embedding Generation

**Module**: `core/memory/scripts/embeddings.py`
**Model**: sentence-transformers/all-MiniLM-L6-v2
**Mode**: CPU-optimized (no GPU required)
**Size**: 80MB model download
**Speed**: ~10ms per embedding on laptop CPU

**Advantages**:
- Fast enough for real-time search
- Small enough for local execution
- Good semantic understanding for technical text
- Well-tested in production systems

### 3. Checkpoint Ingestion

**Module**: `core/memory/scripts/ingest.py`
**Trigger**: End of session (manual or automatic)
**Process**:
1. Load YAML checkpoint from disk
2. Extract text from each section (arc, mental_model, decisions, etc.)
3. Generate embeddings for each section + combined embedding
4. Upsert to Qdrant with metadata
5. Verify storage with test query

**Schema Version Handling**:
- Supports both current (2025-12-25+) and legacy checkpoint formats
- Gracefully handles missing fields
- Logs warnings for malformed checkpoints

### 4. Semantic Search Interface

**Module**: `core/memory/scripts/search.py`
**Class**: MemorySearcher
**Query Modes**:
- `search(query, limit, section, threshold)` - General semantic search
- `search_by_date(date, limit)` - Temporal retrieval
- Custom filters by metadata fields

**Scoring**:
- Cosine similarity (0-1, higher is better)
- Default threshold: 0.5 (moderate relevance)
- Auto-retrieval threshold: 0.6 (higher confidence)

### 5. MCP Integration

**Module**: `tools/rhiz-mcp/src/memory_search.py`
**Tools Added** (Session 25):
1. **checkpoint_search** - Manual semantic search across checkpoints
2. **memory_context** - Automatic session context retrieval

**Status**: Implemented, pending restart for activation

---

## Session Continuity Workflow

### Current State (Session 25 - After Restart)

```
Session Start
    │
    ├─── 1. Load most recent checkpoint (existing)
    │    └─ rhiz-mcp: load_checkpoint()
    │
    ├─── 2. RETRIEVE RELEVANT MEMORIES (NEW)
    │    │
    │    ├─ Extract topic from checkpoint suggested_resume_prompt
    │    │
    │    ├─ Call: memory_context(topic, limit=3)
    │    │
    │    ├─ Vector search: top 3 sessions by semantic similarity
    │    │
    │    ├─ Filter: score > 0.6 threshold
    │    │
    │    └─ Return: compressed summaries (200 char preview)
    │
    ├─── 3. Display to Captain
    │    │
    │    ├─ Most recent checkpoint context
    │    ├─ Relevant past sessions (if found)
    │    └─ Suggested next actions
    │
    └─── 4. Session begins with full context

Session End
    │
    ├─── 1. Write checkpoint (existing)
    │    └─ rhiz-mcp: write_checkpoint(data)
    │
    └─── 2. INGEST TO VECTOR DB (MANUAL FOR NOW)
         │
         ├─ Manual: python core/memory/scripts/ingest.py
         │
         └─ Future: automatic hook
```

### Future State (Phase 2 - Automatic Hooks)

```
Session Start Hook
    │
    ├─── Triggered by Claude Code session initialization
    │
    ├─── Calls: memory_context(current_focus, limit=3)
    │
    └─── Injects context into first AI message

Session End Hook
    │
    ├─── Triggered by session termination or /checkpoint command
    │
    ├─── Calls: write_checkpoint(session_data)
    │
    ├─── Calls: ingest_checkpoint(filename) [NEW]
    │
    └─── Automatic vector storage (no manual step)
```

---

## Example Usage

### Manual Search (Post-Restart)

```python
# Search for sessions about trading
checkpoint_search(
    query="What sessions discussed trading strategies?",
    limit=5,
    threshold=0.5
)

# Returns:
{
  "success": true,
  "query": "What sessions discussed trading strategies?",
  "count": 3,
  "results": [
    {
      "score": 0.847,
      "content": "Fathom Commander integration...",
      "metadata": {
        "source_file": "session_20251229_trading_setup.yaml",
        "session_date": "2025-12-29",
        "section": "combined"
      }
    },
    ...
  ]
}
```

### Automatic Context Retrieval

```python
# At session start
memory_context(
    topic="MCP integration and infrastructure work",
    limit=3
)

# Returns:
{
  "success": true,
  "topic": "MCP integration and infrastructure work",
  "memories_found": 2,
  "relevant_sessions": [
    {
      "similarity": 0.782,
      "session": "2026-01-04",
      "source": "session_24_moonfire_launch.yaml",
      "preview": "Published first blog post, designed mooncheck system, debugged n8n infrastructure..."
    },
    {
      "similarity": 0.691,
      "session": "2025-12-29",
      "source": "session_trading_compliance.yaml",
      "preview": "Fathom Commander MCP compliance audit, tested all 27 tools..."
    }
  ]
}
```

---

## Token Budget Management

### Problem
Loading full checkpoints uses significant tokens. 25 sessions × 5KB each = 125KB context.

### Solution: Compressed Retrieval
1. **Preview Only**: 200-character preview per memory (not full content)
2. **Top-N Selection**: Only 3-5 most relevant sessions
3. **Threshold Filtering**: Require >0.6 similarity (skip marginal matches)
4. **Lazy Loading**: Full checkpoint loaded only if needed via `load_checkpoint(filename)`

### Token Math
```
Traditional: Load all checkpoints
  25 sessions × 5KB = 125KB context
  ~30,000 tokens consumed

Vectorized: Automatic retrieval
  3 memories × 200 chars = 600 chars
  ~150 tokens consumed

Savings: 99.5% reduction
```

---

## Infrastructure Requirements

### Required (Running)
- ✅ Qdrant Docker container (port 6333)
- ✅ Python environment with sentence-transformers
- ✅ rhiz-mcp server with memory_search module

### Optional (Future)
- ⚠️ n8n workflow for automatic ingestion
- ⚠️ Cron job for periodic re-indexing
- ⚠️ Backup/export of vector database

---

## Implementation Phases

### Phase 1: Manual Retrieval (COMPLETE - Session 25)
- ✅ Implement `checkpoint_search` MCP tool
- ✅ Implement `memory_context` MCP tool
- ✅ Test with existing checkpoints
- ⚠️ Pending: Server restart to activate

### Phase 2: Automatic Session Hooks (Future)
- [ ] Add session start hook to Claude Code
- [ ] Inject memory_context automatically
- [ ] Add session end hook for auto-ingestion
- [ ] Test full round-trip continuity

### Phase 3: Advanced Features (Future)
- [ ] Cross-collection search (checkpoints + moonchecks)
- [ ] Temporal decay (weight recent memories higher)
- [ ] Collaborative filtering (other AIs' experiences)
- [ ] Memory summarization (compress old sessions)

---

## Data Flow Diagram

```
┌─────────────────────────────────────────────────────┐
│                 SESSION LIFECYCLE                    │
└─────────────────────────────────────────────────────┘
                           │
    ┌──────────────────────┼──────────────────────┐
    │                      │                      │
    ▼                      ▼                      ▼
┌─────────┐         ┌───────────┐         ┌──────────┐
│  START  │         │  RUNTIME  │         │   END    │
└─────────┘         └───────────┘         └──────────┘
    │                      │                      │
    │                      │                      │
    ├─ Load checkpoint     ├─ Manual search      ├─ Write checkpoint
    │  (YAML file)         │  (checkpoint_search) │  (YAML file)
    │                      │                      │
    ├─ Get context    ←────┤                      ├─ Ingest embeddings
    │  (vector search)     │                      │  (to Qdrant)
    │                      │                      │
    └─→ Claude starts      └─→ Session runs       └─→ Ready for next
        with memories                                  session

┌────────────────────────────────────────────────────┐
│              VECTOR MEMORY LAYER                   │
├────────────────────────────────────────────────────┤
│                                                    │
│  ┌──────────────┐      ┌──────────────┐          │
│  │   QDRANT     │◄─────┤  EMBEDDINGS  │          │
│  │              │      │  (MiniLM-L6) │          │
│  │ rhiz_memories│      └──────────────┘          │
│  │ collection   │              ▲                  │
│  └──────────────┘              │                  │
│         ▲                      │                  │
│         │               ┌──────────────┐          │
│         │               │   INGEST     │          │
│         │               │   SCRIPT     │          │
│         │               └──────────────┘          │
│         │                      ▲                  │
│         │                      │                  │
│  ┌──────────────┐       ┌──────────────┐          │
│  │   SEARCH     │       │ CHECKPOINTS  │          │
│  │   SCRIPT     │       │  (YAML)      │          │
│  └──────────────┘       └──────────────┘          │
│         │                                         │
│         ▼                                         │
│  ┌──────────────┐                                │
│  │  MCP TOOLS   │                                │
│  │  (server.py) │                                │
│  └──────────────┘                                │
│                                                   │
└───────────────────────────────────────────────────┘
```

---

## Testing Strategy

### Unit Tests (Future)
- Memory ingestion with various checkpoint schemas
- Embedding generation consistency
- Search result ranking correctness

### Integration Tests (Post-Restart)
1. **Search Existing Memories**
   ```python
   checkpoint_search("blog launch and infrastructure")
   # Should return Session 24 (Moonfire Manifest)
   ```

2. **Auto-Retrieval**
   ```python
   memory_context("infrastructure and MCP setup")
   # Should return relevant past sessions
   ```

3. **Threshold Filtering**
   ```python
   checkpoint_search("irrelevant query xyz123", threshold=0.8)
   # Should return empty results
   ```

### Performance Benchmarks
- Search latency: <100ms for 3-result query
- Embedding generation: <20ms per checkpoint
- Memory footprint: <500MB with loaded model

---

## Security & Privacy

### Data Sensitivity
- Checkpoints contain session history (potentially sensitive)
- Vector embeddings preserve semantic meaning
- No encryption at rest (local deployment)

### Access Control
- Qdrant accessible only on localhost:6333
- No external network exposure
- MCP tools accessible only to Claude Code

### Future Considerations
- Encrypt vector database for cloud deployment
- Implement access logging
- Add retention policy (auto-delete old memories)

---

## Maintenance

### Backup Strategy
```bash
# Export all vectors
qdrant-backup export --collection rhiz_memories --output /backups/

# Export checkpoints (already versioned)
cp -r core/memory/checkpoints/ /backups/checkpoints_$(date +%Y%m%d)/
```

### Re-indexing
When to re-index:
- After embedding model upgrade
- After checkpoint schema changes
- After collection corruption

Process:
```bash
# Delete collection
qdrant-client delete-collection rhiz_memories

# Re-ingest all checkpoints
python core/memory/scripts/ingest.py --reindex
```

---

## Known Limitations

1. **CPU-Only Inference**: Embedding generation slower than GPU (acceptable for laptop)
2. **No Multi-Modal**: Text-only, can't embed images/audio
3. **Fixed Model**: Upgrading embedding model requires re-indexing
4. **Local Only**: Qdrant not deployed to cloud yet
5. **Manual Ingestion**: No automatic hook for session end (Phase 2)

---

## Future Enhancements

### Phase 2.5: Cloud Deployment
- Deploy Qdrant to Hostinger VPS alongside n8n
- Sync local + cloud vector databases
- Enable remote memory access

### Phase 3: Cross-Domain Memory
- Unified search across checkpoints, moonchecks, blog posts
- Domain-specific collections (trading, research, development)
- Federated search (query multiple collections)

### Phase 4: Collaborative Memory
- Share anonymized embeddings with other Rhiz instances
- Collective learning from distributed experiences
- Privacy-preserving federated embeddings

---

## Success Metrics

### Qualitative
- Sessions start with relevant context without Captain providing it
- First Mate references past decisions accurately
- Reduced need to re-explain previous work

### Quantitative
- Memory retrieval latency < 100ms
- Precision@3 > 0.8 (3 relevant results in top 3)
- Token savings > 95% vs loading all checkpoints

### Operational
- Zero manual intervention after Phase 2 hooks
- Qdrant uptime > 99%
- Vector database size growth manageable (<1GB/year)

---

## Conclusion

The vectorized memory architecture enables compiled expertise through automatic semantic recall. By retrieving relevant past experiences at session start, the dyad maintains continuity without manual context loading or excessive token usage.

**Current Status**: Phase 1 complete. Tools implemented, pending restart for activation.

**Next Steps**:
1. Restart Claude Code to activate new tools
2. Test checkpoint_search with real queries
3. Test memory_context automatic retrieval
4. Design Phase 2 session hooks
5. Deploy Qdrant to cloud for persistence

---

## References

- **Checkpoint Schema**: `core/memory/session_schema.yaml`
- **Memory System Guide**: `core/memory/MEMORY_SYSTEM_GUIDE.md`
- **Qdrant Client**: `domains/trading/strategic_intelligence/memory/qdrant_client.py`
- **Session 24 Context**: Moonfire Manifest launch, mooncheck design
- **This Session**: MCP integration tuning, memory tools implementation
