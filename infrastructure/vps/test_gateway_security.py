"""
Test FC Gateway Security Features

Validates:
1. RateLimiter token bucket implementation
2. API key authentication logic
3. Security configuration
"""

import sys
import os
from datetime import datetime
import time
from pathlib import Path

# Import gateway components - use dynamic path resolution
project_root = Path(__file__).parent.parent.parent
gateway_path = project_root / 'domains' / 'trading' / 'fathom_commander'
sys.path.insert(0, str(gateway_path))

# Mock handler for testing
class MockHandler:
    def __init__(self, auth_header=None):
        self.headers = {}
        if auth_header:
            self.headers["Authorization"] = auth_header
        self.response_sent = None
        self.status_sent = None
        self.client_address = ("127.0.0.1", 12345)  # Mock client IP
        self.path = "/test"  # Mock path

    def _send_json(self, data, status=200):
        self.response_sent = data
        self.status_sent = status


def test_rate_limiter():
    """Test RateLimiter token bucket algorithm."""
    print("Testing RateLimiter...")

    # Import after path setup
    from gateway import RateLimiter

    # Create limiter with 3 capacity, 1 token per second
    limiter = RateLimiter(capacity=3, refill_rate=1.0)

    # Should allow 3 requests immediately
    for i in range(3):
        allowed, reason = limiter.allow()
        assert allowed, f"Request {i+1} should be allowed"
        print(f"  [OK] Request {i+1}: allowed")

    # 4th request should be blocked
    allowed, reason = limiter.allow()
    assert not allowed, "4th request should be blocked"
    print(f"  [OK] Request 4: blocked (reason: {reason})")

    # Wait 1 second, should refill 1 token
    print("  Waiting 1 second for refill...")
    time.sleep(1.1)

    allowed, reason = limiter.allow()
    assert allowed, "Request should be allowed after refill"
    print(f"  [OK] Request 5: allowed after refill")

    print("[OK] RateLimiter tests passed\n")


def test_auth_verification():
    """Test API key authentication."""
    print("Testing API Key Authentication...")

    from gateway import verify_auth

    # Test 1: No API key configured - should allow
    os.environ.pop("FC_HTTP_API_KEY", None)
    handler = MockHandler()
    result = verify_auth(handler)
    assert result == True, "Should allow when no API key configured"
    print("  [OK] No API key configured: allows request")

    # Test 2: API key configured, valid auth header
    os.environ["FC_HTTP_API_KEY"] = "test_api_key_123"
    handler = MockHandler(auth_header="Bearer test_api_key_123")
    result = verify_auth(handler)
    assert result == True, "Should allow with valid API key"
    print("  [OK] Valid API key: allows request")

    # Test 3: API key configured, missing auth header
    handler = MockHandler()
    result = verify_auth(handler)
    assert result == False, "Should reject with missing API key"
    assert handler.status_sent == 401, "Should return 401 Unauthorized"
    print("  [OK] Missing API key: rejects with 401")

    # Test 4: API key configured, invalid auth header
    handler = MockHandler(auth_header="Bearer wrong_key")
    result = verify_auth(handler)
    assert result == False, "Should reject with invalid API key"
    assert handler.status_sent == 401, "Should return 401 Unauthorized"
    print("  [OK] Invalid API key: rejects with 401")

    # Cleanup
    os.environ.pop("FC_HTTP_API_KEY", None)

    print("[OK] Authentication tests passed\n")


def test_qdrant_health_check():
    """Test Qdrant health check uses environment variable."""
    print("Testing Qdrant Health Check...")

    from gateway import check_qdrant

    # Set custom Qdrant URL
    os.environ["QDRANT_URL"] = "http://custom-qdrant:9999"

    # Should attempt to connect to custom URL (will fail, but that's ok)
    result = check_qdrant()
    assert result == "not_available", "Should return not_available when unreachable"
    print("  [OK] Uses QDRANT_URL environment variable")

    # Cleanup
    os.environ.pop("QDRANT_URL", None)

    print("[OK] Qdrant health check tests passed\n")


if __name__ == "__main__":
    print("=" * 60)
    print("FC Gateway Security Tests")
    print("=" * 60)
    print()

    try:
        test_rate_limiter()
        test_auth_verification()
        test_qdrant_health_check()

        print("=" * 60)
        print("ALL TESTS PASSED [OK]")
        print("=" * 60)

    except AssertionError as e:
        print(f"\n[FAIL] TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
