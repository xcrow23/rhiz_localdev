"""
Fathom Commander - Strategy Tools
Trading strategy management and signal generation.
"""

import yaml
import os
import sys
from datetime import datetime
from typing import Optional
from pathlib import Path

# Add paths for imports
_this_dir = os.path.dirname(os.path.abspath(__file__))
_parent_dir = os.path.dirname(_this_dir)
sys.path.insert(0, _parent_dir)

try:
    from state import get_state_manager
    from tools.market import get_market_monitor
except ImportError:
    from ..state import get_state_manager
    from .market import get_market_monitor


class StrategyConfig:
    """Strategy configuration loaded from config.yaml."""

    def __init__(self):
        config_path = Path(__file__).parent.parent / "config.yaml"
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)

        self.strategies = self.config.get("strategies", {})
        self.enabled = self.strategies.get("enabled", [])
        self.default = self.strategies.get("default_strategy", "momentum_basic")

    def get_strategy_params(self, name: str) -> dict:
        """Get parameters for a strategy."""
        return self.strategies.get(name, {})


class BaseStrategy:
    """Base class for trading strategies."""

    name: str = "base"
    description: str = "Base strategy class"

    def __init__(self, params: dict = None):
        self.params = params or {}
        self.state = get_state_manager()
        self.market = get_market_monitor()

    async def generate_signal(self, pair: str) -> dict:
        """Generate trading signal for a pair."""
        raise NotImplementedError

    async def should_exit(self, pair: str, entry_price: float, side: str) -> dict:
        """Check if we should exit a position."""
        raise NotImplementedError


class MomentumBasicStrategy(BaseStrategy):
    """
    Basic momentum strategy.
    Follows price direction after significant moves.
    """

    name = "momentum_basic"
    description = "Simple price momentum following"

    def __init__(self, params: dict = None):
        super().__init__(params)
        self.lookback_minutes = params.get("lookback_minutes", 5)
        self.threshold_percent = params.get("threshold_percent", 1.0)
        self.take_profit_percent = params.get("take_profit_percent", 2.0)
        self.stop_loss_percent = params.get("stop_loss_percent", 1.5)
        self.position_size_usd = params.get("position_size_usd", 10)

    async def generate_signal(self, pair: str) -> dict:
        """
        Generate momentum signal based on recent price action.
        Returns signal with direction, confidence, and reasoning.
        """
        # Get OHLC data
        interval = max(1, self.lookback_minutes)  # Use appropriate interval
        ohlc = await self.market.get_ohlc(pair, interval)

        if not ohlc["success"]:
            return {"success": False, "error": "Failed to fetch OHLC data"}

        candles = ohlc.get("candles", [])
        if len(candles) < 5:
            return {"success": False, "error": "Insufficient candle data"}

        # Calculate momentum
        lookback_count = min(self.lookback_minutes, len(candles) - 1)
        current_price = candles[-1]["close"]
        reference_price = candles[-lookback_count - 1]["close"]

        price_change = ((current_price - reference_price) / reference_price) * 100

        # Analyze volume trend
        recent_volume = sum(c["volume"] for c in candles[-3:]) / 3
        older_volume = sum(c["volume"] for c in candles[-6:-3]) / 3 if len(candles) >= 6 else recent_volume
        volume_trend = "increasing" if recent_volume > older_volume * 1.1 else "stable" if recent_volume > older_volume * 0.9 else "decreasing"

        # Generate signal
        signal = "none"
        confidence = 0.0
        reasoning = []

        if abs(price_change) >= self.threshold_percent:
            if price_change > 0:
                signal = "buy"
                reasoning.append(f"Price up {price_change:.2f}% in {self.lookback_minutes}min")
            else:
                signal = "sell"
                reasoning.append(f"Price down {abs(price_change):.2f}% in {self.lookback_minutes}min")

            # Adjust confidence based on volume
            if volume_trend == "increasing":
                confidence = min(0.8, abs(price_change) / self.threshold_percent * 0.6)
                reasoning.append("Volume confirming move")
            else:
                confidence = min(0.6, abs(price_change) / self.threshold_percent * 0.4)
                reasoning.append(f"Volume {volume_trend}")
        else:
            reasoning.append(f"Price change {price_change:.2f}% below threshold {self.threshold_percent}%")

        # Get market conditions
        analysis = await self.market.analyze_market_condition(pair)
        if analysis["success"]:
            market_rec = analysis.get("analysis", {}).get("recommendation", "")
            if market_rec == "avoid":
                confidence *= 0.5
                reasoning.append("Market conditions unfavorable")
            elif market_rec == "caution":
                confidence *= 0.8
                reasoning.append("High volatility - caution")

        return {
            "success": True,
            "pair": pair,
            "signal": signal,
            "confidence": round(confidence, 2),
            "price_change_percent": round(price_change, 2),
            "volume_trend": volume_trend,
            "reasoning": " | ".join(reasoning),
            "suggested_size_usd": self.position_size_usd if signal != "none" else 0,
            "take_profit_percent": self.take_profit_percent,
            "stop_loss_percent": self.stop_loss_percent,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }

    async def should_exit(self, pair: str, entry_price: float, side: str) -> dict:
        """Check if we should exit a position."""
        ticker = await self.market.get_ticker([pair])

        if not ticker["success"]:
            return {"success": False, "error": "Failed to fetch ticker"}

        ticker_data = ticker.get("tickers", {}).get(pair, {})
        current_price = ticker_data.get("price", 0)

        if current_price == 0:
            return {"success": False, "error": "No price data"}

        # Calculate P&L
        if side == "long" or side == "buy":
            pnl_percent = ((current_price - entry_price) / entry_price) * 100
        else:
            pnl_percent = ((entry_price - current_price) / entry_price) * 100

        exit_signal = "hold"
        reason = ""

        if pnl_percent >= self.take_profit_percent:
            exit_signal = "take_profit"
            reason = f"Target reached: +{pnl_percent:.2f}%"
        elif pnl_percent <= -self.stop_loss_percent:
            exit_signal = "stop_loss"
            reason = f"Stop triggered: {pnl_percent:.2f}%"

        return {
            "success": True,
            "pair": pair,
            "exit_signal": exit_signal,
            "current_price": current_price,
            "entry_price": entry_price,
            "pnl_percent": round(pnl_percent, 2),
            "reason": reason,
            "take_profit_target": entry_price * (1 + self.take_profit_percent / 100) if side in ["long", "buy"] else entry_price * (1 - self.take_profit_percent / 100),
            "stop_loss_level": entry_price * (1 - self.stop_loss_percent / 100) if side in ["long", "buy"] else entry_price * (1 + self.stop_loss_percent / 100)
        }


class StrategyManager:
    """Manages strategy selection and execution."""

    STRATEGIES = {
        "momentum_basic": MomentumBasicStrategy
    }

    def __init__(self):
        self.config = StrategyConfig()
        self.state = get_state_manager()
        self._active_strategy: Optional[BaseStrategy] = None
        self._active_name: Optional[str] = None

    def get_available_strategies(self) -> list:
        """Get list of available strategies."""
        return [
            {
                "name": name,
                "description": cls.description,
                "enabled": name in self.config.enabled,
                "active": name == self._active_name
            }
            for name, cls in self.STRATEGIES.items()
        ]

    def activate_strategy(self, name: str) -> dict:
        """Activate a strategy."""
        if name not in self.STRATEGIES:
            return {"success": False, "error": f"Unknown strategy: {name}"}

        if name not in self.config.enabled:
            return {"success": False, "error": f"Strategy not enabled: {name}"}

        params = self.config.get_strategy_params(name)
        strategy_class = self.STRATEGIES[name]

        self._active_strategy = strategy_class(params)
        self._active_name = name
        self.state.set_strategy(name)
        self.state.save()

        return {
            "success": True,
            "activated": name,
            "params": params,
            "message": f"Strategy '{name}' is now active"
        }

    def deactivate_strategy(self) -> dict:
        """Deactivate current strategy."""
        if self._active_name is None:
            return {"success": False, "error": "No active strategy"}

        old_name = self._active_name
        self._active_strategy = None
        self._active_name = None
        self.state.set_strategy(None)
        self.state.save()

        return {
            "success": True,
            "deactivated": old_name,
            "message": "Strategy deactivated - manual mode"
        }

    def get_active_strategy(self) -> Optional[BaseStrategy]:
        """Get the active strategy instance."""
        return self._active_strategy

    async def generate_signal(self, pair: str) -> dict:
        """Generate signal using active strategy."""
        if self._active_strategy is None:
            return {"success": False, "error": "No active strategy"}

        return await self._active_strategy.generate_signal(pair)

    async def check_exits(self) -> dict:
        """Check all positions for exit signals."""
        if self._active_strategy is None:
            return {"success": False, "error": "No active strategy"}

        positions = self.state.get_positions()
        exit_signals = []

        for pair, pos in positions.items():
            result = await self._active_strategy.should_exit(
                pair,
                pos["entry_price"],
                pos["side"]
            )

            if result["success"] and result["exit_signal"] != "hold":
                exit_signals.append({
                    "pair": pair,
                    "signal": result["exit_signal"],
                    "reason": result["reason"],
                    "pnl_percent": result["pnl_percent"]
                })

        return {
            "success": True,
            "positions_checked": len(positions),
            "exit_signals": exit_signals,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }


# Singleton instance
_strategy_manager: Optional[StrategyManager] = None


def get_strategy_manager() -> StrategyManager:
    """Get or create strategy manager singleton."""
    global _strategy_manager
    if _strategy_manager is None:
        _strategy_manager = StrategyManager()
    return _strategy_manager


# =========================
# Tool Functions
# =========================

def strategy_list() -> dict:
    """List available strategies."""
    manager = get_strategy_manager()
    return {
        "success": True,
        "strategies": manager.get_available_strategies(),
        "active": manager._active_name
    }


def strategy_activate(name: str) -> dict:
    """Activate a trading strategy."""
    manager = get_strategy_manager()
    return manager.activate_strategy(name)


def strategy_deactivate() -> dict:
    """Deactivate current strategy."""
    manager = get_strategy_manager()
    return manager.deactivate_strategy()


async def strategy_signal(pair: str) -> dict:
    """Generate trading signal for a pair."""
    manager = get_strategy_manager()
    return await manager.generate_signal(pair)


async def strategy_check_exits() -> dict:
    """Check all positions for exit signals."""
    manager = get_strategy_manager()
    return await manager.check_exits()


async def strategy_analyze_opportunity(pair: str) -> dict:
    """
    Full opportunity analysis - combines market conditions with strategy signal.
    Use this before considering a trade.
    """
    manager = get_strategy_manager()
    market = get_market_monitor()

    # Get market conditions
    market_analysis = await market.analyze_market_condition(pair)

    # Get strategy signal (if strategy active)
    strategy_signal = None
    if manager._active_strategy:
        strategy_signal = await manager.generate_signal(pair)

    # Combine into recommendation
    recommendation = "wait"
    reasoning = []

    if market_analysis["success"]:
        analysis = market_analysis.get("analysis", {})
        if analysis.get("recommendation") == "avoid":
            recommendation = "avoid"
            reasoning.append("Market conditions unfavorable")
        elif analysis.get("recommendation") == "caution":
            reasoning.append("High volatility")

    if strategy_signal and strategy_signal["success"]:
        signal = strategy_signal.get("signal", "none")
        confidence = strategy_signal.get("confidence", 0)

        if signal != "none" and confidence > 0.5:
            if recommendation != "avoid":
                recommendation = signal
                reasoning.append(f"Strategy signal: {signal} ({confidence:.0%} confidence)")
        else:
            reasoning.append("No strong strategy signal")

    return {
        "success": True,
        "pair": pair,
        "recommendation": recommendation,
        "reasoning": " | ".join(reasoning) if reasoning else "No clear signal",
        "market": market_analysis.get("analysis", {}) if market_analysis["success"] else None,
        "strategy_signal": strategy_signal if strategy_signal and strategy_signal["success"] else None,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
