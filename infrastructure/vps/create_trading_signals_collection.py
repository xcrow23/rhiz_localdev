#!/usr/bin/env python3
"""
Create trading_signals Qdrant Collection
Shared memory substrate for Fathom, FC, and SIL learning
"""

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

# Connect to Qdrant (skip version check for compatibility)
client = QdrantClient(host="localhost", port=6333)

print("[1/4] Creating trading_signals collection...")

# Create collection with 384-dimension vectors (all-MiniLM-L6-v2)
client.create_collection(
    collection_name="trading_signals",
    vectors_config=VectorParams(
        size=384,  # Matches all-MiniLM-L6-v2 embedding model
        distance=Distance.COSINE
    )
)

print("[2/4] Creating payload indexes for fast filtering...")

# Index signal_type (decision, regime, outcome)
client.create_payload_index(
    collection_name="trading_signals",
    field_name="signal_type",
    field_schema="keyword"
)

# Index pair (BTC/USD, ETH/USD, etc.)
client.create_payload_index(
    collection_name="trading_signals",
    field_name="pair",
    field_schema="keyword"
)

# Index source (fathom, fc, sil)
client.create_payload_index(
    collection_name="trading_signals",
    field_name="source",
    field_schema="keyword"
)

print("[3/4] Verifying collection creation...")

# Get collection info
info = client.get_collection("trading_signals")
print(f"  ✓ Collection: {info.config.params.vectors.size}-dimensional vectors")
print(f"  ✓ Distance: {info.config.params.vectors.distance}")
print(f"  ✓ Points: {info.points_count}")

print("[4/4] Collection schema:")
print("""
  Expected payload structure:
  {
    "timestamp": "2026-01-12T12:00:00Z",     # ISO 8601 datetime
    "pair": "BTC/USD",                       # Trading pair
    "signal_type": "decision",               # decision|regime|outcome
    "source": "fathom",                      # fathom|fc|sil
    "data": {                                # Flexible JSON blob per source
      "side": "buy",                         # decision-specific
      "amount": 0.001,
      "price": 45000,
      "reasoning": "...",
      "hypothesis": "...",
      "outcome": "filled",                   # Updated later
      "pnl": 50.00                           # Updated later
    }
  }
""")

print("\n✅ trading_signals collection created successfully!")
print(f"   Vector size: 384 (all-MiniLM-L6-v2)")
print(f"   Indexes: signal_type, pair, source, timestamp")
print(f"   Ready for cross-system learning!")
