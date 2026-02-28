"""
Market Regime Detector
Classifies current market state into one of 6 regimes.

Regimes:
- trending_bull: Strong upward trend with momentum
- trending_bear: Strong downward trend with momentum
- ranging_high_vol: Oscillating with high volatility
- ranging_low_vol: Oscillating with low volatility
- breakout_pending: Compression indicating potential breakout
- crash_recovery: Post-crash stabilization phase
"""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Tuple
import numpy as np
import pandas as pd


@dataclass
class RegimeDetection:
    """Result of regime detection analysis."""
    regime: str
    confidence: float
    supporting_factors: List[dict]
    timestamp: datetime


class RegimeDetector:
    """
    Detects market regime using multiple technical indicators.

    Philosophy: Use simple, robust indicators. Avoid overfitting.
    Confidence comes from agreement between multiple signals.
    """

    def __init__(self):
        self.regimes = [
            "trending_bull",
            "trending_bear",
            "ranging_high_vol",
            "ranging_low_vol",
            "breakout_pending",
            "crash_recovery"
        ]

    def detect(self, ohlcv: pd.DataFrame) -> RegimeDetection:
        """
        Detect current market regime.

        Args:
            ohlcv: DataFrame with columns [timestamp, open, high, low, close, volume]
                   Expected to have at least 200 rows for reliable detection

        Returns:
            RegimeDetection with regime classification and confidence
        """
        if len(ohlcv) < 200:
            return RegimeDetection(
                regime="unknown",
                confidence=0.0,
                supporting_factors=[{
                    "factor": "insufficient_data",
                    "explanation": f"Need 200+ candles, got {len(ohlcv)}",
                    "confidence": 1.0
                }],
                timestamp=datetime.utcnow()
            )

        # Calculate indicators
        trend_score, trend_factors = self._calculate_trend_score(ohlcv)
        range_score, range_factors = self._calculate_range_score(ohlcv)
        volatility_score, vol_factors = self._calculate_volatility_score(ohlcv)
        compression_score, comp_factors = self._calculate_compression_score(ohlcv)
        recovery_score, recovery_factors = self._calculate_recovery_score(ohlcv)

        # Score each regime
        scores = {
            "trending_bull": self._score_trending_bull(trend_score, volatility_score),
            "trending_bear": self._score_trending_bear(trend_score, volatility_score),
            "ranging_high_vol": self._score_ranging_high_vol(range_score, volatility_score),
            "ranging_low_vol": self._score_ranging_low_vol(range_score, volatility_score),
            "breakout_pending": compression_score,
            "crash_recovery": recovery_score
        }

        # Select highest scoring regime
        best_regime = max(scores, key=scores.get)
        confidence = scores[best_regime]

        # Gather supporting factors
        supporting_factors = []
        if "trending" in best_regime:
            supporting_factors.extend(trend_factors)
        if "ranging" in best_regime:
            supporting_factors.extend(range_factors)
        if "breakout" in best_regime:
            supporting_factors.extend(comp_factors)
        if "recovery" in best_regime:
            supporting_factors.extend(recovery_factors)

        supporting_factors.extend(vol_factors)

        return RegimeDetection(
            regime=best_regime,
            confidence=confidence,
            supporting_factors=supporting_factors,
            timestamp=datetime.utcnow()
        )

    def _calculate_trend_score(self, ohlcv: pd.DataFrame) -> Tuple[float, List[dict]]:
        """
        Calculate trend strength and direction.
        Returns: (score, factors)
            score: -1.0 (strong bear) to +1.0 (strong bull)
        """
        close = ohlcv['close'].values

        # EMA analysis
        ema_20 = self._ema(close, 20)
        ema_50 = self._ema(close, 50)
        ema_200 = self._ema(close, 200)

        current_price = close[-1]

        # Trend strength: Distance from EMAs
        above_ema20 = (current_price - ema_20[-1]) / ema_20[-1]
        above_ema50 = (current_price - ema_50[-1]) / ema_50[-1]
        above_ema200 = (current_price - ema_200[-1]) / ema_200[-1]

        # EMA alignment (bullish: 20 > 50 > 200, bearish: opposite)
        ema_alignment = 0.0
        if ema_20[-1] > ema_50[-1] > ema_200[-1]:
            ema_alignment = 1.0  # Bullish
        elif ema_20[-1] < ema_50[-1] < ema_200[-1]:
            ema_alignment = -1.0  # Bearish

        # Price momentum (20-period rate of change)
        momentum = (close[-1] - close[-20]) / close[-20]

        # Combine signals
        trend_score = (
            0.3 * np.sign(above_ema20) * min(abs(above_ema20), 0.1) * 10 +
            0.3 * np.sign(above_ema50) * min(abs(above_ema50), 0.1) * 10 +
            0.2 * ema_alignment +
            0.2 * np.sign(momentum) * min(abs(momentum), 0.2) * 5
        )

        # Clamp to [-1, 1]
        trend_score = np.clip(trend_score, -1.0, 1.0)

        factors = [
            {
                "factor": "ema_position",
                "explanation": f"Price {above_ema20*100:.1f}% from EMA20, {above_ema50*100:.1f}% from EMA50",
                "confidence": min(abs(above_ema20) * 10, 1.0)
            },
            {
                "factor": "ema_alignment",
                "explanation": "Bullish" if ema_alignment > 0 else "Bearish" if ema_alignment < 0 else "Mixed",
                "confidence": abs(ema_alignment)
            },
            {
                "factor": "momentum",
                "explanation": f"{momentum*100:.1f}% change over 20 periods",
                "confidence": min(abs(momentum) * 5, 1.0)
            }
        ]

        return trend_score, factors

    def _calculate_range_score(self, ohlcv: pd.DataFrame) -> Tuple[float, List[dict]]:
        """
        Calculate ranging behavior strength.
        Returns: (score, factors)
            score: 0.0 (not ranging) to 1.0 (strong range)
        """
        close = ohlcv['close'].values
        high = ohlcv['high'].values
        low = ohlcv['low'].values

        # Look back 48 periods (48 hours for hourly data)
        lookback = min(48, len(close))
        recent_high = np.max(high[-lookback:])
        recent_low = np.min(low[-lookback:])
        recent_close = close[-lookback:]

        # Calculate range width (validate to prevent division by zero)
        if recent_low <= 0:
            # Invalid price data
            return 0.0, [{
                "factor": "invalid_price_data",
                "explanation": "Price data contains zero or negative values",
                "confidence": 0.0
            }]

        range_width = (recent_high - recent_low) / recent_low

        # Check if price is oscillating (testing both high and low)
        touched_high = np.max(high[-lookback:]) / recent_high > 0.98
        touched_low = np.min(low[-lookback:]) / recent_low < 1.02

        # Calculate price position within range (handle flat market)
        if recent_high == recent_low:
            # Flat market - no range
            current_position = 0.5
        else:
            current_position = (close[-1] - recent_low) / (recent_high - recent_low)

        # Measure choppiness (how much it oscillates)
        # Fixed: Start at i=1 to avoid accessing recent_close[-1] incorrectly
        direction_changes = 0
        for i in range(1, len(recent_close) - 1):
            if (recent_close[i+1] - recent_close[i]) * (recent_close[i] - recent_close[i-1]) < 0:
                direction_changes += 1

        choppiness = direction_changes / (lookback - 1)

        # Score ranging: High choppiness + touched both boundaries + tight range
        range_score = 0.0
        if touched_high and touched_low:
            range_score += 0.4

        if choppiness > 0.4:  # Frequent direction changes
            range_score += 0.3

        if range_width < 0.05:  # Less than 5% range
            range_score += 0.3

        range_score = min(range_score, 1.0)

        factors = [
            {
                "factor": "range_boundaries",
                "explanation": f"Price between ${recent_low:.2f} - ${recent_high:.2f} ({range_width*100:.1f}% range)",
                "confidence": 1.0 if (touched_high and touched_low) else 0.5
            },
            {
                "factor": "choppiness",
                "explanation": f"{direction_changes} direction changes in {lookback} periods ({choppiness*100:.0f}%)",
                "confidence": min(choppiness * 2, 1.0)
            }
        ]

        return range_score, factors

    def _calculate_volatility_score(self, ohlcv: pd.DataFrame) -> Tuple[float, List[dict]]:
        """
        Calculate volatility level (not regime, just measurement).
        Returns: (score, factors)
            score: 0.0 (low) to 1.0 (high)
        """
        high = ohlcv['high'].values
        low = ohlcv['low'].values
        close = ohlcv['close'].values

        # Average True Range (ATR) - 14 period
        atr = self._calculate_atr(high, low, close, period=14)
        current_atr = atr[-1]

        # ATR as percentage of price
        atr_percent = current_atr / close[-1]

        # Historical percentile (30-day lookback)
        lookback = min(30, len(atr))
        atr_percentile = (np.sum(atr[-lookback:] < current_atr) / lookback) * 100

        # Bollinger Band width
        bb_upper, bb_lower = self._bollinger_bands(close, period=20, std_dev=2)
        bb_width = (bb_upper[-1] - bb_lower[-1]) / close[-1]

        # Normalize volatility score (0-1)
        # High volatility: ATR > 3% of price OR in top 70th percentile
        volatility_score = 0.0
        if atr_percent > 0.03:
            volatility_score += 0.5
        if atr_percentile > 70:
            volatility_score += 0.5

        volatility_score = min(volatility_score, 1.0)

        factors = [
            {
                "factor": "atr_level",
                "explanation": f"ATR at {atr_percentile:.0f}th percentile ({atr_percent*100:.2f}% of price)",
                "confidence": 0.9
            },
            {
                "factor": "bollinger_width",
                "explanation": f"Bollinger Bands width: {bb_width*100:.2f}%",
                "confidence": 0.8
            }
        ]

        return volatility_score, factors

    def _calculate_compression_score(self, ohlcv: pd.DataFrame) -> Tuple[float, List[dict]]:
        """
        Calculate compression (squeeze) score indicating potential breakout.
        Returns: (score, factors)
        """
        close = ohlcv['close'].values
        volume = ohlcv['volume'].values

        # Bollinger Bands
        bb_upper, bb_lower = self._bollinger_bands(close, period=20, std_dev=2)
        bb_width = (bb_upper[-1] - bb_lower[-1]) / close[-1]

        # Is BB width contracting?
        bb_width_ma = np.mean([(bb_upper[i] - bb_lower[i]) / close[i] for i in range(-20, 0)])
        bb_contracting = bb_width < bb_width_ma * 0.8

        # Volume analysis (decreasing volume often precedes breakout)
        recent_volume = np.mean(volume[-10:])
        avg_volume = np.mean(volume[-50:])
        volume_decreasing = recent_volume < avg_volume * 0.9

        # Compression score
        compression_score = 0.0
        if bb_contracting:
            compression_score += 0.6
        if volume_decreasing:
            compression_score += 0.4

        factors = [
            {
                "factor": "bollinger_squeeze",
                "explanation": "Bollinger Bands contracting" if bb_contracting else "Normal width",
                "confidence": 0.8 if bb_contracting else 0.2
            },
            {
                "factor": "volume_pattern",
                "explanation": f"Volume {(recent_volume/avg_volume - 1)*100:.0f}% vs average",
                "confidence": 0.7 if volume_decreasing else 0.3
            }
        ]

        return compression_score, factors

    def _calculate_recovery_score(self, ohlcv: pd.DataFrame) -> Tuple[float, List[dict]]:
        """
        Detect crash recovery phase (sharp drop followed by stabilization).
        Returns: (score, factors)
        """
        close = ohlcv['close'].values

        # Look for sharp drop in recent past (20-50 periods ago)
        lookback_start = min(50, len(close))
        lookback_end = min(20, len(close))

        # Maximum drawdown in lookback window
        peak = np.max(close[-lookback_start:-lookback_end])
        trough = np.min(close[-lookback_start:-lookback_end])
        drawdown = (peak - trough) / peak

        # Recent stabilization (low volatility in last 20 periods)
        recent_volatility = np.std(close[-20:]) / np.mean(close[-20:])

        # Recovery score: Large drawdown + recent stabilization
        recovery_score = 0.0
        if drawdown > 0.15:  # >15% drop
            recovery_score += 0.6
            if recent_volatility < 0.02:  # Low recent volatility
                recovery_score += 0.4

        factors = [
            {
                "factor": "recent_drawdown",
                "explanation": f"{drawdown*100:.1f}% drop from ${peak:.2f} to ${trough:.2f}",
                "confidence": min(drawdown * 3, 1.0)
            },
            {
                "factor": "stabilization",
                "explanation": f"Recent volatility: {recent_volatility*100:.2f}%",
                "confidence": 1.0 - min(recent_volatility * 50, 1.0)
            }
        ]

        return recovery_score, factors

    def _score_trending_bull(self, trend_score: float, volatility_score: float) -> float:
        """Score for trending_bull regime."""
        if trend_score > 0.5:  # Strong uptrend
            return 0.7 + 0.3 * trend_score
        return 0.0

    def _score_trending_bear(self, trend_score: float, volatility_score: float) -> float:
        """Score for trending_bear regime."""
        if trend_score < -0.5:  # Strong downtrend
            return 0.7 + 0.3 * abs(trend_score)
        return 0.0

    def _score_ranging_high_vol(self, range_score: float, volatility_score: float) -> float:
        """Score for ranging_high_vol regime."""
        if range_score > 0.6 and volatility_score > 0.5:
            return 0.5 * range_score + 0.5 * volatility_score
        return 0.0

    def _score_ranging_low_vol(self, range_score: float, volatility_score: float) -> float:
        """Score for ranging_low_vol regime."""
        if range_score > 0.6 and volatility_score < 0.5:
            return 0.7 * range_score + 0.3 * (1.0 - volatility_score)
        return 0.0

    # Utility functions

    def _ema(self, data: np.ndarray, period: int) -> np.ndarray:
        """Calculate Exponential Moving Average."""
        ema = np.zeros_like(data)
        ema[0] = data[0]
        multiplier = 2.0 / (period + 1)

        for i in range(1, len(data)):
            ema[i] = (data[i] - ema[i-1]) * multiplier + ema[i-1]

        return ema

    def _calculate_atr(self, high: np.ndarray, low: np.ndarray, close: np.ndarray, period: int = 14) -> np.ndarray:
        """Calculate Average True Range."""
        tr = np.zeros(len(close))

        for i in range(1, len(close)):
            hl = high[i] - low[i]
            hc = abs(high[i] - close[i-1])
            lc = abs(low[i] - close[i-1])
            tr[i] = max(hl, hc, lc)

        # ATR is EMA of TR
        atr = self._ema(tr, period)
        return atr

    def _bollinger_bands(self, data: np.ndarray, period: int = 20, std_dev: float = 2.0) -> Tuple[np.ndarray, np.ndarray]:
        """Calculate Bollinger Bands."""
        sma = np.convolve(data, np.ones(period) / period, mode='same')
        std = np.array([np.std(data[max(0, i-period+1):i+1]) for i in range(len(data))])

        upper_band = sma + (std_dev * std)
        lower_band = sma - (std_dev * std)

        return upper_band, lower_band
