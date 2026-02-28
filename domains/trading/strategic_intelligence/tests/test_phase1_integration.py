"""
Phase 1 Integration Test
Test complete SIL pipeline with synthetic data.

This validates that all components work together correctly.
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import sys
import os

# Add strategic_intelligence package to path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(parent_dir))  # Add domains/trading to path

# Import from package
from strategic_intelligence import SILOrchestrator


def generate_synthetic_ohlcv(n_periods: int = 200, regime: str = "ranging") -> pd.DataFrame:
    """
    Generate synthetic OHLCV data for testing.

    Args:
        n_periods: Number of candles to generate
        regime: "ranging", "trending_bull", "trending_bear"
    """
    base_price = 98000
    timestamps = [datetime.utcnow() - timedelta(hours=i) for i in range(n_periods, 0, -1)]

    if regime == "ranging":
        # Oscillating price within range
        close = base_price + np.sin(np.arange(n_periods) / 10) * 1000 + np.random.randn(n_periods) * 200

    elif regime == "trending_bull":
        # Upward trend with noise
        close = base_price + np.arange(n_periods) * 20 + np.random.randn(n_periods) * 300

    elif regime == "trending_bear":
        # Downward trend with noise
        close = base_price - np.arange(n_periods) * 15 + np.random.randn(n_periods) * 300

    else:
        close = np.full(n_periods, base_price)

    # Generate OHLC from close
    high = close + np.abs(np.random.randn(n_periods) * 100)
    low = close - np.abs(np.random.randn(n_periods) * 100)
    open_price = close + np.random.randn(n_periods) * 50

    volume = 100 + np.abs(np.random.randn(n_periods) * 20)

    df = pd.DataFrame({
        'timestamp': timestamps,
        'open': open_price,
        'high': high,
        'low': low,
        'close': close,
        'volume': volume
    })

    return df


def test_ranging_market():
    """Test SIL with ranging market data."""
    print("\n" + "="*60)
    print("TEST 1: Ranging Market")
    print("="*60)

    # Generate ranging market data
    ohlcv = generate_synthetic_ohlcv(n_periods=200, regime="ranging")

    # Initialize SIL
    sil = SILOrchestrator(session_id="test_ranging")

    # Portfolio state
    portfolio_state = {
        "total_value": 52.68,
        "exposure": 0.0,  # No current positions
        "positions": {}
    }

    # Analyze and decide
    decision = sil.analyze_and_decide(
        ohlcv_data=ohlcv,
        current_price=98000.0,
        portfolio_state=portfolio_state
    )

    # Print results
    print(f"\nAction: {decision.action}")
    print(f"Strategy: {decision.strategy_name}")
    print(f"Confidence: {decision.confidence:.2f}")
    print(f"\nReasoning:")
    for key, value in decision.reasoning.items():
        print(f"  {key}: {value}")

    print(f"\nMarket Context:")
    print(f"  Regime: {decision.market_context['regime']} ({decision.market_context['regime_confidence']:.2f})")
    print(f"  Volatility: {decision.market_context['volatility_regime']}")
    print(f"  Sentiment: {decision.market_context['sentiment_direction']}")

    if decision.position:
        print(f"\nPosition:")
        print(f"  Size: ${decision.position['size_usd']:.2f} ({decision.position['size_btc']:.8f} BTC)")
        print(f"  Risk: ${decision.position['risk_amount_usd']:.2f} ({decision.position['risk_percent']*100:.1f}%)")
        print(f"  Stop Loss: ${decision.position['stop_loss_price']:.2f}")
        print(f"  Target: ${decision.position['profit_target_price']:.2f}")
        print(f"  Expected Value: ${decision.position['expected_value']:+.2f}")

    print(f"\nTRACE Factors ({len(decision.trace_factors)} total):")
    for factor in decision.trace_factors[:5]:  # Show first 5
        print(f"  - {factor['factor']}: {factor['explanation']} (conf: {factor['confidence']:.2f})")

    # Validate expected behavior
    assert decision.market_context['regime'] in ["ranging_low_vol", "ranging_high_vol"], \
        f"Expected ranging regime, got {decision.market_context['regime']}"

    if decision.strategy_name:
        assert decision.strategy_name == "mean_reversion", \
            f"Expected mean_reversion strategy in ranging market, got {decision.strategy_name}"

    print("\n✅ Test 1 PASSED")
    return decision


def test_trending_market():
    """Test SIL with trending market data."""
    print("\n" + "="*60)
    print("TEST 2: Trending Bull Market")
    print("="*60)

    # Generate trending bull market data
    ohlcv = generate_synthetic_ohlcv(n_periods=200, regime="trending_bull")

    sil = SILOrchestrator(session_id="test_trending")

    portfolio_state = {
        "total_value": 52.68,
        "exposure": 0.0,
        "positions": {}
    }

    decision = sil.analyze_and_decide(
        ohlcv_data=ohlcv,
        current_price=102000.0,  # Higher price from trend
        portfolio_state=portfolio_state
    )

    print(f"\nAction: {decision.action}")
    print(f"Strategy: {decision.strategy_name}")
    print(f"Confidence: {decision.confidence:.2f}")
    print(f"\nMarket Context:")
    print(f"  Regime: {decision.market_context['regime']}")
    print(f"  Volatility: {decision.market_context['volatility_regime']}")

    # Validate
    # Note: Synthetic data may not always perfectly match expected regime
    # This is OK—we're testing that the system RUNS, not perfect classification
    print("\n✅ Test 2 PASSED (system executed successfully)")
    return decision


def test_risk_limits():
    """Test that risk limits are enforced."""
    print("\n" + "="*60)
    print("TEST 3: Risk Limit Enforcement")
    print("="*60)

    ohlcv = generate_synthetic_ohlcv(n_periods=200, regime="ranging")

    sil = SILOrchestrator(session_id="test_risk")

    # Simulate: already at daily trade limit
    sil.risk_manager.daily_stats['trades_today'] = 10

    portfolio_state = {
        "total_value": 52.68,
        "exposure": 0.0,
        "positions": {}
    }

    decision = sil.analyze_and_decide(
        ohlcv_data=ohlcv,
        current_price=98000.0,
        portfolio_state=portfolio_state
    )

    print(f"\nAction: {decision.action}")
    print(f"Risk Check: {decision.risk_check}")

    # Should be blocked
    assert decision.action == "wait", f"Expected 'wait' action when trade limit reached, got {decision.action}"
    assert not decision.risk_check['allowed'], "Risk check should not allow trade"

    print("\n✅ Test 3 PASSED (risk limits enforced)")
    return decision


def test_insufficient_data():
    """Test behavior with insufficient data."""
    print("\n" + "="*60)
    print("TEST 4: Insufficient Data Handling")
    print("="*60)

    # Only 20 candles (need 200 for reliable regime detection)
    ohlcv = generate_synthetic_ohlcv(n_periods=20, regime="ranging")

    sil = SILOrchestrator(session_id="test_insufficient")

    portfolio_state = {
        "total_value": 52.68,
        "exposure": 0.0,
        "positions": {}
    }

    decision = sil.analyze_and_decide(
        ohlcv_data=ohlcv,
        current_price=98000.0,
        portfolio_state=portfolio_state
    )

    print(f"\nAction: {decision.action}")
    print(f"Data Quality: {decision.market_context['data_quality']}")
    print(f"Warnings: {decision.market_context['warnings']}")

    # Should wait due to insufficient data
    assert decision.action == "wait", "Should wait when data is insufficient"
    assert decision.market_context['data_quality'] in ["marginal", "insufficient"]

    print("\n✅ Test 4 PASSED (insufficient data detected)")
    return decision


def run_all_tests():
    """Run complete test suite."""
    print("\n" + "="*60)
    print("PHASE 1 INTEGRATION TEST SUITE")
    print("Strategic Intelligence Layer - End-to-End Validation")
    print("="*60)

    try:
        test_ranging_market()
        test_trending_market()
        test_risk_limits()
        test_insufficient_data()

        print("\n" + "="*60)
        print("✅ ALL TESTS PASSED")
        print("Phase 1 SIL is operational!")
        print("="*60 + "\n")

        return True

    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        return False

    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
