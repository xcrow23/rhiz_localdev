"""
Fathom WebSocket Client
Real-time market data via Kraken WebSocket API.
"""

import asyncio
import json
from typing import Callable, Optional, Set, Tuple
import websockets


class KrakenWebSocketClient:
    """
    Real-time market data via Kraken WebSocket.

    Public Channels:
    - ticker: Price updates
    - book: Order book (L2, configurable depth)
    - trade: Trade executions
    - ohlc: Candlestick updates

    Private Channels (authenticated):
    - ownTrades: Your trade executions
    - openOrders: Your order updates

    Documentation: https://docs.kraken.com/websockets/
    """

    PUBLIC_URL = "wss://ws.kraken.com"
    PRIVATE_URL = "wss://ws-auth.kraken.com"

    def __init__(
        self,
        on_message: Callable,
        on_error: Optional[Callable] = None,
        on_connect: Optional[Callable] = None
    ):
        """
        Initialize WebSocket client.

        Args:
            on_message: Callback for incoming messages (async callable)
            on_error: Callback for errors (async callable)
            on_connect: Callback on successful connection (async callable)
        """
        self.on_message = on_message
        self.on_error = on_error or self._default_error_handler
        self.on_connect = on_connect or self._default_connect_handler

        self._ws: Optional[websockets.WebSocketClientProtocol] = None
        self._subscriptions: Set[Tuple[str, Tuple[str, ...]]] = set()
        self._running = False
        self._listen_task: Optional[asyncio.Task] = None
        self._reconnect_delay = 5
        self._max_reconnect_delay = 60

    async def connect(self, private: bool = False):
        """
        Establish WebSocket connection.

        Args:
            private: Connect to private (authenticated) endpoint
        """
        url = self.PRIVATE_URL if private else self.PUBLIC_URL

        try:
            self._ws = await websockets.connect(url)
            self._running = True
            await self.on_connect(private)

            # Start listening task
            self._listen_task = asyncio.create_task(self._listen())

        except Exception as e:
            await self.on_error(f"Connection failed: {e}")
            raise

    async def subscribe_ticker(self, pairs: list[str]):
        """
        Subscribe to ticker updates.

        Args:
            pairs: List of pairs (e.g., ["BTC/USD", "ETH/USD"])
        """
        await self._subscribe("ticker", pairs)

    async def subscribe_book(self, pairs: list[str], depth: int = 10):
        """
        Subscribe to order book updates.

        Args:
            pairs: List of pairs
            depth: Book depth (10, 25, 100, 500, 1000)
        """
        await self._subscribe("book", pairs, depth=depth)

    async def subscribe_trades(self, pairs: list[str]):
        """
        Subscribe to trade feed.

        Args:
            pairs: List of pairs
        """
        await self._subscribe("trade", pairs)

    async def subscribe_ohlc(self, pairs: list[str], interval: int = 1):
        """
        Subscribe to OHLC candle updates.

        Args:
            pairs: List of pairs
            interval: Interval in minutes (1, 5, 15, 30, 60, 240, 1440, 10080, 21600)
        """
        await self._subscribe("ohlc", pairs, interval=interval)

    async def subscribe_spread(self, pairs: list[str]):
        """
        Subscribe to spread updates (best bid/ask).

        Args:
            pairs: List of pairs
        """
        await self._subscribe("spread", pairs)

    async def unsubscribe(self, channel: str, pairs: list[str]):
        """
        Unsubscribe from channel.

        Args:
            channel: Channel name
            pairs: List of pairs
        """
        msg = {
            "event": "unsubscribe",
            "pair": pairs,
            "subscription": {"name": channel}
        }

        if self._ws:
            await self._ws.send(json.dumps(msg))
            self._subscriptions.discard((channel, tuple(pairs)))

    async def _subscribe(self, channel: str, pairs: list[str], **kwargs):
        """
        Send subscription message.

        Args:
            channel: Channel name (ticker, book, trade, ohlc, spread)
            pairs: List of pairs
            **kwargs: Additional subscription parameters (depth, interval, etc.)
        """
        msg = {
            "event": "subscribe",
            "pair": pairs,
            "subscription": {"name": channel, **kwargs}
        }

        if self._ws:
            await self._ws.send(json.dumps(msg))
            self._subscriptions.add((channel, tuple(pairs)))
        else:
            raise RuntimeError("WebSocket not connected")

    async def _listen(self):
        """
        Listen for incoming messages.

        Runs in background task, handles reconnection on disconnect.
        """
        while self._running:
            try:
                if not self._ws:
                    break

                msg = await self._ws.recv()
                data = json.loads(msg)

                # Filter out system messages
                if isinstance(data, dict):
                    event_type = data.get("event")
                    if event_type == "heartbeat":
                        continue  # Ignore heartbeats
                    elif event_type == "systemStatus":
                        continue  # Ignore system status
                    elif event_type == "subscriptionStatus":
                        # Log subscription confirmations
                        status = data.get("status")
                        if status == "error":
                            await self.on_error(f"Subscription error: {data}")
                        continue

                # Pass data to handler
                await self.on_message(data)

            except websockets.ConnectionClosed:
                if self._running:
                    await self._handle_disconnect()
                break

            except json.JSONDecodeError as e:
                await self.on_error(f"JSON decode error: {e}")

            except Exception as e:
                await self.on_error(f"Listen error: {e}")

    async def _handle_disconnect(self):
        """Handle unexpected disconnection with exponential backoff."""
        await self.on_error(f"Connection lost, reconnecting in {self._reconnect_delay}s...")

        await asyncio.sleep(self._reconnect_delay)

        # Exponential backoff
        self._reconnect_delay = min(self._reconnect_delay * 2, self._max_reconnect_delay)

        try:
            await self.connect()
            await self._restore_subscriptions()
            # Reset delay on successful reconnect
            self._reconnect_delay = 5

        except Exception as e:
            await self.on_error(f"Reconnection failed: {e}")

    async def _restore_subscriptions(self):
        """Restore subscriptions after reconnection."""
        for channel, pairs in self._subscriptions.copy():
            try:
                await self._subscribe(channel, list(pairs))
            except Exception as e:
                await self.on_error(f"Failed to restore subscription {channel}/{pairs}: {e}")

    async def close(self):
        """Close connection gracefully."""
        self._running = False

        if self._listen_task:
            self._listen_task.cancel()
            try:
                await self._listen_task
            except asyncio.CancelledError:
                pass

        if self._ws:
            await self._ws.close()
            self._ws = None

    def is_connected(self) -> bool:
        """Check if WebSocket is connected."""
        return self._ws is not None and self._ws.open

    def get_subscriptions(self) -> list[dict]:
        """
        Get active subscriptions.

        Returns:
            List of subscription dicts with channel and pairs
        """
        return [
            {"channel": channel, "pairs": list(pairs)}
            for channel, pairs in self._subscriptions
        ]

    async def _default_error_handler(self, error):
        """Default error handler (prints to console)."""
        print(f"[WebSocket Error] {error}")

    async def _default_connect_handler(self, private: bool):
        """Default connection handler."""
        endpoint = "private" if private else "public"
        print(f"[WebSocket] Connected to {endpoint} endpoint")
