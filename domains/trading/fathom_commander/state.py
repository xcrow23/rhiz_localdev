"""
Fathom Commander - State Management
Persistent state tracking for trading operations.
"""

import json
import os
from datetime import datetime, date
from pathlib import Path
from typing import Any, Optional
from dataclasses import dataclass, field, asdict
import threading


@dataclass
class Position:
    """Represents an open position."""
    pair: str
    side: str  # "long" or "short"
    volume: float
    entry_price: float
    entry_time: str
    current_price: float = 0.0
    unrealized_pnl: float = 0.0
    decision_id: Optional[int] = None


@dataclass
class PendingApproval:
    """Order pending Captain approval."""
    approval_id: str
    pair: str
    side: str
    volume: float
    estimated_usd: float
    reasoning: str
    hypothesis: str
    created_at: str
    expires_at: str
    slack_message_ts: Optional[str] = None


@dataclass
class TradeRecord:
    """Record of an executed trade."""
    txid: str
    pair: str
    side: str
    volume: float
    price: float
    cost: float
    fee: float
    timestamp: str
    decision_id: Optional[int] = None
    outcome: str = "pending"  # pending, profit, loss


@dataclass
class DailyStats:
    """Daily trading statistics."""
    date: str
    trades_count: int = 0
    total_volume_usd: float = 0.0
    realized_pnl: float = 0.0
    wins: int = 0
    losses: int = 0
    largest_win: float = 0.0
    largest_loss: float = 0.0


@dataclass
class CommanderState:
    """Complete commander state."""
    # Metadata
    version: str = "1.0.0"
    last_updated: str = ""
    start_time: str = ""

    # Operational state
    mode: str = "paper"  # live, paper, disabled, emergency_stop
    active_strategy: Optional[str] = None

    # Positions and orders
    positions: dict = field(default_factory=dict)  # pair -> Position
    pending_approvals: dict = field(default_factory=dict)  # approval_id -> PendingApproval
    open_orders: list = field(default_factory=list)  # List of order txids

    # Trade history (today only, archived daily)
    trades_today: list = field(default_factory=list)  # List of TradeRecord
    daily_stats: Optional[dict] = None  # DailyStats as dict

    # Market state cache
    last_prices: dict = field(default_factory=dict)  # pair -> price
    last_market_update: str = ""

    # Health tracking
    last_heartbeat: str = ""
    consecutive_errors: int = 0
    last_error: str = ""

    # Limits tracking
    trades_remaining_today: int = 10
    daily_loss_current: float = 0.0
    trading_halted: bool = False
    halt_reason: str = ""


class StateManager:
    """
    Manages persistent state for Fathom Commander.
    Thread-safe with auto-save capability.
    """

    def __init__(self, state_file: str = "state/commander_state.json"):
        self.state_file = Path(__file__).parent / state_file
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.RLock()  # Reentrant lock to prevent deadlock
        self._state: CommanderState = self._load_or_create()

    def _load_or_create(self) -> CommanderState:
        """Load state from file or create new."""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r') as f:
                    data = json.load(f)
                    state = CommanderState(**data)

                    # Check if new day - reset daily counters
                    if state.daily_stats:
                        stats_date = state.daily_stats.get("date", "")
                        if stats_date != date.today().isoformat():
                            state = self._reset_daily(state)

                    return state
            except Exception as e:
                print(f"[State] Error loading state: {e}, creating new")

        return self._create_new_state()

    def _create_new_state(self) -> CommanderState:
        """Create fresh state."""
        now = datetime.utcnow().isoformat() + "Z"
        return CommanderState(
            last_updated=now,
            start_time=now,
            daily_stats=asdict(DailyStats(date=date.today().isoformat())),
            trades_remaining_today=10
        )

    def _reset_daily(self, state: CommanderState) -> CommanderState:
        """Reset daily counters for new day."""
        state.daily_stats = asdict(DailyStats(date=date.today().isoformat()))
        state.trades_today = []
        state.trades_remaining_today = 10
        state.daily_loss_current = 0.0

        # Only clear halt if it was due to daily limits
        if state.halt_reason in ["daily_loss_limit", "daily_trade_limit"]:
            state.trading_halted = False
            state.halt_reason = ""

        return state

    def save(self):
        """Save state to file."""
        with self._lock:
            self._state.last_updated = datetime.utcnow().isoformat() + "Z"

            with open(self.state_file, 'w') as f:
                json.dump(asdict(self._state), f, indent=2)

    def get_state(self) -> CommanderState:
        """Get current state (read-only copy)."""
        with self._lock:
            return CommanderState(**asdict(self._state))

    # =========================
    # Operational Methods
    # =========================

    def update_heartbeat(self):
        """Update last heartbeat time."""
        with self._lock:
            self._state.last_heartbeat = datetime.utcnow().isoformat() + "Z"
            self._state.consecutive_errors = 0

    def record_error(self, error: str):
        """Record an error occurrence."""
        with self._lock:
            self._state.consecutive_errors += 1
            self._state.last_error = error

    def set_mode(self, mode: str):
        """Set operational mode."""
        valid_modes = ["live", "paper", "disabled", "emergency_stop"]
        if mode not in valid_modes:
            raise ValueError(f"Invalid mode: {mode}")

        with self._lock:
            self._state.mode = mode
            if mode == "emergency_stop":
                self._state.trading_halted = True
                self._state.halt_reason = "emergency_stop"

    def set_strategy(self, strategy: Optional[str]):
        """Set active strategy."""
        with self._lock:
            self._state.active_strategy = strategy

    # =========================
    # Position Management
    # =========================

    def open_position(self, position: Position):
        """Record a new position."""
        with self._lock:
            self._state.positions[position.pair] = asdict(position)

    def close_position(self, pair: str, close_price: float) -> Optional[float]:
        """Close a position and return realized P&L."""
        with self._lock:
            if pair not in self._state.positions:
                return None

            pos = self._state.positions[pair]
            entry_price = pos["entry_price"]
            volume = pos["volume"]
            side = pos["side"]

            # Calculate P&L
            if side == "long":
                pnl = (close_price - entry_price) * volume
            else:
                pnl = (entry_price - close_price) * volume

            # Update daily stats
            self._update_daily_pnl(pnl)

            # Remove position
            del self._state.positions[pair]

            return pnl

    def update_position_price(self, pair: str, current_price: float):
        """Update current price and unrealized P&L for a position."""
        with self._lock:
            if pair in self._state.positions:
                pos = self._state.positions[pair]
                pos["current_price"] = current_price

                entry_price = pos["entry_price"]
                volume = pos["volume"]
                side = pos["side"]

                if side == "long":
                    pos["unrealized_pnl"] = (current_price - entry_price) * volume
                else:
                    pos["unrealized_pnl"] = (entry_price - current_price) * volume

    def get_positions(self) -> dict:
        """Get all open positions."""
        with self._lock:
            return dict(self._state.positions)

    # =========================
    # Approval Management
    # =========================

    def add_pending_approval(self, approval: PendingApproval) -> str:
        """Add a pending approval request."""
        with self._lock:
            self._state.pending_approvals[approval.approval_id] = asdict(approval)
            return approval.approval_id

    def approve_order(self, approval_id: str) -> Optional[dict]:
        """Mark approval as approved and return order details."""
        with self._lock:
            if approval_id in self._state.pending_approvals:
                approval = self._state.pending_approvals.pop(approval_id)
                return approval
            return None

    def reject_order(self, approval_id: str, reason: str = "") -> bool:
        """Reject a pending approval."""
        with self._lock:
            if approval_id in self._state.pending_approvals:
                del self._state.pending_approvals[approval_id]
                return True
            return False

    def get_pending_approvals(self) -> dict:
        """Get all pending approvals."""
        with self._lock:
            return dict(self._state.pending_approvals)

    def expire_old_approvals(self, timeout_minutes: int = 30) -> list:
        """Expire approvals older than timeout. Returns expired IDs."""
        expired = []
        now = datetime.utcnow()

        with self._lock:
            to_remove = []
            for approval_id, approval in self._state.pending_approvals.items():
                expires_at = datetime.fromisoformat(approval["expires_at"].replace("Z", ""))
                if now > expires_at:
                    to_remove.append(approval_id)
                    expired.append(approval_id)

            for approval_id in to_remove:
                del self._state.pending_approvals[approval_id]

        return expired

    # =========================
    # Trade Recording
    # =========================

    def record_trade(self, trade: TradeRecord) -> bool:
        """Record a trade and update limits."""
        with self._lock:
            # Check if we can trade
            if self._state.trading_halted:
                return False

            if self._state.trades_remaining_today <= 0:
                self._state.trading_halted = True
                self._state.halt_reason = "daily_trade_limit"
                return False

            # Record trade
            self._state.trades_today.append(asdict(trade))
            self._state.trades_remaining_today -= 1

            # Update daily stats
            if self._state.daily_stats:
                self._state.daily_stats["trades_count"] += 1
                self._state.daily_stats["total_volume_usd"] += trade.cost

            return True

    def _update_daily_pnl(self, pnl: float):
        """Update daily P&L and check limits."""
        if self._state.daily_stats:
            self._state.daily_stats["realized_pnl"] += pnl

            if pnl >= 0:
                self._state.daily_stats["wins"] += 1
                if pnl > self._state.daily_stats.get("largest_win", 0):
                    self._state.daily_stats["largest_win"] = pnl
            else:
                self._state.daily_stats["losses"] += 1
                self._state.daily_loss_current += abs(pnl)
                if abs(pnl) > abs(self._state.daily_stats.get("largest_loss", 0)):
                    self._state.daily_stats["largest_loss"] = pnl

        # Check daily loss limit (default $25)
        if self._state.daily_loss_current >= 25:
            self._state.trading_halted = True
            self._state.halt_reason = "daily_loss_limit"

    def get_trades_today(self) -> list:
        """Get today's trades."""
        with self._lock:
            return list(self._state.trades_today)

    # =========================
    # Market State
    # =========================

    def update_prices(self, prices: dict):
        """Update cached prices."""
        with self._lock:
            self._state.last_prices.update(prices)
            self._state.last_market_update = datetime.utcnow().isoformat() + "Z"

            # Update position unrealized P&L
            for pair, price in prices.items():
                if pair in self._state.positions:
                    self.update_position_price(pair, price)

    def get_price(self, pair: str) -> Optional[float]:
        """Get cached price for a pair."""
        with self._lock:
            return self._state.last_prices.get(pair)

    # =========================
    # Limit Checks
    # =========================

    def can_trade(self) -> tuple[bool, str]:
        """Check if trading is allowed. Returns (allowed, reason)."""
        with self._lock:
            if self._state.trading_halted:
                return False, self._state.halt_reason

            if self._state.mode != "live":
                return False, f"mode_{self._state.mode}"

            if self._state.trades_remaining_today <= 0:
                return False, "daily_trade_limit"

            return True, "ok"

    def check_order_limits(self, pair: str, usd_value: float, max_order: float = 50,
                           max_position: float = 100) -> tuple[bool, str]:
        """Check if order within limits. Returns (allowed, reason)."""
        with self._lock:
            # Check max order size
            if usd_value > max_order:
                return False, f"exceeds_max_order_{max_order}"

            # Check position limit
            current_position = 0.0
            if pair in self._state.positions:
                pos = self._state.positions[pair]
                current_position = pos["volume"] * pos.get("current_price", pos["entry_price"])

            if current_position + usd_value > max_position:
                return False, f"exceeds_position_limit_{max_position}"

            return True, "ok"

    def requires_approval(self, usd_value: float, threshold: float = 20) -> bool:
        """Check if order requires Captain approval."""
        return usd_value > threshold

    # =========================
    # Summary Methods
    # =========================

    def get_summary(self) -> dict:
        """Get state summary for heartbeat."""
        with self._lock:
            return {
                "mode": self._state.mode,
                "active_strategy": self._state.active_strategy,
                "trading_halted": self._state.trading_halted,
                "halt_reason": self._state.halt_reason,
                "positions_count": len(self._state.positions),
                "pending_approvals_count": len(self._state.pending_approvals),
                "trades_today": len(self._state.trades_today),
                "trades_remaining": self._state.trades_remaining_today,
                "daily_pnl": self._state.daily_stats.get("realized_pnl", 0) if self._state.daily_stats else 0,
                "daily_loss_current": self._state.daily_loss_current,
                "last_heartbeat": self._state.last_heartbeat,
                "consecutive_errors": self._state.consecutive_errors,
                "uptime_since": self._state.start_time
            }


# Singleton instance
_state_manager: Optional[StateManager] = None


def get_state_manager() -> StateManager:
    """Get or create state manager singleton."""
    global _state_manager
    if _state_manager is None:
        _state_manager = StateManager()
    return _state_manager
