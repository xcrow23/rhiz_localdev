"""
Volatility Mapper
Maps current volatility environment into actionable classifications.

Classifications:
- expanding: Risk-off signal, volatility increasing
- contracting: Opportunity building, volatility decreasing
- explosive: Breakout or crash, extreme volatility
- stable: Normal conditions, typical volatility
"""

from dataclasses import dataclass
from datetime import datetime
from typing import List
import numpy as np
import pandas as pd


@dataclass
class VolatilityMapping:
    """Result of volatility mapping."""
    regime: str
    percentile: float  # Historical percentile (0-100)
    trend: str  # "expanding", "contracting", "stable"
    level: str  # "low", "normal", "high", "extreme"
    confidence: float
    supporting_factors: List[dict]
    timestamp: datetime


class VolatilityMapper:
    """
    Maps volatility into actionable regime classifications.

    Uses multiple volatility measures for robustness:
    - ATR (Average True Range)
    - Bollinger Band width
    - Historical volatility
    - Parkinson volatility (high-low range)
    """

    def map(self, ohlcv: pd.DataFrame) -> VolatilityMapping:
        """
        Map current volatility environment.

        Args:
            ohlcv: DataFrame with [timestamp, open, high, low, close, volume]

        Returns:
            VolatilityMapping with regime, trend, and confidence
        """
        if len(ohlcv) < 30:
            return VolatilityMapping(
                regime="unknown",
                percentile=50.0,
                trend="unknown",
                level="unknown",
                confidence=0.0,
                supporting_factors=[{
                    "factor": "insufficient_data",
                    "explanation": f"Need 30+ candles for volatility analysis",
                    "confidence": 1.0
                }],
                timestamp=datetime.utcnow()
            )

        # Calculate volatility metrics
        atr_percentile, atr_trend = self._calculate_atr_metrics(ohlcv)
        bb_width_percentile, bb_trend = self._calculate_bb_metrics(ohlcv)
        hv_percentile, hv_trend = self._calculate_historical_volatility(ohlcv)

        # Aggregate percentile
        avg_percentile = (atr_percentile + bb_width_percentile + hv_percentile) / 3

        # Aggregate trend
        trend_votes = {"expanding": 0, "contracting": 0, "stable": 0}
        for t in [atr_trend, bb_trend, hv_trend]:
            trend_votes[t] += 1

        dominant_trend = max(trend_votes, key=trend_votes.get)
        trend_confidence = trend_votes[dominant_trend] / 3

        # Classify level
        if avg_percentile < 20:
            level = "low"
            regime = "contracting" if dominant_trend == "contracting" else "stable"
        elif avg_percentile < 70:
            level = "normal"
            regime = "stable"
        elif avg_percentile < 90:
            level = "high"
            regime = "expanding" if dominant_trend == "expanding" else "stable"
        else:
            level = "extreme"
            regime = "explosive"

        # Build supporting factors
        supporting_factors = [
            {
                "factor": "atr_analysis",
                "explanation": f"ATR at {atr_percentile:.0f}th percentile, {atr_trend}",
                "confidence": 0.9
            },
            {
                "factor": "bollinger_analysis",
                "explanation": f"BB width at {bb_width_percentile:.0f}th percentile, {bb_trend}",
                "confidence": 0.85
            },
            {
                "factor": "historical_volatility",
                "explanation": f"HV at {hv_percentile:.0f}th percentile, {hv_trend}",
                "confidence": 0.8
            },
            {
                "factor": "regime_classification",
                "explanation": f"Volatility {level}, regime {regime}",
                "confidence": trend_confidence
            }
        ]

        return VolatilityMapping(
            regime=regime,
            percentile=avg_percentile,
            trend=dominant_trend,
            level=level,
            confidence=trend_confidence,
            supporting_factors=supporting_factors,
            timestamp=datetime.utcnow()
        )

    def _calculate_atr_metrics(self, ohlcv: pd.DataFrame) -> tuple:
        """Calculate ATR percentile and trend."""
        high = ohlcv['high'].values
        low = ohlcv['low'].values
        close = ohlcv['close'].values

        # ATR calculation
        atr = self._atr(high, low, close, period=14)
        atr_percent = (atr / close) * 100  # ATR as % of price

        # Historical percentile (30-day)
        lookback = min(30, len(atr))
        current_atr_pct = atr_percent[-1]
        percentile = (np.sum(atr_percent[-lookback:] < current_atr_pct) / lookback) * 100

        # Trend (is ATR expanding or contracting?)
        atr_ma = np.mean(atr_percent[-10:])
        atr_ma_prev = np.mean(atr_percent[-20:-10])

        if atr_ma > atr_ma_prev * 1.1:
            trend = "expanding"
        elif atr_ma < atr_ma_prev * 0.9:
            trend = "contracting"
        else:
            trend = "stable"

        return percentile, trend

    def _calculate_bb_metrics(self, ohlcv: pd.DataFrame) -> tuple:
        """Calculate Bollinger Band width percentile and trend."""
        close = ohlcv['close'].values

        # Bollinger Bands
        upper, lower = self._bollinger_bands(close, period=20, std_dev=2)
        bb_width = ((upper - lower) / close) * 100

        # Historical percentile
        lookback = min(30, len(bb_width))
        current_width = bb_width[-1]
        percentile = (np.sum(bb_width[-lookback:] < current_width) / lookback) * 100

        # Trend
        width_ma = np.mean(bb_width[-10:])
        width_ma_prev = np.mean(bb_width[-20:-10])

        if width_ma > width_ma_prev * 1.1:
            trend = "expanding"
        elif width_ma < width_ma_prev * 0.9:
            trend = "contracting"
        else:
            trend = "stable"

        return percentile, trend

    def _calculate_historical_volatility(self, ohlcv: pd.DataFrame) -> tuple:
        """Calculate historical volatility percentile and trend."""
        close = ohlcv['close'].values

        # Returns
        returns = np.diff(np.log(close))

        # Rolling volatility (20-period)
        window = 20
        rolling_vol = np.array([
            np.std(returns[max(0, i-window):i]) * np.sqrt(365) * 100  # Annualized %
            for i in range(1, len(returns))
        ])

        # Percentile
        lookback = min(30, len(rolling_vol))
        current_vol = rolling_vol[-1]
        percentile = (np.sum(rolling_vol[-lookback:] < current_vol) / lookback) * 100

        # Trend
        vol_ma = np.mean(rolling_vol[-10:])
        vol_ma_prev = np.mean(rolling_vol[-20:-10])

        if vol_ma > vol_ma_prev * 1.1:
            trend = "expanding"
        elif vol_ma < vol_ma_prev * 0.9:
            trend = "contracting"
        else:
            trend = "stable"

        return percentile, trend

    # Utility functions

    def _atr(self, high: np.ndarray, low: np.ndarray, close: np.ndarray, period: int = 14) -> np.ndarray:
        """Calculate Average True Range."""
        tr = np.zeros(len(close))

        for i in range(1, len(close)):
            hl = high[i] - low[i]
            hc = abs(high[i] - close[i-1])
            lc = abs(low[i] - close[i-1])
            tr[i] = max(hl, hc, lc)

        # Smooth with EMA
        atr = np.zeros_like(tr)
        atr[period-1] = np.mean(tr[:period])
        multiplier = 1.0 / period

        for i in range(period, len(tr)):
            atr[i] = (tr[i] - atr[i-1]) * multiplier + atr[i-1]

        return atr

    def _bollinger_bands(self, data: np.ndarray, period: int = 20, std_dev: float = 2.0) -> tuple:
        """Calculate Bollinger Bands."""
        sma = np.convolve(data, np.ones(period) / period, mode='same')
        std = np.array([np.std(data[max(0, i-period+1):i+1]) for i in range(len(data))])

        upper_band = sma + (std_dev * std)
        lower_band = sma - (std_dev * std)

        return upper_band, lower_band
