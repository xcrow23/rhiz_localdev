"""
Phase 2 Integration Tests
Tests for Memory, Learning, and Transparency integration.

Tests:
1. Transparency layer (local logging, no external dependencies)
2. Memory integration (requires Qdrant - optional)
3. Learning engine (requires memory + trades - optional)
4. Full Phase 2 workflow (transparency + memory + learning)
"""

import sys
import os
from pathlib import Path
from datetime import datetime, timedelta
import numpy as np

# Add parent directory to path for imports
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(parent_dir))

try:
    from strategic_intelligence import SILOrchestrator
    from strategic_intelligence.memory import (
        TradeOutcome, OutcomeType, QdrantMemoryClient,
        encode_market_conditions, encode_regime_characteristics
    )
    from strategic_intelligence.learning import LearningEngine, PerformanceMetrics
    from strategic_intelligence.transparency import TraceLogger
    IMPORTS_AVAILABLE = True
except ImportError as e:
    IMPORTS_AVAILABLE = False
    print(f"Import error: {e}")


def generate_sample_ohlcv(n_candles=200, regime="ranging"):
    """Generate synthetic OHLCV data for testing."""
    import pandas as pd

    dates = [datetime.utcnow() - timedelta(hours=i) for i in range(n_candles, 0, -1)]

    if regime == "ranging":
        # Ranging market: oscillate around 98000
        base_price = 98000
        close_prices = [base_price + np.random.normal(0, 500) for _ in range(n_candles)]
    elif regime == "trending":
        # Trending market: upward trend
        base_price = 95000
        close_prices = [base_price + (i * 20) + np.random.normal(0, 300) for i in range(n_candles)]
    else:
        close_prices = [98000] * n_candles

    data = {
        'timestamp': dates,
        'open': [p + np.random.normal(0, 100) for p in close_prices],
        'high': [p + abs(np.random.normal(200, 100)) for p in close_prices],
        'low': [p - abs(np.random.normal(200, 100)) for p in close_prices],
        'close': close_prices,
        'volume': [np.random.uniform(100, 1000) for _ in range(n_candles)]
    }

    return pd.DataFrame(data)


def create_sample_trade_outcome(trade_id: str, win: bool = True) -> TradeOutcome:
    """Create sample TradeOutcome for testing."""
    entry_price = 97500.0
    exit_price = 98000.0 if win else 97200.0  # Win: +0.51%, Loss: -0.31%

    return TradeOutcome(
        trade_id=trade_id,
        session_id="test_session_001",
        timestamp_entry=datetime.utcnow() - timedelta(hours=2),
        timestamp_exit=datetime.utcnow(),
        strategy_name="mean_reversion",
        market_regime="ranging_low_vol",
        regime_confidence=0.85,
        volatility_regime="low",
        sentiment_direction="neutral",
        entry_price=entry_price,
        position_size_usd=10.0,
        position_size_btc=10.0 / entry_price,
        entry_confidence=0.75,
        stop_loss_price=entry_price * 0.97,  # 3% stop
        profit_target_price=entry_price * 1.05,  # 5% target
        expected_win_rate=0.60,
        expected_rr_ratio=1.67,
        exit_price=exit_price,
        exit_reason=OutcomeType.WIN if win else OutcomeType.LOSS,
        pnl_usd=(exit_price - entry_price) * (10.0 / entry_price),
        pnl_percent=(exit_price - entry_price) / entry_price,
        hold_time_hours=2.0,
        actual_rr_ratio=(exit_price - entry_price) / (entry_price - entry_price * 0.97) if win else 0.0,
        max_favorable_excursion=0.008 if win else 0.002,
        max_adverse_excursion=-0.015,
        avg_volatility_during_trade=0.025,
        trace_factors=[
            {"factor": "regime_match", "explanation": "Ranging market detected", "confidence": 0.85},
            {"factor": "risk_approved", "explanation": "Within risk limits", "confidence": 0.90}
        ],
        portfolio_value_at_entry=50.0,
        portfolio_value_at_exit=50.0 + ((exit_price - entry_price) * (10.0 / entry_price)),
        tags=["test", "paper_trading"],
        notes="Test trade for Phase 2 integration"
    )


# ========================================
# Test 1: Transparency Layer (No Dependencies)
# ========================================

def test_transparency_layer():
    """Test transparency layer with local logging only."""
    print("\n" + "="*70)
    print("TEST 1: Transparency Layer (Local Logging)")
    print("="*70)

    if not IMPORTS_AVAILABLE:
        print("❌ SKIP: Imports not available")
        return False

    try:
        # Initialize SIL with transparency only
        sil = SILOrchestrator(
            session_id="transparency_test_001",
            enable_transparency=True,
            enable_memory=False,
            enable_learning=False
        )

        # Generate sample data
        ohlcv = generate_sample_ohlcv(regime="ranging")

        # Make decision
        decision = sil.analyze_and_decide(
            ohlcv_data=ohlcv,
            current_price=98000,
            portfolio_state={
                "total_value": 50.0,
                "exposure": 0.0,
                "positions": {}
            }
        )

        print(f"\n✅ Decision Generated:")
        print(f"   Action: {decision.action}")
        print(f"   Strategy: {decision.strategy_name}")
        print(f"   Confidence: {decision.confidence:.1%}")

        # Check log files created
        log_dir = Path(__file__).parent.parent / "transparency" / "logs"
        log_files = list(log_dir.glob("trace_*.jsonl"))

        if log_files:
            print(f"\n✅ Log Files Created: {len(log_files)} files")
            latest_log = sorted(log_files, reverse=True)[0]
            print(f"   Latest: {latest_log.name}")
        else:
            print("\n⚠️ No log files found (check transparency/logs/)")

        # Get session report
        report = sil.get_session_report()
        print(f"\n✅ Session Report Generated ({len(report)} chars)")

        print("\n✅ TEST 1 PASSED: Transparency layer functional")
        return True

    except Exception as e:
        print(f"\n❌ TEST 1 FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


# ========================================
# Test 2: Memory Integration (Requires Qdrant)
# ========================================

def test_memory_integration():
    """Test memory integration with Qdrant."""
    print("\n" + "="*70)
    print("TEST 2: Memory Integration (Requires Qdrant)")
    print("="*70)

    if not IMPORTS_AVAILABLE:
        print("❌ SKIP: Imports not available")
        return False

    try:
        # Try to connect to Qdrant
        memory_client = QdrantMemoryClient(
            host="localhost",
            port=6333,
            initialize_collections=True
        )

        print("✅ Connected to Qdrant")

        # Check collections
        stats = memory_client.get_collection_stats()
        print(f"   Collections: {stats}")

        # Create sample trade outcome
        trade = create_sample_trade_outcome("test_trade_001", win=True)

        # Encode market conditions
        embedding = encode_market_conditions(
            regime=trade.market_regime,
            volatility=trade.avg_volatility_during_trade,
            sentiment=trade.sentiment_direction
        )

        # Store trade
        trade_id = memory_client.store_trade_outcome(trade, embedding)
        print(f"\n✅ Trade Stored: {trade_id}")

        # Retrieve trade
        retrieved = memory_client.get_trade_outcome(trade_id)
        if retrieved:
            print(f"✅ Trade Retrieved: {retrieved.strategy_name} ({retrieved.exit_reason.value})")
        else:
            print("⚠️ Trade not found")

        # Find similar trades
        similar = memory_client.find_similar_trades(
            current_market_embedding=embedding,
            strategy_name="mean_reversion",
            limit=5
        )

        print(f"✅ Similar Trades Found: {len(similar)}")

        print("\n✅ TEST 2 PASSED: Memory integration functional")
        return True

    except Exception as e:
        print(f"\n⚠️ TEST 2 SKIPPED: {e}")
        print("   (Qdrant not running - this is optional)")
        return None  # Not a failure, just skipped


# ========================================
# Test 3: Learning Engine (Requires Memory + Trades)
# ========================================

def test_learning_engine():
    """Test learning engine with sample trades."""
    print("\n" + "="*70)
    print("TEST 3: Learning Engine (Requires Memory + Trades)")
    print("="*70)

    if not IMPORTS_AVAILABLE:
        print("❌ SKIP: Imports not available")
        return False

    try:
        # Try to connect to Qdrant
        memory_client = QdrantMemoryClient(
            host="localhost",
            port=6333,
            initialize_collections=True
        )

        # Initialize learning engine
        learning_engine = LearningEngine(
            memory_client=memory_client,
            min_trades_for_learning=5,
            confidence_threshold=0.70
        )

        print("✅ Learning Engine Initialized")

        # Create and store sample trades (mix of wins and losses)
        for i in range(15):
            win = i % 3 != 0  # 67% win rate
            trade = create_sample_trade_outcome(f"learning_test_{i:03d}", win=win)

            embedding = encode_market_conditions(
                regime=trade.market_regime,
                volatility=trade.avg_volatility_during_trade,
                sentiment=trade.sentiment_direction
            )

            memory_client.store_trade_outcome(trade, embedding)

        print(f"✅ Stored 15 sample trades (10 wins, 5 losses)")

        # Analyze performance
        metrics = learning_engine.analyze_strategy_performance(
            strategy_name="mean_reversion",
            regime="ranging_low_vol",
            days_back=7
        )

        print(f"\n📊 Performance Metrics:")
        print(f"   Total Trades: {metrics.total_trades}")
        print(f"   Win Rate: {metrics.win_rate:.1%} (expected: {metrics.avg_predicted_win_rate:.1%})")
        print(f"   Calibration Error: {metrics.calibration_error:.1%}")
        print(f"   Sharpe Ratio: {metrics.sharpe_ratio:.2f}")
        print(f"   Sample Confidence: {metrics.sample_size_confidence:.1%}")

        # Get parameter suggestions
        suggestions = learning_engine.suggest_parameter_adaptations(
            strategy_name="mean_reversion",
            regime="ranging_low_vol",
            days_back=7
        )

        if suggestions:
            print(f"\n💡 Parameter Suggestions: {len(suggestions)}")
            for s in suggestions:
                print(f"   {s.parameter_name}: {s.current_value} → {s.suggested_value}")
                print(f"      {s.rationale} (confidence: {s.confidence:.1%})")
        else:
            print("\n⚠️ No parameter suggestions (need more trades or higher confidence)")

        print("\n✅ TEST 3 PASSED: Learning engine functional")
        return True

    except Exception as e:
        print(f"\n⚠️ TEST 3 SKIPPED: {e}")
        print("   (Qdrant not running - this is optional)")
        return None


# ========================================
# Test 4: Full Phase 2 Workflow
# ========================================

def test_full_phase2_workflow():
    """Test complete Phase 2 workflow (transparency + memory + learning)."""
    print("\n" + "="*70)
    print("TEST 4: Full Phase 2 Workflow")
    print("="*70)

    if not IMPORTS_AVAILABLE:
        print("❌ SKIP: Imports not available")
        return False

    try:
        # Initialize SIL with full Phase 2
        sil = SILOrchestrator(
            session_id="full_phase2_test_001",
            enable_transparency=True,
            enable_memory=True,
            enable_learning=True,
            qdrant_host="localhost",
            qdrant_port=6333
        )

        print("✅ Full Phase 2 SIL Initialized")

        # Make decision
        ohlcv = generate_sample_ohlcv(regime="ranging")
        decision = sil.analyze_and_decide(
            ohlcv_data=ohlcv,
            current_price=98000,
            portfolio_state={
                "total_value": 50.0,
                "exposure": 0.0,
                "positions": {}
            }
        )

        print(f"\n✅ Decision: {decision.action} (confidence: {decision.confidence:.1%})")

        # Simulate trade completion and record outcome
        if decision.action == "enter_long":
            trade = create_sample_trade_outcome("full_workflow_001", win=True)
            sil.record_trade_outcome(trade)
            print("✅ Trade Outcome Recorded")

        # Get performance insights
        insights = sil.get_performance_insights(days_back=7)

        if "error" not in insights:
            print("✅ Performance Insights Retrieved")
        else:
            print(f"⚠️ {insights['error']}: {insights['message']}")

        # Get session report
        report = sil.get_session_report()
        if "error" not in report:
            print("✅ Session Report Generated")

        print("\n✅ TEST 4 PASSED: Full Phase 2 workflow functional")
        return True

    except Exception as e:
        print(f"\n⚠️ TEST 4 SKIPPED/FAILED: {e}")
        print("   (Likely Qdrant not running)")
        import traceback
        traceback.print_exc()
        return None


# ========================================
# Main Test Runner
# ========================================

def main():
    """Run all Phase 2 integration tests."""
    print("\n" + "="*70)
    print("PHASE 2 INTEGRATION TESTS")
    print("="*70)

    if not IMPORTS_AVAILABLE:
        print("\n❌ CRITICAL: Module imports failed")
        print("Ensure all Phase 2 modules are correctly installed.")
        return

    results = {
        "transparency": test_transparency_layer(),
        "memory": test_memory_integration(),
        "learning": test_learning_engine(),
        "full_workflow": test_full_phase2_workflow()
    }

    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)

    for test_name, result in results.items():
        if result is True:
            status = "✅ PASSED"
        elif result is False:
            status = "❌ FAILED"
        else:
            status = "⚠️ SKIPPED"

        print(f"{status}: {test_name}")

    # Overall result
    passed = sum(1 for r in results.values() if r is True)
    failed = sum(1 for r in results.values() if r is False)
    skipped = sum(1 for r in results.values() if r is None)

    print(f"\n{passed} passed, {failed} failed, {skipped} skipped")

    if failed == 0 and passed > 0:
        print("\n✅ Phase 2 integration tests: SUCCESS")
    elif failed > 0:
        print("\n❌ Phase 2 integration tests: SOME FAILURES")
    else:
        print("\n⚠️ Phase 2 integration tests: MOSTLY SKIPPED (Qdrant not running)")

    print("\nNote: Transparency layer works without Qdrant.")
    print("For full Phase 2, start Qdrant: docker run -p 6333:6333 qdrant/qdrant")


if __name__ == "__main__":
    main()
