"""
Quick connectivity test for Fathom Phase 1.

Tests:
- Public API connectivity (server time)
- System status
- Authenticated balance request
"""

import asyncio
import os
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from auth import CredentialManager
from clients.rest import KrakenRESTClient
from rate_limiter import RateLimiter


async def test_public_api(client: KrakenRESTClient):
    """Test public API endpoints."""
    print("\n=== Testing Public API ===")

    try:
        # Server time
        print("→ Getting server time...")
        server_time = await client.get_server_time()
        print(f"✓ Server time: {server_time.get('unixtime')}")

        # System status
        print("→ Getting system status...")
        status = await client.get_system_status()
        print(f"✓ System status: {status.get('status')}")

        # Ticker
        print("→ Getting BTC/USD ticker...")
        ticker = await client.get_ticker(["XBTUSD"])
        if ticker and "XXBTZUSD" in ticker:
            last_price = ticker["XXBTZUSD"]["c"][0]
            print(f"✓ BTC/USD last price: ${float(last_price):,.2f}")

        return True

    except Exception as e:
        print(f"✗ Public API error: {e}")
        return False


async def test_authenticated_api(client: KrakenRESTClient):
    """Test authenticated API endpoints."""
    print("\n=== Testing Authenticated API ===")

    try:
        # Balance
        print("→ Getting account balance...")
        balance = await client.get_account_balance()
        print(f"✓ Balance retrieved: {len(balance)} assets")

        for asset, amount in list(balance.items())[:3]:  # Show first 3
            print(f"  - {asset}: {amount}")

        return True

    except Exception as e:
        print(f"✗ Authenticated API error: {e}")
        return False


async def test_rate_limiter():
    """Test rate limiter."""
    print("\n=== Testing Rate Limiter ===")

    limiter = RateLimiter(tier="starter")

    # Check stats
    stats = limiter.get_stats()
    print(f"✓ Rate limiter initialized")
    print(f"  - Limit: {stats['limit']} calls/min")
    print(f"  - Remaining: {stats['remaining']}")

    # Simulate calls
    for i in range(3):
        can_proceed, wait_time = limiter.check_rate_limit()
        if can_proceed:
            limiter.record_call()
            print(f"  - Call {i+1} recorded")
        else:
            print(f"  - Would need to wait {wait_time:.2f}s")

    return True


async def main():
    """Run all tests."""
    print("=" * 60)
    print("FATHOM PHASE 1 CONNECTIVITY TEST")
    print("=" * 60)

    # Load environment
    print("\n→ Loading credentials from environment...")
    try:
        auth = CredentialManager()
        print("✓ Credentials loaded")
    except ValueError as e:
        print(f"✗ Credential error: {e}")
        print("\nSet environment variables:")
        print("  export FATHOM_KRAKEN_API_KEY='...'")
        print("  export FATHOM_KRAKEN_SECRET_KEY='...'")
        return

    # Initialize client
    client = KrakenRESTClient(auth=auth)

    try:
        # Run tests
        results = {
            "public_api": await test_public_api(client),
            "authenticated_api": await test_authenticated_api(client),
            "rate_limiter": await test_rate_limiter()
        }

        # Summary
        print("\n" + "=" * 60)
        print("SUMMARY")
        print("=" * 60)

        for test_name, passed in results.items():
            status = "✓ PASS" if passed else "✗ FAIL"
            print(f"{status} - {test_name}")

        all_passed = all(results.values())
        print("\n" + "=" * 60)

        if all_passed:
            print("🎉 ALL TESTS PASSED - Phase 1 foundation is working!")
        else:
            print("⚠️  SOME TESTS FAILED - Review errors above")

        print("=" * 60)

    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())
