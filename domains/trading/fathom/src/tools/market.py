"""
Fathom Market Tools
Market data retrieval (ticker, orderbook, OHLC, trades).
"""

from typing import Any, Optional
from ..clients.rest import KrakenRESTClient
from ..validator import Validator


async def fathom_get_ticker(
    client: KrakenRESTClient,
    validator: Validator,
    pairs: list[str]
) -> dict[str, Any]:
    """
    Get ticker information for trading pairs.

    Args:
        pairs: List of trading pairs (e.g., ["BTC/USD", "ETH/USD"])

    Returns:
        {
            "tickers": {
                "XBTUSD": {
                    "ask": [price, whole_lot_volume, lot_volume],
                    "bid": [price, whole_lot_volume, lot_volume],
                    "last": [price, lot_volume],
                    "volume": [today, last_24h],
                    "vwap": [today, last_24h],
                    "trades": [today, last_24h],
                    "low": [today, last_24h],
                    "high": [today, last_24h],
                    "open": price
                }
            },
            "timestamp": str,
            "success": bool
        }
    """
    from datetime import datetime

    # Validate pairs
    for pair in pairs:
        is_valid, error = validator.validate_pair(pair)
        if not is_valid:
            return {
                "success": False,
                "error": error,
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }

    try:
        # Normalize pairs to Kraken format
        normalized_pairs = [validator.sanitize_pair(p) for p in pairs]

        tickers = await client.get_ticker(normalized_pairs)

        return {
            "tickers": tickers,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "success": True
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }


async def fathom_get_orderbook(
    client: KrakenRESTClient,
    validator: Validator,
    pair: str,
    depth: int = 10
) -> dict[str, Any]:
    """
    Get order book (market depth).

    Args:
        pair: Trading pair
        depth: Number of levels (10, 25, 100, 500, 1000)

    Returns:
        {
            "pair": str,
            "asks": [[price, volume, timestamp], ...],
            "bids": [[price, volume, timestamp], ...],
            "timestamp": str,
            "success": bool
        }
    """
    from datetime import datetime

    # Validate inputs
    is_valid, error = validator.validate_pair(pair)
    if not is_valid:
        return {
            "success": False,
            "error": error,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }

    is_valid, error = validator.validate_book_depth(depth)
    if not is_valid:
        return {
            "success": False,
            "error": error,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }

    try:
        normalized_pair = validator.sanitize_pair(pair)
        book = await client.get_orderbook(normalized_pair, count=depth)

        # Extract the first key (Kraken returns nested dict)
        pair_key = list(book.keys())[0]
        book_data = book[pair_key]

        return {
            "pair": pair,
            "asks": book_data.get("asks", []),
            "bids": book_data.get("bids", []),
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "success": True
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }


async def fathom_get_ohlc(
    client: KrakenRESTClient,
    validator: Validator,
    pair: str,
    interval: int = 1,
    since: Optional[int] = None
) -> dict[str, Any]:
    """
    Get OHLC (candlestick) data.

    Args:
        pair: Trading pair
        interval: Interval in minutes (1, 5, 15, 30, 60, 240, 1440, 10080, 21600)
        since: Return data since this timestamp (optional)

    Returns:
        {
            "pair": str,
            "interval": int,
            "candles": [[time, open, high, low, close, vwap, volume, count], ...],
            "last": int,
            "timestamp": str,
            "success": bool
        }
    """
    from datetime import datetime

    # Validate inputs
    is_valid, error = validator.validate_pair(pair)
    if not is_valid:
        return {
            "success": False,
            "error": error,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }

    is_valid, error = validator.validate_interval(interval)
    if not is_valid:
        return {
            "success": False,
            "error": error,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }

    try:
        normalized_pair = validator.sanitize_pair(pair)
        ohlc_data = await client.get_ohlc(normalized_pair, interval=interval, since=since)

        # Extract pair key
        pair_key = list(ohlc_data.keys())[0] if isinstance(ohlc_data, dict) else normalized_pair
        candles = ohlc_data.get(pair_key, []) if isinstance(ohlc_data, dict) else []
        last = ohlc_data.get("last", 0) if isinstance(ohlc_data, dict) else 0

        return {
            "pair": pair,
            "interval": interval,
            "candles": candles,
            "last": last,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "success": True
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }


async def fathom_get_recent_trades(
    client: KrakenRESTClient,
    validator: Validator,
    pair: str,
    since: Optional[int] = None
) -> dict[str, Any]:
    """
    Get recent public trades.

    Args:
        pair: Trading pair
        since: Return trades since this ID (optional)

    Returns:
        {
            "pair": str,
            "trades": [[price, volume, time, buy/sell, market/limit, misc], ...],
            "last": str,
            "timestamp": str,
            "success": bool
        }
    """
    from datetime import datetime

    # Validate pair
    is_valid, error = validator.validate_pair(pair)
    if not is_valid:
        return {
            "success": False,
            "error": error,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }

    try:
        normalized_pair = validator.sanitize_pair(pair)
        trades_data = await client.get_recent_trades(normalized_pair, since=since)

        # Extract pair key
        pair_key = list(trades_data.keys())[0] if "last" not in trades_data else normalized_pair
        trades = trades_data.get(pair_key, []) if isinstance(trades_data, dict) else []
        last = trades_data.get("last", "") if isinstance(trades_data, dict) else ""

        return {
            "pair": pair,
            "trades": trades,
            "last": last,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "success": True
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
