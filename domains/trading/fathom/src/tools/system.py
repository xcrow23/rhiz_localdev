"""
Fathom System Tools
Health checks and system status monitoring.
"""

from typing import Any
from ..clients.rest import KrakenRESTClient
from ..clients.websocket import KrakenWebSocketClient
from ..rate_limiter import RateLimiter


async def fathom_health_check(
    rest_client: KrakenRESTClient,
    rate_limiter: RateLimiter
) -> dict[str, Any]:
    """
    Health check for Fathom MCP.

    Tests:
    - Kraken API connectivity (public endpoint)
    - System status
    - Rate limiter status

    Returns:
        {
            "status": "healthy" | "degraded" | "unhealthy",
            "kraken_api": {"reachable": bool, "latency_ms": float},
            "kraken_status": {"status": str, "timestamp": str},
            "rate_limiter": {"calls_remaining": int, "limit": int},
            "timestamp": str
        }
    """
    import time
    from datetime import datetime

    result = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }

    # Test Kraken API connectivity
    try:
        start = time.time()
        server_time = await rest_client.get_server_time()
        latency = (time.time() - start) * 1000

        result["kraken_api"] = {
            "reachable": True,
            "latency_ms": round(latency, 2),
            "server_time": server_time.get("unixtime")
        }
    except Exception as e:
        result["kraken_api"] = {
            "reachable": False,
            "error": str(e)
        }
        result["status"] = "unhealthy"

    # Test system status
    try:
        status = await rest_client.get_system_status()
        result["kraken_status"] = status

        if status.get("status") != "online":
            result["status"] = "degraded"
    except Exception as e:
        result["kraken_status"] = {"error": str(e)}
        result["status"] = "degraded"

    # Rate limiter stats
    result["rate_limiter"] = rate_limiter.get_stats()

    return result


async def fathom_get_rate_limits(rate_limiter: RateLimiter) -> dict[str, Any]:
    """
    Get current rate limit status.

    Returns:
        {
            "calls_in_window": int,
            "limit": int,
            "remaining": int,
            "window_seconds": int,
            "percentage_used": float
        }
    """
    stats = rate_limiter.get_stats()

    stats["percentage_used"] = round(
        (stats["calls_in_window"] / stats["limit"]) * 100, 2
    ) if stats["limit"] > 0 else 0

    return stats


async def fathom_get_websocket_status(ws_client: KrakenWebSocketClient) -> dict[str, Any]:
    """
    Get WebSocket connection status.

    Returns:
        {
            "connected": bool,
            "subscriptions": [{"channel": str, "pairs": [str]}],
            "subscription_count": int
        }
    """
    return {
        "connected": ws_client.is_connected(),
        "subscriptions": ws_client.get_subscriptions(),
        "subscription_count": len(ws_client.get_subscriptions())
    }
