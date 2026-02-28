"""
Unit Tests for TradeOutcome Validation (HIGH-2)

Tests the comprehensive input validation added in Sprint 2 to prevent
corrupt data from entering the memory system.
"""

import pytest
from datetime import datetime, timedelta
from memory.qdrant_schema import TradeOutcome, OutcomeType


class TestTradeOutcomeValidation:
    """Test TradeOutcome __post_init__ validation."""

    def test_valid_trade_outcome(self):
        """Test that valid TradeOutcome is accepted."""
        now = datetime.utcnow()
        trade = TradeOutcome(
            trade_id="test_001",
            session_id="session_001",
            timestamp_entry=now,
            timestamp_exit=now + timedelta(hours=2),
            strategy_name="mean_reversion",
            market_regime="ranging_low_vol",
            regime_confidence=0.85,
            volatility_regime="low",
            sentiment_direction="neutral",
            entry_price=50000.0,
            position_size_usd=100.0,
            position_size_btc=0.002,
            entry_confidence=0.75,
            stop_loss_price=49000.0,
            profit_target_price=51500.0,
            expected_win_rate=0.60,
            expected_rr_ratio=1.5,
            exit_price=51200.0,
            exit_reason=OutcomeType.WIN,
            pnl_usd=24.0,
            pnl_percent=2.4,
            hold_time_hours=2.0,
            actual_rr_ratio=1.47,
            max_favorable_excursion=0.03,
            max_adverse_excursion=-0.01,
            avg_volatility_during_trade=0.02,
            trace_factors=[{"factor": "regime_match", "confidence": 0.9}],
            portfolio_value_at_entry=10000.0,
            portfolio_value_at_exit=10024.0,
            tags=["paper_trading"]
        )
        assert trade.trade_id == "test_001"

    def test_exit_before_entry_rejected(self):
        """Test that exit timestamp before entry is rejected."""
        now = datetime.utcnow()
        with pytest.raises(ValueError, match="Exit timestamp.*must be after entry timestamp"):
            TradeOutcome(
                trade_id="test_002",
                session_id="session_001",
                timestamp_entry=now,
                timestamp_exit=now - timedelta(hours=1),  # INVALID: before entry
                strategy_name="mean_reversion",
                market_regime="ranging_low_vol",
                regime_confidence=0.85,
                volatility_regime="low",
                sentiment_direction="neutral",
                entry_price=50000.0,
                position_size_usd=100.0,
                position_size_btc=0.002,
                entry_confidence=0.75,
                stop_loss_price=49000.0,
                profit_target_price=51500.0,
                expected_win_rate=0.60,
                expected_rr_ratio=1.5,
                exit_price=51200.0,
                exit_reason=OutcomeType.WIN,
                pnl_usd=24.0,
                pnl_percent=2.4,
                hold_time_hours=2.0,
                actual_rr_ratio=1.47,
                max_favorable_excursion=0.03,
                max_adverse_excursion=-0.01,
                avg_volatility_during_trade=0.02,
                trace_factors=[],
                portfolio_value_at_entry=10000.0,
                portfolio_value_at_exit=10024.0,
                tags=["paper_trading"]
            )

    def test_negative_hold_time_rejected(self):
        """Test that negative hold time is rejected."""
        now = datetime.utcnow()
        with pytest.raises(ValueError, match="Hold time cannot be negative"):
            TradeOutcome(
                trade_id="test_003",
                session_id="session_001",
                timestamp_entry=now,
                timestamp_exit=now + timedelta(hours=2),
                strategy_name="mean_reversion",
                market_regime="ranging_low_vol",
                regime_confidence=0.85,
                volatility_regime="low",
                sentiment_direction="neutral",
                entry_price=50000.0,
                position_size_usd=100.0,
                position_size_btc=0.002,
                entry_confidence=0.75,
                stop_loss_price=49000.0,
                profit_target_price=51500.0,
                expected_win_rate=0.60,
                expected_rr_ratio=1.5,
                exit_price=51200.0,
                exit_reason=OutcomeType.WIN,
                pnl_usd=24.0,
                pnl_percent=2.4,
                hold_time_hours=-1.0,  # INVALID: negative
                actual_rr_ratio=1.47,
                max_favorable_excursion=0.03,
                max_adverse_excursion=-0.01,
                avg_volatility_during_trade=0.02,
                trace_factors=[],
                portfolio_value_at_entry=10000.0,
                portfolio_value_at_exit=10024.0,
                tags=["paper_trading"]
            )

    def test_invalid_confidence_values_rejected(self):
        """Test that confidence values outside 0-1 range are rejected."""
        now = datetime.utcnow()

        # Test regime_confidence > 1
        with pytest.raises(ValueError, match="Regime confidence must be 0-1"):
            TradeOutcome(
                trade_id="test_004",
                session_id="session_001",
                timestamp_entry=now,
                timestamp_exit=now + timedelta(hours=2),
                strategy_name="mean_reversion",
                market_regime="ranging_low_vol",
                regime_confidence=1.5,  # INVALID: >1
                volatility_regime="low",
                sentiment_direction="neutral",
                entry_price=50000.0,
                position_size_usd=100.0,
                position_size_btc=0.002,
                entry_confidence=0.75,
                stop_loss_price=49000.0,
                profit_target_price=51500.0,
                expected_win_rate=0.60,
                expected_rr_ratio=1.5,
                exit_price=51200.0,
                exit_reason=OutcomeType.WIN,
                pnl_usd=24.0,
                pnl_percent=2.4,
                hold_time_hours=2.0,
                actual_rr_ratio=1.47,
                max_favorable_excursion=0.03,
                max_adverse_excursion=-0.01,
                avg_volatility_during_trade=0.02,
                trace_factors=[],
                portfolio_value_at_entry=10000.0,
                portfolio_value_at_exit=10024.0,
                tags=["paper_trading"]
            )

        # Test entry_confidence < 0
        with pytest.raises(ValueError, match="Entry confidence must be 0-1"):
            TradeOutcome(
                trade_id="test_005",
                session_id="session_001",
                timestamp_entry=now,
                timestamp_exit=now + timedelta(hours=2),
                strategy_name="mean_reversion",
                market_regime="ranging_low_vol",
                regime_confidence=0.85,
                volatility_regime="low",
                sentiment_direction="neutral",
                entry_price=50000.0,
                position_size_usd=100.0,
                position_size_btc=0.002,
                entry_confidence=-0.1,  # INVALID: <0
                stop_loss_price=49000.0,
                profit_target_price=51500.0,
                expected_win_rate=0.60,
                expected_rr_ratio=1.5,
                exit_price=51200.0,
                exit_reason=OutcomeType.WIN,
                pnl_usd=24.0,
                pnl_percent=2.4,
                hold_time_hours=2.0,
                actual_rr_ratio=1.47,
                max_favorable_excursion=0.03,
                max_adverse_excursion=-0.01,
                avg_volatility_during_trade=0.02,
                trace_factors=[],
                portfolio_value_at_entry=10000.0,
                portfolio_value_at_exit=10024.0,
                tags=["paper_trading"]
            )

    def test_negative_position_size_rejected(self):
        """Test that negative position sizes are rejected."""
        now = datetime.utcnow()

        with pytest.raises(ValueError, match="Position size USD must be positive"):
            TradeOutcome(
                trade_id="test_006",
                session_id="session_001",
                timestamp_entry=now,
                timestamp_exit=now + timedelta(hours=2),
                strategy_name="mean_reversion",
                market_regime="ranging_low_vol",
                regime_confidence=0.85,
                volatility_regime="low",
                sentiment_direction="neutral",
                entry_price=50000.0,
                position_size_usd=-100.0,  # INVALID: negative
                position_size_btc=0.002,
                entry_confidence=0.75,
                stop_loss_price=49000.0,
                profit_target_price=51500.0,
                expected_win_rate=0.60,
                expected_rr_ratio=1.5,
                exit_price=51200.0,
                exit_reason=OutcomeType.WIN,
                pnl_usd=24.0,
                pnl_percent=2.4,
                hold_time_hours=2.0,
                actual_rr_ratio=1.47,
                max_favorable_excursion=0.03,
                max_adverse_excursion=-0.01,
                avg_volatility_during_trade=0.02,
                trace_factors=[],
                portfolio_value_at_entry=10000.0,
                portfolio_value_at_exit=10024.0,
                tags=["paper_trading"]
            )

    def test_zero_price_rejected(self):
        """Test that zero prices are rejected."""
        now = datetime.utcnow()

        with pytest.raises(ValueError, match="Entry price must be positive"):
            TradeOutcome(
                trade_id="test_007",
                session_id="session_001",
                timestamp_entry=now,
                timestamp_exit=now + timedelta(hours=2),
                strategy_name="mean_reversion",
                market_regime="ranging_low_vol",
                regime_confidence=0.85,
                volatility_regime="low",
                sentiment_direction="neutral",
                entry_price=0.0,  # INVALID: zero
                position_size_usd=100.0,
                position_size_btc=0.002,
                entry_confidence=0.75,
                stop_loss_price=49000.0,
                profit_target_price=51500.0,
                expected_win_rate=0.60,
                expected_rr_ratio=1.5,
                exit_price=51200.0,
                exit_reason=OutcomeType.WIN,
                pnl_usd=24.0,
                pnl_percent=2.4,
                hold_time_hours=2.0,
                actual_rr_ratio=1.47,
                max_favorable_excursion=0.03,
                max_adverse_excursion=-0.01,
                avg_volatility_during_trade=0.02,
                trace_factors=[],
                portfolio_value_at_entry=10000.0,
                portfolio_value_at_exit=10024.0,
                tags=["paper_trading"]
            )

    def test_empty_tags_rejected(self):
        """Test that empty tags list is rejected."""
        now = datetime.utcnow()

        with pytest.raises(ValueError, match="tags cannot be empty"):
            TradeOutcome(
                trade_id="test_008",
                session_id="session_001",
                timestamp_entry=now,
                timestamp_exit=now + timedelta(hours=2),
                strategy_name="mean_reversion",
                market_regime="ranging_low_vol",
                regime_confidence=0.85,
                volatility_regime="low",
                sentiment_direction="neutral",
                entry_price=50000.0,
                position_size_usd=100.0,
                position_size_btc=0.002,
                entry_confidence=0.75,
                stop_loss_price=49000.0,
                profit_target_price=51500.0,
                expected_win_rate=0.60,
                expected_rr_ratio=1.5,
                exit_price=51200.0,
                exit_reason=OutcomeType.WIN,
                pnl_usd=24.0,
                pnl_percent=2.4,
                hold_time_hours=2.0,
                actual_rr_ratio=1.47,
                max_favorable_excursion=0.03,
                max_adverse_excursion=-0.01,
                avg_volatility_during_trade=0.02,
                trace_factors=[],
                portfolio_value_at_entry=10000.0,
                portfolio_value_at_exit=10024.0,
                tags=[]  # INVALID: empty
            )

    def test_negative_rr_ratio_rejected(self):
        """Test that negative R:R ratios are rejected."""
        now = datetime.utcnow()

        with pytest.raises(ValueError, match="Expected R:R ratio cannot be negative"):
            TradeOutcome(
                trade_id="test_009",
                session_id="session_001",
                timestamp_entry=now,
                timestamp_exit=now + timedelta(hours=2),
                strategy_name="mean_reversion",
                market_regime="ranging_low_vol",
                regime_confidence=0.85,
                volatility_regime="low",
                sentiment_direction="neutral",
                entry_price=50000.0,
                position_size_usd=100.0,
                position_size_btc=0.002,
                entry_confidence=0.75,
                stop_loss_price=49000.0,
                profit_target_price=51500.0,
                expected_win_rate=0.60,
                expected_rr_ratio=-1.5,  # INVALID: negative
                exit_price=51200.0,
                exit_reason=OutcomeType.WIN,
                pnl_usd=24.0,
                pnl_percent=2.4,
                hold_time_hours=2.0,
                actual_rr_ratio=1.47,
                max_favorable_excursion=0.03,
                max_adverse_excursion=-0.01,
                avg_volatility_during_trade=0.02,
                trace_factors=[],
                portfolio_value_at_entry=10000.0,
                portfolio_value_at_exit=10024.0,
                tags=["paper_trading"]
            )

    def test_negative_portfolio_value_rejected(self):
        """Test that negative portfolio values are rejected."""
        now = datetime.utcnow()

        with pytest.raises(ValueError, match="Portfolio value at entry must be positive"):
            TradeOutcome(
                trade_id="test_010",
                session_id="session_001",
                timestamp_entry=now,
                timestamp_exit=now + timedelta(hours=2),
                strategy_name="mean_reversion",
                market_regime="ranging_low_vol",
                regime_confidence=0.85,
                volatility_regime="low",
                sentiment_direction="neutral",
                entry_price=50000.0,
                position_size_usd=100.0,
                position_size_btc=0.002,
                entry_confidence=0.75,
                stop_loss_price=49000.0,
                profit_target_price=51500.0,
                expected_win_rate=0.60,
                expected_rr_ratio=1.5,
                exit_price=51200.0,
                exit_reason=OutcomeType.WIN,
                pnl_usd=24.0,
                pnl_percent=2.4,
                hold_time_hours=2.0,
                actual_rr_ratio=1.47,
                max_favorable_excursion=0.03,
                max_adverse_excursion=-0.01,
                avg_volatility_during_trade=0.02,
                trace_factors=[],
                portfolio_value_at_entry=-10000.0,  # INVALID: negative
                portfolio_value_at_exit=10024.0,
                tags=["paper_trading"]
            )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
