# SYNTHESIS REPORT: Multi-Asset Historical Intelligence for Strategic Intelligence Layer (BTC/ETH/SOL)

**Date**: 2026-01-03
**Agent**: Delta (Synthesis Specialist)
**Status**: FRAMEWORK COMPLETE - AWAITING AGENT INPUTS
**Dependencies**: Agent Alpha (BTC), Agent Beta (ETH), Agent Gamma (SOL)

---

## Executive Summary

**CRITICAL NOTE**: This synthesis report framework has been created, but the three underlying agent reports (Alpha-BTC, Beta-ETH, Gamma-SOL) have not yet been completed. This document provides the structure and methodology for synthesizing multi-asset historical intelligence once the prerequisite analyses are available.

**Mission**: Synthesize historical market analysis from three separate agents into a unified, actionable implementation roadmap for multi-asset trading in the Strategic Intelligence Layer.

**Current Blockers**:
- ❌ Agent Alpha (a0c6be2): Bitcoin Historical Market Analysis (2022-2026) - NOT FOUND
- ❌ Agent Beta (aeae655): Ethereum Historical Behavior Analysis (2022-2026) - NOT FOUND
- ❌ Agent Gamma (a6a8eee): Solana Historical Market Analysis & Risk Management (2022-2026) - NOT FOUND

**Next Steps**:
1. Complete Agent Alpha analysis (BTC historical patterns, regime behavior, strategy performance)
2. Complete Agent Beta analysis (ETH volatility profile, correlation with BTC, unique characteristics)
3. Complete Agent Gamma analysis (SOL high-volatility behavior, tail risk, extreme moves)
4. Return to this synthesis report and populate all sections with concrete findings

---

## 1. Cross-Asset Comparative Analysis

### 1.1 Volatility Hierarchy

**Expected Structure** (to be populated from agent data):

| Asset | Baseline Volatility (20-day) | Multiplier vs BTC | Regime-Dependent Variation |
|-------|------------------------------|-------------------|----------------------------|
| BTC   | [ALPHA DATA]% | 1.00x (baseline) | Low Vol: [X]% / High Vol: [Y]% |
| ETH   | [BETA DATA]% | [BETA/ALPHA]x | Low Vol: [X]% / High Vol: [Y]% |
| SOL   | [GAMMA DATA]% | [GAMMA/ALPHA]x | Low Vol: [X]% / High Vol: [Y]% |

**Key Questions for Agent Reports**:
- What is the historical 20-day rolling volatility mean for each asset?
- How does volatility behave in ranging_low_vol vs trending_high_vol regimes?
- What are the 95th/99th percentile volatility events (tail risk)?

**Expected Finding Template**:
```
BTC establishes the baseline at [X]% annualized volatility.
ETH exhibits [X.XX]x BTC volatility, averaging [Y]% annualized.
SOL demonstrates [X.XX]x BTC volatility, averaging [Z]% annualized.

Volatility hierarchy is consistent across most regimes except:
- [Regime exception 1]: SOL/ETH volatility convergence
- [Regime exception 2]: BTC volatility spike during [market event]
```

---

### 1.2 Correlation Matrix

**Expected Structure**:

#### Overall Correlation (2022-2026)
|       | BTC   | ETH   | SOL   |
|-------|-------|-------|-------|
| BTC   | 1.00  | [BETA] | [GAMMA] |
| ETH   | [BETA] | 1.00  | [GAMMA] |
| SOL   | [GAMMA] | [GAMMA] | 1.00  |

#### Regime-Dependent Correlation Variations

**Ranging Markets (Low Vol)**:
- BTC-ETH: [X.XX] (expected: 0.80-0.90)
- BTC-SOL: [X.XX] (expected: 0.65-0.80)
- ETH-SOL: [X.XX] (expected: 0.70-0.85)

**Trending Markets (High Vol)**:
- BTC-ETH: [X.XX] (expected: 0.90-0.95)
- BTC-SOL: [X.XX] (expected: 0.75-0.90)
- ETH-SOL: [X.XX] (expected: 0.80-0.92)

**Crisis Events (2022 bear, 2024 correction)**:
- BTC-ETH: [X.XX] (expected: 0.95+)
- BTC-SOL: [X.XX] (expected: 0.90+)
- ETH-SOL: [X.XX] (expected: 0.93+)

**Critical Insight for Risk Management**:
```
During high-stress periods, correlation approaches 1.0 across all pairs.
This means multi-asset "diversification" provides FALSE SECURITY in crisis scenarios.

Risk management MUST account for correlation regime:
- Normal markets: Apply standard correlation discounts
- High volatility: Increase correlation assumptions by +0.15
- Crisis detected: Treat all crypto positions as single exposure
```

---

### 1.3 Regime Frequency Comparison

**Expected Structure** (percentage of time spent in each regime, 2022-2026):

| Regime | BTC (Alpha) | ETH (Beta) | SOL (Gamma) | Notes |
|--------|-------------|------------|-------------|-------|
| ranging_low_vol | [X]% | [X]% | [X]% | Base state |
| ranging_medium_vol | [X]% | [X]% | [X]% | Uncertainty |
| ranging_high_vol | [X]% | [X]% | [X]% | Choppy |
| trending_bullish_low_vol | [X]% | [X]% | [X]% | Steady climb |
| trending_bullish_medium_vol | [X]% | [X]% | [X]% | Strong momentum |
| trending_bullish_high_vol | [X]% | [X]% | [X]% | Euphoric |
| trending_bearish_low_vol | [X]% | [X]% | [X]% | Slow bleed |
| trending_bearish_medium_vol | [X]% | [X]% | [X]% | Distribution |
| trending_bearish_high_vol | [X]% | [X]% | [X]% | Panic |
| uncertain | [X]% | [X]% | [X]% | Transition |

**Key Comparative Questions**:
1. Does SOL spend MORE time in high_vol regimes than BTC/ETH?
2. Which asset has the most stable regime persistence (fewer transitions)?
3. Do regime transitions lead or lag across assets? (e.g., BTC shifts first, ETH follows)

**Expected Finding**:
```
BTC demonstrates the most regime stability (average regime duration: [X] hours).
ETH transitions [X]% more frequently than BTC.
SOL exhibits [X]x regime churn vs BTC, indicating higher reactivity.

Key asymmetry: SOL spends [X]% more time in high_vol regimes,
making volatility-based strategies more applicable.
```

---

### 1.4 Strategy Performance by Asset

**Expected Structure**:

#### Mean Reversion Strategy

| Asset | Win Rate | Avg R:R | Sharpe | Best Regime | Worst Regime |
|-------|----------|---------|--------|-------------|--------------|
| BTC   | [X]% | [X.XX] | [X.XX] | [regime] | [regime] |
| ETH   | [X]% | [X.XX] | [X.XX] | [regime] | [regime] |
| SOL   | [X]% | [X.XX] | [X.XX] | [regime] | [regime] |

#### Trend Following Strategy

| Asset | Win Rate | Avg R:R | Sharpe | Best Regime | Worst Regime |
|-------|----------|---------|--------|-------------|--------------|
| BTC   | [X]% | [X.XX] | [X.XX] | [regime] | [regime] |
| ETH   | [X]% | [X.XX] | [X.XX] | [regime] | [regime] |
| SOL   | [X]% | [X.XX] | [X.XX] | [regime] | [regime] |

**Cross-Asset Strategy Recommendations**:

1. **Mean Reversion**:
   - **Best on**: [Asset] (win rate: [X]%, Sharpe: [X])
   - **Avoid on**: [Asset] (win rate: [X]%, Sharpe: [X])
   - **Rationale**: [from agent reports]

2. **Trend Following**:
   - **Best on**: [Asset] (win rate: [X]%, Sharpe: [X])
   - **Avoid on**: [Asset] (win rate: [X]%, Sharpe: [X])
   - **Rationale**: [from agent reports]

3. **Breakout Capture**:
   - **Best on**: [Asset] (win rate: [X]%, Sharpe: [X])
   - **Avoid on**: [Asset] (win rate: [X]%, Sharpe: [X])
   - **Rationale**: [from agent reports]

---

## 2. Unified Strategy Parameter Recommendations

### 2.1 Consolidated Parameter Adjustment Matrix

**Baseline: BTC Parameters**

| Strategy Component | BTC (Baseline) | ETH Adjustment | SOL Adjustment | Rationale |
|-------------------|----------------|----------------|----------------|-----------|
| **Position Size** | | | | |
| Max position % | 25% | -5% (20%) | -10% (15%) | Higher vol = lower size |
| Min position $ | $50 | $50 | $30 | SOL allows smaller |
| **Stop Loss** | | | | |
| ranging_low_vol | 3.0% | ×1.3 (3.9%) | ×1.8 (5.4%) | Volatility scaling |
| trending_high_vol | 5.0% | ×1.3 (6.5%) | ×1.8 (9.0%) | Volatility scaling |
| **Profit Target** | | | | |
| ranging_low_vol | 5.0% | ×1.2 (6.0%) | ×1.5 (7.5%) | Higher reward for risk |
| trending_high_vol | 8.0% | ×1.2 (9.6%) | ×1.5 (12.0%) | Higher reward for risk |
| **Entry Threshold** | | | | |
| Bollinger % | 0.5 (50%) | 0.55 (55%) | 0.60 (60%) | Wider bands |
| RSI oversold | 30 | 28 | 25 | More extreme |
| **Time Horizon** | | | | |
| Avg trade duration | 8-12h | 8-12h | 6-10h | SOL faster |
| Max hold time | 48h | 48h | 36h | SOL faster exits |

**Volatility Multiplier Calculation**:
```python
def get_volatility_multiplier(asset: str, baseline_vol: float, current_vol: float) -> float:
    """
    Calculate how much to adjust parameters based on asset and volatility.

    Args:
        asset: "BTC", "ETH", or "SOL"
        baseline_vol: Historical mean volatility for this asset
        current_vol: Current 20-period volatility

    Returns:
        Multiplier for stop loss and profit targets
    """
    asset_base_multipliers = {
        "BTC": 1.00,
        "ETH": 1.30,  # [FROM BETA ANALYSIS]
        "SOL": 1.80   # [FROM GAMMA ANALYSIS]
    }

    # Current volatility vs baseline
    vol_ratio = current_vol / baseline_vol

    # Combined multiplier
    return asset_base_multipliers[asset] * vol_ratio
```

---

### 2.2 Asset-Specific Strategy Applicability

**Matrix: Which Strategies Work on Which Assets?**

| Strategy | BTC | ETH | SOL | Priority Rank |
|----------|-----|-----|-----|---------------|
| Mean Reversion | ✅ Excellent | ✅ Good | ⚠️ Risky | BTC > ETH > SOL |
| Trend Following | ✅ Good | ✅ Good | ✅ Excellent | SOL > ETH > BTC |
| Breakout Capture | ⚠️ Moderate | ✅ Good | ✅ Excellent | SOL > ETH > BTC |
| DCA Accumulation | ✅ Excellent | ✅ Good | ⚠️ Risky | BTC > ETH > SOL |
| Risk-Off | ✅ Use BTC | ✅ Use BTC | ✅ Use BTC | Exit to BTC |

**Key Insight**:
```
SOL is a momentum/volatility asset - best for trend following and breakouts.
BTC is a stability asset - best for mean reversion and accumulation.
ETH is balanced - performs adequately across all strategies.

For $100-150 initial capital:
- Start with BTC only (stability, learning curve)
- Add ETH after 20+ successful trades
- Add SOL only after mastering volatility management
```

---

### 2.3 Multi-Asset Implementation Priority

**Phase 1: BTC Only (Weeks 1-4)**
- Learn SIL behavior with most stable asset
- Validate regime detection
- Build confidence with lower volatility
- Capital target: $100 → $125

**Phase 2: BTC + ETH (Weeks 5-8)**
- Add ETH for moderate diversification
- Test correlation-based position sizing
- Validate parameter adjustments
- Capital target: $125 → $175

**Phase 3: BTC + ETH + SOL (Weeks 9-12)**
- Full multi-asset operation
- Advanced correlation management
- Higher risk/reward profile
- Capital target: $175 → $250

**DO NOT skip phases. Each phase requires minimum 15 successful trades before advancing.**

---

## 3. Multi-Asset Risk Management Framework

### 3.1 Concentration Risk Model

**Problem**: High correlation means holding BTC+ETH+SOL is NOT true diversification.

**Solution**: Correlation-weighted exposure limits.

```python
class MultiAssetRiskManager:
    """Manage risk across correlated crypto assets."""

    def __init__(self):
        # From historical analysis
        self.base_correlations = {
            ('BTC', 'ETH'): 0.85,  # [FROM BETA ANALYSIS]
            ('BTC', 'SOL'): 0.75,  # [FROM GAMMA ANALYSIS]
            ('ETH', 'SOL'): 0.80   # [FROM BETA/GAMMA CROSS-ANALYSIS]
        }

        # Correlation increases in high volatility
        self.volatility_correlation_adjustment = {
            'low': 0.00,
            'medium': 0.10,
            'high': 0.20
        }

    def calculate_effective_exposure(
        self,
        positions: dict[str, float],  # {asset: position_size_usd}
        volatility_regime: str
    ) -> float:
        """
        Calculate correlation-adjusted total exposure.

        Returns effective exposure as % of capital.
        """
        if len(positions) == 1:
            # Single asset - no correlation adjustment
            return sum(positions.values())

        # Adjust correlations for volatility regime
        corr_adj = self.volatility_correlation_adjustment[volatility_regime]
        adjusted_corrs = {
            pair: min(1.0, base_corr + corr_adj)
            for pair, base_corr in self.base_correlations.items()
        }

        # Calculate correlation-weighted exposure
        total_exposure = 0
        assets = list(positions.keys())

        for i, asset1 in enumerate(assets):
            for asset2 in assets[i:]:
                if asset1 == asset2:
                    # Self-correlation = 1.0
                    total_exposure += positions[asset1]
                else:
                    # Cross-correlation weighted
                    pair = tuple(sorted([asset1, asset2]))
                    corr = adjusted_corrs.get(pair, 0.8)  # Default high
                    total_exposure += positions[asset1] * positions[asset2] * corr

        return total_exposure

    def check_concentration_limits(
        self,
        current_positions: dict[str, float],
        new_position: tuple[str, float],  # (asset, size_usd)
        total_capital: float,
        volatility_regime: str
    ) -> tuple[bool, str]:
        """
        Check if adding new position would exceed concentration limits.

        Returns (allowed, reason)
        """
        # Add proposed position
        proposed_positions = current_positions.copy()
        asset, size = new_position
        proposed_positions[asset] = proposed_positions.get(asset, 0) + size

        # Calculate effective exposure
        effective_exposure = self.calculate_effective_exposure(
            proposed_positions,
            volatility_regime
        )

        effective_exposure_pct = effective_exposure / total_capital

        # Limits by volatility regime
        limits = {
            'low': 0.50,    # 50% effective exposure in low vol
            'medium': 0.40, # 40% in medium vol
            'high': 0.30    # 30% in high vol (correlation near 1.0)
        }

        limit = limits[volatility_regime]

        if effective_exposure_pct > limit:
            return False, (
                f"Concentration limit exceeded: {effective_exposure_pct:.1%} > {limit:.0%} "
                f"(effective exposure in {volatility_regime} volatility regime)"
            )

        return True, "Within concentration limits"
```

**Example Scenario**:
```
Capital: $150
Current positions: BTC $30 (20%), ETH $25 (17%)
Proposed: Add SOL $25 (17%)

Without correlation adjustment: 54% total exposure ✅
With correlation adjustment (medium vol):
  - BTC-ETH correlation: 0.95 (0.85 + 0.10)
  - BTC-SOL correlation: 0.85 (0.75 + 0.10)
  - ETH-SOL correlation: 0.90 (0.80 + 0.10)

Effective exposure: ~70% ❌ EXCEEDS 40% LIMIT

Decision: REJECT SOL position OR reduce BTC/ETH first
```

---

### 3.2 Circuit Breaker Thresholds by Asset

**Asset-Specific Circuit Breakers**:

| Asset | Consecutive Losses | Daily Loss % | Weekly Loss % | Rationale |
|-------|-------------------|--------------|---------------|-----------|
| BTC   | 5 losses | -5.0% | -10.0% | [FROM ALPHA] |
| ETH   | 4 losses | -6.0% | -12.0% | Higher vol = tighter |
| SOL   | 3 losses | -7.0% | -14.0% | Highest vol = tightest |

**Multi-Asset Aggregate Circuit Breaker**:
```python
# Global circuit breaker (across all assets)
MAX_PORTFOLIO_DAILY_LOSS = -8.0%  # Stricter than any single asset
MAX_PORTFOLIO_WEEKLY_LOSS = -15.0%

# If portfolio hits these limits, HALT ALL TRADING regardless of asset-specific limits
```

**Circuit Breaker Logic**:
```python
def should_trip_circuit_breaker(
    asset: str,
    recent_trades: list[Trade],
    portfolio_performance: dict
) -> tuple[bool, str]:
    """
    Check both asset-specific and portfolio-level circuit breakers.

    Returns (should_trip, reason)
    """
    # Asset-specific checks
    consecutive_losses = count_consecutive_losses(asset, recent_trades)
    daily_loss_pct = calculate_daily_loss(asset, recent_trades)
    weekly_loss_pct = calculate_weekly_loss(asset, recent_trades)

    thresholds = {
        'BTC': {'consecutive': 5, 'daily': -5.0, 'weekly': -10.0},
        'ETH': {'consecutive': 4, 'daily': -6.0, 'weekly': -12.0},
        'SOL': {'consecutive': 3, 'daily': -7.0, 'weekly': -14.0}
    }

    asset_threshold = thresholds[asset]

    if consecutive_losses >= asset_threshold['consecutive']:
        return True, f"{asset}: {consecutive_losses} consecutive losses"

    if daily_loss_pct <= asset_threshold['daily']:
        return True, f"{asset}: {daily_loss_pct:.1%} daily loss"

    if weekly_loss_pct <= asset_threshold['weekly']:
        return True, f"{asset}: {weekly_loss_pct:.1%} weekly loss"

    # Portfolio-level checks
    portfolio_daily = portfolio_performance['daily_pnl_pct']
    portfolio_weekly = portfolio_performance['weekly_pnl_pct']

    if portfolio_daily <= -8.0:
        return True, f"PORTFOLIO: {portfolio_daily:.1%} daily loss (HALT ALL)"

    if portfolio_weekly <= -15.0:
        return True, f"PORTFOLIO: {portfolio_weekly:.1%} weekly loss (HALT ALL)"

    return False, "No circuit breaker triggered"
```

---

### 3.3 Position Sizing Formulas with Asset-Specific Discounts

**Base Formula** (from risk_management/position_sizer.py):
```python
position_size = (capital * risk_per_trade) / stop_loss_pct
```

**Multi-Asset Enhanced Formula**:
```python
def calculate_position_size_multi_asset(
    asset: str,
    capital: float,
    risk_per_trade: float,  # e.g., 0.02 for 2%
    stop_loss_pct: float,
    current_positions: dict[str, float],
    regime: str
) -> float:
    """
    Calculate position size with asset-specific and correlation adjustments.
    """
    # Step 1: Asset-specific volatility discount
    volatility_discounts = {
        'BTC': 1.00,  # No discount (baseline)
        'ETH': 0.85,  # 15% reduction for higher vol
        'SOL': 0.70   # 30% reduction for highest vol
    }

    vol_discount = volatility_discounts[asset]

    # Step 2: Correlation discount (if already holding correlated assets)
    corr_discount = calculate_correlation_discount(asset, current_positions)

    # Step 3: Regime discount (reduce size in uncertain regimes)
    regime_discounts = {
        'ranging_low_vol': 1.00,
        'ranging_medium_vol': 0.90,
        'ranging_high_vol': 0.75,
        'trending_bullish_low_vol': 1.00,
        'trending_bullish_medium_vol': 0.95,
        'trending_bullish_high_vol': 0.80,
        'trending_bearish_low_vol': 0.90,
        'trending_bearish_medium_vol': 0.75,
        'trending_bearish_high_vol': 0.60,
        'uncertain': 0.50
    }

    regime_discount = regime_discounts.get(regime, 0.70)

    # Step 4: Calculate size with all discounts
    base_size = (capital * risk_per_trade) / stop_loss_pct
    adjusted_size = base_size * vol_discount * corr_discount * regime_discount

    return adjusted_size


def calculate_correlation_discount(
    asset: str,
    current_positions: dict[str, float]
) -> float:
    """
    Reduce position size if already holding correlated assets.

    Returns multiplier between 0.5 and 1.0.
    """
    if not current_positions:
        return 1.0  # No existing positions

    correlations = {
        ('BTC', 'ETH'): 0.85,
        ('BTC', 'SOL'): 0.75,
        ('ETH', 'SOL'): 0.80
    }

    max_corr = 0.0
    for existing_asset in current_positions:
        if existing_asset == asset:
            continue  # Adding to existing position

        pair = tuple(sorted([asset, existing_asset]))
        corr = correlations.get(pair, 0.5)
        max_corr = max(max_corr, corr)

    # Higher correlation = lower discount (more reduction)
    # Correlation 0.0 → discount 1.0 (no reduction)
    # Correlation 1.0 → discount 0.5 (50% reduction)
    discount = 1.0 - (max_corr * 0.5)

    return discount
```

**Example Calculation**:
```
Asset: SOL
Capital: $150
Risk per trade: 2%
Stop loss: 6.0%
Current positions: BTC $30
Regime: ranging_medium_vol

Step 1: Base size = ($150 × 0.02) / 0.06 = $50
Step 2: Volatility discount = 0.70 (SOL) → $35
Step 3: Correlation discount = 0.625 (BTC-SOL corr 0.75) → $21.88
Step 4: Regime discount = 0.90 (ranging_medium) → $19.69

FINAL POSITION SIZE: $19.69 (13.1% of capital)

Without discounts: $50 (33.3% of capital) ❌ TOO RISKY
With discounts: $19.69 (13.1% of capital) ✅ APPROPRIATE
```

---

### 3.4 Daily/Weekly Risk Budget Allocation

**Risk Budget Framework**:

```python
class RiskBudgetAllocator:
    """Allocate risk budget across BTC, ETH, SOL."""

    def __init__(self, total_daily_risk_budget: float = 0.05):
        """
        Args:
            total_daily_risk_budget: Max 5% of capital at risk per day
        """
        self.total_daily_budget = total_daily_risk_budget
        self.total_weekly_budget = total_daily_risk_budget * 3.5  # ~17.5% weekly

        # Allocation percentages (based on stability/opportunity)
        self.base_allocations = {
            'BTC': 0.50,  # 50% of risk budget
            'ETH': 0.30,  # 30% of risk budget
            'SOL': 0.20   # 20% of risk budget
        }

    def get_asset_risk_budget(
        self,
        asset: str,
        capital: float,
        already_used_budget: dict[str, float]
    ) -> float:
        """
        Get remaining risk budget for asset.

        Returns: Dollar amount available to risk on next trade.
        """
        # Asset-specific allocation
        asset_allocation = self.base_allocations[asset]
        asset_daily_budget = capital * self.total_daily_budget * asset_allocation

        # Subtract already used
        used = already_used_budget.get(asset, 0)
        remaining = asset_daily_budget - used

        return max(0, remaining)

    def record_trade_risk(
        self,
        asset: str,
        position_size: float,
        stop_loss_pct: float,
        used_budget: dict[str, float]
    ):
        """
        Update used risk budget when opening position.
        """
        risk_amount = position_size * stop_loss_pct
        used_budget[asset] = used_budget.get(asset, 0) + risk_amount
```

**Example Budget Allocation**:
```
Capital: $150
Daily risk budget: 5% = $7.50

BTC allocation: 50% × $7.50 = $3.75
ETH allocation: 30% × $7.50 = $2.25
SOL allocation: 20% × $7.50 = $1.50

Scenario: Already took BTC trade with $2.00 risk
BTC remaining: $3.75 - $2.00 = $1.75 ✅ Can take another small BTC trade
ETH remaining: $2.25 ✅ Can take ETH trade
SOL remaining: $1.50 ✅ Can take SOL trade

Scenario: Already took BTC ($2.00), ETH ($2.00), SOL ($1.50)
Total used: $5.50 / $7.50 (73%)
BTC remaining: $1.75
ETH remaining: $0.25
SOL remaining: $0.00 ❌ SOL budget exhausted

Next decision: Wait for existing trades to close OR only micro-size BTC
```

---

## 4. Data Collection & Baseline Calibration Roadmap

### 4.1 Unified Data Ingestion Plan

**Objective**: Fetch 2-3 years of OHLCV data for BTC, ETH, SOL from Kraken.

**Implementation Steps**:

#### Step 1: Kraken API Integration
```python
# File: strategic_intelligence/data_ingestion/kraken_fetcher.py

import requests
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
import time

class KrakenHistoricalFetcher:
    """Fetch historical OHLCV data from Kraken API."""

    BASE_URL = "https://api.kraken.com/0/public/OHLC"

    PAIR_MAPPING = {
        'BTC': 'XXBTZUSD',  # Kraken's BTC/USD pair code
        'ETH': 'XETHZUSD',  # Kraken's ETH/USD pair code
        'SOL': 'SOLUSD'     # Kraken's SOL/USD pair code
    }

    def __init__(self, cache_dir: str = "./historical_data"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.rate_limit_delay = 0.1  # 10 requests/sec max

    def fetch_asset_history(
        self,
        asset: str,
        start_date: datetime,
        end_date: datetime,
        interval: int = 60  # 60 min = 1 hour
    ) -> pd.DataFrame:
        """
        Fetch historical OHLCV data for single asset.

        Args:
            asset: "BTC", "ETH", or "SOL"
            start_date: Start of historical window
            end_date: End of historical window
            interval: Candle interval in minutes (60 = 1h)

        Returns:
            DataFrame with columns: timestamp, open, high, low, close, volume
        """
        # Check cache
        cache_file = self._get_cache_filename(asset, start_date, end_date, interval)
        if cache_file.exists():
            print(f"Loading {asset} from cache: {cache_file}")
            return pd.read_parquet(cache_file)

        print(f"Fetching {asset} from Kraken API...")

        # Kraken returns max 720 candles per request
        # For 1h candles, that's 30 days per request
        all_data = []
        current_since = int(start_date.timestamp())
        end_timestamp = int(end_date.timestamp())

        while current_since < end_timestamp:
            # Rate limiting
            time.sleep(self.rate_limit_delay)

            # Fetch batch
            data = self._fetch_batch(asset, current_since, interval)

            if not data:
                break  # No more data

            all_data.extend(data)

            # Update since for next batch
            current_since = data[-1][0] + (interval * 60)  # Convert to seconds

            print(f"  Fetched up to {datetime.fromtimestamp(current_since)}")

        # Convert to DataFrame
        df = pd.DataFrame(all_data, columns=[
            'timestamp', 'open', 'high', 'low', 'close', 'volume', 'vwap', 'count'
        ])

        # Convert timestamp to datetime
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')

        # Keep only needed columns
        df = df[['timestamp', 'open', 'high', 'low', 'close', 'volume']]

        # Cache for future use
        df.to_parquet(cache_file)
        print(f"Cached {asset} data: {len(df)} candles")

        return df

    def _fetch_batch(self, asset: str, since: int, interval: int) -> list:
        """Fetch single batch from Kraken API."""
        pair = self.PAIR_MAPPING[asset]

        params = {
            'pair': pair,
            'interval': interval,
            'since': since
        }

        try:
            response = requests.get(self.BASE_URL, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()

            if data.get('error'):
                print(f"Kraken API error: {data['error']}")
                return []

            # Extract OHLC data
            result_key = list(data['result'].keys())[0]  # Pair name in result
            ohlc_data = data['result'][result_key]

            return ohlc_data

        except Exception as e:
            print(f"Error fetching {asset}: {e}")
            return []

    def _get_cache_filename(
        self,
        asset: str,
        start_date: datetime,
        end_date: datetime,
        interval: int
    ) -> Path:
        """Generate cache filename."""
        start_str = start_date.strftime('%Y%m%d')
        end_str = end_date.strftime('%Y%m%d')
        return self.cache_dir / f"{asset}_{interval}min_{start_str}_{end_str}.parquet"

    def fetch_all_assets(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> dict[str, pd.DataFrame]:
        """
        Fetch all three assets (BTC, ETH, SOL).

        Returns:
            {
                'BTC': DataFrame,
                'ETH': DataFrame,
                'SOL': DataFrame
            }
        """
        return {
            asset: self.fetch_asset_history(asset, start_date, end_date)
            for asset in ['BTC', 'ETH', 'SOL']
        }
```

**Usage**:
```python
from datetime import datetime
from data_ingestion.kraken_fetcher import KrakenHistoricalFetcher

fetcher = KrakenHistoricalFetcher(cache_dir="./data/historical")

# Fetch 2022-2026 data
start = datetime(2022, 1, 1)
end = datetime(2026, 1, 3)

all_data = fetcher.fetch_all_assets(start, end)

# Access individual assets
btc_data = all_data['BTC']
eth_data = all_data['ETH']
sol_data = all_data['SOL']

print(f"BTC: {len(btc_data)} candles")
print(f"ETH: {len(eth_data)} candles")
print(f"SOL: {len(sol_data)} candles")
```

---

### 4.2 Regime Classification Pipeline

**Objective**: Classify every historical candle into market regime.

```python
# File: strategic_intelligence/data_ingestion/regime_classifier.py

from market_context.context_engine import MarketContextEngine
import pandas as pd
from tqdm import tqdm

class HistoricalRegimeClassifier:
    """Classify historical candles into market regimes."""

    def __init__(self, context_engine: MarketContextEngine):
        self.context_engine = context_engine

    def classify_dataframe(
        self,
        ohlcv_data: pd.DataFrame,
        window_size: int = 200,
        asset: str = "BTC"
    ) -> pd.DataFrame:
        """
        Add regime classifications to OHLCV DataFrame.

        Args:
            ohlcv_data: DataFrame with OHLCV columns
            window_size: Lookback period for regime detection
            asset: Asset name for logging

        Returns:
            DataFrame with added columns:
            - regime
            - regime_confidence
            - volatility_regime
            - sentiment_direction
        """
        print(f"Classifying regimes for {asset}...")

        regimes = []

        # Need at least window_size candles to classify
        for i in tqdm(range(window_size, len(ohlcv_data))):
            # Get window
            window = ohlcv_data.iloc[i-window_size:i]

            # Classify using MarketContextEngine
            context = self.context_engine.analyze(window)

            regimes.append({
                'timestamp': ohlcv_data.iloc[i]['timestamp'],
                'regime': context.regime,
                'regime_confidence': context.regime_confidence,
                'volatility_regime': context.volatility_regime,
                'sentiment_direction': context.sentiment_direction,
                'volatility_20h': context.volatility_20  # Store for analysis
            })

        # Convert to DataFrame
        regime_df = pd.DataFrame(regimes)

        # Merge with original OHLCV data
        result = pd.merge(ohlcv_data, regime_df, on='timestamp', how='left')

        return result

    def classify_all_assets(
        self,
        asset_data: dict[str, pd.DataFrame]
    ) -> dict[str, pd.DataFrame]:
        """
        Classify regimes for all assets.

        Args:
            asset_data: {'BTC': df, 'ETH': df, 'SOL': df}

        Returns:
            Same structure with regime columns added
        """
        return {
            asset: self.classify_dataframe(df, asset=asset)
            for asset, df in asset_data.items()
        }
```

---

### 4.3 Baseline Storage Schema in Qdrant

**New Collection**: `sil_historical_baseline_v2`

```python
# File: memory/historical_baseline_schema.py

from dataclasses import dataclass
from datetime import datetime

@dataclass
class HistoricalBaseline:
    """Schema for historical strategy performance baseline."""

    # Identification
    asset: str  # "BTC", "ETH", "SOL"
    strategy: str  # "mean_reversion", "trend_following", etc.
    regime: str  # "ranging_low_vol", etc.

    # Performance metrics
    total_opportunities: int  # How many times this setup occurred
    win_rate: float  # Percentage of winners
    avg_rr_ratio: float  # Average reward:risk
    avg_trade_duration_hours: float
    sharpe_ratio: float
    max_drawdown_pct: float

    # Confidence indicators
    sample_period_start: datetime
    sample_period_end: datetime
    sample_confidence: float  # 0-1, based on sample size

    # Metadata
    last_updated: datetime
    data_version: str  # "2022-2026_v1"


def store_baseline_in_qdrant(
    memory_client,
    baseline: HistoricalBaseline
):
    """Store baseline in Qdrant for fast retrieval."""

    # Create embedding from regime characteristics
    # (reuse existing regime embedding logic)
    from market_context.context_engine import MarketContextEngine
    embedding = MarketContextEngine.encode_regime(baseline.regime)

    payload = {
        'asset': baseline.asset,
        'strategy': baseline.strategy,
        'regime': baseline.regime,
        'total_opportunities': baseline.total_opportunities,
        'win_rate': baseline.win_rate,
        'avg_rr_ratio': baseline.avg_rr_ratio,
        'avg_trade_duration_hours': baseline.avg_trade_duration_hours,
        'sharpe_ratio': baseline.sharpe_ratio,
        'max_drawdown_pct': baseline.max_drawdown_pct,
        'sample_period_start': baseline.sample_period_start.isoformat(),
        'sample_period_end': baseline.sample_period_end.isoformat(),
        'sample_confidence': baseline.sample_confidence,
        'last_updated': baseline.last_updated.isoformat(),
        'data_version': baseline.data_version
    }

    point_id = f"{baseline.asset}_{baseline.strategy}_{baseline.regime}"

    memory_client.client.upsert(
        collection_name='sil_historical_baseline_v2',
        points=[{
            'id': point_id,
            'vector': embedding,
            'payload': payload
        }]
    )


def retrieve_baseline(
    memory_client,
    asset: str,
    strategy: str,
    regime: str
) -> HistoricalBaseline:
    """Retrieve baseline from Qdrant."""

    point_id = f"{asset}_{strategy}_{regime}"

    result = memory_client.client.retrieve(
        collection_name='sil_historical_baseline_v2',
        ids=[point_id]
    )

    if not result:
        raise ValueError(f"No baseline found for {asset}/{strategy}/{regime}")

    payload = result[0].payload

    return HistoricalBaseline(
        asset=payload['asset'],
        strategy=payload['strategy'],
        regime=payload['regime'],
        total_opportunities=payload['total_opportunities'],
        win_rate=payload['win_rate'],
        avg_rr_ratio=payload['avg_rr_ratio'],
        avg_trade_duration_hours=payload['avg_trade_duration_hours'],
        sharpe_ratio=payload['sharpe_ratio'],
        max_drawdown_pct=payload['max_drawdown_pct'],
        sample_period_start=datetime.fromisoformat(payload['sample_period_start']),
        sample_period_end=datetime.fromisoformat(payload['sample_period_end']),
        sample_confidence=payload['sample_confidence'],
        last_updated=datetime.fromisoformat(payload['last_updated']),
        data_version=payload['data_version']
    )
```

---

### 4.4 Validation Criteria for Historical Performance Expectations

**Questions to Answer**:

1. **Sample Size Adequacy**:
   - Minimum 30 opportunities per strategy/regime/asset combo for statistical significance
   - Flag low-confidence baselines (< 30 samples)

2. **Regime Balance**:
   - Did we see all 10 regimes during 2022-2026?
   - Are some regimes under-represented? (e.g., euphoric bull runs rare)

3. **Market Cycle Coverage**:
   - 2022: Bear market ✅
   - 2023: Recovery/ranging ✅
   - 2024: Bull run ✅
   - 2025: Maturation ✅
   - Does our baseline cover full crypto cycle?

4. **Strategy Validity**:
   - Do strategies perform as expected in their "best" regimes?
   - Are there regimes where ALL strategies fail? (risk-off indicator)

**Validation Script**:
```python
def validate_historical_baselines(baselines: list[HistoricalBaseline]):
    """
    Validate that baselines are statistically significant and logically sound.
    """
    validation_report = {
        'total_baselines': len(baselines),
        'low_confidence': [],
        'missing_regimes': [],
        'anomalies': []
    }

    # Check 1: Sample size
    for baseline in baselines:
        if baseline.total_opportunities < 30:
            validation_report['low_confidence'].append({
                'asset': baseline.asset,
                'strategy': baseline.strategy,
                'regime': baseline.regime,
                'opportunities': baseline.total_opportunities,
                'note': 'Sample size < 30 - low statistical confidence'
            })

    # Check 2: Regime coverage
    all_regimes = set([
        'ranging_low_vol', 'ranging_medium_vol', 'ranging_high_vol',
        'trending_bullish_low_vol', 'trending_bullish_medium_vol', 'trending_bullish_high_vol',
        'trending_bearish_low_vol', 'trending_bearish_medium_vol', 'trending_bearish_high_vol',
        'uncertain'
    ])

    for asset in ['BTC', 'ETH', 'SOL']:
        asset_baselines = [b for b in baselines if b.asset == asset]
        covered_regimes = set([b.regime for b in asset_baselines])
        missing = all_regimes - covered_regimes

        if missing:
            validation_report['missing_regimes'].append({
                'asset': asset,
                'missing': list(missing),
                'note': f'These regimes never occurred or had insufficient data'
            })

    # Check 3: Logical anomalies
    for baseline in baselines:
        # Mean reversion should work best in ranging markets
        if baseline.strategy == 'mean_reversion' and 'ranging' in baseline.regime:
            if baseline.win_rate < 0.45:  # Expected ~50-60%
                validation_report['anomalies'].append({
                    'baseline': f"{baseline.asset}/{baseline.strategy}/{baseline.regime}",
                    'issue': f"Unexpectedly low win rate: {baseline.win_rate:.1%}",
                    'note': 'Mean reversion should perform well in ranging markets'
                })

        # Trend following should work best in trending markets
        if baseline.strategy == 'trend_following' and 'trending' in baseline.regime:
            if baseline.win_rate < 0.40:  # Expected ~40-50%
                validation_report['anomalies'].append({
                    'baseline': f"{baseline.asset}/{baseline.strategy}/{baseline.regime}",
                    'issue': f"Unexpectedly low win rate: {baseline.win_rate:.1%}",
                    'note': 'Trend following should capture trends'
                })

    return validation_report
```

---

## 5. Critical Discrepancies & Conflicts

**NOTE**: This section will be populated once the three agent reports are complete. Expected discrepancies to investigate:

### 5.1 Contradictory Recommendations

**Template for Analysis**:

| Issue | Alpha (BTC) | Beta (ETH) | Gamma (SOL) | Resolution |
|-------|-------------|------------|-------------|------------|
| Best strategy in ranging_low_vol | [TBD] | [TBD] | [TBD] | [TBD] |
| Optimal stop loss % | [TBD] | [TBD] | [TBD] | [TBD] |
| Max position size | [TBD] | [TBD] | [TBD] | [TBD] |
| Regime transition timing | [TBD] | [TBD] | [TBD] | [TBD] |

---

### 5.2 Asset-Specific Deviations from Expected Patterns

**Questions to Investigate**:

1. **Does SOL behave fundamentally differently?**
   - Expected: Higher volatility, more regime churn
   - If not observed: Why? Data quality? Different market structure?

2. **Does ETH track BTC or lead it?**
   - Expected: ETH follows BTC with slight lag
   - If ETH leads: Opportunity for BTC prediction
   - If uncorrelated: Diversification benefit

3. **Are there regime-specific correlations?**
   - Expected: High correlation in trending markets, lower in ranging
   - If opposite: Recalibrate risk model

---

### 5.3 Compounding Risks in Multi-Asset Trading

**Key Risks to Quantify**:

1. **Correlation Surge Risk**:
   - Normal: BTC-ETH = 0.85
   - Crisis: BTC-ETH = 0.98+
   - Impact: "Diversified" portfolio acts as single asset
   - Mitigation: Dynamic correlation monitoring, reduce total exposure in high vol

2. **Liquidity Asymmetry Risk**:
   - BTC: Deep liquidity, minimal slippage
   - SOL: Thinner markets, slippage risk on $100+ orders
   - Impact: SOL stop losses may not fill at expected price
   - Mitigation: Wider stops on SOL, smaller size

3. **Regime Desynchronization Risk**:
   - BTC in ranging_low_vol
   - ETH in trending_bullish_medium_vol
   - SOL in ranging_high_vol (choppy)
   - Impact: Strategies optimized for one regime fail on others
   - Mitigation: Asset-specific regime detection (not portfolio-wide)

4. **Sequential Loss Amplification**:
   - Lose on BTC → Reduce capital
   - Lose on ETH with reduced capital → Deeper drawdown
   - Lose on SOL → Circuit breaker trips, but capital depleted
   - Impact: Multi-asset losses compound faster than single-asset
   - Mitigation: Circuit breaker BEFORE multi-asset exhaustion

---

## 6. Actionable Implementation Priority List

### 6.1 Week-by-Week Implementation Plan

#### Week 1: Historical Data Collection (Alpha, Beta, Gamma Begin)
**Goal**: Fetch and cache 2-3 years of BTC, ETH, SOL data

**Tasks**:
- [ ] Implement Kraken API fetcher (KrakenHistoricalFetcher)
- [ ] Fetch BTC data (2022-01-01 to 2026-01-03)
- [ ] Fetch ETH data (same period)
- [ ] Fetch SOL data (same period)
- [ ] Cache all data in Parquet format
- [ ] Validate data quality (no gaps, OHLC consistency)

**Deliverable**: `historical_data/` directory with 3 Parquet files

**Estimated Time**: 8 hours
- Kraken fetcher: 3 hours
- Data fetching: 2 hours (includes API delays)
- Validation: 2 hours
- Documentation: 1 hour

---

#### Week 2: Regime Classification & Agent Analysis
**Goal**: Classify all historical candles into regimes, begin individual asset analysis

**Tasks**:
- [ ] Run `HistoricalRegimeClassifier` on BTC data
- [ ] Run on ETH data
- [ ] Run on SOL data
- [ ] **Agent Alpha**: Analyze BTC regime distribution, transitions, volatility
- [ ] **Agent Beta**: Analyze ETH vs BTC deviations
- [ ] **Agent Gamma**: Analyze SOL extreme events
- [ ] Generate regime transition matrices for each asset
- [ ] Store regime-classified data

**Deliverable**:
- `historical_data/BTC_regimes.parquet`
- `historical_data/ETH_regimes.parquet`
- `historical_data/SOL_regimes.parquet`
- Agent Alpha preliminary report

**Estimated Time**: 12 hours
- Regime classification: 4 hours (compute-intensive)
- Transition analysis: 3 hours
- Agent analysis: 5 hours

---

#### Week 3: Strategy Backtesting & Baseline Calculation
**Goal**: Calculate historical performance for each strategy/regime/asset combination

**Tasks**:
- [ ] Implement `BaselinePerformanceCalculator`
- [ ] Backtest mean_reversion on BTC (all regimes)
- [ ] Backtest trend_following on BTC
- [ ] Backtest breakout_capture on BTC
- [ ] Repeat for ETH (all strategies)
- [ ] Repeat for SOL (all strategies)
- [ ] Calculate win rates, R:R ratios, Sharpe, max drawdown
- [ ] **Agents Beta & Gamma**: Complete individual reports
- [ ] Store baselines in Qdrant

**Deliverable**:
- Populated `sil_historical_baseline_v2` Qdrant collection
- Agent Beta final report
- Agent Gamma final report

**Estimated Time**: 16 hours
- Backtesting engine: 6 hours
- Running backtests: 5 hours
- Baseline storage: 2 hours
- Agent reports: 3 hours

---

#### Week 4: Multi-Asset Synthesis & Integration (Agent Delta)
**Goal**: Synthesize all findings, integrate into SIL

**Tasks**:
- [ ] **Agent Delta**: Read Alpha, Beta, Gamma reports
- [ ] Calculate cross-asset correlation matrices
- [ ] Build multi-asset risk management rules
- [ ] Implement correlation-weighted position sizing
- [ ] Implement asset-specific circuit breakers
- [ ] Update `StrategySelector` to use historical baselines
- [ ] Update `LearningEngine` to compare vs baselines
- [ ] Create unified synthesis report (THIS DOCUMENT, completed)
- [ ] Integration testing

**Deliverable**:
- Synthesis report (this document, fully populated)
- Updated SIL codebase with multi-asset support
- Integration test suite

**Estimated Time**: 12 hours
- Synthesis analysis: 4 hours
- Code integration: 5 hours
- Testing: 3 hours

---

### 6.2 Which Asset to Start With

**Phase 1: BTC Only (Recommended)**

**Rationale**:
1. **Lowest volatility** = easiest to learn from
2. **Most liquid** = best fills, minimal slippage
3. **Most regime stability** = consistent behavior
4. **Best historical data** = longest track record
5. **Lower correlation risk** = isolated learning

**Success Criteria Before Adding ETH**:
- [ ] 20+ successful BTC trades
- [ ] Win rate ≥ baseline expectation (within 5%)
- [ ] Circuit breaker never tripped due to strategy failure (only market regime shifts)
- [ ] Regime detection accuracy validated
- [ ] Stop loss and profit target execution verified

**Estimated Duration**: 3-4 weeks of paper trading

---

**Phase 2: BTC + ETH (Moderate Diversification)**

**Rationale**:
1. **Moderate correlation** (0.85) = some diversification benefit
2. **ETH volatility** (1.3x BTC) = manageable step up
3. **Liquid markets** = reliable execution
4. **Test correlation-based risk management** = validate multi-asset logic

**Success Criteria Before Adding SOL**:
- [ ] 15+ successful ETH trades
- [ ] Correlation-weighted position sizing validated
- [ ] No concentration limit breaches
- [ ] Portfolio circuit breaker logic tested
- [ ] Both assets simultaneously profitable over 2+ weeks

**Estimated Duration**: 2-3 weeks of paper trading

---

**Phase 3: BTC + ETH + SOL (Full Multi-Asset)**

**Rationale**:
1. **SOL volatility** (1.8x BTC) = high risk/reward
2. **Complete asset coverage** = full strategy diversity
3. **Maximum opportunity set** = more trades

**Success Criteria**:
- [ ] 10+ successful SOL trades
- [ ] Volatility-adjusted stops working correctly
- [ ] Asset-specific circuit breakers validated
- [ ] Risk budget allocation functioning
- [ ] Portfolio-level risk < daily/weekly limits

**Estimated Duration**: 2-3 weeks of paper trading

---

**Total Time to Full Multi-Asset: 7-10 weeks of paper trading**

---

### 6.3 Technical Debt & Gaps

**Current Gaps** (to address before multi-asset):

1. **Qdrant Collection for Historical Baselines**:
   - Status: NOT CREATED
   - Action: Run `create_collection('sil_historical_baseline_v2')`
   - Priority: HIGH
   - Est. Time: 1 hour

2. **Asset-Specific Position Sizer**:
   - Status: PARTIALLY EXISTS (single-asset)
   - Action: Extend `PositionSizer` to accept asset parameter
   - Priority: HIGH
   - Est. Time: 3 hours

3. **Correlation Calculator**:
   - Status: NOT IMPLEMENTED
   - Action: Create `CorrelationAnalyzer` class
   - Priority: HIGH
   - Est. Time: 4 hours

4. **Multi-Asset RiskManager State Persistence**:
   - Status: SINGLE-ASSET ONLY
   - Action: Extend `daily_stats.json` schema to track per-asset metrics
   - Priority: MEDIUM
   - Est. Time: 2 hours

5. **Asset-Specific Strategy Configuration**:
   - Status: SINGLE CONFIG FILE
   - Action: Extend `strategies.yaml` with asset-specific overrides
   - Priority: MEDIUM
   - Est. Time: 2 hours

**Total Technical Debt**: ~12 hours to resolve before full multi-asset deployment

---

### 6.4 Quick Wins vs Long-Term Infrastructure

#### Quick Wins (< 4 hours each)

1. **Add Asset Parameter to Decision API**:
   ```python
   # Before
   decision = sil.analyze_and_decide(ohlcv_df, capital, current_positions)

   # After
   decision = sil.analyze_and_decide(ohlcv_df, capital, current_positions, asset="BTC")
   ```
   - Impact: Enables asset-aware decisions
   - Time: 2 hours

2. **Fetch Historical Data for BTC**:
   - Already designed (KrakenHistoricalFetcher)
   - Just execute and cache
   - Impact: Foundation for all analysis
   - Time: 3 hours

3. **Create Baseline Qdrant Collection**:
   ```python
   from memory.qdrant_client import QdrantMemoryClient
   client = QdrantMemoryClient()
   client.create_collection('sil_historical_baseline_v2')
   ```
   - Impact: Enables baseline storage
   - Time: 1 hour

4. **Implement Asset-Specific Stop Loss Multipliers**:
   ```python
   STOP_LOSS_MULTIPLIERS = {
       'BTC': 1.0,
       'ETH': 1.3,
       'SOL': 1.8
   }
   stop_loss = base_stop_loss * STOP_LOSS_MULTIPLIERS[asset]
   ```
   - Impact: Immediate volatility adjustment
   - Time: 1 hour

**Total Quick Wins Time**: ~7 hours

---

#### Long-Term Infrastructure (> 8 hours each)

1. **Full Backtesting Engine**:
   - Simulate all strategies on 3 years of data
   - Calculate comprehensive performance metrics
   - Store baselines in Qdrant
   - Impact: True intelligence foundation
   - Time: 16 hours

2. **Real-Time Correlation Monitoring**:
   - Calculate rolling correlations
   - Adjust position sizing dynamically
   - Detect correlation regime shifts
   - Impact: Advanced risk management
   - Time: 12 hours

3. **Regime Transition Prediction**:
   - Build transition probability matrices
   - Predict regime shifts before they happen
   - Adjust strategies preemptively
   - Impact: Predictive intelligence
   - Time: 20 hours

4. **Multi-Asset Learning Engine**:
   - Learn from cross-asset patterns
   - Adapt parameters based on multi-asset performance
   - Optimize portfolio-level Sharpe
   - Impact: True symbiotic intelligence
   - Time: 24 hours

**Total Long-Term Infrastructure**: ~72 hours

---

## 7. Implementation Recommendations

### 7.1 Critical Path to Multi-Asset Trading

**Minimum Viable Multi-Asset SIL** (40 hours total):

1. **Historical Data Collection** (8 hours)
   - ✅ Fetch BTC, ETH, SOL from Kraken
   - ✅ Cache in Parquet
   - ✅ Validate data quality

2. **Regime Classification** (12 hours)
   - ✅ Run MarketContextEngine on all data
   - ✅ Store regime-classified data
   - ✅ Generate regime distribution stats

3. **Strategy Backtesting** (16 hours)
   - ✅ Backtest 3 strategies × 3 assets × 10 regimes = 90 baselines
   - ✅ Store in Qdrant
   - ✅ Validate statistical significance

4. **Multi-Asset Integration** (4 hours)
   - ✅ Add asset parameter to SIL API
   - ✅ Implement volatility multipliers
   - ✅ Add asset-specific circuit breakers

**After 40 hours**: Can trade BTC, ETH, SOL with historical context

---

### 7.2 Recommended Starting Point

**Option A: Complete Sprint 2 First (Recommended)**
- Finish HIGH-6 (Qdrant pagination) - 2 hours
- Finish HIGH-8 (Unit tests) - 6 hours
- **Then** begin historical context work
- **Rationale**: Solid foundation before adding complexity

**Option B: Parallel Sprint 2 + Historical Context**
- Captain: Complete HIGH-8 (tests)
- First Mate: Begin historical data collection
- **Rationale**: Faster time to multi-asset, but more context switching

**Option C: Historical Context First**
- Delay Sprint 2 completion
- Focus entirely on historical intelligence
- **Rationale**: True intelligence is more valuable than edge-case safety

**Recommendation**: **Option A** - finish Sprint 2, then full focus on historical context.

**Reasoning**:
- Sprint 2 is 78% complete, only 8 hours to finish
- Historical context is 40+ hour project
- Better to complete one thing fully than leave both incomplete
- Unit tests (HIGH-8) will help validate multi-asset logic later

---

### 7.3 Success Metrics

**After Historical Context Implementation, Measure**:

1. **Baseline Accuracy**:
   - Live win rates within ±10% of historical baselines
   - R:R ratios within ±20% of historical
   - If outside range: Regime detection or strategy execution issue

2. **Regime Prediction**:
   - Regime transitions predicted ≥60% of the time
   - False regime changes < 10% (stability)

3. **Multi-Asset Correlation**:
   - Effective exposure ≤ concentration limits 100% of time
   - No correlation-induced circuit breaker trips

4. **Strategy Optimization**:
   - Portfolio Sharpe ratio > best single-asset Sharpe
   - Diversification benefit measurable (lower volatility)

---

## 8. Next Steps

**Immediate Actions** (this session):

1. ✅ **Complete this synthesis framework** (Agent Delta task)
2. ⏳ **Assign historical analysis tasks**:
   - Agent Alpha: BTC 2022-2026 regime/volatility/strategy analysis
   - Agent Beta: ETH comparative analysis vs BTC
   - Agent Gamma: SOL extreme volatility and risk analysis
3. ⏳ **Decide on implementation path** (Option A, B, or C above)

**Next Session Actions**:

1. **IF Sprint 2 complete**:
   - Begin KrakenHistoricalFetcher implementation
   - Fetch BTC data as proof of concept
   - Run regime classification on BTC

2. **IF Agents Alpha/Beta/Gamma complete**:
   - Return to this document
   - Populate all [TBD] sections with concrete findings
   - Finalize multi-asset parameter adjustments

---

## Appendices

### Appendix A: Expected Agent Report Structures

**Agent Alpha Template** (Bitcoin Historical Analysis):
```markdown
# Agent Alpha: Bitcoin Historical Market Analysis (2022-2026)

## 1. Data Summary
- Total candles: [X]
- Date range: 2022-01-01 to 2026-01-03
- Data quality: [gaps, anomalies, etc.]

## 2. Regime Distribution
- ranging_low_vol: [X]% of time
- [etc. for all regimes]

## 3. Volatility Analysis
- Mean 20-day volatility: [X]%
- 95th percentile: [X]%
- 99th percentile (tail events): [X]%
- Volatility by regime: [table]

## 4. Strategy Performance
### Mean Reversion
- Best regimes: [list]
- Win rate: [X]%
- Avg R:R: [X]
- Total opportunities: [X]

[etc. for all strategies]

## 5. Regime Transitions
- Transition matrix: [table]
- Average regime duration: [X] hours
- Most stable regime: [X]
- Most volatile regime: [X]

## 6. Key Findings
- [Bullet points]

## 7. Recommendations
- [Bullet points]
```

**Agent Beta Template** (Ethereum Analysis):
```markdown
# Agent Beta: Ethereum Historical Behavior Analysis (2022-2026)

## 1. Data Summary
[Same as Alpha]

## 2. BTC Comparison
- Volatility multiplier vs BTC: [X.XX]x
- Correlation with BTC: [X.XX]
- Regime alignment with BTC: [X]% of time

## 3. Unique ETH Characteristics
- [What makes ETH different from BTC?]

## 4. Strategy Performance
[Same structure as Alpha, but with BTC comparisons]

## 5. Risk Considerations
- [ETH-specific risks vs BTC]

## 6. Recommendations
- [ETH parameter adjustments vs BTC baseline]
```

**Agent Gamma Template** (Solana Analysis):
```markdown
# Agent Gamma: Solana Historical Market Analysis & Risk Management (2022-2026)

## 1. Data Summary
[Same as Alpha]

## 2. Extreme Volatility Analysis
- Volatility multiplier vs BTC: [X.XX]x
- Frequency of >10% daily moves: [X]%
- Flash crash events: [list with dates]

## 3. SOL-Specific Risks
- Liquidity risk
- Network downtime events (if any)
- Correlation breakdown events

## 4. Strategy Performance
[Same structure, with emphasis on volatility adaptation]

## 5. Risk Management Recommendations
- Circuit breaker thresholds
- Position size limits
- Stop loss widths

## 6. Recommendations
- [When to trade SOL, when to avoid]
```

---

### Appendix B: Validation Checklist

Before deploying multi-asset SIL, validate:

**Data Quality**:
- [ ] No gaps in OHLCV data > 2 hours
- [ ] All OHLC relationships valid (high ≥ low, etc.)
- [ ] No NaN or infinite values
- [ ] Timestamps monotonically increasing

**Regime Classification**:
- [ ] All 10 regimes observed in historical data
- [ ] Regime transitions logical (no instant flips)
- [ ] Regime confidence scores calibrated

**Baseline Quality**:
- [ ] All strategy/regime/asset combos have ≥30 samples OR flagged as low-confidence
- [ ] Win rates between 30-70% (outside this = suspicious)
- [ ] R:R ratios > 1.0 for viable strategies
- [ ] Sharpe ratios realistic (< 3.0 for crypto)

**Multi-Asset Logic**:
- [ ] Correlation matrix symmetric and valid (-1 to +1)
- [ ] Position sizing never negative
- [ ] Circuit breakers trip correctly in backtests
- [ ] Risk budget allocation sums to 100%

**Integration**:
- [ ] SIL accepts asset parameter
- [ ] Baselines retrieved correctly from Qdrant
- [ ] Learning engine uses baselines for comparison
- [ ] Transparency logs include asset in all events

---

## Conclusion

This synthesis framework is ready to receive inputs from Agents Alpha (BTC), Beta (ETH), and Gamma (SOL). Once their historical analyses are complete, this document will transform from a template into a concrete, actionable roadmap for multi-asset trading intelligence.

**Current Status**:
- ✅ Framework complete
- ❌ Agent reports pending
- ❌ Concrete findings pending
- ❌ Final recommendations pending

**Estimated Time to Full Synthesis**: 40-50 hours (including agent work)

**Next Action**: Captain decides implementation path, assigns agent tasks.

---

**Document Version**: 1.0 (Framework)
**Last Updated**: 2026-01-03
**Agent**: Delta (Synthesis Specialist)
**Status**: AWAITING AGENT INPUTS
