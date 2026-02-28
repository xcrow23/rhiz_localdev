# Fathom Commander MCP Audit - Session 25

**Date**: 2026-01-05
**Auditor**: First Mate Daemon
**Server Location**: domains/trading/fathom_commander/server.py
**Configuration**: .mcp.json (stdio server with Kraken API credentials)

---

## Executive Summary

Fathom Commander is configured in .mcp.json but tools are **not currently accessible** through the MCP interface in this session. This may be due to server not being started by Claude Code, or a configuration issue requiring restart.

**Status**:
- ⚠️ Server configured but not responding to MCP calls
- ✅ Source code verified - 27 tools defined
- 📋 Requires restart/verification

---

## Configuration (from .mcp.json)

```json
{
  "fathom-commander": {
    "command": "python",
    "args": ["C:\\Users\\dread\\Documents\\Rhiz_LocalDev\\domains\\trading\\fathom_commander\\server.py"],
    "env": {
      "KRAKEN_API_KEY": "${KRAKEN_API_KEY}",
      "KRAKEN_SECRET_KEY": "${KRAKEN_SECRET_KEY}"
    }
  }
}
```

**Type**: stdio server
**Dependencies**: Kraken API credentials (environment variables)
**Purpose**: Trading execution, portfolio management, market analysis

---

## Tool Inventory (27 Tools Defined in Source)

### System Tools (3)

1. **heartbeat**
   - Health check called by n8n every 60s
   - Returns operational status
   - Used for monitoring

2. **set_mode**
   - Set operational mode: live, paper, disabled, emergency_stop
   - Critical safety control
   - Captain command

3. **get_state_summary**
   - Get current state summary
   - Mode, last heartbeat, pending approvals
   - Non-destructive query

4. **get_pending_approvals**
   - Get all pending approval requests
   - For trades > $20 requiring Captain approval

---

### Market Data Tools (3)

5. **market_ticker**
   - Get current ticker data for trading pairs
   - Real-time price, volume, spread

6. **market_ohlc**
   - Get OHLC candlestick data
   - Historical price action
   - Timeframe configurable

7. **market_analyze**
   - Analyze market conditions for trading
   - Comprehensive market assessment

---

### Trade Execution Tools (5)

8. **execute_trade**
   - Execute a trade with safety checks
   - Requires approval for orders > $20
   - Primary trading interface

9. **validate_trade**
   - Validate a trade without executing
   - Pre-flight check before execution

10. **approve_order**
    - Approve a pending order
    - Captain command
    - Required for large trades

11. **reject_order**
    - Reject a pending order
    - Captain command

12. **cancel_order**
    - Cancel an open order
    - Emergency stop capability

13. **get_open_orders**
    - Get all open orders
    - Monitor active positions

14. **get_trade_history**
    - Get recent trade history
    - Performance tracking

---

### Portfolio Management Tools (4)

15. **portfolio_balance**
    - Get account balances
    - USD and crypto holdings

16. **portfolio_holdings**
    - Get holdings with USD values
    - Current position sizes

17. **portfolio_summary**
    - Get comprehensive portfolio summary
    - Total value, allocation, P&L

18. **portfolio_performance**
    - Get trading performance metrics
    - Win rate, Sharpe ratio, max drawdown

---

### Strategy Tools (5)

19. **strategy_list**
    - List available trading strategies
    - Shows configured strategy library

20. **strategy_activate**
    - Activate a trading strategy
    - Sets active strategy for signals

21. **strategy_deactivate**
    - Deactivate current strategy
    - Returns to manual mode

22. **strategy_signal**
    - Generate trading signal using active strategy
    - Autonomous decision-making

23. **strategy_check_exits**
    - Check all positions for exit signals
    - Risk management

24. **strategy_analyze_opportunity**
    - Full opportunity analysis
    - Market + strategy signal combined

---

### Alert Tools (3)

25. **alert_send**
    - Send a notification
    - Multi-channel (console, file, future: email/SMS)

26. **alert_history**
    - Get recent alert history
    - Audit trail

27. **alert_status**
    - Get alert system status
    - Configuration and health

---

## Integration Points

### n8n Heartbeat
**Workflow**: Rhiz Daily Health Monitor (LfO8CCuyrjj45z4P)
**Interval**: 60 seconds
**Purpose**: Monitor Fathom Commander liveness, detect crashes
**Action**: Alerts if heartbeat fails

### Kraken API
**Exchange**: Kraken
**Account**: Active with ~$100-150 capital
**Assets**: BTC, USD (likely)
**Risk Profile**: Low financial tolerance, high experimental tolerance

### State Management
**State Directory**: domains/trading/fathom_commander/state/
**Persistence**: File-based state storage
**Mode Tracking**: Live/paper/disabled/emergency_stop

---

## Safety Architecture

### Trade Approval Workflow
```
Trade Request
    │
    ├─ < $20 → Execute immediately
    │
    └─ > $20 → Pending approval
               │
               ├─ Captain approves → Execute
               └─ Captain rejects → Cancel
```

### Emergency Controls
- **emergency_stop mode**: Halt all trading immediately
- **cancel_order**: Manual intervention capability
- **reject_order**: Disapprove pending trades
- **set_mode**: Override operational mode

### Risk Limits (Assumed from Documentation)
- Position size limits
- Daily loss limits
- Volatility-based adjustments
- Max open positions

---

## MCP Compliance Status

**From Session 24 Context** (MCP_COMPLIANCE_REPORT.md):
- ✅ Valid JSON Schema tool definitions
- ✅ Proper async/await patterns
- ✅ Thread-safe state management
- ✅ Structured error responses
- ✅ No stdio interference

Fathom Commander is fully MCP spec compliant according to Session 24 audit.

---

## Current Issue: MCP Tools Not Accessible

### Symptoms
- `ListMcpResourcesTool("fathom-commander")` returns empty array
- Direct tool calls fail with "No such tool available"
- Server source code verified - tools properly defined

### Possible Causes
1. **Server not started**: Claude Code may not have launched fathom-commander on session start
2. **Naming mismatch**: Tool names may be prefixed differently than expected
3. **Configuration issue**: .mcp.json entry may have syntax error
4. **Dependency issue**: Kraken API credentials not available in environment

### Diagnostic Steps (Post-Restart)
1. Check if fathom-commander process is running
2. Verify environment variables (KRAKEN_API_KEY, KRAKEN_SECRET_KEY)
3. Test direct server execution: `python server.py`
4. Check Claude Code logs for server startup errors
5. Verify tool naming convention (may need mcp__ prefix)

---

## Test Plan (Post-Restart)

### Priority 1: Connection Verification
- [ ] Verify fathom-commander server is running
- [ ] Test `heartbeat` tool
- [ ] Test `get_state_summary` tool
- [ ] Verify n8n heartbeat workflow is calling server

### Priority 2: Portfolio Queries (Non-Destructive)
- [ ] `portfolio_balance` - Check account balances
- [ ] `portfolio_holdings` - View current positions
- [ ] `portfolio_summary` - Overall portfolio state
- [ ] `portfolio_performance` - Performance metrics

### Priority 3: Market Data (Non-Destructive)
- [ ] `market_ticker` - Get BTC/USD ticker
- [ ] `market_ohlc` - Get recent candles
- [ ] `market_analyze` - Market condition analysis

### Priority 4: Strategy System (Non-Destructive)
- [ ] `strategy_list` - List available strategies
- [ ] `get_pending_approvals` - Check for pending orders
- [ ] `get_open_orders` - View active orders
- [ ] `get_trade_history` - Recent trade history

### Priority 5: Safety Controls (Verify, Don't Execute)
- [ ] Verify `set_mode` accepts valid modes
- [ ] Verify `approve_order` / `reject_order` workflow
- [ ] **DO NOT** execute real trades without explicit Captain approval

---

## Recommendations

### Immediate (Post-Restart)
1. Verify fathom-commander MCP server connectivity
2. Test heartbeat to confirm operational
3. Check portfolio balance to verify Kraken API connection
4. Verify n8n heartbeat workflow is functional

### Short-Term
1. Document actual MCP tool naming convention once accessible
2. Create tool usage examples for common operations
3. Test trade validation workflow (validate, not execute)
4. Review strategy library configuration

### Integration with Memory System
1. Consider logging trade decisions to Qdrant for analysis
2. Create embeddings for market conditions at trade entry
3. Enable semantic search: "Find trades similar to current market"
4. Strategy performance tracking with vector similarity

---

## Notes

- **Financial Safety**: All trade execution respects approval thresholds
- **Paper Trading**: Verify mode is set correctly before live trading
- **API Rate Limits**: Kraken has rate limits, avoid excessive API calls
- **State Persistence**: Check state/ directory for operational history
- **n8n Integration**: Health monitoring via heartbeat is operational infrastructure

---

## Known Issues

### Deprecation Warning
**File**: server.py:75
**Issue**: `datetime.utcnow()` is deprecated
**Impact**: Will break in future Python versions
**Fix**: Replace with `datetime.now(datetime.UTC)`
**Priority**: Medium (works now, but should be updated)

---

## Session 24 Context

Fathom Commander was operational in Session 24:
- n8n heartbeat workflow confirmed functional
- Server has been tested in previous sessions
- MCP compliance audit passed
- No reported connectivity issues

Current session connectivity issue is likely environmental or session-specific, not a code defect.
