"""
Unit Tests for OHLCV Data Validation (HIGH-9)

Tests the comprehensive OHLCV data validation added in Sprint 2 to prevent
corrupt or invalid market data from entering the analysis pipeline.
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from sil_orchestrator import SILOrchestrator


@pytest.fixture
def valid_ohlcv_data():
    """Create valid OHLCV DataFrame for testing."""
    timestamps = [datetime.utcnow() - timedelta(hours=i) for i in range(30)]
    data = {
        'timestamp': timestamps,
        'open': [50000.0 + i * 100 for i in range(30)],
        'high': [50500.0 + i * 100 for i in range(30)],
        'low': [49500.0 + i * 100 for i in range(30)],
        'close': [50200.0 + i * 100 for i in range(30)],
        'volume': [100.0 + i * 5 for i in range(30)]
    }
    return pd.DataFrame(data)


@pytest.fixture
def sil():
    """Create SILOrchestrator instance for testing."""
    return SILOrchestrator(enable_memory=False, enable_transparency=False)


class TestOHLCVValidationBasics:
    """Test basic OHLCV validation rules."""

    def test_valid_data_passes(self, sil, valid_ohlcv_data):
        """Test that valid OHLCV data passes validation."""
        error = sil._validate_ohlcv_data(valid_ohlcv_data)
        assert error is None, f"Valid data should pass validation, got: {error}"

    def test_empty_dataframe_rejected(self, sil):
        """Test that empty DataFrame is rejected."""
        empty_df = pd.DataFrame()
        error = sil._validate_ohlcv_data(empty_df)
        assert error is not None
        assert "empty" in error.lower()

    def test_none_dataframe_rejected(self, sil):
        """Test that None DataFrame is rejected."""
        error = sil._validate_ohlcv_data(None)
        assert error is not None
        assert "empty" in error.lower()


class TestOHLCVSchemaValidation:
    """Test schema and column validation."""

    def test_missing_timestamp_rejected(self, sil, valid_ohlcv_data):
        """Test that missing timestamp column is rejected."""
        df = valid_ohlcv_data.drop(columns=['timestamp'])
        error = sil._validate_ohlcv_data(df)
        assert error is not None
        assert "Missing required columns" in error
        assert "timestamp" in error

    def test_missing_ohlc_columns_rejected(self, sil, valid_ohlcv_data):
        """Test that missing OHLC columns are rejected."""
        # Missing 'open'
        df = valid_ohlcv_data.drop(columns=['open'])
        error = sil._validate_ohlcv_data(df)
        assert error is not None
        assert "open" in error

        # Missing 'high'
        df = valid_ohlcv_data.drop(columns=['high'])
        error = sil._validate_ohlcv_data(df)
        assert error is not None
        assert "high" in error

        # Missing 'low'
        df = valid_ohlcv_data.drop(columns=['low'])
        error = sil._validate_ohlcv_data(df)
        assert error is not None
        assert "low" in error

        # Missing 'close'
        df = valid_ohlcv_data.drop(columns=['close'])
        error = sil._validate_ohlcv_data(df)
        assert error is not None
        assert "close" in error

    def test_missing_volume_rejected(self, sil, valid_ohlcv_data):
        """Test that missing volume column is rejected."""
        df = valid_ohlcv_data.drop(columns=['volume'])
        error = sil._validate_ohlcv_data(df)
        assert error is not None
        assert "volume" in error

    def test_insufficient_rows_rejected(self, sil):
        """Test that data with < 20 rows is rejected."""
        # Create data with only 19 rows
        timestamps = [datetime.utcnow() - timedelta(hours=i) for i in range(19)]
        data = {
            'timestamp': timestamps,
            'open': [50000.0] * 19,
            'high': [50500.0] * 19,
            'low': [49500.0] * 19,
            'close': [50200.0] * 19,
            'volume': [100.0] * 19
        }
        df = pd.DataFrame(data)

        error = sil._validate_ohlcv_data(df)
        assert error is not None
        assert "Insufficient data" in error
        assert "19" in error

    def test_exactly_20_rows_accepted(self, sil):
        """Test that data with exactly 20 rows (minimum) is accepted."""
        timestamps = [datetime.utcnow() - timedelta(hours=i) for i in range(20)]
        data = {
            'timestamp': timestamps,
            'open': [50000.0] * 20,
            'high': [50500.0] * 20,
            'low': [49500.0] * 20,
            'close': [50200.0] * 20,
            'volume': [100.0] * 20
        }
        df = pd.DataFrame(data)

        error = sil._validate_ohlcv_data(df)
        assert error is None, f"20 rows should be accepted (minimum), got: {error}"


class TestOHLCVDataQuality:
    """Test data quality validation (NaN, types, values)."""

    def test_nan_in_open_rejected(self, sil, valid_ohlcv_data):
        """Test that NaN values in open column are rejected."""
        df = valid_ohlcv_data.copy()
        df.loc[5, 'open'] = np.nan
        error = sil._validate_ohlcv_data(df)
        assert error is not None
        assert "NaN" in error
        assert "open" in error

    def test_nan_in_high_rejected(self, sil, valid_ohlcv_data):
        """Test that NaN values in high column are rejected."""
        df = valid_ohlcv_data.copy()
        df.loc[10, 'high'] = np.nan
        error = sil._validate_ohlcv_data(df)
        assert error is not None
        assert "NaN" in error
        assert "high" in error

    def test_nan_in_low_rejected(self, sil, valid_ohlcv_data):
        """Test that NaN values in low column are rejected."""
        df = valid_ohlcv_data.copy()
        df.loc[3, 'low'] = np.nan
        error = sil._validate_ohlcv_data(df)
        assert error is not None
        assert "NaN" in error
        assert "low" in error

    def test_nan_in_close_rejected(self, sil, valid_ohlcv_data):
        """Test that NaN values in close column are rejected."""
        df = valid_ohlcv_data.copy()
        df.loc[15, 'close'] = np.nan
        error = sil._validate_ohlcv_data(df)
        assert error is not None
        assert "NaN" in error
        assert "close" in error

    def test_non_numeric_data_rejected(self, sil, valid_ohlcv_data):
        """Test that non-numeric data types are rejected."""
        df = valid_ohlcv_data.copy()
        df['open'] = df['open'].astype(str)  # Convert to string
        error = sil._validate_ohlcv_data(df)
        assert error is not None
        assert "numeric" in error.lower()
        assert "open" in error

    def test_negative_price_rejected(self, sil, valid_ohlcv_data):
        """Test that negative prices are rejected."""
        df = valid_ohlcv_data.copy()
        df.loc[5, 'close'] = -100.0
        error = sil._validate_ohlcv_data(df)
        assert error is not None
        assert "Negative values" in error
        assert "close" in error

    def test_negative_volume_rejected(self, sil, valid_ohlcv_data):
        """Test that negative volume is rejected."""
        df = valid_ohlcv_data.copy()
        df.loc[8, 'volume'] = -50.0
        error = sil._validate_ohlcv_data(df)
        assert error is not None
        assert "Negative values" in error
        assert "volume" in error


class TestOHLCRelationships:
    """Test OHLC relationship validation."""

    def test_high_less_than_low_rejected(self, sil, valid_ohlcv_data):
        """Test that high < low is rejected."""
        df = valid_ohlcv_data.copy()
        df.loc[10, 'high'] = 49000.0
        df.loc[10, 'low'] = 50000.0  # Low > high (invalid)
        error = sil._validate_ohlcv_data(df)
        assert error is not None
        assert "Invalid OHLC relationships" in error

    def test_high_less_than_open_rejected(self, sil, valid_ohlcv_data):
        """Test that high < open is rejected."""
        df = valid_ohlcv_data.copy()
        df.loc[5, 'high'] = 48000.0
        df.loc[5, 'open'] = 50000.0  # Open > high (invalid)
        error = sil._validate_ohlcv_data(df)
        assert error is not None
        assert "Invalid OHLC relationships" in error

    def test_high_less_than_close_rejected(self, sil, valid_ohlcv_data):
        """Test that high < close is rejected."""
        df = valid_ohlcv_data.copy()
        df.loc[7, 'high'] = 48000.0
        df.loc[7, 'close'] = 51000.0  # Close > high (invalid)
        error = sil._validate_ohlcv_data(df)
        assert error is not None
        assert "Invalid OHLC relationships" in error

    def test_low_greater_than_open_rejected(self, sil, valid_ohlcv_data):
        """Test that low > open is rejected."""
        df = valid_ohlcv_data.copy()
        df.loc[12, 'low'] = 52000.0
        df.loc[12, 'open'] = 50000.0  # Low > open (invalid)
        error = sil._validate_ohlcv_data(df)
        assert error is not None
        assert "Invalid OHLC relationships" in error

    def test_low_greater_than_close_rejected(self, sil, valid_ohlcv_data):
        """Test that low > close is rejected."""
        df = valid_ohlcv_data.copy()
        df.loc[3, 'low'] = 52000.0
        df.loc[3, 'close'] = 50000.0  # Low > close (invalid)
        error = sil._validate_ohlcv_data(df)
        assert error is not None
        assert "Invalid OHLC relationships" in error

    def test_valid_doji_candle_accepted(self, sil, valid_ohlcv_data):
        """Test that valid doji candle (open=close, within high/low) is accepted."""
        df = valid_ohlcv_data.copy()
        df.loc[5, 'open'] = 50000.0
        df.loc[5, 'close'] = 50000.0  # Doji: open = close
        df.loc[5, 'high'] = 50100.0
        df.loc[5, 'low'] = 49900.0
        error = sil._validate_ohlcv_data(df)
        assert error is None, f"Valid doji should be accepted, got: {error}"


class TestOHLCVEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_zero_volume_accepted(self, sil, valid_ohlcv_data):
        """Test that zero volume (no trading) is accepted."""
        df = valid_ohlcv_data.copy()
        df.loc[10, 'volume'] = 0.0
        error = sil._validate_ohlcv_data(df)
        assert error is None, "Zero volume should be accepted (quiet period)"

    def test_all_prices_equal_accepted(self, sil):
        """Test that all prices equal (flat market) is accepted."""
        timestamps = [datetime.utcnow() - timedelta(hours=i) for i in range(25)]
        data = {
            'timestamp': timestamps,
            'open': [50000.0] * 25,
            'high': [50000.0] * 25,
            'low': [50000.0] * 25,
            'close': [50000.0] * 25,
            'volume': [100.0] * 25
        }
        df = pd.DataFrame(data)
        error = sil._validate_ohlcv_data(df)
        assert error is None, "Flat market (all prices equal) should be accepted"

    def test_multiple_invalid_rows_reported(self, sil, valid_ohlcv_data):
        """Test that multiple invalid rows are detected."""
        df = valid_ohlcv_data.copy()
        # Create multiple invalid rows
        df.loc[5, 'high'] = 48000.0
        df.loc[5, 'low'] = 50000.0  # Invalid
        df.loc[10, 'high'] = 47000.0
        df.loc[10, 'open'] = 50000.0  # Invalid
        error = sil._validate_ohlcv_data(df)
        assert error is not None
        assert "Invalid OHLC relationships" in error


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
