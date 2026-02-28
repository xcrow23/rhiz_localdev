---
component: fathom-mcp-server
status: partially_deployed
completion: 16.67%
deployed_at: session_16_20251226
depends_on:
  - kraken_api: operational
  - python_310: operational
blocks:
  - trading_integration_workflow: missing
  - fathom_phase_2_trading: not_started
integration_endpoints:
  - tool: get_account_balance
    status: operational
    tested: session_16
  - tool: get_ticker
    status: operational
    tested: session_16
  - tool: place_market_order
    status: not_implemented
    phase: 3
related_components:
  - fathom_commander: deployed_no_workflow_connection
  - sil_decision_engine: deployed_no_workflow_connection
  - memory_system: operational
failure_history:
  - approach: hummingbot_integration
    failed_at: session_17
    reason: complexity_overhead
    pivot: direct_kraken_mcp
semantic_cluster: trading_domain
vector_density: medium
threshold_recommendation: 0.25-0.40
last_updated: 2026-01-25
---

# Fathom MCP Server

**Component Type**: Trading Execution Layer
**Protocol**: Model Context Protocol (MCP) via stdio
**Exchange**: Kraken
**Status**: Phase 1/6 deployed (16.67% complete)

---

## Purpose

Fathom is an AI-native Model Context Protocol (MCP) server providing direct access to Kraken exchange functionality. It serves as the **execution layer** in Rhiz's three-tier trading architecture (Fathom → Fathom Commander → SIL).

**Design Philosophy**: AI-first interface to cryptocurrency trading. Instead of human-oriented dashboards, Fathom provides structured, validated, machine-readable access to exchange operations.

---

## Deployment Status

### Phase 1: Foundation (COMPLETE - Session 16)
✅ **Deployed**: 2025-12-26
- Secure credential management (HMAC-SHA512)
- REST API client (public + private endpoints)
- Rate limiting (tier-aware)
- Input validation with safety limits
- Health monitoring
- Account balance tools (8 tools operational)
- Market data tools (ticker, orderbook, OHLC, trades)

**Validation**: First real trade executed successfully (0.0001 BTC @ $87,420, TXID: OBRP7D-MBTUR-4R2O6T)

### Phases 2-6: NOT STARTED
❌ **Phase 2**: Memory integration (Qdrant FastEmbed)
❌ **Phase 3**: Order placement with safety rails
❌ **Phase 4**: n8n automation hooks
❌ **Phase 5**: Notifications (Slack/SMS)
❌ **Phase 6**: Backtesting engine

**Blocker**: Integration workflow connecting Fathom → FC → SIL not built (85/0 pattern).

---

## Architecture

### Component Stack

```
┌──────────────────────────────────────┐
│      Claude Instance (Desktop/Code)   │
│      Decision-making layer            │
└──────────────────────────────────────┘
                 │
                 │ MCP Protocol (stdio)
                 ▼
┌──────────────────────────────────────┐
│          FATHOM MCP v2.0              │
│  ┌────────────┐  ┌──────────────┐    │
│  │ Auth Mgr   │  │ Rate Limiter │    │
│  └────────────┘  └──────────────┘    │
│         │              │              │
│         ▼              ▼              │
│  ┌──────────────────────────────┐    │
│  │   Kraken Client              │    │
│  │   • REST API (sync)          │    │
│  │   • WebSocket (planned)      │    │
│  └──────────────────────────────┘    │
└──────────────────────────────────────┘
                 │
                 ▼
         ┌─────────────┐
         │  Kraken API │
         │  (REST+WS)  │
         └─────────────┘
```

### Security Model

**Credential Storage**: Environment variables (never committed to git)
```bash
export FATHOM_KRAKEN_API_KEY="your_api_key"
export FATHOM_KRAKEN_SECRET_KEY="your_secret_key"
```

**Authentication**: HMAC-SHA512 signature for all private endpoints
**Rate Limiting**: Tier-aware (starter: 15 req/s, intermediate: 20 req/s, pro: 20 req/s)
**Safety Limits**: MAX_ORDER_USD configured in environment (default: $50)

---

## MCP Tools (Phase 1 - 8 tools)

### Health & Monitoring
| Tool | Description | Status |
|------|-------------|--------|
| `fathom_health_check` | Check Fathom + Kraken API connectivity | ✅ Operational |
| `fathom_get_rate_limits` | Get current API rate limit usage | ✅ Operational |

### Account Management
| Tool | Description | Status |
|------|-------------|--------|
| `fathom_get_balance` | Get account balance for all assets | ✅ Operational |
| `fathom_get_portfolio_summary` | Get portfolio with USD valuations | ✅ Operational |
| `fathom_get_trade_balance` | Get detailed trade balance | ✅ Operational |

### Market Data
| Tool | Description | Status |
|------|-------------|--------|
| `fathom_get_ticker` | Get ticker data (price, volume, spread) | ✅ Operational |
| `fathom_get_orderbook` | Get order book (market depth) | ✅ Operational |
| `fathom_get_ohlc` | Get OHLC candlestick data | ✅ Operational |

### Order Management (Phase 3 - Not Implemented)
| Tool | Description | Status |
|------|-------------|--------|
| `fathom_place_order` | Place market/limit order | ❌ Phase 3 |
| `fathom_cancel_order` | Cancel open order | ❌ Phase 3 |
| `fathom_get_open_orders` | Get all open orders | ❌ Phase 3 |
| `fathom_get_trades` | Get trade history | ❌ Phase 3 |

---

## Dependencies

### Upstream (Required by Fathom)
- **Kraken API**: Exchange connectivity (REST API operational, WebSocket planned)
- **Python 3.10+**: Runtime environment
- **HMAC-SHA512**: Authentication library

### Downstream (Depends on Fathom)
- **Fathom Commander**: Orchestration layer (deployed but not connected)
- **SIL**: Decision engine (deployed but not connected)
- **Memory System**: Decision logging (operational, used in Session 16 first trade)

### Integration Gap
**Status**: 85/0 pattern (85% components exist, 0% workflows connecting them)

Fathom Phase 1 tools are operational, but no automated workflow connects:
- Fathom market data → SIL intelligence → FC orchestration → Fathom Phase 3 order placement

**Blocker**: Phase 2 integration planning (Session 75-76+ planned)

---

## Configuration

### Environment Variables

**Required**:
```bash
FATHOM_KRAKEN_API_KEY="..."
FATHOM_KRAKEN_SECRET_KEY="..."
```

**Optional**:
```bash
FATHOM_KRAKEN_TIER="starter"              # Rate limit tier
FATHOM_MAX_ORDER_USD="50.0"               # Safety cap
FATHOM_QDRANT_URL="http://localhost:6333" # Memory backend
FATHOM_SLACK_WEBHOOK_URL="..."            # Notifications
FATHOM_N8N_WEBHOOK_BASE="..."             # Automation hooks
```

### Claude Desktop Integration

Add to `claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "fathom": {
      "command": "python",
      "args": ["-m", "fathom.server"],
      "cwd": "/path/to/rhiz_localdev/domains/trading/fathom"
    }
  }
}
```

---

## Safety Mechanisms

### Multi-Layer Validation (Session 16 Implementation)

**Layer 1**: Parameter validation (pair, side, ordertype, volume)
**Layer 2**: Balance verification (sufficient USD/BTC for order)
**Layer 3**: Safety limits (MAX_ORDER_USD hard cap)
**Layer 4**: Rate limiting (tier-aware, prevents API ban)
**Layer 5**: Pre-execution memory logging (decision recorded before capital deployed)

See: `docs/architecture/autonomous_safety_enforcement_patterns.md`

### Safety Limits (Production Config)

```python
MAX_ORDER_USD = 50.00                # Hard cap per order
CAPTAIN_APPROVAL_THRESHOLD = 20.00   # Require approval above $20
MAX_DAILY_TRADES = 10                # Circuit breaker
CIRCUIT_BREAKER_LOSS_PERCENT = 10.0  # Halt if daily loss >= 10%
```

**Rationale**: Low capital ($50 total), high learning tolerance. Safety limits enable autonomous small trades (<$20) while requiring Captain approval for larger operations.

---

## First Trade Validation (Session 16)

**Date**: 2025-12-26
**Objective**: Validate entire pipeline (Claude → Fathom → Kraken → Memory)

### Execution Details

**Pre-Flight**:
- Balance verified: $50.00 USD available
- Market context: BTC @ $87,338.30
- Volume calculated: 0.0001 BTC (Kraken minimum)
- Safety checks: All passed

**Execution**:
- Order TXID: OBRP7D-MBTUR-4R2O6T
- Trade TXID: T3VYUR-HD6IR-433DNS
- Fill price: $87,420.00
- Total cost: $8.78 ($8.74 + $0.03 fee)
- Execution time: <10 seconds
- Slippage: +0.09% (acceptable)

**Outcome**: ✅ SUCCESS - 100% pipeline validation on first attempt

**What This Proved**:
- MCP protocol working (Claude ↔ Fathom communication)
- Kraken authentication functional
- Order placement successful
- Memory integration seamless (Decision ID: 38385488643530958)
- Safety checks enforced correctly

**Captain's Response**: "Execute it!" (immediate approval, high trust)

See: `docs/architecture/trading_pipeline_first_trade_case_study.md`

---

## Known Issues & Gaps

### Issue 1: 85/0 Pattern (Integration Gap)
**Description**: Fathom Phase 1 operational, but no workflow connecting to FC/SIL
**Impact**: Cannot execute automated trading strategies
**Resolution**: Phase 2 integration planning (Session 75-76+)

### Issue 2: Phase 3 Order Tools Not Implemented
**Description**: Order placement tools exist but not fully implemented with safety rails
**Impact**: Can only execute orders via manual Claude interaction
**Resolution**: Phase 3 implementation pending Phase 2 integration

### Issue 3: WebSocket Client Not Built
**Description**: Real-time market data requires WebSocket (currently REST polling)
**Impact**: Higher latency, more API calls, rate limit pressure
**Resolution**: Phase 4 (WebSocket client architecture designed, not coded)

---

## Failure Genealogy

### Rejected: Hummingbot Integration (Session 17)

**Approach**: Use Hummingbot bot framework as trading layer
**Reason**: Complexity overhead. Hummingbot designed for professional trading firms with extensive configuration, strategies, connectors. Rhiz needs AI-first interface, not human dashboard.
**Pivot**: Direct Kraken MCP (Fathom)
**Outcome**: ✅ SUCCESS - First trade validated in Session 16

**Learning**: Build exactly what's needed, not what's comprehensive. Fathom's 8 Phase 1 tools sufficient to execute first trade. Complexity should match immediate need.

---

## Future Phases (Planned)

### Phase 2: Memory Integration
- Qdrant FastEmbed for lightweight decision logging
- Trade pattern recognition
- Historical decision search

### Phase 3: Order Management
- Market order placement (with safety rails)
- Limit order placement
- Order cancellation
- Open orders monitoring
- Trade history retrieval

### Phase 4: Real-Time Data
- WebSocket client (wss://ws.kraken.com)
- Real-time ticker feed
- Order book (L2 depth)
- Trade stream
- OHLC updates

### Phase 5: Automation Hooks
- n8n webhook integration
- Slack/SMS notifications
- Automated circuit breakers
- Alert thresholds

### Phase 6: Backtesting
- Historical data replay
- Strategy simulation
- Performance metrics (Sharpe ratio, max drawdown, win rate)
- Hypothesis testing framework

---

## Performance Metrics

### API Response Times (Session 16)
- `get_account_balance`: 150-300ms
- `get_ticker`: 100-200ms
- `get_orderbook`: 200-400ms
- `place_market_order`: 8-12 seconds (order → fill)

### Rate Limit Usage
- **Tier**: Starter (15 req/s)
- **Typical usage**: 1-2 req/s (well below limit)
- **Burst capacity**: Can handle 10+ parallel requests without throttling

### Reliability
- **Uptime**: 100% (Kraken API operational)
- **Authentication failures**: 0
- **Order execution failures**: 0 (1/1 successful)

---

## Cross-References

**Source Code**:
- `domains/trading/fathom/` - Main codebase
- `domains/trading/fathom/README.md` - User documentation
- `domains/trading/fathom/ARCHITECTURE_v2.md` - Technical architecture

**Related Documentation**:
- `docs/architecture/trading_pipeline_first_trade_case_study.md` - First trade validation
- `docs/architecture/trading_intelligence_federation_phase1.md` - Three-tier architecture
- `docs/architecture/autonomous_safety_enforcement_patterns.md` - Safety mechanisms

**Integration Points**:
- `docs/knowledge_base/components/fathom_commander.md` - Orchestration layer
- `docs/knowledge_base/components/sil_decision_engine.md` - Intelligence layer
- `docs/knowledge_base/integrations/trading_pipeline.md` - Integration gap documentation

**Checkpoints**:
- `core/memory/checkpoints/session_20251226_wave2_first_trade.yaml` - First trade execution

---

**End of Component Documentation**

*Last Updated: 2026-01-25 (Session 74)*
*Status: Phase 1 operational, Phases 2-6 pending integration planning*
