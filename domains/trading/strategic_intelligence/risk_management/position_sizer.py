"""
Position Sizer
Calculate optimal position sizes based on risk parameters.

Philosophy: In crypto, position sizing IS risk management.
Conservative Kelly Criterion-inspired approach with hard caps.

NEVER:
- Risk more than portfolio can sustain
- Size positions assuming "can't lose"
- Ignore volatility when sizing

ALWAYS:
- Size based on stop loss distance
- Adjust for volatility
- Respect portfolio limits
"""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Dict
import math


@dataclass
class PositionSize:
    """
    Calculated position size with risk metrics.
    """
    # Position sizing
    size_usd: float
    size_btc: float
    entry_price: float

    # Risk metrics
    risk_amount_usd: float
    risk_percent: float
    stop_loss_price: float
    profit_target_price: float

    # Expected value
    expected_value: float
    reward_risk_ratio: float

    # Adjustments applied
    adjustments: Dict[str, float]

    # TRACE_FE
    trace_factors: List[dict]

    # Metadata
    timestamp: datetime


class PositionSizer:
    """
    Calculate position sizes using conservative risk-first approach.

    Size calculation steps:
    1. Determine max risk amount (% of portfolio)
    2. Calculate position size from stop loss distance
    3. Apply volatility adjustment
    4. Apply confidence scaling
    5. Apply portfolio allocation caps
    6. Validate against global limits
    """

    def __init__(self, crypto_mode: bool = True):
        """
        Initialize position sizer.

        Args:
            crypto_mode: If True, use crypto-appropriate adjustments
        """
        self.crypto_mode = crypto_mode

    def calculate(
        self,
        strategy_config: dict,
        market_context: dict,
        portfolio_state: dict,
        current_price: float,
        confidence: float
    ) -> PositionSize:
        """
        Calculate optimal position size.

        Args:
            strategy_config: Strategy risk parameters
            market_context: Current market conditions (volatility, etc.)
            portfolio_state: Portfolio value and exposure
            current_price: Current BTC price
            confidence: Strategy confidence (0-1)

        Returns:
            PositionSize with all calculations and reasoning
        """
        trace_factors = []
        adjustments = {}

        portfolio_value = portfolio_state.get('total_value', 0)

        if portfolio_value == 0:
            return self._zero_position("No portfolio value", trace_factors)

        # Step 1: Calculate base risk amount
        risk_config = strategy_config.get('risk', {})
        max_risk_per_trade = risk_config.get('stop_loss', 0.03)  # 3% default
        global_max_risk = portfolio_state.get('global_risk_limits', {}).get('max_risk_per_trade', 0.02)

        # Use more conservative of the two
        risk_percent = min(max_risk_per_trade, global_max_risk)
        risk_amount_usd = portfolio_value * risk_percent

        trace_factors.append({
            "factor": "risk_allocation",
            "explanation": f"Risking {risk_percent*100:.1f}% of ${portfolio_value:.2f} portfolio = ${risk_amount_usd:.2f}",
            "confidence": 1.0
        })

        # Step 2: Calculate position size from stop loss
        stop_loss_percent = risk_config.get('stop_loss', 0.03)

        # Validate stop loss (prevent division by zero)
        if stop_loss_percent <= 0:
            return self._zero_position(
                f"Invalid stop loss: {stop_loss_percent*100:.2f}% (must be > 0)",
                trace_factors
            )

        # Position size formula:
        # If we risk $X and stop is Y% away, position size = $X / Y
        # Example: Risk $1, stop 3% away → position = $1 / 0.03 = $33.33
        base_position_usd = risk_amount_usd / stop_loss_percent

        adjustments['base_calculation'] = base_position_usd

        trace_factors.append({
            "factor": "stop_loss_sizing",
            "explanation": f"Risk ${risk_amount_usd:.2f} with {stop_loss_percent*100:.1f}% stop = ${base_position_usd:.2f} position",
            "confidence": 0.95
        })

        # Step 3: Volatility adjustment
        volatility_percentile = market_context.get('volatility_percentile', 50)
        volatility_level = market_context.get('volatility_level', 'normal')

        volatility_scalar = self._calculate_volatility_adjustment(
            volatility_percentile,
            volatility_level
        )

        position_usd = base_position_usd * volatility_scalar
        adjustments['volatility_adjustment'] = volatility_scalar

        if volatility_scalar < 1.0:
            trace_factors.append({
                "factor": "volatility_reduction",
                "explanation": f"Reduced {(1-volatility_scalar)*100:.0f}% due to {volatility_level} volatility ({volatility_percentile:.0f}th percentile)",
                "confidence": 0.85
            })
        elif volatility_scalar > 1.0:
            trace_factors.append({
                "factor": "volatility_increase",
                "explanation": f"Increased {(volatility_scalar-1)*100:.0f}% due to low volatility",
                "confidence": 0.75
            })

        # Step 4: Confidence scaling
        confidence_scalar = self._calculate_confidence_adjustment(confidence)
        position_usd *= confidence_scalar
        adjustments['confidence_adjustment'] = confidence_scalar

        if confidence_scalar < 1.0:
            trace_factors.append({
                "factor": "confidence_scaling",
                "explanation": f"Reduced {(1-confidence_scalar)*100:.0f}% due to confidence level {confidence:.2f}",
                "confidence": confidence
            })

        # Step 5: Portfolio allocation cap
        max_position_size_percent = risk_config.get('max_position_size', 0.30)
        max_position_usd = portfolio_value * max_position_size_percent

        if position_usd > max_position_usd:
            allocation_cap_applied = True
            position_usd = max_position_usd
            adjustments['allocation_cap'] = max_position_size_percent

            trace_factors.append({
                "factor": "allocation_cap",
                "explanation": f"Capped at {max_position_size_percent*100:.0f}% of portfolio (${max_position_usd:.2f})",
                "confidence": 1.0
            })
        else:
            allocation_cap_applied = False

        # Step 6: Minimum position size (don't trade dust)
        min_position_usd = 5.0  # $5 minimum
        if position_usd < min_position_usd:
            return self._zero_position(
                f"Calculated position (${position_usd:.2f}) below minimum (${min_position_usd})",
                trace_factors
            )

        # Convert to BTC
        size_btc = position_usd / current_price

        # Calculate stop loss and profit target prices
        stop_loss_price = current_price * (1 - stop_loss_percent)

        profit_target_percent = risk_config.get('profit_target', stop_loss_percent * 2)
        profit_target_price = current_price * (1 + profit_target_percent)

        # Calculate expected value
        # EV = (win_rate * avg_win) - (loss_rate * avg_loss)
        expected_perf = strategy_config.get('expected_performance', {})
        win_rate = expected_perf.get('win_rate', 0.50)
        reward_risk = expected_perf.get('reward_risk_ratio', 2.0)

        expected_value = (win_rate * reward_risk) - ((1 - win_rate) * 1.0)
        expected_value_usd = expected_value * risk_amount_usd

        trace_factors.append({
            "factor": "expected_value",
            "explanation": f"EV = ${expected_value_usd:+.2f} ({win_rate*100:.0f}% win rate, {reward_risk:.1f}:1 R:R)",
            "confidence": 0.6
        })

        return PositionSize(
            size_usd=position_usd,
            size_btc=size_btc,
            entry_price=current_price,
            risk_amount_usd=risk_amount_usd,
            risk_percent=risk_percent,
            stop_loss_price=stop_loss_price,
            profit_target_price=profit_target_price,
            expected_value=expected_value_usd,
            reward_risk_ratio=reward_risk,
            adjustments=adjustments,
            trace_factors=trace_factors,
            timestamp=datetime.utcnow()
        )

    def _calculate_volatility_adjustment(self, percentile: float, level: str) -> float:
        """
        Adjust position size based on volatility.

        Higher volatility → smaller position
        Lower volatility → can take slightly larger position
        """
        if level == "extreme":
            return 0.5  # Cut position in half
        elif level == "high":
            return 0.75  # Reduce 25%
        elif percentile < 30:
            return 1.15  # Increase 15% in low vol
        else:
            return 1.0  # Normal

    def _calculate_confidence_adjustment(self, confidence: float) -> float:
        """
        Scale position by confidence level.

        Low confidence → smaller position
        High confidence → normal position
        """
        if confidence < 0.6:
            return 0.5  # Cut in half if low confidence
        elif confidence < 0.75:
            return 0.75  # Reduce if moderate confidence
        else:
            return confidence  # Scale linearly for high confidence

    def _zero_position(self, reason: str, trace_factors: List[dict]) -> PositionSize:
        """Return zero position with explanation."""
        trace_factors.append({
            "factor": "no_position",
            "explanation": reason,
            "confidence": 1.0
        })

        return PositionSize(
            size_usd=0.0,
            size_btc=0.0,
            entry_price=0.0,
            risk_amount_usd=0.0,
            risk_percent=0.0,
            stop_loss_price=0.0,
            profit_target_price=0.0,
            expected_value=0.0,
            reward_risk_ratio=0.0,
            adjustments={},
            trace_factors=trace_factors,
            timestamp=datetime.utcnow()
        )


class RiskManager:
    """
    Enforce risk controls and circuit breakers.

    Monitors:
    - Daily loss limits
    - Trade count limits
    - Consecutive loss limits
    - Drawdown limits

    State persists to file to prevent bypassing limits via restart.
    """

    def __init__(self, state_dir: str = None):
        """
        Initialize RiskManager with persistent state.

        Args:
            state_dir: Directory to store state files (default: ./risk_state/)
        """
        from pathlib import Path
        import json
        import os

        if state_dir is None:
            # Default to risk_state directory in same location as this file
            state_dir = Path(__file__).parent.parent / "risk_state"

        self.state_dir = Path(state_dir)
        self.state_dir.mkdir(parents=True, exist_ok=True)

        # Load or initialize state
        self.daily_stats = self._load_state()

    def check_trade_allowed(
        self,
        position_size: PositionSize,
        portfolio_state: dict,
        global_limits: dict,
        market_data: dict = None
    ) -> tuple:
        """
        Check if trade is allowed under current risk constraints.

        Args:
            position_size: Proposed position
            portfolio_state: Current portfolio state
            global_limits: Risk limit configuration
            market_data: Optional market data for flash crash detection
                        Format: {'price_15min_ago': float, 'current_price': float}

        Returns: (allowed: bool, reason: str)
        """
        portfolio_value = portfolio_state.get('total_value', 0)

        # Circuit Breaker 1: Flash crash detection
        if market_data:
            flash_crash_check = self._check_flash_crash(market_data, global_limits)
            if not flash_crash_check[0]:
                return flash_crash_check

        # Circuit Breaker 2: Drawdown limit
        drawdown_check = self._check_drawdown_limit(portfolio_value, global_limits)
        if not drawdown_check[0]:
            return drawdown_check

        # Circuit Breaker 3: Correlation/concentration limit
        correlation_check = self._check_correlation_limit(
            position_size,
            portfolio_state,
            global_limits
        )
        if not correlation_check[0]:
            return correlation_check

        # Check daily trade limit
        max_trades_daily = global_limits.get('max_daily_trades', 10)
        if self.daily_stats['trades_today'] >= max_trades_daily:
            return False, f"Daily trade limit reached ({max_trades_daily})"

        # Check daily loss limit
        max_daily_loss_percent = global_limits.get('max_daily_loss', 0.05)
        max_daily_loss_usd = portfolio_value * max_daily_loss_percent

        if self.daily_stats['pnl_today'] <= -max_daily_loss_usd:
            return False, f"Daily loss limit reached (${-self.daily_stats['pnl_today']:.2f})"

        # Circuit Breaker 4: Consecutive loss limit with manual override
        max_consecutive_losses = global_limits.get('max_consecutive_losses', 5)
        if self.daily_stats['consecutive_losses'] >= max_consecutive_losses:
            # Trip circuit breaker
            self.daily_stats['circuit_breaker_tripped'] = True
            self.daily_stats['circuit_breaker_reason'] = f"Consecutive losses: {self.daily_stats['consecutive_losses']}"
            self._save_state()
            return False, f"🛑 CIRCUIT BREAKER TRIPPED: {max_consecutive_losses} consecutive losses - CAPTAIN OVERRIDE REQUIRED (call captain_override_circuit_breaker())"

        # Check if circuit breaker was previously tripped and not reset
        if self.daily_stats.get('circuit_breaker_tripped', False):
            reason = self.daily_stats.get('circuit_breaker_reason', 'Unknown reason')
            return False, f"🛑 CIRCUIT BREAKER ACTIVE: {reason} - CAPTAIN OVERRIDE REQUIRED (call captain_override_circuit_breaker())"

        # Check position risk vs remaining daily risk budget
        remaining_daily_risk = max_daily_loss_usd + self.daily_stats['pnl_today']
        if position_size.risk_amount_usd > remaining_daily_risk:
            return False, f"Position risk (${position_size.risk_amount_usd:.2f}) exceeds daily budget (${remaining_daily_risk:.2f})"

        # All checks passed
        return True, "Trade allowed"

    def _check_drawdown_limit(self, current_portfolio_value: float, global_limits: dict) -> tuple:
        """
        Track peak portfolio value and check for excessive drawdown.

        This prevents the scenario where daily losses stay within limits
        but cumulative drawdown exceeds acceptable levels.

        Returns: (allowed: bool, reason: str)
        """
        # Update peak value if current value is higher
        peak_value = self.daily_stats.get('peak_portfolio_value', current_portfolio_value)

        if current_portfolio_value > peak_value:
            self.daily_stats['peak_portfolio_value'] = current_portfolio_value
            self.daily_stats['max_drawdown_from_peak'] = 0.0
            peak_value = current_portfolio_value

        # Calculate current drawdown from peak
        if peak_value > 0:
            current_drawdown = (peak_value - current_portfolio_value) / peak_value
            self.daily_stats['max_drawdown_from_peak'] = max(
                current_drawdown,
                self.daily_stats.get('max_drawdown_from_peak', 0.0)
            )
        else:
            current_drawdown = 0.0

        # Check against max drawdown limit (default 15%)
        max_drawdown_threshold = global_limits.get('max_drawdown', 0.15)

        if current_drawdown >= max_drawdown_threshold:
            return False, f"Drawdown circuit breaker: {current_drawdown*100:.1f}% from peak ${peak_value:.2f} → ${current_portfolio_value:.2f}"

        return True, "Drawdown within limits"

    def _check_flash_crash(self, market_data: dict, global_limits: dict) -> tuple:
        """
        Detect flash crashes (rapid price drops) and halt trading.

        Flash crashes can cause:
        - Stop losses to execute at terrible prices
        - Slippage to spike dramatically
        - Emotional panic decisions

        Args:
            market_data: Dict with 'price_15min_ago' and 'current_price'
            global_limits: Risk configuration

        Returns: (allowed: bool, reason: str)
        """
        price_15min_ago = market_data.get('price_15min_ago')
        current_price = market_data.get('current_price')

        if not price_15min_ago or not current_price or price_15min_ago <= 0:
            # Missing data - allow trade but log warning
            return True, "Flash crash check skipped (missing price data)"

        # Calculate 15-minute price change
        price_change = (current_price - price_15min_ago) / price_15min_ago

        # Flash crash threshold (default -8% in 15 minutes)
        flash_crash_threshold = global_limits.get('flash_crash_threshold', -0.08)

        if price_change <= flash_crash_threshold:
            return False, f"Flash crash detected: {price_change*100:.1f}% drop in 15min (${price_15min_ago:.2f} → ${current_price:.2f})"

        # Also check for extreme upward moves (potential manipulation)
        flash_pump_threshold = global_limits.get('flash_pump_threshold', 0.10)  # +10% in 15min

        if price_change >= flash_pump_threshold:
            return False, f"Flash pump detected: {price_change*100:.1f}% rise in 15min - possible manipulation"

        return True, "No flash crash detected"

    def _check_correlation_limit(
        self,
        position_size: PositionSize,
        portfolio_state: dict,
        global_limits: dict
    ) -> tuple:
        """
        Check total exposure to correlated assets.

        Prevents scenario where multiple "independent" positions
        are actually all correlated (e.g., 3 BTC long strategies = 3x BTC exposure).

        Args:
            position_size: New position to add
            portfolio_state: Current positions
            global_limits: Risk configuration

        Returns: (allowed: bool, reason: str)
        """
        # Calculate total BTC exposure (current + proposed)
        current_positions = portfolio_state.get('positions', {})
        total_btc_exposure_usd = 0.0

        # Sum all existing BTC positions
        for pos_id, position in current_positions.items():
            asset = position.get('asset', 'BTC')  # Default to BTC for now
            if asset == 'BTC':
                total_btc_exposure_usd += abs(position.get('size_usd', 0.0))

        # Add proposed position
        total_btc_exposure_usd += position_size.size_usd

        # Calculate as percentage of portfolio
        portfolio_value = portfolio_state.get('total_value', 0)
        if portfolio_value > 0:
            btc_exposure_percent = total_btc_exposure_usd / portfolio_value
        else:
            return True, "No portfolio value to calculate correlation"

        # Check against correlation limit (default 50%)
        max_correlated_exposure = global_limits.get('max_correlated_exposure', 0.50)

        if btc_exposure_percent > max_correlated_exposure:
            return False, f"Correlation limit exceeded: ${total_btc_exposure_usd:.2f} ({btc_exposure_percent*100:.0f}%) BTC exposure > {max_correlated_exposure*100:.0f}% limit"

        return True, f"Correlation OK ({btc_exposure_percent*100:.0f}% BTC exposure)"

    def record_trade_result(self, pnl_usd: float):
        """Record trade result for risk tracking."""
        self.daily_stats['trades_today'] += 1
        self.daily_stats['pnl_today'] += pnl_usd

        if pnl_usd < 0:
            self.daily_stats['consecutive_losses'] += 1
        else:
            self.daily_stats['consecutive_losses'] = 0

        # Persist state after every trade
        self._save_state()

    def captain_override_circuit_breaker(self, reason: str = "Captain manual override"):
        """
        Captain (human) manually overrides the circuit breaker.

        This should only be called after the Captain has:
        1. Reviewed the consecutive losses
        2. Analyzed what went wrong
        3. Made necessary adjustments (strategy params, risk limits, etc.)
        4. Decided to resume trading

        Args:
            reason: Explanation for why Captain is overriding (logged for audit)
        """
        if self.daily_stats.get('circuit_breaker_tripped', False):
            print("="*70)
            print("🚨 CAPTAIN OVERRIDE: Resetting Circuit Breaker")
            print(f"Previous trigger: {self.daily_stats.get('circuit_breaker_reason', 'Unknown')}")
            print(f"Override reason: {reason}")
            print(f"Consecutive losses reset: {self.daily_stats.get('consecutive_losses', 0)} → 0")
            print("="*70)

        # Reset circuit breaker and consecutive losses
        self.daily_stats['circuit_breaker_tripped'] = False
        self.daily_stats['circuit_breaker_reason'] = None
        self.daily_stats['consecutive_losses'] = 0

        # Log override for audit trail
        self.daily_stats['last_captain_override'] = {
            'timestamp': datetime.utcnow().isoformat(),
            'reason': reason
        }

        self._save_state()
        print("✅ Circuit breaker reset - trading may resume")

    def reset_daily_stats(self):
        """
        Reset daily statistics (call at start of each trading day).

        Note: Does NOT reset circuit breaker - Captain must explicitly override.
        """
        # Preserve circuit breaker state across day boundaries
        circuit_breaker_state = {
            'circuit_breaker_tripped': self.daily_stats.get('circuit_breaker_tripped', False),
            'circuit_breaker_reason': self.daily_stats.get('circuit_breaker_reason'),
            'last_captain_override': self.daily_stats.get('last_captain_override')
        }

        self.daily_stats = {
            "trades_today": 0,
            "pnl_today": 0.0,
            "consecutive_losses": 0,
            "max_drawdown_from_peak": 0.0,
            "date": datetime.utcnow().strftime("%Y-%m-%d")
        }

        # Restore circuit breaker state if it was tripped
        if circuit_breaker_state['circuit_breaker_tripped']:
            self.daily_stats.update(circuit_breaker_state)
            print("⚠️ Circuit breaker still active from previous day - Captain override required")

        self._save_state()

    def _get_state_file_path(self) -> 'Path':
        """Get path to today's state file."""
        from pathlib import Path
        today = datetime.utcnow().strftime("%Y-%m-%d")
        return self.state_dir / f"risk_state_{today}.json"

    def _load_state(self) -> dict:
        """Load state from file, auto-reset if new day."""
        import json

        state_file = self._get_state_file_path()
        today = datetime.utcnow().strftime("%Y-%m-%d")

        if state_file.exists():
            try:
                with open(state_file, 'r') as f:
                    state = json.load(f)

                # Check if state is from today
                if state.get('date') == today:
                    return state
                else:
                    # Old state from previous day - reset daily stats but preserve circuit breaker
                    circuit_breaker_state = {
                        'circuit_breaker_tripped': state.get('circuit_breaker_tripped', False),
                        'circuit_breaker_reason': state.get('circuit_breaker_reason'),
                        'last_captain_override': state.get('last_captain_override')
                    }

                    fresh_state = self._create_fresh_state()

                    # Restore circuit breaker state if it was tripped
                    if circuit_breaker_state['circuit_breaker_tripped']:
                        fresh_state.update(circuit_breaker_state)
                        print("⚠️ Circuit breaker still active from previous day - Captain override required")

                    return fresh_state

            except (json.JSONDecodeError, IOError):
                # Corrupted file - reset
                return self._create_fresh_state()
        else:
            # No state file - initialize fresh
            return self._create_fresh_state()

    def _save_state(self):
        """Save current state to file."""
        import json

        state_file = self._get_state_file_path()

        # Ensure date is current
        self.daily_stats['date'] = datetime.utcnow().strftime("%Y-%m-%d")

        try:
            with open(state_file, 'w') as f:
                json.dump(self.daily_stats, f, indent=2)
        except IOError as e:
            # Log error but don't crash (fail-safe)
            print(f"Warning: Could not save RiskManager state: {e}")

    def _create_fresh_state(self) -> dict:
        """Create fresh daily state."""
        return {
            "trades_today": 0,
            "pnl_today": 0.0,
            "consecutive_losses": 0,
            "max_drawdown_from_peak": 0.0,
            "peak_portfolio_value": 0.0,  # Will be set on first check
            "circuit_breaker_tripped": False,
            "circuit_breaker_reason": None,
            "last_captain_override": None,
            "date": datetime.utcnow().strftime("%Y-%m-%d")
        }
