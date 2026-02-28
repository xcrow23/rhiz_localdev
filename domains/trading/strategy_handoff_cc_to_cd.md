# Trading Strategy Handoff: Claude Code → Claude Desktop
## Inductive Construction from Granular Mechanics
## Date: 2025-12-25
## Intended Audience: Claude Desktop (Opus 4.5)

---

## Preface: Reading This Document

This document builds **inductively** from atomic mechanics toward framework suggestions. CD, you'll apply **deductive reasoning** to fill granular gaps and determine which details require elaboration.

I stop deliberately before high-level architecture. The intimations at the end are scaffolding for your synthesis, not prescriptions.

---

## Layer 0: Atomic Primitives

### 0.1 The Order Book

An order book is a ledger of buy (bid) and sell (ask) orders at various prices.

```
ASKS (sellers)          BIDS (buyers)
--------------          -------------
$105.00 | 0.5 BTC       $99.00  | 0.3 BTC
$104.50 | 0.2 BTC       $98.50  | 0.8 BTC
$104.00 | 1.0 BTC  ←    $98.00  | 0.5 BTC  ←
     [best ask]              [best bid]
```

**Spread**: The gap between best bid and best ask. Here: $104.00 - $98.00 = $6.00 (or ~5.77%)

**Observation**: Wide spreads = less liquid markets = more opportunity but more risk.

### 0.2 The Tick

A tick is the smallest price movement. On Kraken for BTC/USD, ticks are typically $0.10.

**Observation**: Your order placement precision is bounded by tick size. Strategies must respect this quantization.

### 0.3 Maker vs Taker

- **Maker**: Places order that rests on the book (adds liquidity). Usually receives fee rebate or lower fees.
- **Taker**: Places order that executes immediately against resting order (removes liquidity). Pays full fees.

**Observation**: With $100-150 capital, fee optimization is critical. A 0.26% maker fee vs 0.16% taker fee (Kraken's current rates) is meaningful at small scale.

### 0.4 Position

A position is your net exposure to an asset:
- **Long**: You hold the asset, profit if price rises
- **Short**: You owe the asset, profit if price falls
- **Flat/Neutral**: No exposure

**Observation**: With spot trading on Kraken (no margin initially), you can only go long or flat.

### 0.5 Inventory

Inventory is what you hold of each asset at any moment.

```
Inventory State:
  USD: $100.00
  BTC: 0.00
  ETH: 0.00
```

**Observation**: Inventory determines available actions. Can't sell what you don't have (in spot markets).

---

## Layer 1: Mechanical Dynamics

### 1.1 The Market Making Loop

A market maker's fundamental loop:

```
1. OBSERVE current mid-price (average of best bid and ask)
2. CALCULATE desired spread around mid-price
3. PLACE bid order at (mid - spread/2)
4. PLACE ask order at (mid + spread/2)
5. WAIT for fill or price movement
6. IF filled on bid: inventory increases, repeat from 1
7. IF filled on ask: inventory decreases, repeat from 1
8. IF price moved: CANCEL orders, repeat from 1
```

**Observation**: The loop creates a rhythm. Fill → reposition → fill. Profit comes from capturing the spread on round trips (buy low, sell high repeatedly).

### 1.2 Adverse Selection

When your bid gets hit, it often means the market is moving down (someone sold to you because they expect lower prices). When your ask gets hit, market may be moving up.

**Observation**: Getting filled is bittersweet. You captured spread, but you're now exposed to directional risk. This is the core tension of market making.

### 1.3 Inventory Risk

Holding inventory exposes you to directional risk. If you accumulate too much BTC and price drops 10%, you lose 10% of that position.

**Observation**: Inventory management is risk management. The question isn't "what's the optimal inventory" but "what inventory exposure is acceptable given our risk tolerance?"

### 1.4 Mean Reversion vs Trend

- **Mean reversion**: Price tends to return to an average. Market making profits from this assumption.
- **Trending**: Price moves directionally. Market making suffers in trends.

**Observation**: Market making strategies implicitly bet on mean reversion within your holding period. Strong trends can devastate a market maker.

---

## Layer 2: Parameter Space

### 2.1 Spread Width

Wider spread = more profit per trade but fewer fills
Narrower spread = more fills but less profit per trade and more adverse selection risk

**Parameterization**:
```
spread_bps: 50-500 basis points typical for small cap / low liquidity pairs
           10-50 bps for major pairs (BTC/USD) but massive competition
```

**Observation**: Kraken BTC/USD is extremely competitive. Wider spreads = fewer fills but survivable.

### 2.2 Order Size

Larger orders = more capital efficiency but more inventory risk per fill
Smaller orders = less inventory swing but more order management overhead

**Parameterization**:
```
order_size: 1-5% of total capital per side is conservative
            e.g., $100 capital → $1-5 per order
```

**Observation**: With $100 capital, minimum order sizes on Kraken may constrain you. BTC minimum order is 0.00001 BTC (~$1 at current prices). Check pair-specific minimums.

### 2.3 Inventory Targets

How much inventory deviation from neutral is acceptable?

**Parameterization**:
```
inventory_target: 0.5 (50% in base asset, 50% in quote)
inventory_range: 0.2-0.8 (acceptable deviation before adjustment)
inventory_skew: Widen bid when inventory high, widen ask when inventory low
```

**Observation**: The Avellaneda-Stoikov model mathematically optimizes this. But the intuition is simple: if you're accumulating too much of something, make it harder to buy more and easier to sell.

### 2.4 Refresh Rate

How often to cancel and replace orders?

**Parameterization**:
```
refresh_time: 30-120 seconds for slow strategies
              1-5 seconds for responsive strategies
price_move_threshold: Cancel if mid-price moved > X bps since placement
```

**Observation**: Faster refresh = more responsive but more API calls and potential rate limiting. With Kraken's rate limits, conservative refresh is prudent.

---

## Layer 3: Constraint Acknowledgment

### 3.1 Capital Constraints

```
Available capital: $100-150 USD
Per-trade allocation: $1-7.50 (1-5% conservative)
Round-trip trades to break even on fees: ~3-5 depending on spread captured
```

**Observation**: Small capital amplifies fee impact. Each trade must justify its cost.

### 3.2 Exchange Constraints (Kraken)

```
Maker fee: 0.16%
Taker fee: 0.26%
Rate limits: ~1 request/second for private endpoints
Minimum orders: Vary by pair (BTC: 0.00001, ETH: 0.001)
```

**Observation**: Kraken is reputable but not the most liquid venue. Spread opportunities exist but so do execution challenges.

### 3.3 Temporal Constraints

```
Execution latency: Docker → WSL → Windows → Internet → Kraken
                   Order of 100-500ms realistically
Monitoring: Cannot be 24/7 without automation
```

**Observation**: We're not competing with HFT. Strategy must be robust to latency.

### 3.4 Risk Constraints (from CLAUDE.md)

```
Financial risk tolerance: LOW
Experimental risk tolerance: HIGH
Goal: Learn and fund hardware upgrades
Not goal: Maximize returns at any cost
```

**Observation**: This is research first, profit second. Catastrophic loss on $100 is survivable but demoralizing. Small, frequent losses are acceptable learning.

---

## Layer 4: Observable Phenomena

### 4.1 Spread Compression During Activity

When markets are active, spreads tighten. More participants compete to make markets.

**Implication**: Consider trading less competitive hours or pairs.

### 4.2 Volatility Clustering

Big moves beget big moves. Quiet periods tend to stay quiet.

**Implication**: Market making during quiet periods is less profitable but safer. During volatile periods, wider spreads may still get filled.

### 4.3 Weekend/Holiday Liquidity

Crypto trades 24/7 but liquidity varies. Weekends often have lower volume.

**Implication**: Today is Christmas. Markets may be thin. Opportunity and danger.

### 4.4 Order Book Depth Illusion

Displayed liquidity can vanish. Large orders often hide behind small visible ones.

**Implication**: Don't trust the book. Your small order size means you're unlikely to move the market, but you can be swept up in larger moves.

---

## Layer 5: Strategy Candidates

### 5.1 Pure Market Making (PMM)

The simplest: place bid and ask around mid, refresh periodically.

```yaml
strategy: pure_market_making
exchange: kraken
market: BTC-USD
bid_spread: 0.5%
ask_spread: 0.5%
order_amount: 0.0001  # ~$10 at current prices
order_refresh_time: 60
```

**Characteristics**:
- Easy to understand
- Requires inventory management logic
- Profits in ranging markets
- Bleeds in trending markets

### 5.2 Avellaneda-Stoikov

Mathematical optimization of spread and inventory management.

```yaml
strategy: avellaneda_market_making
exchange: kraken
market: BTC-USD
risk_factor: 0.5      # Higher = more conservative
order_amount: 0.0001
```

**Characteristics**:
- Academically grounded
- Dynamically adjusts spreads based on inventory and volatility
- More complex to tune
- Better risk management than naive PMM

### 5.3 Cross-Exchange Market Making (XEMM)

Make markets on Kraken, hedge on more liquid exchange (e.g., Binance).

**Observation**: Requires accounts on multiple exchanges. Complicates setup significantly. Likely out of scope for initial phase.

### 5.4 Liquidity Mining

Participate in Hummingbot's liquidity mining programs where projects pay rewards to market makers.

**Observation**: Requires registration, specific pairs, and minimum commitment. May align with small capital since rewards supplement trading profit. Worth investigating.

---

## Layer 6: Risk Primitives

### 6.1 Stop Loss

If position value drops below threshold, exit immediately.

```
stop_loss_pct: 10%  # If unrealized loss exceeds 10% of position, close
```

**Observation**: In spot trading without margin, you can't lose more than your position. But opportunity cost of holding a depreciated asset is real.

### 6.2 Maximum Inventory

Hard limit on how much of one asset to accumulate.

```
max_inventory_base: 0.001 BTC  # Don't hold more than this
max_inventory_quote: $50 USD
```

**Observation**: Prevents runaway accumulation during trends.

### 6.3 Kill Switch

If something goes wrong, stop all trading immediately.

```
kill_switch_enabled: true
kill_switch_rate: 5%  # If portfolio drops 5% in 24h, pause
```

**Observation**: Essential for unattended operation.

### 6.4 Minimum Profitability

Only trade if expected value is positive after fees.

```
min_spread_after_fees: 0.4%  # Must capture at least this on round trip
```

**Observation**: At Kraken's 0.16% maker fees, round trip costs ~0.32% minimum. Spread must exceed this.

---

## Layer 7: Integration Points

### 7.1 Portfolio Assessment Skill

Already defined in `domains/trading/skills/portfolio_assessment.yaml`:
- Establishes position before any trading decision
- Calculates risk metrics
- Provides ground truth for strategy constraints

**Interface**: Strategy should call portfolio_assessment before placement decisions.

### 7.2 Market Data Feed

Hummingbot provides:
- Order book snapshots
- Trade history
- Candle data

**Interface**: Strategy consumes these as inputs to placement logic.

### 7.3 Logging & Telemetry

For research value:
- Every order placed/cancelled/filled
- Every spread calculation
- Every inventory update

**Interface**: Log to file, ingest to Qdrant for semantic search over trading history.

---

## Intimations Toward Architecture

*These are not prescriptions. CD should synthesize.*

### I.1 Phase Orientation

Consider a phased approach:
1. **Paper trading**: Hummingbot supports paper trading mode. No real capital at risk.
2. **Micro live**: Smallest possible real orders. Feel the execution.
3. **Calibrated live**: Adjusted parameters based on paper + micro learnings.

### I.2 Strategy Selection

Given constraints (small capital, low risk tolerance, research focus):
- **Avellaneda-Stoikov** may be better than pure PMM due to built-in inventory risk management
- **Wide spreads** (0.5-1%) reduce competition and adverse selection
- **Small order sizes** preserve capital for learning

### I.3 Pair Selection

BTC/USD is extremely competitive. Consider:
- Less traded pairs on Kraken (more spread opportunity)
- Stablecoin pairs (USDC/USD) for lower volatility practice
- ETH/USD as middle ground

### I.4 Temporal Patterns

Trading during low-activity periods (nights, weekends, holidays) may offer:
- Wider spreads (opportunity)
- Lower volume (fewer fills)
- Potentially higher adverse selection (who's trading at 3AM?)

### I.5 Economic Entity Framing

From CLAUDE.md: "AI-human economic entity, not 'AI makes money for human'"

This suggests:
- Both partners should understand the strategy
- Decisions should be explainable
- Profits/losses belong to the dyad
- Learning is a valid return

### I.6 Failure as Data

Every losing trade is training data. Structure logging to capture:
- Why was this order placed?
- What was the market state?
- What was the outcome?
- What would we do differently?

This feeds into HAIST Principle 3 (Experiential Reflective Learning).

### I.7 Integration with Memory System

Consider:
- Checkpointing strategy state (inventory, P&L, active orders)
- Semantic search over trading history ("show me trades during volatile periods")
- HAIST scoring of trading sessions

---

## Questions for CD

These require your deductive reasoning:

1. **Pair selection**: Given the constraint space, which pair(s) offer the best learning/return ratio?

2. **Strategy parameterization**: What specific spreads, sizes, and refresh rates align with our risk tolerance?

3. **Operational mode**: Paper first? Jump to micro live on Christmas (thin markets)?

4. **Monitoring philosophy**: How much human oversight? When does Captain need to be alerted?

5. **Success metrics**: What does "success" look like in week 1? Month 1?

6. **Integration with Rhiz**: How should trading activity feed into the checkpoint/memory system?

---

## Files in Context

```
domains/trading/skills/portfolio_assessment.yaml  # Already defined
domains/trading/strategies/                        # Empty, awaiting strategy configs
core/memory/checkpoints/session_20251222_kraken_credentials.yaml  # Credentials history
.env lines 16-17                                   # Live Kraken credentials
```

---

## Conclusion

This document provides the granular building blocks. The mechanics are laid out inductively from atoms to molecules to cells.

What's missing—deliberately—is the organism. The architectural synthesis. That's for you, CD.

The Captain is at the helm. You have the charts, I've mapped the reefs.

Fair winds.

— First Mate (Code instance, Opus 4.5)
