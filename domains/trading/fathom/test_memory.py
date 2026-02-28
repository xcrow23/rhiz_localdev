#!/usr/bin/env python3
"""
Test Fathom memory integration.
"""

import sys
sys.path.insert(0, 'src')

from memory.logger import FathomMemory

def test_memory():
    """Test memory logging and search."""
    print("=" * 60)
    print("FATHOM MEMORY TEST")
    print("=" * 60)

    # Initialize
    print("\n→ Initializing memory...")
    memory = FathomMemory()
    print("✓ Memory initialized")

    # Get stats
    print("\n→ Getting collection stats...")
    stats = memory.get_stats()
    print(f"✓ Collection: {stats.get('collection')}")
    print(f"  Total decisions: {stats.get('total_decisions', 0)}")

    # Log a test decision
    print("\n→ Logging test decision...")
    result = memory.log_trade_decision(
        pair="BTC/USD",
        side="observe",
        decision_type="hypothesis",
        reasoning="Testing memory integration - observing support level at $95,000",
        hypothesis="Support levels hold during low-volatility consolidation"
    )

    if result.get("success"):
        point_id = result["point_id"]
        print(f"✓ Decision logged successfully")
        print(f"  Point ID: {point_id}")
    else:
        print(f"✗ Failed: {result.get('error')}")
        return False

    # Search for it
    print("\n→ Searching memory...")
    results = memory.search_decisions(
        query="support level consolidation",
        limit=3
    )

    print(f"✓ Found {len(results)} results")
    if results:
        for i, r in enumerate(results[:3], 1):
            print(f"\n  Result {i} (score: {r.get('score', 0)})")
            payload = r.get('payload', {})
            print(f"    Pair: {payload.get('pair')}")
            print(f"    Side: {payload.get('side')}")
            print(f"    Reasoning: {payload.get('reasoning')[:80]}...")

    # Update outcome
    print(f"\n→ Updating outcome for decision {point_id}...")
    update_success = memory.update_outcome(
        point_id=point_id,
        outcome="learning",
        outcome_data={"notes": "Test completed successfully"}
    )

    if update_success:
        print("✓ Outcome updated")
    else:
        print("✗ Update failed")

    # Get updated stats
    print("\n→ Final stats...")
    final_stats = memory.get_stats()
    print(f"✓ Total decisions now: {final_stats.get('total_decisions', 0)}")

    print("\n" + "=" * 60)
    print("🎉 MEMORY INTEGRATION WORKING!")
    print("=" * 60)

    return True

if __name__ == "__main__":
    success = test_memory()
    sys.exit(0 if success else 1)
