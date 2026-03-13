#!/usr/bin/env python3
"""Test that metadata extraction is working correctly."""

import sys
from pathlib import Path

RHIZ_ROOT = Path(__file__).parent
sys.path.insert(0, str(RHIZ_ROOT / "core" / "memory" / "scripts"))

from search import MemorySearcher

searcher = MemorySearcher()

# Test 1: Check metadata fields
print("=== Testing Metadata Extraction ===\n")
result = searcher.search('trading', limit=1)
if result:
    metadata = result[0]['metadata']
    print(f"Source: {metadata.get('source_file', 'N/A')}")
    print(f"Checkpoint ID: {metadata.get('checkpoint_id', 'N/A')}")
    print(f"Session Date: {metadata.get('session_date', 'N/A')}")
    print(f"Phase: {metadata.get('phase', 'N/A')}")
    print()

    if metadata.get('checkpoint_id') != "unknown":
        print("[OK] checkpoint_id extraction WORKING")
    else:
        print("[FAIL] checkpoint_id still unknown")

    if metadata.get('session_date') != "unknown":
        print("[OK] session_date extraction WORKING")
    else:
        print("[FAIL] session_date still unknown")

# Test 2: Check domain inference
print("\n=== Testing Domain Inference ===\n")
from qdrant_client import QdrantClient
client = QdrantClient(host="localhost", port=6333)
points = client.scroll(collection_name="rhiz_memories", limit=5)[0]

for point in points:
    domains = point.payload.get("domains", [])
    source = point.payload.get("source_file", "unknown")
    print(f"{source}: domains = {domains}")

print("\n[OK] If domains are non-empty arrays above, inference is working!")
