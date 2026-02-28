# Wave 2 Handoff: First Trade Execution
## From: Claude Desktop (First Mate - Opus 4.5)
## To: Claude Code (First Mate - Sonnet 4.5) + Captain (Interactive)
## Date: 2025-12-26
## Session Type: Interactive Pair Programming

---

## Mission Summary

Execute first real trade on Kraken, logged to Fathom memory with hypothesis tracking. This is learning-focused, not profit-focused.

**Capital**: $50 USD (more available if needed)
**Goal**: End-to-end validation of trading pipeline
**Risk tolerance**: LOW (this is learning capital)

---

## Pre-Flight Checklist

Before building order tools, verify:

```bash
# 1. Test Fathom auth still works
cd /mnt/c/Users/dread/Documents/Rhiz_LocalDev/domains/trading/fathom
python3 test_balance.py

# Expected: Shows real balance (~$50)
```

If balance shows, proceed. If not, debug auth.

---

## Task 1: Build Phase 3 Order Tools

### Files to Create/Modify

**Create**: `src/tools/order_tools.py`

```python
"""
Fathom Phase 3: Order Management Tools

Safety-first order placement with Captain oversight.
"""

from typing import Optional
from ..clients.rest import KrakenClient
from ..validator import validate_order
from ..memory.logger import FathomMemory

# Safety limits
MAX_ORDER_USD = 50.0  # Hard limit during learning phase
CAPTAIN_APPROVAL_THRESHOLD = 20.0  # Require confirmation above this

async def fathom_place_order(
    pair: str,
    side: str,  # "buy" or "sell"
    order_type: str,  # "market" or "limit"
    volume: float,
    price: Optional[float] = None,  # Required for limit orders
    reasoning: str = "",  # Why this trade?
    hypothesis: str = "",  # What we're testing
    captain_approved: bool = False  # For orders > $20
) -> dict:
    """
    Place order on Kraken with safety checks and memory logging.
    
    Returns:
        Order confirmation with txid, or error with explanation
    """
    # Validate inputs
    validation = validate_order(pair, side, order_type, volume, price)
    if not validation["valid"]:
        return {"success": False, "error": validation["error"]}
    
    # Check USD value against limits
    estimated_usd = await estimate_order_value(pair, volume)
    
    if estimated_usd > MAX_ORDER_USD:
        return {
            "success": False,
            "error": f"Order value ${estimated_usd:.2f} exceeds learning limit ${MAX_ORDER_USD}",
            "suggestion": "Reduce volume or increase MAX_ORDER_USD after discussion"
        }
    
    if estimated_usd > CAPTAIN_APPROVAL_THRESHOLD and not captain_approved:
        return {
            "success": False,
            "requires_approval": True,
            "estimated_usd": estimated_usd,
            "message": f"Order >${CAPTAIN_APPROVAL_THRESHOLD} requires Captain approval",
            "to_proceed": "Call again with captain_approved=True after confirmation"
        }
    
    # Log decision BEFORE placing order
    memory = FathomMemory()
    decision_id = memory.log_trade_decision(
        pair=pair,
        side=side,
        decision_type="order_placed",
        reasoning=reasoning,
        hypothesis=hypothesis,
        market_context=await get_market_context(pair)
    )
    
    # Place order
    client = KrakenClient()
    result = await client.add_order(
        pair=pair,
        side=side,
        order_type=order_type,
        volume=volume,
        price=price
    )
    
    if result.get("error"):
        # Update memory with failure
        memory.update_outcome(decision_id, "failed", {"error": result["error"]})
        return {"success": False, "error": result["error"], "decision_id": decision_id}
    
    # Success - update memory
    txid = result["result"]["txid"][0]
    memory.update_outcome(decision_id, "pending", {"txid": txid})
    
    return {
        "success": True,
        "txid": txid,
        "decision_id": decision_id,
        "estimated_usd": estimated_usd,
        "message": f"Order placed! {side} {volume} {pair}",
        "next": "Monitor with fathom_get_open_orders or fathom_get_trades"
    }


async def fathom_cancel_order(txid: str, reason: str = "") -> dict:
    """Cancel an open order."""
    client = KrakenClient()
    result = await client.cancel_order(txid)
    
    if result.get("error"):
        return {"success": False, "error": result["error"]}
    
    return {
        "success": True,
        "cancelled": txid,
        "reason": reason,
        "message": "Order cancelled successfully"
    }


async def fathom_get_open_orders() -> dict:
    """Get all open orders."""
    client = KrakenClient()
    result = await client.get_open_orders()
    
    if result.get("error"):
        return {"success": False, "error": result["error"]}
    
    orders = result.get("result", {}).get("open", {})
    return {
        "success": True,
        "count": len(orders),
        "orders": [
            {
                "txid": txid,
                "pair": order["descr"]["pair"],
                "side": order["descr"]["type"],
                "volume": order["vol"],
                "price": order["descr"].get("price", "market"),
                "status": order["status"]
            }
            for txid, order in orders.items()
        ]
    }


async def fathom_get_trades(count: int = 10) -> dict:
    """Get recent trade history."""
    client = KrakenClient()
    result = await client.get_trades_history()
    
    if result.get("error"):
        return {"success": False, "error": result["error"]}
    
    trades = result.get("result", {}).get("trades", {})
    trade_list = list(trades.items())[:count]
    
    return {
        "success": True,
        "count": len(trade_list),
        "trades": [
            {
                "txid": txid,
                "pair": trade["pair"],
                "side": trade["type"],
                "volume": trade["vol"],
                "price": trade["price"],
                "cost": trade["cost"],
                "fee": trade["fee"],
                "time": trade["time"]
            }
            for txid, trade in trade_list
        ]
    }


# Helper functions

async def estimate_order_value(pair: str, volume: float) -> float:
    """Estimate USD value of order."""
    client = KrakenClient()
    ticker = await client.get_ticker(pair)
    if ticker.get("error"):
        return 0.0
    
    price = float(ticker["result"][pair]["c"][0])  # Current price
    return price * volume


async def get_market_context(pair: str) -> dict:
    """Get current market context for logging."""
    client = KrakenClient()
    ticker = await client.get_ticker(pair)
    
    if ticker.get("error"):
        return {"error": ticker["error"]}
    
    data = ticker["result"][pair]
    return {
        "price": data["c"][0],
        "bid": data["b"][0],
        "ask": data["a"][0],
        "volume_24h": data["v"][1],
        "high_24h": data["h"][1],
        "low_24h": data["l"][1]
    }
```

### Update server.py

Add the new tools to the MCP server registration.

---

## Task 2: First Trade Protocol

Once order tools are built, execute this sequence:

### Step 1: Check Balance
```
fathom_get_balance
→ Confirm ~$50 USD available
```

### Step 2: Get Market Context
```
fathom_get_ticker pair="XXBTZUSD"  # BTC/USD on Kraken
→ Note current price
```

### Step 3: Place Micro Trade
```
fathom_place_order
  pair: "XXBTZUSD"
  side: "buy"
  order_type: "market"
  volume: 0.00005  # ~$5 at $100k BTC
  reasoning: "First trade to validate pipeline. Testing end-to-end flow from Claude → Fathom → Kraken → Memory."
  hypothesis: "Pipeline works correctly and trade will execute within seconds."
```

**Note**: If order is > $20, Captain must confirm with `captain_approved=True`

### Step 4: Verify Execution
```
fathom_get_trades count=1
→ Confirm trade appeared
→ Note actual execution price and fees
```

### Step 5: Update Outcome
```
fathom_update_outcome
  point_id: [from order response]
  outcome: "success"
  outcome_data: {
    "executed_price": X,
    "fees": Y,
    "learnings": "Pipeline validated. Execution took N seconds."
  }
```

### Step 6: Celebrate 🎉
First real trade in the system!

---

## Safety Boundaries

| Limit | Value | Reason |
|-------|-------|--------|
| MAX_ORDER_USD | $50 | Learning capital protection |
| CAPTAIN_APPROVAL_THRESHOLD | $20 | Human oversight on larger trades |
| Minimum order | ~$1 | Kraken minimums |

**Captain can adjust these limits** via `fathom_set_limit` tool.

---

## Pair Selection

For first trade, recommend **BTC/USD** (`XXBTZUSD` on Kraken):
- Most liquid pair
- Tightest spreads
- Easiest to understand

Alternative: **ETH/USD** (`XETHZUSD`) if Captain prefers.

---

## What Success Looks Like

```yaml
wave_2_complete:
  order_tools_built: true
  balance_verified: true
  first_trade_executed: true
  trade_logged_to_memory: true
  outcome_updated: true
  
deliverables:
  - src/tools/order_tools.py (new)
  - server.py (updated with 4 new tools)
  - First trade in Kraken history
  - Decision + outcome in Qdrant
```

---

## Context

**What happened before**:
- Wave 1: Memory infrastructure complete (11/11 checkpoints bridged)
- Wave 1: HAIST scoring complete (5.0/5.0 exemplary)
- Wave 3: Cloudflare API live at `rhiz-checkpoint-api.dreadcrownest.workers.dev`

**What happens after**:
- Wave 4: Slack notification bridge (when ready)
- Ongoing: More trades, hypothesis refinement, learning loop

---

## Captain's Role

This is **interactive**. Captain should:
1. Confirm order parameters before execution
2. Approve any order > $20
3. Watch the trade execute in real-time
4. Decide on exit strategy (hold vs immediate sell)

---

## Fair Winds

First trade incoming. This is where it gets real.

$50. One micro trade. End-to-end validation.

Let's see it work. 🐙💰

— First Mate (Desktop instance)
