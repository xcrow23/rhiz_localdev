"""
Learning Engine - Adaptive Strategy Optimization

Tracks actual vs expected performance and adapts strategy parameters over time.

Core Capabilities:
1. Performance Tracking: Win rate, R:R ratio, Sharpe by strategy-regime
2. Confidence Calibration: Compare predicted vs actual outcomes
3. Parameter Adaptation: Suggest threshold adjustments based on results
4. Regime Detection Validation: Track regime prediction accuracy
"""

from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
import numpy as np

try:
    from memory import (
        QdrantMemoryClient, TradeOutcome, StrategyPerformanceSnapshot,
        encode_regime_characteristics
    )
    MEMORY_AVAILABLE = True
except ImportError:
    MEMORY_AVAILABLE = False
    # Define stub classes for type hints
    TradeOutcome = dict
    StrategyPerformanceSnapshot = dict
    print("Warning: Memory module not available")


@dataclass
class PerformanceMetrics:
    """
    Aggregated performance metrics for a strategy-regime combination.
    """
    strategy_name: str
    regime: str
    time_window_days: int

    # Trade statistics
    total_trades: int
    winning_trades: int
    losing_trades: int
    breakeven_trades: int

    # Performance
    win_rate: float
    avg_win_percent: float
    avg_loss_percent: float
    avg_rr_ratio: float

    # Confidence calibration
    avg_predicted_win_rate: float
    calibration_error: float  # abs(predicted - actual)

    # Risk metrics
    sharpe_ratio: float
    max_drawdown: float
    consecutive_losses_max: int

    # Sample size confidence
    sample_size_confidence: float  # How confident are we in these stats?

    # Timestamp
    calculated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ParameterSuggestion:
    """
    Suggestion to adapt strategy parameters based on learning.
    """
    strategy_name: str
    parameter_name: str
    current_value: float
    suggested_value: float
    rationale: str
    confidence: float
    evidence: List[str]  # Supporting evidence from data


class LearningEngine:
    """
    Continuously learns from trade outcomes to improve strategy performance.

    Philosophy:
    - Trust the data, not the assumptions
    - Small incremental adjustments over time
    - Require statistical significance before adapting
    - Track confidence calibration to prevent overconfidence
    """

    def __init__(
        self,
        memory_client: Optional['QdrantMemoryClient'] = None,
        min_trades_for_learning: int = 10,
        confidence_threshold: float = 0.70
    ):
        """
        Initialize Learning Engine.

        Args:
            memory_client: QdrantMemoryClient instance (optional)
            min_trades_for_learning: Minimum trades before suggesting adaptations
            confidence_threshold: Minimum confidence for parameter changes
        """
        if not MEMORY_AVAILABLE:
            raise ImportError("Memory module required for Learning Engine")

        self.memory = memory_client
        self.min_trades = min_trades_for_learning
        self.confidence_threshold = confidence_threshold

        # Learning state
        self.last_update_time: Optional[datetime] = None
        self.performance_cache: Dict[str, PerformanceMetrics] = {}

    # ========================================
    # Performance Analysis
    # ========================================

    def analyze_strategy_performance(
        self,
        strategy_name: str,
        regime: str,
        days_back: int = 30
    ) -> PerformanceMetrics:
        """
        Analyze strategy performance in specific regime.

        Args:
            strategy_name: Strategy to analyze
            regime: Regime to analyze
            days_back: Time window (default 30 days)

        Returns:
            PerformanceMetrics object
        """
        if not self.memory:
            raise ValueError("Memory client not initialized")

        # Get all trades for this strategy-regime combination
        trades = self.memory.get_trades_by_strategy_and_regime(
            strategy_name,
            regime,
            days_back
        )

        if not trades:
            # No trades yet - return zero metrics
            return PerformanceMetrics(
                strategy_name=strategy_name,
                regime=regime,
                time_window_days=days_back,
                total_trades=0,
                winning_trades=0,
                losing_trades=0,
                breakeven_trades=0,
                win_rate=0.0,
                avg_win_percent=0.0,
                avg_loss_percent=0.0,
                avg_rr_ratio=0.0,
                avg_predicted_win_rate=0.0,
                calibration_error=0.0,
                sharpe_ratio=0.0,
                max_drawdown=0.0,
                consecutive_losses_max=0,
                sample_size_confidence=0.0
            )

        # Count outcomes
        wins = [t for t in trades if t.exit_reason.value == 'win']
        losses = [t for t in trades if t.exit_reason.value == 'loss']
        breakevens = [t for t in trades if t.exit_reason.value == 'breakeven']

        total = len(trades)
        win_count = len(wins)
        loss_count = len(losses)
        breakeven_count = len(breakevens)

        # Calculate win rate
        win_rate = win_count / total if total > 0 else 0.0

        # Average win/loss
        avg_win = sum(t.pnl_percent for t in wins) / win_count if wins else 0.0
        avg_loss = sum(abs(t.pnl_percent) for t in losses) / loss_count if losses else 0.0

        # Average R:R
        avg_rr = sum(t.actual_rr_ratio for t in trades) / total

        # Confidence calibration
        avg_predicted = sum(t.expected_win_rate for t in trades) / total
        calibration_error = abs(avg_predicted - win_rate)

        # Risk metrics
        sharpe = self._calculate_sharpe_ratio(trades)
        max_dd = self._calculate_max_drawdown(trades)
        max_consec_losses = self._calculate_max_consecutive_losses(trades)

        # Sample size confidence (how confident are we in these stats?)
        sample_confidence = self._calculate_sample_confidence(total)

        metrics = PerformanceMetrics(
            strategy_name=strategy_name,
            regime=regime,
            time_window_days=days_back,
            total_trades=total,
            winning_trades=win_count,
            losing_trades=loss_count,
            breakeven_trades=breakeven_count,
            win_rate=win_rate,
            avg_win_percent=avg_win,
            avg_loss_percent=avg_loss,
            avg_rr_ratio=avg_rr,
            avg_predicted_win_rate=avg_predicted,
            calibration_error=calibration_error,
            sharpe_ratio=sharpe,
            max_drawdown=max_dd,
            consecutive_losses_max=max_consec_losses,
            sample_size_confidence=sample_confidence
        )

        # Cache for future use
        cache_key = f"{strategy_name}_{regime}_{days_back}"
        self.performance_cache[cache_key] = metrics

        return metrics

    def get_all_strategy_performance(
        self,
        days_back: int = 30
    ) -> Dict[str, Dict[str, PerformanceMetrics]]:
        """
        Get performance for all strategy-regime combinations.

        Returns:
            Nested dict: {strategy_name: {regime: PerformanceMetrics}}
        """
        if not self.memory:
            raise ValueError("Memory client not initialized")

        # Get unique strategy-regime combinations from recent trades
        stats_dict = self.memory.get_strategy_stats_by_regime("mean_reversion", days_back)

        # TODO: Get this dynamically from config
        strategies = ["mean_reversion", "trend_following", "breakout_capture",
                      "accumulation_dca", "risk_off"]
        regimes = ["trending_bull", "trending_bear", "ranging_low_vol",
                   "ranging_high_vol", "breakout_pending", "crash_recovery"]

        results = {}

        for strategy in strategies:
            results[strategy] = {}
            for regime in regimes:
                metrics = self.analyze_strategy_performance(strategy, regime, days_back)
                if metrics.total_trades > 0:
                    results[strategy][regime] = metrics

        return results

    # ========================================
    # Parameter Adaptation
    # ========================================

    def suggest_parameter_adaptations(
        self,
        strategy_name: str,
        regime: str,
        days_back: int = 30
    ) -> List[ParameterSuggestion]:
        """
        Suggest parameter adaptations based on performance.

        Returns adaptations with high confidence when:
        1. Sufficient trade sample (>= min_trades)
        2. Clear performance pattern
        3. Statistical significance

        Args:
            strategy_name: Strategy to analyze
            regime: Regime to analyze
            days_back: Time window

        Returns:
            List of ParameterSuggestion objects
        """
        suggestions = []

        # Get performance metrics
        metrics = self.analyze_strategy_performance(strategy_name, regime, days_back)

        # Need minimum trades
        if metrics.total_trades < self.min_trades:
            return []

        # 1. Confidence Calibration Adjustment
        if metrics.calibration_error > 0.15:  # >15% miscalibration
            # Strategy is overconfident or underconfident
            if metrics.avg_predicted_win_rate > metrics.win_rate:
                # Overconfident - reduce confidence threshold
                suggestions.append(ParameterSuggestion(
                    strategy_name=strategy_name,
                    parameter_name="min_confidence",
                    current_value=0.65,  # TODO: Get from config
                    suggested_value=0.70,  # Increase threshold
                    rationale=f"Strategy overconfident: predicted {metrics.avg_predicted_win_rate:.1%} but actual {metrics.win_rate:.1%}",
                    confidence=min(metrics.sample_size_confidence, 0.85),
                    evidence=[
                        f"Calibration error: {metrics.calibration_error:.1%}",
                        f"Sample size: {metrics.total_trades} trades"
                    ]
                ))
            else:
                # Underconfident - could be more aggressive
                suggestions.append(ParameterSuggestion(
                    strategy_name=strategy_name,
                    parameter_name="min_confidence",
                    current_value=0.65,
                    suggested_value=0.60,
                    rationale=f"Strategy underconfident: predicted {metrics.avg_predicted_win_rate:.1%} but actual {metrics.win_rate:.1%}",
                    confidence=min(metrics.sample_size_confidence, 0.80),
                    evidence=[
                        f"Calibration error: {metrics.calibration_error:.1%}",
                        f"Sample size: {metrics.total_trades} trades"
                    ]
                ))

        # 2. Stop Loss Adjustment
        if metrics.avg_loss_percent > 0.04:  # Losses averaging >4%
            # Stop loss too wide, getting stopped out with larger losses
            suggestions.append(ParameterSuggestion(
                strategy_name=strategy_name,
                parameter_name="stop_loss",
                current_value=0.03,  # TODO: Get from config
                suggested_value=0.025,  # Tighter stop
                rationale=f"Average loss {metrics.avg_loss_percent:.1%} exceeds stop loss expectation",
                confidence=min(metrics.sample_size_confidence, 0.75),
                evidence=[
                    f"Avg loss: {metrics.avg_loss_percent:.1%} (expected ~3%)",
                    f"Loss trades: {metrics.losing_trades}/{metrics.total_trades}"
                ]
            ))

        # 3. Profit Target Adjustment
        if metrics.avg_win_percent < 0.04 and metrics.win_rate > 0.55:
            # High win rate but small wins - could let winners run more
            suggestions.append(ParameterSuggestion(
                strategy_name=strategy_name,
                parameter_name="profit_target",
                current_value=0.05,
                suggested_value=0.06,
                rationale=f"High win rate ({metrics.win_rate:.1%}) but small wins ({metrics.avg_win_percent:.1%}) - consider wider target",
                confidence=min(metrics.sample_size_confidence, 0.70),
                evidence=[
                    f"Win rate: {metrics.win_rate:.1%}",
                    f"Avg win: {metrics.avg_win_percent:.1%}"
                ]
            ))

        # 4. Position Size Adjustment (based on Sharpe)
        if metrics.sharpe_ratio < 0.5 and metrics.total_trades >= 20:
            # Poor risk-adjusted returns
            suggestions.append(ParameterSuggestion(
                strategy_name=strategy_name,
                parameter_name="max_position_size",
                current_value=0.25,
                suggested_value=0.20,
                rationale=f"Low Sharpe ratio ({metrics.sharpe_ratio:.2f}) suggests reducing position size",
                confidence=min(metrics.sample_size_confidence, 0.80),
                evidence=[
                    f"Sharpe ratio: {metrics.sharpe_ratio:.2f}",
                    f"Max drawdown: {metrics.max_drawdown:.1%}"
                ]
            ))

        # Filter to high-confidence suggestions only
        high_confidence = [
            s for s in suggestions
            if s.confidence >= self.confidence_threshold
        ]

        return high_confidence

    # ========================================
    # Regime Validation
    # ========================================

    def validate_regime_predictions(
        self,
        days_back: int = 30
    ) -> Dict[str, float]:
        """
        Validate regime detection accuracy.

        Checks: Did strategies perform as expected in detected regimes?

        Returns:
            Dict mapping regime -> accuracy score (0-1)
        """
        if not self.memory:
            raise ValueError("Memory client not initialized")

        regime_scores = {}

        regimes = ["trending_bull", "trending_bear", "ranging_low_vol",
                   "ranging_high_vol", "breakout_pending", "crash_recovery"]

        for regime in regimes:
            # Check if mean_reversion performed well in ranging regimes
            if regime in ["ranging_low_vol", "ranging_high_vol"]:
                metrics = self.analyze_strategy_performance("mean_reversion", regime, days_back)
                if metrics.total_trades >= 5:
                    # Mean reversion should have >50% win rate in ranging
                    regime_scores[regime] = 1.0 if metrics.win_rate >= 0.50 else metrics.win_rate / 0.50

            # Check if trend_following performed well in trending regimes
            elif regime in ["trending_bull", "trending_bear"]:
                metrics = self.analyze_strategy_performance("trend_following", regime, days_back)
                if metrics.total_trades >= 5:
                    # Trend following should have >45% win rate with good R:R
                    regime_scores[regime] = 1.0 if metrics.win_rate >= 0.45 else metrics.win_rate / 0.45

        return regime_scores

    # ========================================
    # Snapshot Updates
    # ========================================

    def update_performance_snapshots(self, days_back: int = 30):
        """
        Update strategy performance snapshots in Qdrant.

        This aggregates recent trades into StrategyPerformanceSnapshot
        objects for fast lookup.

        Args:
            days_back: Time window to aggregate
        """
        if not self.memory:
            raise ValueError("Memory client not initialized")

        strategies = ["mean_reversion", "trend_following", "breakout_capture",
                      "accumulation_dca", "risk_off"]
        regimes = ["trending_bull", "trending_bear", "ranging_low_vol",
                   "ranging_high_vol", "breakout_pending", "crash_recovery"]

        for strategy in strategies:
            for regime in regimes:
                metrics = self.analyze_strategy_performance(strategy, regime, days_back)

                if metrics.total_trades > 0:
                    # Create snapshot
                    snapshot = StrategyPerformanceSnapshot(
                        strategy_name=strategy,
                        regime=regime,
                        start_date=datetime.utcnow() - timedelta(days=days_back),
                        end_date=datetime.utcnow(),
                        total_trades=metrics.total_trades,
                        winning_trades=metrics.winning_trades,
                        losing_trades=metrics.losing_trades,
                        breakeven_trades=metrics.breakeven_trades,
                        win_rate=metrics.win_rate,
                        avg_win_pnl_percent=metrics.avg_win_percent,
                        avg_loss_pnl_percent=metrics.avg_loss_percent,
                        avg_rr_ratio=metrics.avg_rr_ratio,
                        avg_predicted_win_rate=metrics.avg_predicted_win_rate,
                        actual_win_rate=metrics.win_rate,
                        calibration_error=metrics.calibration_error,
                        sharpe_ratio=metrics.sharpe_ratio,
                        max_drawdown=metrics.max_drawdown,
                        consecutive_losses_max=metrics.consecutive_losses_max,
                        last_updated=datetime.utcnow(),
                        sample_size_confidence=metrics.sample_size_confidence
                    )

                    # Encode regime for embedding
                    embedding = encode_regime_characteristics(regime)

                    # Store in Qdrant
                    self.memory.store_strategy_performance(snapshot, embedding)

        self.last_update_time = datetime.utcnow()
        print(f"Updated performance snapshots at {self.last_update_time}")

    # ========================================
    # Helper Methods
    # ========================================

    def _calculate_sharpe_ratio(self, trades: List[TradeOutcome]) -> float:
        """Calculate Sharpe ratio from trade results."""
        if not trades:
            return 0.0

        returns = [t.pnl_percent for t in trades]

        # Guard against empty returns list
        if not returns or len(returns) == 0:
            return 0.0

        avg_return = sum(returns) / len(returns)
        std_return = np.std(returns) if len(returns) > 1 else 0.0

        # Guard against zero standard deviation
        if std_return == 0:
            return 0.0

        # Annualized Sharpe (assuming ~250 trading days/year)
        sharpe = (avg_return / std_return) * np.sqrt(250)
        return sharpe

    def _calculate_max_drawdown(self, trades: List[TradeOutcome]) -> float:
        """Calculate maximum drawdown from trade sequence."""
        if not trades:
            return 0.0

        # Sort by exit time
        sorted_trades = sorted(trades, key=lambda t: t.timestamp_exit)

        # Calculate cumulative P&L
        cumulative = 0.0
        peak = 0.0
        max_dd = 0.0

        for trade in sorted_trades:
            cumulative += trade.pnl_percent
            peak = max(peak, cumulative)
            drawdown = peak - cumulative
            max_dd = max(max_dd, drawdown)

        return max_dd

    def _calculate_max_consecutive_losses(self, trades: List[TradeOutcome]) -> int:
        """Calculate maximum consecutive losing trades."""
        if not trades:
            return 0

        sorted_trades = sorted(trades, key=lambda t: t.timestamp_exit)

        max_streak = 0
        current_streak = 0

        for trade in sorted_trades:
            if trade.exit_reason.value in ['loss', 'stopped_out']:
                current_streak += 1
                max_streak = max(max_streak, current_streak)
            else:
                current_streak = 0

        return max_streak

    def _calculate_sample_confidence(self, n_trades: int) -> float:
        """
        Calculate confidence in statistics based on sample size.

        Uses diminishing returns curve:
        - 10 trades = 50% confidence
        - 20 trades = 70% confidence
        - 50 trades = 90% confidence
        - 100 trades = 95% confidence
        """
        if n_trades == 0:
            return 0.0

        # Logarithmic confidence curve
        confidence = min(1.0, 0.5 + 0.45 * np.log10(n_trades))
        return confidence
