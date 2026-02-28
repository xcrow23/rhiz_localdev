"""
Pattern Ingestion for Rhiz Memory System
Ingests Strudel MCP patterns into Qdrant for semantic search.

Usage:
    python ingest_patterns.py [patterns_dir] [--qdrant-url URL]

Example:
    python ingest_patterns.py "../../Gifts_From_Alex/strudel-mcp-server-main/patterns/examples"
    python ingest_patterns.py --qdrant-url localhost:6333
"""

import argparse
import glob
import hashlib
import json
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory for imports
sys.path.insert(0, str(Path(__file__).parent))

from embeddings import create_embedder

try:
    from qdrant_client import QdrantClient
    from qdrant_client.models import PointStruct, VectorParams, Distance
except ImportError:
    print("Error: qdrant-client not installed. Run: pip install qdrant-client")
    sys.exit(1)


def hash_id(text: str) -> int:
    """Create numeric ID from string for Qdrant."""
    return int(hashlib.md5(text.encode()).hexdigest()[:16], 16)


def build_embed_text(pattern: dict) -> str:
    """Build text for embedding from pattern metadata."""
    genre = pattern.get("genre", "unknown")
    key = pattern.get("key", "C")
    bpm = pattern.get("bpm", 120)
    description = pattern.get("description", "")
    tags = ", ".join(pattern.get("tags", []))

    return f"{genre} pattern in {key} at {bpm} BPM. {description}. Tags: {tags}."


def load_patterns(patterns_dir: str) -> list:
    """Load all JSON pattern files from directory."""
    patterns = []
    pattern_files = glob.glob(f"{patterns_dir}/**/*.json", recursive=True)

    for pattern_file in pattern_files:
        try:
            with open(pattern_file, 'r', encoding='utf-8') as f:
                pattern = json.load(f)
                pattern['_source_file'] = pattern_file
                patterns.append(pattern)
                print(f"  Loaded: {pattern.get('name', 'unknown')} ({pattern.get('genre', 'unknown')})")
        except json.JSONDecodeError as e:
            print(f"  Warning: Could not parse {pattern_file}: {e}")
        except Exception as e:
            print(f"  Warning: Error loading {pattern_file}: {e}")

    return patterns


def ensure_collection(client: QdrantClient, collection_name: str, vector_size: int):
    """Ensure collection exists with correct settings."""
    collections = client.get_collections().collections
    collection_names = [c.name for c in collections]

    if collection_name not in collection_names:
        print(f"Creating collection: {collection_name}")
        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE)
        )
    else:
        print(f"Collection exists: {collection_name}")


def ingest_patterns(patterns_dir: str, qdrant_url: str = "localhost:6333"):
    """Ingest Strudel patterns into Rhiz memory system."""

    print(f"\n{'='*60}")
    print("RHIZ PATTERN INGESTION")
    print(f"{'='*60}\n")

    # Parse URL
    if ':' in qdrant_url:
        host, port = qdrant_url.split(':')
        port = int(port)
    else:
        host = qdrant_url
        port = 6333

    print(f"Connecting to Qdrant at {host}:{port}...")

    try:
        client = QdrantClient(host=host, port=port)
        # Test connection
        client.get_collections()
        print("Connected to Qdrant.\n")
    except Exception as e:
        print(f"Error connecting to Qdrant: {e}")
        print("\nMake sure Qdrant is running. You can start it with:")
        print("  docker run -p 6333:6333 qdrant/qdrant")
        return

    # Load embedding model
    print("Loading embedding model...")
    embedder = create_embedder()
    print(f"Model loaded. Dimension: {embedder.get_dimension()}\n")

    # Load patterns
    print(f"Loading patterns from: {patterns_dir}")
    patterns = load_patterns(patterns_dir)
    print(f"\nLoaded {len(patterns)} patterns.\n")

    if not patterns:
        print("No patterns found. Check the directory path.")
        return

    # Ensure collection exists
    collection_name = "rhiz_memories"
    ensure_collection(client, collection_name, embedder.get_dimension())

    # Build points
    print("\nGenerating embeddings and building points...")
    points = []

    for pattern in patterns:
        # Build embedding text
        embed_text = build_embed_text(pattern)
        embedding = embedder.embed(embed_text)

        # Create unique ID
        pattern_id = f"pattern_{pattern.get('genre', 'unknown')}_{pattern.get('name', 'unknown')}"

        point = PointStruct(
            id=hash_id(pattern_id),
            vector=embedding.tolist(),
            payload={
                "type": "musical_pattern",
                "name": pattern.get("name"),
                "genre": pattern.get("genre"),
                "bpm": pattern.get("bpm"),
                "key": pattern.get("key"),
                "description": pattern.get("description", ""),
                "tags": pattern.get("tags", []),
                "pattern_code": pattern.get("pattern", ""),
                "source_file": pattern.get("_source_file"),
                "timestamp": pattern.get("timestamp"),
                "ingested_at": datetime.utcnow().isoformat()
            }
        )
        points.append(point)
        print(f"  Embedded: {pattern.get('name')} -> {len(embedding)} dims")

    # Upsert to Qdrant
    print(f"\nUpserting {len(points)} patterns to Qdrant...")
    client.upsert(collection_name=collection_name, points=points)
    print("Done!\n")

    # Summary
    print(f"{'='*60}")
    print("INGESTION COMPLETE")
    print(f"{'='*60}")
    print(f"Patterns ingested: {len(points)}")
    print(f"Collection: {collection_name}")
    print(f"Vector dimension: {embedder.get_dimension()}")

    # Show what was ingested
    genres = {}
    for p in patterns:
        genre = p.get('genre', 'unknown')
        genres[genre] = genres.get(genre, 0) + 1

    print("\nBy genre:")
    for genre, count in sorted(genres.items()):
        print(f"  {genre}: {count}")


def main():
    parser = argparse.ArgumentParser(description="Ingest Strudel patterns into Rhiz memory")
    parser.add_argument(
        "patterns_dir",
        nargs="?",
        default=str(Path(__file__).parent.parent.parent.parent / "Gifts_From_Alex" / "strudel-mcp-server-main" / "patterns" / "examples"),
        help="Directory containing pattern JSON files"
    )
    parser.add_argument(
        "--qdrant-url",
        default="localhost:6333",
        help="Qdrant server URL (default: localhost:6333)"
    )

    args = parser.parse_args()

    # Resolve path
    patterns_dir = Path(args.patterns_dir).resolve()

    if not patterns_dir.exists():
        print(f"Error: Directory not found: {patterns_dir}")
        sys.exit(1)

    ingest_patterns(str(patterns_dir), args.qdrant_url)


if __name__ == "__main__":
    main()
