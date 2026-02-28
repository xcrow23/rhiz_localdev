"""
Fathom REST Client
HTTP client for Kraken REST API.
"""

import httpx
from typing import Any, Optional
from ..auth import CredentialManager


class KrakenRESTClient:
    """
    REST API client for Kraken exchange.

    API Documentation: https://docs.kraken.com/rest/

    Endpoints:
    - Public: No authentication required (market data)
    - Private: Requires API-Key and API-Sign headers
    """

    BASE_URL = "https://api.kraken.com"
    API_VERSION = "0"

    def __init__(self, auth: Optional[CredentialManager] = None, timeout: float = 30.0):
        """
        Initialize REST client.

        Args:
            auth: CredentialManager instance (required for private endpoints)
            timeout: Request timeout in seconds
        """
        self.auth = auth
        self.client = httpx.AsyncClient(
            base_url=self.BASE_URL,
            timeout=timeout,
            headers={"User-Agent": "Fathom/2.0 (Rhiz MCP)"}
        )

    async def close(self):
        """Close HTTP client."""
        await self.client.aclose()

    async def _request(
        self,
        method: str,
        endpoint: str,
        data: Optional[dict] = None,
        authenticated: bool = False
    ) -> dict:
        """
        Make HTTP request to Kraken API.

        Args:
            method: HTTP method (GET or POST)
            endpoint: API endpoint (e.g., "public/Time")
            data: Request data (for POST)
            authenticated: Whether to include auth headers

        Returns:
            API response dict

        Raises:
            httpx.HTTPError: On network/HTTP errors
            ValueError: On API error responses
        """
        url_path = f"/{self.API_VERSION}/{endpoint}"
        headers = {}

        if authenticated:
            if not self.auth:
                raise ValueError("Authentication required but no credentials provided")
            headers = self.auth.get_headers(url_path, data or {})

        response = await self.client.request(
            method,
            url_path,
            data=data,
            headers=headers
        )

        response.raise_for_status()
        result = response.json()

        # Kraken API returns {"error": [...], "result": {...}}
        if result.get("error"):
            raise ValueError(f"Kraken API error: {result['error']}")

        return result.get("result", {})

    # =========================
    # Public Endpoints
    # =========================

    async def get_server_time(self) -> dict:
        """
        Get server time (public endpoint for connectivity testing).

        Returns:
            {"unixtime": int, "rfc1123": str}
        """
        return await self._request("GET", "public/Time")

    async def get_system_status(self) -> dict:
        """
        Get system status.

        Returns:
            {"status": str, "timestamp": str}
        """
        return await self._request("GET", "public/SystemStatus")

    async def get_asset_info(self, assets: Optional[list[str]] = None) -> dict:
        """
        Get asset information.

        Args:
            assets: List of assets to query (e.g., ["BTC", "USD"])

        Returns:
            Dict mapping asset names to info
        """
        data = {"asset": ",".join(assets)} if assets else {}
        return await self._request("POST", "public/Assets", data=data)

    async def get_tradable_pairs(self, pairs: Optional[list[str]] = None) -> dict:
        """
        Get tradable asset pairs.

        Args:
            pairs: List of pairs to query (e.g., ["XBTUSD", "ETHUSD"])

        Returns:
            Dict mapping pair names to info
        """
        data = {"pair": ",".join(pairs)} if pairs else {}
        return await self._request("POST", "public/AssetPairs", data=data)

    async def get_ticker(self, pairs: list[str]) -> dict:
        """
        Get ticker information for pairs.

        Args:
            pairs: List of pairs (e.g., ["XBTUSD"])

        Returns:
            Dict mapping pairs to ticker data (ask, bid, last, volume, etc.)
        """
        return await self._request("POST", "public/Ticker", data={"pair": ",".join(pairs)})

    async def get_ohlc(
        self,
        pair: str,
        interval: int = 1,
        since: Optional[int] = None
    ) -> dict:
        """
        Get OHLC (candlestick) data.

        Args:
            pair: Trading pair (e.g., "XBTUSD")
            interval: Time interval in minutes (1, 5, 15, 30, 60, 240, 1440, 10080, 21600)
            since: Return data since this timestamp

        Returns:
            {"pair": [[time, open, high, low, close, vwap, volume, count], ...], "last": int}
        """
        data = {"pair": pair, "interval": interval}
        if since:
            data["since"] = since
        return await self._request("POST", "public/OHLC", data=data)

    async def get_orderbook(self, pair: str, count: int = 100) -> dict:
        """
        Get order book (market depth).

        Args:
            pair: Trading pair
            count: Maximum number of asks/bids to return

        Returns:
            {"asks": [[price, volume, timestamp], ...], "bids": [...]}
        """
        return await self._request("POST", "public/Depth", data={"pair": pair, "count": count})

    async def get_recent_trades(self, pair: str, since: Optional[int] = None) -> dict:
        """
        Get recent trades.

        Args:
            pair: Trading pair
            since: Return trades since this timestamp

        Returns:
            {"trades": [[price, volume, time, buy/sell, market/limit, misc], ...], "last": str}
        """
        data = {"pair": pair}
        if since:
            data["since"] = since
        return await self._request("POST", "public/Trades", data=data)

    # =========================
    # Private Endpoints
    # =========================

    async def get_account_balance(self) -> dict:
        """
        Get account balance (private endpoint).

        Returns:
            Dict mapping asset names to balance amounts
        """
        return await self._request("POST", "private/Balance", data={}, authenticated=True)

    async def get_trade_balance(self, asset: str = "USD") -> dict:
        """
        Get trade balance summary.

        Args:
            asset: Base asset for balance calculation

        Returns:
            {"eb": str, "tb": str, "m": str, "n": str, "c": str, "v": str, "e": str, "mf": str}
        """
        return await self._request(
            "POST",
            "private/TradeBalance",
            data={"asset": asset},
            authenticated=True
        )

    async def get_open_orders(self, trades: bool = False) -> dict:
        """
        Get open orders.

        Args:
            trades: Whether to include trades info

        Returns:
            {"open": {order_id: order_info, ...}}
        """
        return await self._request(
            "POST",
            "private/OpenOrders",
            data={"trades": trades},
            authenticated=True
        )

    async def get_closed_orders(
        self,
        trades: bool = False,
        start: Optional[int] = None,
        end: Optional[int] = None
    ) -> dict:
        """
        Get closed orders.

        Args:
            trades: Whether to include trades
            start: Starting timestamp
            end: Ending timestamp

        Returns:
            {"closed": {order_id: order_info, ...}, "count": int}
        """
        data = {"trades": trades}
        if start:
            data["start"] = start
        if end:
            data["end"] = end
        return await self._request("POST", "private/ClosedOrders", data=data, authenticated=True)

    async def add_order(
        self,
        pair: str,
        side: str,
        order_type: str,
        volume: float,
        price: Optional[float] = None,
        validate: bool = False
    ) -> dict:
        """
        Place new order.

        Args:
            pair: Trading pair
            side: "buy" or "sell"
            order_type: "market" or "limit"
            volume: Order volume
            price: Limit price (required for limit orders)
            validate: If True, only validates without placing

        Returns:
            {"descr": {"order": str}, "txid": [str]}
        """
        data = {
            "pair": pair,
            "type": side,
            "ordertype": order_type,
            "volume": str(volume),
            "validate": validate
        }

        if price is not None:
            data["price"] = str(price)

        return await self._request("POST", "private/AddOrder", data=data, authenticated=True)

    async def cancel_order(self, txid: str) -> dict:
        """
        Cancel open order.

        Args:
            txid: Transaction ID

        Returns:
            {"count": int, "pending": bool}
        """
        return await self._request(
            "POST",
            "private/CancelOrder",
            data={"txid": txid},
            authenticated=True
        )

    async def get_trades_history(
        self,
        trade_type: str = "all",
        start: Optional[int] = None,
        end: Optional[int] = None
    ) -> dict:
        """
        Get trades history.

        Args:
            trade_type: "all", "any position", "closed position", "closing position", "no position"
            start: Starting timestamp
            end: Ending timestamp

        Returns:
            {"trades": {trade_id: trade_info, ...}, "count": int}
        """
        data = {"type": trade_type}
        if start:
            data["start"] = start
        if end:
            data["end"] = end
        return await self._request("POST", "private/TradesHistory", data=data, authenticated=True)
