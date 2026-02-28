"""
Fathom Commander HTTP Gateway
REST API for n8n integration.

Exposes Commander tools as HTTP endpoints for n8n workflows.
Run with: python gateway.py [port]
Default port: 8765
"""

import asyncio
import json
import sys
import os
import secrets
import logging
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from datetime import datetime

# Configure security logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Ensure imports work
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from state import get_state_manager

# Import tool modules
from tools.market import (
    market_get_ticker,
    market_get_ohlc,
    market_get_orderbook,
    market_analyze
)
from tools.execution import (
    get_execution_engine,
    execute_trade,
    validate_trade,
    approve_order,
    reject_order,
    cancel_order,
    get_open_orders,
    get_trade_history
)
from tools.portfolio import (
    portfolio_get_balance,
    portfolio_get_holdings,
    portfolio_get_summary,
    portfolio_get_performance
)
from tools.strategy import (
    strategy_list,
    strategy_activate,
    strategy_deactivate,
    strategy_signal,
    strategy_check_exits,
    strategy_analyze_opportunity
)
from tools.alerts import (
    alert_send,
    alert_history,
    alert_status
)


# Track startup
_start_time = datetime.utcnow()


def get_uptime() -> str:
    """Get uptime as human-readable string."""
    delta = datetime.utcnow() - _start_time
    hours, remainder = divmod(int(delta.total_seconds()), 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours}h {minutes}m {seconds}s"


def check_kraken() -> str:
    """Check Kraken auth status."""
    try:
        engine = get_execution_engine()
        return "ok" if engine.auth else "not_configured"
    except Exception:
        return "error"


def check_qdrant() -> str:
    """Check Qdrant connection."""
    try:
        import urllib.request
        qdrant_url = os.getenv("QDRANT_URL", "http://qdrant:6333")
        req = urllib.request.Request(f"{qdrant_url}/health")
        with urllib.request.urlopen(req, timeout=2) as resp:
            return "ok" if resp.status == 200 else "error"
    except Exception:
        return "not_available"


def verify_auth(handler) -> bool:
    """
    Verify API key from Authorization header using constant-time comparison.

    Expects: Authorization: Bearer <api_key>
    Configured via FC_HTTP_API_KEY environment variable.

    If no API key is configured, allows all requests with warning log.
    Uses secrets.compare_digest() to prevent timing attacks.
    """
    expected_key = os.getenv("FC_HTTP_API_KEY")

    # No auth key configured - allow request but log warning (once per session)
    if not expected_key:
        if not hasattr(verify_auth, '_warned'):
            logger.warning("FC_HTTP_API_KEY not configured - authentication DISABLED")
            verify_auth._warned = True
        return True

    # Get client info for logging
    client_ip = handler.client_address[0]
    path = handler.path

    # Check Authorization header
    auth_header = handler.headers.get("Authorization", "")

    # Extract token from "Bearer <token>" format
    if not auth_header.startswith("Bearer "):
        logger.warning(f"Auth failed from {client_ip} for {path}: missing Bearer prefix")
        handler._send_json({
            "error": "Unauthorized",
            "message": "Invalid Authorization header. Use: Authorization: Bearer <api_key>"
        }, 401)
        return False

    provided_key = auth_header[7:]  # Remove "Bearer " prefix

    # Constant-time comparison to prevent timing attacks
    if not secrets.compare_digest(expected_key, provided_key):
        logger.warning(f"Auth failed from {client_ip} for {path}: invalid API key")
        handler._send_json({
            "error": "Unauthorized",
            "message": "Invalid API key"
        }, 401)
        return False

    # Success - log at debug level only (avoid log spam)
    logger.debug(f"Auth success from {client_ip} for {path}")
    return True


class RateLimiter:
    """
    Token bucket rate limiter for trade endpoints.

    Prevents runaway trading by limiting requests per minute.
    Each trade endpoint gets its own bucket with configurable capacity and refill rate.
    """

    def __init__(self, capacity: int = 10, refill_rate: float = 1.0):
        """
        Args:
            capacity: Maximum tokens in bucket (max burst)
            refill_rate: Tokens added per second
        """
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.tokens = capacity
        self.last_refill = datetime.utcnow()

    def allow(self) -> tuple[bool, str]:
        """
        Check if request is allowed.

        Returns:
            (allowed: bool, reason: str)
        """
        # Refill tokens based on time elapsed
        now = datetime.utcnow()
        elapsed = (now - self.last_refill).total_seconds()
        self.tokens = min(self.capacity, self.tokens + (elapsed * self.refill_rate))
        self.last_refill = now

        # Check if we have tokens
        if self.tokens >= 1.0:
            self.tokens -= 1.0
            return True, ""
        else:
            wait_time = int((1.0 - self.tokens) / self.refill_rate)
            return False, f"Rate limit exceeded. Try again in {wait_time} seconds."


# Global rate limiters for trade endpoints
# Each endpoint gets 10 requests per 60 seconds (1 token per 6 seconds)
_rate_limiters = {
    "/trade/execute": RateLimiter(capacity=10, refill_rate=1.0/6.0),
    "/execute": RateLimiter(capacity=10, refill_rate=1.0/6.0),
}


class CommanderHandler(BaseHTTPRequestHandler):
    """HTTP request handler for Commander gateway."""

    def _send_json(self, data: dict, status: int = 200):
        """Send JSON response."""
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2).encode())

    def _run_async(self, coro):
        """Run async function synchronously."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(coro)
        finally:
            loop.close()

    def _query_sil_regime(self, pair: str) -> dict:
        """
        Query SIL for regime classification.

        Fetches OHLCV data and sends to SIL for analysis.
        Returns regime, volatility, and sentiment information.
        """
        try:
            import urllib.request
            import urllib.error

            # Get SIL URL from environment
            sil_url = os.getenv("SIL_URL", "http://sil-fastapi:8000")

            # Fetch OHLCV data (200+ candles for accurate regime detection)
            ohlc_result = self._run_async(market_get_ohlc(pair, interval=5))

            if not ohlc_result.get("success"):
                return {"success": False, "error": f"Failed to fetch OHLCV: {ohlc_result.get('error')}"}

            candles = ohlc_result.get("candles", [])

            if len(candles) < 30:
                return {"success": False, "error": f"Insufficient data: got {len(candles)} candles, need 30+"}

            # Format OHLCV for SIL (convert timestamps to ISO format)
            ohlcv_data = [
                {
                    "timestamp": datetime.utcfromtimestamp(c["time"]).isoformat() + "Z",
                    "open": float(c["open"]),
                    "high": float(c["high"]),
                    "low": float(c["low"]),
                    "close": float(c["close"]),
                    "volume": float(c["volume"])
                }
                for c in candles
            ]

            # Convert pair format for display (XXBTZUSD -> BTC/USD)
            display_pair = pair.replace("XXBTZ", "BTC/").replace("XETHZ", "ETH/")

            # Call SIL regime classification endpoint (now accepts 30+ candles)
            payload = {
                "pair": display_pair,
                "ohlcv": ohlcv_data
            }

            req = urllib.request.Request(
                f"{sil_url}/regime/classify",
                data=json.dumps(payload).encode(),
                headers={"Content-Type": "application/json"},
                method="POST"
            )

            with urllib.request.urlopen(req, timeout=30) as response:
                result = json.loads(response.read())
                return {
                    "success": True,
                    "pair": result.get("pair"),
                    "regime": result.get("regime"),
                    "confidence": result.get("confidence"),
                    "volatility_regime": result.get("volatility_regime"),
                    "trend_strength": result.get("trend_strength", 0),
                    "candles_analyzed": len(candles),
                    "timestamp": result.get("timestamp")
                }

        except urllib.error.URLError as e:
            return {"success": False, "error": f"SIL connection failed: {str(e)}"}
        except Exception as e:
            return {"success": False, "error": f"SIL query failed: {str(e)}"}

    def _query_sil_strategy(self, pair: str) -> dict:
        """
        Query SIL for strategy selection.

        Fetches OHLCV and portfolio data, sends to SIL for full strategy decision.
        Returns action, position size, and reasoning.
        """
        try:
            import urllib.request
            import urllib.error

            # Get SIL URL from environment
            sil_url = os.getenv("SIL_URL", "http://sil-fastapi:8000")

            # Fetch OHLCV data
            ohlc_result = self._run_async(market_get_ohlc(pair, interval=5))

            if not ohlc_result.get("success"):
                return {"success": False, "error": f"Failed to fetch OHLCV: {ohlc_result.get('error')}"}

            candles = ohlc_result.get("candles", [])

            if len(candles) < 30:
                return {"success": False, "error": f"Insufficient data: got {len(candles)} candles, need 30+"}

            # Get portfolio balance
            portfolio_result = self._run_async(portfolio_get_balance())

            if not portfolio_result.get("success"):
                return {"success": False, "error": f"Failed to fetch portfolio: {portfolio_result.get('error')}"}

            # Extract USD balance
            balances = portfolio_result.get("balances", {})
            portfolio_balance = float(balances.get("ZUSD", {}).get("balance", 0))

            # Get current position if any
            state = get_state_manager()
            positions = state.get_positions()
            current_position = positions.get(pair, {}).get("volume", 0)

            # Format OHLCV for SIL
            ohlcv_data = [
                {
                    "timestamp": datetime.utcfromtimestamp(c["time"]).isoformat() + "Z",
                    "open": float(c["open"]),
                    "high": float(c["high"]),
                    "low": float(c["low"]),
                    "close": float(c["close"]),
                    "volume": float(c["volume"])
                }
                for c in candles
            ]

            # Convert pair format for display
            display_pair = pair.replace("XXBTZ", "BTC/").replace("XETHZ", "ETH/")

            # Call SIL strategy selection endpoint
            payload = {
                "pair": display_pair,
                "ohlcv": ohlcv_data,
                "portfolio_balance": portfolio_balance,
                "current_position": current_position
            }

            req = urllib.request.Request(
                f"{sil_url}/strategy/select",
                data=json.dumps(payload).encode(),
                headers={"Content-Type": "application/json"},
                method="POST"
            )

            with urllib.request.urlopen(req, timeout=30) as response:
                result = json.loads(response.read())
                return {
                    "success": True,
                    "pair": result.get("pair"),
                    "regime": result.get("regime"),
                    "regime_confidence": result.get("regime_confidence"),
                    "selected_strategy": result.get("selected_strategy"),
                    "action": result.get("action"),
                    "position_size_usd": result.get("position_size_usd"),
                    "position_size_asset": result.get("position_size_asset"),
                    "confidence": result.get("confidence"),
                    "reasoning": result.get("reasoning"),
                    "risk_check": result.get("risk_check"),
                    "candles_analyzed": len(candles),
                    "timestamp": result.get("timestamp")
                }

        except urllib.error.URLError as e:
            return {"success": False, "error": f"SIL connection failed: {str(e)}"}
        except Exception as e:
            return {"success": False, "error": f"SIL query failed: {str(e)}"}

    def _handle_usd_trade(self, data: dict) -> dict:
        """
        Handle USD-based trade execution for n8n/automation.
        Converts USD amount to BTC volume and executes.

        Expected data:
            action: "buy" or "sell"
            symbol: "BTC/USD" (will be converted to Kraken pair)
            amount_usd: Dollar amount to spend
            reason: Trade reasoning (optional)
        """
        # Symbol mapping
        SYMBOL_TO_PAIR = {
            "BTC/USD": "XXBTZUSD",
            "BTCUSD": "XXBTZUSD",
            "ETH/USD": "XETHZUSD",
            "ETHUSD": "XETHZUSD"
        }
        
        try:
            # Parse inputs
            action = data.get("action", "").lower()
            symbol = data.get("symbol", "BTC/USD").upper()
            amount_usd = float(data.get("amount_usd", 0))
            reason = data.get("reason", "Automated trade via n8n")
            
            # Validate
            if action not in ["buy", "sell"]:
                return {"success": False, "error": f"Invalid action: {action}. Use 'buy' or 'sell'"}
            
            if amount_usd <= 0:
                return {"success": False, "error": f"Invalid amount_usd: {amount_usd}"}
            
            # Convert symbol to Kraken pair
            pair = SYMBOL_TO_PAIR.get(symbol)
            if not pair:
                return {"success": False, "error": f"Unknown symbol: {symbol}. Supported: BTC/USD, ETH/USD"}
            
            # Get current price to calculate volume
            ticker_result = self._run_async(market_get_ticker([pair]))
            if not ticker_result.get("success"):
                return {"success": False, "error": f"Failed to get price: {ticker_result.get('error')}"}
            
            current_price = ticker_result["tickers"][pair]["price"]
            
            # Calculate volume (BTC amount from USD)
            # For buys: how much BTC can we get for $amount_usd
            # Add small buffer for market movement (0.5%)
            volume = (amount_usd / current_price) * 0.995
            
            # Round to 8 decimal places (satoshi precision)
            volume = round(volume, 8)
            
            # Execute the trade
            return self._run_async(execute_trade(
                pair=pair,
                side=action,
                order_type="market",
                volume=volume,
                price=None,
                reasoning=reason,
                hypothesis=f"USD-based DCA: ${amount_usd} at ~${current_price:.2f}/BTC",
                captain_approved=False  # Let safety system decide
            ))
            
        except Exception as e:
            return {"success": False, "error": f"Trade execution failed: {str(e)}"}

    def do_OPTIONS(self):
        """Handle CORS preflight."""
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        """Handle GET requests."""
        parsed = urlparse(self.path)
        path = parsed.path

        # /health endpoint bypasses authentication (for Docker healthcheck)
        if path != "/health":
            # Verify authentication for all other endpoints
            if not verify_auth(self):
                return

        query = parse_qs(parsed.query)

        try:
            # Update heartbeat
            state = get_state_manager()
            state.update_heartbeat()

            result = self._handle_get(path, query)
            self._send_json(result)

        except Exception as e:
            self._send_json({"success": False, "error": str(e)}, 500)

    def do_POST(self):
        """Handle POST requests."""
        # Verify authentication
        if not verify_auth(self):
            return

        parsed = urlparse(self.path)
        path = parsed.path

        # Check rate limiting for trade endpoints
        if path in _rate_limiters:
            allowed, reason = _rate_limiters[path].allow()
            if not allowed:
                client_ip = self.client_address[0]
                logger.warning(f"Rate limit exceeded from {client_ip} for {path}")
                self._send_json({
                    "success": False,
                    "error": "Rate limit exceeded",
                    "message": reason
                }, 429)
                return

        try:
            # Read body
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length).decode() if content_length > 0 else "{}"
            data = json.loads(body) if body else {}

            # Update heartbeat
            state = get_state_manager()
            state.update_heartbeat()

            result = self._handle_post(path, data)

            # Save state for modifying operations
            if path in ["/execute", "/trade/execute", "/approve", "/reject", "/mode", "/strategy/activate", "/strategy/deactivate"]:
                state.save()

            self._send_json(result)

        except json.JSONDecodeError as e:
            self._send_json({"success": False, "error": f"Invalid JSON: {e}"}, 400)
        except Exception as e:
            self._send_json({"success": False, "error": str(e)}, 500)

    def _handle_get(self, path: str, query: dict) -> dict:
        """Handle GET endpoints."""

        # Health check - unauthenticated, minimal (for Docker healthcheck)
        if path == "/health":
            return {
                "status": "alive",
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }

        # Heartbeat - authenticated, detailed system status (for n8n polling)
        if path == "/heartbeat" or path == "/":
            state = get_state_manager()
            summary = state.get_summary()
            positions = state.get_positions()
            pending = state.get_pending_approvals()

            return {
                "status": "alive",
                "uptime": get_uptime(),
                "mode": summary.get("mode", "unknown"),
                "positions": {
                    "count": len(positions),
                    "pairs": list(positions.keys())
                },
                "pending_approvals": {
                    "count": len(pending),
                    "ids": list(pending.keys())
                },
                "today": {
                    "trades": summary.get("trades_today", 0),
                    "trades_remaining": summary.get("trades_remaining", 0),
                    "pnl": summary.get("daily_pnl", 0),
                    "loss_current": summary.get("daily_loss_current", 0)
                },
                "strategy": summary.get("active_strategy"),
                "trading_halted": summary.get("trading_halted", False),
                "halt_reason": summary.get("halt_reason", ""),
                "health": {
                    "kraken_auth": check_kraken(),
                    "memory": check_qdrant(),
                    "errors": summary.get("consecutive_errors", 0)
                },
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }

        # Market endpoints
        elif path == "/market/ticker":
            pairs = query.get("pairs", ["XXBTZUSD"])
            if isinstance(pairs, list) and len(pairs) == 1 and "," in pairs[0]:
                pairs = pairs[0].split(",")
            return self._run_async(market_get_ticker(pairs))

        elif path == "/market/ohlc":
            pair = query.get("pair", ["XXBTZUSD"])[0]
            interval = int(query.get("interval", [5])[0])
            return self._run_async(market_get_ohlc(pair, interval))

        elif path == "/market/analyze":
            pair = query.get("pair", ["XXBTZUSD"])[0]
            return self._run_async(market_analyze(pair))

        elif path == "/market/orderbook":
            pair = query.get("pair", ["XXBTZUSD"])[0]
            depth = int(query.get("depth", [10])[0])
            return self._run_async(market_get_orderbook(pair, depth))

        # Portfolio endpoints
        elif path == "/portfolio/balance":
            return self._run_async(portfolio_get_balance())

        elif path == "/portfolio/holdings":
            return self._run_async(portfolio_get_holdings())

        elif path == "/portfolio/summary":
            return self._run_async(portfolio_get_summary())

        elif path == "/portfolio/performance":
            return self._run_async(portfolio_get_performance())

        # Strategy endpoints
        elif path == "/strategy/list":
            return strategy_list()

        elif path == "/strategy/activate":
            name = query.get("name", [None])[0]
            if not name:
                return {"success": False, "error": "Missing 'name' query parameter"}
            result = strategy_activate(name)
            state = get_state_manager()
            state.save()
            return result

        elif path == "/strategy/deactivate":
            result = strategy_deactivate()
            state = get_state_manager()
            state.save()
            return result

        elif path == "/strategy/signal":
            pair = query.get("pair", ["XXBTZUSD"])[0]
            return self._run_async(strategy_signal(pair))

        elif path == "/strategy/check-exits":
            return self._run_async(strategy_check_exits())

        elif path == "/strategy/analyze":
            pair = query.get("pair", ["XXBTZUSD"])[0]
            return self._run_async(strategy_analyze_opportunity(pair))

        # Orders endpoints
        elif path == "/orders/open":
            return self._run_async(get_open_orders())

        elif path == "/orders/history":
            count = int(query.get("count", [10])[0])
            return self._run_async(get_trade_history(count))

        # State endpoints
        elif path == "/state/summary":
            state = get_state_manager()
            return {"success": True, "summary": state.get_summary()}

        elif path == "/state/pending":
            state = get_state_manager()
            return {"success": True, "pending": state.get_pending_approvals()}

        # SIL integration endpoints
        elif path == "/sil/regime":
            pair = query.get("pair", ["XXBTZUSD"])[0]
            return self._query_sil_regime(pair)

        elif path == "/sil/strategy":
            pair = query.get("pair", ["XXBTZUSD"])[0]
            return self._query_sil_strategy(pair)

        # Alerts endpoints
        elif path == "/alerts/history":
            limit = int(query.get("limit", [20])[0])
            return alert_history(limit)

        elif path == "/alerts/status":
            return alert_status()

        else:
            return {"success": False, "error": f"Unknown endpoint: {path}"}

    def _handle_post(self, path: str, data: dict) -> dict:
        """Handle POST endpoints."""

        # Execute trade (direct - requires pair, side, volume)
        if path == "/execute":
            return self._run_async(execute_trade(
                pair=data["pair"],
                side=data["side"],
                order_type=data.get("order_type", "market"),
                volume=data["volume"],
                price=data.get("price"),
                reasoning=data.get("reasoning", ""),
                hypothesis=data.get("hypothesis", ""),
                captain_approved=data.get("captain_approved", False)
            ))

        # Execute trade (USD-based - simpler interface for n8n/automation)
        # Accepts: action (buy/sell), symbol (BTC/USD), amount_usd, reason
        elif path == "/trade/execute":
            return self._handle_usd_trade(data)

        # Validate trade
        elif path == "/validate":
            return self._run_async(validate_trade(
                pair=data["pair"],
                side=data["side"],
                order_type=data.get("order_type", "market"),
                volume=data["volume"],
                price=data.get("price")
            ))

        # Approve order
        elif path == "/approve":
            return self._run_async(approve_order(data["approval_id"]))

        # Reject order
        elif path == "/reject":
            return self._run_async(reject_order(
                data["approval_id"],
                data.get("reason", "")
            ))

        # Cancel order
        elif path == "/cancel":
            return self._run_async(cancel_order(
                data["txid"],
                data.get("reason", "")
            ))

        # Set mode
        elif path == "/mode":
            state = get_state_manager()
            state.set_mode(data["mode"])
            return {"success": True, "mode": data["mode"]}

        # Strategy activation
        elif path == "/strategy/activate":
            return strategy_activate(data["name"])

        elif path == "/strategy/deactivate":
            return strategy_deactivate()

        # Send alert
        elif path == "/alert":
            return alert_send(
                title=data["title"],
                message=data["message"],
                alert_type=data.get("alert_type", "info"),
                priority=data.get("priority", "normal")
            )

        else:
            return {"success": False, "error": f"Unknown endpoint: {path}"}

    def log_message(self, format, *args):
        """Custom log format."""
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {args[0]}")


def run_gateway(port: int = 8765):
    """Run the HTTP gateway server."""
    server = HTTPServer(("0.0.0.0", port), CommanderHandler)
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    print(f"""
+--------------------------------------------------------------+
|           FATHOM COMMANDER HTTP GATEWAY                      |
+--------------------------------------------------------------+
|  Port: {port:<54}|
|  Time: {timestamp:<54}|
+--------------------------------------------------------------+
|  Endpoints:                                                  |
|    GET  /              - Status/heartbeat (n8n polls)        |
|    GET  /market/ticker - Ticker data                         |
|    GET  /portfolio/summary - Portfolio overview              |
|    GET  /strategy/signal - Trading signal                    |
|    GET  /sil/regime    - SIL regime classification           |
|    GET  /sil/strategy  - SIL strategy decision               |
|    POST /trade/execute - Execute trade                       |
+--------------------------------------------------------------+
    """)
    print(f"[Commander] Gateway listening on http://0.0.0.0:{port}")
    print("[Commander] Press Ctrl+C to stop\n")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[Commander] Shutting down gateway...")
        server.shutdown()


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8765
    run_gateway(port)
