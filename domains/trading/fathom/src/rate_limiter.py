"""
Fathom Rate Limiter
Prevents exceeding Kraken API rate limits.
"""

import time
from collections import deque
from typing import Optional


class RateLimiter:
    """
    Token bucket rate limiter for Kraken API.

    Kraken Rate Limits (REST API):
    - Tier: Starter = 15 call counter decay, Intermediate = 20, Pro = 20
    - Counter increases by cost of call (most are 1, some are 2-4)
    - Counter decreases by 1 every 3 seconds
    - Maximum counter = 15 (Starter) or 20 (Intermediate/Pro)

    This implementation uses a simpler sliding window approach:
    - Track timestamps of recent calls
    - Limit calls per time window
    - Configurable per tier

    WebSocket has no rate limits (event-driven).
    """

    # Tier configurations (conservative limits)
    TIERS = {
        "starter": {"calls_per_minute": 15, "burst": 5},
        "intermediate": {"calls_per_minute": 20, "burst": 8},
        "pro": {"calls_per_minute": 20, "burst": 10}
    }

    def __init__(self, tier: str = "starter"):
        """
        Initialize rate limiter.

        Args:
            tier: Kraken verification tier (starter, intermediate, pro)
        """
        if tier not in self.TIERS:
            raise ValueError(f"Invalid tier: {tier}. Must be one of {list(self.TIERS.keys())}")

        config = self.TIERS[tier]
        self.calls_per_minute = config["calls_per_minute"]
        self.burst_limit = config["burst"]

        # Sliding window of call timestamps
        self._call_history: deque[float] = deque(maxlen=self.calls_per_minute)
        self._window_seconds = 60

    def check_rate_limit(self) -> tuple[bool, Optional[float]]:
        """
        Check if we can make a call now.

        Returns:
            (can_proceed, wait_seconds)
            - can_proceed: True if call can be made
            - wait_seconds: If False, how long to wait before retrying
        """
        now = time.time()

        # Remove calls outside the window
        while self._call_history and (now - self._call_history[0]) > self._window_seconds:
            self._call_history.popleft()

        # Check if under limit
        if len(self._call_history) < self.calls_per_minute:
            return True, None

        # Calculate wait time
        oldest_call = self._call_history[0]
        wait_time = self._window_seconds - (now - oldest_call)

        return False, max(0, wait_time)

    def record_call(self):
        """Record that a call was made."""
        self._call_history.append(time.time())

    async def wait_if_needed(self):
        """
        Wait if rate limit would be exceeded.

        Blocks until a call can be made safely.
        """
        can_proceed, wait_time = self.check_rate_limit()

        if not can_proceed and wait_time:
            import asyncio
            await asyncio.sleep(wait_time)

    def get_stats(self) -> dict:
        """
        Get rate limiter statistics.

        Returns:
            {
                "calls_in_window": int,
                "limit": int,
                "remaining": int,
                "window_seconds": int
            }
        """
        now = time.time()

        # Clean old entries
        while self._call_history and (now - self._call_history[0]) > self._window_seconds:
            self._call_history.popleft()

        calls_made = len(self._call_history)

        return {
            "calls_in_window": calls_made,
            "limit": self.calls_per_minute,
            "remaining": max(0, self.calls_per_minute - calls_made),
            "window_seconds": self._window_seconds
        }

    def reset(self):
        """Reset rate limiter (clear call history)."""
        self._call_history.clear()
