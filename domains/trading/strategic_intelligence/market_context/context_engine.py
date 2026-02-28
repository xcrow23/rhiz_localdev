"""
Market Context Engine
Main orchestrator combining regime detection, volatility mapping, and sentiment synthesis.

IMPORTANT: Crypto-specific calibration required!
Crypto markets are 5-10x more volatile than traditional markets.
Default thresholds are placeholders—must be tuned with real BTC data.
"""

from dataclasses import dataclass, asdict
from datetime import datetime
from typing import List, Dict, Optional
import pandas as pd

from market_context.regime_detector import RegimeDetector, RegimeDetection
from market_context.volatility_mapper import VolatilityMapper, VolatilityMapping
from market_context.sentiment_synthesizer import SentimentSynthesizer, SentimentAnalysis


@dataclass
class MarketContext:
    """
    Complete market context snapshot.

    Combines regime, volatility, and sentiment into unified view.
    """
    # Regime analysis
    regime: str
    regime_confidence: float
    regime_factors: List[dict]

    # Volatility analysis
    volatility_regime: str
    volatility_percentile: float
    volatility_level: str
    volatility_factors: List[dict]

    # Sentiment analysis
    sentiment_direction: str
    sentiment_confidence: float
    sentiment_signals: Dict[str, float]
    sentiment_factors: List[dict]

    # Metadata
    timestamp: datetime
    data_quality: str  # "excellent", "good", "marginal", "insufficient"
    warnings: List[str]

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)

    def to_trace_fe(self) -> List[dict]:
        """
        Convert to TRACE_FE format (SynLang transparency protocol).

        Returns list of factor explanations with confidence scores.
        """
        trace_factors = []

        # Regime factors
        for factor in self.regime_factors[:3]:  # Top 3 most confident
            trace_factors.append({
                "factor": f"regime_{factor['factor']}",
                "explanation": factor['explanation'],
                "confidence": factor['confidence']
            })

        # Volatility factors
        for factor in self.volatility_factors[:2]:
            trace_factors.append({
                "factor": f"volatility_{factor['factor']}",
                "explanation": factor['explanation'],
                "confidence": factor['confidence']
            })

        # Sentiment factors
        for factor in self.sentiment_factors[:2]:
            trace_factors.append({
                "factor": f"sentiment_{factor['factor']}",
                "explanation": factor['explanation'],
                "confidence": factor['confidence']
            })

        return trace_factors


class MarketContextEngine:
    """
    Main orchestrator for market context analysis.

    Combines three specialized analyzers:
    1. RegimeDetector - Market state classification
    2. VolatilityMapper - Volatility environment mapping
    3. SentimentSynthesizer - Sentiment aggregation

    Usage:
        engine = MarketContextEngine()
        context = engine.analyze(ohlcv_df, orderbook=optional_ob_data)
    """

    def __init__(self, crypto_calibrated: bool = True):
        """
        Initialize context engine.

        Args:
            crypto_calibrated: If True, use crypto-specific thresholds
                              If False, use traditional market defaults

        Note: crypto_calibrated=True is REQUIRED for BTC/crypto trading!
        """
        self.regime_detector = RegimeDetector()
        self.volatility_mapper = VolatilityMapper()
        self.sentiment_synthesizer = SentimentSynthesizer()
        self.crypto_calibrated = crypto_calibrated

        # TODO: Load crypto-specific calibration parameters
        # Will be tuned with historical BTC data
        self.calibration_params = self._load_calibration()

    def analyze(
        self,
        ohlcv: pd.DataFrame,
        orderbook: Optional[dict] = None
    ) -> MarketContext:
        """
        Perform complete market context analysis.

        Args:
            ohlcv: DataFrame with columns [timestamp, open, high, low, close, volume]
                  Minimum 200 rows recommended for reliable regime detection
            orderbook: Optional order book data with 'bids' and 'asks'

        Returns:
            MarketContext with regime, volatility, sentiment, and metadata
        """
        warnings = []

        # Validate data quality
        data_quality, quality_warnings = self._assess_data_quality(ohlcv)
        warnings.extend(quality_warnings)

        # Run parallel analysis
        regime_result = self.regime_detector.detect(ohlcv)
        volatility_result = self.volatility_mapper.map(ohlcv)
        sentiment_result = self.sentiment_synthesizer.synthesize(ohlcv, orderbook)

        # Cross-validate results
        cross_warnings = self._cross_validate(regime_result, volatility_result, sentiment_result)
        warnings.extend(cross_warnings)

        return MarketContext(
            # Regime
            regime=regime_result.regime,
            regime_confidence=regime_result.confidence,
            regime_factors=regime_result.supporting_factors,

            # Volatility
            volatility_regime=volatility_result.regime,
            volatility_percentile=volatility_result.percentile,
            volatility_level=volatility_result.level,
            volatility_factors=volatility_result.supporting_factors,

            # Sentiment
            sentiment_direction=sentiment_result.direction,
            sentiment_confidence=sentiment_result.confidence,
            sentiment_signals=sentiment_result.signals,
            sentiment_factors=sentiment_result.supporting_factors,

            # Metadata
            timestamp=datetime.utcnow(),
            data_quality=data_quality,
            warnings=warnings
        )

    def _assess_data_quality(self, ohlcv: pd.DataFrame) -> tuple:
        """
        Assess data quality for reliable analysis.

        Returns: (quality_level, warnings)
        """
        warnings = []

        # Check row count
        n_rows = len(ohlcv)
        if n_rows < 30:
            return "insufficient", ["Less than 30 candles - cannot perform reliable analysis"]
        elif n_rows < 100:
            warnings.append("Less than 100 candles - regime detection may be unreliable")
            quality = "marginal"
        elif n_rows < 200:
            warnings.append("Less than 200 candles - regime detection not optimal")
            quality = "good"
        else:
            quality = "excellent"

        # Check for missing data
        if ohlcv.isnull().any().any():
            warnings.append("Missing data detected - results may be unreliable")
            quality = max_quality_downgrade(quality, "marginal")

        # Check for anomalies (price = 0, volume = 0)
        if (ohlcv['close'] == 0).any():
            warnings.append("Zero prices detected - data corruption possible")
            quality = "marginal"

        # Check timestamp consistency (if timestamp column exists)
        if 'timestamp' in ohlcv.columns:
            time_diffs = ohlcv['timestamp'].diff().dropna()
            if time_diffs.std() / time_diffs.mean() > 0.5:  # High variance in intervals
                warnings.append("Irregular time intervals - some periods may have gaps")

        return quality, warnings

    def _cross_validate(
        self,
        regime: RegimeDetection,
        volatility: VolatilityMapping,
        sentiment: SentimentAnalysis
    ) -> List[str]:
        """
        Cross-validate results for logical consistency.

        Checks:
        - Trending regime should align with sentiment direction
        - High volatility should not coincide with ranging_low_vol
        - Extreme events should show across multiple dimensions
        """
        warnings = []

        # Check regime-sentiment alignment
        if "bull" in regime.regime and "bearish" in sentiment.direction:
            if regime.confidence > 0.7 and sentiment.confidence > 0.7:
                warnings.append("Conflicting signals: bullish regime but bearish sentiment")
        elif "bear" in regime.regime and "bullish" in sentiment.direction:
            if regime.confidence > 0.7 and sentiment.confidence > 0.7:
                warnings.append("Conflicting signals: bearish regime but bullish sentiment")

        # Check volatility-regime consistency
        if regime.regime == "ranging_low_vol" and volatility.level in ["high", "extreme"]:
            warnings.append("Inconsistency: ranging_low_vol regime but high volatility detected")
        elif regime.regime == "ranging_high_vol" and volatility.level == "low":
            warnings.append("Inconsistency: ranging_high_vol regime but low volatility detected")

        # Check for extreme conditions
        if volatility.regime == "explosive":
            if regime.regime not in ["breakout_pending", "crash_recovery"]:
                warnings.append("Explosive volatility without corresponding regime classification")

        return warnings

    def _load_calibration(self) -> dict:
        """
        Load calibration parameters.

        TODO: Load from YAML config file with crypto-specific thresholds.
        For now, returns placeholder structure.
        """
        if self.crypto_calibrated:
            return {
                "volatility_thresholds": {
                    "low": 5.0,      # <5% daily = low for crypto
                    "normal": 12.0,  # 5-12% = normal
                    "high": 20.0,    # 12-20% = high
                    "extreme": 30.0  # >20% = extreme
                },
                "trend_thresholds": {
                    "weak": 0.02,    # 2% for weak trend
                    "moderate": 0.05,  # 5% for moderate
                    "strong": 0.10   # 10% for strong
                },
                "sentiment_thresholds": {
                    "neutral_range": 0.15  # ±15% for neutral sentiment
                }
            }
        else:
            # Traditional market defaults (NOT for crypto!)
            return {
                "volatility_thresholds": {
                    "low": 1.0,
                    "normal": 2.5,
                    "high": 5.0,
                    "extreme": 10.0
                },
                "trend_thresholds": {
                    "weak": 0.005,
                    "moderate": 0.015,
                    "strong": 0.03
                },
                "sentiment_thresholds": {
                    "neutral_range": 0.05
                }
            }


def max_quality_downgrade(current: str, new: str) -> str:
    """Helper to downgrade quality level."""
    quality_levels = ["insufficient", "marginal", "good", "excellent"]
    current_idx = quality_levels.index(current)
    new_idx = quality_levels.index(new)
    return quality_levels[min(current_idx, new_idx)]
