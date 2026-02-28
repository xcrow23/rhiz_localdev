---
integration: trading-pipeline
status: missing
completion: 0%
gap_identified: session_73_20260125
components_exist: true
workflow_exists: false
pattern: 85_percent_components_0_percent_workflows
blocks:
  - fathom_phase2_trading: not_implemented
  - fc_http_gateway: not_deployed_requires_captain_vps_access
  - sil_workflow_connection: no_orchestration_layer
  - data_flow_automation: missing
required_components:
  - fathom_mcp_server: deployed_phase1_only
  - fathom_commander: deployed_not_connected
  - sil_decision_engine: deployed_not_connected
  - memory_system: operational
semantic_cluster: trading_domain
vector_density: high
threshold_recommendation: 0.30-0.40
last_updated: 2026-01-25
---

# Trading Pipeline Integration (MISSING)

**Integration Type**: Multi-Component Data Flow
**Status**: ❌ **NOT IMPLEMENTED** (85/0 pattern)
**Components**: All deployed separately, no connecting workflow

---

## Overview

The trading pipeline integration represents the **largest identified gap** in the Rhiz architecture. All three trading components exist and are operational:

- **Fathom MCP**: Phase 1 deployed (account + market data tools)
- **Fathom Commander**: Deployed to VPS (27 tools, HTTP gateway)
- **SIL**: Deployed to VPS (regime classification, strategy selection)

**However**: No automated workflow connects them. This is the quintessential **85/0 pattern**—85% of components exist, 0% of workflows connecting them.

---

## Intended Architecture (Not Implemented)

### Desired Data Flow

```
┌─────────────────────────────────────────────────────────────┐
│ 1. MARKET DATA INGESTION                                     │
│    Fathom MCP → Market Data (ticker, orderbook, OHLC)       │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ 2. INTELLIGENCE ANALYSIS                                     │
│    SIL → Regime Classification                              │
│    SIL → Strategy Selection                                 │
│    SIL → Risk Assessment                                    │
│    SIL → TRACE_FE Reasoning                                 │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ 3. ORCHESTRATION (MISSING LAYER)                            │
│    FC → Workflow Composition                                │
│    FC → Captain Approval (if >$20)                          │
│    FC → Safety Validation                                   │
│    FC → Pre-Execution Memory Logging                        │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ 4. TRADE EXECUTION (NOT IMPLEMENTED)                        │
│    Fathom MCP Phase 3 → Order Placement                     │
│    Fathom MCP → Trade Verification                          │
│    FC → Post-Execution Memory Update                        │
└─────────────────────────────────────────────────────────────┘
```

**Current Reality**: Each box exists independently. No arrows connecting them.

---

## What Works (Components)

### Fathom MCP Phase 1 ✅
- Account balance queries operational
- Market data tools (ticker, orderbook, OHLC) functional
- Kraken authentication working
- **Validated**: First trade executed successfully (Session 16)

### Fathom Commander ✅
- 27 MCP tools defined
- HTTP gateway deployed to VPS
- Traefik routing operational (https://fathom.dreamthewilderness.com/)
- Paper mode enforced (Session 6 safety intervention)

### SIL ✅
- Regime classification operational
- Strategy selection functional
- FastAPI endpoints deployed
- Qdrant integration working (regime_patterns, strategy_outcomes)

---

## What's Missing (Workflows)

### Missing 1: Automated Data Flow
**Gap**: No automated process to:
1. Fetch market data from Fathom
2. Send to SIL for analysis
3. Route SIL recommendations to FC
4. Trigger FC orchestration

**Current Workaround**: Manual Claude Code interactions
- Human must manually call `get_ticker` → copy data → ask SIL for analysis → interpret result

### Missing 2: FC HTTP Gateway Access
**Gap**: FC deployed to VPS but HTTP endpoints not accessible for automation

**Blocker**: Requires Captain VPS access to configure endpoints, test connectivity

**Impact**: n8n workflows cannot call FC tools via HTTP

### Missing 3: Fathom Phase 2-3
**Gap**: Order placement tools not implemented

**Blocker**: Fathom Phase 3 (order management) not started

**Impact**: Even if workflow existed, cannot execute trades

### Missing 4: Cross-Component Memory
**Gap**: `trading_signals` collection exists but empty

**Intent**: Share learnings across Fathom/FC/SIL (Intelligence Federation)

**Impact**: Components cannot learn from each other's patterns

---

## Why This Matters (Impact Analysis)

### Without Integration

**Current Capability**:
- Can query account balance
- Can fetch market data
- Can analyze market conditions (SIL)
- Can recommend strategies (SIL)
- **Cannot**: Execute automated trades

**Use Case Enabled**: Manual analysis only
- Captain asks "What's BTC doing?"
- First Mate fetches ticker, analyzes regime, recommends strategy
- Captain manually decides execution

**Use Case Blocked**: Autonomous trading
- Scheduled DCA execution (Weekly DCA Buyer workflow)
- Risk-managed position taking (Smart DCA workflow)
- Automated circuit breakers (Volatility Sentinel workflow)

### With Integration

**Enabled Use Cases**:
1. **Scheduled Trading**: Weekly DCA Buyer executes Sunday 6PM CT automatically
2. **Risk Management**: Volatility Sentinel halts trading during extreme moves
3. **Strategy Automation**: Smart DCA adjusts based on SIL regime analysis
4. **Learning Loop**: `trading_signals` collection accumulates cross-component patterns
5. **Decision Logging**: Full pipeline execution logged to memory (hypothesis → execution → outcome)

---

## Integration Design (Planned for Phase 2)

### Workflow Example: DCA Execution

**Trigger**: n8n cron (Sunday 6PM CT)

**Step 1: Data Collection**
```http
POST http://fathom.dreamthewilderness.com/tools/get_ticker
{"pair": "XXBTZUSD"}
→ Response: {price: 87420, spread: 0.10, volume: 1275.97}
```

**Step 2: Intelligence Analysis**
```http
POST http://sil:8000/regime
{"pair": "XXBTZUSD", "timeframe": "1h"}
→ Response: {regime: "high_volatility_bullish", confidence: 0.87}

POST http://sil:8000/strategy
{"regime": "high_volatility_bullish", "portfolio_value": 50.68}
→ Response: {strategy: "momentum_breakout", position_size: 10.14}
```

**Step 3: Orchestration** (FC)
```http
POST http://fathom.dreamthewilderness.com/tools/execute_trade
{
  "pair": "XXBTZUSD",
  "side": "buy",
  "order_type": "market",
  "volume": 0.0001,
  "reasoning": "SIL recommends momentum_breakout in high_volatility_bullish regime",
  "hypothesis": "BTC breakout continuation based on regime classification"
}
```

**Step 4: Safety Checks** (FC internal)
- Check if $10.14 < $20 (auto-approve threshold) → Yes, proceed
- Check if $10.14 < $50 (max order) → Yes, proceed
- Check daily trades < 10 → Yes (0/10), proceed
- Check circuit breaker not halted → Yes, proceed

**Step 5: Memory Logging** (FC)
```
Log decision to Qdrant BEFORE execution:
- Decision ID: generated
- Hypothesis: from SIL
- Reasoning: regime + strategy
- Expected outcome: breakout continuation
- Status: pending
```

**Step 6: Execution** (Fathom Phase 3 - not implemented)
```
Call Kraken API:
- Place market order 0.0001 BTC
- Receive order TXID
- Wait for fill
- Verify execution
```

**Step 7: Memory Update** (FC)
```
Update decision in Qdrant with outcome:
- Status: success/failed
- Execution details: fill price, fee, slippage
- Learnings: actual vs expected
```

**Step 8: Cross-Component Learning** (Intelligence Federation)
```
Store signal in trading_signals collection:
- Regime: high_volatility_bullish
- Strategy: momentum_breakout
- Outcome: TBD (track over time)
- Components: Fathom + FC + SIL
```

---

## Blockers to Implementation

### Blocker 1: Fathom Phase 3 Not Implemented
**Component**: Fathom MCP
**Gap**: Order placement tools not coded
**Impact**: Cannot execute Step 6 (trade execution)
**Resolution**: Implement Phase 3 tools (estimate: 2-3 sessions)

### Blocker 2: FC HTTP Gateway Not Configured
**Component**: Fathom Commander
**Gap**: HTTP endpoints exist but not accessible from n8n/external
**Impact**: Cannot call FC tools via HTTP (Step 3)
**Blocker**: Requires Captain VPS access for configuration
**Resolution**: Captain configures VPS networking, FC environment

### Blocker 3: SIL HTTP Endpoints Not Tested
**Component**: SIL
**Gap**: FastAPI endpoints deployed but not tested with external calls
**Impact**: Unknown if Step 2 will work
**Resolution**: Integration testing (estimate: 1 session)

### Blocker 4: Memory Logging Not Integrated
**Component**: FC + Memory System
**Gap**: Pre/post-execution logging exists (Session 16) but not integrated into FC tools
**Impact**: Steps 5 & 7 not automated
**Resolution**: Integrate memory logging into FC execute_trade tool (estimate: 1 session)

### Blocker 5: n8n Workflows Not Updated
**Component**: n8n / Cloudflare Workers
**Gap**: Workflows reference old endpoints, not updated for new architecture
**Impact**: Cannot trigger Step 1 (no automation)
**Resolution**: Update workflows or migrate to Cloudflare Workers (estimate: 2-3 sessions)

---

## Effort Estimate for Full Integration

**Phase 2 Integration Plan** (Session 75-76+):

1. **Implement Fathom Phase 3** (3 sessions)
   - Order placement tool with safety validation
   - Order cancellation
   - Trade history retrieval
   - Testing with paper trades

2. **Configure FC HTTP Gateway** (1 session)
   - Captain VPS access session
   - Configure FC environment
   - Test HTTP endpoints
   - Validate n8n connectivity

3. **SIL Integration Testing** (1 session)
   - Test regime classification endpoint
   - Test strategy selection endpoint
   - Validate response formats
   - Error handling

4. **Memory Logging Integration** (1 session)
   - Integrate pre-execution logging into FC
   - Integrate post-execution updates
   - Test decision tracking end-to-end

5. **Workflow Implementation** (2-3 sessions)
   - Update n8n DCA workflows
   - Or: Migrate to Cloudflare Workers
   - Test automated execution
   - Validate safety mechanisms

**Total Estimate**: 8-10 sessions (assuming no major blockers)

---

## Failure Genealogy (Parallel Development)

### Pattern: Components Built Independently

**What Happened**:
- Dec 17-26: Fathom Phase 1 built and validated (Session 1-16)
- Dec 29-Jan 3: Fathom Commander discovered already deployed (Session 6)
- Jan 10-11: SIL deployed to VPS (Session 42)

**Each component built correctly in isolation. No integration testing between them.**

**Why This Occurred**:
1. **Focused execution**: Each session tackled one component thoroughly
2. **Delayed integration planning**: Assumed "build components first, connect later"
3. **Discovery mode**: VPS infrastructure discovered mid-project (Session 6)
4. **No integration specification**: Components built to spec but spec didn't define connections

**Learning**: Architecture decisions should include integration workflows from start, not just component specifications.

**Alternative That Wasn't Taken**:
- Build minimal end-to-end workflow first (thin vertical slice)
- Then expand each component's capabilities
- Would have surfaced integration issues earlier

**Why We Didn't**: Spec-driven development (build Fathom Phase 1 completely, then Phase 2, etc.) felt more organized. In hindsight, caused 85/0 pattern.

---

## Recommended Next Steps (Phase 2 Priority)

**Highest ROI**: Trading pipeline integration before any other feature work

**Why**:
1. **Unblocks value**: Components exist but provide no autonomous trading capability
2. **Validates architecture**: Tests if three-tier design actually works
3. **Enables learning**: `trading_signals` collection starts accumulating patterns
4. **Completes existing work**: 85% components → 100% with workflows

**Suggested Session 75 Focus**:
1. Captain VPS access session
2. Configure FC HTTP Gateway
3. Test SIL endpoints
4. Validate end-to-end connectivity (minimal DCA workflow)

**Deferred to Later**:
- Fathom Phase 4-6 (WebSocket, notifications, backtesting)
- n8n → Cloudflare Workers migration (mooncheck complete, trading can wait)
- Skill-tool binding framework

---

## Cross-References

**Component Documentation**:
- `docs/knowledge_base/components/fathom_mcp_server.md` - Execution layer
- `docs/knowledge_base/components/fathom_commander.md` - Orchestration layer
- `docs/knowledge_base/components/sil_decision_engine.md` - Intelligence layer

**Architecture Documents**:
- `docs/architecture/trading_intelligence_federation_phase1.md` - Three-tier architecture design
- `docs/architecture/trading_pipeline_first_trade_case_study.md` - Manual execution validation (Session 16)

**Session Synthesis**:
- `docs/sessions/session_73_architectural_synthesis.md` - 85/0 pattern discovery

**Checkpoints**:
- `core/memory/checkpoints/session_20260125_session_73.yaml` - Documentation drift analysis

---

**End of Integration Documentation**

*Last Updated: 2026-01-25 (Session 74)*
*Status: Gap identified and documented, awaiting Phase 2 implementation*
*Priority: HIGHEST (unblocks autonomous trading capability)*
