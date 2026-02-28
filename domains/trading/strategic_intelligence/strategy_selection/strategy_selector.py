"""
Strategy Selector
Matches market context to optimal trading strategy.

Implements Skill Compression "Composition Layer":
- Pattern recognition identifies market context
- Strategy library provides available responses
- Selector composes optimal strategic response
- Outputs decision with full TRACE_FE transparency
"""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Dict, Optional
import yaml
from pathlib import Path

# Import market context (using absolute import for Docker compatibility)
from market_context.context_engine import MarketContext


@dataclass
class StrategyDecision:
    """
    Decision on which strategy to activate.

    Includes full reasoning chain for transparency (TRACE_FE).
    """
    # Decision
    action: str  # "activate", "switch", "hold", "wait"
    strategy_name: Optional[str]
    strategy_config: Optional[dict]

    # Confidence and reasoning
    confidence: float
    reasoning: Dict[str, str]  # primary, secondary, risk_assessment

    # TRACE_FE transparency
    trace_factors: List[dict]

    # Alternatives considered
    alternatives: List[dict]

    # Metadata
    timestamp: datetime
    market_context_snapshot: dict


class StrategySelector:
    """
    Select optimal strategy based on market context.

    Uses multi-factor scoring:
    1. Regime match (50% weight)
    2. Historical performance (30% weight) - from memory (Phase 2)
    3. Risk fit (20% weight)
    """

    def __init__(self, strategy_config_path: Optional[str] = None):
        """
        Initialize strategy selector.

        Args:
            strategy_config_path: Path to strategies.yaml
                                 If None, uses STRATEGY_CONFIG_PATH env var or default location
        """
        import os

        if strategy_config_path is None:
            # Try to get from environment variable first
            env_path = os.getenv('STRATEGY_CONFIG_PATH')
            if env_path:
                strategy_config_path = env_path
            else:
                # Default to config/strategies.yaml in same directory tree
                base_dir = Path(__file__).parent.parent
                strategy_config_path = base_dir / "config" / "strategies.yaml"

        self.config_path = Path(strategy_config_path)
        self.strategies = self._load_strategies()
        self.global_settings = self.strategies.get('global_settings', {})
        self.crypto_calibration = self.strategies.get('crypto_calibration', {})

        # Track active strategy for switch detection
        self.current_strategy: Optional[str] = None
        self.strategy_start_time: Optional[datetime] = None
        self.last_regime_confirmation: Optional[str] = None
        self.regime_confirmation_count: int = 0

    def select(
        self,
        market_context: MarketContext,
        portfolio_state: dict,
        constraints: dict
    ) -> StrategyDecision:
        """
        Select optimal strategy for current market conditions.

        Args:
            market_context: Current market analysis from MarketContextEngine
            portfolio_state: Current portfolio (value, positions, exposure)
            constraints: Risk constraints and limits

        Returns:
            StrategyDecision with selected strategy and full reasoning
        """
        # Check for regime stability (avoid whipsaw)
        regime_stable = self._check_regime_stability(market_context.regime)

        if not regime_stable:
            return StrategyDecision(
                action="wait",
                strategy_name=None,
                strategy_config=None,
                confidence=0.8,
                reasoning={
                    "primary": "Waiting for regime stability",
                    "secondary": f"Regime {market_context.regime} not yet confirmed",
                    "risk_assessment": "Switching strategies prematurely increases risk"
                },
                trace_factors=[{
                    "factor": "regime_instability",
                    "explanation": f"Need {self.global_settings.get('regime_confirmation_required', 2)} confirmations",
                    "confidence": 0.8
                }],
                alternatives=[],
                timestamp=datetime.utcnow(),
                market_context_snapshot=market_context.to_dict()
            )

        # Score all strategies
        scored_strategies = self._score_all_strategies(market_context, portfolio_state, constraints)

        # Check if we should switch from current strategy
        if self.current_strategy:
            should_switch, switch_reason = self._should_switch_strategy(
                scored_strategies,
                market_context
            )

            if not should_switch:
                return StrategyDecision(
                    action="hold",
                    strategy_name=self.current_strategy,
                    strategy_config=self.strategies['strategies'][self.current_strategy],
                    confidence=0.9,
                    reasoning={
                        "primary": f"Continuing {self.current_strategy}",
                        "secondary": switch_reason,
                        "risk_assessment": "Current strategy still appropriate"
                    },
                    trace_factors=[{
                        "factor": "strategy_continuity",
                        "explanation": switch_reason,
                        "confidence": 0.9
                    }],
                    alternatives=[],
                    timestamp=datetime.utcnow(),
                    market_context_snapshot=market_context.to_dict()
                )

        # Select best strategy
        if not scored_strategies:
            return StrategyDecision(
                action="wait",
                strategy_name=None,
                strategy_config=None,
                confidence=0.0,
                reasoning={
                    "primary": "No suitable strategy found",
                    "secondary": "Market conditions don't match any strategy profile",
                    "risk_assessment": "Waiting for clearer signals"
                },
                trace_factors=[{
                    "factor": "no_strategy_match",
                    "explanation": "All strategies below confidence threshold",
                    "confidence": 1.0
                }],
                alternatives=[],
                timestamp=datetime.utcnow(),
                market_context_snapshot=market_context.to_dict()
            )

        best = scored_strategies[0]

        # Check minimum confidence threshold
        strategy_config = self.strategies['strategies'][best['strategy']]
        min_confidence = strategy_config.get('min_confidence', 0.60)

        if best['confidence'] < min_confidence:
            return StrategyDecision(
                action="wait",
                strategy_name=None,
                strategy_config=None,
                confidence=best['confidence'],
                reasoning={
                    "primary": f"{best['strategy']} selected but confidence too low",
                    "secondary": f"Confidence {best['confidence']:.2f} < threshold {min_confidence:.2f}",
                    "risk_assessment": "Waiting for higher confidence signal"
                },
                trace_factors=best['trace'],
                alternatives=scored_strategies[1:3],  # Show top 2 alternatives
                timestamp=datetime.utcnow(),
                market_context_snapshot=market_context.to_dict()
            )

        # Activate or switch to best strategy
        action = "activate" if not self.current_strategy else "switch"
        self.current_strategy = best['strategy']
        self.strategy_start_time = datetime.utcnow()

        return StrategyDecision(
            action=action,
            strategy_name=best['strategy'],
            strategy_config=strategy_config,
            confidence=best['confidence'],
            reasoning=best['reasoning'],
            trace_factors=best['trace'],
            alternatives=scored_strategies[1:3],
            timestamp=datetime.utcnow(),
            market_context_snapshot=market_context.to_dict()
        )

    def _score_all_strategies(
        self,
        market_context: MarketContext,
        portfolio_state: dict,
        constraints: dict
    ) -> List[dict]:
        """
        Score all strategies and return sorted by confidence.

        Returns list of dicts with:
            - strategy: name
            - score: composite score
            - confidence: final confidence
            - reasoning: dict of reasoning
            - trace: list of TRACE_FE factors
        """
        scored = []

        for strategy_name, strategy_config in self.strategies['strategies'].items():
            # Skip risk_off unless explicitly triggered
            if strategy_name == 'risk_off':
                if not self._check_risk_off_triggers(market_context, portfolio_state):
                    continue

            score_result = self._score_strategy(
                strategy_name,
                strategy_config,
                market_context,
                portfolio_state,
                constraints
            )

            if score_result['composite_score'] > 0:
                scored.append(score_result)

        # Sort by composite score
        scored.sort(key=lambda x: x['composite_score'], reverse=True)

        return scored

    def _score_strategy(
        self,
        strategy_name: str,
        strategy_config: dict,
        market_context: MarketContext,
        portfolio_state: dict,
        constraints: dict
    ) -> dict:
        """Score individual strategy against market context."""

        # 1. Regime match (50% weight)
        regime_score, regime_factors = self._score_regime_match(
            strategy_config,
            market_context
        )

        # 2. Historical performance (30% weight)
        # TODO Phase 2: Query memory for historical performance
        # For now, use expected performance from config
        perf_score = 0.7  # Placeholder
        perf_factor = {
            "factor": "historical_performance",
            "explanation": "Using expected performance (historical data not yet available)",
            "confidence": 0.5
        }

        # 3. Risk fit (20% weight)
        risk_score, risk_factor = self._score_risk_fit(
            strategy_config,
            portfolio_state,
            constraints
        )

        # Composite score
        composite_score = (
            0.5 * regime_score +
            0.3 * perf_score +
            0.2 * risk_score
        )

        # Calculate confidence (based on factor agreement)
        confidence = self._calculate_confidence(regime_score, perf_score, risk_score)

        # Build reasoning
        reasoning = {
            "primary": f"{strategy_name}: {self._get_primary_reason(strategy_config, market_context)}",
            "secondary": self._get_secondary_reason(perf_score, risk_score),
            "risk_assessment": risk_factor['explanation']
        }

        # Build TRACE_FE
        trace = regime_factors + [perf_factor, risk_factor]

        return {
            "strategy": strategy_name,
            "composite_score": composite_score,
            "confidence": confidence,
            "reasoning": reasoning,
            "trace": trace
        }

    def _score_regime_match(self, strategy_config: dict, market_context: MarketContext) -> tuple:
        """Score how well current regime matches strategy profile."""
        best_regimes = strategy_config.get('best_regimes', [])
        avoid_regimes = strategy_config.get('avoid_regimes', [])
        trigger_regimes = strategy_config.get('trigger_regimes', [])

        current_regime = market_context.regime

        # Check avoid list first (disqualifying)
        if current_regime in avoid_regimes:
            return 0.0, [{
                "factor": "regime_mismatch",
                "explanation": f"Current regime ({current_regime}) in avoid list",
                "confidence": 0.9
            }]

        # Check best regimes
        if current_regime in best_regimes:
            score = 0.9 * market_context.regime_confidence
            return score, [{
                "factor": "regime_match",
                "explanation": f"Current regime ({current_regime}) matches strategy profile",
                "confidence": market_context.regime_confidence
            }]

        # Check trigger regimes (for risk_off, etc.)
        if trigger_regimes and current_regime in trigger_regimes:
            return 0.95, [{
                "factor": "regime_trigger",
                "explanation": f"Regime ({current_regime}) triggers strategy activation",
                "confidence": 0.95
            }]

        # No match
        return 0.2, [{
            "factor": "weak_regime_match",
            "explanation": f"Regime ({current_regime}) not optimal for strategy",
            "confidence": 0.6
        }]

    def _score_risk_fit(self, strategy_config: dict, portfolio_state: dict, constraints: dict) -> tuple:
        """Score how well strategy fits risk constraints."""
        risk_config = strategy_config.get('risk', {})

        portfolio_value = portfolio_state.get('total_value', 0)
        current_exposure = portfolio_state.get('exposure', 0)

        # Check position size limits
        max_position = risk_config.get('max_position_size', 0.3)
        max_position_usd = portfolio_value * max_position

        # Check if we have room for this strategy
        available_capital = portfolio_value - current_exposure

        if available_capital < max_position_usd * 0.5:
            return 0.3, {
                "factor": "capital_constrained",
                "explanation": f"Limited capital available ({available_capital:.2f} of {max_position_usd:.2f} needed)",
                "confidence": 0.8
            }

        # Check against global risk limits
        global_max_risk = self.global_settings.get('global_risk_limits', {}).get('max_portfolio_risk', 0.10)
        strategy_risk = risk_config.get('stop_loss', 0.03)

        if strategy_risk > global_max_risk:
            return 0.5, {
                "factor": "excessive_risk",
                "explanation": f"Strategy risk ({strategy_risk*100:.1f}%) exceeds limit ({global_max_risk*100:.1f}%)",
                "confidence": 0.9
            }

        # Good fit
        return 0.9, {
            "factor": "risk_compatible",
            "explanation": f"Strategy fits within risk budget ({strategy_risk*100:.1f}% risk)",
            "confidence": 0.85
        }

    def _calculate_confidence(self, regime_score: float, perf_score: float, risk_score: float) -> float:
        """Calculate confidence based on score agreement."""
        scores = [regime_score, perf_score, risk_score]
        avg_score = sum(scores) / len(scores)
        std_score = (sum([(s - avg_score) ** 2 for s in scores]) / len(scores)) ** 0.5

        # High agreement = high confidence
        confidence = avg_score * (1.0 - min(std_score, 0.5))
        return min(max(confidence, 0.0), 1.0)

    def _get_primary_reason(self, strategy_config: dict, market_context: MarketContext) -> str:
        """Generate primary reasoning string."""
        return f"Regime ({market_context.regime}) matches {strategy_config['name']} profile"

    def _get_secondary_reason(self, perf_score: float, risk_score: float) -> str:
        """Generate secondary reasoning string."""
        if perf_score > 0.7 and risk_score > 0.7:
            return "Strong historical performance and good risk fit"
        elif perf_score > 0.7:
            return "Strong historical performance"
        elif risk_score > 0.7:
            return "Good risk-reward profile"
        else:
            return "Moderate historical performance and risk fit"

    def _check_regime_stability(self, current_regime: str) -> bool:
        """Check if regime is stable enough to act on."""
        required_confirmations = self.global_settings.get('regime_confirmation_required', 2)

        if current_regime == self.last_regime_confirmation:
            self.regime_confirmation_count += 1
        else:
            self.last_regime_confirmation = current_regime
            self.regime_confirmation_count = 1

        return self.regime_confirmation_count >= required_confirmations

    def _should_switch_strategy(self, scored_strategies: List[dict], market_context: MarketContext) -> tuple:
        """
        Determine if we should switch from current strategy.

        Returns: (should_switch: bool, reason: str)
        """
        if not self.current_strategy or not scored_strategies:
            return True, "No current strategy"

        # Find current strategy in scores
        current_score = None
        best_alternative = scored_strategies[0]

        for s in scored_strategies:
            if s['strategy'] == self.current_strategy:
                current_score = s
                break

        if not current_score:
            return True, "Current strategy no longer viable"

        # Check cooldown period
        if self.strategy_start_time:
            cooldown_periods = self.global_settings.get('strategy_switch_cooldown', 2)

            # Get timeframe from crypto_calibration (default to 4H confirmation timeframe)
            timeframe_config = self.crypto_calibration.get('timeframes', {})
            confirmation_tf = timeframe_config.get('confirmation', '4H')

            # Parse timeframe to hours (4H → 4 hours, 1H → 1 hour, etc.)
            if confirmation_tf.endswith('H'):
                hours_per_period = int(confirmation_tf[:-1])
            elif confirmation_tf.endswith('D'):
                hours_per_period = int(confirmation_tf[:-1]) * 24
            else:
                hours_per_period = 4  # Default to 4 hours

            # Calculate cooldown duration
            from datetime import timedelta
            cooldown_duration = timedelta(hours=cooldown_periods * hours_per_period)
            time_since_start = datetime.utcnow() - self.strategy_start_time

            if time_since_start < cooldown_duration:
                hours_remaining = (cooldown_duration - time_since_start).total_seconds() / 3600
                return False, f"Cooldown active: {hours_remaining:.1f}h remaining (need {cooldown_periods} periods @ {confirmation_tf})"

        # Switch if alternative is significantly better
        score_diff = best_alternative['composite_score'] - current_score['composite_score']

        if score_diff > 0.3:  # 30% better score
            return True, f"{best_alternative['strategy']} significantly outperforms current"

        return False, "Current strategy still optimal"

    def _check_risk_off_triggers(self, market_context: MarketContext, portfolio_state: dict) -> bool:
        """Check if risk-off conditions are triggered."""
        # TODO Phase 2: Implement comprehensive risk-off triggers
        # For now, check basic conditions

        # Extreme volatility
        if market_context.volatility_regime == "explosive":
            return True

        # Crash recovery regime
        if market_context.regime == "crash_recovery":
            return True

        return False

    def _load_strategies(self) -> dict:
        """Load strategy configuration from YAML."""
        try:
            with open(self.config_path, 'r') as f:
                config = yaml.safe_load(f)
            return config
        except FileNotFoundError:
            raise FileNotFoundError(f"Strategy config not found: {self.config_path}")
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML in strategy config: {e}")
