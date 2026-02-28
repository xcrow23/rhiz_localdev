"""
Fathom Commander MCP Server
Claude Code's Trading Command Center

An MCP server providing trading tools with safety limits,
approval workflows, and n8n heartbeat monitoring.
"""

import asyncio
import json
import sys
import os
from datetime import datetime
from typing import Any

# Ensure we can import from parent
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp.server import Server
from mcp.types import Tool, TextContent

from state import get_state_manager

# Import tool modules
from tools.market import (
    get_market_monitor,
    market_get_ticker,
    market_get_ohlc,
    market_get_orderbook,
    market_analyze
)
from tools.execution import (
    get_execution_engine,
    execute_trade,
    validate_trade,
    approve_order,
    reject_order,
    cancel_order,
    get_open_orders,
    get_trade_history
)
from tools.portfolio import (
    get_portfolio_manager,
    portfolio_get_balance,
    portfolio_get_holdings,
    portfolio_get_summary,
    portfolio_get_performance,
    portfolio_track_position,
    portfolio_close_position
)
from tools.strategy import (
    get_strategy_manager,
    strategy_list,
    strategy_activate,
    strategy_deactivate,
    strategy_signal,
    strategy_check_exits,
    strategy_analyze_opportunity
)
from tools.alerts import (
    get_alert_manager,
    alert_send,
    alert_trade_executed,
    alert_approval_request,
    alert_error,
    alert_history,
    alert_status
)


# Initialize MCP server
app = Server("fathom-commander")

# Track startup time
_start_time = datetime.utcnow()


def get_uptime() -> str:
    """Get uptime as human-readable string."""
    delta = datetime.utcnow() - _start_time
    hours, remainder = divmod(int(delta.total_seconds()), 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours}h {minutes}m {seconds}s"


def check_kraken() -> str:
    """Check Kraken auth status."""
    try:
        engine = get_execution_engine()
        return "ok" if engine.auth else "not_configured"
    except Exception:
        return "error"


def check_qdrant() -> str:
    """Check Qdrant connection."""
    try:
        import urllib.request
        req = urllib.request.Request("http://localhost:6333/health")
        with urllib.request.urlopen(req, timeout=2) as resp:
            return "ok" if resp.status == 200 else "error"
    except Exception:
        return "not_available"


# =========================
# Core Tools
# =========================

@app.list_tools()
async def list_tools() -> list[Tool]:
    """List all available tools."""
    return [
        # Heartbeat
        Tool(
            name="heartbeat",
            description="Health check - called by n8n every 60s. Returns operational status.",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),

        # Market Tools
        Tool(
            name="market_ticker",
            description="Get current ticker data for trading pairs",
            inputSchema={
                "type": "object",
                "properties": {
                    "pairs": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Trading pairs (e.g., ['XXBTZUSD', 'XETHZUSD'])"
                    }
                },
                "required": ["pairs"]
            }
        ),
        Tool(
            name="market_ohlc",
            description="Get OHLC candlestick data",
            inputSchema={
                "type": "object",
                "properties": {
                    "pair": {"type": "string", "description": "Trading pair"},
                    "interval": {"type": "integer", "description": "Candle interval in minutes", "default": 5}
                },
                "required": ["pair"]
            }
        ),
        Tool(
            name="market_analyze",
            description="Analyze market conditions for trading",
            inputSchema={
                "type": "object",
                "properties": {
                    "pair": {"type": "string", "description": "Trading pair to analyze"}
                },
                "required": ["pair"]
            }
        ),

        # Execution Tools
        Tool(
            name="execute_trade",
            description="Execute a trade with safety checks. Requires approval for orders > $20.",
            inputSchema={
                "type": "object",
                "properties": {
                    "pair": {"type": "string", "description": "Trading pair"},
                    "side": {"type": "string", "enum": ["buy", "sell"], "description": "Trade direction"},
                    "order_type": {"type": "string", "enum": ["market", "limit"], "description": "Order type"},
                    "volume": {"type": "number", "description": "Order volume in base currency"},
                    "price": {"type": "number", "description": "Limit price (required for limit orders)"},
                    "reasoning": {"type": "string", "description": "Why this trade"},
                    "hypothesis": {"type": "string", "description": "What we're testing"},
                    "captain_approved": {"type": "boolean", "description": "Set true if Captain approved", "default": False}
                },
                "required": ["pair", "side", "order_type", "volume"]
            }
        ),
        Tool(
            name="validate_trade",
            description="Validate a trade without executing",
            inputSchema={
                "type": "object",
                "properties": {
                    "pair": {"type": "string"},
                    "side": {"type": "string", "enum": ["buy", "sell"]},
                    "order_type": {"type": "string", "enum": ["market", "limit"]},
                    "volume": {"type": "number"},
                    "price": {"type": "number"}
                },
                "required": ["pair", "side", "order_type", "volume"]
            }
        ),
        Tool(
            name="approve_order",
            description="Approve a pending order (Captain command)",
            inputSchema={
                "type": "object",
                "properties": {
                    "approval_id": {"type": "string", "description": "The approval ID to approve"}
                },
                "required": ["approval_id"]
            }
        ),
        Tool(
            name="reject_order",
            description="Reject a pending order (Captain command)",
            inputSchema={
                "type": "object",
                "properties": {
                    "approval_id": {"type": "string", "description": "The approval ID to reject"},
                    "reason": {"type": "string", "description": "Reason for rejection"}
                },
                "required": ["approval_id"]
            }
        ),
        Tool(
            name="cancel_order",
            description="Cancel an open order",
            inputSchema={
                "type": "object",
                "properties": {
                    "txid": {"type": "string", "description": "Transaction ID to cancel"},
                    "reason": {"type": "string", "description": "Reason for cancellation"}
                },
                "required": ["txid"]
            }
        ),
        Tool(
            name="get_open_orders",
            description="Get all open orders",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="get_trade_history",
            description="Get recent trade history",
            inputSchema={
                "type": "object",
                "properties": {
                    "count": {"type": "integer", "description": "Number of trades to fetch", "default": 10}
                },
                "required": []
            }
        ),

        # Portfolio Tools
        Tool(
            name="portfolio_balance",
            description="Get account balances",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="portfolio_holdings",
            description="Get holdings with USD values",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="portfolio_summary",
            description="Get comprehensive portfolio summary",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="portfolio_performance",
            description="Get trading performance metrics",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),

        # Strategy Tools
        Tool(
            name="strategy_list",
            description="List available trading strategies",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="strategy_activate",
            description="Activate a trading strategy",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Strategy name to activate"}
                },
                "required": ["name"]
            }
        ),
        Tool(
            name="strategy_deactivate",
            description="Deactivate current strategy",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="strategy_signal",
            description="Generate trading signal using active strategy",
            inputSchema={
                "type": "object",
                "properties": {
                    "pair": {"type": "string", "description": "Trading pair"}
                },
                "required": ["pair"]
            }
        ),
        Tool(
            name="strategy_check_exits",
            description="Check all positions for exit signals",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="strategy_analyze_opportunity",
            description="Full opportunity analysis - market + strategy signal",
            inputSchema={
                "type": "object",
                "properties": {
                    "pair": {"type": "string", "description": "Trading pair"}
                },
                "required": ["pair"]
            }
        ),

        # Alert Tools
        Tool(
            name="alert_send",
            description="Send a notification",
            inputSchema={
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "message": {"type": "string"},
                    "alert_type": {"type": "string", "enum": ["info", "success", "warning", "error"], "default": "info"},
                    "priority": {"type": "string", "enum": ["low", "normal", "high", "urgent"], "default": "normal"}
                },
                "required": ["title", "message"]
            }
        ),
        Tool(
            name="alert_history",
            description="Get recent alert history",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {"type": "integer", "default": 20}
                },
                "required": []
            }
        ),
        Tool(
            name="alert_status",
            description="Get alert system status",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),

        # State Management
        Tool(
            name="set_mode",
            description="Set operational mode (live, paper, disabled, emergency_stop)",
            inputSchema={
                "type": "object",
                "properties": {
                    "mode": {"type": "string", "enum": ["live", "paper", "disabled", "emergency_stop"]}
                },
                "required": ["mode"]
            }
        ),
        Tool(
            name="get_state_summary",
            description="Get current state summary",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="get_pending_approvals",
            description="Get all pending approval requests",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool calls."""

    try:
        # Update heartbeat on any tool call
        state = get_state_manager()
        state.update_heartbeat()

        result = await _execute_tool(name, arguments)

        # Save state after operations that modify it
        if name in ["execute_trade", "approve_order", "reject_order", "set_mode",
                    "strategy_activate", "strategy_deactivate", "portfolio_track_position",
                    "portfolio_close_position"]:
            state.save()

        return [TextContent(type="text", text=json.dumps(result, indent=2))]

    except Exception as e:
        error_result = {"success": False, "error": str(e)}
        return [TextContent(type="text", text=json.dumps(error_result, indent=2))]


async def _execute_tool(name: str, args: dict) -> Any:
    """Execute a specific tool."""

    # Heartbeat - the core n8n integration point
    if name == "heartbeat":
        state = get_state_manager()
        summary = state.get_summary()
        positions = state.get_positions()
        pending = state.get_pending_approvals()

        return {
            "status": "alive",
            "uptime": get_uptime(),
            "mode": summary.get("mode", "unknown"),
            "positions": {
                "count": len(positions),
                "pairs": list(positions.keys())
            },
            "pending_approvals": {
                "count": len(pending),
                "ids": list(pending.keys())
            },
            "today": {
                "trades": summary.get("trades_today", 0),
                "trades_remaining": summary.get("trades_remaining", 0),
                "pnl": summary.get("daily_pnl", 0),
                "loss_current": summary.get("daily_loss_current", 0)
            },
            "strategy": summary.get("active_strategy"),
            "trading_halted": summary.get("trading_halted", False),
            "halt_reason": summary.get("halt_reason", ""),
            "health": {
                "kraken_auth": check_kraken(),
                "memory": check_qdrant(),
                "errors": summary.get("consecutive_errors", 0)
            },
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }

    # Market Tools
    elif name == "market_ticker":
        return await market_get_ticker(args["pairs"])
    elif name == "market_ohlc":
        return await market_get_ohlc(args["pair"], args.get("interval", 5))
    elif name == "market_analyze":
        return await market_analyze(args["pair"])

    # Execution Tools
    elif name == "execute_trade":
        return await execute_trade(
            pair=args["pair"],
            side=args["side"],
            order_type=args["order_type"],
            volume=args["volume"],
            price=args.get("price"),
            reasoning=args.get("reasoning", ""),
            hypothesis=args.get("hypothesis", ""),
            captain_approved=args.get("captain_approved", False)
        )
    elif name == "validate_trade":
        return await validate_trade(
            pair=args["pair"],
            side=args["side"],
            order_type=args["order_type"],
            volume=args["volume"],
            price=args.get("price")
        )
    elif name == "approve_order":
        return await approve_order(args["approval_id"])
    elif name == "reject_order":
        return await reject_order(args["approval_id"], args.get("reason", ""))
    elif name == "cancel_order":
        return await cancel_order(args["txid"], args.get("reason", ""))
    elif name == "get_open_orders":
        return await get_open_orders()
    elif name == "get_trade_history":
        return await get_trade_history(args.get("count", 10))

    # Portfolio Tools
    elif name == "portfolio_balance":
        return await portfolio_get_balance()
    elif name == "portfolio_holdings":
        return await portfolio_get_holdings()
    elif name == "portfolio_summary":
        return await portfolio_get_summary()
    elif name == "portfolio_performance":
        return await portfolio_get_performance()

    # Strategy Tools
    elif name == "strategy_list":
        return strategy_list()
    elif name == "strategy_activate":
        return strategy_activate(args["name"])
    elif name == "strategy_deactivate":
        return strategy_deactivate()
    elif name == "strategy_signal":
        return await strategy_signal(args["pair"])
    elif name == "strategy_check_exits":
        return await strategy_check_exits()
    elif name == "strategy_analyze_opportunity":
        return await strategy_analyze_opportunity(args["pair"])

    # Alert Tools
    elif name == "alert_send":
        return alert_send(
            title=args["title"],
            message=args["message"],
            alert_type=args.get("alert_type", "info"),
            priority=args.get("priority", "normal")
        )
    elif name == "alert_history":
        return alert_history(args.get("limit", 20))
    elif name == "alert_status":
        return alert_status()

    # State Management
    elif name == "set_mode":
        state = get_state_manager()
        state.set_mode(args["mode"])
        state.save()
        return {"success": True, "mode": args["mode"], "message": f"Mode set to {args['mode']}"}

    elif name == "get_state_summary":
        state = get_state_manager()
        return {"success": True, "summary": state.get_summary()}

    elif name == "get_pending_approvals":
        state = get_state_manager()
        return {"success": True, "pending": state.get_pending_approvals()}

    else:
        return {"success": False, "error": f"Unknown tool: {name}"}


async def main():
    """Run the MCP server."""
    from mcp.server.stdio import stdio_server

    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
