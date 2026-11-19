"""
Fathom Commander - Execution Tools
Order placement with safety checks and approval workflow.
"""

import json
import os
import sys
import urllib.request
import urllib.parse
import uuid
from datetime import datetime, timedelta
from typing import Optional

# Add paths for imports
_this_dir = os.path.dirname(os.path.abspath(__file__))
_parent_dir = os.path.dirname(_this_dir)
sys.path.insert(0, _parent_dir)
sys.path.insert(0, os.path.join(_parent_dir, '..', 'fathom', 'src'))

try:
    from state import get_state_manager, Position, PendingApproval, TradeRecord
    from tools.market import get_market_monitor
except ImportError:
    from ..state import get_state_manager, Position, PendingApproval, TradeRecord
    from .market import get_market_monitor

# Load environment for auth - try multiple paths
env_paths = [
    os.path.join(_parent_dir, '.env'),  # Commander directory
    os.path.join(_parent_dir, '..', '..', '..', '.env'),  # Project root (Windows)
    'C:/Users/dread/Documents/Rhiz/origin/.env',  # Absolute Windows path
    '/mnt/c/Users/dread/Documents/Rhiz/origin/.env',  # WSL path
]

for env_path in env_paths:
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
    try:
        from auth import CredentialManager
    except ImportError:
        CredentialManager = None


class ExecutionEngine:
    """
    Handles order execution with safety checks and approval workflow.
    """

    BASE_URL = "https://api.kraken.com/0"

    # Default limits (can be overridden by config)
    MAX_ORDER_USD = 50
    APPROVAL_THRESHOLD = 20
    MAX_DAILY_TRADES = 10
    MAX_POSITION_PER_PAIR = 100
    MIN_TIME_BETWEEN_TRADES = 60

    def __init__(self):
        self.state = get_state_manager()
        self.market = get_market_monitor()
        self.auth = CredentialManager() if CredentialManager else None
        self._last_trade_time = None

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

    async def check_pre_trade_conditions(self, pair: str, usd_value: float) -> tuple[bool, str]:
        """
        Run all pre-trade safety checks.
        Returns (can_trade, reason).
        """
        # Check if trading allowed
        can_trade, reason = self.state.can_trade()
        if not can_trade:
            return False, reason

        # Check order limits
        limit_ok, limit_reason = self.state.check_order_limits(
            pair, usd_value,
            max_order=self.MAX_ORDER_USD,
            max_position=self.MAX_POSITION_PER_PAIR
        )
        if not limit_ok:
            return False, limit_reason

        # Check time between trades
        if self._last_trade_time:
            elapsed = (datetime.utcnow() - self._last_trade_time).total_seconds()
            if elapsed < self.MIN_TIME_BETWEEN_TRADES:
                return False, f"wait_{int(self.MIN_TIME_BETWEEN_TRADES - elapsed)}_seconds"

        return True, "ok"

    async def estimate_order_value(self, pair: str, volume: float) -> float:
        """Estimate USD value of order."""
        ticker = await self.market.get_ticker([pair])
        if ticker["success"] and pair in ticker.get("tickers", {}):
            price = ticker["tickers"][pair]["price"]
            return price * volume
        return 0.0

    async def request_approval(
        self,
        pair: str,
        side: str,
        volume: float,
        estimated_usd: float,
        reasoning: str,
        hypothesis: str
    ) -> dict:
        """
        Create approval request for Captain.
        Returns approval_id for tracking.
        """
        approval_id = str(uuid.uuid4())[:8]
        now = datetime.utcnow()
        expires = now + timedelta(minutes=30)

        approval = PendingApproval(
            approval_id=approval_id,
            pair=pair,
            side=side,
            volume=volume,
            estimated_usd=estimated_usd,
            reasoning=reasoning,
            hypothesis=hypothesis,
            created_at=now.isoformat() + "Z",
            expires_at=expires.isoformat() + "Z"
        )

        self.state.add_pending_approval(approval)

        return {
            "success": True,
            "requires_approval": True,
            "approval_id": approval_id,
            "estimated_usd": estimated_usd,
            "message": f"Order ${estimated_usd:.2f} requires Captain approval",
            "expires_at": expires.isoformat() + "Z",
            "to_approve": f"Call approve_order('{approval_id}')",
            "order_details": {
                "pair": pair,
                "side": side,
                "volume": volume,
                "reasoning": reasoning,
                "hypothesis": hypothesis
            }
        }

    async def execute_order(
        self,
        pair: str,
        side: str,
        order_type: str,
        volume: float,
        price: Optional[float] = None,
        reasoning: str = "",
        hypothesis: str = "",
        captain_approved: bool = False,
        validate_only: bool = False
    ) -> dict:
        """
        Execute order with full safety checks.

        Args:
            pair: Trading pair (e.g., "XXBTZUSD")
            side: "buy" or "sell"
            order_type: "market" or "limit"
            volume: Order volume in base currency
            price: Limit price (required for limit orders)
            reasoning: Why this trade
            hypothesis: What we're testing
            captain_approved: Set True if Captain has approved
            validate_only: If True, only validate without executing

        Returns:
            Order result with txid or approval request
        """
        # Get estimated value
        estimated_usd = await self.estimate_order_value(pair, volume)

        if estimated_usd == 0:
            return {"success": False, "error": "Could not estimate order value"}

        # Pre-trade checks
        can_trade, reason = await self.check_pre_trade_conditions(pair, estimated_usd)
        if not can_trade:
            return {"success": False, "error": reason}

        # Check if needs approval
        needs_approval = self.state.requires_approval(estimated_usd, self.APPROVAL_THRESHOLD)

        if needs_approval and not captain_approved:
            return await self.request_approval(
                pair, side, volume, estimated_usd, reasoning, hypothesis
            )

        # Validate only mode
        if validate_only:
            return {
                "success": True,
                "validated": True,
                "would_execute": {
                    "pair": pair,
                    "side": side,
                    "order_type": order_type,
                    "volume": volume,
                    "estimated_usd": estimated_usd
                }
            }

        # Log decision to memory BEFORE executing
        try:
            from memory.logger import FathomMemory
            memory = FathomMemory()
            log_result = memory.log_trade_decision(
                pair=pair,
                side=side,
                decision_type=order_type,
                reasoning=reasoning,
                hypothesis=hypothesis,
                trade_data={
                    "volume": volume,
                    "price": price,
                    "estimated_usd": estimated_usd,
                    "captain_approved": captain_approved
                }
            )
            decision_id = log_result.get("point_id")
        except Exception as e:
            decision_id = None
            print(f"[Execution] Memory logging failed: {e}")

        # Execute order
        order_data = {
            "pair": pair,
            "type": side,
            "ordertype": order_type,
            "volume": str(volume)
        }

        if price is not None and order_type == "limit":
            order_data["price"] = str(price)

        result = self._authenticated_request("private/AddOrder", order_data)

        if not result["success"]:
            # Update memory with failure
            if decision_id:
                try:
                    memory.update_outcome(decision_id, "failure", {"error": result["error"]})
                except:
                    pass
            return result

        # Success - extract txid
        txid = result["result"].get("txid", [None])[0]

        if not txid:
            return {"success": False, "error": "No transaction ID returned"}

        # Update memory with success
        if decision_id:
            try:
                memory.update_outcome(decision_id, "pending", {"txid": txid})
            except:
                pass

        # Record trade in state
        trade = TradeRecord(
            txid=txid,
            pair=pair,
            side=side,
            volume=volume,
            price=price or 0,
            cost=estimated_usd,
            fee=0,  # Will be updated after fill
            timestamp=datetime.utcnow().isoformat() + "Z",
            decision_id=decision_id
        )
        self.state.record_trade(trade)

        # Update last trade time
        self._last_trade_time = datetime.utcnow()

        return {
            "success": True,
            "txid": txid,
            "decision_id": decision_id,
            "estimated_usd": estimated_usd,
            "message": f"Order placed! {side} {volume} {pair}",
            "description": result["result"].get("descr", {}).get("order", "")
        }

    async def approve_pending_order(self, approval_id: str) -> dict:
        """
        Approve a pending order and execute it.
        Called when Captain approves via Slack.
        """
        approval = self.state.approve_order(approval_id)

        if not approval:
            return {"success": False, "error": f"No pending approval: {approval_id}"}

        # Execute the approved order
        return await self.execute_order(
            pair=approval["pair"],
            side=approval["side"],
            order_type="market",  # Approved orders execute as market
            volume=approval["volume"],
            reasoning=approval["reasoning"],
            hypothesis=approval["hypothesis"],
            captain_approved=True
        )

    async def reject_pending_order(self, approval_id: str, reason: str = "") -> dict:
        """Reject a pending order."""
        success = self.state.reject_order(approval_id, reason)

        if not success:
            return {"success": False, "error": f"No pending approval: {approval_id}"}

        # Log rejection to memory
        try:
            from memory.logger import FathomMemory
            memory = FathomMemory()
            memory.log_trade_decision(
                pair="N/A",
                side="rejected",
                decision_type="approval_rejected",
                reasoning=f"Captain rejected: {reason}",
                hypothesis="N/A"
            )
        except:
            pass

        return {
            "success": True,
            "rejected": approval_id,
            "reason": reason,
            "message": "Order rejected by Captain"
        }

    async def cancel_order(self, txid: str, reason: str = "") -> dict:
        """Cancel an open order."""
        result = self._authenticated_request("private/CancelOrder", {"txid": txid})

        if not result["success"]:
            return result

        return {
            "success": True,
            "cancelled": txid,
            "count": result["result"].get("count", 1),
            "reason": reason
        }

    async def get_open_orders(self) -> dict:
        """Get all open orders."""
        result = self._authenticated_request("private/OpenOrders", {"trades": False})

        if not result["success"]:
            return result

        orders = result["result"].get("open", {})

        return {
            "success": True,
            "count": len(orders),
            "orders": [
                {
                    "txid": txid,
                    "pair": order["descr"]["pair"],
                    "side": order["descr"]["type"],
                    "order_type": order["descr"]["ordertype"],
                    "volume": order["vol"],
                    "price": order["descr"].get("price", "market"),
                    "status": order["status"]
                }
                for txid, order in orders.items()
            ]
        }

    async def get_recent_trades(self, count: int = 10) -> dict:
        """Get recent trade history."""
        result = self._authenticated_request("private/TradesHistory", {"type": "all"})

        if not result["success"]:
            return result

        trades = result["result"].get("trades", {})
        trade_list = list(trades.items())[:count]

        return {
            "success": True,
            "count": len(trade_list),
            "trades": [
                {
                    "txid": txid,
                    "pair": trade["pair"],
                    "side": trade["type"],
                    "volume": trade["vol"],
                    "price": trade["price"],
                    "cost": trade["cost"],
                    "fee": trade["fee"],
                    "time": trade["time"]
                }
                for txid, trade in trade_list
            ]
        }


# Singleton instance
_execution_engine: Optional[ExecutionEngine] = None


def get_execution_engine() -> ExecutionEngine:
    """Get or create execution engine singleton."""
    global _execution_engine
    if _execution_engine is None:
        _execution_engine = ExecutionEngine()
    return _execution_engine


# =========================
# Tool Functions
# =========================

async def execute_trade(
    pair: str,
    side: str,
    order_type: str,
    volume: float,
    price: Optional[float] = None,
    reasoning: str = "",
    hypothesis: str = "",
    captain_approved: bool = False
) -> dict:
    """Execute a trade with safety checks."""
    engine = get_execution_engine()
    return await engine.execute_order(
        pair, side, order_type, volume, price,
        reasoning, hypothesis, captain_approved
    )


async def validate_trade(
    pair: str,
    side: str,
    order_type: str,
    volume: float,
    price: Optional[float] = None
) -> dict:
    """Validate a trade without executing."""
    engine = get_execution_engine()
    return await engine.execute_order(
        pair, side, order_type, volume, price,
        validate_only=True
    )


async def approve_order(approval_id: str) -> dict:
    """Approve a pending order (Captain command)."""
    engine = get_execution_engine()
    return await engine.approve_pending_order(approval_id)


async def reject_order(approval_id: str, reason: str = "") -> dict:
    """Reject a pending order (Captain command)."""
    engine = get_execution_engine()
    return await engine.reject_pending_order(approval_id, reason)


async def cancel_order(txid: str, reason: str = "") -> dict:
    """Cancel an open order."""
    engine = get_execution_engine()
    return await engine.cancel_order(txid, reason)


async def get_open_orders() -> dict:
    """Get open orders."""
    engine = get_execution_engine()
    return await engine.get_open_orders()


async def get_trade_history(count: int = 10) -> dict:
    """Get recent trades."""
    engine = get_execution_engine()
    return await engine.get_recent_trades(count)
