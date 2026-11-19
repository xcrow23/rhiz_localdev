# Rhiz Memory MCP Server

Model Context Protocol (MCP) server providing semantic memory access to the Rhiz session history stored in Qdrant.

## Overview

The Memory MCP Server gives Claude Code direct access to our session memories through semantic search, enabling:
- Pattern recognition across conversations
- Retrieval of past decisions and reasoning
- Learning from documented experiences
- Context-aware session continuation

## Architecture

```
Memory MCP Server
├── Semantic Search (vector similarity)
├── Date-filtered Search
├── Recent Session Retrieval
├── Memory Storage
└── Database Statistics
```

**Backend**: Qdrant vector database (localhost:6333)
**Embeddings**: all-MiniLM-L6-v2 (384-dim, CPU-optimized)
**Collection**: rhiz_memories (161 points as of 2025-12-28)

## Tools Provided

### 1. `memory_search`
Search the memory system semantically.

**Parameters**:
- `query` (required): Natural language search query
- `limit` (optional): Max results (default: 5)
- `section_filter` (optional): Filter by section type
  - Options: combined, session_arc, mental_model, hypotheses, questions, decisions, resume_prompt
- `score_threshold` (optional): Minimum similarity (0-1, default: 0.5)

**Example**:
```json
{
  "query": "How did we set up the trading pipeline?",
  "limit": 3,
  "section_filter": "combined"
}
```

### 2. `memory_search_by_date`
Search memories from a specific session.

**Parameters**:
- `query` (required): Search query
- `session_date` (required): Date in YYYYMMDD format (e.g., "20251227")
- `limit` (optional): Max results (default: 5)

**Example**:
```json
{
  "query": "Fathom implementation",
  "session_date": "20251226"
}
```

### 3. `memory_get_recent_sessions`
Get recent session summaries.

**Parameters**:
- `limit` (optional): Number of sessions (default: 3)

**Example**:
```json
{
  "limit": 5
}
```

### 4. `memory_store`
Store a new memory manually.

**Parameters**:
- `content` (required): Memory content
- `metadata` (optional): Metadata object
  - `session_date`: Session date
  - `section`: Section type
  - `checkpoint_id`: Checkpoint ID
  - `phase`: Project phase
  - `source_file`: Source file name

**Example**:
```json
{
  "content": "Realized that memory MCP server enables compiled expertise patterns",
  "metadata": {
    "session_date": "20251228",
    "section": "insights",
    "checkpoint_id": "session_20251228_memory_mcp"
  }
}
```

### 5. `memory_stats`
Get database statistics.

**Parameters**: None

**Returns**: Collection info, point count, vector dimension, status.

### 6. `memory_health_check`
Check system health.

**Parameters**: None

**Returns**: Connectivity status for Qdrant, embedder, searcher.

## Installation

1. Install dependencies:
```bash
cd tools/memory-mcp
pip install -r requirements.txt
```

2. Verify Qdrant is running:
```bash
docker ps | grep qdrant
# Should show rhiz_qdrant container on port 6333
```

3. Test the server:
```bash
python server.py
# Should initialize without errors
```

## Configuration

Environment variables:
- `QDRANT_HOST`: Qdrant host (default: localhost)
- `QDRANT_PORT`: Qdrant port (default: 6333)
- `COLLECTION_NAME`: Collection name (default: rhiz_memories)

## Usage with Claude Code

Add to your Claude Code MCP configuration (typically `~/.config/claude/mcp.json` or similar):

```json
{
  "mcpServers": {
    "rhiz-memory": {
      "command": "python",
      "args": ["/mnt/c/Users/dread/documents/Rhiz/origin/tools/memory-mcp/server.py"],
      "env": {
        "QDRANT_HOST": "localhost",
        "QDRANT_PORT": "6333"
      }
    }
  }
}
```

Then restart Claude Code to load the server.

## Memory Data Model

Each memory point contains:
- **Vector**: 384-dimensional embedding
- **Content**: Memory text (string or structured dict)
- **Metadata**:
  - `source_file`: Origin checkpoint file
  - `session_date`: Session date (YYYYMMDD)
  - `section`: Section type (combined, session_arc, etc.)
  - `checkpoint_id`: Checkpoint identifier
  - `phase`: Project phase

## Integration with Checkpoint System

The MCP server reads from the same Qdrant instance populated by:
- `core/memory/scripts/ingest.py` - Ingests YAML checkpoints
- `core/memory/scripts/embeddings.py` - Generates embeddings
- `core/memory/checkpoints/` - Source YAML files

**Workflow**:
1. Session ends → Create checkpoint YAML
2. Run ingest.py → Embed & store in Qdrant
3. Next session → MCP server provides semantic access
4. Claude searches past decisions/patterns during work

## Performance

**Search Speed**: ~100ms for semantic search (5 results)
**Embedding Generation**: ~50ms per query (CPU-bound)
**Memory Footprint**: ~500MB (model + Qdrant client)

Optimized for the Dell Inspiron 15 3535 (16GB RAM, AMD Ryzen 5 7530U).

## Troubleshooting

**"Qdrant connection failed"**
- Check Docker: `docker ps | grep qdrant`
- Start if needed: `docker-compose up -d qdrant`

**"No memories found"**
- Verify collection exists: Check `core/memory/scripts/search.py`
- Run ingest: `cd core/memory/scripts && python ingest.py`

**"Embedding model download failed"**
- Requires internet on first run (downloads ~80MB)
- Model cached to `~/.cache/huggingface/`

## Future Enhancements

- [ ] Time-weighted search (recent memories score higher)
- [ ] Cross-reference between related sessions
- [ ] Automatic memory consolidation (merge similar memories)
- [ ] Export/import memory snapshots
- [ ] Integration with cloud Qdrant sync

## Related Documentation

- `core/memory/MEMORY_ARCHITECTURE_DESIGN.md` - Five-layer architecture
- `core/memory/MEMORY_SYSTEM_GUIDE.md` - Implementation guide
- `core/memory/session_schema.yaml` - Checkpoint schema
- `CLAUDE.md` - Project context and philosophy

---

**Status**: Production Ready
**Last Updated**: 2025-12-28
**Maintainer**: Captain & First Mate (Rhiz Symbiotic Partnership)
