"""
Sentiment Synthesizer
Aggregates market signals into coherent sentiment assessment.

Sentiment Components:
- Order book pressure (bid/ask imbalance)
- Volume trend (accumulation vs distribution)
- Price momentum (directional strength)
- Market structure (higher highs/lower lows)
"""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Dict
import numpy as np
import pandas as pd


@dataclass
class SentimentAnalysis:
    """Result of sentiment synthesis."""
    direction: str  # "bullish", "bearish", "neutral", "neutral_bullish", "neutral_bearish"
    confidence: float  # 0.0 to 1.0
    signals: Dict[str, float]  # Individual signal contributions
    supporting_factors: List[dict]
    timestamp: datetime


class SentimentSynthesizer:
    """
    Synthesizes market sentiment from multiple signals.

    Philosophy: Sentiment is not binary—it's a spectrum with confidence levels.
    We aggregate multiple independent signals to reduce false positives.
    """

    def synthesize(self, ohlcv: pd.DataFrame, orderbook: dict = None) -> SentimentAnalysis:
        """
        Synthesize market sentiment.

        Args:
            ohlcv: DataFrame with [timestamp, open, high, low, close, volume]
            orderbook: Optional dict with 'bids' and 'asks' for order book analysis

        Returns:
            SentimentAnalysis with direction and confidence
        """
        if len(ohlcv) < 20:
            return SentimentAnalysis(
                direction="neutral",
                confidence=0.0,
                signals={},
                supporting_factors=[{
                    "factor": "insufficient_data",
                    "explanation": "Need 20+ candles for sentiment analysis",
                    "confidence": 1.0
                }],
                timestamp=datetime.utcnow()
            )

        signals = {}
        factors = []

        # 1. Order book pressure (if available)
        if orderbook:
            ob_pressure, ob_factor = self._analyze_orderbook(orderbook)
            signals["orderbook_pressure"] = ob_pressure
            factors.append(ob_factor)

        # 2. Volume trend
        volume_signal, volume_factor = self._analyze_volume(ohlcv)
        signals["volume_trend"] = volume_signal
        factors.append(volume_factor)

        # 3. Price momentum
        momentum_signal, momentum_factor = self._analyze_momentum(ohlcv)
        signals["price_momentum"] = momentum_signal
        factors.append(momentum_factor)

        # 4. Market structure
        structure_signal, structure_factor = self._analyze_market_structure(ohlcv)
        signals["market_structure"] = structure_signal
        factors.append(structure_factor)

        # 5. Money flow
        mfi_signal, mfi_factor = self._analyze_money_flow(ohlcv)
        signals["money_flow"] = mfi_signal
        factors.append(mfi_factor)

        # Aggregate signals
        total_signal = sum(signals.values())
        num_signals = len(signals)
        avg_signal = total_signal / num_signals if num_signals > 0 else 0.0

        # Calculate confidence (agreement between signals)
        signal_values = list(signals.values())
        signal_std = np.std(signal_values) if len(signal_values) > 1 else 1.0
        confidence = 1.0 - min(signal_std, 1.0)  # High agreement = high confidence

        # Classify direction
        if avg_signal > 0.3:
            direction = "bullish"
        elif avg_signal > 0.1:
            direction = "neutral_bullish"
        elif avg_signal < -0.3:
            direction = "bearish"
        elif avg_signal < -0.1:
            direction = "neutral_bearish"
        else:
            direction = "neutral"

        return SentimentAnalysis(
            direction=direction,
            confidence=confidence,
            signals=signals,
            supporting_factors=factors,
            timestamp=datetime.utcnow()
        )

    def _analyze_orderbook(self, orderbook: dict) -> tuple:
        """
        Analyze order book for bid/ask pressure.
        Returns: (signal, factor)
            signal: -1.0 (sell pressure) to +1.0 (buy pressure)
        """
        bids = orderbook.get('bids', [])
        asks = orderbook.get('asks', [])

        if not bids or not asks:
            return 0.0, {
                "factor": "orderbook_pressure",
                "explanation": "No order book data available",
                "confidence": 0.0
            }

        # Calculate total volume in top N levels
        n_levels = min(10, len(bids), len(asks))

        bid_volume = sum([float(bid[1]) for bid in bids[:n_levels]])
        ask_volume = sum([float(ask[1]) for ask in asks[:n_levels]])

        # Pressure ratio
        if bid_volume + ask_volume == 0:
            pressure = 0.0
        else:
            pressure = (bid_volume - ask_volume) / (bid_volume + ask_volume)

        explanation = f"Bid volume: {bid_volume:.4f}, Ask volume: {ask_volume:.4f}"
        if pressure > 0.1:
            explanation += " (buy pressure)"
        elif pressure < -0.1:
            explanation += " (sell pressure)"
        else:
            explanation += " (balanced)"

        return pressure, {
            "factor": "orderbook_pressure",
            "explanation": explanation,
            "confidence": 0.7
        }

    def _analyze_volume(self, ohlcv: pd.DataFrame) -> tuple:
        """
        Analyze volume trend for accumulation/distribution.
        Returns: (signal, factor)
        """
        close = ohlcv['close'].values
        volume = ohlcv['volume'].values

        # Volume trend (recent vs historical average)
        recent_volume = np.mean(volume[-10:])
        avg_volume = np.mean(volume[-30:])

        volume_ratio = (recent_volume / avg_volume) - 1.0  # % change

        # Price direction
        price_change = (close[-1] - close[-10]) / close[-10]

        # Signal: Rising price + rising volume = bullish
        #         Falling price + rising volume = bearish
        #         Rising volume alone = neutral (inconclusive)
        if volume_ratio > 0.2:  # Volume increasing
            if price_change > 0.02:
                signal = 0.6  # Bullish accumulation
            elif price_change < -0.02:
                signal = -0.6  # Bearish distribution
            else:
                signal = 0.0  # Neutral
        else:
            signal = 0.0  # No strong volume signal

        explanation = f"Volume {volume_ratio*100:+.0f}% vs 30-day average, price {price_change*100:+.1f}%"

        return signal, {
            "factor": "volume_trend",
            "explanation": explanation,
            "confidence": min(abs(volume_ratio), 0.8)
        }

    def _analyze_momentum(self, ohlcv: pd.DataFrame) -> tuple:
        """
        Analyze price momentum.
        Returns: (signal, factor)
        """
        close = ohlcv['close'].values

        # Rate of change (10-period)
        roc_10 = (close[-1] - close[-10]) / close[-10]

        # Momentum direction
        if roc_10 > 0.05:
            signal = 0.7
            strength = "strong upward"
        elif roc_10 > 0.02:
            signal = 0.4
            strength = "moderate upward"
        elif roc_10 < -0.05:
            signal = -0.7
            strength = "strong downward"
        elif roc_10 < -0.02:
            signal = -0.4
            strength = "moderate downward"
        else:
            signal = 0.0
            strength = "weak/neutral"

        return signal, {
            "factor": "price_momentum",
            "explanation": f"{roc_10*100:+.1f}% change over 10 periods ({strength})",
            "confidence": min(abs(roc_10) * 10, 1.0)
        }

    def _analyze_market_structure(self, ohlcv: pd.DataFrame) -> tuple:
        """
        Analyze market structure (higher highs/lower lows).
        Returns: (signal, factor)
        """
        high = ohlcv['high'].values
        low = ohlcv['low'].values

        # Recent highs/lows
        recent_high = np.max(high[-10:])
        recent_low = np.min(low[-10:])

        # Previous highs/lows
        prev_high = np.max(high[-20:-10])
        prev_low = np.min(low[-20:-10])

        # Structure analysis
        higher_high = recent_high > prev_high
        higher_low = recent_low > prev_low
        lower_high = recent_high < prev_high
        lower_low = recent_low < prev_low

        # Signal
        if higher_high and higher_low:
            signal = 0.6  # Bullish structure
            structure = "higher highs and higher lows (bullish)"
        elif lower_high and lower_low:
            signal = -0.6  # Bearish structure
            structure = "lower highs and lower lows (bearish)"
        elif higher_high and lower_low:
            signal = 0.0  # Expanding range (neutral)
            structure = "expanding range (neutral)"
        else:
            signal = 0.0  # Contracting range (neutral)
            structure = "contracting range (neutral)"

        return signal, {
            "factor": "market_structure",
            "explanation": structure,
            "confidence": 0.7
        }

    def _analyze_money_flow(self, ohlcv: pd.DataFrame) -> tuple:
        """
        Analyze Money Flow Index (MFI) - volume-weighted RSI.
        Returns: (signal, factor)
        """
        high = ohlcv['high'].values
        low = ohlcv['low'].values
        close = ohlcv['close'].values
        volume = ohlcv['volume'].values

        if len(close) < 15:
            return 0.0, {
                "factor": "money_flow",
                "explanation": "Insufficient data for MFI",
                "confidence": 0.0
            }

        # Typical price
        typical_price = (high + low + close) / 3

        # Money flow
        money_flow = typical_price * volume

        # Positive and negative money flow
        period = 14
        positive_flow = []
        negative_flow = []

        for i in range(1, len(typical_price)):
            if typical_price[i] > typical_price[i-1]:
                positive_flow.append(money_flow[i])
                negative_flow.append(0)
            else:
                positive_flow.append(0)
                negative_flow.append(money_flow[i])

        # MFI calculation
        if len(positive_flow) >= period:
            pos_mf = np.sum(positive_flow[-period:])
            neg_mf = np.sum(negative_flow[-period:])

            if neg_mf == 0:
                mfi = 100
            else:
                money_ratio = pos_mf / neg_mf
                mfi = 100 - (100 / (1 + money_ratio))

            # Signal based on MFI
            if mfi > 70:
                signal = -0.4  # Overbought (bearish)
                condition = "overbought"
            elif mfi < 30:
                signal = 0.4  # Oversold (bullish)
                condition = "oversold"
            else:
                signal = 0.0  # Neutral
                condition = "neutral"

            explanation = f"MFI: {mfi:.0f} ({condition})"
            confidence = 0.6
        else:
            signal = 0.0
            explanation = "Insufficient data for MFI calculation"
            confidence = 0.0

        return signal, {
            "factor": "money_flow",
            "explanation": explanation,
            "confidence": confidence
        }
