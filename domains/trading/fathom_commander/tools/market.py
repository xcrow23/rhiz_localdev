"""
Fathom Commander - Market Intelligence Tools
Real-time market monitoring and analysis.
"""

import json
import urllib.request
import urllib.parse
from datetime import datetime
from typing import Optional
import sys
import os

# Add paths for imports
_this_dir = os.path.dirname(os.path.abspath(__file__))
_parent_dir = os.path.dirname(_this_dir)
sys.path.insert(0, _parent_dir)
sys.path.insert(0, os.path.join(_parent_dir, '..', 'fathom', 'src'))

try:
    from state import get_state_manager
except ImportError:
    from ..state import get_state_manager


class MarketMonitor:
    """
    Market data fetching and caching.
    Uses Kraken public API (no auth needed for market data).
    """

    BASE_URL = "https://api.kraken.com/0"

    def __init__(self):
        self.state = get_state_manager()

    def _request(self, endpoint: str, data: dict = None) -> dict:
        """Make API request to Kraken."""
        url = f"{self.BASE_URL}/{endpoint}"

        if data:
            post_data = urllib.parse.urlencode(data).encode('utf-8')
            req = urllib.request.Request(url, data=post_data)
        else:
            req = urllib.request.Request(url)

        try:
            with urllib.request.urlopen(req, timeout=10) as response:
                result = json.loads(response.read())

                if result.get("error") and len(result["error"]) > 0:
                    return {"success": False, "error": result["error"]}

                return {"success": True, "result": result.get("result", {})}

        except Exception as e:
            self.state.record_error(str(e))
            return {"success": False, "error": str(e)}

    async def get_ticker(self, pairs: list[str]) -> dict:
        """
        Get ticker data for multiple pairs.
        Returns price, bid, ask, volume, etc.
        """
        result = self._request("public/Ticker", {"pair": ",".join(pairs)})

        if not result["success"]:
            return result

        tickers = {}
        prices_update = {}

        for pair, data in result["result"].items():
            current_price = float(data["c"][0])
            prices_update[pair] = current_price

            tickers[pair] = {
                "price": current_price,
                "bid": float(data["b"][0]),
                "ask": float(data["a"][0]),
                "spread": float(data["a"][0]) - float(data["b"][0]),
                "spread_percent": ((float(data["a"][0]) - float(data["b"][0])) / current_price) * 100 if current_price > 0 else 0,
                "volume_24h": float(data["v"][1]),
                "high_24h": float(data["h"][1]),
                "low_24h": float(data["l"][1]),
                "vwap_24h": float(data["p"][1]),
                "trades_24h": int(data["t"][1]),
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }

        # Update state cache
        self.state.update_prices(prices_update)

        return {
            "success": True,
            "tickers": tickers,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }

    async def get_ohlc(self, pair: str, interval: int = 1) -> dict:
        """
        Get OHLC candlestick data.
        Interval: 1, 5, 15, 30, 60, 240, 1440, 10080, 21600 (minutes)
        """
        result = self._request("public/OHLC", {"pair": pair, "interval": interval})

        if not result["success"]:
            return result

        # Parse OHLC data
        ohlc_data = []
        for candle in result["result"].get(pair, [])[-50:]:  # Last 50 candles
            ohlc_data.append({
                "time": candle[0],
                "open": float(candle[1]),
                "high": float(candle[2]),
                "low": float(candle[3]),
                "close": float(candle[4]),
                "vwap": float(candle[5]),
                "volume": float(candle[6]),
                "count": int(candle[7])
            })

        return {
            "success": True,
            "pair": pair,
            "interval": interval,
            "candles": ohlc_data,
            "last": result["result"].get("last", 0)
        }

    async def get_orderbook(self, pair: str, depth: int = 10) -> dict:
        """Get order book depth."""
        result = self._request("public/Depth", {"pair": pair, "count": depth})

        if not result["success"]:
            return result

        book = result["result"].get(pair, {})

        return {
            "success": True,
            "pair": pair,
            "asks": [[float(p), float(v)] for p, v, _ in book.get("asks", [])],
            "bids": [[float(p), float(v)] for p, v, _ in book.get("bids", [])],
            "spread": float(book["asks"][0][0]) - float(book["bids"][0][0]) if book.get("asks") and book.get("bids") else 0,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }

    async def analyze_market_condition(self, pair: str) -> dict:
        """
        Analyze current market conditions for a pair.
        Returns volatility, trend, and trading recommendations.
        """
        # Get ticker and OHLC
        ticker = await self.get_ticker([pair])
        ohlc = await self.get_ohlc(pair, interval=5)  # 5-minute candles

        if not ticker["success"] or not ohlc["success"]:
            return {"success": False, "error": "Failed to fetch market data"}

        ticker_data = ticker["tickers"].get(pair, {})
        candles = ohlc.get("candles", [])

        if len(candles) < 10:
            return {"success": False, "error": "Insufficient data for analysis"}

        # Calculate volatility (standard deviation of returns)
        closes = [c["close"] for c in candles[-20:]]
        returns = [(closes[i] - closes[i-1]) / closes[i-1] for i in range(1, len(closes))]
        volatility = (sum([r**2 for r in returns]) / len(returns)) ** 0.5 * 100

        # Determine trend (simple: compare current to 10-candle average)
        avg_10 = sum(closes[-10:]) / 10
        current = closes[-1]
        trend_strength = ((current - avg_10) / avg_10) * 100

        if trend_strength > 0.5:
            trend = "bullish"
        elif trend_strength < -0.5:
            trend = "bearish"
        else:
            trend = "neutral"

        # Determine volatility regime
        if volatility > 2:
            volatility_regime = "high"
        elif volatility > 0.5:
            volatility_regime = "normal"
        else:
            volatility_regime = "low"

        # Trading recommendation
        spread_percent = ticker_data.get("spread_percent", 0)

        if spread_percent > 0.1:  # >0.1% spread
            liquidity = "low"
            recommendation = "avoid"
        elif volatility_regime == "high":
            liquidity = "normal"
            recommendation = "caution"
        else:
            liquidity = "good"
            recommendation = "favorable"

        return {
            "success": True,
            "pair": pair,
            "price": ticker_data.get("price", 0),
            "analysis": {
                "trend": trend,
                "trend_strength_percent": round(trend_strength, 2),
                "volatility_percent": round(volatility, 2),
                "volatility_regime": volatility_regime,
                "spread_percent": round(spread_percent, 4),
                "liquidity": liquidity,
                "recommendation": recommendation
            },
            "24h_stats": {
                "high": ticker_data.get("high_24h", 0),
                "low": ticker_data.get("low_24h", 0),
                "volume": ticker_data.get("volume_24h", 0),
                "trades": ticker_data.get("trades_24h", 0)
            },
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }


# Singleton instance
_market_monitor: Optional[MarketMonitor] = None


def get_market_monitor() -> MarketMonitor:
    """Get or create market monitor singleton."""
    global _market_monitor
    if _market_monitor is None:
        _market_monitor = MarketMonitor()
    return _market_monitor


# =========================
# Tool Functions
# =========================

async def market_get_ticker(pairs: list[str]) -> dict:
    """Get ticker data for pairs."""
    monitor = get_market_monitor()
    return await monitor.get_ticker(pairs)


async def market_get_ohlc(pair: str, interval: int = 5) -> dict:
    """Get OHLC candlestick data."""
    monitor = get_market_monitor()
    return await monitor.get_ohlc(pair, interval)


async def market_get_orderbook(pair: str, depth: int = 10) -> dict:
    """Get order book depth."""
    monitor = get_market_monitor()
    return await monitor.get_orderbook(pair, depth)


async def market_analyze(pair: str) -> dict:
    """Analyze market conditions for trading."""
    monitor = get_market_monitor()
    return await monitor.analyze_market_condition(pair)
