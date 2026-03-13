#!/usr/bin/env python3
"""Test local Qdrant search to diagnose why session_start returns 0 results."""

import sys
from pathlib import Path

# Add paths
RHIZ_ROOT = Path(__file__).parent
sys.path.insert(0, str(RHIZ_ROOT / "core" / "memory" / "scripts"))

from search import MemorySearcher

print("[TEST] Initializing MemorySearcher for localhost:6333...")
searcher = MemorySearcher(
    qdrant_host="localhost",
    qdrant_port=6333,
    collection_name="rhiz_memories"
)

# Test search with simple query
test_query = "trading Kraken Fathom integration"
print(f"[TEST] Searching for: '{test_query}'")
print(f"[TEST] Threshold: 0.3, Limit: 3")

try:
    results = searcher.search(
        query=test_query,
        limit=3,
        score_threshold=0.3
    )

    print(f"\n[RESULT] Found {len(results)} results\n")

    if len(results) == 0:
        print("[WARN] Zero results despite 124 points in Qdrant!")
        print("[TEST] Trying lower threshold (0.2)...")
        results_low = searcher.search(
            query=test_query,
            limit=3,
            score_threshold=0.2
        )
        print(f"[RESULT] With threshold=0.2: {len(results_low)} results")

        if len(results_low) > 0:
            print("\n=== Top Result (threshold 0.2) ===")
            r = results_low[0]
            print(f"Score: {r['score']:.3f}")
            print(f"Session: {r['metadata'].get('session_date', 'unknown')}")
            print(f"Section: {r['metadata'].get('section', 'unknown')}")
            print(f"Content: {r['content'][:200]}...")
    else:
        for i, result in enumerate(results, 1):
            print(f"=== Result {i} ===")
            print(f"Result keys: {result.keys()}")
            print(f"Score: {result.get('score', 'N/A')}")
            print(f"Metadata: {result.get('metadata', {})}")
            # Content might be under different key
            content = result.get('content') or result.get('text') or str(result.get('payload', ''))
            if content and len(content) > 200:
                print(f"Content: {content[:200]}...")
            else:
                print(f"Content: {content}")
            print()

except Exception as e:
    print(f"[ERROR] Search failed: {e}")
    import traceback
    traceback.print_exc()
