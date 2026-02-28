"""
Market Regime Classification

Classifies historical OHLCV data into market regimes using the SIL
Market Context Engine. Used for backtesting and validation.

Regime Categories (from strategies.yaml):
- trending_bull: Sustained uptrend with momentum
- trending_bear: Sustained downtrend with momentum
- ranging_low_vol: Sideways consolidation, low volatility
- ranging_high_vol: Sideways consolidation, high volatility
- breakout_pending: Compression phase before volatility expansion
- crash_recovery: Post-crash recovery phase
- volatile_extreme: Extreme volatility (>90th percentile)
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Optional, List, Dict, Tuple
from datetime import datetime
import logging
import sys

# Add parent directory to path to import SIL components
sys.path.append(str(Path(__file__).parent.parent))

try:
    from market_context.context_engine import MarketContext
except ImportError:
    logging.warning("MarketContext not available - using standalone regime detection")
    MarketContext = None


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class RegimeClassifier:
    """
    Classifies historical OHLCV data into market regimes.

    Uses technical indicators to identify regime boundaries:
    - Trend: EMA crossovers, ADX, slope analysis
    - Volatility: Bollinger Bands width, ATR
    - Range detection: Support/resistance, consolidation patterns
    """

    def __init__(self, use_sil_engine: bool = True):
        """
        Initialize regime classifier.

        Args:
            use_sil_engine: If True, use SIL MarketContext engine (preferred)
                           If False, use standalone technical analysis
        """
        self.use_sil_engine = use_sil_engine and MarketContext is not None

        if self.use_sil_engine:
            logger.info("Using SIL MarketContext engine for regime classification")
        else:
            logger.info("Using standalone technical analysis for regime classification")

    def classify_historical_data(
        self,
        ohlcv_df: pd.DataFrame,
        window_size: int = 200
    ) -> pd.DataFrame:
        """
        Classify each candle in historical data with regime label.

        Args:
            ohlcv_df: DataFrame with columns: timestamp, open, high, low, close, volume
            window_size: Rolling window for regime classification (default: 200 candles)

        Returns:
            DataFrame with additional columns:
                - regime: Regime label
                - regime_confidence: Confidence score (0-1)
                - trend_strength: Trend strength indicator
                - volatility_percentile: Volatility relative to historical range
        """
        logger.info(f"Classifying {len(ohlcv_df)} candles into regimes")

        if len(ohlcv_df) < window_size:
            raise ValueError(f"Insufficient data: need {window_size} candles, got {len(ohlcv_df)}")

        # Calculate technical indicators
        df = ohlcv_df.copy()
        df = self._add_technical_indicators(df)

        # Classify each candle
        regimes = []
        confidences = []

        for i in range(len(df)):
            if i < window_size:
                # Insufficient history - mark as unknown
                regimes.append("insufficient_data")
                confidences.append(0.0)
                continue

            # Get window of data for regime classification
            window_df = df.iloc[max(0, i - window_size):i + 1]

            # Classify regime
            if self.use_sil_engine:
                regime, confidence = self._classify_with_sil(window_df)
            else:
                regime, confidence = self._classify_standalone(window_df)

            regimes.append(regime)
            confidences.append(confidence)

        df['regime'] = regimes
        df['regime_confidence'] = confidences

        logger.info(f"Classification complete. Regime distribution:")
        regime_counts = df[df['regime'] != 'insufficient_data']['regime'].value_counts()
        for regime, count in regime_counts.items():
            pct = (count / len(df)) * 100
            logger.info(f"  {regime}: {count} ({pct:.1f}%)")

        return df

    def _add_technical_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add technical indicators for regime classification."""
        df = df.copy()

        # Exponential Moving Averages
        df['ema_20'] = df['close'].ewm(span=20, adjust=False).mean()
        df['ema_50'] = df['close'].ewm(span=50, adjust=False).mean()
        df['ema_200'] = df['close'].ewm(span=200, adjust=False).mean()

        # Bollinger Bands
        df['bb_middle'] = df['close'].rolling(window=20).mean()
        bb_std = df['close'].rolling(window=20).std()
        df['bb_upper'] = df['bb_middle'] + (bb_std * 2)
        df['bb_lower'] = df['bb_middle'] - (bb_std * 2)
        df['bb_width'] = (df['bb_upper'] - df['bb_lower']) / df['bb_middle']

        # ATR (Average True Range)
        high_low = df['high'] - df['low']
        high_close = np.abs(df['high'] - df['close'].shift())
        low_close = np.abs(df['low'] - df['close'].shift())
        true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        df['atr'] = true_range.rolling(window=14).mean()
        df['atr_pct'] = (df['atr'] / df['close']) * 100

        # RSI (Relative Strength Index)
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))

        # Trend strength (slope of EMA20)
        df['trend_strength'] = df['ema_20'].pct_change(periods=10) * 100

        # Volatility percentile (rolling 100 periods)
        df['volatility_percentile'] = df['atr_pct'].rolling(window=100).apply(
            lambda x: (x.iloc[-1] - x.min()) / (x.max() - x.min()) if (x.max() - x.min()) > 0 else 0.5
        )

        return df

    def _classify_with_sil(self, window_df: pd.DataFrame) -> Tuple[str, float]:
        """
        Classify regime using SIL MarketContext engine.

        Returns:
            (regime_label, confidence)
        """
        # Use MarketContext engine to analyze window
        # This will use the same logic as live trading
        try:
            from market_context.context_engine import MarketContext
            context_engine = MarketContext()
            context = context_engine.analyze(window_df)

            if context is None:
                return "unknown", 0.0

            return context.regime, context.regime_confidence

        except Exception as e:
            logger.error(f"SIL classification failed: {e}, falling back to standalone")
            return self._classify_standalone(window_df)

    def _classify_standalone(self, window_df: pd.DataFrame) -> Tuple[str, float]:
        """
        Classify regime using standalone technical analysis.

        Returns:
            (regime_label, confidence)
        """
        latest = window_df.iloc[-1]

        # Extract indicators
        ema_20 = latest['ema_20']
        ema_50 = latest['ema_50']
        ema_200 = latest['ema_200']
        close = latest['close']
        bb_width = latest['bb_width']
        atr_pct = latest['atr_pct']
        trend_strength = latest['trend_strength']
        vol_percentile = latest['volatility_percentile']
        rsi = latest['rsi']

        # Detect regime based on indicators
        confidence = 0.5  # Base confidence

        # 1. Trending Bull
        if (ema_20 > ema_50 > ema_200 and
            close > ema_20 and
            trend_strength > 2.0 and
            rsi > 50):
            return "trending_bull", min(0.7 + (trend_strength / 100), 0.95)

        # 2. Trending Bear
        if (ema_20 < ema_50 < ema_200 and
            close < ema_20 and
            trend_strength < -2.0 and
            rsi < 50):
            return "trending_bear", min(0.7 + (abs(trend_strength) / 100), 0.95)

        # 3. Ranging Low Vol
        if (bb_width < 0.04 and  # Tight Bollinger Bands
            atr_pct < 2.0 and
            abs(trend_strength) < 1.0):
            return "ranging_low_vol", min(0.65 + (1 - vol_percentile) * 0.2, 0.9)

        # 4. Ranging High Vol
        if (abs(ema_20 - ema_50) / ema_50 < 0.02 and  # EMAs flat
            atr_pct > 4.0 and
            abs(trend_strength) < 2.0):
            return "ranging_high_vol", min(0.65 + vol_percentile * 0.2, 0.9)

        # 5. Breakout Pending
        if (bb_width < 0.03 and  # Very tight Bollinger Bands
            atr_pct < 2.5 and
            vol_percentile < 0.3):  # Low volatility environment
            compression_score = (1 - bb_width / 0.03) * 0.3
            return "breakout_pending", min(0.6 + compression_score, 0.85)

        # 6. Volatile Extreme
        if (atr_pct > 10.0 or vol_percentile > 0.9):
            return "volatile_extreme", min(0.75 + vol_percentile * 0.2, 0.95)

        # 7. Crash Recovery (experimental - detect sharp bounce from low RSI)
        if (rsi < 30 and
            close > ema_20 and
            trend_strength > 3.0):
            return "crash_recovery", 0.65

        # Default: Ranging High Vol (if no clear pattern)
        return "ranging_high_vol", 0.50

    def get_regime_summary(self, classified_df: pd.DataFrame) -> pd.DataFrame:
        """
        Generate summary statistics for regime classification.

        Args:
            classified_df: DataFrame with regime classifications

        Returns:
            Summary DataFrame with regime counts, durations, transitions
        """
        df = classified_df[classified_df['regime'] != 'insufficient_data'].copy()

        if df.empty:
            return pd.DataFrame()

        # Regime frequency
        regime_counts = df['regime'].value_counts()
        total = len(df)

        summary_rows = []
        for regime in regime_counts.index:
            regime_df = df[df['regime'] == regime]
            count = len(regime_df)
            pct = (count / total) * 100
            avg_confidence = regime_df['regime_confidence'].mean()

            # Calculate average regime duration
            regime_changes = (df['regime'] != df['regime'].shift()).cumsum()
            regime_groups = df[df['regime'] == regime].groupby(regime_changes)
            avg_duration_candles = regime_groups.size().mean()

            summary_rows.append({
                'regime': regime,
                'count': count,
                'percentage': pct,
                'avg_confidence': avg_confidence,
                'avg_duration_candles': avg_duration_candles
            })

        summary = pd.DataFrame(summary_rows).sort_values('count', ascending=False)
        return summary


def main():
    """CLI interface for regime classification."""
    import argparse

    parser = argparse.ArgumentParser(description="Classify historical data into market regimes")
    parser.add_argument(
        "--input",
        type=str,
        required=True,
        help="Path to input CSV file (OHLCV data)"
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Path to output CSV file (default: input_classified.csv)"
    )
    parser.add_argument(
        "--window",
        type=int,
        default=200,
        help="Rolling window size for classification (default: 200)"
    )
    parser.add_argument(
        "--summary",
        action="store_true",
        help="Print regime summary statistics"
    )

    args = parser.parse_args()

    # Load data
    logger.info(f"Loading data from {args.input}")
    df = pd.read_csv(args.input, parse_dates=['timestamp'])

    # Classify
    classifier = RegimeClassifier(use_sil_engine=True)
    classified_df = classifier.classify_historical_data(df, window_size=args.window)

    # Save
    output_path = args.output or args.input.replace(".csv", "_classified.csv")
    logger.info(f"Saving classified data to {output_path}")
    classified_df.to_csv(output_path, index=False)

    # Print summary
    if args.summary:
        summary = classifier.get_regime_summary(classified_df)
        print("\nRegime Summary:")
        print(summary.to_string(index=False))


if __name__ == "__main__":
    main()
