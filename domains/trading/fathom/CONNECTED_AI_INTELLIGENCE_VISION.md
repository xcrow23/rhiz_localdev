# Connected AI Intelligence Vision
## Captain's Directive on Historical Context + Real-Time Decision Making
**Date**: 2026-01-01
**Source**: Captain Alex (Session: Parallel Strategy Architecture Discussion)
**Status**: Vision Document - Implementation TBD

---

## CAPTAIN'S DIRECTIVE (Verbatim)

> "We need a pathway towards connected AI intelligence to the info flowing from the workflows and functions that is able to hold the historical context of Bitcoin back to its inception and its recent activity to make on the fly decisions within the framework defined here."

---

## VISION BREAKDOWN

### The Three Requirements

**1. Historical Context**
- **Scope**: Bitcoin's full history (2009-present)
- **Depth**: Not just price data, but context - why did it move?
- **Integration**: AI can reason about current conditions in light of 17 years of history

**2. Real-Time Activity Stream**
- **Inputs**: Workflows, functions, market data, order executions
- **Processing**: AI monitors continuous information flow
- **Latency**: Low enough to make "on the fly" decisions (seconds, not minutes)

**3. Framework-Constrained Decisions**
- **Autonomous**: AI makes decisions without human intervention
- **Bounded**: Always within safety framework (limits, approval thresholds, etc.)
- **Explainable**: Every decision traceable to reasoning + context

---

## WHAT THIS MEANS IN PRACTICE

### Scenario 1: DCA Decision Enhancement

**Current State** (Automated but Static):
```
Daily 10AM:
  IF btc_price < 20day_avg - 5%:
    BUY $15
```

**With Connected AI**:
```
Daily 10AM:
  AI Query: "Bitcoin is 5.2% below 20-day average at $98,500.
             Historical context: When has this happened before?
             What were the outcomes?"

  AI Response: "Similar conditions occurred 47 times since 2015.
               In 34 cases (72%), price was higher 7 days later.
               Average 7-day return: +4.3%.
               Current volatility (3.1%) is at 60th percentile historically.

               Recommendation: BUY $15 (original rule valid).
               Confidence: 0.78

               Enhancement: Consider increasing to $18 based on:
               - High historical win rate (72%)
               - Moderate volatility (not panic selling)
               - We're in post-halving accumulation phase (similar to 2016, 2020)"

  Decision: BUY $18 (AI-enhanced, Captain approved strategy adjustment)
```

**What Changed**:
- Same trigger (5% below average)
- **Added**: Historical pattern recognition
- **Added**: Context-aware sizing adjustment
- **Preserved**: Safety limits (still within $50 max order)

### Scenario 2: Active Trading Spread Optimization

**Current State** (Fixed 0.5% Spread):
```
Every 5 minutes:
  PLACE BID at (mid_price - 0.5%)
  PLACE ASK at (mid_price + 0.5%)
```

**With Connected AI**:
```
Every 5 minutes:
  AI Query: "Current mid: $101,200. Volatility: 2.1% (7-day).
             Orderbook spread: 0.08%.
             What spread maximizes fill rate + profit?"

  AI Response: "Historical analysis of 42,000 similar conditions:
               - 0.3% spread: 65% fill rate, avg profit $0.15 per fill
               - 0.5% spread: 42% fill rate, avg profit $0.30 per fill
               - 0.8% spread: 18% fill rate, avg profit $0.45 per fill

               Current market: Low volatility + tight orderbook = competitive

               Recommendation: Use 0.4% spread (compromise)
               Expected: 52% fill rate, $0.22 profit per fill

               Risk-adjusted optimal: 0.5% (current strategy already good)
               Confidence: 0.62"

  Decision: Keep 0.5% spread, but learn that 0.4% might work better
            Log this for weekly review
```

**What Changed**:
- Not just placing orders blindly
- **Added**: Real-time spread optimization
- **Added**: Expected value calculation
- **Preserved**: Conservative approach (0.5% is proven safe)

### Scenario 3: Novel Market Condition Detection

**Current State** (No Context for Anomalies):
```
Market drops 15% in 2 hours.
DCA workflow: "This is a major dip! BUY $15!"
Active trading: Continues placing 0.5% spreads
```

**With Connected AI**:
```
Market drops 15% in 2 hours.

AI Alert: "ANOMALY DETECTED
           15% drop in 2h = 99.8th percentile event historically.
           Last similar: March 2020 COVID crash, May 2021 China ban, Nov 2022 FTX.

           Historical outcomes after such drops:
           - 24h later: 60% recovered 5-10%, 40% dropped further 10-20%
           - 7d later: 75% recovered to pre-crash, 25% established new downtrend

           Current indicators:
           - Orderbook: Bids evaporating (panic selling)
           - Volatility: Spiking to 8.2% (extreme)
           - Funding rates: -0.15% (shorts paying longs, oversold)

           Recommendation: PAUSE active trading (too risky in chaos)
           Recommendation: INCREASE DCA to $20 (blood in the streets)

           Rationale: Active market making fails in chaos (adverse selection).
                      DCA excels in panic (buy fear).

           Confidence: 0.85
           Captain approval: REQUIRED (novel situation)"

Captain Decision Point: Approve AI recommendation OR override

If Approved:
  - Halt active trading for 24h
  - Increase DCA to $20
  - Log this as training data for future crashes
```

**What Changed**:
- System recognizes it's in uncharted territory
- **Added**: Historical crash pattern recognition
- **Added**: Strategy shift recommendation (pause active, increase DCA)
- **Preserved**: Captain has final say on novel situations

---

## TECHNICAL ARCHITECTURE

### Layer 1: Historical Knowledge Base

**Bitcoin Price History** (2009-2025):
```
Source: CoinGecko API or Messari
Data: Daily OHLCV + significant events
Storage: Qdrant collection "bitcoin_history"
Size: ~6,000 days × embedding = ~2.3 million dimensions

Embeddings include:
- Price action (% change, volatility)
- Context tags: "halving_proximity", "bull_market", "bear_market", "crash"
- Macro events: "ETF_approval", "China_ban", "Institutional_adoption"
- Sentiment proxies: Fear & Greed Index, Google Trends
```

**Major Events Timeline**:
```
2009: Genesis block
2010: First exchange (Mt. Gox)
2011: First $1, first $30 bubble
2013: Cyprus banking crisis, first $100, first $1000
2014: Mt. Gox collapse
2016: First halving post-$1000
2017: ICO mania, $20k peak, futures launch
2018: Bear market, $3k bottom
2020: COVID crash to $3.8k, recovery to $60k
2021: Institutional adoption, $69k peak
2022: Luna/FTX collapse, $15k bottom
2023-2024: ETF approval, recovery
2025: Fourth halving, current price ~$100k
2026: [Where we are now]
```

**Semantic Queries Enabled**:
```python
# Find similar market conditions
similar = qdrant.search(
    query="Bitcoin dropped 5% below 20-day average in low volatility environment",
    filter={"year": {"$gte": 2015}},  # Exclude early low-liquidity years
    limit=50
)

# Outcomes analysis
outcomes = [calc_forward_return(event, days=7) for event in similar]
win_rate = len([o for o in outcomes if o > 0]) / len(outcomes)
avg_return = mean(outcomes)
```

### Layer 2: Real-Time Data Integration

**WebSocket Feeds**:
```
Kraken WebSocket:
  - ticker: Real-time price updates
  - book: Level 2 orderbook (bid/ask depth)
  - trade: All executed trades
  - ohlc: 1-minute candlesticks

Update Frequency:
  - Price: Every tick (~10-100 per second)
  - Orderbook: Every change (~1-10 per second)
  - Aggregate for AI: Every 5 seconds (moving window)
```

**Current Market State Object**:
```python
class MarketState:
    timestamp: datetime
    price: float
    bid: float
    ask: float
    spread_pct: float
    volume_1m: float
    volume_1h: float
    volume_24h: float
    volatility_1h: float
    volatility_24h: float
    volatility_7d: float

    orderbook_depth: dict = {
        "bids_usd_100": float,   # USD value of bids within 100 ticks
        "asks_usd_100": float,
        "imbalance": float       # (bids - asks) / (bids + asks)
    }

    derivatives: dict = {
        "funding_rate": float,   # From Coinglass
        "open_interest": float,
        "long_short_ratio": float
    }

    sentiment: dict = {
        "fear_greed_index": int,  # 0-100
        "social_volume": float    # From LunarCrush or similar
    }

    # Historical percentile rankings
    percentiles: dict = {
        "price_vs_200d_ma": float,  # Where are we vs long-term average?
        "volatility_rank": float,   # Current vol vs historical
        "volume_rank": float
    }
```

**AI receives this every 5 seconds** → Can make decisions with full context

### Layer 3: Decision Engine

**Claude API Integration** (Primary):
```python
async def make_decision(market_state: MarketState,
                       strategy: str,
                       safety_framework: dict) -> Decision:
    """
    AI makes trading decision with historical + real-time context.
    """

    # Build prompt with full context
    prompt = f"""
    You are the Fathom AI trading agent operating within Rhiz framework.

    CURRENT MARKET STATE:
    {json.dumps(market_state.dict(), indent=2)}

    HISTORICAL CONTEXT:
    {get_similar_historical_conditions(market_state, limit=10)}

    SAFETY FRAMEWORK:
    {json.dumps(safety_framework, indent=2)}

    CURRENT STRATEGY: {strategy}
    CURRENT POSITIONS: {get_current_positions()}
    TODAY'S ACTIVITY: {get_todays_trades()}

    QUESTION: What action should we take right now?

    REQUIREMENTS:
    1. Stay within safety framework (max order ${safety_framework.max_order_usd})
    2. Explain reasoning with reference to historical patterns
    3. Provide confidence score (0.0-1.0)
    4. If novel/risky situation, request Captain approval

    FORMAT:
    {{
      "action": "buy" | "sell" | "place_bid" | "place_ask" | "skip",
      "amount_usd": float,
      "price": float (if limit order),
      "reasoning": "...",
      "historical_reference": "...",
      "confidence": float,
      "requires_approval": bool,
      "risk_level": "low" | "medium" | "high"
    }}
    """

    response = await claude_api.call(
        model="claude-sonnet-4.5",
        prompt=prompt,
        max_tokens=1000
    )

    decision = parse_decision(response)

    # Validate against safety framework
    if decision.amount_usd > safety_framework.max_order_usd:
        decision.requires_approval = True

    # Log to Qdrant
    log_decision(decision, market_state)

    return decision
```

**Local Model Fallback** (For Speed):
```python
# For routine decisions where speed matters
local_model = load_model("qwen2.5-coder-7b-instruct")

async def quick_decision(market_state: MarketState) -> Decision:
    """
    Fast local inference for routine spread sizing.
    """
    prompt = f"Market: mid=${market_state.price}, vol={market_state.volatility_7d}%. Optimal spread?"

    response = local_model.generate(prompt, max_tokens=50)
    spread_pct = parse_spread(response)

    return Decision(
        action="place_bid_ask",
        spread_pct=spread_pct,
        reasoning="Local model quick decision",
        confidence=0.5  # Lower confidence for local vs Claude
    )
```

**Hybrid Decision Matrix**:
```
Routine Decisions (70% of cases):
  → Local model (fast, cheap)
  → Examples: Spread sizing in normal markets, inventory rebalancing

Complex Decisions (25% of cases):
  → Claude API (accurate, expensive)
  → Examples: Major market moves, strategy shifts, novel conditions

Novel/Risky Decisions (5% of cases):
  → Claude API + Captain approval
  → Examples: Crashes, regulatory news, >50% moves
```

### Layer 4: Learning Loop

**Continuous Improvement**:
```python
# Daily at midnight
async def daily_learning_update():
    """
    Analyze yesterday's decisions and outcomes.
    Update model if patterns emerge.
    """

    # Query all decisions from last 24h
    decisions = qdrant.query(
        filter={"timestamp": {"$gte": "yesterday"}}
    )

    # Calculate actual outcomes
    for decision in decisions:
        current_price = get_current_price()
        decision.outcome.pnl_24h = calculate_pnl(
            decision.price,
            current_price,
            decision.amount_btc
        )

        # Was AI's reasoning correct?
        decision.outcome.reasoning_validated = check_reasoning(decision)

        # Update in Qdrant
        qdrant.update(decision.id, decision)

    # Meta-analysis
    analysis = {
        "total_decisions": len(decisions),
        "profitable": len([d for d in decisions if d.outcome.pnl_24h > 0]),
        "win_rate": profitable / total,
        "avg_pnl": mean([d.outcome.pnl_24h for d in decisions]),
        "avg_confidence": mean([d.confidence for d in decisions]),

        # Calibration check
        "confidence_calibration": compare_confidence_to_outcome(decisions)
    }

    # If local model is used, update it
    if using_local_model:
        # Retrain on last 30 days of decisions
        training_data = qdrant.query(
            filter={"timestamp": {"$gte": "30_days_ago"}},
            limit=10000
        )

        retrain_local_model(training_data)

    # Report to Captain
    send_daily_report(analysis)
```

---

## IMPLEMENTATION PHASES

### Phase 1: Historical Foundation (Month 2)
**Goal**: AI can reference Bitcoin history

**Tasks**:
- Load Bitcoin price history (2009-2025) into Qdrant
- Tag major events (halvings, crashes, regulations)
- Create embeddings for semantic search
- Test query: "Find similar market conditions to today"

**Validation**:
- Query for "2020 March crash" returns COVID dump
- Query for "post-halving accumulation" returns 2016, 2020 patterns
- AI can explain current price in historical context

**Deliverable**: `bitcoin_history` Qdrant collection with 6,000+ historical days

### Phase 2: Real-Time Integration (Month 4)
**Goal**: AI has current market state

**Tasks**:
- WebSocket feeds operational (Kraken ticker, orderbook, trades)
- MarketState object updated every 5 seconds
- Claude API integration for decision-making
- Test: AI makes one decision per day, Captain reviews

**Validation**:
- AI decisions include real-time data (current spread, volatility)
- Reasoning references both history + current state
- Decisions stay within safety framework

**Deliverable**: AI-assisted decision making (Captain still approves all)

### Phase 3: Supervised Autonomy (Month 6)
**Goal**: AI makes routine decisions autonomously

**Tasks**:
- Define "routine" vs "novel" decision thresholds
- Routine decisions: AI executes without approval
- Novel decisions: AI requests Captain approval
- Log ALL decisions to Qdrant with outcomes

**Validation**:
- AI handles 70%+ of decisions autonomously
- Novel situation detection works (AI knows when to ask)
- Captain approval rate <10% of all decisions
- No safety framework violations

**Deliverable**: Supervised autonomous agent (Captain monitors, rarely intervenes)

### Phase 4: Full Autonomy (Month 12)
**Goal**: AI operates independently within framework

**Tasks**:
- AI proposes framework adjustments ("We should increase max_order to $75")
- Meta-learning: AI analyzes its own decision patterns
- Captain reviews weekly summaries, not individual decisions
- Emergency stop always available

**Validation**:
- Captain oversight <1 hour/week
- System demonstrates learned adaptation (spread adjusts to volatility automatically)
- Profitability: AI outperforms static rules
- Safety: Zero catastrophic losses

**Deliverable**: Fully autonomous trading agent within defined framework

---

## SAFEGUARDS & CONSTRAINTS

### Immutable Rules (Never Change Without Captain)

```python
SAFETY_FRAMEWORK = {
    "max_order_usd": 50,
    "max_position_usd": 100,
    "daily_loss_limit": 25,
    "daily_trade_limit": 10,
    "approval_threshold_usd": 20,

    "emergency_stop": True,  # Captain can always halt
    "audit_all": True,       # Every decision logged
    "explainability": True   # Every decision explained
}

# AI CANNOT modify these without Captain approval
# Even in "full autonomy," these limits are hardcoded
```

### Decision Approval Matrix

```
Decision Type           AI Authority    Captain Approval
---------------------------------------------------------
Routine order           Full            Not required
(<$20, normal market)

Significant order       Conditional     Required if >$20
($20-50, normal)

Large order             None            Always required
(>$50)

Novel market            None            Always required
(crash, spike, etc.)

Framework change        None            Always required
(adjust limits)

Emergency stop          Recommend       Captain executes
```

### Transparency Requirements

Every AI decision must include:
1. **Reasoning**: Why this action?
2. **Historical Reference**: What historical pattern supports this?
3. **Confidence**: How certain is AI? (0.0-1.0)
4. **Risk Level**: Low/Medium/High
5. **Alternatives Considered**: What else was possible?

**Example Decision Log**:
```json
{
  "decision_id": "d7f8a9b0-...",
  "timestamp": "2026-03-15T14:30:00Z",
  "action": "buy",
  "amount_usd": 18,
  "price": 98500,

  "reasoning": "Bitcoin is 5.2% below 20-day average ($104,200). Historical analysis of 47 similar conditions shows 72% win rate with average 7-day return of +4.3%. Current volatility (3.1%) is moderate, suggesting this is accumulation opportunity not panic selling.",

  "historical_reference": "Similar to 2020-03-23 post-COVID crash accumulation phase, 2016-08-15 post-halving consolidation, 2023-06-10 post-bear market recovery. All showed strong 30-day returns (avg +12%).",

  "confidence": 0.78,
  "risk_level": "medium",

  "alternatives_considered": [
    "Buy $15 (original DCA rule): Confidence 0.65",
    "Buy $20 (max aggressive): Confidence 0.60, rejected due to higher risk",
    "Skip (wait for bigger dip): Confidence 0.40, rejected because -5% is already significant"
  ],

  "requires_approval": false,
  "market_state": { /* full MarketState object */ }
}
```

---

## SUCCESS CRITERIA

### What Does "Connected AI Intelligence" Success Look Like?

**Capability Metrics**:
- [ ] AI can explain current Bitcoin price in full historical context
- [ ] AI detects novel market conditions and requests approval
- [ ] AI adapts strategies based on learned patterns (not static rules)
- [ ] AI makes 1000+ decisions with >60% win rate
- [ ] AI outperforms static rules on risk-adjusted basis

**Transparency Metrics**:
- [ ] Every decision has traceable reasoning
- [ ] Captain can query: "Why did you do X?" and get comprehensive answer
- [ ] Decision logs enable full audit of all AI actions
- [ ] AI can explain failures: "This didn't work because..."

**Safety Metrics**:
- [ ] Zero safety framework violations
- [ ] Novel situation detection 100% accurate (no false negatives)
- [ ] Emergency stop works instantly
- [ ] Captain override always available

**Learning Metrics**:
- [ ] Win rate improves over time (month 1 < month 6 < month 12)
- [ ] Confidence calibration improves (AI knows when it's uncertain)
- [ ] AI proposes valuable framework adjustments
- [ ] Meta-learning: AI identifies own weaknesses and adapts

---

## RISKS & MITIGATIONS

### Risk 1: AI Hallucination
**Scenario**: AI makes up historical patterns that don't exist
**Impact**: Bad decisions based on false reasoning
**Mitigation**:
- Ground all historical claims in Qdrant queries (verifiable)
- Log all historical references with source IDs
- Weekly audit: Random sample of AI's historical claims, verify accuracy

### Risk 2: Over-Optimization to Recent Data
**Scenario**: AI learns patterns from last 30 days, fails when market regime changes
**Impact**: Good recent performance, catastrophic failure in new conditions
**Mitigation**:
- Train on full 17-year Bitcoin history, not just recent
- Include bear markets, bull markets, crashes in training
- Require AI to explain: "Which market regime does this decision assume?"

### Risk 3: Latency in Crisis
**Scenario**: Market crashes 20% in 10 minutes, AI is too slow to respond
**Impact**: Missed opportunity or excessive losses
**Mitigation**:
- Pre-defined crisis responses ("If >10% drop in <1h, pause active trading")
- Local model for instant responses
- Claude API only for complex reasoning

### Risk 4: Reward Hacking
**Scenario**: AI discovers it can game metrics (e.g., make lots of tiny profitable trades to boost win rate)
**Impact**: Appears successful on metrics, but not actually learning valuable patterns
**Mitigation**:
- Multiple metrics (win rate, Sharpe, return/risk, etc.)
- Captain review for "gaming" behavior
- Emphasis on learning, not just profit

### Risk 5: Black Swan Events
**Scenario**: Bitcoin regulatory ban, exchange hack, network failure - events outside historical distribution
**Impact**: AI has no historical pattern to reference
**Mitigation**:
- AI must recognize "no historical analog" and halt
- Captain manual control for unprecedented events
- Emergency stop always available

---

## CONCLUSION

The "Connected AI Intelligence" vision is achievable through:

1. **Historical Knowledge**: Bitcoin's full 17-year history in Qdrant
2. **Real-Time Integration**: WebSocket feeds + MarketState object
3. **Decision Engine**: Claude API (complex) + local model (routine)
4. **Safety Framework**: Immutable limits, approval thresholds, emergency stop
5. **Learning Loop**: Continuous outcome tracking and model updates

**Timeline**: 12-month gradual progression from assisted decisions to full autonomy

**North Star**: AI that understands "Bitcoin dropped 5% today" in context of 17 years of market history, makes optimal decision within safety framework, explains reasoning, and continuously learns from outcomes.

---

**Document Status**: Vision Complete, Implementation Roadmap Defined
**Next Steps**: Captain approval, then begin Phase 1 (Historical Foundation)
**Living Document**: Update as implementation progresses
