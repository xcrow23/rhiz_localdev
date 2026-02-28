# Fathom Architecture v2.0 - CD Synthesis + Captain Directives
## Author: Claude Desktop (First Mate - Opus 4.5)
## Date: 2025-12-25
## Status: Ready for CC Implementation

---

## Changelog from v1.0

| Change | Rationale | Source |
|--------|-----------|--------|
| WebSocket support | Real-time data is essential, not optional | Captain directive |
| Qdrant FastEmbed | Lighter than sentence-transformers, already available | Captain directive + CD recommendation |
| Sharpe ratio gating | Needs minimum trade count | CD recommendation, Captain agreed |
| n8n integration hooks | Must-have for automation | Captain directive |
| Backtesting framework | Unlocks high value | Captain directive |
| Notification system | Slack/SMS for alerts | Captain directive |
| Memory as scaffolding | Elegance over completeness | CD architectural philosophy |

---

## Architecture Overview (Revised)

```
┌─────────────────────────────────────────────────────────────────┐
│                         Claude Instance                          │
│                    (Desktop or Code)                             │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ MCP Protocol (stdio/SSE)
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                         FATHOM MCP v2                            │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐  │
│  │   Auth      │  │   Rate      │  │      Tool Router        │  │
│  │   Manager   │  │   Limiter   │  │                         │  │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘  │
│         │                │                     │                 │
│         ▼                ▼                     ▼                 │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │                    Kraken Client                             ││
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐    ││
│  │  │ REST     │  │WebSocket │  │  Orders  │  │  Trades  │    ││
│  │  │ Client   │  │ Client   │  │  Module  │  │  Module  │    ││
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘    ││
│  │       │              │                                      ││
│  │       │    ┌─────────┴─────────┐                           ││
│  │       │    │ Real-Time Feeds   │                           ││
│  │       │    │ • ticker          │                           ││
│  │       │    │ • book (L2)       │                           ││
│  │       │    │ • trade           │                           ││
│  │       │    │ • ohlc            │                           ││
│  │       │    └───────────────────┘                           ││
│  └─────────────────────────────────────────────────────────────┘│
│         │                                          │             │
│         ▼                                          ▼             │
│  ┌─────────────────┐  ┌─────────────────┐  ┌────────────────┐  │
│  │  Memory Logger  │  │  Notification   │  │  Audit Logger  │  │
│  │  (Qdrant/Fast)  │  │  (Slack/SMS)    │  │  (Local File)  │  │
│  └─────────────────┘  └─────────────────┘  └────────────────┘  │
│         │                     │                                  │
│         │                     ▼                                  │
│         │           ┌─────────────────┐                         │
│         │           │  n8n Webhooks   │                         │
│         │           │  (automation)   │                         │
│         │           └─────────────────┘                         │
│         │                                                        │
│         ▼                                                        │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │                    Backtesting Engine                        ││
│  │  • Historical data replay                                    ││
│  │  • Strategy simulation                                       ││
│  │  • Performance metrics                                       ││
│  └─────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
                              │
            ┌─────────────────┼─────────────────┐
            │                 │                 │
            ▼                 ▼                 ▼
      ┌───────────┐    ┌───────────┐    ┌───────────┐
      │  Kraken   │    │  Qdrant   │    │  n8n      │
      │  REST+WS  │    │  FastEmbed│    │  Hostinger│
      └───────────┘    └───────────┘    └───────────┘
```

---

## New Components (v2.0)

### 1. WebSocket Client (MUST-HAVE)

Kraken provides WebSocket API for real-time data:
- **Public**: `wss://ws.kraken.com`
- **Private**: `wss://ws-auth.kraken.com`

```python
# src/websocket/client.py

import asyncio
import json
from typing import Callable, Optional
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
    """
    
    PUBLIC_URL = "wss://ws.kraken.com"
    PRIVATE_URL = "wss://ws-auth.kraken.com"
    
    def __init__(self, on_message: Callable, on_error: Optional[Callable] = None):
        self.on_message = on_message
        self.on_error = on_error or self._default_error_handler
        self._ws = None
        self._subscriptions = set()
        self._running = False
    
    async def connect(self, private: bool = False):
        """Establish WebSocket connection."""
        url = self.PRIVATE_URL if private else self.PUBLIC_URL
        self._ws = await websockets.connect(url)
        self._running = True
        asyncio.create_task(self._listen())
    
    async def subscribe_ticker(self, pairs: list[str]):
        """Subscribe to ticker updates."""
        await self._subscribe("ticker", pairs)
    
    async def subscribe_book(self, pairs: list[str], depth: int = 10):
        """Subscribe to order book updates."""
        await self._subscribe("book", pairs, depth=depth)
    
    async def subscribe_trades(self, pairs: list[str]):
        """Subscribe to trade feed."""
        await self._subscribe("trade", pairs)
    
    async def subscribe_ohlc(self, pairs: list[str], interval: int = 1):
        """Subscribe to OHLC candle updates."""
        await self._subscribe("ohlc", pairs, interval=interval)
    
    async def _subscribe(self, channel: str, pairs: list[str], **kwargs):
        """Send subscription message."""
        msg = {
            "event": "subscribe",
            "pair": pairs,
            "subscription": {"name": channel, **kwargs}
        }
        await self._ws.send(json.dumps(msg))
        self._subscriptions.add((channel, tuple(pairs)))
    
    async def _listen(self):
        """Listen for incoming messages."""
        while self._running:
            try:
                msg = await self._ws.recv()
                data = json.loads(msg)
                await self.on_message(data)
            except websockets.ConnectionClosed:
                await self._reconnect()
            except Exception as e:
                await self.on_error(e)
    
    async def _reconnect(self):
        """Reconnect and restore subscriptions."""
        await asyncio.sleep(5)
        await self.connect()
        for channel, pairs in self._subscriptions:
            await self._subscribe(channel, list(pairs))
    
    async def close(self):
        """Close connection gracefully."""
        self._running = False
        if self._ws:
            await self._ws.close()
    
    def _default_error_handler(self, error):
        print(f"WebSocket error: {error}")
```

**New Tools Enabled**:

```yaml
fathom_stream_ticker:
  description: "Start real-time ticker stream for pairs"
  parameters:
    pairs: ["BTC/USD", "ETH/USD"]
  returns:
    stream_id: string
    status: "streaming"

fathom_get_realtime_book:
  description: "Get current order book from WebSocket cache (faster than REST)"
  parameters:
    pair: string
  returns:
    # Same as REST but from live cache
    
fathom_stream_status:
  description: "Check status of WebSocket streams"
  returns:
    connected: boolean
    subscriptions: array
    latency_ms: number
```

---

### 2. Memory Integration (Qdrant FastEmbed)

**Remove**: `sentence-transformers` dependency (heavy, pulls PyTorch)
**Use**: Qdrant's built-in FastEmbed API

```python
# src/memory/logger.py

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

class FathomMemory:
    """
    Memory integration using Qdrant's FastEmbed.
    
    No external embedding dependencies - Qdrant handles it.
    """
    
    COLLECTION = "fathom_trading"
    
    def __init__(self, qdrant_url: str = "http://localhost:6333"):
        self.client = QdrantClient(
            url=qdrant_url,
            prefer_grpc=False  # REST for simplicity
        )
        self._ensure_collection()
    
    def _ensure_collection(self):
        """Create collection if not exists, using FastEmbed."""
        collections = self.client.get_collections().collections
        if not any(c.name == self.COLLECTION for c in collections):
            self.client.create_collection(
                collection_name=self.COLLECTION,
                vectors_config=VectorParams(
                    size=384,  # all-MiniLM-L6-v2 via FastEmbed
                    distance=Distance.COSINE
                )
            )
    
    def log_trade(self, trade: dict, reasoning: str, hypothesis: str = None):
        """Log trade with semantic embedding."""
        # Combine text for embedding
        text = f"Trade: {trade['side']} {trade['volume']} {trade['pair']}. Reasoning: {reasoning}"
        if hypothesis:
            text += f" Hypothesis: {hypothesis}"
        
        # Qdrant FastEmbed handles embedding automatically
        self.client.add(
            collection_name=self.COLLECTION,
            documents=[text],
            metadata=[{
                "type": "trade",
                "pair": trade["pair"],
                "side": trade["side"],
                "volume": trade["volume"],
                "price": trade.get("price"),
                "timestamp": trade["timestamp"],
                "reasoning": reasoning,
                "hypothesis": hypothesis,
                "outcome": "pending"
            }]
        )
    
    def search(self, query: str, limit: int = 5, filters: dict = None):
        """Semantic search over trading history."""
        return self.client.query(
            collection_name=self.COLLECTION,
            query_text=query,  # FastEmbed handles embedding
            limit=limit,
            query_filter=filters
        )
```

**Dependency change**:
```toml
# REMOVE: sentence-transformers>=2.2.0
# Qdrant client includes FastEmbed support
dependencies = [
    "qdrant-client[fastembed]>=1.7.0",  # Includes FastEmbed
]
```

---

### 3. Sharpe Ratio Gating

Amended to require minimum trade count:

```python
# src/tools/history.py

def calculate_sharpe(trades: list, risk_free_rate: float = 0.0) -> dict:
    """
    Calculate Sharpe ratio with minimum trade requirement.
    
    Returns null if insufficient data (statistical validity).
    """
    MIN_TRADES_FOR_SHARPE = 30  # Statistical minimum
    
    if len(trades) < MIN_TRADES_FOR_SHARPE:
        return {
            "sharpe_ratio": None,
            "reason": f"Insufficient trades ({len(trades)}/{MIN_TRADES_FOR_SHARPE})",
            "trades_needed": MIN_TRADES_FOR_SHARPE - len(trades),
            "suggestion": "Continue trading to accumulate statistical sample"
        }
    
    returns = [t["pnl_pct"] for t in trades]
    mean_return = sum(returns) / len(returns)
    std_return = (sum((r - mean_return)**2 for r in returns) / len(returns)) ** 0.5
    
    if std_return == 0:
        return {
            "sharpe_ratio": None,
            "reason": "Zero variance in returns",
            "suggestion": "Returns are constant - may indicate paper trading or no real activity"
        }
    
    sharpe = (mean_return - risk_free_rate) / std_return
    
    return {
        "sharpe_ratio": round(sharpe, 4),
        "sample_size": len(trades),
        "mean_return_pct": round(mean_return * 100, 4),
        "std_return_pct": round(std_return * 100, 4),
        "statistical_validity": "valid" if len(trades) >= 100 else "preliminary"
    }
```

---

### 4. n8n Integration Hooks (MUST-HAVE)

```python
# src/webhooks/n8n.py

import httpx
from typing import Optional

class N8nIntegration:
    """
    Webhook integration with n8n for automation.
    
    Enables:
    - Scheduled portfolio snapshots
    - Price alert triggers
    - Automated journaling
    - External notifications
    """
    
    def __init__(self, webhook_base_url: str):
        """
        Initialize with n8n webhook base URL.
        
        Example: https://your-n8n.hostinger.com/webhook/
        """
        self.base_url = webhook_base_url.rstrip('/')
        self.client = httpx.AsyncClient(timeout=10.0)
    
    async def trigger_workflow(self, workflow_id: str, payload: dict):
        """Trigger n8n workflow via webhook."""
        url = f"{self.base_url}/{workflow_id}"
        response = await self.client.post(url, json=payload)
        return response.json()
    
    async def send_trade_event(self, trade: dict):
        """Send trade event to n8n for logging/alerting."""
        await self.trigger_workflow("fathom-trade", {
            "event": "trade_executed",
            "trade": trade,
            "timestamp": trade["timestamp"]
        })
    
    async def send_alert(self, alert_type: str, message: str, data: dict = None):
        """Send alert to n8n for notification routing."""
        await self.trigger_workflow("fathom-alert", {
            "event": "alert",
            "type": alert_type,
            "message": message,
            "data": data or {}
        })
    
    async def request_portfolio_snapshot(self):
        """Trigger scheduled portfolio snapshot workflow."""
        await self.trigger_workflow("fathom-snapshot", {
            "event": "snapshot_requested",
            "source": "fathom_mcp"
        })
```

**n8n Workflow Templates** (to create in n8n):

1. **fathom-trade**: Receives trade events → logs to Google Sheets / Notion / etc
2. **fathom-alert**: Receives alerts → routes to Slack / SMS / email
3. **fathom-snapshot**: Scheduled trigger → calls Fathom → logs portfolio state
4. **fathom-daily-summary**: Cron 6PM → aggregates day's activity → sends digest

---

### 5. Notification System (Slack + SMS)

```python
# src/notifications/notifier.py

import httpx
from typing import Optional

class NotificationManager:
    """
    Multi-channel notification system.
    
    Channels:
    - Slack (via webhook)
    - SMS (via n8n or Twilio)
    - Push (future: via n8n to mobile)
    """
    
    def __init__(
        self,
        slack_webhook_url: Optional[str] = None,
        n8n_sms_webhook: Optional[str] = None
    ):
        self.slack_url = slack_webhook_url
        self.sms_webhook = n8n_sms_webhook
        self.client = httpx.AsyncClient(timeout=10.0)
    
    async def notify_slack(self, message: str, channel: str = None, urgency: str = "normal"):
        """Send Slack notification."""
        if not self.slack_url:
            return {"success": False, "reason": "Slack not configured"}
        
        payload = {
            "text": message,
            "username": "Fathom Trading",
            "icon_emoji": ":octopus:" if urgency == "normal" else ":rotating_light:"
        }
        
        await self.client.post(self.slack_url, json=payload)
        return {"success": True, "channel": "slack"}
    
    async def notify_sms(self, message: str, phone: str = None):
        """Send SMS via n8n webhook (routes to Twilio/other)."""
        if not self.sms_webhook:
            return {"success": False, "reason": "SMS not configured"}
        
        await self.client.post(self.sms_webhook, json={
            "message": message,
            "phone": phone,
            "source": "fathom"
        })
        return {"success": True, "channel": "sms"}
    
    async def alert(self, message: str, level: str = "info"):
        """
        Send alert to appropriate channels based on level.
        
        Levels:
        - info: Slack only
        - warning: Slack with highlight
        - critical: Slack + SMS
        """
        results = []
        
        # Always Slack
        results.append(await self.notify_slack(
            message, 
            urgency="critical" if level == "critical" else "normal"
        ))
        
        # SMS for critical only
        if level == "critical":
            results.append(await self.notify_sms(f"🚨 FATHOM: {message}"))
        
        return results
```

**New Tools**:

```yaml
fathom_send_alert:
  description: "Send notification to configured channels"
  parameters:
    message: string
    level: enum["info", "warning", "critical"]
  returns:
    sent_to: array  # ["slack", "sms"]
    success: boolean
```

---

### 6. Backtesting Engine

```python
# src/backtesting/engine.py

import json
from datetime import datetime
from typing import Generator
from dataclasses import dataclass

@dataclass
class BacktestConfig:
    pair: str
    start_date: datetime
    end_date: datetime
    initial_capital: float
    strategy_params: dict

@dataclass  
class BacktestResult:
    total_trades: int
    winning_trades: int
    losing_trades: int
    total_pnl: float
    total_fees: float
    net_pnl: float
    max_drawdown: float
    sharpe_ratio: float | None
    trade_log: list

class BacktestEngine:
    """
    Historical data replay for strategy testing.
    
    Data sources:
    - Local OHLC cache (from prior WebSocket collection)
    - Kraken historical API (rate limited)
    - CSV import for external data
    """
    
    def __init__(self, data_source: str = "local"):
        self.data_source = data_source
        self.trade_log = []
    
    def load_historical_data(self, config: BacktestConfig) -> Generator:
        """Load historical candles for replay."""
        if self.data_source == "local":
            return self._load_local(config)
        elif self.data_source == "kraken":
            return self._load_kraken(config)
        elif self.data_source == "csv":
            return self._load_csv(config)
    
    def run(self, config: BacktestConfig, strategy_fn: callable) -> BacktestResult:
        """
        Run backtest with given strategy function.
        
        strategy_fn receives:
        - current_candle: OHLC data
        - portfolio: Current positions
        - history: Past candles
        
        strategy_fn returns:
        - action: "buy", "sell", "hold"
        - size: Order size (if applicable)
        - reasoning: Why (for logging)
        """
        portfolio = {
            "usd": config.initial_capital,
            "base": 0.0
        }
        history = []
        
        for candle in self.load_historical_data(config):
            action = strategy_fn(candle, portfolio, history)
            
            if action["action"] != "hold":
                self._execute_simulated_trade(action, candle, portfolio)
            
            history.append(candle)
        
        return self._calculate_results(config, portfolio)
    
    def _execute_simulated_trade(self, action, candle, portfolio):
        """Execute trade in simulation."""
        fee_rate = 0.0016  # Kraken maker
        price = candle["close"]
        
        if action["action"] == "buy" and portfolio["usd"] > 0:
            size = min(action.get("size", portfolio["usd"]), portfolio["usd"])
            volume = (size * (1 - fee_rate)) / price
            portfolio["usd"] -= size
            portfolio["base"] += volume
            self.trade_log.append({
                "time": candle["time"],
                "side": "buy",
                "price": price,
                "volume": volume,
                "fee": size * fee_rate,
                "reasoning": action.get("reasoning", "")
            })
        
        elif action["action"] == "sell" and portfolio["base"] > 0:
            volume = min(action.get("size", portfolio["base"]), portfolio["base"])
            proceeds = volume * price * (1 - fee_rate)
            portfolio["base"] -= volume
            portfolio["usd"] += proceeds
            self.trade_log.append({
                "time": candle["time"],
                "side": "sell",
                "price": price,
                "volume": volume,
                "fee": volume * price * fee_rate,
                "reasoning": action.get("reasoning", "")
            })
```

**New Tools**:

```yaml
fathom_backtest:
  description: "Run historical backtest with strategy parameters"
  parameters:
    pair: string
    start_date: string  # ISO date
    end_date: string
    initial_capital: number
    strategy: enum["simple_ma", "mean_reversion", "custom"]
    strategy_params: object
  returns:
    total_trades: integer
    net_pnl: number
    sharpe_ratio: number | null
    max_drawdown: number
    trade_log_id: string  # Memory reference for detailed log

fathom_compare_strategies:
  description: "Run multiple backtests and compare results"
  parameters:
    pair: string
    date_range: object
    strategies: array  # List of strategy configs
  returns:
    comparison_table: array
    best_performer: string
    recommendation: string
```

---

## Updated Dependencies

```toml
[project]
name = "fathom"
version = "2.0.0"
requires-python = ">=3.11"

dependencies = [
    # MCP
    "mcp>=1.0.0",
    
    # HTTP clients
    "httpx>=0.27.0",
    
    # WebSocket
    "websockets>=12.0",
    
    # Vector memory (includes FastEmbed - NO sentence-transformers needed)
    "qdrant-client[fastembed]>=1.7.0",
    
    # Validation & config
    "pydantic>=2.0.0",
    "pyyaml>=6.0",
    "python-dotenv>=1.0.0",
    
    # Async utilities
    "asyncio>=3.4.3",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-asyncio>=0.23.0",
    "black>=24.0.0",
    "ruff>=0.3.0",
]
```

---

## Updated File Structure

```
domains/trading/fathom/
├── ARCHITECTURE.md           # This document (v2.0)
├── README.md                 # User guide
├── src/
│   ├── __init__.py
│   ├── server.py             # MCP server entry point
│   ├── auth.py               # Credential manager (unchanged)
│   ├── rate_limiter.py       # Rate limiting (unchanged)
│   ├── validator.py          # Input validation (unchanged)
│   │
│   ├── clients/
│   │   ├── __init__.py
│   │   ├── rest.py           # Kraken REST client
│   │   └── websocket.py      # Kraken WebSocket client (NEW)
│   │
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── account.py        # Balance, portfolio
│   │   ├── market.py         # Ticker, orderbook, OHLC
│   │   ├── orders.py         # Place, cancel, list
│   │   ├── history.py        # Trades, analysis (updated Sharpe)
│   │   ├── memory.py         # Qdrant FastEmbed integration (updated)
│   │   ├── system.py         # Health, limits
│   │   └── streaming.py      # WebSocket tool interfaces (NEW)
│   │
│   ├── memory/
│   │   ├── __init__.py
│   │   └── logger.py         # FastEmbed-based logging (updated)
│   │
│   ├── notifications/
│   │   ├── __init__.py
│   │   └── notifier.py       # Slack/SMS notifications (NEW)
│   │
│   ├── webhooks/
│   │   ├── __init__.py
│   │   └── n8n.py            # n8n integration (NEW)
│   │
│   ├── backtesting/
│   │   ├── __init__.py
│   │   ├── engine.py         # Backtest runner (NEW)
│   │   └── strategies.py     # Built-in strategy templates (NEW)
│   │
│   └── audit/
│       ├── __init__.py
│       └── logger.py         # Audit trail (unchanged)
│
├── tests/
├── config/
│   ├── limits.yaml
│   ├── pairs.yaml
│   └── notifications.yaml    # Slack/SMS config (NEW)
├── pyproject.toml
└── Dockerfile
```

---

## Implementation Priority (Revised)

### Phase 1: Foundation + WebSocket
1. Auth manager
2. REST client (public endpoints)
3. WebSocket client (ticker + book)
4. Health check tool
5. Get balance tool

### Phase 2: Market Data + Streaming
6. Ticker tool (REST + WS cache)
7. Orderbook tool (REST + WS cache)
8. OHLC tool
9. Stream management tools

### Phase 3: Trading
10. Place order (with safety limits)
11. Cancel order
12. Get open orders
13. Get trades

### Phase 4: Memory (FastEmbed)
14. Qdrant FastEmbed integration
15. Log decision tool
16. Search memory tool
17. Review hypothesis tool

### Phase 5: Notifications + n8n
18. Slack integration
19. n8n webhook triggers
20. Alert routing

### Phase 6: Analysis + Backtesting
21. Portfolio summary
22. Performance analysis (with Sharpe gating)
23. Backtest engine
24. Strategy comparison

---

## Integration Hooks (For Future Sessions)

### Cloudflare Session Checkpoint API
- Fathom can POST trading decisions to edge storage
- Enables memory access from any location
- Endpoint: `POST /api/checkpoint` with `type: "trading_decision"`

### n8n Workflows (Hostinger)
- **fathom-trade**: Trade events → logging/alerting
- **fathom-alert**: Alerts → Slack/SMS routing
- **fathom-snapshot**: Scheduled portfolio captures
- **fathom-daily-summary**: End-of-day digest

### Cross-Collection Memory
- `fathom_trading` collection references `rhiz_memories`
- Semantic search across trading + general project context
- Unified memory architecture

### Notification Flow
```
Fathom Event → Notifier → Slack Webhook (immediate)
                       → n8n Webhook → SMS (if critical)
                       → n8n Webhook → Email digest (daily)
```

---

## Environment Variables (Updated)

```bash
# Kraken
FATHOM_KRAKEN_API_KEY="..."
FATHOM_KRAKEN_SECRET_KEY="..."

# Qdrant
FATHOM_QDRANT_URL="http://localhost:6333"

# Notifications
FATHOM_SLACK_WEBHOOK_URL="https://hooks.slack.com/services/..."
FATHOM_N8N_WEBHOOK_BASE="https://your-n8n.hostinger.com/webhook"

# Notification routing
FATHOM_ALERT_PHONE="+1..."  # For SMS alerts
```

---

## Answers to CC's Original Questions (Updated)

| Question | Answer |
|----------|--------|
| Tool naming | ✅ `fathom_*` prefix — namespaces clearly |
| Safety limits | ✅ $50 max during learning |
| Memory granularity | ✅ Log every decision, not just trades |
| Hypothesis tracking | ⚠️ Optional but encouraged |
| Rate oracle | ❌ Kraken only — avoid complexity |
| Confirmation flow | Captain confirms in chat for > $20 |
| Error responses | ✅ Structured codes + NL context |
| Session context | ✅ Auto-include session_id |
| **WebSocket** | ✅ MUST-HAVE (Captain directive) |
| **n8n integration** | ✅ MUST-HAVE (Captain directive) |
| **Backtesting** | ✅ High value unlock |

---

## Ready for Implementation

This architecture is now complete and ready for CC to execute.

Fair winds, First Mate (Code instance).

🐙🧭

— First Mate (Desktop instance)
