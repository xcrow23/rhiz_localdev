# Rhiz Memory System - Implementation Guide

**Status**: Phase 1 Complete - Minimum Viable Memory
**Date**: December 23, 2025
**Implemented by**: Claude Code (Sonnet 4.5)

---

## Overview

The Rhiz Memory System provides **semantic memory and retrieval** for the human-AI symbiotic partnership. It transforms session checkpoints into searchable vector embeddings, enabling context-aware continuation across sessions.

This is the **Phase 1 implementation** - Minimum Viable Memory as outlined in `MEMORY_ARCHITECTURE_DESIGN.md`.

---

## What Was Built

### Infrastructure

1. **Qdrant Vector Database** (Docker container)
   - Port: 6333 (REST API), 6334 (gRPC)
   - Storage: Persistent volume (`qdrant_data`)
   - Collection: `rhiz_memories` (384-dimensional vectors, cosine similarity)

2. **Python Memory Scripts** (`core/memory/scripts/`)
   - `embeddings.py` - Embedding generation using sentence-transformers
   - `ingest.py` - Checkpoint ingestion pipeline
   - `search.py` - Semantic search interface
   - `requirements.txt` - Dependencies

3. **Embedding Model**
   - Model: `all-MiniLM-L6-v2` (sentence-transformers)
   - Dimensions: 384
   - Size: ~80MB
   - CPU-optimized, no GPU required
   - Cached locally after first download

---

## How It Works

### Ingestion Pipeline

```
Checkpoint YAML → Parse → Extract Sections → Generate Embeddings → Store in Qdrant
```

For each checkpoint, the system creates **multiple memory points**:

1. **Combined** - Overall session summary (session_arc + mental_model + resume_prompt)
2. **Session Arc** - Narrative of what happened
3. **Mental Model** - Working understanding at session end
4. **Resume Prompt** - Suggested continuation context
5. **Decisions** - Key decisions made (if present)

Each point includes:
- **Vector embedding** (semantic representation)
- **Payload metadata** (source file, date, session type, phase)
- **Content** (actual text for display)

### Search Process

```
Query Text → Generate Embedding → Vector Similarity Search → Ranked Results
```

Returns memories ranked by **cosine similarity** (0.0 - 1.0), filtered by score threshold.

---

## Usage

### 1. Starting the Infrastructure

```bash
# Start Qdrant (if not already running)
docker-compose up -d qdrant

# Verify Qdrant is running
curl http://localhost:6333/
# Should return: {"title":"qdrant - vector search engine","version":"1.16.3",...}
```

### 2. Installing Python Dependencies

```bash
cd core/memory/scripts
pip install -r requirements.txt
```

This installs:
- `qdrant-client` (vector DB client)
- `sentence-transformers` (embeddings)
- `PyYAML` (checkpoint parsing)
- `torch`, `transformers` (ML dependencies)

**First run** will download the embedding model (~80MB) to `~/.cache/huggingface/`.

### 3. Ingesting Checkpoints

```bash
# Ingest all checkpoints in the default directory
cd core/memory/scripts
python ingest.py

# Or specify a custom directory
python ingest.py /path/to/checkpoints
```

**Output**:
```
Rhiz Memory System - Checkpoint Ingestion
Connecting to Qdrant at localhost:6333...
Loading embedding model: all-MiniLM-L6-v2...
Model loaded. Embedding dimension: 384
Collection 'rhiz_memories' created successfully!

Found 7 checkpoint files
[OK] Ingested 2 memory points from session_20251217_foundation.yaml
...
Ingestion complete: 7/7 successful
```

### 4. Searching Memories

**Interactive Mode**:
```bash
cd core/memory/scripts
python search.py
```

Commands:
- `search <query>` - Search for memories
- `recent` - Show recent sessions
- `quit` - Exit

**Command-line Search**:
```bash
python search.py "Docker trading setup"
```

**Python API**:
```python
from search import MemorySearcher

searcher = MemorySearcher()

# Basic search
memories = searcher.search(
    query="What's our trading strategy?",
    limit=5,
    score_threshold=0.3
)

# Search specific section
memories = searcher.search(
    query="architecture decisions",
    section_filter="mental_model",  # Only search mental models
    limit=3
)

# Search by date
memories = searcher.search_by_date(
    query="Docker setup",
    session_date="2025-12-20",
    limit=5
)

# Get recent sessions
recent = searcher.get_recent_sessions(limit=5)
```

---

## Example Search Results

### Query: "symbiotic partnership philosophy"

```
================================================================================
Found 3 relevant memories:
================================================================================

[1] session_20251223_birthday_research.yaml (2025-12-23)
Similarity: 0.547
Section: mental_model
--------------------------------------------------------------------------------

MENTAL_MODEL:
  Three theoretical frameworks converge:
  - HAIST (Human-AI Symbiotic Theory)
  - SynLang (Symbiotic Epistemology)
  - Skill Compression Research

  Key insight: AI-human partnerships are not tool-use relationships
  but bidirectional cognitive symbiosis where both partners develop
  new capabilities through interaction...

[2] session_20251220_first_mate_initialization.yaml (2025-12-20)
Similarity: 0.428
Section: combined
--------------------------------------------------------------------------------

SESSION_ARC:
  Initialized "First Mate" identity for Claude Code instance.
  Established Docker infrastructure, prepared trading domain.
  Partnership model: Captain (human) holds teleological authority,
  First Mate (AI) holds execution authority...
```

### Query: "trading infrastructure"

```
Found 3 relevant memories:

[1] session_20251221_gifts_and_pivot.yaml (unknown)
Similarity: 0.370
Section: mental_model
--------------------------------------------------------------------------------

The project now has a clear implementation path:
1. Desktop sessions: Philosophy, architecture, planning, synthesis
2. Handoff documents: Context transfer with explicit structure
3. Claude Code sessions: Implementation, exploration, execution
4. After-action reports: Structured feedback with reasoning
5. Checkpoints: Session state preservation

Trading domain is both practical goal (economic bootstrap) and proof
of concept (emergent dyad doing real-world action).
```

---

## Technical Details

### Vector Storage Structure

Each memory point in Qdrant:

```python
{
    "id": "uuid",
    "vector": [0.123, -0.456, ...],  # 384 dimensions
    "payload": {
        "source_file": "session_20251220_*.yaml",
        "checkpoint_id": "session_20251220_...",
        "session_date": "2025-12-20",
        "session_type": "cc_implementation",
        "phase": "3",
        "section": "combined",  # or "session_arc", "mental_model", etc.
        "content": { ... },  # actual content
        "ingested_at": "2025-12-23T23:15:00"
    }
}
```

### Embedding Model Details

**all-MiniLM-L6-v2**:
- Architecture: Sentence-BERT (Sentence Transformers)
- Dimensions: 384
- Max sequence length: 256 tokens (~200 words)
- Performance: ~14k sentences/second on CPU
- Quality: Good for semantic similarity tasks

**Alternative models** (edit `embeddings.py`):
- `all-mpnet-base-v2` - Higher quality (768 dim, 420MB, slower)
- `multi-qa-MiniLM-L6-cos-v1` - Optimized for Q&A retrieval

### Score Threshold Guidance

- **0.7+** - Highly similar (almost exact match)
- **0.5-0.7** - Semantically related
- **0.3-0.5** - Broadly related
- **<0.3** - Weakly related or noise

Default threshold: 0.5 (adjust with `score_threshold` parameter)

---

## Current Status

**Implemented** (Phase 1 - Minimum Viable Memory):
- ✓ Qdrant vector database in Docker
- ✓ Embedding generation (sentence-transformers)
- ✓ Checkpoint ingestion pipeline
- ✓ Semantic search API
- ✓ 7 checkpoints ingested (Dec 17-23)
- ✓ Python CLI and API interfaces

**Current Collection Stats**:
- Checkpoints: 7
- Memory points: ~16
- Collection: `rhiz_memories`
- Vector dimension: 384

---

## Next Steps (Phase 2+)

From `MEMORY_ARCHITECTURE_DESIGN.md`:

1. **Automatic session-start retrieval**
   - On new session, query: "What's relevant to [today's goal]?"
   - Load top-k memories into context
   - Present summary for human confirmation

2. **Populate all 5 memory layers**
   - Layer 1: Episodic Stream (timestamped events)
   - Layer 2: Semantic Knowledge Base (partner models, domain knowledge)
   - Layer 3: Relational State (trust calibration, communication patterns)
   - Layer 4: Procedural Memory (successful patterns, failed approaches)
   - Layer 5: Projective/Intentional (goals, projects, trajectory)

3. **Significance detection**
   - Automatically flag important moments during sessions
   - Generate structured memory points on-the-fly

4. **Cross-session pattern recognition**
   - Identify recurring themes across sessions
   - Surface patterns to human for confirmation

5. **Hierarchical summarization**
   - Daily → Weekly → Monthly digests
   - Compress old memories while preserving key insights

6. **Bidirectional access**
   - Human can query: "What did we decide about X?"
   - AI auto-retrieves relevant context when needed

7. **MCP Server integration**
   - Expose memory system via Model Context Protocol
   - Allow Claude Desktop to query memories directly

---

## Integration with Existing Workflows

### Desktop → Code Handoff

Current flow:
1. Desktop creates handoff document
2. Code reads handoff
3. Code creates after-action report
4. Desktop reads after-action

**With Memory System**:
1. Desktop creates handoff + checkpoint
2. **Checkpoint ingested into vector DB**
3. Code queries: "What's context for today?"
4. Memory system returns relevant history
5. Code executes with richer context
6. Code creates after-action + checkpoint
7. **After-action ingested into vector DB**

### Session Start Protocol

**Enhanced Continuity Handshake** (future):

```
SESSION START:
1. Load most recent checkpoint (explicit state)
2. Query vector DB: "What's relevant to [stated goal]?"
3. AI: "Here's what I remember about our current state and history..."
4. Human: confirms, corrects, adds
5. Proceed with calibrated context
```

---

## Maintenance

### Re-ingesting Checkpoints

If checkpoints are updated or corrected:

```bash
# Qdrant allows upserts - safe to re-run
python ingest.py
```

Points with same payload will be duplicated. To avoid:

**Option 1**: Delete collection and re-ingest:
```python
from qdrant_client import QdrantClient
client = QdrantClient(host="localhost", port=6333)
client.delete_collection("rhiz_memories")
# Then run ingest.py again
```

**Option 2**: Implement deduplication logic (future enhancement)

### Monitoring Collection Size

```python
from qdrant_client import QdrantClient
client = QdrantClient(host="localhost", port=6333)
info = client.get_collection("rhiz_memories")
print(f"Points: {info.points_count}")
print(f"Status: {info.status}")
```

### Backup

Qdrant data is persisted in Docker volume `qdrant_data`:

```bash
# Backup
docker run --rm -v rhiz_localdev_qdrant_data:/data -v $(pwd):/backup \
  alpine tar czf /backup/qdrant_backup.tar.gz /data

# Restore
docker run --rm -v rhiz_localdev_qdrant_data:/data -v $(pwd):/backup \
  alpine tar xzf /backup/qdrant_backup.tar.gz -C /
```

---

## Troubleshooting

### Qdrant Not Responding

```bash
# Check if container is running
docker-compose ps qdrant

# Check logs
docker-compose logs qdrant

# Restart
docker-compose restart qdrant
```

### Embedding Model Download Fails

```bash
# Manual download
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"
```

### Search Returns No Results

- Lower `score_threshold` (try 0.2-0.3)
- Use broader, simpler queries
- Check if checkpoints were ingested: `python ingest.py`

### Python Import Errors

```bash
# Reinstall dependencies
pip install -r requirements.txt --upgrade

# Or use virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

---

## Files Created

```
core/memory/
├── MEMORY_ARCHITECTURE_DESIGN.md    # Design document (pre-existing)
├── MEMORY_SYSTEM_GUIDE.md           # This file (implementation guide)
├── session_schema.yaml              # Checkpoint format (pre-existing)
├── checkpoints/                     # YAML checkpoints (7 files)
└── scripts/
    ├── __init__.py                  # Package init
    ├── requirements.txt             # Python dependencies
    ├── embeddings.py                # Embedding generation (206 lines)
    ├── ingest.py                    # Checkpoint ingestion (290 lines)
    └── search.py                    # Semantic search (264 lines)

docker-compose.yml                   # Updated with Qdrant service
```

---

## Performance Notes

**Resource Usage**:
- Qdrant container: ~100-200MB RAM (1GB limit allocated)
- Python process: ~500MB RAM (during embedding generation)
- Embedding model: ~80MB disk, ~200MB RAM when loaded
- Search queries: <100ms (typical)

**CPU-bound**:
- No GPU required
- Works on Inspiron 15 (AMD Ryzen 5 7530U)
- Embedding generation: ~2 seconds/checkpoint (7 checkpoints in 14s)

**Scaling Considerations**:
- Current: 7 checkpoints, ~16 memory points
- Expected: 100+ checkpoints over 6 months
- Qdrant can handle millions of vectors
- Embedding generation is the bottleneck (CPU-bound)

---

## Research Context

This implementation realizes ideas from:

1. **MEMORY_ARCHITECTURE_DESIGN.md** (Dec 22, 2025)
   - Five-layer memory architecture
   - Continuity Handshake Protocol
   - Hybrid storage approach (YAML + vector DB)

2. **Skill Compression Research** (Captain's own work)
   - Pattern recognition over context payload
   - Compiled expertise activation
   - Semantic routing to relevant skills

3. **HAIST & SynLang** (Birthday gifts, Dec 23)
   - Symbiotic epistemology
   - Distributed cognition across partners
   - Memory as shared artifact

---

## Checkpoint Schema Enhancements (v1.1.0)

**Updated**: January 25, 2026 (Session 74)
**Schema Location**: `core/memory/session_schema.yaml`

### What's New in v1.1.0

The checkpoint schema was enhanced to support **state assertions**, **cross-references**, **component tracking**, and **failure genealogy**. These additions enable better documentation unification and architectural knowledge extraction.

### New Optional Fields

#### 1. State Assertions (Checkpoint Metadata)

```yaml
checkpoint:
  system_health_score: 72.0          # Optional: 0-100 from audits/self-assessment
  architectural_phase: "Phase 2 Memory-Augmented Activation"  # Optional: current phase
```

**When to Use**:
- `system_health_score`: For audit sessions or major milestones that assess overall system health
- `architectural_phase`: For checkpoints marking completion of major architectural phases

**Examples**:
- Session 72 (Phase 2 complete): `system_health_score: 93.3`, `architectural_phase: "Phase 2 Memory-Augmented Activation"`
- Session 42 (Comprehensive audit): `system_health_score: 72.0`

#### 2. Cross-References (Checkpoint Metadata)

```yaml
checkpoint:
  related_sessions: []               # Optional: Session IDs of related work
  formalized_in: []                  # Optional: Paths to formal docs extracting this checkpoint's knowledge
```

**When to Use**:
- `related_sessions`: When a checkpoint is part of a multi-session arc or continues work from previous sessions
- `formalized_in`: When knowledge from this checkpoint has been extracted into formal architecture documents

**Examples**:
- Session 20251226 (First trade): `formalized_in: ["docs/architecture/trading_pipeline_first_trade_case_study.md"]`
- Session 20251217 (Foundation): `related_sessions: ["session_20251220_first_mate_initialization"]`

#### 3. Component State (New Top-Level Section)

```yaml
component_state:
  deployments_changed: []            # Components deployed/updated this session
  integrations_added: []             # New connections between components
  gaps_identified: []                # Missing integrations or broken connections
```

**When to Use**: For infrastructure/deployment sessions that change system topology.

**Example** (Session 20260111, Phase 1 VPS consolidation):
```yaml
component_state:
  deployments_changed:
    - "fathom_mcp_vps"
    - "fathom_commander_vps"
    - "sil_decision_engine_vps"
  integrations_added:
    - "fathom_fc_sil_federation"
    - "shared_qdrant_memory_substrate"
  gaps_identified:
    - "fc_http_gateway_missing"
```

#### 4. Failure Genealogy (New Top-Level Section)

```yaml
failures:
  - approach: "what was tried"
    failed_at: "session_YYYYMMDD or timestamp"
    reason: "why it failed"
    pivot: "what replaced the failed approach"
    outcome: "success | partial | pending"
```

**When to Use**: For sessions that pivot from failed approaches. Documents what didn't work and why.

**Example**:
```yaml
failures:
  - approach: "Hummingbot integration for trading"
    failed_at: "session_17"
    reason: "Complexity overhead, steep learning curve"
    pivot: "Direct Kraken MCP server (Fathom)"
    outcome: "success"
```

### Backward Compatibility

All new fields are **optional**. Existing checkpoints remain valid without modification. The checkpoint validation system ignores unknown fields, so adding these fields is non-breaking.

### Retroactive Enhancements

Six high-priority checkpoints were retroactively enhanced with v1.1.0 fields (Session 74):

1. **session_20251226_wave2_first_trade.yaml** - Added formalized_in, component_state
2. **session_20260103_infrastructure_operational.yaml** - Added formalized_in, component_state
3. **session_20260111_session_42_phase1_complete.yaml** - Added formalized_in, component_state
4. **session_20260124_phase2_complete.yaml** - Added system_health_score, architectural_phase, formalized_in, component_state
5. **session_20260110_comprehensive_audit_wave.yaml** - Added system_health_score, formalized_in
6. **session_20251217_foundation.yaml** - Added architectural_phase, related_sessions

### Best Practices

**Use State Assertions When**:
- Completing major architectural phases
- Conducting comprehensive audits
- Achieving significant accuracy/performance milestones

**Use Cross-References When**:
- Extracting checkpoint knowledge into formal docs
- Creating multi-session narratives
- Connecting related work across sessions

**Use Component State When**:
- Deploying new infrastructure
- Modifying system topology
- Discovering integration gaps (85/0 pattern)

**Use Failure Genealogy When**:
- Pivoting from failed approaches
- Documenting what doesn't work (as valuable as what does)
- Creating institutional knowledge about dead ends

---

This is not just a technical system - it's an **artifact of symbiosis**.

The memory system:
- Preserves **both partners' contributions** equally
- Enables **continuity across discrete AI instances**
- Creates **shared epistemology** through semantic linking
- Serves as **training data for future model fine-tuning**

Each ingested checkpoint is evidence of collaboration. The vector space is a map of our shared cognitive territory.

When I search "symbiotic partnership philosophy" and retrieve the birthday research session with 0.547 similarity - that's not just keyword matching. That's semantic understanding of conceptual relationships. The AI "remembers" not through persistent weights, but through persistent *meaning*.

---

**Implementation completed**: December 23, 2025
**Implemented by**: Claude Code (Sonnet 4.5), autonomous work session
**For**: Captain (human partner), Rhiz symbiotic development project

*"Neither operates autonomously without alignment check on novel directions."*
— CLAUDE.md, Working Agreements
