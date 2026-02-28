"""
Qdrant Memory Schema for Strategic Intelligence Layer
Stores trade outcomes, strategy performance, and decision history.

This enables the Learning Engine to:
- Track actual vs expected performance by strategy
- Learn which strategies work in which market regimes
- Adapt parameters based on historical results
- Build confidence calibration (predicted vs actual win rate)
"""

from dataclasses import dataclass, asdict
from datetime import datetime
from typing import List, Dict, Optional
from enum import Enum


class OutcomeType(Enum):
    """Trade outcome classification."""
    WIN = "win"
    LOSS = "loss"
    BREAKEVEN = "breakeven"
    STOPPED_OUT = "stopped_out"
    TIME_STOPPED = "time_stopped"
    MANUAL_EXIT = "manual_exit"


@dataclass
class TradeOutcome:
    """
    Complete record of a trade from entry to exit.
    This is what gets stored in Qdrant for learning.
    """
    # Identifiers
    trade_id: str
    session_id: str
    timestamp_entry: datetime
    timestamp_exit: datetime

    # Strategy & Market Context
    strategy_name: str
    market_regime: str
    regime_confidence: float
    volatility_regime: str
    sentiment_direction: str

    # Entry Conditions
    entry_price: float
    position_size_usd: float
    position_size_btc: float
    entry_confidence: float  # SIL confidence at entry

    # Risk Parameters
    stop_loss_price: float
    profit_target_price: float
    expected_win_rate: float  # From strategy config
    expected_rr_ratio: float

    # Exit Conditions
    exit_price: float
    exit_reason: OutcomeType

    # Performance Metrics
    pnl_usd: float
    pnl_percent: float
    hold_time_hours: float
    actual_rr_ratio: float  # Actual R:R achieved

    # Market Conditions During Trade
    max_favorable_excursion: float  # How far in profit did it go?
    max_adverse_excursion: float    # How far against us?
    avg_volatility_during_trade: float

    # TRACE Factors (for learning what factors correlate with success)
    trace_factors: List[dict]

    # Portfolio Context
    portfolio_value_at_entry: float
    portfolio_value_at_exit: float

    # Metadata
    tags: List[str]  # ["paper_trading", "live", "backtest"]
    notes: Optional[str] = None

    def __post_init__(self):
        """
        Validate TradeOutcome fields to ensure data integrity.

        Raises:
            ValueError: If any field contains invalid data
        """
        # Validate timestamps
        if self.timestamp_exit < self.timestamp_entry:
            raise ValueError(
                f"Exit timestamp ({self.timestamp_exit}) must be after entry timestamp ({self.timestamp_entry})"
            )

        # Validate hold time
        if self.hold_time_hours < 0:
            raise ValueError(f"Hold time cannot be negative: {self.hold_time_hours}")

        # Validate confidence values (0 to 1)
        if not 0 <= self.regime_confidence <= 1:
            raise ValueError(f"Regime confidence must be 0-1: {self.regime_confidence}")
        if not 0 <= self.entry_confidence <= 1:
            raise ValueError(f"Entry confidence must be 0-1: {self.entry_confidence}")
        if not 0 <= self.expected_win_rate <= 1:
            raise ValueError(f"Expected win rate must be 0-1: {self.expected_win_rate}")

        # Validate position sizes (must be positive)
        if self.position_size_usd <= 0:
            raise ValueError(f"Position size USD must be positive: {self.position_size_usd}")
        if self.position_size_btc <= 0:
            raise ValueError(f"Position size BTC must be positive: {self.position_size_btc}")

        # Validate prices (must be positive)
        if self.entry_price <= 0:
            raise ValueError(f"Entry price must be positive: {self.entry_price}")
        if self.exit_price <= 0:
            raise ValueError(f"Exit price must be positive: {self.exit_price}")
        if self.stop_loss_price <= 0:
            raise ValueError(f"Stop loss price must be positive: {self.stop_loss_price}")
        if self.profit_target_price <= 0:
            raise ValueError(f"Profit target price must be positive: {self.profit_target_price}")

        # Validate R:R ratios (cannot be negative)
        if self.expected_rr_ratio < 0:
            raise ValueError(f"Expected R:R ratio cannot be negative: {self.expected_rr_ratio}")
        if self.actual_rr_ratio < 0:
            raise ValueError(f"Actual R:R ratio cannot be negative: {self.actual_rr_ratio}")

        # Validate portfolio values (must be positive)
        if self.portfolio_value_at_entry <= 0:
            raise ValueError(f"Portfolio value at entry must be positive: {self.portfolio_value_at_entry}")
        if self.portfolio_value_at_exit <= 0:
            raise ValueError(f"Portfolio value at exit must be positive: {self.portfolio_value_at_exit}")

        # Validate volatility (cannot be negative)
        if self.avg_volatility_during_trade < 0:
            raise ValueError(f"Average volatility cannot be negative: {self.avg_volatility_during_trade}")

        # Validate excursions (MFE should be positive for wins, MAE should be negative)
        # Note: We don't enforce this strictly as edge cases exist
        if abs(self.max_favorable_excursion) > 1.0:  # More than 100% move seems suspicious
            print(f"Warning: Unusual max favorable excursion: {self.max_favorable_excursion:.1%}")
        if abs(self.max_adverse_excursion) > 1.0:  # More than 100% move seems suspicious
            print(f"Warning: Unusual max adverse excursion: {self.max_adverse_excursion:.1%}")

        # Validate trace_factors structure
        if not isinstance(self.trace_factors, list):
            raise ValueError("trace_factors must be a list")

        # Validate tags
        if not isinstance(self.tags, list):
            raise ValueError("tags must be a list")
        if not self.tags:
            raise ValueError("tags cannot be empty - must include at least one tag (e.g., 'paper_trading')")


@dataclass
class StrategyPerformanceSnapshot:
    """
    Aggregated performance metrics for a strategy in a specific regime.
    Used for fast lookups without scanning all trades.
    """
    strategy_name: str
    regime: str

    # Time window
    start_date: datetime
    end_date: datetime

    # Performance metrics
    total_trades: int
    winning_trades: int
    losing_trades: int
    breakeven_trades: int

    win_rate: float
    avg_win_pnl_percent: float
    avg_loss_pnl_percent: float
    avg_rr_ratio: float

    # Confidence calibration
    avg_predicted_win_rate: float  # What SIL expected
    actual_win_rate: float          # What actually happened
    calibration_error: float        # Difference

    # Robustness
    sharpe_ratio: float
    max_drawdown: float
    consecutive_losses_max: int

    # Update metadata
    last_updated: datetime
    sample_size_confidence: float  # How confident are we in these stats?


class QdrantCollections:
    """
    Qdrant collection names and configurations.
    """

    TRADE_OUTCOMES = "sil_trade_outcomes"
    STRATEGY_PERFORMANCE = "sil_strategy_performance"
    DECISION_LOG = "sil_decision_log"  # All decisions, including non-trades

    @staticmethod
    def get_trade_outcome_schema() -> dict:
        """
        Schema for trade_outcomes collection.

        Qdrant vector: Embedding of market conditions at entry
        (regime, volatility, sentiment, price action features)

        This enables similarity search: "Find trades similar to current market"
        """
        return {
            "collection_name": QdrantCollections.TRADE_OUTCOMES,
            "vector_size": 128,  # Embedding dimension
            "distance": "Cosine",
            "payload_schema": {
                "trade_id": "keyword",
                "session_id": "keyword",
                "strategy_name": "keyword",
                "market_regime": "keyword",
                "exit_reason": "keyword",
                "timestamp_entry": "datetime",
                "timestamp_exit": "datetime",
                "pnl_usd": "float",
                "pnl_percent": "float",
                "win_rate_predicted": "float",
                "confidence": "float",
                "tags": "keyword[]"
            },
            "indexes": [
                "strategy_name",
                "market_regime",
                "timestamp_entry"
            ]
        }

    @staticmethod
    def get_strategy_performance_schema() -> dict:
        """
        Schema for strategy_performance collection.

        Aggregated metrics for fast lookups.
        Updated periodically (daily or after N trades).
        """
        return {
            "collection_name": QdrantCollections.STRATEGY_PERFORMANCE,
            "vector_size": 64,  # Smaller embedding for regime characteristics
            "distance": "Cosine",
            "payload_schema": {
                "strategy_name": "keyword",
                "regime": "keyword",
                "total_trades": "integer",
                "win_rate": "float",
                "avg_rr_ratio": "float",
                "sharpe_ratio": "float",
                "last_updated": "datetime",
                "sample_size_confidence": "float"
            },
            "indexes": [
                "strategy_name",
                "regime"
            ]
        }

    @staticmethod
    def get_decision_log_schema() -> dict:
        """
        Schema for decision_log collection.

        Logs ALL SIL decisions (even "wait" decisions).
        Enables analysis of what we DIDN'T trade and why.
        """
        return {
            "collection_name": QdrantCollections.DECISION_LOG,
            "vector_size": 128,
            "distance": "Cosine",
            "payload_schema": {
                "decision_id": "keyword",
                "session_id": "keyword",
                "timestamp": "datetime",
                "action": "keyword",  # "enter_long", "wait", etc.
                "strategy_name": "keyword",
                "confidence": "float",
                "market_regime": "keyword",
                "reasoning": "text",
                "risk_check_passed": "boolean"
            },
            "indexes": [
                "action",
                "timestamp"
            ]
        }


def trade_outcome_to_dict(outcome: TradeOutcome) -> dict:
    """
    Convert TradeOutcome to dict for Qdrant storage.

    Handles datetime serialization and enum conversion.
    """
    data = asdict(outcome)

    # Convert datetime to ISO string
    data['timestamp_entry'] = outcome.timestamp_entry.isoformat()
    data['timestamp_exit'] = outcome.timestamp_exit.isoformat()

    # Convert enum
    data['exit_reason'] = outcome.exit_reason.value

    return data


def dict_to_trade_outcome(data: dict) -> TradeOutcome:
    """
    Convert dict from Qdrant back to TradeOutcome object.

    Raises:
        ValueError: If datetime strings are malformed
    """
    # Convert ISO string back to datetime with error handling
    try:
        data['timestamp_entry'] = datetime.fromisoformat(data['timestamp_entry'])
    except (ValueError, TypeError) as e:
        raise ValueError(f"Invalid timestamp_entry format: {data.get('timestamp_entry')}") from e

    try:
        data['timestamp_exit'] = datetime.fromisoformat(data['timestamp_exit'])
    except (ValueError, TypeError) as e:
        raise ValueError(f"Invalid timestamp_exit format: {data.get('timestamp_exit')}") from e

    # Convert string back to enum
    try:
        data['exit_reason'] = OutcomeType(data['exit_reason'])
    except (ValueError, KeyError) as e:
        raise ValueError(f"Invalid exit_reason: {data.get('exit_reason')}") from e

    return TradeOutcome(**data)


# Example usage and queries
EXAMPLE_QUERIES = """
# Query 1: Get performance of mean_reversion in ranging_low_vol
collection.search(
    vector=encode_market_conditions(regime='ranging_low_vol'),
    filter={
        'must': [
            {'key': 'strategy_name', 'match': {'value': 'mean_reversion'}},
            {'key': 'market_regime', 'match': {'value': 'ranging_low_vol'}}
        ]
    },
    limit=50
)

# Query 2: Find similar trades to current market conditions
collection.search(
    vector=encode_current_market(),
    filter={
        'must': [
            {'key': 'strategy_name', 'match': {'value': 'trend_following'}}
        ]
    },
    limit=10
)
# Returns: 10 most similar past trades → calculate actual win rate

# Query 3: Get recent performance trend
collection.scroll(
    filter={
        'must': [
            {'key': 'strategy_name', 'match': {'value': 'mean_reversion'}},
            {
                'key': 'timestamp_entry',
                'range': {
                    'gte': (datetime.now() - timedelta(days=30)).isoformat()
                }
            }
        ]
    }
)
# Returns: All mean_reversion trades in last 30 days → track performance drift
"""
