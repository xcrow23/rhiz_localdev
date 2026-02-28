"""
Unit Tests for Circuit Breaker (HIGH-12)

Tests the circuit breaker implementation added in Sprint 2 to prevent
runaway losses and require human intervention after consecutive failures.
"""

import pytest
from datetime import datetime
from pathlib import Path
import tempfile
import shutil
from risk_management.position_sizer import RiskManager, PositionSize


@pytest.fixture
def temp_state_dir():
    """Create temporary directory for state files."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def risk_manager(temp_state_dir):
    """Create RiskManager with temporary state directory."""
    return RiskManager(state_dir=temp_state_dir)


@pytest.fixture
def sample_position():
    """Create sample PositionSize for testing."""
    return PositionSize(
        size_usd=100.0,
        size_btc=0.002,
        entry_price=50000.0,
        risk_amount_usd=3.0,
        risk_percent=0.03,
        stop_loss_price=49000.0,
        profit_target_price=51500.0,
        expected_value=1.5,
        reward_risk_ratio=1.5,
        adjustments={},
        trace_factors=[],
        timestamp=datetime.utcnow()
    )


class TestCircuitBreakerBasics:
    """Test basic circuit breaker functionality."""

    def test_circuit_breaker_trips_after_max_losses(self, risk_manager, sample_position):
        """Test that circuit breaker trips after max consecutive losses."""
        portfolio_state = {'total_value': 1000.0, 'positions': {}}
        global_limits = {'max_consecutive_losses': 5}

        # Record 5 consecutive losses
        for i in range(5):
            risk_manager.record_trade_result(-10.0)

        # 6th trade should be blocked by circuit breaker
        allowed, reason = risk_manager.check_trade_allowed(
            sample_position,
            portfolio_state,
            global_limits
        )

        assert not allowed, "Trade should be blocked after max consecutive losses"
        assert "CIRCUIT BREAKER TRIPPED" in reason
        assert "CAPTAIN OVERRIDE REQUIRED" in reason
        assert risk_manager.daily_stats['circuit_breaker_tripped'] is True

    def test_win_resets_consecutive_loss_counter(self, risk_manager, sample_position):
        """Test that a win resets the consecutive loss counter."""
        portfolio_state = {'total_value': 1000.0, 'positions': {}}
        global_limits = {'max_consecutive_losses': 5}

        # Record 3 losses
        for i in range(3):
            risk_manager.record_trade_result(-10.0)

        assert risk_manager.daily_stats['consecutive_losses'] == 3

        # Record a win
        risk_manager.record_trade_result(15.0)

        assert risk_manager.daily_stats['consecutive_losses'] == 0, "Win should reset counter to 0"

        # Trade should still be allowed
        allowed, reason = risk_manager.check_trade_allowed(
            sample_position,
            portfolio_state,
            global_limits
        )

        assert allowed, "Trade should be allowed after counter reset"

    def test_circuit_breaker_prevents_trading(self, risk_manager, sample_position):
        """Test that circuit breaker blocks all trades when active."""
        portfolio_state = {'total_value': 1000.0, 'positions': {}}
        global_limits = {'max_consecutive_losses': 5}

        # Manually trip circuit breaker
        risk_manager.daily_stats['circuit_breaker_tripped'] = True
        risk_manager.daily_stats['circuit_breaker_reason'] = "Test trigger"

        # Attempt trade
        allowed, reason = risk_manager.check_trade_allowed(
            sample_position,
            portfolio_state,
            global_limits
        )

        assert not allowed, "Circuit breaker should block trade"
        assert "CIRCUIT BREAKER ACTIVE" in reason
        assert "CAPTAIN OVERRIDE REQUIRED" in reason


class TestCaptainOverride:
    """Test Captain override functionality."""

    def test_captain_override_resets_circuit_breaker(self, risk_manager):
        """Test that Captain override resets circuit breaker."""
        # Trip circuit breaker
        risk_manager.daily_stats['circuit_breaker_tripped'] = True
        risk_manager.daily_stats['circuit_breaker_reason'] = "5 consecutive losses"
        risk_manager.daily_stats['consecutive_losses'] = 5

        # Captain override
        risk_manager.captain_override_circuit_breaker(reason="Reviewed losses, adjusted strategy")

        assert risk_manager.daily_stats['circuit_breaker_tripped'] is False
        assert risk_manager.daily_stats['circuit_breaker_reason'] is None
        assert risk_manager.daily_stats['consecutive_losses'] == 0

    def test_override_logs_audit_trail(self, risk_manager):
        """Test that override logs audit trail."""
        risk_manager.daily_stats['circuit_breaker_tripped'] = True
        risk_manager.daily_stats['circuit_breaker_reason'] = "Test trigger"

        override_reason = "Analyzed losses, increased stop loss"
        risk_manager.captain_override_circuit_breaker(reason=override_reason)

        assert 'last_captain_override' in risk_manager.daily_stats
        assert risk_manager.daily_stats['last_captain_override']['reason'] == override_reason
        assert 'timestamp' in risk_manager.daily_stats['last_captain_override']

    def test_override_allows_trading_to_resume(self, risk_manager, sample_position):
        """Test that trading resumes after Captain override."""
        portfolio_state = {'total_value': 1000.0, 'positions': {}}
        global_limits = {'max_consecutive_losses': 5}

        # Trip circuit breaker
        risk_manager.daily_stats['circuit_breaker_tripped'] = True
        risk_manager.daily_stats['circuit_breaker_reason'] = "Test"

        # Verify trading blocked
        allowed_before, _ = risk_manager.check_trade_allowed(
            sample_position,
            portfolio_state,
            global_limits
        )
        assert not allowed_before

        # Override
        risk_manager.captain_override_circuit_breaker(reason="Test override")

        # Verify trading allowed
        allowed_after, reason = risk_manager.check_trade_allowed(
            sample_position,
            portfolio_state,
            global_limits
        )
        assert allowed_after, f"Trading should resume after override: {reason}"


class TestStatePersistence:
    """Test circuit breaker state persistence."""

    def test_circuit_breaker_state_saves_to_file(self, temp_state_dir):
        """Test that circuit breaker state persists to file."""
        risk_manager = RiskManager(state_dir=temp_state_dir)

        # Trip circuit breaker
        risk_manager.daily_stats['circuit_breaker_tripped'] = True
        risk_manager.daily_stats['circuit_breaker_reason'] = "5 losses"
        risk_manager._save_state()

        # Load fresh instance
        risk_manager2 = RiskManager(state_dir=temp_state_dir)

        assert risk_manager2.daily_stats['circuit_breaker_tripped'] is True
        assert risk_manager2.daily_stats['circuit_breaker_reason'] == "5 losses"

    def test_circuit_breaker_persists_across_day_boundaries(self, temp_state_dir):
        """Test that circuit breaker remains active across day reset."""
        risk_manager = RiskManager(state_dir=temp_state_dir)

        # Trip circuit breaker
        risk_manager.daily_stats['circuit_breaker_tripped'] = True
        risk_manager.daily_stats['circuit_breaker_reason'] = "Consecutive losses"
        risk_manager._save_state()

        # Simulate day reset
        risk_manager.reset_daily_stats()

        # Circuit breaker should still be active
        assert risk_manager.daily_stats['circuit_breaker_tripped'] is True
        assert risk_manager.daily_stats['trades_today'] == 0  # Daily stats reset
        assert risk_manager.daily_stats['pnl_today'] == 0.0  # Daily stats reset

    def test_consecutive_losses_reset_on_new_day(self, temp_state_dir):
        """Test that consecutive loss counter resets on new day."""
        risk_manager = RiskManager(state_dir=temp_state_dir)

        # Record losses but don't trip circuit breaker
        risk_manager.daily_stats['consecutive_losses'] = 3
        risk_manager._save_state()

        # Reset for new day
        risk_manager.reset_daily_stats()

        # Consecutive losses should be reset (since circuit breaker not tripped)
        assert risk_manager.daily_stats['consecutive_losses'] == 0


class TestConsecutiveLossTracking:
    """Test consecutive loss counter behavior."""

    def test_multiple_losses_increment_counter(self, risk_manager):
        """Test that multiple losses increment the counter."""
        assert risk_manager.daily_stats['consecutive_losses'] == 0

        risk_manager.record_trade_result(-5.0)
        assert risk_manager.daily_stats['consecutive_losses'] == 1

        risk_manager.record_trade_result(-10.0)
        assert risk_manager.daily_stats['consecutive_losses'] == 2

        risk_manager.record_trade_result(-3.0)
        assert risk_manager.daily_stats['consecutive_losses'] == 3

    def test_small_win_resets_counter(self, risk_manager):
        """Test that even a small win resets the counter."""
        # Record losses
        for _ in range(4):
            risk_manager.record_trade_result(-10.0)

        assert risk_manager.daily_stats['consecutive_losses'] == 4

        # Small win (even $0.01)
        risk_manager.record_trade_result(0.01)

        assert risk_manager.daily_stats['consecutive_losses'] == 0

    def test_breakeven_trade_resets_counter(self, risk_manager):
        """Test that breakeven (0.0 PnL) counts as non-loss."""
        risk_manager.record_trade_result(-10.0)
        risk_manager.record_trade_result(-5.0)
        assert risk_manager.daily_stats['consecutive_losses'] == 2

        # Breakeven
        risk_manager.record_trade_result(0.0)

        assert risk_manager.daily_stats['consecutive_losses'] == 0


class TestCircuitBreakerEdgeCases:
    """Test edge cases and error scenarios."""

    def test_circuit_breaker_with_zero_max_losses(self, risk_manager, sample_position):
        """Test circuit breaker with max_consecutive_losses = 0."""
        portfolio_state = {'total_value': 1000.0, 'positions': {}}
        global_limits = {'max_consecutive_losses': 0}

        # Even zero losses should trip immediately
        allowed, reason = risk_manager.check_trade_allowed(
            sample_position,
            portfolio_state,
            global_limits
        )

        # With 0 max losses and 0 consecutive losses, should trip
        assert not allowed
        assert "CIRCUIT BREAKER" in reason

    def test_override_when_not_tripped_does_nothing(self, risk_manager):
        """Test that override when not tripped doesn't cause issues."""
        # Circuit breaker not tripped
        assert risk_manager.daily_stats.get('circuit_breaker_tripped', False) is False

        # Override anyway (shouldn't crash)
        risk_manager.captain_override_circuit_breaker(reason="Preventive reset")

        # Should still be not tripped
        assert risk_manager.daily_stats['circuit_breaker_tripped'] is False

    def test_circuit_breaker_reason_captured(self, risk_manager, sample_position):
        """Test that circuit breaker captures trigger reason."""
        portfolio_state = {'total_value': 1000.0, 'positions': {}}
        global_limits = {'max_consecutive_losses': 3}

        # Trip breaker
        for _ in range(3):
            risk_manager.record_trade_result(-10.0)

        risk_manager.check_trade_allowed(
            sample_position,
            portfolio_state,
            global_limits
        )

        # Reason should be captured
        assert risk_manager.daily_stats['circuit_breaker_reason'] is not None
        assert "Consecutive losses" in risk_manager.daily_stats['circuit_breaker_reason']


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
