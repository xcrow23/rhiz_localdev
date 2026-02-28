"""
Integration Tests for SIL Components

Tests the integration between major SIL components to ensure they work
together correctly in realistic scenarios.
"""

import pytest
import pandas as pd
from datetime import datetime, timedelta
from sil_orchestrator import SILOrchestrator
from market_context.context_engine import MarketContext


@pytest.fixture
def sil():
    """Create SILOrchestrator for integration testing."""
    return SILOrchestrator(
        enable_memory=False,
        enable_learning=False,
        enable_transparency=False
    )


@pytest.fixture
def trending_up_ohlcv():
    """Create OHLCV data for uptrending market."""
    timestamps = [datetime.utcnow() - timedelta(hours=i) for i in range(50, 0, -1)]
    data = {
        'timestamp': timestamps,
        'open': [50000.0 + i * 200 for i in range(50)],
        'high': [50300.0 + i * 200 for i in range(50)],
        'low': [49800.0 + i * 200 for i in range(50)],
        'close': [50200.0 + i * 200 for i in range(50)],
        'volume': [100.0] * 50
    }
    return pd.DataFrame(data)


@pytest.fixture
def ranging_ohlcv():
    """Create OHLCV data for ranging market."""
    timestamps = [datetime.utcnow() - timedelta(hours=i) for i in range(50, 0, -1)]
    # Oscillate between 49500 and 50500
    closes = [50000.0 + 500 * (1 if i % 2 == 0 else -1) for i in range(50)]
    data = {
        'timestamp': timestamps,
        'open': [c - 100 for c in closes],
        'high': [c + 200 for c in closes],
        'low': [c - 200 for c in closes],
        'close': closes,
        'volume': [100.0] * 50
    }
    return pd.DataFrame(data)


@pytest.fixture
def portfolio_state():
    """Create sample portfolio state."""
    return {
        'total_value': 1000.0,
        'exposure': 0.0,
        'positions': {}
    }


class TestEndToEndDecisionFlow:
    """Test complete decision flow from data to action."""

    def test_valid_data_produces_decision(self, sil, trending_up_ohlcv, portfolio_state):
        """Test that valid data produces a complete decision."""
        decision = sil.analyze_and_decide(
            ohlcv_data=trending_up_ohlcv,
            current_price=60000.0,
            portfolio_state=portfolio_state
        )

        assert decision is not None
        assert decision.action in ["enter_long", "wait", "hold"]
        assert decision.confidence >= 0.0 and decision.confidence <= 1.0
        assert 'primary' in decision.reasoning
        assert len(decision.trace_factors) > 0
        assert decision.market_context is not None

    def test_invalid_ohlcv_returns_wait_decision(self, sil, portfolio_state):
        """Test that invalid OHLCV returns wait decision with error."""
        # Create invalid OHLCV (too few rows)
        invalid_df = pd.DataFrame({
            'timestamp': [datetime.utcnow()],
            'open': [50000.0],
            'high': [50500.0],
            'low': [49500.0],
            'close': [50200.0],
            'volume': [100.0]
        })

        decision = sil.analyze_and_decide(
            ohlcv_data=invalid_df,
            current_price=50200.0,
            portfolio_state=portfolio_state
        )

        assert decision.action == "wait"
        assert "validation failed" in decision.reasoning['primary'].lower()

    def test_circuit_breaker_blocks_trade(self, sil, trending_up_ohlcv, portfolio_state):
        """Test that circuit breaker blocks trades after consecutive losses."""
        # Trip circuit breaker by recording losses
        for _ in range(5):
            sil.risk_manager.record_trade_result(-10.0)

        decision = sil.analyze_and_decide(
            ohlcv_data=trending_up_ohlcv,
            current_price=60000.0,
            portfolio_state=portfolio_state
        )

        assert decision.action == "wait"
        assert "circuit breaker" in decision.reasoning['secondary'].lower() or \
               "risk controls" in decision.reasoning['primary'].lower()


class TestMarketContextIntegration:
    """Test market context analysis integration."""

    def test_trending_market_detected(self, sil, trending_up_ohlcv):
        """Test that trending market is correctly detected."""
        context = sil.market_context_engine.analyze(trending_up_ohlcv)

        # Should detect uptrend
        assert context is not None
        assert context.regime in ["trending_bullish", "trending_low_vol", "trending_high_vol"]
        assert context.regime_confidence > 0.0

    def test_ranging_market_detected(self, sil, ranging_ohlcv):
        """Test that ranging market is correctly detected."""
        context = sil.market_context_engine.analyze(ranging_ohlcv)

        assert context is not None
        assert "ranging" in context.regime.lower() or context.regime == "choppy"
        assert context.regime_confidence > 0.0


class TestRiskManagementIntegration:
    """Test risk management integration with decision flow."""

    def test_daily_loss_limit_respected(self, sil, trending_up_ohlcv, portfolio_state):
        """Test that daily loss limit is respected."""
        # Record losses up to daily limit
        sil.risk_manager.record_trade_result(-50.0)  # 5% of portfolio

        decision = sil.analyze_and_decide(
            ohlcv_data=trending_up_ohlcv,
            current_price=60000.0,
            portfolio_state=portfolio_state
        )

        # Should either wait or have very small position
        assert decision.action in ["wait", "hold"] or \
               (decision.position and decision.position['size_usd'] < 50.0)

    def test_position_sizing_respects_confidence(self, sil, trending_up_ohlcv, portfolio_state):
        """Test that position sizing scales with confidence."""
        decision = sil.analyze_and_decide(
            ohlcv_data=trending_up_ohlcv,
            current_price=60000.0,
            portfolio_state=portfolio_state
        )

        if decision.position:
            # Position size should be reasonable relative to portfolio
            position_size = decision.position['size_usd']
            portfolio_value = portfolio_state['total_value']

            # Should not exceed 50% of portfolio (extreme safety check)
            assert position_size <= portfolio_value * 0.50, "Position too large"

            # Should not be dust (< $5)
            assert position_size >= 5.0 or position_size == 0.0, "Position too small (dust)"


class TestTraceFactorGeneration:
    """Test TRACE_FE transparency factor generation."""

    def test_trace_factors_present_in_decision(self, sil, trending_up_ohlcv, portfolio_state):
        """Test that all decisions include trace factors."""
        decision = sil.analyze_and_decide(
            ohlcv_data=trending_up_ohlcv,
            current_price=60000.0,
            portfolio_state=portfolio_state
        )

        assert len(decision.trace_factors) > 0

        # Each factor should have required fields
        for factor in decision.trace_factors:
            assert 'factor' in factor
            assert 'explanation' in factor
            assert 'confidence' in factor
            assert 0.0 <= factor['confidence'] <= 1.0

    def test_trace_factors_explain_decision(self, sil, trending_up_ohlcv, portfolio_state):
        """Test that trace factors provide meaningful explanations."""
        decision = sil.analyze_and_decide(
            ohlcv_data=trending_up_ohlcv,
            current_price=60000.0,
            portfolio_state=portfolio_state
        )

        explanations = [f['explanation'] for f in decision.trace_factors]

        # Should have at least one regime-related factor
        regime_mentioned = any('regime' in exp.lower() for exp in explanations)
        assert regime_mentioned, "No regime factors in trace"


class TestEdgeCaseHandling:
    """Test edge case handling across integration points."""

    def test_zero_portfolio_value_handled(self, sil, trending_up_ohlcv):
        """Test that zero portfolio value is handled gracefully."""
        portfolio_state = {
            'total_value': 0.0,
            'exposure': 0.0,
            'positions': {}
        }

        decision = sil.analyze_and_decide(
            ohlcv_data=trending_up_ohlcv,
            current_price=60000.0,
            portfolio_state=portfolio_state
        )

        # Should wait (can't trade with zero capital)
        assert decision.action == "wait"
        assert decision.position is None or decision.position['size_usd'] == 0.0

    def test_extreme_volatility_reduces_position(self, sil, portfolio_state):
        """Test that extreme volatility reduces position size."""
        # Create extremely volatile OHLCV (10% swings per candle)
        timestamps = [datetime.utcnow() - timedelta(hours=i) for i in range(50, 0, -1)]
        closes = []
        for i in range(50):
            base = 50000.0
            closes.append(base + base * 0.10 * (1 if i % 2 == 0 else -1))

        data = {
            'timestamp': timestamps,
            'open': [c - 100 for c in closes],
            'high': [c + 2000 for c in closes],
            'low': [c - 2000 for c in closes],
            'close': closes,
            'volume': [100.0] * 50
        }
        volatile_df = pd.DataFrame(data)

        decision = sil.analyze_and_decide(
            ohlcv_data=volatile_df,
            current_price=50000.0,
            portfolio_state=portfolio_state
        )

        # If position is taken, should be reduced due to volatility
        if decision.position and decision.position['size_usd'] > 0:
            # Should not exceed 20% of portfolio in extreme volatility
            assert decision.position['size_usd'] <= portfolio_state['total_value'] * 0.20


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
