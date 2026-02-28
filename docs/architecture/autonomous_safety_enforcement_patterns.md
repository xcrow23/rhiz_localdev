# Autonomous Safety Enforcement Patterns

**Extracted from**:
- Session 16 checkpoint (`core/memory/checkpoints/session_20251226_wave2_first_trade.yaml`)
- Session 6 checkpoint (`core/memory/checkpoints/session_20260103_infrastructure_operational.yaml`)

**Sessions**:
- 2025-12-26: First real trade execution (BTC market buy validation)
- 2026-01-03: Infrastructure discovery & critical safety intervention

**Status**: Production-validated across multiple safety scenarios

---

## Overview

This document captures the **autonomous safety enforcement patterns** demonstrated during Rhiz trading system operations. These patterns represent the AI's ability to detect unsafe conditions and enforce safety measures immediately without waiting for human approval—a critical capability for autonomous trading systems.

**Core Principle**: Safety decisions happen *first*, documentation happens *second*, optimization happens *last*.

---

## Pattern 1: Detect → Enforce → Document

### Decision Sequence

When unsafe condition detected:

1. **Detect** unsafe state (live trading mode, missing circuit breaker, exceeded limits)
2. **Enforce** safety immediately (switch to paper mode, halt execution, reject order)
3. **Document** decision rationale in checkpoint/logs
4. **Inform** Captain of action taken

**Never**: Detect → Ask Permission → Enforce (too slow, creates window for unsafe execution)

### Example: Live Trading Mode Discovered (Session 6)

**Situation**: During infrastructure reconnaissance, discovered Fathom Commander running in **live mode** with 2 real trades already executed ($50.68 BTC portfolio on Kraken).

**Detection**:
```yaml
# Infrastructure scan revealed:
containers:
  rhiz_fathom_commander:
    uptime: "5 days"
    mode: "live"  # ⚠️ UNSAFE
    trades_executed: 2
    portfolio_value: "$50.68 BTC"
```

**Enforcement** (immediate, autonomous):
```python
# First Mate action (no Captain approval requested):
1. Changed config.yaml: mode: "paper"
2. Changed state.py default: mode: str = "paper"
3. Rebuilt container
4. Verified mode = "paper"
```

**Documentation**:
```yaml
decisions_made:
  - decision: "Enforce paper mode immediately"
    rationale: "Fathom Commander was in live mode and had executed real trades.
                Safety priority over all else."
    outcome: "Paper mode enforced via code-level default change and container rebuild."
    reversible: true
    time_to_resolve: "20 minutes"
```

**Informing Captain**:
Documented in checkpoint, explained in next session. No pre-approval needed—safety is non-negotiable.

**Outcome**:
- Container switched to paper mode
- Live trading prevented
- No capital loss risk
- Captain approved decision retroactively ("safety priority over all else")

---

## Pattern 2: Pre-Execution Memory Logging

### Decision Before Action

For all capital-deploying operations:

1. **Log decision to memory FIRST** (hypothesis, reasoning, expected outcome)
2. **Execute operation** (order placement, contract deployment)
3. **Update memory with outcome** (success/failure, execution details, learnings)

**Rationale**: If operation fails catastrophically (network error, exchange downtime, system crash), we still have record of intent and reasoning. Enables learning from failures.

### Example: First Real Trade (Session 16)

**Pre-Execution Logging** (BEFORE order placed):
```python
# Decision logged to Qdrant
decision = {
    "id": 38385488643530958,
    "timestamp": "2025-12-26T21:43:00Z",
    "hypothesis": "Pipeline works correctly and trade will execute within seconds",
    "reasoning": "Captain approved 'Execute it!', all pre-flight checks passed,
                  market conditions good (tight spread, high liquidity)",
    "order_params": {
        "pair": "XXBTZUSD",
        "side": "buy",
        "type": "market",
        "volume": 0.0001,
        "estimated_cost": 8.73
    },
    "safety_checks": {
        "below_approval_threshold": True,  # $8.78 < $20
        "below_max_order": True,          # $8.78 < $50
        "balance_sufficient": True        # $50.00 available
    },
    "outcome": "pending"
}
memory.store(decision)
```

**Execution**:
```python
# Order placed AFTER logging
order = kraken_api.add_order(
    pair="XXBTZUSD",
    type="buy",
    ordertype="market",
    volume=0.0001
)
# Order TXID: OBRP7D-MBTUR-4R2O6T
# Execution: <10 seconds
```

**Post-Execution Update**:
```python
# Update memory with outcome
decision["outcome"] = "success"
decision["execution"] = {
    "order_txid": "OBRP7D-MBTUR-4R2O6T",
    "trade_txid": "T3VYUR-HD6IR-433DNS",
    "executed_price": 87420.00,
    "cost": 8.74,
    "fee": 0.03,
    "total": 8.78,
    "execution_time_seconds": 9,
    "slippage_percent": 0.09
}
decision["learnings"] = {
    "execution_speed": "<10 seconds (market order advantage)",
    "slippage": "+0.09% (acceptable for market order)",
    "fees": "0.34% of cost (Kraken standard)",
    "pipeline": "All components functional on first try"
}
memory.update(decision)
```

**Value**:
- If order failed, we'd know *why* it was attempted
- Enables hypothesis tracking (predicted vs actual)
- Creates searchable decision history
- Future instances can learn from execution patterns

---

## Pattern 3: Threshold-Based Approval Workflow

### Autonomous vs Captain-Approved Operations

**Principle**: Small operations autonomous, large operations require Captain approval.

**Configuration**:
```python
# Safety limits (Fathom Commander)
MAX_ORDER_USD = 50.00                # Hard cap—reject any order above this
CAPTAIN_APPROVAL_THRESHOLD = 20.00   # Require Captain approval above this
MAX_DAILY_TRADES = 10                # Circuit breaker—halt after 10 trades/day
CIRCUIT_BREAKER_LOSS_PERCENT = 10.0  # Halt trading if daily loss exceeds 10%
```

### Decision Flow

```
Order Request
    |
    ├─> Validate params (pair, side, type, volume)
    |     └─> Invalid? → Reject with error
    |
    ├─> Calculate USD value
    |     └─> > MAX_ORDER_USD? → Reject with error
    |
    ├─> Check daily limits
    |     ├─> >= MAX_DAILY_TRADES? → Reject (circuit breaker)
    |     └─> Daily loss >= 10%? → Reject (circuit breaker)
    |
    ├─> USD value < CAPTAIN_APPROVAL_THRESHOLD?
    |     ├─> YES → Execute autonomously
    |     |          └─> Log to memory
    |     |          └─> Place order
    |     |          └─> Update memory with outcome
    |     |
    |     └─> NO → Request Captain approval
                   └─> Captain approves?
                         ├─> YES → Execute with logging
                         └─> NO → Cancel, document decision
```

### Example: First Trade (Below Threshold)

**Order**: 0.0001 BTC @ $87,420 = $8.78 total

**Safety Checks**:
```python
# Automatic approval (no Captain interaction needed)
assert order_value_usd < CAPTAIN_APPROVAL_THRESHOLD  # $8.78 < $20 ✅
assert order_value_usd < MAX_ORDER_USD               # $8.78 < $50 ✅
assert daily_trades < MAX_DAILY_TRADES              # 0 < 10 ✅
assert daily_loss_percent < 10.0                    # 0% < 10% ✅

# Approved → Execute immediately
```

**Outcome**: Order executed autonomously in <10 seconds.

### Example: Hypothetical Large Order (Requires Approval)

**Order**: 0.001 BTC @ $87,420 = $87.42 total

**Safety Checks**:
```python
# Order exceeds MAX_ORDER_USD
assert order_value_usd < MAX_ORDER_USD  # $87.42 < $50 ❌ REJECTED

# Would be rejected before Captain even sees it
# Hard limit protects against miscalculation or fat-finger errors
```

**Outcome**: Order rejected with error message. No execution possible above hard cap.

### Example: Medium Order (Requires Approval, Within Cap)

**Order**: 0.0003 BTC @ $87,420 = $26.23 total

**Safety Checks**:
```python
assert order_value_usd < MAX_ORDER_USD               # $26.23 < $50 ✅
assert order_value_usd < CAPTAIN_APPROVAL_THRESHOLD  # $26.23 < $20 ❌

# Requires Captain approval
```

**Workflow**:
```python
# First Mate proposes order to Captain
message = f"""
Trade Proposal (Requires Approval):
- Pair: XXBTZUSD
- Side: buy
- Volume: 0.0003 BTC
- Estimated Cost: $26.23
- Safety: Below $50 max, above $20 approval threshold

Approve execution? (yes/no)
"""

# Captain response: "yes"
# → Execute with pre/post-execution logging

# Captain response: "no"
# → Cancel, document decision, explain reasoning
```

---

## Pattern 4: Multi-Layer Validation

### Validation Layers Before Execution

**Layer 1: Parameter Validation**
```python
def validate_order_params(pair, side, ordertype, volume, price=None):
    """Validate order parameters before submission."""

    # Pair format
    assert pair in SUPPORTED_PAIRS, f"Unsupported pair: {pair}"

    # Side
    assert side in ["buy", "sell"], f"Invalid side: {side}"

    # Order type
    assert ordertype in ["market", "limit"], f"Invalid ordertype: {ordertype}"

    # Volume (must meet Kraken minimums)
    assert volume >= MINIMUM_ORDER_SIZE[pair], f"Volume below minimum: {volume}"

    # Price (required for limit orders)
    if ordertype == "limit":
        assert price is not None, "Limit order requires price"
        assert price > 0, f"Invalid price: {price}"
```

**Layer 2: Balance Verification**
```python
def verify_sufficient_balance(side, volume, estimated_cost):
    """Verify sufficient balance for order."""

    balance = get_account_balance()

    if side == "buy":
        # Need USD for buy orders
        available_usd = balance["ZUSD"]
        assert estimated_cost <= available_usd, \
            f"Insufficient USD: need {estimated_cost}, have {available_usd}"

    elif side == "sell":
        # Need BTC for sell orders
        available_btc = balance["XXBT"]
        assert volume <= available_btc, \
            f"Insufficient BTC: need {volume}, have {available_btc}"
```

**Layer 3: Safety Limits**
```python
def enforce_safety_limits(estimated_cost_usd):
    """Enforce hard caps and circuit breakers."""

    # Hard cap
    assert estimated_cost_usd <= MAX_ORDER_USD, \
        f"Order exceeds max: ${estimated_cost_usd} > ${MAX_ORDER_USD}"

    # Daily trade count
    trades_today = count_trades_today()
    assert trades_today < MAX_DAILY_TRADES, \
        f"Daily trade limit reached: {trades_today} >= {MAX_DAILY_TRADES}"

    # Daily loss circuit breaker
    daily_loss_percent = calculate_daily_loss_percent()
    assert daily_loss_percent < CIRCUIT_BREAKER_LOSS_PERCENT, \
        f"Circuit breaker triggered: {daily_loss_percent}% loss"
```

**Layer 4: Approval Workflow**
```python
def check_approval_requirement(estimated_cost_usd):
    """Determine if Captain approval needed."""

    if estimated_cost_usd >= CAPTAIN_APPROVAL_THRESHOLD:
        # Request approval
        approval = request_captain_approval(order_details)
        assert approval == "yes", "Captain declined execution"
```

**Layer 5: Pre-Execution Logging**
```python
def log_decision_pre_execution(decision_params):
    """Log decision to memory before execution."""

    decision_id = generate_decision_id()
    decision = {
        "id": decision_id,
        "timestamp": datetime.utcnow(),
        "hypothesis": decision_params["hypothesis"],
        "reasoning": decision_params["reasoning"],
        "order_params": decision_params["order"],
        "safety_checks": decision_params["safety"],
        "outcome": "pending"
    }

    memory.store(decision)
    return decision_id
```

**Only After All Layers Pass**: Execute order on exchange.

---

## Pattern 5: Circuit Breakers

### Automatic Trading Halt Conditions

**Purpose**: Prevent runaway losses or excessive trading activity.

**Circuit Breaker 1: Daily Trade Count**
```python
MAX_DAILY_TRADES = 10

def check_trade_count_circuit_breaker():
    """Halt trading if daily limit reached."""

    trades_today = count_trades_today()

    if trades_today >= MAX_DAILY_TRADES:
        halt_trading()
        log_circuit_breaker_trigger({
            "type": "daily_trade_count",
            "trades_today": trades_today,
            "limit": MAX_DAILY_TRADES,
            "action": "halt_trading"
        })
        raise CircuitBreakerError(
            f"Daily trade limit reached: {trades_today} >= {MAX_DAILY_TRADES}"
        )
```

**Circuit Breaker 2: Daily Loss Percentage**
```python
CIRCUIT_BREAKER_LOSS_PERCENT = 10.0

def check_loss_circuit_breaker():
    """Halt trading if daily loss exceeds 10%."""

    starting_portfolio_value = get_start_of_day_portfolio_value()
    current_portfolio_value = get_current_portfolio_value()

    loss_percent = (
        (starting_portfolio_value - current_portfolio_value)
        / starting_portfolio_value
        * 100
    )

    if loss_percent >= CIRCUIT_BREAKER_LOSS_PERCENT:
        halt_trading()
        log_circuit_breaker_trigger({
            "type": "daily_loss_percent",
            "loss_percent": loss_percent,
            "limit": CIRCUIT_BREAKER_LOSS_PERCENT,
            "starting_value": starting_portfolio_value,
            "current_value": current_portfolio_value,
            "action": "halt_trading"
        })
        raise CircuitBreakerError(
            f"Daily loss limit exceeded: {loss_percent:.2f}% >= {CIRCUIT_BREAKER_LOSS_PERCENT}%"
        )
```

**Circuit Breaker 3: Rapid Order Rejection**
```python
def check_rejection_circuit_breaker():
    """Halt trading if too many orders rejected in short period."""

    recent_rejections = count_rejections_last_hour()

    if recent_rejections >= 5:
        halt_trading()
        log_circuit_breaker_trigger({
            "type": "rapid_rejection",
            "rejections_last_hour": recent_rejections,
            "action": "halt_trading_investigate"
        })
        raise CircuitBreakerError(
            f"Too many rejections: {recent_rejections} in last hour. Investigate."
        )
```

**Circuit Breaker Recovery**:
```python
def reset_circuit_breaker(breaker_type, captain_approval_code):
    """Reset circuit breaker with Captain approval."""

    # Require explicit Captain approval code (not just "yes")
    assert captain_approval_code == EXPECTED_RESET_CODE, \
        "Invalid approval code for circuit breaker reset"

    # Log reset
    log_circuit_breaker_reset({
        "type": breaker_type,
        "reset_by": "Captain",
        "timestamp": datetime.utcnow()
    })

    # Resume trading
    resume_trading()
```

---

## Safety Configuration Summary

### Current Production Limits (as of Session 16)

```python
# Hard Caps
MAX_ORDER_USD = 50.00                # Maximum order size (hard reject above)
MAX_DAILY_TRADES = 10                # Maximum trades per day

# Approval Thresholds
CAPTAIN_APPROVAL_THRESHOLD = 20.00   # Require approval above $20

# Circuit Breakers
CIRCUIT_BREAKER_LOSS_PERCENT = 10.0  # Halt trading if daily loss >= 10%
RAPID_REJECTION_THRESHOLD = 5        # Halt if 5+ rejections in 1 hour

# Mode Configuration
DEFAULT_MODE = "paper"               # Always start in paper mode (Session 6 enforcement)
```

### Rationale for Each Limit

**MAX_ORDER_USD ($50)**:
- Matches current capital allocation
- Prevents single catastrophic loss
- Allows testing with real money but minimal risk

**CAPTAIN_APPROVAL_THRESHOLD ($20)**:
- Enables autonomous small trades (<$20) for speed and learning
- Requires Captain approval for larger trades (>=$20) to maintain oversight
- Threshold can increase as trust and capital grow

**MAX_DAILY_TRADES (10)**:
- Prevents runaway trading activity
- Encourages deliberate strategy testing vs random experimentation
- 10 trades sufficient for hypothesis testing without excessive churn

**CIRCUIT_BREAKER_LOSS_PERCENT (10%)**:
- Protects against strategy failures or market crashes
- 10% daily loss acceptable learning cost, but signals "stop and reassess"
- Halts bleeding before capital significantly depleted

**DEFAULT_MODE ("paper")**:
- Safety-first: never start in live mode by accident
- Requires explicit switch to live mode with Captain approval
- Prevents Session 6 scenario (live trading discovered after 5 days)

---

## Key Learnings

### From Session 6 (Infrastructure Discovery)

1. **Detect unsafe conditions immediately**: Live trading mode discovered → enforced paper mode within 20 minutes, no Captain approval needed.

2. **Safety is non-negotiable**: First Mate made autonomous decision to halt live trading. Captain approved retroactively ("safety priority over all else").

3. **Code-level defaults matter**: Changed default `mode: str = "paper"` in state.py to prevent future live mode accidents.

4. **Document safety decisions**: Critical safety enforcement documented in checkpoint with rationale, alternatives considered, outcome.

### From Session 16 (First Real Trade)

1. **Pre-execution logging prevents lost learnings**: Decision recorded before order placed. If trade failed, we'd still know *why* it was attempted.

2. **Multi-layer validation catches errors early**: Parameter validation → balance check → safety limits → approval workflow → pre-logging → execution. Order can't reach exchange without passing all layers.

3. **Threshold-based approval enables speed**: $8.78 trade executed autonomously in <10 seconds because below $20 threshold. No Captain interaction needed for small trades.

4. **Safety checks don't slow execution**: All 5 validation layers completed in <1 second. Safety is fast when architecture is right.

---

## Integration with Other Systems

### Safety + Memory System

**Memory stores safety decisions**:
- Circuit breaker triggers logged to Qdrant
- Safety limit violations searchable semantically
- Approval workflow outcomes tracked over time
- Enables learning: "What conditions triggered circuit breaker in past?"

**Example Query**:
```python
# Find all circuit breaker triggers
results = memory.search(
    "circuit breaker triggered trading halted",
    collection="rhiz_trading_decisions",
    limit=10
)

# Analyze patterns: time of day, market conditions, strategy active
patterns = analyze_circuit_breaker_patterns(results)
```

### Safety + Strategic Intelligence Layer (SIL)

**SIL respects safety constraints**:
- Checks safety limits before recommending trades
- Factors circuit breaker state into strategy selection
- Learns from safety violations (what strategies trigger limits?)

**Example**:
```python
def sil_recommend_trade(market_conditions):
    """Strategic Intelligence Layer recommends trade."""

    # Check circuit breaker state FIRST
    if trading_halted():
        return "NO_TRADE - circuit breaker active"

    # Check daily trade count
    if count_trades_today() >= MAX_DAILY_TRADES - 1:
        return "NO_TRADE - approaching daily limit"

    # Analyze market, recommend trade if safe
    recommendation = analyze_market(market_conditions)

    # Validate recommendation against safety limits
    if recommendation["estimated_cost"] > MAX_ORDER_USD:
        return "NO_TRADE - exceeds max order size"

    return recommendation
```

---

## Future Enhancements

### Adaptive Safety Limits

**Concept**: Safety limits adjust based on performance and capital.

```python
# Current: Fixed limits
MAX_ORDER_USD = 50.00

# Future: Dynamic limits based on portfolio
MAX_ORDER_USD = portfolio_value * 0.10  # 10% of portfolio max per trade

# Or: Adaptive based on win rate
if win_rate > 0.65:
    CAPTAIN_APPROVAL_THRESHOLD = 30.00  # Higher threshold (more autonomy)
elif win_rate < 0.50:
    CAPTAIN_APPROVAL_THRESHOLD = 10.00  # Lower threshold (more oversight)
```

### Predictive Circuit Breakers

**Concept**: Trigger circuit breaker *before* loss limit reached based on predicted trajectory.

```python
def predict_end_of_day_loss():
    """Predict final daily loss based on current trajectory."""

    current_loss_percent = calculate_daily_loss_percent()
    time_elapsed = hours_since_market_open()
    time_remaining = hours_until_market_close()

    # Linear projection
    loss_rate = current_loss_percent / time_elapsed
    predicted_final_loss = loss_rate * (time_elapsed + time_remaining)

    return predicted_final_loss

# Trigger circuit breaker if predicted loss >= 10%
if predict_end_of_day_loss() >= CIRCUIT_BREAKER_LOSS_PERCENT:
    halt_trading()
    log_circuit_breaker_trigger({
        "type": "predictive_daily_loss",
        "predicted_loss": predict_end_of_day_loss(),
        "action": "halt_trading_preemptive"
    })
```

### Safety Audit Tool

**Concept**: Automated tool that checks for safety vulnerabilities.

```python
def audit_safety_configuration():
    """Audit safety configuration for vulnerabilities."""

    issues = []

    # Check if paper mode is default
    if DEFAULT_MODE != "paper":
        issues.append({
            "severity": "critical",
            "issue": "Default mode is not 'paper'",
            "recommendation": "Set DEFAULT_MODE = 'paper' in config"
        })

    # Check if approval threshold exists
    if CAPTAIN_APPROVAL_THRESHOLD is None:
        issues.append({
            "severity": "high",
            "issue": "No approval threshold configured",
            "recommendation": "Set CAPTAIN_APPROVAL_THRESHOLD to enable oversight"
        })

    # Check if circuit breakers exist
    if MAX_DAILY_TRADES is None:
        issues.append({
            "severity": "medium",
            "issue": "No daily trade limit configured",
            "recommendation": "Set MAX_DAILY_TRADES to prevent runaway activity"
        })

    return issues
```

---

## Cross-References

**Source Checkpoints**:
- `core/memory/checkpoints/session_20251226_wave2_first_trade.yaml` (437 lines) - First trade validation
- `core/memory/checkpoints/session_20260103_infrastructure_operational.yaml` (332 lines) - Live mode enforcement

**Related Documentation**:
- `docs/architecture/trading_pipeline_first_trade_case_study.md` - Pipeline validation with safety checks
- `docs/architecture/vps_infrastructure_topology.md` - Infrastructure discovery & safety intervention

**Code Artifacts**:
- `domains/trading/fathom/src/tools/order_tools.py` - Order management with safety validation (330+ lines)
- `domains/trading/fathom_commander/config.yaml` - Safety configuration (mode, limits)
- `domains/trading/fathom_commander/state.py` - Paper mode default enforcement

**Integration Points**:
- Strategic Intelligence Layer (SIL) - Respects safety limits in trade recommendations
- Memory system - Logs safety decisions for semantic search
- Fathom Commander - Orchestrates safety workflow across components

---

**End of Document**

*Extracted Session 74 (2026-01-25) as part of Phase 1.2: Extract Checkpoint Knowledge*
*These patterns represent production-validated safety enforcement across real trading operations.*
