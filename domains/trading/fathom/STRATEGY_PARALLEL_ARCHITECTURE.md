# Fathom Parallel Strategy Architecture
## Training Laboratory for Autonomous Trading
**Date**: 2026-01-01
**Author**: First Mate (Claude Sonnet 4.5) + Captain (Alex)
**Status**: Design Complete, Implementation Pending
**Context**: Session analysis of current workflows vs. architectural vision

---

## EXECUTIVE SUMMARY

Fathom is not simply a trading system - it is a **training laboratory** for AI-driven autonomous trading. The architecture employs parallel execution of two complementary strategies:

1. **DCA Strategy (Baseline)**: Conservative accumulation providing proven returns and baseline training data
2. **Active Trading Strategy (Experimental)**: Micro market making generating high-frequency decision data

**North Star**: Autonomous trading based on learned patterns, with capital allocation dynamically adjusted by performance metrics rather than human decisions.

**Current State**: System implements DCA automation (8 n8n workflows) but lacks the active trading component described in architecture documents.

**Next Phase**: Implement parallel execution, capture comprehensive training data, develop pathway to connected AI intelligence.

---

## PHILOSOPHICAL FOUNDATION

### The Learning Laboratory Concept

From Captain's directive (2026-01-01):

> "Ground state DCA was intended to be like a training data generation lab for yourself or the daemon or AI. The intent was to implement a base level active trading strategy alongside the base DCA to accumulate the best training and enhancement data possible to pivot more to automated, autonomous active trading predicated and premised in the outlined papers and approaches within the research portion. Parallel fundamentals for training then pivoting to accumulation as the north star."

**Key Insights**:
- This is **research infrastructure**, not production profit-maximization
- Goal: Generate training data that enables autonomous decision-making
- Parallel strategies provide comparative learning (what works when?)
- Gradual graduation from 70% DCA / 30% active → autonomous allocation
- Connected AI intelligence pathway needed (historical Bitcoin context + real-time decisions)

### Why Parallel Execution?

Traditional approach: Pick one strategy, optimize it.

Rhiz approach: Run multiple strategies simultaneously to learn comparative performance.

**Benefits**:
1. **Comparative Data**: Which strategy performs better under which market conditions?
2. **Risk Mitigation**: If active trading fails, DCA baseline continues
3. **Diverse Training Corpus**: Low-frequency (DCA) + high-frequency (active) decisions
4. **Meta-Learning**: System learns not just "how to trade" but "which strategy to use when"
5. **Validation**: Active trading results validated against proven DCA baseline

---

## CURRENT STATE ANALYSIS

### What Exists Today (Jan 1, 2026)

**8 n8n Workflows Deployed**:

1. **Smart DCA** (`smart_dca_workflow.json`)
   - Trigger: Daily 10AM CT
   - Logic: Buy $10-15 BTC based on price vs 20-day average
   - Conditions: Major dip (-5%), moderate dip (-3%), or Sunday accumulation
   - **Result**: Bitcoin accumulation automation

2. **Portfolio Rebalancer** (`portfolio_rebalancer_workflow.json`)
   - Trigger: Every 8 hours
   - Logic: Sell BTC if >65% of portfolio AND >5% profit
   - Target: Maintain 50/50 BTC/USD balance
   - **Result**: Profit-taking discipline + risk management

3. **Heartbeat Monitor** (`heartbeat_workflow.json`)
   - Trigger: Every 60 seconds
   - Logic: Health check Commander endpoint, alert on failures
   - **Result**: Uptime monitoring

4. **Risk Monitor** (`risk_monitor_workflow.json`)
   - Trigger: Every 15 minutes
   - Logic: Check daily limits, loss thresholds, trading halt status
   - **Result**: Safety enforcement

5. **Daily Journal** (`daily_journal_workflow.json`)
   - Trigger: Daily 11PM CT
   - Logic: Summarize day's trades, P&L, market conditions
   - **Result**: Performance logging

6. **Weekly Review** (`weekly_review_workflow.json`)
   - Trigger: Sunday 8PM CT
   - Logic: 7-day performance analysis, insights generation
   - **Result**: Weekly learning summaries

7. **Spread Scanner** (`spread_scanner_workflow.json`)
   - Trigger: Every 5 minutes
   - Logic: Monitor bid/ask spreads for arbitrage opportunities
   - **Result**: Passive opportunity alerts (not execution)

8. **Volatility Sentinel** (`volatility_sentinel_workflow.json`)
   - Trigger: Every 30 minutes
   - Logic: Track volatility metrics, alert on high-volatility periods
   - **Result**: Market condition awareness

### What's Missing: Active Trading Execution

**Architectural Vision** (from `strategy_handoff_cc_to_cd.md`):
- Pure Market Making (PMM) or Avellaneda-Stoikov
- Continuous bid/ask order placement
- Spread capture as profit source
- Inventory management
- Real-time WebSocket market data
- <5 minute order refresh cycles

**Current Reality**:
- DCA accumulation (daily frequency)
- Rebalancing (8-hour frequency)
- No continuous order placement
- No market making activity

**The Gap**:
- Current: Accumulation automation with monitoring
- Vision: Active trading laboratory generating high-frequency training data

---

## PARALLEL ARCHITECTURE DESIGN

### Capital Allocation Model

```
Total Capital: $100 (example)

┌─────────────────────────────────────────────┐
│              SPLIT ALLOCATION               │
├─────────────────────┬───────────────────────┤
│   DCA Account       │  Active Trading       │
│   $70 (70%)         │  $30 (30%)            │
│                     │                       │
│   Conservative      │  Experimental         │
│   Proven strategy   │  Learning focus       │
│   Baseline data     │  High-frequency data  │
└─────────────────────┴───────────────────────┘
```

**Rationale for 70/30 Split**:
- **Risk Management**: Can lose entire active account ($30) without destroying experiment
- **Psychological Safety**: $30 loss is acceptable learning cost
- **Data Sufficiency**: 30% provides enough capital for meaningful active trading data
- **Baseline Preservation**: 70% DCA continues accumulating regardless of active results

**Separation of Concerns**:
- Each strategy tracks its own inventory
- Each logs decisions independently
- Comparison happens in memory layer
- No cross-contamination

### Strategy 1: DCA (Current Implementation)

**Parameters**:
```yaml
Strategy: Smart Dollar-Cost Averaging
Capital: $70
Frequency: Daily
Order Size: $10-15 (variable based on conditions)

Decision Logic:
  IF price < 20day_avg - 5% AND 24h_change < -3%:
    BUY $15  # Major dip opportunity
  ELIF price < 20day_avg - 3%:
    BUY $12  # Moderate dip
  ELIF is_sunday:
    BUY $10  # Regular accumulation
  ELSE:
    SKIP

Profit Taking (Rebalancer):
  IF btc_pct > 65% AND unrealized_profit > 5%:
    SELL 25% of excess to bring back toward 50%
```

**Training Data Generated**:
- Entry prices relative to moving averages
- Market conditions at purchase time
- Long-term outcomes (7/30/90 day returns)
- Effectiveness of "buy the dip" heuristics
- Optimal rebalancing thresholds

**Annual Expected Data Points**: ~365 DCA decisions + ~120 rebalancing decisions = 485 data points

### Strategy 2: Micro Market Making (New Implementation)

**Parameters**:
```yaml
Strategy: Micro Market Making v1.0
Capital: $30
Frequency: Every 5 minutes
Order Size: $5 per order

Decision Logic:
  EVERY 5 minutes:
    1. Get BTC mid-price
    2. Cancel existing orders
    3. Check inventory (max $15 BTC holdings)
    4. IF inventory < max:
         PLACE BID at (mid - 0.5%)
    5. IF inventory > 0:
         PLACE ASK at (mid + 0.5%)

Inventory Management:
  max_inventory_usd: $15  # Half of active capital
  IF inventory > max:
    ONLY place ASK orders (no new BIDs)
  IF inventory = 0:
    ONLY place BID orders (no ASKs)

Safety Limits:
  max_loss_per_day: $3
  max_orders_per_day: 20
  IF daily_loss >= $3 OR orders >= 20:
    HALT active trading, resume next day
```

**Training Data Generated**:
- Bid/ask placement decisions
- Fill rates (% of orders that execute)
- Spread capture effectiveness
- Inventory duration (how long holding BTC)
- Adverse selection rates (filled at bad times?)
- Fee impact on profitability
- Market microstructure patterns

**Annual Expected Data Points**: ~105,120 order placements (12/hour × 24 × 365)
- With 40% fill rate: ~42,000 fills per year
- Each with market context, outcome, P&L

### Memory Integration (Qdrant)

**Unified Decision Schema**:

```python
class TradingDecision:
    """
    Unified schema for both DCA and active trading decisions.
    Enables comparative analysis and pattern learning.
    """

    # Metadata
    decision_id: str           # UUID
    strategy: str              # "dca" or "micro_market_making"
    timestamp: str             # ISO 8601

    # Decision Details
    action: str                # "buy", "sell", "place_bid", "place_ask", "skip"
    pair: str                  # "XXBTZUSD"
    price: float               # Execution or target price
    amount_usd: float          # Dollar amount
    amount_btc: float          # BTC amount

    # Market Context
    market_context: dict = {
        "mid_price": float,
        "bid_price": float,
        "ask_price": float,
        "spread_pct": float,
        "20day_avg": float,     # DCA context
        "24h_change_pct": float,
        "volume_24h": float,
        "volatility_7d": float,
        "orderbook_depth": dict # Active trading context
    }

    # Reasoning
    hypothesis: str            # What are we testing?
    reasoning: str             # Why this decision?
    confidence: float          # 0.0-1.0
    alternatives_considered: list

    # Outcomes (filled in later)
    outcome: dict = {
        "filled": bool,
        "fill_time_seconds": int,
        "execution_price": float,
        "slippage_pct": float,
        "fees_paid": float,

        # Time-series outcomes
        "pnl_1h": float,
        "pnl_24h": float,
        "pnl_7d": float,
        "pnl_30d": float,
        "pnl_90d": float,

        # Meta
        "adverse_selection": bool,  # Filled but immediately unfavorable
        "optimal_in_hindsight": bool # Was this the right decision?
    }

    # Learning
    embedding: list[float]     # 384-dim vector for semantic search
    tags: list[str]            # ["volatile_market", "weekend", "major_dip", etc.]
```

**Outcome Tracking Automation**:
```python
# n8n workflow: outcome_tracker.json
# Runs hourly

async def update_outcomes():
    """
    Query all decisions from last 90 days.
    For each, calculate current P&L and update outcome fields.
    """

    recent_decisions = qdrant.query(
        filter={"timestamp": {"$gte": "90_days_ago"}}
    )

    for decision in recent_decisions:
        current_price = get_current_btc_price()

        if decision.action in ["buy", "place_bid"]:
            entry_price = decision.price

            # Calculate P&L at various horizons
            hours_elapsed = hours_since(decision.timestamp)

            if hours_elapsed >= 1:
                decision.outcome.pnl_1h = calculate_pnl(
                    entry_price,
                    get_price_at(decision.timestamp + 1h)
                )

            if hours_elapsed >= 24:
                decision.outcome.pnl_24h = calculate_pnl(
                    entry_price,
                    get_price_at(decision.timestamp + 24h)
                )

            # ... continue for 7d, 30d, 90d

            # Update in Qdrant
            qdrant.update(decision.id, decision)
```

---

## COMPARATIVE LEARNING FRAMEWORK

### Weekly Analysis Dashboard

**Metrics Tracked**:

**DCA Performance**:
```
- Total invested (cumulative $)
- Total BTC acquired
- Average entry price
- Current value
- Unrealized P&L (%)
- Win rate (% of entries profitable after 7/30/90 days)
- Sharpe ratio (if sufficient data)
- Maximum drawdown
- Time invested (Captain oversight hours)
```

**Active Trading Performance**:
```
- Total volume traded (cumulative $)
- Number of round trips (buy→sell cycles)
- Gross profit from spread capture
- Fees paid
- Net profit
- Return on capital (%)
- Fill rate (% orders executed)
- Average spread captured
- Adverse selection rate
- Inventory turnover
- Sharpe ratio
- Sortino ratio (downside risk focus)
- Time invested (oversight + monitoring hours)
```

**Comparative Metrics**:
```
- Risk-adjusted return: DCA Sharpe vs Active Sharpe
- Return per dollar invested
- Return per hour of Captain time
- Consistency (standard deviation of returns)
- Tail risk (worst 5% of outcomes)
- Strategy correlation (do they move together?)
```

### Pattern Recognition Queries

**Questions to Answer Through Memory**:

1. **When does DCA outperform?**
   - Query: All decisions during trending markets
   - Analysis: Does DCA beat active in strong trends?

2. **When does active trading work?**
   - Query: All active decisions during ranging markets
   - Analysis: Does spread capture work better in low-volatility ranges?

3. **What market conditions favor each?**
   - Tag decisions with market regime: trending_up, trending_down, ranging, volatile
   - Compare P&L by regime

4. **What spreads actually get filled?**
   - Query: Active orders with fill=true
   - Analysis: What spread sizes have >50% fill rate?

5. **Are we capturing adverse selection?**
   - Query: Filled orders where price moved against us <1h after fill
   - Analysis: Are we "picking up pennies in front of a steamroller"?

6. **What's the optimal DCA dip threshold?**
   - Query: DCA buys at different % below 20-day avg
   - Analysis: Does -3% dip outperform -5% dip after 30 days?

**Example Query**:
```python
# Find: What spread size has best risk-adjusted returns?

results = qdrant.query(
    filter={
        "strategy": "micro_market_making",
        "outcome.filled": True,
        "outcome.pnl_24h": {"$exists": True}
    },
    group_by="spread_pct",
    aggregate={
        "avg_pnl": "mean(outcome.pnl_24h)",
        "std_pnl": "std(outcome.pnl_24h)",
        "sharpe": "mean / std",
        "fill_rate": "count(filled) / count(total)"
    }
)

# Results might show:
# 0.3% spread: Sharpe 0.2, fill_rate 60%
# 0.5% spread: Sharpe 0.6, fill_rate 40%  ← Optimal?
# 0.8% spread: Sharpe 0.4, fill_rate 20%

# Action: Adjust spread parameter based on learned optimal
```

---

## GRADUATION PATH: AUTONOMOUS ALLOCATION

### Phase Transitions Based on Performance

**Phase 1: Initial Split (Months 0-1)**
```
Allocation: 70% DCA / 30% Active
Duration: 30 days minimum
Goal: Collect baseline data, validate systems

Success Criteria:
  ✓ Both strategies executing without errors
  ✓ Memory capture working (>90% of decisions logged)
  ✓ No catastrophic losses (active losses < $10)
  ✓ Fill rate >30% (active orders executing)
```

**Phase 2: First Reallocation (Months 1-3)**
```
Trigger Conditions:
  ✓ Active Sharpe ratio > 0.5
  ✓ Active net P&L > 0 after fees
  ✓ Fill rate > 40%
  ✓ No single-day loss > $5
  ✓ Captain comfort level: "I understand what's happening"

Action: Shift to 50% DCA / 50% Active ($50 / $50)

If Conditions NOT Met: Stay 70/30
```

**Phase 3: Primary Active (Months 3-6)**
```
Trigger Conditions:
  ✓ Active Sharpe > DCA Sharpe (90-day window)
  ✓ Active cumulative return > DCA cumulative return
  ✓ Active Sortino ratio > 1.0 (downside-focused)
  ✓ <2 hours/week Captain oversight needed
  ✓ System demonstrates learned adaptation (spread adjusts to volatility)

Action: Shift to 30% DCA / 70% Active ($30 / $70)

If Conditions NOT Met: Stay 50/50 or revert to 70/30
```

**Phase 4: Autonomous Allocation (Month 6+)**
```
Trigger Conditions:
  ✓ 6 months of data collected
  ✓ System demonstrates:
    - Volatility-adaptive spread sizing
    - Regime-aware strategy selection
    - Risk-aware inventory management
  ✓ Meta-learning: System recommends own allocation shifts
  ✓ Captain approves autonomous mode

Action: Dynamic weekly reallocation
  Algorithm decides DCA/Active split based on:
    - Recent 30-day performance of each
    - Current market regime (trending vs ranging)
    - Volatility environment
    - Opportunity detection (spread compression = more active?)

Example Autonomous Decision:
  "Market is ranging, volatility is low, spreads are tight.
   Active trading has 0.8 Sharpe in last 30 days vs DCA 0.3.
   Recommendation: 20% DCA / 80% Active for next 7 days.
   Rationale: Ranging markets favor spread capture.
   Confidence: 0.72"
```

---

## CONNECTED AI INTELLIGENCE PATHWAY

### Captain's Vision (2026-01-01)

> "We need a pathway towards connected AI intelligence to the info flowing from the workflows and functions that is able to hold the historical context of Bitcoin back to its inception and its recent activity to make on the fly decisions within the framework defined here."

**Requirements**:

1. **Historical Bitcoin Context**
   - Price history: 2009-present
   - Major events: halving cycles, regulatory changes, adoption milestones
   - Market structure evolution: How has Bitcoin trading changed?
   - Macro context: Correlation with traditional markets, inflation data

2. **Real-Time Decision Making**
   - Ingest: Current market data (price, volume, orderbook)
   - Context: Where are we in historical patterns? (e.g., "This volatility is 90th percentile historically")
   - Decision: Within safety framework, what's optimal action?
   - Execution: Place orders, manage inventory
   - Learning: Update beliefs based on outcomes

3. **Framework Constraints**
   - Safety limits always enforced (max order, daily loss, etc.)
   - Explainability required (every decision has reasoning)
   - Memory integration (all decisions logged for learning)
   - Captain oversight for novel situations

### Architectural Components Needed

**1. Historical Data Integration**
```
External API: CoinGecko, Messari, or Glassnode
- Bitcoin price history (daily OHLC since 2009)
- On-chain metrics (hash rate, active addresses, etc.)
- Macro economic data (S&P 500, gold, DXY, CPI)

Storage: Local Qdrant collection
- Preload historical embeddings
- Tag major events (halvings, ETF approvals, etc.)
- Enable semantic queries: "Similar market conditions to 2017 bull run"
```

**2. Real-Time Context Window**
```
WebSocket Feeds:
- Kraken: Live price, orderbook, trades
- Coinglass: Funding rates, open interest (derivatives context)
- Fear & Greed Index: Sentiment proxy

Processing:
- Every 5 seconds: Update current market state
- Every 5 minutes: Recalculate decision context
- Pass to AI: "Here's current state + historical similar situations"
```

**3. Decision Engine**
```
AI Model Integration:
Option A: Claude API with extended context
  - Load: Historical embeddings + current market state
  - Prompt: "Given this context, what's optimal action within safety framework?"
  - Response: Decision + reasoning + confidence

Option B: Fine-tuned local model (Qwen2.5-Coder or DeepSeek)
  - Trained on: Historical Rhiz decision corpus
  - Inference: <1 second latency
  - Constraint: Harder to explain reasoning

Hybrid Approach (Recommended):
  - Local model for routine decisions (spread sizing, inventory management)
  - Claude API for novel situations or strategy shifts
  - Human approval for significant changes
```

**4. Feedback Loop**
```
Execution → Outcome → Memory Update → Model Refinement

Every decision:
1. Log to Qdrant with full context
2. Track outcome over time (1h, 24h, 7d, 30d)
3. Weekly: Retrain local model on recent data
4. Monthly: Meta-analysis - what worked? What didn't?
5. Quarterly: Strategy evolution - should we change approach?
```

### Implementation Phases

**Phase A: Static Historical Context (Month 2)**
- Load Bitcoin price history into Qdrant
- Create semantic embeddings of major events
- Enable queries: "What happened in similar market conditions?"
- Manual decision-making, AI-assisted context

**Phase B: Real-Time Integration (Month 4)**
- WebSocket feeds operational
- AI has current + historical context
- AI suggests decisions, Captain approves
- Log approval/rejection reasoning

**Phase C: Supervised Autonomy (Month 6)**
- AI makes routine decisions autonomously
- Novel situations → Captain approval
- Weekly Captain review of all decisions
- Continuous learning from outcomes

**Phase D: Full Autonomy (Month 12)**
- AI operates within framework independently
- Captain monitors, intervenes only on anomalies
- System explains all decisions
- Meta-learning: AI proposes framework improvements

---

## RISK MANAGEMENT FRAMEWORK

### Immutable Safety Constraints

**No matter how autonomous the system becomes, these limits NEVER change without Captain approval:**

```yaml
Hard Limits:
  max_order_usd: 50          # Largest single order
  max_position_usd: 100      # Largest BTC holding
  daily_loss_limit: 25       # Halt if lose $25 in one day
  daily_trade_limit: 10      # Max trades per 24h
  approval_threshold: 20     # Captain approval needed for >$20

Active Trading Specific:
  max_active_capital: 30     # Can't risk more than $30 in active
  max_inventory_usd: 15      # Half of active capital max
  max_loss_per_day: 3        # Halt active if lose $3
  max_orders_per_day: 20     # Activity limit

Emergency Controls:
  emergency_stop: true       # Captain can halt all trading
  paper_mode: false          # Can switch to paper trading anytime
  audit_all_decisions: true  # Every decision logged, no exceptions
```

### Risk Monitoring Workflows

**1. Daily Risk Report** (n8n, 8AM daily)
```
Check:
- Current exposure (DCA + Active positions)
- Yesterday's P&L
- Days remaining in daily trade/loss limits
- Any anomalies (unusual volatility, API errors)

Alert if:
- Daily loss >50% of limit ($12.50 of $25)
- Trades >80% of limit (8 of 10)
- Active trading losing streak >3 days
- Fill rate <20% (active orders not executing)
```

**2. Weekly Strategy Review** (n8n, Sunday 8PM)
```
Generate:
- DCA vs Active performance comparison
- Sharpe ratio trends
- Win rate analysis
- Fee impact assessment
- Recommendations: stay current allocation or shift?

Captain Decision Point:
- Approve recommended allocation shift OR
- Override with manual allocation OR
- Request deeper analysis on specific metric
```

**3. Monthly Deep Dive** (Manual, Captain + AI)
```
Questions:
- Are we learning? (Improving over time?)
- What patterns emerged? (Market regime impacts)
- Should we change parameters? (Spread size, refresh rate, etc.)
- Are safety limits appropriate? (Too tight? Too loose?)
- Is the framework still aligned with goals?
```

---

## SUCCESS METRICS

### What Does "Success" Look Like?

**NOT**: Maximum profit
**IS**: Maximum learning toward autonomous capability

**Primary Metrics** (in order of importance):

1. **Learning Rate**
   - Are decisions improving over time?
   - Measure: Compare Sharpe ratio of first month vs most recent month
   - Target: >10% improvement quarter-over-quarter

2. **Data Quality**
   - Are we capturing comprehensive context?
   - Measure: % of decisions with complete market context logged
   - Target: >95%

3. **System Reliability**
   - Is the infrastructure stable?
   - Measure: Uptime %, failed executions
   - Target: >99% uptime, <1% failed trades

4. **Risk Management**
   - Are safety limits working?
   - Measure: Number of limit breaches, emergency stops
   - Target: 0 catastrophic losses (>$50 single event)

5. **Return on Learning**
   - Is active trading becoming more effective?
   - Measure: Active Sharpe ratio trend
   - Target: Positive slope over 6 months

**Secondary Metrics**:

6. **Profitability**
   - Are we making money?
   - Measure: Net P&L after fees
   - Target: Positive returns, but secondary to learning

7. **Capital Efficiency**
   - Are we using capital effectively?
   - Measure: Return per dollar at risk
   - Target: Active beats DCA on risk-adjusted basis by month 6

8. **Autonomy Progress**
   - Are we reducing Captain intervention?
   - Measure: Hours per week of oversight needed
   - Target: <2 hours/week by month 6, <1 hour/week by month 12

---

## IMPLEMENTATION ROADMAP

### Week 1: Foundation (Current)
- [x] Analyze existing workflows
- [x] Identify gap between current and vision
- [x] Design parallel architecture
- [ ] Document comprehensively (this document)
- [ ] Captain approval to proceed

### Week 2-3: Micro Market Making Implementation
- [ ] Create `strategy_micro_mm.py` in Commander
- [ ] Build n8n workflow: `micro_market_making_workflow.json`
- [ ] Extend memory logging for active trading context
- [ ] Deploy to Hostinger in PAPER MODE
- [ ] Validate: 7 days of paper trading data

### Week 4: Parallel Execution
- [ ] Split capital: $70 DCA / $30 Active (or paper equivalent)
- [ ] Run both strategies simultaneously
- [ ] Validate data capture (both logging to Qdrant)
- [ ] Build weekly comparison dashboard
- [ ] Captain review: Is data quality sufficient?

### Month 2: Go Live + Outcome Tracking
- [ ] Switch active trading to LIVE mode
- [ ] Implement outcome tracker (hourly update script)
- [ ] First weekly review with comparative metrics
- [ ] Begin pattern analysis queries
- [ ] Load historical Bitcoin data into Qdrant

### Month 3: First Reallocation Decision
- [ ] Analyze 60 days of parallel data
- [ ] Compare DCA vs Active performance
- [ ] Apply graduation criteria
- [ ] Captain decision: Stay 70/30 or shift to 50/50?

### Month 4-6: AI Integration
- [ ] Real-time WebSocket integration
- [ ] Claude API integration for decision assistance
- [ ] Supervised autonomy: AI suggests, Captain approves
- [ ] Weekly model performance reviews

### Month 7-12: Autonomous Evolution
- [ ] Progressive reduction of Captain intervention
- [ ] System proposes parameter adjustments
- [ ] Meta-learning: "What did we learn about learning?"
- [ ] Document transferable patterns for future AIs

---

## DECISION LOG

**Major Design Decisions & Rationale**:

| Decision | Rationale | Date |
|----------|-----------|------|
| 70/30 DCA/Active split | Balance risk (preserve 70%) with learning (30% experiments) | 2026-01-01 |
| $5 micro orders | Small enough to learn affordably, large enough for meaningful data | 2026-01-01 |
| 0.5% spread | Conservative starting point, can tighten as we learn optimal | 2026-01-01 |
| 5-minute refresh | Fast enough for data generation, slow enough to avoid excessive fees | 2026-01-01 |
| Paper mode first | Validate mechanics before risking real capital | 2026-01-01 |
| Qdrant for memory | Already integrated, proven for semantic search | 2026-01-01 |
| n8n for orchestration | Already deployed, visual workflow design, Captain familiar | 2026-01-01 |
| Gradual autonomy path | De-risk AI control, ensure alignment at each phase | 2026-01-01 |

---

## APPENDICES

### A. Research References

Documents informing this architecture:

1. **strategy_handoff_cc_to_cd.md**
   - Pure market making mechanics
   - Order book dynamics
   - Inventory risk management
   - Fee optimization strategies

2. **ARCHITECTURE_v2.md**
   - MCP integration patterns
   - Memory scaffolding philosophy
   - n8n automation hooks
   - Backtesting framework

3. **Rhiz Core Memory Architecture**
   - Session checkpoints with TRACE confidence
   - YAML schema versioning
   - Decision traceability to telos
   - Learning extraction from sessions

4. **External Research** (referenced in Gifts_From_Alex)
   - Skill Compression: Pattern recognition → retrieval → composition → execution
   - HAIST: Human-AI Symbiotic Theory
   - SynLang TRACE: Transparency, autonomy, calibration, explanation

### B. Configuration Files

**Micro Market Making Config** (`config/micro_mm_config.yaml`):
```yaml
strategy:
  name: micro_market_making
  version: 1.0.0
  capital_usd: 30

parameters:
  spread_pct: 0.5
  order_size_usd: 5
  refresh_interval_seconds: 300
  max_inventory_usd: 15

safety:
  max_loss_per_day: 3
  max_orders_per_day: 20
  paper_mode: true  # Start in paper mode

logging:
  log_every_decision: true
  include_market_context: true
  qdrant_collection: "fathom_trading_decisions"
```

### C. Memory Query Examples

**Query 1: Find similar market conditions**
```python
similar_conditions = qdrant.search(
    collection="fathom_trading_decisions",
    query_vector=embed("Current: BTC at $102k, volatility 3.2%, ranging market"),
    filter={
        "market_context.volatility_7d": {"$gte": 2.5, "$lte": 4.0},
        "outcome.pnl_24h": {"$exists": True}
    },
    limit=20
)

# Analyze: What worked in similar conditions?
profitable = [d for d in similar_conditions if d.outcome.pnl_24h > 0]
win_rate = len(profitable) / len(similar_conditions)
avg_spread = mean([d.spread_pct for d in profitable])
```

**Query 2: What's optimal spread by volatility?**
```python
spread_analysis = qdrant.aggregate(
    collection="fathom_trading_decisions",
    group_by=["spread_pct", "market_context.volatility_7d_bucket"],
    metrics={
        "avg_pnl_24h": "mean(outcome.pnl_24h)",
        "fill_rate": "count(outcome.filled=true) / count(*)",
        "sharpe": "mean(pnl) / std(pnl)"
    }
)

# Results might show:
# Low volatility (<2%): 0.3% spread best (high fill rate, small profits)
# Medium volatility (2-4%): 0.5% spread best (balanced)
# High volatility (>4%): 0.8% spread best (wider protection needed)
```

---

## CONCLUSION

Fathom is not a trading system. Fathom is a **learning laboratory** for developing autonomous trading intelligence.

The parallel DCA + active trading architecture provides:
- **Comparative learning**: What works when?
- **Risk mitigation**: Baseline strategy always running
- **Rich training data**: Both low-frequency (DCA) and high-frequency (active) decisions
- **Gradual autonomy**: Proven performance → increased allocation → eventual autonomy
- **Meta-learning**: System learns not just how to trade, but how to learn to trade

**Next Steps**: Captain approval, then Week 2-3 implementation begins.

**North Star**: Autonomous trading agent that:
- Understands Bitcoin's full historical context
- Makes real-time decisions within safety framework
- Explains every decision
- Continuously learns from outcomes
- Requires minimal human oversight
- Preserves capital while maximizing learning

Fair winds and good hunting.

---

**Document Status**: Complete
**Next Review**: After Week 1 implementation
**Living Document**: Update as architecture evolves
