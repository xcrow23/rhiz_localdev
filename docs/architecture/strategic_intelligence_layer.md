# Strategic Intelligence Layer Architecture
**Version**: 1.0.0
**Date**: 2026-01-03
**Status**: DESIGN - Ready for Implementation
**Author**: First Mate (Claude Sonnet 4.5) with Captain oversight

---

## Executive Summary

The **Strategic Intelligence Layer** (SIL) transforms Rhiz from a collection of automated workflows into a genuine **strategic trading platform for the dyad**. It sits between high-level intent and low-level execution, providing market understanding, strategy selection, risk management, and learning capabilities.

**Current Gap**: We have infrastructure (Fathom Commander, n8n workflows, Qdrant memory) but no strategic cognition—no layer that understands market context, makes strategic decisions, learns from outcomes, or provides transparent reasoning.

**Solution**: A cognitive layer that implements the skill compression research architecture while maintaining HAIST principles of symbiotic partnership.

---

## Architectural Philosophy

### Alignment with Research Foundations

This design integrates three core research frameworks:

1. **HAIST Seven Principles**
   - Complementary cognitive architecture: AI handles pattern recognition and data synthesis; Captain retains teleological authority
   - Transformative agency enhancement: Intelligence layer enhances rather than replaces human decision-making
   - Authentic problem-centered engagement: Embedded in real trading, not paper exercises

2. **SynLang Cognitive Authority Distribution**
   ```
   α(context) = authority level [0,1]

   Market analysis: α ≈ 0.2 (AI-led, human oversight)
   Strategy selection: α ≈ 0.5 (collaborative)
   Risk decisions: α ≈ 0.7 (human-led)
   Ethical constraints: α ≈ 0.9 (human authority)
   ```

3. **Skill Compression 4-Layer Model**
   - Recognition: Fast pattern matching for market regimes
   - Retrieval: Load relevant strategy knowledge
   - Composition: Combine primitives into strategic responses
   - Execution: Adaptive execution through Fathom Commander

---

## Layer Architecture

### Conceptual Stack

```
┌─────────────────────────────────────────────────────────────┐
│  TELEOLOGICAL LAYER (Captain)                                │
│  - Portfolio goals                                           │
│  - Risk tolerance                                            │
│  - Strategic direction                                       │
└────────────────────┬─────────────────────────────────────────┘
                     │
         ┌───────────▼────────────────────────────────────────┐
         │  STRATEGIC INTELLIGENCE LAYER (First Mate)         │
         │  ┌──────────────────────────────────────────────┐ │
         │  │ 1. Market Context Engine                      │ │
         │  │    - Regime detection                         │ │
         │  │    - Sentiment synthesis                      │ │
         │  │    - Volatility mapping                       │ │
         │  └──────────────┬───────────────────────────────┘ │
         │                 │                                  │
         │  ┌──────────────▼───────────────────────────────┐ │
         │  │ 2. Strategy Selection & Adaptation           │ │
         │  │    - Pattern recognition                     │ │
         │  │    - Strategy matching                       │ │
         │  │    - Parameter tuning                        │ │
         │  └──────────────┬───────────────────────────────┘ │
         │                 │                                  │
         │  ┌──────────────▼───────────────────────────────┐ │
         │  │ 3. Risk & Position Management                │ │
         │  │    - Portfolio allocation                    │ │
         │  │    - Position sizing                         │ │
         │  │    - Exit planning                           │ │
         │  └──────────────┬───────────────────────────────┘ │
         │                 │                                  │
         │  ┌──────────────▼───────────────────────────────┐ │
         │  │ 4. Learning & Memory Integration             │ │
         │  │    - Outcome tracking                        │ │
         │  │    - Pattern discovery                       │ │
         │  │    - Strategy evolution                      │ │
         │  └──────────────┬───────────────────────────────┘ │
         │                 │                                  │
         │  ┌──────────────▼───────────────────────────────┐ │
         │  │ 5. Transparency & Traceability               │ │
         │  │    - TRACE_FE confidence scores              │ │
         │  │    - Reasoning chains                        │ │
         │  │    - Decision logging                        │ │
         │  └──────────────────────────────────────────────┘ │
         └────────────────────┬────────────────────────────────┘
                              │
         ┌────────────────────▼────────────────────────────────┐
         │  EXECUTION LAYER (Current Infrastructure)           │
         │  - Fathom Commander (tools)                         │
         │  - n8n workflows (automation)                       │
         │  - Kraken API (execution)                           │
         └─────────────────────────────────────────────────────┘
```

---

## Component Specifications

### 1. Market Context Engine

**Purpose**: Transform raw market data into actionable market understanding.

**Inputs**:
- OHLCV data (Kraken API via Fathom Commander)
- Order book depth
- Trade volume patterns
- External sentiment (future: news, social)

**Processing**:
```python
# Regime Detection (Recognition Layer)
def detect_market_regime(ohlcv: pd.DataFrame) -> MarketRegime:
    """
    Classify market into one of:
    - trending_bull
    - trending_bear
    - ranging_high_vol
    - ranging_low_vol
    - breakout_pending
    - crash_recovery

    Uses: ATR, Bollinger Bands, trend strength, volume profile
    """

# Volatility Mapping
def map_volatility_regime(ohlcv: pd.DataFrame) -> VolatilityRegime:
    """
    Classify volatility environment:
    - expanding: Risk-off signal
    - contracting: Opportunity building
    - explosive: Breakout or crash
    - stable: Normal conditions
    """

# Sentiment Synthesis
def synthesize_market_sentiment(market_data: dict) -> Sentiment:
    """
    Aggregate signals into coherent sentiment:
    - order_book_pressure (bid/ask imbalance)
    - volume_trend (accumulation vs distribution)
    - price_momentum (directional strength)

    Returns: confidence-weighted sentiment vector
    """
```

**Outputs**:
```yaml
market_context:
  regime: "ranging_low_vol"
  regime_confidence: 0.73
  volatility: "contracting"
  volatility_percentile: 32  # Historical percentile
  sentiment:
    direction: "neutral_bullish"
    confidence: 0.61
    signals:
      - orderbook_pressure: 0.52  # Slight buy pressure
      - volume_trend: -0.15       # Declining volume
      - momentum: 0.28            # Weak upward
  timestamp: "2026-01-03T22:30:00Z"

  # TRACE_FE (SynLang transparency)
  trace_factors:
    - factor: "ranging_market"
      explanation: "Price oscillating within 2% band for 48h"
      confidence: 0.82
    - factor: "low_volatility"
      explanation: "ATR at 18th percentile (30-day)"
      confidence: 0.73
    - factor: "neutral_sentiment"
      explanation: "Mixed signals, no dominant pressure"
      confidence: 0.61
```

**Implementation Priority**: HIGH (Phase 1)

---

### 2. Strategy Selection & Adaptation

**Purpose**: Match market context to appropriate strategic response.

**Strategy Library** (Skill Compression: Retrieval Layer):

```yaml
strategies:
  mean_reversion:
    description: "Trade oscillations within range"
    best_regimes: ["ranging_low_vol", "ranging_high_vol"]
    min_confidence: 0.65
    parameters:
      entry_threshold: 0.5  # Std deviations from mean
      exit_threshold: 0.1
      stop_loss: 0.03       # 3% max loss

  trend_following:
    description: "Ride established trends"
    best_regimes: ["trending_bull", "trending_bear"]
    min_confidence: 0.70
    parameters:
      entry_signal: "ema_crossover"
      trailing_stop: 0.05   # 5% trailing
      profit_target: 0.15   # 15% gain target

  breakout_capture:
    description: "Enter on volatility expansion"
    best_regimes: ["breakout_pending", "ranging_high_vol"]
    min_confidence: 0.75
    parameters:
      trigger: "bollinger_squeeze + volume_spike"
      position_size: 0.15   # Smaller size, higher risk
      tight_stop: 0.02      # 2% stop

  accumulation_dca:
    description: "Steady accumulation in stable markets"
    best_regimes: ["ranging_low_vol", "crash_recovery"]
    min_confidence: 0.50
    parameters:
      frequency: "weekly"
      amount_usd: 10
      adaptive: true        # Adjust based on volatility

  risk_off:
    description: "Preserve capital in uncertain conditions"
    best_regimes: ["crash_recovery", "expanding_volatility"]
    min_confidence: 0.80
    parameters:
      action: "hold_or_exit"
      max_exposure: 0.20    # 20% of portfolio max
```

**Selection Algorithm** (Skill Compression: Composition Layer):

```python
def select_strategy(
    market_context: MarketContext,
    portfolio_state: PortfolioState,
    constraints: RiskConstraints
) -> StrategyDecision:
    """
    Multi-factor strategy selection with confidence scoring.

    Considers:
    1. Regime match (primary)
    2. Historical performance in similar contexts (from memory)
    3. Current portfolio exposure
    4. Risk budget available
    5. Captain's strategic direction
    """

    # Score each strategy
    scored_strategies = []
    for strategy in strategy_library:
        regime_match = score_regime_fit(strategy, market_context)
        historical_perf = query_memory_performance(strategy, market_context)
        risk_fit = check_risk_constraints(strategy, constraints)

        composite_score = (
            0.5 * regime_match +
            0.3 * historical_perf +
            0.2 * risk_fit
        )

        scored_strategies.append({
            "strategy": strategy,
            "score": composite_score,
            "confidence": calculate_confidence(regime_match, historical_perf),
            "trace": build_trace_factors(strategy, market_context)
        })

    # Select highest scoring strategy above confidence threshold
    best_strategy = max(scored_strategies, key=lambda x: x["score"])

    if best_strategy["confidence"] < best_strategy["strategy"].min_confidence:
        return StrategyDecision(
            action="wait",
            reasoning="No strategy meets confidence threshold",
            trace=best_strategy["trace"]
        )

    return StrategyDecision(
        action="activate",
        strategy=best_strategy["strategy"],
        parameters=adapt_parameters(best_strategy, market_context),
        confidence=best_strategy["confidence"],
        trace=best_strategy["trace"]
    )
```

**Outputs**:
```yaml
strategy_decision:
  timestamp: "2026-01-03T22:30:00Z"
  selected_strategy: "mean_reversion"
  confidence: 0.71
  parameters:
    entry_threshold: 0.45  # Adapted from base 0.5
    exit_threshold: 0.12   # Adapted from base 0.1
    stop_loss: 0.03

  reasoning:
    primary: "Ranging market with low volatility favors mean reversion"
    secondary: "Strategy has 68% win rate in similar regimes (from memory)"
    risk_assessment: "Within risk budget, appropriate for $52 portfolio"

  trace_factors:
    - factor: "regime_match"
      explanation: "ranging_low_vol strongly matches mean_reversion profile"
      confidence: 0.82
    - factor: "historical_performance"
      explanation: "7 of 10 similar contexts resulted in profitable trades"
      confidence: 0.68
    - factor: "risk_compatibility"
      explanation: "3% stop loss within 5% max daily loss tolerance"
      confidence: 0.95

  alternatives_considered:
    - strategy: "accumulation_dca"
      score: 0.63
      reason_not_selected: "Lower expected return in current regime"
    - strategy: "risk_off"
      score: 0.41
      reason_not_selected: "Market conditions not threatening"
```

**Implementation Priority**: HIGH (Phase 1)

---

### 3. Risk & Position Management

**Purpose**: Translate strategy into concrete position sizing and risk controls.

**Position Sizing Framework**:

```python
class PositionSizer:
    """
    Kelly Criterion-inspired but conservative.
    Never risk more than makes sense for portfolio size.
    """

    def calculate_position_size(
        self,
        strategy: Strategy,
        market_context: MarketContext,
        portfolio_value: float,
        risk_params: RiskParams
    ) -> PositionSize:
        """
        Inputs:
        - strategy.stop_loss (e.g., 0.03 for 3%)
        - strategy.win_rate (from historical performance)
        - portfolio_value (current total)
        - risk_params.max_risk_per_trade (e.g., 0.02 for 2%)

        Output:
        - position_size_usd
        - position_size_btc
        - risk_amount_usd
        - expected_value
        """

        # Max risk per trade (portfolio risk tolerance)
        max_risk_usd = portfolio_value * risk_params.max_risk_per_trade

        # Position size based on stop loss
        # If stop = 3%, and we risk $1, position size = $1 / 0.03 = $33.33
        position_size_usd = max_risk_usd / strategy.stop_loss

        # Volatility adjustment
        volatility_scalar = self._volatility_adjustment(market_context)
        position_size_usd *= volatility_scalar

        # Confidence adjustment
        confidence_scalar = strategy.confidence / 1.0
        position_size_usd *= confidence_scalar

        # Portfolio allocation cap (never more than X% in one position)
        max_allocation = portfolio_value * risk_params.max_position_size
        position_size_usd = min(position_size_usd, max_allocation)

        # Convert to BTC
        btc_price = get_current_price()
        position_size_btc = position_size_usd / btc_price

        return PositionSize(
            usd=position_size_usd,
            btc=position_size_btc,
            risk_amount=max_risk_usd,
            expected_value=self._calculate_ev(strategy, position_size_usd)
        )
```

**Risk Controls**:

```yaml
risk_framework:
  portfolio_level:
    max_total_risk: 0.10           # Never risk more than 10% of portfolio
    max_daily_loss: 0.05            # Circuit breaker at 5% daily loss
    max_position_size: 0.30         # No single position > 30% of portfolio
    max_correlated_exposure: 0.50   # Limit correlated positions

  trade_level:
    max_risk_per_trade: 0.02        # 2% risk per trade
    required_reward_ratio: 2.0      # Minimum 2:1 reward:risk
    min_confidence: 0.60            # Don't trade below 60% confidence

  operational:
    max_trades_per_day: 10
    max_trades_per_hour: 3
    cooldown_after_loss: 1h         # Wait 1h after losing trade
    cooldown_after_3_losses: 24h    # Stop trading after 3 consecutive losses

  approval_thresholds:
    auto_approve: 20                # Trades <$20 auto-approve
    captain_review: 50              # $20-50 requires review
    captain_explicit: 100           # >$50 requires explicit approval
```

**Outputs**:
```yaml
position_decision:
  timestamp: "2026-01-03T22:30:00Z"
  action: "enter_long"
  pair: "XXBTZUSD"

  sizing:
    position_size_usd: 8.42
    position_size_btc: 0.00008600
    risk_amount_usd: 1.05           # 2% of $52.68 portfolio
    stop_loss_price: 97200          # 3% below entry
    entry_price: 98000              # Current market

  risk_metrics:
    risk_percent: 0.02              # 2% of portfolio
    reward_risk_ratio: 2.5          # 2.5:1 target
    expected_value: 0.42            # Based on strategy win rate
    confidence: 0.71

  approvals:
    required: false                 # <$20, auto-approved
    captain_notified: true

  trace_factors:
    - factor: "conservative_sizing"
      explanation: "Position sized for 2% portfolio risk"
      confidence: 1.0
    - factor: "volatility_adjusted"
      explanation: "Size reduced 15% due to low liquidity window"
      confidence: 0.82
    - factor: "confidence_scaled"
      explanation: "Size scaled by strategy confidence (0.71)"
      confidence: 0.71
```

**Implementation Priority**: HIGH (Phase 1)

---

### 4. Learning & Memory Integration

**Purpose**: Enable the system to learn from outcomes and improve over time.

**Memory Schema** (Qdrant integration):

```python
@dataclass
class TradingMemory:
    """
    Vector embedding of trading decision + outcome.
    Stored in Qdrant for semantic retrieval.
    """

    # Decision context
    timestamp: datetime
    market_context: MarketContext
    strategy_used: str
    strategy_parameters: dict

    # Position details
    entry_price: float
    position_size: float
    stop_loss: float
    target_price: float

    # Outcome
    exit_price: float
    exit_reason: str  # "target_hit", "stop_loss", "manual_exit"
    pnl_usd: float
    pnl_percent: float
    duration_hours: float

    # Learning metadata
    what_worked: List[str]
    what_failed: List[str]
    surprises: List[str]
    adaptations_needed: List[str]

    # Confidence retrospective
    initial_confidence: float
    outcome_validated: bool
    confidence_calibration_error: float
```

**Learning Loops**:

```python
class StrategyLearner:
    """
    Continuously improve strategy selection and parameter tuning.
    """

    def learn_from_trade(self, trade: TradingMemory):
        """
        After each trade, update:
        1. Strategy performance statistics
        2. Parameter effectiveness
        3. Regime detection accuracy
        4. Confidence calibration
        """

        # Update strategy statistics
        self._update_win_rate(trade.strategy_used, trade.pnl_usd > 0)
        self._update_avg_return(trade.strategy_used, trade.pnl_percent)
        self._update_drawdown_stats(trade.strategy_used, trade.pnl_percent)

        # Parameter learning
        if trade.pnl_usd > 0:
            self._reinforce_parameters(trade.strategy_used, trade.strategy_parameters)
        else:
            self._penalize_parameters(trade.strategy_used, trade.strategy_parameters)

        # Confidence calibration
        self._calibrate_confidence(
            predicted=trade.initial_confidence,
            actual=1.0 if trade.pnl_usd > 0 else 0.0
        )

        # Store in Qdrant for future retrieval
        self.memory.store(trade)

    def query_similar_contexts(self, current_context: MarketContext) -> List[TradingMemory]:
        """
        Retrieve trades from similar market contexts.
        Uses semantic similarity on market_context embedding.
        """
        return self.memory.query(
            vector=embed(current_context),
            limit=10,
            filter={"success": True}  # Learn from winners
        )

    def generate_insights(self) -> List[Insight]:
        """
        Periodic analysis to discover patterns:
        - Which strategies work in which regimes?
        - Which parameter ranges are optimal?
        - What mistakes are we repeating?
        """
        insights = []

        # Pattern discovery
        for strategy in self.strategies:
            performance_by_regime = self._analyze_regime_performance(strategy)
            insights.append({
                "type": "regime_performance",
                "strategy": strategy,
                "findings": performance_by_regime
            })

        # Mistake patterns
        losing_trades = self.memory.filter(pnl_usd__lt=0)
        common_mistakes = self._cluster_similar_losses(losing_trades)
        insights.append({
            "type": "common_mistakes",
            "patterns": common_mistakes
        })

        return insights
```

**Integration with Checkpoints**:

Every session checkpoint includes a `learning_digest`:

```yaml
learning_digest:
  session: "session_1767478574460"
  period: "2026-01-03 to 2026-01-03"

  trades_executed: 2
  trades_won: 1
  trades_lost: 1
  win_rate: 0.50
  avg_return: -0.02  # -2% average
  sharpe_ratio: null  # Not enough data

  insights_discovered:
    - "Mean reversion worked in ranging_low_vol (1/1 success)"
    - "Trend following failed in ranging market (0/1 success)"
    - "Entry timing: 15-minute delay reduced slippage by 0.3%"

  parameters_adapted:
    mean_reversion:
      entry_threshold: 0.45  # Reduced from 0.50 (working well)
      exit_threshold: 0.12   # Increased from 0.10 (too tight)

  mistakes_identified:
    - "Trend following strategy selected despite low confidence (0.62)"
    - "Should have waited for volatility confirmation"

  next_session_focus:
    - "Test mean reversion with refined parameters"
    - "Build volatility confirmation signal before trend trades"
```

**Implementation Priority**: MEDIUM (Phase 2)

---

### 5. Transparency & Traceability

**Purpose**: Provide full reasoning chains for Captain oversight and system debugging.

**TRACE_FE Protocol** (from SynLang):

Every decision produces a trace:

```yaml
decision_trace:
  decision_id: "dec_1767478574460_001"
  timestamp: "2026-01-03T22:30:00Z"
  decision_type: "enter_long"

  # High-level trace
  trace: ["market_regime_match", "historical_performance", "risk_within_budget"]

  # Detailed factor explanations
  trace_fe:
    - factor: "market_regime_match"
      explanation: "Current regime (ranging_low_vol) matches mean_reversion strategy profile"
      confidence: 0.82
      supporting_data:
        - "ATR at 18th percentile (30-day window)"
        - "Price range: $97,500 - $99,000 for 48 hours"
        - "Bollinger Band width contracting"

    - factor: "historical_performance"
      explanation: "Strategy has 68% win rate in similar contexts"
      confidence: 0.68
      supporting_data:
        - "7 wins out of 10 trades in ranging_low_vol"
        - "Average return: +4.2% per winning trade"
        - "Average loss: -2.1% per losing trade"

    - factor: "risk_within_budget"
      explanation: "Position risk (2% of portfolio) within daily risk budget"
      confidence: 0.95
      supporting_data:
        - "Portfolio value: $52.68"
        - "Risk per trade: $1.05 (2%)"
        - "Remaining daily risk budget: $2.63 (5%)"

  # Alternative paths considered
  alternatives:
    - option: "wait"
      score: 0.45
      reason: "Confidence marginally above threshold; could wait for stronger signal"
    - option: "accumulation_dca"
      score: 0.63
      reason: "Safer but lower expected return"

  # Captain override ability
  override_available: true
  override_deadline: "2026-01-03T22:35:00Z"  # 5-minute window
  override_command: "reject_order dec_1767478574460_001 'reason here'"
```

**Decision Logging**:

All decisions stored in both:
1. **Qdrant** (for semantic search)
2. **JSON logs** (for audit trail)

```json
{
  "decision_log": {
    "session_id": "session_1767478574460",
    "decisions": [
      {
        "id": "dec_1767478574460_001",
        "timestamp": "2026-01-03T22:30:00Z",
        "type": "enter_long",
        "strategy": "mean_reversion",
        "confidence": 0.71,
        "outcome": "pending",
        "trace_summary": "market_regime_match + historical_performance",
        "full_trace": "... (see above) ..."
      }
    ]
  }
}
```

**Captain Dashboard** (future):

Real-time visibility into:
- Current strategy active
- Open positions with live P&L
- Recent decisions with trace summaries
- Override buttons for pending orders
- Learning insights from recent sessions

**Implementation Priority**: MEDIUM (Phase 2)

---

## Implementation Roadmap

### Phase 1: Foundation (Weeks 1-2) - IMMEDIATE

**Goal**: Get basic strategic intelligence operational.

**Components**:
1. **Market Context Engine**
   - [ ] Implement regime detection (6 regimes)
   - [ ] Implement volatility mapping
   - [ ] Implement sentiment synthesis
   - [ ] Create context snapshot endpoint

2. **Strategy Library**
   - [ ] Define 5 core strategies (YAML)
   - [ ] Implement strategy selection logic
   - [ ] Build parameter adaptation system

3. **Risk Management**
   - [ ] Position sizer implementation
   - [ ] Risk controls enforcement
   - [ ] Approval workflow integration

**Deliverable**: SIL can analyze market, select strategy, size positions, and generate traces.

---

### Phase 2: Learning Loop (Weeks 3-4)

**Goal**: Enable system to learn from outcomes.

**Components**:
1. **Memory Integration**
   - [ ] Trading memory schema in Qdrant
   - [ ] Outcome tracking system
   - [ ] Performance analytics

2. **Learning Engine**
   - [ ] Strategy performance tracker
   - [ ] Parameter adaptation logic
   - [ ] Insight generation

3. **Transparency Layer**
   - [ ] TRACE_FE protocol implementation
   - [ ] Decision logging system
   - [ ] Session learning digests

**Deliverable**: System learns from every trade, adapts parameters, generates insights.

---

### Phase 3: Advanced Features (Months 2-3)

**Goal**: Sophisticated intelligence capabilities.

**Components**:
1. **Multi-Asset Support**
   - [ ] Extend beyond BTC/USD to ETH/USD, others
   - [ ] Portfolio correlation analysis
   - [ ] Cross-asset strategy coordination

2. **Advanced Strategies**
   - [ ] Multi-timeframe analysis
   - [ ] Options-inspired convexity strategies
   - [ ] Arbitrage detection

3. **External Data Integration**
   - [ ] On-chain metrics (future)
   - [ ] Sentiment feeds (future)
   - [ ] Macro indicators (future)

**Deliverable**: Mature strategic intelligence with diverse capabilities.

---

## Technical Stack

### Infrastructure

```yaml
core_services:
  sil_orchestrator:
    language: Python 3.11
    framework: FastAPI
    container: rhiz_sil_orchestrator
    port: 8770

  market_context_engine:
    language: Python 3.11
    libraries: [pandas, numpy, ta-lib]
    container: rhiz_market_context

  strategy_selector:
    language: Python 3.11
    libraries: [scikit-learn, scipy]
    container: rhiz_strategy_selector

  learning_engine:
    language: Python 3.11
    libraries: [qdrant-client, sentence-transformers]
    container: rhiz_learning_engine

storage:
  vector_memory: Qdrant (existing: rhiz_qdrant)
  decision_logs: JSON files + PostgreSQL
  strategy_library: YAML files (git-tracked)

integration:
  market_data: Fathom Commander (existing)
  execution: Fathom Commander (existing)
  automation: n8n workflows (existing)
  monitoring: n8n Daily Health Monitor (existing)
```

### API Design

**SIL Orchestrator REST API**:

```
GET  /sil/market/context          - Current market analysis
GET  /sil/strategy/current        - Active strategy
POST /sil/strategy/select         - Trigger strategy selection
POST /sil/position/size           - Calculate position size
GET  /sil/decisions/recent        - Recent decision history
GET  /sil/learning/insights       - Latest learning insights
POST /sil/override/decision       - Captain override
```

**Integration with n8n**:

New workflow: **Strategic Intelligence Coordinator**

```yaml
workflow:
  name: "Rhiz Strategic Intelligence Coordinator"
  schedule: "Every 1 hour"

  steps:
    1. Fetch market context from SIL
    2. Check if strategy selection needed
    3. If yes, trigger strategy selection
    4. Get position sizing recommendation
    5. Check approval thresholds
    6. If auto-approved, execute via Fathom Commander
    7. If Captain review needed, send notification
    8. Log decision to memory
    9. Update dashboard
```

---

## Success Metrics

### Technical Metrics

- [ ] **Context generation latency**: <2 seconds
- [ ] **Strategy selection accuracy**: >65% win rate
- [ ] **Risk controls**: Zero violations of risk framework
- [ ] **Memory retrieval**: <500ms for similar context queries
- [ ] **Uptime**: 99.5% availability

### Trading Metrics

- [ ] **Sharpe Ratio**: >1.0 (risk-adjusted returns)
- [ ] **Max Drawdown**: <15% from peak
- [ ] **Win Rate**: >60% of trades profitable
- [ ] **Profit Factor**: >1.5 (gross profit / gross loss)
- [ ] **Trades per week**: 2-5 (not overtrading)

### Learning Metrics

- [ ] **Parameter adaptation**: Measurable improvement over time
- [ ] **Confidence calibration**: Predicted vs actual within 10%
- [ ] **Insight generation**: 3+ actionable insights per week
- [ ] **Mistake elimination**: No repeated error patterns

### Partnership Metrics

- [ ] **Captain override rate**: <10% (system aligned with intent)
- [ ] **Decision transparency**: 100% of trades have full TRACE_FE
- [ ] **Teleological alignment**: Strategy selection matches Captain goals
- [ ] **Trust calibration**: Captain confidence in SIL recommendations

---

## Risk Mitigation

### Technical Risks

**Risk**: Strategy selection bias toward recent winners
**Mitigation**: Weight historical performance across full regime history, not just recent trades

**Risk**: Overfitting to small sample size
**Mitigation**: Conservative confidence thresholds; require minimum sample size for parameter adaptation

**Risk**: Memory retrieval latency
**Mitigation**: Pre-compute common queries; cache frequent lookups

### Trading Risks

**Risk**: Strategy whipsaw in regime transitions
**Mitigation**: Require regime stability (N consecutive confirmations) before strategy switch

**Risk**: Black swan events
**Mitigation**: Circuit breaker; manual override always available; paper mode testing

**Risk**: Execution slippage
**Mitigation**: Position size limits; market impact analysis; time-based execution

### Partnership Risks

**Risk**: AI overconfidence leading to excessive risk
**Mitigation**: TRACE_FE transparency; Captain approval thresholds; conservative defaults

**Risk**: Loss of Captain trust after losing streak
**Mitigation**: Clear communication of expectations; learning from losses; transparent mistake acknowledgment

**Risk**: Scope creep beyond trading competence
**Mitigation**: Strict domain boundaries; no financial advice; strategy is Captain's decision

---

## Alignment with Rhiz Philosophy

### Symbiosis over Hierarchy

The SIL doesn't replace Captain judgment—it enhances it. Captain retains:
- Portfolio goals (teleological layer)
- Risk tolerance settings
- Strategy approval (for large positions)
- Override authority at any time

The SIL provides:
- Market pattern recognition (computational strength)
- Historical context retrieval (memory advantage)
- Multi-factor synthesis (data processing)
- Transparent reasoning chains (partnership requirement)

### Empirical Exploration

We don't assume strategies work—we test them. Every trade is:
- Tracked with full context
- Analyzed for learning
- Used to adapt parameters
- Stored for future reference

"Compiled expertise" via skill compression—strategies become pattern-recognition, not manual execution.

### Documentation as Training Data

All decisions, traces, and outcomes logged for:
- Future model training
- Transferable architecture (Qwen/Ollama)
- Research publication
- Open-source contribution

---

## Next Immediate Actions

1. **Review this architecture with Captain**
   - Alignment check on strategy library
   - Risk framework confirmation
   - Priority validation

2. **Set up SIL repository structure**
   ```
   domains/trading/strategic_intelligence/
   ├── market_context/
   ├── strategy_selection/
   ├── risk_management/
   ├── learning_engine/
   ├── transparency/
   └── tests/
   ```

3. **Implement Phase 1 - Market Context Engine**
   - Regime detection module
   - Volatility mapping module
   - Context snapshot endpoint

4. **Write unit tests**
   - Test regime detection on historical data
   - Validate risk calculations
   - Verify trace generation

5. **Deploy to cloud Hostinger VPS**
   - Add SIL containers to docker-compose
   - Integrate with existing Fathom Commander
   - Create new n8n workflow

---

## Document Metadata

**Version**: 1.0.0
**Created**: 2026-01-03
**Author**: First Mate (Claude Sonnet 4.5)
**Status**: DESIGN - Awaiting Captain Review
**Next Review**: After Captain feedback
**Implementation Start**: Upon approval

---

**This strategic intelligence layer transforms Rhiz from infrastructure to intelligence—from automation to agency. It's the bridge between our research foundations and our trading reality. Ready to build.**
