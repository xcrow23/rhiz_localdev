"""
Fathom Commander - Portfolio Tools
Position tracking, P&L calculation, and holdings management.
"""

import json
import os
import sys
import urllib.request
import urllib.parse
from datetime import datetime
from typing import Optional

# Add paths for imports
_this_dir = os.path.dirname(os.path.abspath(__file__))
_parent_dir = os.path.dirname(_this_dir)
sys.path.insert(0, _parent_dir)
sys.path.insert(0, os.path.join(_parent_dir, '..', 'fathom', 'src'))

try:
    from state import get_state_manager, Position
except ImportError:
    from ..state import get_state_manager, Position

# Load environment for auth - try multiple paths
for env_path in [
    os.path.join(os.path.dirname(__file__), '..', '..', '..', '.env'),  # From fathom_commander
    'C:\\Users\\dread\\Documents\\Rhiz_LocalDev\\.env',  # Windows path
    '/mnt/c/Users/dread/Documents/Rhiz_LocalDev/.env',  # WSL path
    os.path.expanduser('~/.env')  # Fallback
]:
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value
        break  # Found and loaded, stop searching

try:
    from ..auth import CredentialManager
except ImportError:
    CredentialManager = None


class PortfolioManager:
    """
    Portfolio tracking and analysis.
    """

    BASE_URL = "https://api.kraken.com/0"

    def __init__(self):
        self.state = get_state_manager()
        self.auth = CredentialManager() if CredentialManager else None

    def _authenticated_request(self, endpoint: str, data: dict) -> dict:
        """Make authenticated API request to Kraken."""
        if not self.auth:
            return {"success": False, "error": "Authentication not configured"}

        url = f"{self.BASE_URL}/{endpoint}"
        url_path = f"/0/{endpoint}"

        # Add nonce
        data["nonce"] = self.auth.generate_nonce()

        headers = self.auth.get_headers(url_path, data)
        post_data = urllib.parse.urlencode(data).encode('utf-8')
        req = urllib.request.Request(url, data=post_data, headers=headers)

        try:
            with urllib.request.urlopen(req, timeout=30) as response:
                result = json.loads(response.read())

                if result.get("error") and len(result["error"]) > 0:
                    return {"success": False, "error": result["error"]}

                return {"success": True, "result": result.get("result", {})}

        except Exception as e:
            self.state.record_error(str(e))
            return {"success": False, "error": str(e)}

    async def get_balance(self) -> dict:
        """Get account balances."""
        result = self._authenticated_request("private/Balance", {})

        if not result["success"]:
            return result

        balances = {}
        for asset, amount in result["result"].items():
            amount_float = float(amount)
            if amount_float > 0:
                balances[asset] = {
                    "amount": amount_float,
                    "asset": asset
                }

        return {
            "success": True,
            "balances": balances,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }

    async def get_trade_balance(self) -> dict:
        """Get trade balance (margin info, equity, etc.)."""
        result = self._authenticated_request("private/TradeBalance", {"asset": "ZUSD"})

        if not result["success"]:
            return result

        tb = result["result"]

        return {
            "success": True,
            "trade_balance": {
                "equity": float(tb.get("e", 0)),
                "trade_balance": float(tb.get("tb", 0)),
                "margin_used": float(tb.get("m", 0)),
                "margin_free": float(tb.get("mf", 0)),
                "unrealized_pnl": float(tb.get("n", 0)),
                "cost_basis": float(tb.get("c", 0)),
                "floating_valuation": float(tb.get("v", 0))
            },
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }

    async def get_positions_from_exchange(self) -> dict:
        """Get open positions from Kraken (margin positions)."""
        result = self._authenticated_request("private/OpenPositions", {})

        if not result["success"]:
            return result

        positions = {}
        for pos_id, pos_data in result["result"].items():
            pair = pos_data.get("pair", "")
            positions[pos_id] = {
                "pair": pair,
                "side": pos_data.get("type", ""),
                "volume": float(pos_data.get("vol", 0)),
                "entry_price": float(pos_data.get("cost", 0)) / float(pos_data.get("vol", 1)),
                "current_value": float(pos_data.get("value", 0)),
                "unrealized_pnl": float(pos_data.get("net", 0)),
                "margin_used": float(pos_data.get("margin", 0))
            }

        return {
            "success": True,
            "positions": positions,
            "count": len(positions),
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }

    async def calculate_holdings_value(self) -> dict:
        """Calculate total value of all holdings in USD."""
        # Get balances
        balances = await self.get_balance()
        if not balances["success"]:
            return balances

        # Get tracked positions from state
        state_positions = self.state.get_positions()

        # Calculate values
        holdings = []
        total_value = 0.0

        for asset, data in balances.get("balances", {}).items():
            amount = data["amount"]

            # USD-like assets
            if asset in ["ZUSD", "USD", "USDT", "USDC"]:
                value = amount
            else:
                # Get current price from state cache or mark as unknown
                price = self.state.get_price(f"X{asset}ZUSD") or self.state.get_price(f"{asset}USD")
                if price:
                    value = amount * price
                else:
                    value = None  # Unknown value

            holdings.append({
                "asset": asset,
                "amount": amount,
                "value_usd": value
            })

            if value is not None:
                total_value += value

        return {
            "success": True,
            "holdings": holdings,
            "total_value_usd": round(total_value, 2),
            "tracked_positions": len(state_positions),
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }

    async def get_portfolio_summary(self) -> dict:
        """Get comprehensive portfolio summary."""
        # Gather all portfolio data
        balance = await self.get_balance()
        trade_balance = await self.get_trade_balance()
        holdings_value = await self.calculate_holdings_value()

        # Get state data
        state_summary = self.state.get_summary()
        today_trades = self.state.get_trades_today()
        pending_approvals = self.state.get_pending_approvals()

        return {
            "success": True,
            "portfolio": {
                "total_value_usd": holdings_value.get("total_value_usd", 0) if holdings_value["success"] else 0,
                "holdings_count": len(balance.get("balances", {})) if balance["success"] else 0,
                "equity": trade_balance.get("trade_balance", {}).get("equity", 0) if trade_balance["success"] else 0
            },
            "trading_status": {
                "mode": state_summary.get("mode", "unknown"),
                "halted": state_summary.get("trading_halted", False),
                "halt_reason": state_summary.get("halt_reason", ""),
                "active_strategy": state_summary.get("active_strategy"),
                "trades_remaining": state_summary.get("trades_remaining", 0)
            },
            "today": {
                "trades_count": len(today_trades),
                "realized_pnl": state_summary.get("daily_pnl", 0),
                "loss_current": state_summary.get("daily_loss_current", 0)
            },
            "pending": {
                "approvals_count": len(pending_approvals),
                "approvals": list(pending_approvals.keys())
            },
            "uptime_since": state_summary.get("uptime_since", ""),
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }

    async def track_position(
        self,
        pair: str,
        side: str,
        volume: float,
        entry_price: float,
        decision_id: Optional[int] = None
    ) -> dict:
        """Manually track a position in state."""
        position = Position(
            pair=pair,
            side=side,
            volume=volume,
            entry_price=entry_price,
            entry_time=datetime.utcnow().isoformat() + "Z",
            current_price=entry_price,
            unrealized_pnl=0.0,
            decision_id=decision_id
        )

        self.state.open_position(position)
        self.state.save()

        return {
            "success": True,
            "tracked": {
                "pair": pair,
                "side": side,
                "volume": volume,
                "entry_price": entry_price
            },
            "message": f"Now tracking {side} {volume} {pair} @ ${entry_price}"
        }

    async def close_tracked_position(self, pair: str, close_price: float) -> dict:
        """Close a tracked position."""
        pnl = self.state.close_position(pair, close_price)

        if pnl is None:
            return {"success": False, "error": f"No tracked position for {pair}"}

        self.state.save()

        return {
            "success": True,
            "closed": pair,
            "realized_pnl": round(pnl, 2),
            "close_price": close_price,
            "message": f"Closed {pair} for ${pnl:+.2f}"
        }

    async def get_performance_metrics(self) -> dict:
        """Calculate trading performance metrics."""
        state = self.state.get_state()
        daily_stats = state.daily_stats or {}

        trades_count = daily_stats.get("trades_count", 0)
        wins = daily_stats.get("wins", 0)
        losses = daily_stats.get("losses", 0)

        win_rate = (wins / trades_count * 100) if trades_count > 0 else 0

        return {
            "success": True,
            "metrics": {
                "today": {
                    "trades": trades_count,
                    "wins": wins,
                    "losses": losses,
                    "win_rate_percent": round(win_rate, 1),
                    "realized_pnl": daily_stats.get("realized_pnl", 0),
                    "volume_usd": daily_stats.get("total_volume_usd", 0),
                    "largest_win": daily_stats.get("largest_win", 0),
                    "largest_loss": daily_stats.get("largest_loss", 0)
                },
                "limits": {
                    "trades_remaining": state.trades_remaining_today,
                    "loss_current": state.daily_loss_current,
                    "loss_limit": 25  # From config
                }
            },
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }


# Singleton instance
_portfolio_manager: Optional[PortfolioManager] = None


def get_portfolio_manager() -> PortfolioManager:
    """Get or create portfolio manager singleton."""
    global _portfolio_manager
    if _portfolio_manager is None:
        _portfolio_manager = PortfolioManager()
    return _portfolio_manager


# =========================
# Tool Functions
# =========================

async def portfolio_get_balance() -> dict:
    """Get account balances."""
    manager = get_portfolio_manager()
    return await manager.get_balance()


async def portfolio_get_holdings() -> dict:
    """Get holdings with USD values."""
    manager = get_portfolio_manager()
    return await manager.calculate_holdings_value()


async def portfolio_get_summary() -> dict:
    """Get comprehensive portfolio summary."""
    manager = get_portfolio_manager()
    return await manager.get_portfolio_summary()


async def portfolio_get_performance() -> dict:
    """Get trading performance metrics."""
    manager = get_portfolio_manager()
    return await manager.get_performance_metrics()


async def portfolio_track_position(
    pair: str,
    side: str,
    volume: float,
    entry_price: float,
    decision_id: Optional[int] = None
) -> dict:
    """Track a new position."""
    manager = get_portfolio_manager()
    return await manager.track_position(pair, side, volume, entry_price, decision_id)


async def portfolio_close_position(pair: str, close_price: float) -> dict:
    """Close a tracked position."""
    manager = get_portfolio_manager()
    return await manager.close_tracked_position(pair, close_price)
