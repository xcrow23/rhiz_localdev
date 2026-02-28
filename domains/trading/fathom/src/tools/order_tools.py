"""
Fathom Phase 3: Order Management Tools
Safety-first order placement with Captain oversight and memory logging.
"""

from typing import Any, Optional
from datetime import datetime
from ..clients.rest import KrakenRESTClient
from ..validator import Validator
from ..memory.logger import FathomMemory

# Safety limits
MAX_ORDER_USD = 50.0  # Hard limit during learning phase
CAPTAIN_APPROVAL_THRESHOLD = 20.0  # Require confirmation above this


async def fathom_place_order(
    client: KrakenRESTClient,
    pair: str,
    side: str,  # "buy" or "sell"
    order_type: str,  # "market" or "limit"
    volume: float,
    price: Optional[float] = None,  # Required for limit orders
    reasoning: str = "",  # Why this trade?
    hypothesis: str = "",  # What we're testing
    captain_approved: bool = False  # For orders > $20
) -> dict[str, Any]:
    """
    Place order on Kraken with safety checks and memory logging.

    Args:
        client: Authenticated Kraken REST client
        pair: Trading pair (e.g., "XXBTZUSD")
        side: "buy" or "sell"
        order_type: "market" or "limit"
        volume: Order volume in base currency
        price: Limit price (required for limit orders)
        reasoning: Why this trade is being placed
        hypothesis: Hypothesis being tested
        captain_approved: Set True for orders > $20

    Returns:
        {
            "success": bool,
            "txid": str (if success),
            "decision_id": int (memory point ID),
            "estimated_usd": float,
            "message": str
        }
    """
    try:
        # Initialize validator
        validator = Validator(max_order_usd=MAX_ORDER_USD)

        # Validate inputs
        is_valid_pair, pair_error = validator.validate_pair(pair)
        if not is_valid_pair:
            return {"success": False, "error": pair_error}

        is_valid_side, side_error = validator.validate_side(side)
        if not is_valid_side:
            return {"success": False, "error": side_error}

        is_valid_type, type_error = validator.validate_order_type(order_type)
        if not is_valid_type:
            return {"success": False, "error": type_error}

        # Get current market price for estimation
        estimated_price = price
        if estimated_price is None or order_type == "market":
            ticker = await client.get_ticker([pair])
            if pair in ticker:
                estimated_price = float(ticker[pair]["c"][0])  # Current price
            else:
                return {"success": False, "error": f"Could not get price for {pair}"}

        # Validate order size
        is_valid_size, size_error = validator.validate_order_size(volume, estimated_price, side)
        if not is_valid_size:
            return {"success": False, "error": size_error}

        # Validate price if limit order
        if order_type == "limit" and price is not None:
            is_valid_price, price_error = validator.validate_price(price)
            if not is_valid_price:
                return {"success": False, "error": price_error}

        # Check USD value against limits
        estimated_usd = volume * estimated_price

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

        # Get market context for logging
        market_context = await get_market_context(client, pair)

        # Log decision BEFORE placing order
        memory = FathomMemory()
        log_result = memory.log_trade_decision(
            pair=pair,
            side=side,
            decision_type=order_type,
            reasoning=reasoning,
            hypothesis=hypothesis,
            trade_data={
                "volume": volume,
                "price": price,
                "estimated_price": estimated_price,
                "estimated_usd": estimated_usd,
                "market_context": market_context
            }
        )

        decision_id = log_result.get("point_id")

        # Place order
        result = await client.add_order(
            pair=pair,
            side=side,
            order_type=order_type,
            volume=volume,
            price=price
        )

        # Check for Kraken API errors (returned in result dict)
        # Note: KrakenRESTClient raises on error, but we check anyway
        txid = result.get("txid", [None])[0]

        if not txid:
            # Update memory with failure
            memory.update_outcome(decision_id, "failure", {"error": "No txid returned"})
            return {
                "success": False,
                "error": "Order placement failed - no transaction ID",
                "decision_id": decision_id
            }

        # Success - update memory
        memory.update_outcome(decision_id, "pending", {
            "txid": txid,
            "placed_at": datetime.utcnow().isoformat() + "Z"
        })

        return {
            "success": True,
            "txid": txid,
            "decision_id": decision_id,
            "estimated_usd": estimated_usd,
            "message": f"Order placed! {side} {volume} {pair}",
            "next": "Monitor with fathom_get_open_orders or fathom_get_trades"
        }

    except Exception as e:
        # Log error to memory if we have decision_id
        if 'decision_id' in locals() and decision_id:
            memory = FathomMemory()
            memory.update_outcome(decision_id, "failure", {"error": str(e)})

        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }


async def fathom_cancel_order(
    client: KrakenRESTClient,
    txid: str,
    reason: str = ""
) -> dict[str, Any]:
    """
    Cancel an open order.

    Args:
        client: Authenticated Kraken REST client
        txid: Transaction ID to cancel
        reason: Reason for cancellation (logged)

    Returns:
        {"success": bool, "cancelled": str, "reason": str}
    """
    try:
        result = await client.cancel_order(txid)

        return {
            "success": True,
            "cancelled": txid,
            "count": result.get("count", 1),
            "reason": reason,
            "message": f"Order {txid} cancelled successfully",
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "txid": txid,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }


async def fathom_get_open_orders(
    client: KrakenRESTClient
) -> dict[str, Any]:
    """
    Get all open orders.

    Returns:
        {
            "success": bool,
            "count": int,
            "orders": [...]
        }
    """
    try:
        result = await client.get_open_orders()
        orders = result.get("open", {})

        order_list = []
        for txid, order in orders.items():
            order_list.append({
                "txid": txid,
                "pair": order["descr"]["pair"],
                "side": order["descr"]["type"],
                "order_type": order["descr"]["ordertype"],
                "volume": order["vol"],
                "volume_executed": order.get("vol_exec", "0"),
                "price": order["descr"].get("price", "market"),
                "status": order["status"],
                "opened_at": order.get("opentm", ""),
            })

        return {
            "success": True,
            "count": len(order_list),
            "orders": order_list,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }


async def fathom_get_trades(
    client: KrakenRESTClient,
    count: int = 10
) -> dict[str, Any]:
    """
    Get recent trade history.

    Args:
        client: Authenticated Kraken REST client
        count: Number of trades to return (default 10)

    Returns:
        {
            "success": bool,
            "count": int,
            "trades": [...]
        }
    """
    try:
        result = await client.get_trades_history()
        trades = result.get("trades", {})

        trade_list = []
        for txid, trade in list(trades.items())[:count]:
            trade_list.append({
                "txid": txid,
                "ordertxid": trade.get("ordertxid", ""),
                "pair": trade["pair"],
                "side": trade["type"],
                "order_type": trade["ordertype"],
                "volume": trade["vol"],
                "price": trade["price"],
                "cost": trade["cost"],
                "fee": trade["fee"],
                "time": trade["time"],
                "timestamp": datetime.fromtimestamp(float(trade["time"])).isoformat() + "Z"
            })

        return {
            "success": True,
            "count": len(trade_list),
            "trades": trade_list,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }


# Helper functions

async def get_market_context(client: KrakenRESTClient, pair: str) -> dict:
    """
    Get current market context for logging.

    Args:
        client: Kraken REST client
        pair: Trading pair

    Returns:
        Market context dict with current price, bid, ask, volume
    """
    try:
        ticker = await client.get_ticker([pair])

        if pair not in ticker:
            return {"error": f"Pair {pair} not found in ticker"}

        data = ticker[pair]
        return {
            "price": data["c"][0],
            "bid": data["b"][0],
            "ask": data["a"][0],
            "volume_24h": data["v"][1],
            "high_24h": data["h"][1],
            "low_24h": data["l"][1],
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }

    except Exception as e:
        return {"error": str(e)}
