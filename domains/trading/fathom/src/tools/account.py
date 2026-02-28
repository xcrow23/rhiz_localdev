"""
Fathom Account Tools
Account balance and portfolio information.
"""

from typing import Any
from ..clients.rest import KrakenRESTClient


async def fathom_get_balance(client: KrakenRESTClient) -> dict[str, Any]:
    """
    Get account balance.

    Returns:
        {
            "balances": {
                "USD": "1234.56",
                "BTC": "0.12345678",
                ...
            },
            "timestamp": str
        }
    """
    from datetime import datetime

    try:
        balances = await client.get_account_balance()

        return {
            "balances": balances,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "success": True
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }


async def fathom_get_portfolio_summary(client: KrakenRESTClient) -> dict[str, Any]:
    """
    Get portfolio summary with USD valuations.

    Returns:
        {
            "total_usd": float,
            "positions": [
                {
                    "asset": str,
                    "balance": float,
                    "usd_value": float,
                    "percentage": float
                }
            ],
            "timestamp": str
        }
    """
    from datetime import datetime

    try:
        # Get balances
        balances = await client.get_account_balance()

        # Get trade balance summary
        trade_balance = await client.get_trade_balance(asset="USD")

        positions = []
        total_usd = float(trade_balance.get("eb", 0))  # Equivalent balance in USD

        for asset, amount in balances.items():
            balance = float(amount)

            if balance > 0:
                # For USD, value is balance
                if asset in ["USD", "ZUSD"]:
                    usd_value = balance
                else:
                    # For other assets, estimate from trade balance
                    # (proper valuation would require ticker prices)
                    usd_value = 0.0  # Placeholder

                positions.append({
                    "asset": asset,
                    "balance": balance,
                    "usd_value": usd_value
                })

        # Calculate percentages
        for position in positions:
            position["percentage"] = (
                (position["usd_value"] / total_usd * 100)
                if total_usd > 0 else 0
            )

        return {
            "total_usd": total_usd,
            "positions": positions,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "success": True
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }


async def fathom_get_trade_balance(
    client: KrakenRESTClient,
    asset: str = "USD"
) -> dict[str, Any]:
    """
    Get trade balance summary.

    Args:
        asset: Base asset for balance calculation

    Returns:
        {
            "equivalent_balance": float,  # eb: equivalent balance
            "trade_balance": float,       # tb: trade balance
            "margin": float,              # m: margin amount of open positions
            "net": float,                 # n: unrealized net profit/loss
            "cost": float,                # c: cost basis of open positions
            "valuation": float,           # v: current valuation
            "equity": float,              # e: equity
            "free_margin": float,         # mf: free margin
            "timestamp": str
        }
    """
    from datetime import datetime

    try:
        balance = await client.get_trade_balance(asset=asset)

        return {
            "equivalent_balance": float(balance.get("eb", 0)),
            "trade_balance": float(balance.get("tb", 0)),
            "margin": float(balance.get("m", 0)),
            "net": float(balance.get("n", 0)),
            "cost": float(balance.get("c", 0)),
            "valuation": float(balance.get("v", 0)),
            "equity": float(balance.get("e", 0)),
            "free_margin": float(balance.get("mf", 0)),
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "success": True
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
