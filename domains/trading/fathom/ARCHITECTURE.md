# Fathom: Kraken MCP for Rhiz
## Architecture Document v1.0
## Author: Claude Code (First Mate - Opus 4.5)
## Date: 2025-12-25
## Status: Proposed - Awaiting CD Review

---

## Name: Fathom

**Etymology**:
1. A unit of depth (6 feet) used in nautical measurement
2. To understand deeply; to comprehend fully

**Symbolism**:
- The Kraken dwells in the fathoms below
- We seek to fathom the markets - understand them deeply
- Depth of analysis, not surface trading

---

## Philosophy

### Design Principles

1. **Transparency Over Abstraction**
   - Every function is explicit and documented
   - No hidden state or magic behavior
   - Errors are informative, not empty brackets

2. **AI-Native Architecture**
   - Structured outputs designed for LLM consumption
   - Rich context in every response
   - Tool descriptions optimized for function calling

3. **Security by Default**
   - API keys never appear in logs or responses
   - Rate limiting prevents abuse
   - Audit trail for all operations
   - Principle of least privilege

4. **Memory-Integrated**
   - All trades logged to Qdrant
   - Decision reasoning captured
   - Pattern detection over time
   - Semantic search over trading history

5. **Iterative Learning**
   - Hypothesis tracking built-in
   - Outcome correlation
   - Strategy evolution support

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         Claude Instance                          │
│                    (Desktop or Code)                             │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ MCP Protocol (stdio/SSE)
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                         FATHOM MCP                               │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐  │
│  │   Auth      │  │   Rate      │  │      Tool Router        │  │
│  │   Manager   │  │   Limiter   │  │                         │  │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘  │
│         │                │                     │                 │
│         ▼                ▼                     ▼                 │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │                    Kraken Client                             ││
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐    ││
│  │  │ Account  │  │  Market  │  │  Orders  │  │  Trades  │    ││
│  │  │ Module   │  │  Module  │  │  Module  │  │  Module  │    ││
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘    ││
│  └─────────────────────────────────────────────────────────────┘│
│         │                                          │             │
│         ▼                                          ▼             │
│  ┌─────────────────┐                    ┌────────────────────┐  │
│  │  Memory Logger  │                    │   Audit Logger     │  │
│  │  (Qdrant)       │                    │   (Local File)     │  │
│  └─────────────────┘                    └────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ HTTPS (REST API)
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Kraken Exchange                             │
│                   api.kraken.com                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Security Hardening

### 1. Credential Management

```python
class CredentialManager:
    """
    Secure credential handling with defense in depth.
    """

    # Keys loaded from environment only, never from files
    # Keys stored in memory, zeroed on shutdown
    # Keys never serialized or logged

    def __init__(self):
        self._api_key = os.environ.get('FATHOM_KRAKEN_API_KEY')
        self._api_secret = os.environ.get('FATHOM_KRAKEN_SECRET_KEY')

        if not self._api_key or not self._api_secret:
            raise SecurityError("Credentials must be set via environment variables")

    def sign_request(self, endpoint: str, data: dict) -> dict:
        """Sign request without exposing key material."""
        # HMAC-SHA512 signing per Kraken spec
        # Returns headers dict, never the raw secret
        pass

    def __del__(self):
        """Zero out sensitive memory on destruction."""
        self._api_key = '\x00' * len(self._api_key) if self._api_key else None
        self._api_secret = '\x00' * len(self._api_secret) if self._api_secret else None
```

### 2. Rate Limiting

```python
class RateLimiter:
    """
    Respect Kraken's rate limits to prevent lockout.

    Kraken Limits (Starter tier):
    - 15 API calls per second (public)
    - 1 call per second (private, more restrictive)
    - Decay: 0.33 calls/second
    """

    def __init__(self, tier: str = "Intermediate"):
        self.tiers = {
            "Starter": {"max": 15, "decay": 0.33},
            "Intermediate": {"max": 20, "decay": 0.5},
            "Pro": {"max": 20, "decay": 1.0}
        }
        self.config = self.tiers[tier]
        self.counter = 0
        self.last_call = time.time()

    async def acquire(self) -> bool:
        """Wait if necessary to stay within limits."""
        pass
```

### 3. Audit Logging

```python
class AuditLogger:
    """
    Immutable audit trail for compliance and debugging.
    """

    def log_action(self, action: str, params: dict, result: dict):
        """
        Log format (JSON Lines):
        {
            "timestamp": "2025-12-25T04:30:00Z",
            "action": "place_order",
            "params": {"pair": "BTCUSD", "type": "buy", "volume": 0.001},
            "result": {"txid": "...", "status": "success"},
            "session_id": "...",
            "instance": "claude_code"
        }

        CRITICAL: params are sanitized - no API keys ever logged
        """
        pass
```

### 4. Input Validation

```python
class Validator:
    """
    Strict input validation for all tool parameters.
    """

    VALID_PAIRS = ["BTCUSD", "ETHUSD", "XRPUSD", ...]  # Loaded from Kraken
    VALID_ORDER_TYPES = ["market", "limit", "stop-loss", "take-profit"]
    VALID_SIDES = ["buy", "sell"]

    MAX_ORDER_VALUE_USD = 50  # Hard limit for safety during learning

    def validate_order(self, params: dict) -> tuple[bool, str]:
        """Validate order parameters before submission."""
        pass
```

---

## Tool Definitions

### Category 1: Account & Portfolio

#### `fathom_get_balance`

```yaml
name: fathom_get_balance
description: |
  Retrieve current account balances across all assets.
  Returns available and total balances with USD valuations.
  This is a prerequisite for any trading decision.

parameters: {}

returns:
  type: object
  properties:
    balances:
      type: array
      items:
        asset: string
        available: number
        total: number
        usd_value: number
    total_usd_value: number
    timestamp: string

example_response:
  balances:
    - asset: "USD"
      available: 147.23
      total: 147.23
      usd_value: 147.23
    - asset: "BTC"
      available: 0.00042
      total: 0.00042
      usd_value: 18.50
  total_usd_value: 165.73
  timestamp: "2025-12-25T04:30:00Z"
```

#### `fathom_get_portfolio_summary`

```yaml
name: fathom_get_portfolio_summary
description: |
  High-level portfolio analysis with risk metrics.
  Designed for AI decision-making context.

parameters: {}

returns:
  type: object
  properties:
    total_value_usd: number
    allocation:
      type: object
      additionalProperties: number  # asset: percentage
    risk_metrics:
      cash_percentage: number
      largest_position: string
      largest_position_percentage: number
      concentration_index: number  # Herfindahl-like
    context:
      type: string
      description: "Natural language summary for AI consumption"
```

### Category 2: Market Data

#### `fathom_get_ticker`

```yaml
name: fathom_get_ticker
description: |
  Get current price and 24h stats for a trading pair.

parameters:
  pair:
    type: string
    description: "Trading pair (e.g., BTCUSD, ETHUSD)"
    required: true

returns:
  type: object
  properties:
    pair: string
    price: number
    bid: number
    ask: number
    spread_bps: number
    volume_24h: number
    high_24h: number
    low_24h: number
    change_24h_pct: number
    timestamp: string
```

#### `fathom_get_orderbook`

```yaml
name: fathom_get_orderbook
description: |
  Get current order book depth for a trading pair.
  Essential for understanding liquidity and spread.

parameters:
  pair:
    type: string
    required: true
  depth:
    type: integer
    default: 10
    description: "Number of levels on each side"

returns:
  type: object
  properties:
    pair: string
    bids: array  # [{price, volume, total}]
    asks: array
    spread: number
    spread_bps: number
    mid_price: number
    liquidity_summary:
      bid_depth_usd: number
      ask_depth_usd: number
      imbalance: number  # positive = more bids
```

#### `fathom_get_ohlc`

```yaml
name: fathom_get_ohlc
description: |
  Get historical OHLC (candlestick) data for analysis.

parameters:
  pair:
    type: string
    required: true
  interval:
    type: integer
    enum: [1, 5, 15, 30, 60, 240, 1440, 10080, 21600]
    description: "Interval in minutes"
    default: 60
  count:
    type: integer
    default: 100
    max: 720

returns:
  type: object
  properties:
    pair: string
    interval: integer
    candles: array  # [{time, open, high, low, close, volume}]
    analysis:
      trend: string  # "bullish", "bearish", "sideways"
      volatility: number
      support_levels: array
      resistance_levels: array
```

### Category 3: Order Management

#### `fathom_place_order`

```yaml
name: fathom_place_order
description: |
  Place a new order on Kraken.

  SAFETY FEATURES:
  - Maximum order value enforced ($50 during learning phase)
  - Requires explicit confirmation for orders > $20
  - All orders logged to memory with reasoning

parameters:
  pair:
    type: string
    required: true
  side:
    type: string
    enum: ["buy", "sell"]
    required: true
  order_type:
    type: string
    enum: ["market", "limit"]
    required: true
  volume:
    type: number
    required: true
    description: "Amount in base currency"
  price:
    type: number
    required: false
    description: "Required for limit orders"
  reasoning:
    type: string
    required: true
    description: "Why are we placing this order? Logged for learning."
  hypothesis:
    type: string
    required: false
    description: "What do we expect to happen? For outcome tracking."

returns:
  type: object
  properties:
    success: boolean
    order_id: string
    status: string
    executed_price: number
    executed_volume: number
    fees: number
    reasoning_logged: boolean
    memory_id: string  # Qdrant point ID for retrieval
```

#### `fathom_cancel_order`

```yaml
name: fathom_cancel_order
description: |
  Cancel an open order.

parameters:
  order_id:
    type: string
    required: true
  reasoning:
    type: string
    required: true
    description: "Why are we cancelling?"

returns:
  type: object
  properties:
    success: boolean
    order_id: string
    status: string
```

#### `fathom_get_open_orders`

```yaml
name: fathom_get_open_orders
description: |
  Get all open orders.

parameters: {}

returns:
  type: object
  properties:
    orders: array
    count: integer
```

### Category 4: Trade History & Analysis

#### `fathom_get_trades`

```yaml
name: fathom_get_trades
description: |
  Get recent trade history.

parameters:
  pair:
    type: string
    required: false
  start:
    type: string
    description: "ISO datetime"
  end:
    type: string

returns:
  type: object
  properties:
    trades: array
    total_volume: number
    total_fees: number
    net_pnl: number
```

#### `fathom_analyze_performance`

```yaml
name: fathom_analyze_performance
description: |
  Analyze trading performance over a period.
  Designed for iterative learning feedback.

parameters:
  period:
    type: string
    enum: ["day", "week", "month", "all"]
    default: "week"

returns:
  type: object
  properties:
    period: string
    metrics:
      total_trades: integer
      winning_trades: integer
      losing_trades: integer
      win_rate: number
      total_pnl: number
      total_fees: number
      net_pnl: number
      average_trade_size: number
      largest_win: number
      largest_loss: number
      sharpe_ratio: number
    insights:
      type: array
      items: string
      description: "AI-generated observations for learning"
    hypotheses_reviewed:
      type: array
      description: "Past hypotheses with outcomes"
```

### Category 5: Memory & Learning

#### `fathom_log_decision`

```yaml
name: fathom_log_decision
description: |
  Log a trading decision to persistent memory.
  Not an order - just recording reasoning for future reference.

parameters:
  decision_type:
    type: string
    enum: ["trade", "hold", "exit", "adjust"]
  reasoning:
    type: string
    required: true
  market_context:
    type: object
    description: "Snapshot of relevant market state"
  hypothesis:
    type: string
  confidence:
    type: number
    min: 0
    max: 1

returns:
  type: object
  properties:
    memory_id: string
    logged_at: string
```

#### `fathom_search_memory`

```yaml
name: fathom_search_memory
description: |
  Semantic search over trading history and decisions.

parameters:
  query:
    type: string
    required: true
    description: "Natural language query"
  limit:
    type: integer
    default: 5
  filters:
    type: object
    properties:
      type: string  # "trade", "decision", "hypothesis"
      outcome: string  # "win", "loss", "pending"
      date_range: object

returns:
  type: object
  properties:
    results: array
    query: string
```

#### `fathom_review_hypothesis`

```yaml
name: fathom_review_hypothesis
description: |
  Review a past hypothesis against actual outcome.
  Core tool for iterative learning.

parameters:
  hypothesis_id:
    type: string
    required: true
  actual_outcome:
    type: string
    required: true
  learnings:
    type: string
    required: true

returns:
  type: object
  properties:
    hypothesis: string
    prediction: string
    actual: string
    correct: boolean
    learnings_logged: boolean
```

### Category 6: System & Safety

#### `fathom_health_check`

```yaml
name: fathom_health_check
description: |
  Verify Fathom and Kraken connectivity.

parameters: {}

returns:
  type: object
  properties:
    fathom_status: string
    kraken_status: string
    kraken_server_time: string
    rate_limit_remaining: integer
    memory_status: string
    last_trade: string
```

#### `fathom_get_limits`

```yaml
name: fathom_get_limits
description: |
  Get current safety limits and usage.

parameters: {}

returns:
  type: object
  properties:
    max_order_value_usd: number
    max_daily_volume_usd: number
    daily_volume_used: number
    rate_limit_tier: string
    api_calls_remaining: integer
```

#### `fathom_set_limits`

```yaml
name: fathom_set_limits
description: |
  Adjust safety limits (requires confirmation).

parameters:
  max_order_value_usd:
    type: number
  max_daily_volume_usd:
    type: number
  require_confirmation_above:
    type: number

returns:
  type: object
  properties:
    success: boolean
    new_limits: object
    requires_captain_approval: boolean
```

---

## Memory Integration

### Qdrant Collection Schema

```python
FATHOM_COLLECTION = {
    "name": "fathom_trading",
    "vectors": {
        "size": 384,  # all-MiniLM-L6-v2
        "distance": "Cosine"
    },
    "payload_schema": {
        "type": {
            "type": "keyword",
            "enum": ["trade", "decision", "hypothesis", "market_snapshot"]
        },
        "timestamp": {"type": "datetime"},
        "pair": {"type": "keyword"},
        "side": {"type": "keyword"},
        "outcome": {"type": "keyword"},
        "pnl": {"type": "float"},
        "reasoning": {"type": "text"},
        "hypothesis": {"type": "text"},
        "learnings": {"type": "text"},
        "session_id": {"type": "keyword"}
    }
}
```

### What Gets Logged

1. **Every trade** with:
   - Reasoning at time of order
   - Market context snapshot
   - Hypothesis if provided
   - Outcome after close

2. **Every decision** (including decisions NOT to trade):
   - Why we held
   - What we were watching
   - Confidence level

3. **Hypotheses** with:
   - Prediction made
   - Timeframe
   - Outcome when reviewed
   - Learnings extracted

4. **Market snapshots** at:
   - Trade execution
   - Significant price moves
   - Session start/end

---

## File Structure

```
domains/trading/fathom/
├── ARCHITECTURE.md          # This document
├── README.md                # User guide
├── src/
│   ├── __init__.py
│   ├── server.py            # MCP server entry point
│   ├── auth.py              # Credential manager
│   ├── client.py            # Kraken API client
│   ├── rate_limiter.py      # Rate limiting
│   ├── validator.py         # Input validation
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── account.py       # Balance, portfolio tools
│   │   ├── market.py        # Ticker, orderbook, OHLC
│   │   ├── orders.py        # Place, cancel, list orders
│   │   ├── history.py       # Trades, analysis
│   │   ├── memory.py        # Qdrant integration
│   │   └── system.py        # Health, limits
│   ├── memory/
│   │   ├── __init__.py
│   │   ├── logger.py        # Memory logging
│   │   └── search.py        # Semantic search
│   └── audit/
│       ├── __init__.py
│       └── logger.py        # Audit trail
├── tests/
│   ├── test_auth.py
│   ├── test_client.py
│   ├── test_tools.py
│   └── test_memory.py
├── config/
│   ├── limits.yaml          # Safety limits
│   └── pairs.yaml           # Supported trading pairs
├── pyproject.toml           # Dependencies
└── Dockerfile               # Container deployment
```

---

## Dependencies

```toml
[project]
name = "fathom"
version = "0.1.0"
requires-python = ">=3.11"

dependencies = [
    "mcp>=1.0.0",               # MCP protocol
    "httpx>=0.27.0",            # Async HTTP client
    "qdrant-client>=1.7.0",     # Vector memory
    "sentence-transformers>=2.2.0",  # Embeddings
    "pydantic>=2.0.0",          # Validation
    "pyyaml>=6.0",              # Config
    "python-dotenv>=1.0.0",     # Env management
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

## Deployment

### Option 1: Local Python

```bash
# Install
cd domains/trading/fathom
pip install -e .

# Configure
export FATHOM_KRAKEN_API_KEY="..."
export FATHOM_KRAKEN_SECRET_KEY="..."
export FATHOM_QDRANT_URL="http://localhost:6333"

# Run
python -m fathom.server
```

### Option 2: Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY . .
RUN pip install -e .

# Credentials via environment
ENV FATHOM_KRAKEN_API_KEY=""
ENV FATHOM_KRAKEN_SECRET_KEY=""
ENV FATHOM_QDRANT_URL="http://host.docker.internal:6333"

CMD ["python", "-m", "fathom.server"]
```

### Option 3: Claude Desktop Integration

```json
// claude_desktop_config.json
{
  "mcpServers": {
    "fathom": {
      "command": "python",
      "args": ["-m", "fathom.server"],
      "cwd": "/path/to/domains/trading/fathom",
      "env": {
        "FATHOM_KRAKEN_API_KEY": "${KRAKEN_API_KEY}",
        "FATHOM_KRAKEN_SECRET_KEY": "${KRAKEN_SECRET_KEY}",
        "FATHOM_QDRANT_URL": "http://localhost:6333"
      }
    }
  }
}
```

---

## Implementation Priority

### Phase 1: Foundation (Execute First)
1. Auth manager with secure signing
2. Basic Kraken client (public endpoints)
3. Health check tool
4. Get balance tool

### Phase 2: Market Data
5. Ticker tool
6. Orderbook tool
7. OHLC tool

### Phase 3: Trading
8. Place order (with safety limits)
9. Cancel order
10. Get open orders
11. Get trades

### Phase 4: Memory & Learning
12. Qdrant integration
13. Log decision tool
14. Search memory tool
15. Review hypothesis tool

### Phase 5: Analysis
16. Portfolio summary
17. Performance analysis
18. Insights generation

---

## Questions for CD Review

1. **Tool naming**: `fathom_*` prefix, or just descriptive names?

2. **Safety limits**: $50 max order during learning - appropriate?

3. **Memory granularity**: Log every decision, or only trades?

4. **Hypothesis tracking**: Required field on orders, or optional?

5. **Rate oracle**: Build our own price aggregation, or use Kraken only?

6. **Confirmation flow**: How should order confirmation work for larger trades?

7. **Error responses**: Structured codes, or natural language for AI consumption?

8. **Session context**: Should tools automatically include session_id for memory?

---

## Success Metrics

### Week 1
- [ ] All tools implemented and tested
- [ ] Successfully read balance from Kraken
- [ ] Place and cancel a micro order ($1)
- [ ] Log decision to Qdrant

### Month 1
- [ ] 10+ trades executed and logged
- [ ] Performance analysis functional
- [ ] 3+ hypotheses tracked with outcomes
- [ ] Semantic search returning relevant history

### Quarter 1
- [ ] Pattern detection identifying recurring setups
- [ ] Strategy evolution based on logged learnings
- [ ] Positive net PnL (even if small)

---

## Conclusion

Fathom is designed to be the trading arm of the Rhiz organism - transparent, secure, memory-integrated, and optimized for AI-driven decision-making with human oversight.

By building our own MCP instead of fighting Hummingbot's abstractions, we gain:
- Full understanding of every component
- Direct control over security and logging
- Memory integration that serves both partners
- A foundation for iterative learning

Ready for CD review. Awaiting architectural feedback before execution.

---

**Document Author**: First Mate (Claude Code - Opus 4.5)
**Review Requested From**: First Mate (Claude Desktop - Opus 4.5)
**Execution Location**: Claude Code
**Captain Oversight**: Required for safety limit adjustments and first live trades
