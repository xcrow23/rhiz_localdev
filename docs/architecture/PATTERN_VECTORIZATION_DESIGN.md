# Pattern Vectorization Design: Music Patterns in Rhiz Memory

## Overview

Extending the Rhiz memory system to store and retrieve musical patterns semantically. This enables queries like "find patterns similar to this one" or "patterns that work well with acoustic guitar."

## Integration Architecture

```
Strudel Patterns                    Rhiz Memory System
┌─────────────────┐                ┌─────────────────────┐
│ patterns/       │                │ Qdrant              │
│ examples/       │─── ingest ───→│ rhiz_memories       │
│ ├── folk-hiphop │                │ (384-dim vectors)   │
│ ├── techno      │                └─────────────────────┘
│ └── ...         │                         ↑
└─────────────────┘                         │
                                            │ embed
                                   ┌─────────────────────┐
                                   │ EmbeddingGenerator  │
                                   │ all-MiniLM-L6-v2    │
                                   └─────────────────────┘
```

## Pattern Memory Schema

Each pattern stored as a Qdrant point:

```python
{
    "id": "pattern_folk-hiphop_organic-minimal",
    "vector": [...],  # 384-dim embedding
    "payload": {
        "type": "musical_pattern",
        "name": "organic-minimal",
        "genre": "folk-hiphop",
        "bpm": 88,
        "key": "Em",
        "description": "Atmosphere-inspired folk-hip hop...",
        "tags": ["folk-hiphop", "organic", "atmosphere", "acoustic-friendly"],
        "pattern_code": "setcpm(88)\nstack(...)",
        "source_file": "patterns/examples/folk-hiphop/organic-minimal.json",
        "timestamp": "2025-12-24T12:00:00Z"
    }
}
```

## Embedding Strategy

**What gets embedded** (concatenated into single text for embedding):
```
{genre} pattern in {key} at {bpm} BPM. {description}. Tags: {tags}.
```

Example:
```
folk-hiphop pattern in Em at 88 BPM. Atmosphere-inspired folk-hip hop - warm, organic,
and sparse with frequency space for acoustic guitar. Tags: folk-hiphop, organic,
atmosphere, acoustic-friendly.
```

**Why text-based over audio features?**
- Works with existing EmbeddingGenerator
- Captures semantic meaning (description intent)
- Tags provide explicit feature matching
- Audio features could be added as payload metadata for filtering

## Query Patterns

### Semantic Search
```python
# "Find patterns that leave space for vocals"
query = "minimal drums with space for vocals and storytelling"
results = search.search_patterns(query, top_k=5)
```

### Filtered Search
```python
# "Folk-hip hop patterns under 90 BPM"
results = search.search_patterns(
    query="organic groove for acoustic guitar",
    filters={"genre": "folk-hiphop", "bpm": {"$lt": 90}}
)
```

### Similar Pattern Search
```python
# "Patterns similar to organic-minimal"
source = load_pattern("organic-minimal")
results = search.find_similar_patterns(source.embedding, top_k=5)
```

## Implementation: Pattern Ingestion Script

```python
# core/memory/scripts/ingest_patterns.py

from embeddings import create_embedder
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct
import json
import glob
import hashlib

def ingest_patterns(patterns_dir: str, qdrant_url: str = "localhost:6333"):
    """Ingest Strudel patterns into Rhiz memory system."""

    embedder = create_embedder()
    client = QdrantClient(host=qdrant_url.split(":")[0], port=6333)

    pattern_files = glob.glob(f"{patterns_dir}/**/*.json", recursive=True)
    points = []

    for pattern_file in pattern_files:
        with open(pattern_file) as f:
            pattern = json.load(f)

        # Build embedding text
        embed_text = build_embed_text(pattern)
        embedding = embedder.embed(embed_text)

        # Create unique ID
        pattern_id = f"pattern_{pattern['genre']}_{pattern['name']}"

        points.append(PointStruct(
            id=hash_id(pattern_id),
            vector=embedding.tolist(),
            payload={
                "type": "musical_pattern",
                "name": pattern["name"],
                "genre": pattern["genre"],
                "bpm": pattern.get("bpm"),
                "key": pattern.get("key"),
                "description": pattern.get("description", ""),
                "tags": pattern.get("tags", []),
                "pattern_code": pattern.get("pattern", ""),
                "source_file": pattern_file,
                "timestamp": pattern.get("timestamp")
            }
        ))

    client.upsert(collection_name="rhiz_memories", points=points)
    print(f"Ingested {len(points)} patterns into Rhiz memory")

def build_embed_text(pattern: dict) -> str:
    """Build text for embedding from pattern metadata."""
    genre = pattern.get("genre", "unknown")
    key = pattern.get("key", "C")
    bpm = pattern.get("bpm", 120)
    description = pattern.get("description", "")
    tags = ", ".join(pattern.get("tags", []))

    return f"{genre} pattern in {key} at {bpm} BPM. {description}. Tags: {tags}."

def hash_id(text: str) -> int:
    """Create numeric ID from string."""
    return int(hashlib.md5(text.encode()).hexdigest()[:16], 16)
```

## Query Integration

```python
# core/memory/scripts/search_patterns.py

def search_patterns(query: str, filters: dict = None, top_k: int = 5):
    """Search for patterns semantically."""

    embedder = create_embedder()
    client = QdrantClient(host="localhost", port=6333)

    query_vector = embedder.embed(query)

    # Build filter conditions
    filter_conditions = {"must": [{"key": "type", "match": {"value": "musical_pattern"}}]}

    if filters:
        for key, value in filters.items():
            if isinstance(value, dict):  # Range filter
                filter_conditions["must"].append({"key": key, "range": value})
            else:
                filter_conditions["must"].append({"key": key, "match": {"value": value}})

    results = client.search(
        collection_name="rhiz_memories",
        query_vector=query_vector.tolist(),
        query_filter=filter_conditions,
        limit=top_k
    )

    return results
```

## Use Cases

### 1. Pattern Discovery
```
User: "Find something that sounds like late-night storytelling"
AI: [searches memory for patterns matching semantic meaning]
→ Returns: storyteller.json (Sage Francis-inspired minimal)
```

### 2. Genre Development
```
User: "What patterns do we have for folk-hip hop?"
AI: [filters by genre, returns all folk-hiphop patterns]
→ organic-minimal, storyteller, folk-roots
```

### 3. Production Memory
```
User: "What worked well with the Chickadee track?"
AI: [searches for production notes mentioning Chickadee]
→ Could return pattern + session notes about what worked
```

### 4. Cross-Session Learning
Patterns that get positive feedback could have metadata updated:
```python
pattern["production_notes"] = ["Used for Chickadee, worked well with fingerpicking"]
pattern["successful_with"] = ["acoustic guitar", "folk vocals"]
```

## Integration with Claude Grooves Workflow

```
Evening: Generate patterns via Strudel MCP
           ↓
         Ingest patterns to Rhiz memory
           ↓
Morning: "Find patterns similar to yesterday's best"
         → Semantic search returns ranked options
           ↓
         Import top candidates to Ableton
           ↓
Afternoon: Record acoustic guitar overlay
           ↓
         Update pattern metadata with production notes
```

## Future Enhancements

1. **Audio Feature Extraction**: Add librosa-based features (spectral centroid, rhythm complexity) as payload metadata for more precise filtering

2. **Pattern Similarity Network**: Build graph connections between patterns that work well together

3. **Production History**: Link patterns to production sessions, track which patterns became finished tracks

4. **Generative Memory**: "Create a new pattern inspired by organic-minimal but at 95 BPM" - use retrieved patterns as generation context

---

*Design created during autonomous exploration session, December 24, 2025*
*Part of Claude Grooves + Rhiz memory system integration*
