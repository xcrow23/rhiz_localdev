#!/usr/bin/env python3
"""Test the exact query that session_start used."""

import sys
from pathlib import Path

RHIZ_ROOT = Path(__file__).parent
sys.path.insert(0, str(RHIZ_ROOT / "core" / "memory" / "scripts"))

from search import MemorySearcher

searcher = MemorySearcher(
    qdrant_host="localhost",
    qdrant_port=6333,
    collection_name="rhiz_memories"
)

# Exact query from .session_context.json
query = "recent session work, active domains, pending tasks"

print(f"Query: '{query}'")
print(f"Threshold: 0.3")

results = searcher.search(
    query=query,
    limit=3,
    section_filter="combined",  # session_start uses this
    score_threshold=0.3
)

print(f"\nResults: {len(results)}")

if len(results) == 0:
    print("\n[TRYING LOWER THRESHOLD]")
    results_low = searcher.search(query=query, limit=5, score_threshold=0.2)
    print(f"Threshold 0.2: {len(results_low)} results")

    if results_low:
        print(f"Top score: {results_low[0]['score']:.3f}")

else:
    for r in results:
        print(f"Score: {r['score']:.3f}, Session: {r['metadata'].get('source_file', 'unknown')}")
