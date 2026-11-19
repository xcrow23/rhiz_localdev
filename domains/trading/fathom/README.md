# Fathom v2.0 - Kraken MCP for Rhiz

**Fathom** is an AI-native Model Context Protocol (MCP) server for trading on Kraken exchange, built as part of the Rhiz human-AI symbiotic development project.

---

## Features

### Phase 1: Foundation (COMPLETE)
- ✅ Secure credential management (HMAC-SHA512)
- ✅ REST API client (public + private endpoints)
- ✅ WebSocket client (real-time market data)
- ✅ Rate limiting (tier-aware)
- ✅ Input validation with safety limits
- ✅ Health monitoring
- ✅ Account balance tools
- ✅ Market data tools (ticker, orderbook, OHLC, trades)

### Upcoming Phases
- Phase 2: Memory integration (Qdrant FastEmbed)
- Phase 3: Order placement with safety rails
- Phase 4: n8n automation hooks
- Phase 5: Notifications (Slack/SMS)
- Phase 6: Backtesting engine

---

## Installation

```bash
cd /mnt/c/Users/dread/Documents/Rhiz/origin/domains/trading/fathom
pip install -e .
```

---

## Configuration

### Environment Variables

```bash
# Required
export FATHOM_KRAKEN_API_KEY="your_api_key"
export FATHOM_KRAKEN_SECRET_KEY="your_secret_key"

# Optional
export FATHOM_KRAKEN_TIER="starter"         # starter, intermediate, or pro
export FATHOM_MAX_ORDER_USD="50.0"          # Safety limit during learning
export FATHOM_QDRANT_URL="http://localhost:6333"
export FATHOM_SLACK_WEBHOOK_URL="https://hooks.slack.com/..."
export FATHOM_N8N_WEBHOOK_BASE="https://your-n8n.hostinger.com/webhook"
export FATHOM_ALERT_PHONE="+1..."
```

Or use existing Rhiz `.env`:
```bash
# Fathom will also read from KRAKEN_API_KEY and KRAKEN_SECRET_KEY
source /mnt/c/Users/dread/Documents/Rhiz/origin/.env
```

---

## Usage

### Running the MCP Server

```bash
fathom
```

The server will listen on stdio for MCP protocol messages.

### Using with Claude Desktop

Add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "fathom": {
      "command": "python",
      "args": ["-m", "fathom.server"],
      "cwd": "/mnt/c/Users/dread/Documents/Rhiz/origin/domains/trading/fathom"
    }
  }
}
```

### Available Tools

| Tool | Description |
|------|-------------|
| `fathom_health_check` | Check Fathom and Kraken API status |
| `fathom_get_rate_limits` | Get current API rate limit usage |
| `fathom_get_balance` | Get account balance for all assets |
| `fathom_get_portfolio_summary` | Get portfolio with USD valuations |
| `fathom_get_trade_balance` | Get detailed trade balance |
| `fathom_get_ticker` | Get ticker data (price, volume, spread) |
| `fathom_get_orderbook` | Get order book (market depth) |
| `fathom_get_ohlc` | Get OHLC candlestick data |
| `fathom_get_recent_trades` | Get recent public trades |
| `fathom_get_websocket_status` | Get WebSocket connection status |

---

## Architecture

```
domains/trading/fathom/
├── ARCHITECTURE_v2.md          # Detailed architecture document
├── README.md                   # This file
├── pyproject.toml              # Package configuration
├── src/
│   ├── server.py               # MCP server entry point
│   ├── auth.py                 # Credential manager
│   ├── rate_limiter.py         # Rate limiting
│   ├── validator.py            # Input validation
│   ├── clients/
│   │   ├── rest.py             # Kraken REST client
│   │   └── websocket.py        # Kraken WebSocket client
│   └── tools/
│       ├── system.py           # Health & monitoring
│       ├── account.py          # Balance & portfolio
│       └── market.py           # Market data
├── config/
│   ├── limits.yaml             # Safety limits
│   ├── pairs.yaml              # Trading pairs
│   └── notifications.yaml      # Notification config
└── tests/                      # Test suite (TBD)
```

---

## Safety Features

- **Order size limits**: Max $50 during learning phase
- **Confirmation required**: Orders > $20 need Captain approval
- **Rate limiting**: Tier-aware API call throttling
- **Input validation**: All parameters validated before API calls
- **Audit logging**: All actions logged (Phase 2+)

---

## Development Philosophy

Fathom follows Rhiz principles:
- **Transparency**: Every function is explicit and documented
- **AI-native**: Designed for tool-use patterns, not human UI
- **Memory-integrated**: Decisions logged to Qdrant (Phase 2+)
- **Lightweight**: Single service, minimal dependencies
- **Secure**: We control auth flow completely

---

## Testing

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run with coverage
pytest --cov=src
```

---

## Contributing

This is a personal research project. No external contributions accepted.

---

## License

MIT

---

## Status

**Phase 1: COMPLETE** ✅
- Foundation implemented and ready for testing

**Next**: Test connectivity and begin Phase 2 (Memory integration)

---

Built with 🐙 by the Rhiz Project
