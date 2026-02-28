"""
Fathom MCP Server
Main entry point for the Fathom Model Context Protocol server.
"""

import asyncio
import os
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from .auth import CredentialManager
from .clients.rest import KrakenRESTClient
from .clients.websocket import KrakenWebSocketClient
from .rate_limiter import RateLimiter
from .validator import Validator

from .tools import system, account, market, memory_tools, order_tools
from .memory.logger import FathomMemory


# Initialize server
app = Server("fathom")

# Global instances (initialized on startup)
auth_manager: CredentialManager = None
rest_client: KrakenRESTClient = None
ws_client: KrakenWebSocketClient = None
rate_limiter: RateLimiter = None
validator: Validator = None
memory: FathomMemory = None


# =========================
# Tool Definitions
# =========================

TOOLS = [
    Tool(
        name="fathom_health_check",
        description="Check Fathom MCP health and Kraken API connectivity",
        inputSchema={
            "type": "object",
            "properties": {},
            "required": []
        }
    ),
    Tool(
        name="fathom_get_rate_limits",
        description="Get current API rate limit status",
        inputSchema={
            "type": "object",
            "properties": {},
            "required": []
        }
    ),
    Tool(
        name="fathom_get_balance",
        description="Get account balance for all assets",
        inputSchema={
            "type": "object",
            "properties": {},
            "required": []
        }
    ),
    Tool(
        name="fathom_get_portfolio_summary",
        description="Get portfolio summary with USD valuations",
        inputSchema={
            "type": "object",
            "properties": {},
            "required": []
        }
    ),
    Tool(
        name="fathom_get_trade_balance",
        description="Get detailed trade balance summary",
        inputSchema={
            "type": "object",
            "properties": {
                "asset": {
                    "type": "string",
                    "description": "Base asset for balance calculation (default: USD)",
                    "default": "USD"
                }
            },
            "required": []
        }
    ),
    Tool(
        name="fathom_get_ticker",
        description="Get ticker information (price, volume, spread) for trading pairs",
        inputSchema={
            "type": "object",
            "properties": {
                "pairs": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of trading pairs (e.g., ['BTC/USD', 'ETH/USD'])"
                }
            },
            "required": ["pairs"]
        }
    ),
    Tool(
        name="fathom_get_orderbook",
        description="Get order book (market depth) for a trading pair",
        inputSchema={
            "type": "object",
            "properties": {
                "pair": {
                    "type": "string",
                    "description": "Trading pair (e.g., 'BTC/USD')"
                },
                "depth": {
                    "type": "integer",
                    "description": "Number of levels to return (10, 25, 100, 500, 1000)",
                    "default": 10,
                    "enum": [10, 25, 100, 500, 1000]
                }
            },
            "required": ["pair"]
        }
    ),
    Tool(
        name="fathom_get_ohlc",
        description="Get OHLC (candlestick) data for a trading pair",
        inputSchema={
            "type": "object",
            "properties": {
                "pair": {
                    "type": "string",
                    "description": "Trading pair (e.g., 'BTC/USD')"
                },
                "interval": {
                    "type": "integer",
                    "description": "Interval in minutes (1, 5, 15, 30, 60, 240, 1440, 10080, 21600)",
                    "default": 1,
                    "enum": [1, 5, 15, 30, 60, 240, 1440, 10080, 21600]
                },
                "since": {
                    "type": "integer",
                    "description": "Return data since this timestamp (optional)"
                }
            },
            "required": ["pair"]
        }
    ),
    Tool(
        name="fathom_get_recent_trades",
        description="Get recent public trades for a trading pair",
        inputSchema={
            "type": "object",
            "properties": {
                "pair": {
                    "type": "string",
                    "description": "Trading pair (e.g., 'BTC/USD')"
                },
                "since": {
                    "type": "integer",
                    "description": "Return trades since this ID (optional)"
                }
            },
            "required": ["pair"]
        }
    ),
    Tool(
        name="fathom_get_websocket_status",
        description="Get WebSocket connection status and active subscriptions",
        inputSchema={
            "type": "object",
            "properties": {},
            "required": []
        }
    ),
    # Memory Tools
    Tool(
        name="fathom_log_decision",
        description="Log a trading decision to memory with reasoning and hypothesis",
        inputSchema={
            "type": "object",
            "properties": {
                "pair": {"type": "string", "description": "Trading pair (e.g., 'BTC/USD')"},
                "side": {"type": "string", "enum": ["buy", "sell", "observe"], "description": "Action type"},
                "decision_type": {"type": "string", "enum": ["market", "limit", "observe", "hypothesis"], "description": "Decision type"},
                "reasoning": {"type": "string", "description": "Why this decision was made"},
                "hypothesis": {"type": "string", "description": "Optional hypothesis being tested"},
                "trade_data": {"type": "object", "description": "Optional actual trade details"}
            },
            "required": ["pair", "side", "decision_type", "reasoning"]
        }
    ),
    Tool(
        name="fathom_search_memory",
        description="Search trading memory semantically for patterns and insights",
        inputSchema={
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query (e.g., 'successful BTC buys during consolidation')"},
                "limit": {"type": "integer", "default": 5, "description": "Number of results"},
                "pair": {"type": "string", "description": "Optional filter by pair"},
                "outcome": {"type": "string", "enum": ["success", "failure", "pending", "learning"], "description": "Optional filter by outcome"}
            },
            "required": ["query"]
        }
    ),
    Tool(
        name="fathom_update_outcome",
        description="Update the outcome of a logged decision",
        inputSchema={
            "type": "object",
            "properties": {
                "point_id": {"type": "integer", "description": "Decision ID from fathom_log_decision"},
                "outcome": {"type": "string", "enum": ["success", "failure", "learning", "ongoing"], "description": "Outcome classification"},
                "pnl": {"type": "number", "description": "Optional profit/loss amount"},
                "notes": {"type": "string", "description": "Optional outcome notes"}
            },
            "required": ["point_id", "outcome"]
        }
    ),
    Tool(
        name="fathom_review_hypothesis",
        description="Review all outcomes for a specific hypothesis",
        inputSchema={
            "type": "object",
            "properties": {
                "hypothesis": {"type": "string", "description": "Hypothesis text to review"}
            },
            "required": ["hypothesis"]
        }
    ),
    Tool(
        name="fathom_get_memory_stats",
        description="Get memory collection statistics and health",
        inputSchema={
            "type": "object",
            "properties": {},
            "required": []
        }
    ),
    # Order Management Tools (Phase 3)
    Tool(
        name="fathom_place_order",
        description="Place order on Kraken with safety checks and memory logging. Orders >$20 require captain_approved=True",
        inputSchema={
            "type": "object",
            "properties": {
                "pair": {"type": "string", "description": "Trading pair (e.g., 'XXBTZUSD')"},
                "side": {"type": "string", "enum": ["buy", "sell"], "description": "Order side"},
                "order_type": {"type": "string", "enum": ["market", "limit"], "description": "Order type"},
                "volume": {"type": "number", "description": "Order volume in base currency"},
                "price": {"type": "number", "description": "Limit price (required for limit orders)"},
                "reasoning": {"type": "string", "description": "Why this trade is being placed"},
                "hypothesis": {"type": "string", "description": "Optional hypothesis being tested"},
                "captain_approved": {"type": "boolean", "default": False, "description": "Set true for orders >$20"}
            },
            "required": ["pair", "side", "order_type", "volume"]
        }
    ),
    Tool(
        name="fathom_cancel_order",
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
        name="fathom_get_open_orders",
        description="Get all open orders",
        inputSchema={
            "type": "object",
            "properties": {},
            "required": []
        }
    ),
    Tool(
        name="fathom_get_trades",
        description="Get recent trade history",
        inputSchema={
            "type": "object",
            "properties": {
                "count": {"type": "integer", "default": 10, "description": "Number of trades to return"}
            },
            "required": []
        }
    ),
]


# =========================
# Tool Handlers
# =========================

@app.list_tools()
async def list_tools() -> list[Tool]:
    """List all available tools."""
    return TOOLS


@app.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    """Handle tool calls."""

    try:
        # Ensure rate limiting
        await rate_limiter.wait_if_needed()
        rate_limiter.record_call()

        # System tools
        if name == "fathom_health_check":
            result = await system.fathom_health_check(rest_client, rate_limiter)

        elif name == "fathom_get_rate_limits":
            result = await system.fathom_get_rate_limits(rate_limiter)

        elif name == "fathom_get_websocket_status":
            result = await system.fathom_get_websocket_status(ws_client)

        # Account tools
        elif name == "fathom_get_balance":
            result = await account.fathom_get_balance(rest_client)

        elif name == "fathom_get_portfolio_summary":
            result = await account.fathom_get_portfolio_summary(rest_client)

        elif name == "fathom_get_trade_balance":
            asset = arguments.get("asset", "USD")
            result = await account.fathom_get_trade_balance(rest_client, asset=asset)

        # Market tools
        elif name == "fathom_get_ticker":
            pairs = arguments["pairs"]
            result = await market.fathom_get_ticker(rest_client, validator, pairs)

        elif name == "fathom_get_orderbook":
            pair = arguments["pair"]
            depth = arguments.get("depth", 10)
            result = await market.fathom_get_orderbook(rest_client, validator, pair, depth)

        elif name == "fathom_get_ohlc":
            pair = arguments["pair"]
            interval = arguments.get("interval", 1)
            since = arguments.get("since")
            result = await market.fathom_get_ohlc(rest_client, validator, pair, interval, since)

        elif name == "fathom_get_recent_trades":
            pair = arguments["pair"]
            since = arguments.get("since")
            result = await market.fathom_get_recent_trades(rest_client, validator, pair, since)

        # Memory tools
        elif name == "fathom_log_decision":
            result = await memory_tools.fathom_log_decision(
                memory=memory,
                pair=arguments["pair"],
                side=arguments["side"],
                decision_type=arguments["decision_type"],
                reasoning=arguments["reasoning"],
                hypothesis=arguments.get("hypothesis"),
                trade_data=arguments.get("trade_data")
            )

        elif name == "fathom_search_memory":
            result = await memory_tools.fathom_search_memory(
                memory=memory,
                query=arguments["query"],
                limit=arguments.get("limit", 5),
                pair=arguments.get("pair"),
                outcome=arguments.get("outcome")
            )

        elif name == "fathom_update_outcome":
            result = await memory_tools.fathom_update_outcome(
                memory=memory,
                point_id=arguments["point_id"],
                outcome=arguments["outcome"],
                pnl=arguments.get("pnl"),
                notes=arguments.get("notes")
            )

        elif name == "fathom_review_hypothesis":
            result = await memory_tools.fathom_review_hypothesis(
                memory=memory,
                hypothesis=arguments["hypothesis"]
            )

        elif name == "fathom_get_memory_stats":
            result = await memory_tools.fathom_get_memory_stats(memory=memory)

        # Order Management tools (Phase 3)
        elif name == "fathom_place_order":
            result = await order_tools.fathom_place_order(
                client=rest_client,
                pair=arguments["pair"],
                side=arguments["side"],
                order_type=arguments["order_type"],
                volume=arguments["volume"],
                price=arguments.get("price"),
                reasoning=arguments.get("reasoning", ""),
                hypothesis=arguments.get("hypothesis", ""),
                captain_approved=arguments.get("captain_approved", False)
            )

        elif name == "fathom_cancel_order":
            result = await order_tools.fathom_cancel_order(
                client=rest_client,
                txid=arguments["txid"],
                reason=arguments.get("reason", "")
            )

        elif name == "fathom_get_open_orders":
            result = await order_tools.fathom_get_open_orders(client=rest_client)

        elif name == "fathom_get_trades":
            result = await order_tools.fathom_get_trades(
                client=rest_client,
                count=arguments.get("count", 10)
            )

        else:
            result = {"error": f"Unknown tool: {name}"}

        # Return result as text content
        import json
        return [TextContent(type="text", text=json.dumps(result, indent=2))]

    except Exception as e:
        import json
        error_result = {
            "success": False,
            "error": str(e),
            "tool": name
        }
        return [TextContent(type="text", text=json.dumps(error_result, indent=2))]


# =========================
# Server Lifecycle
# =========================

async def async_message_handler(data: dict):
    """Handle WebSocket messages (placeholder for future streaming tools)."""
    # TODO: Implement message broadcasting to connected clients
    pass


async def initialize_server():
    """Initialize server components."""
    global auth_manager, rest_client, ws_client, rate_limiter, validator, memory

    # Load configuration from environment
    tier = os.getenv("FATHOM_KRAKEN_TIER", "starter")
    max_order_usd = float(os.getenv("FATHOM_MAX_ORDER_USD", "50.0"))
    qdrant_url = os.getenv("FATHOM_QDRANT_URL", "http://localhost:6333")

    # Initialize components
    auth_manager = CredentialManager()
    rest_client = KrakenRESTClient(auth=auth_manager)
    ws_client = KrakenWebSocketClient(
        on_message=async_message_handler,
        on_error=lambda e: print(f"[WS Error] {e}")
    )
    rate_limiter = RateLimiter(tier=tier)
    validator = Validator(max_order_usd=max_order_usd)
    memory = FathomMemory(qdrant_url=qdrant_url)

    print(f"[Fathom] Initialized with tier={tier}, max_order=${max_order_usd}, memory={qdrant_url}")


async def cleanup_server():
    """Cleanup server resources."""
    global rest_client, ws_client

    if rest_client:
        await rest_client.close()

    if ws_client and ws_client.is_connected():
        await ws_client.close()

    try:
        print("[Fathom] Cleanup complete")
    except (ValueError, OSError):
        # stdout may already be closed during shutdown
        pass


# =========================
# Main Entry Point
# =========================

async def main():
    """Run the MCP server."""
    await initialize_server()

    try:
        async with stdio_server() as (read_stream, write_stream):
            await app.run(
                read_stream,
                write_stream,
                app.create_initialization_options()
            )
    finally:
        await cleanup_server()


def run():
    """Entry point for the server."""
    asyncio.run(main())


if __name__ == "__main__":
    run()
