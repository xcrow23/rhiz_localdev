# Historical Context Ingestion System - Design Document

**Date**: 2026-01-03
**Status**: DESIGN PHASE
**Priority**: CRITICAL for True Intelligence

---

## Executive Summary

The Strategic Intelligence Layer currently lacks historical market context - it cannot learn from how BTC, ETH, and SOL have historically reacted to different market conditions. This makes it **reactive** rather than **truly intelligent**.

**Goal**: Ingest and analyze 2-3 years of historical OHLCV data for BTC, ETH, and SOL to build:
1. **Baseline regime classifications** (what regimes existed historically)
2. **Regime transition patterns** (how markets move between regimes)
3. **Strategy performance expectations** (how strategies should perform in each regime)
4. **Market correlation patterns** (how assets move together)

---

## Architecture Overview

```
Historical Data Sources
        ↓
  Ingestion Pipeline
        ↓
  Regime Analysis Engine
        ↓
  Learning Engine Baseline Calibration
        ↓
  Qdrant Historical Context Storage
```

---

## Data Requirements

### Assets
1. **Bitcoin (BTC/USD)**
2. **Ethereum (ETH/USD)**
3. **Solana (SOL/USD)**

### Timeframe
- **Historical Window**: 2-3 years (2022-01-01 to 2026-01-03)
- **Granularity**: 1-hour candles (26,280 candles per asset)
- **Total Data Points**: ~79k candles across 3 assets

### Data Schema
```python
@dataclass
class HistoricalCandle:
    asset: str  # "BTC", "ETH", "SOL"
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float
    # Derived fields (calculated during ingestion)
    returns: float  # Percent change from previous close
    volatility_20h: float  # 20-hour rolling volatility
    regime: str  # Classified regime
    regime_confidence: float
```

---

## Data Sources (Priority Order)

### Option 1: Kraken API (FREE - Recommended)
- **Endpoint**: `https://api.kraken.com/0/public/OHLC`
- **Rate Limit**: 15 requests/sec (generous)
- **Pairs**: BTC/USD, ETH/USD, SOL/USD
- **Granularity**: 1h, 4h, 1d
- **History**: Full 2+ years available
- **Cost**: FREE
- **Implementation**:
  ```python
  import requests

  def fetch_kraken_ohlcv(pair, since=0):
      url = f"https://api.kraken.com/0/public/OHLC"
      params = {
          'pair': pair,  # e.g., 'XBTUSD'
          'interval': 60,  # 1 hour
          'since': since
      }
      response = requests.get(url, params=params)
      return response.json()
  ```

### Option 2: CoinGecko API (FREE - Fallback)
- **Endpoint**: `/coins/{id}/market_chart/range`
- **Rate Limit**: 10-30 calls/min (free tier)
- **Cost**: FREE
- **Granularity**: Hourly (for ranges < 90 days, needs batching)

### Option 3: Binance API (FREE - High Quality)
- **Endpoint**: `/api/v3/klines`
- **Rate Limit**: 1200 weight/min
- **Granularity**: 1h
- **History**: Full 2+ years
- **Cost**: FREE

**Recommendation**: Use **Kraken** as primary (we're already using Kraken), Binance as fallback.

---

## Ingestion Pipeline

### Phase 1: Data Collection

```python
class HistoricalDataIngester:
    """Fetch and store historical OHLCV data."""

    def __init__(self, source="kraken", cache_dir="./historical_data"):
        self.source = source
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def fetch_asset_history(
        self,
        asset: str,
        start_date: datetime,
        end_date: datetime,
        interval: str = "1h"
    ) -> pd.DataFrame:
        """
        Fetch historical data for one asset.

        Returns DataFrame with OHLCV columns.
        """
        # Check cache first
        cache_file = self.cache_dir / f"{asset}_{interval}_{start_date.date()}_{end_date.date()}.parquet"
        if cache_file.exists():
            return pd.read_parquet(cache_file)

        # Fetch from source
        data = self._fetch_from_source(asset, start_date, end_date, interval)

        # Cache for future use
        data.to_parquet(cache_file)

        return data

    def fetch_all_assets(self, start_date, end_date):
        """Fetch BTC, ETH, SOL history."""
        return {
            "BTC": self.fetch_asset_history("BTC", start_date, end_date),
            "ETH": self.fetch_asset_history("ETH", start_date, end_date),
            "SOL": self.fetch_asset_history("SOL", start_date, end_date)
        }
```

### Phase 2: Regime Classification

```python
class HistoricalRegimeAnalyzer:
    """Classify historical data into market regimes."""

    def __init__(self, context_engine: MarketContextEngine):
        self.context_engine = context_engine

    def classify_historical_regimes(
        self,
        ohlcv_data: pd.DataFrame,
        window_size: int = 200
    ) -> pd.DataFrame:
        """
        Classify each candle's regime using rolling window.

        Returns DataFrame with regime columns added.
        """
        regimes = []

        for i in range(window_size, len(ohlcv_data)):
            # Get window of data
            window = ohlcv_data.iloc[i-window_size:i]

            # Classify regime
            context = self.context_engine.analyze(window)

            regimes.append({
                'timestamp': ohlcv_data.iloc[i]['timestamp'],
                'regime': context.regime,
                'regime_confidence': context.regime_confidence,
                'volatility_regime': context.volatility_regime,
                'sentiment_direction': context.sentiment_direction
            })

        return pd.DataFrame(regimes)
```

### Phase 3: Baseline Performance Calculation

```python
class BaselinePerformanceCalculator:
    """Calculate expected strategy performance from historical data."""

    def calculate_strategy_baseline(
        self,
        asset: str,
        regime_data: pd.DataFrame,
        strategy_config: dict
    ) -> dict:
        """
        Simulate strategy on historical data to get baseline expectations.

        Returns:
            {
                "expected_win_rate": float,
                "expected_rr_ratio": float,
                "expected_sharpe": float,
                "total_opportunities": int,
                "regime_breakdown": {
                    "ranging_low_vol": {...},
                    "trending_bullish_high_vol": {...}
                }
            }
        """
        # Identify trade opportunities based on strategy rules
        opportunities = self._identify_opportunities(regime_data, strategy_config)

        # Calculate performance metrics
        wins = sum(1 for opp in opportunities if opp['outcome'] == 'win')
        total = len(opportunities)

        return {
            "asset": asset,
            "strategy": strategy_config['name'],
            "expected_win_rate": wins / total if total > 0 else 0,
            "total_opportunities": total,
            "sample_period": f"{regime_data['timestamp'].min()} to {regime_data['timestamp'].max()}"
        }
```

### Phase 4: Storage in Qdrant

```python
# New collection for historical context
HISTORICAL_CONTEXT_COLLECTION = "sil_historical_baseline"

def store_historical_baseline(
    memory_client: QdrantMemoryClient,
    asset: str,
    strategy: str,
    regime: str,
    baseline_data: dict
):
    """Store baseline performance expectations in Qdrant."""

    payload = {
        "asset": asset,
        "strategy": strategy,
        "regime": regime,
        "expected_win_rate": baseline_data['expected_win_rate'],
        "expected_sharpe": baseline_data['expected_sharpe'],
        "total_historical_opportunities": baseline_data['total_opportunities'],
        "data_period_start": baseline_data['period_start'].isoformat(),
        "data_period_end": baseline_data['period_end'].isoformat(),
        "last_updated": datetime.utcnow().isoformat()
    }

    # Create embedding based on market conditions
    embedding = encode_regime_characteristics(regime)

    memory_client.client.upsert(
        collection_name=HISTORICAL_CONTEXT_COLLECTION,
        points=[{
            "id": f"{asset}_{strategy}_{regime}",
            "vector": embedding,
            "payload": payload
        }]
    )
```

---

## Integration with Learning Engine

### Before Historical Context:
```python
# Learning engine has no baseline - uses hard-coded expectations
strategy_config = {
    "expected_win_rate": 0.60,  # Guess!
    "expected_rr_ratio": 1.67   # Guess!
}
```

### After Historical Context:
```python
# Learning engine looks up historical baseline
baseline = memory_client.get_historical_baseline(
    asset="BTC",
    strategy="mean_reversion",
    regime="ranging_low_vol"
)

strategy_config = {
    "expected_win_rate": baseline.expected_win_rate,  # From 2 years of data!
    "expected_rr_ratio": baseline.expected_rr_ratio,
    "confidence": baseline.sample_confidence  # Based on how many historical opportunities
}
```

---

## Regime Transition Analysis

### Key Insight: Markets Don't Stay in One Regime

```python
class RegimeTransitionAnalyzer:
    """Analyze how regimes transition over time."""

    def build_transition_matrix(self, regime_history: pd.DataFrame) -> dict:
        """
        Calculate probability of transitioning from one regime to another.

        Returns:
            {
                "ranging_low_vol": {
                    "ranging_low_vol": 0.85,  # 85% stay in same regime
                    "ranging_medium_vol": 0.10,
                    "trending_bullish_low_vol": 0.03,
                    ...
                },
                ...
            }
        """
        transitions = {}

        for i in range(len(regime_history) - 1):
            current = regime_history.iloc[i]['regime']
            next_regime = regime_history.iloc[i+1]['regime']

            if current not in transitions:
                transitions[current] = {}

            transitions[current][next_regime] = transitions[current].get(next_regime, 0) + 1

        # Normalize to probabilities
        for current, nexts in transitions.items():
            total = sum(nexts.values())
            transitions[current] = {k: v/total for k, v in nexts.items()}

        return transitions
```

**Use Case**: Predict when regime is about to change → adjust strategy selection

---

## Multi-Asset Correlation Analysis

```python
class CorrelationAnalyzer:
    """Analyze how BTC, ETH, SOL move together."""

    def calculate_rolling_correlations(
        self,
        btc_data: pd.DataFrame,
        eth_data: pd.DataFrame,
        sol_data: pd.DataFrame,
        window: int = 168  # 1 week of hourly data
    ) -> pd.DataFrame:
        """
        Calculate rolling correlation between assets.

        Returns DataFrame with:
        - timestamp
        - btc_eth_corr
        - btc_sol_corr
        - eth_sol_corr
        """
        # Align timestamps
        merged = pd.merge(btc_data, eth_data, on='timestamp', suffixes=('_btc', '_eth'))
        merged = pd.merge(merged, sol_data, on='timestamp')
        merged.rename(columns={'close': 'close_sol'}, inplace=True)

        # Calculate returns
        merged['returns_btc'] = merged['close_btc'].pct_change()
        merged['returns_eth'] = merged['close_eth'].pct_change()
        merged['returns_sol'] = merged['close_sol'].pct_change()

        # Rolling correlations
        merged['btc_eth_corr'] = merged['returns_btc'].rolling(window).corr(merged['returns_eth'])
        merged['btc_sol_corr'] = merged['returns_btc'].rolling(window).corr(merged['returns_sol'])
        merged['eth_sol_corr'] = merged['returns_eth'].rolling(window).corr(merged['returns_sol'])

        return merged[['timestamp', 'btc_eth_corr', 'btc_sol_corr', 'eth_sol_corr']]
```

**Use Case**: Risk management - if BTC/ETH/SOL highly correlated, don't hold all three (concentration risk)

---

## Implementation Plan

### Step 1: Data Collection (Week 1)
- [ ] Implement Kraken API fetcher
- [ ] Fetch BTC historical data (2022-2026)
- [ ] Fetch ETH historical data
- [ ] Fetch SOL historical data
- [ ] Cache to local parquet files

### Step 2: Regime Analysis (Week 1-2)
- [ ] Run MarketContextEngine on all historical data
- [ ] Store regime classifications
- [ ] Generate regime transition matrix
- [ ] Identify regime "meta-patterns" (e.g., bull market = more trending regimes)

### Step 3: Baseline Calculation (Week 2)
- [ ] Simulate each strategy on historical data
- [ ] Calculate win rates, R:R ratios, Sharpe by regime
- [ ] Store baselines in Qdrant
- [ ] Update Learning Engine to use baselines

### Step 4: Multi-Asset Integration (Week 3)
- [ ] Calculate correlation matrices
- [ ] Implement correlation-based risk limits
- [ ] Add asset-specific regime detection
- [ ] Enable multi-asset strategy selection

---

## Key Benefits

### 1. Realistic Expectations
- **Before**: "Mean reversion in ranging markets should win 60%" (guess)
- **After**: "Mean reversion in ranging_low_vol won 58.3% over 2 years (127 opportunities)"

### 2. Regime Awareness
- **Before**: "Current regime is ranging_low_vol"
- **After**: "Current regime is ranging_low_vol, 85% likely to stay there next hour, 10% chance of volatility increase"

### 3. Strategy Validation
- **Before**: "Let's try this strategy and see what happens"
- **After**: "This strategy had 12 opportunities in this regime historically with 67% win rate - proceed with confidence"

### 4. Multi-Asset Intelligence
- **Before**: Only trade BTC
- **After**: "BTC correlation with ETH is 0.92 (high), don't over-expose to crypto risk"

---

## Storage Requirements

### Parquet Cache (Local)
- 3 assets × 26,280 candles × 10 fields × 8 bytes = ~6.3 MB
- Negligible storage cost

### Qdrant Collections
- **Historical Baseline**: ~150 records (3 assets × 5 strategies × 10 regimes)
- **Regime Transitions**: ~100 records (10 regimes × 10 possible transitions)
- **Correlation Data**: ~26k records (1 per hour)

**Total Qdrant Overhead**: ~50 MB

---

## Performance Impact

- **Ingestion (one-time)**: ~10 minutes to fetch + classify 79k candles
- **Query Latency**: <5ms to lookup historical baseline
- **Update Frequency**: Weekly (re-calculate correlations with new data)

---

## Cloud-First Considerations

### Local Development
- Fetch historical data once
- Cache to local parquet
- Run analysis locally

### Production (n8n Cloud)
- Store parquet files in S3/Backblaze
- Qdrant Cloud for baseline storage
- Scheduled workflow (weekly) to update correlations

---

## Next Steps

1. **Immediate**: Implement Kraken API fetcher
2. **Week 1**: Fetch BTC/ETH/SOL data, cache locally
3. **Week 2**: Run regime analysis, store baselines
4. **Week 3**: Integrate with Learning Engine

**Est. Time to Full Historical Context**: 2-3 weeks

---

**Status**: Ready for implementation after Sprint 2 completion
