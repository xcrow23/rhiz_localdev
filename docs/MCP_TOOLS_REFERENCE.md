# MCP Tools Reference

**Purpose**: Comprehensive catalog of all Model Context Protocol tools in Rhiz
**Last Updated**: 2026-01-25 (Session 74)
**Total Tools**: 52 (across 4 MCP servers)

---

## Quick Index

| MCP Server | Tool Count | Status | Purpose |
|------------|------------|--------|---------|
| [rhiz-mcp](#rhiz-mcp-11-tools) | 11 | ✅ Operational | Dyad state, checkpoints, memory context |
| [memory-mcp](#memory-mcp-6-tools) | 6 | ✅ Operational | Semantic search, memory stats |
| [fathom](#fathom-phase-1-8-tools) | 8 | ✅ Operational | Kraken account + market data |
| [fathom-commander](#fathom-commander-27-tools) | 27 | ✅ Operational | Orchestration, health monitoring |

**Total**: 52 tools operational

---

## rhiz-mcp (11 Tools)

**Purpose**: Core Rhiz infrastructure - dyad state management, checkpoint operations, memory context
**Protocol**: stdio (local MCP server)
**Location**: `tools/rhiz-mcp/`
**Configuration**: `.mcp.json` with `RHIZ_ROOT` environment variable
**Status**: ✅ Fully operational

---

### Dyad State Management (3 tools)

#### 1. `get_dyad_state`

**Purpose**: Retrieve current dyad state (session count, Captain status, shared focus)
**Parameters**: None
**Returns**:
```json
{
  "session_count": 74,
  "captain_state": "active",
  "first_mate_state": "operational",
  "shared_focus": "Phase 1 Documentation Unification",
  "captain_session_count": 74,
  "project_day": 40
}
```
**Use Case**: Session startup, state verification
**Example**: `get_dyad_state()` → returns current session metadata

---

#### 2. `set_captain_state`

**Purpose**: Update Captain's status (active, away, reviewing)
**Parameters**:
- `state` (string): New Captain state
**Returns**: Confirmation of state update
**Use Case**: Captain availability changes
**Example**: `set_captain_state("away")` → marks Captain as unavailable

---

#### 3. `update_shared_focus`

**Purpose**: Update current session focus area
**Parameters**:
- `focus` (string): New focus description
**Returns**: Confirmation of focus update
**Use Case**: Session direction changes, phase transitions
**Example**: `update_shared_focus("Phase 2 Component Integration")` → updates dyad.md

---

### Checkpoint Operations (4 tools)

#### 4. `checkpoint_search`

**Purpose**: Semantic search across checkpoint content
**Parameters**:
- `query` (string): Search query
- `limit` (int, optional): Max results (default: 5)
**Returns**: List of relevant checkpoints with similarity scores
**Use Case**: Find past sessions about specific topics
**Example**: `checkpoint_search("threshold tuning", limit=3)` → returns Sessions 71-72

---

#### 5. `load_checkpoint`

**Purpose**: Load full checkpoint file content
**Parameters**:
- `session_id` (string): Session identifier or filename
**Returns**: Full checkpoint YAML content
**Use Case**: Detailed session review, context loading
**Example**: `load_checkpoint("session_20260124_phase2_complete.yaml")` → returns full checkpoint

---

#### 6. `write_checkpoint`

**Purpose**: Write new checkpoint file (session end)
**Parameters**:
- `checkpoint_data` (dict): Full checkpoint content (follows session_schema.yaml)
**Returns**: Confirmation with file path
**Use Case**: Session end, milestone documentation
**Example**: `write_checkpoint({...})` → creates new checkpoint file

---

#### 7. `list_checkpoints`

**Purpose**: List all available checkpoints with metadata
**Parameters**:
- `limit` (int, optional): Max checkpoints to return
**Returns**: List of checkpoint filenames with dates
**Use Case**: Browse checkpoint history
**Example**: `list_checkpoints(limit=10)` → returns 10 most recent checkpoints

---

### Memory Context (4 tools)

#### 8. `memory_context`

**Purpose**: Automatic relevant memory retrieval for query
**Parameters**:
- `query` (string): Context query
- `threshold` (float, optional): Similarity threshold (default: 0.25)
**Returns**: Relevant memory snippets with context
**Use Case**: Contextual question answering, automatic context loading
**Example**: `memory_context("trading pipeline integration")` → returns relevant memories

---

#### 9. `hybrid_search_checkpoints`

**Purpose**: Combined semantic + keyword + pattern + temporal search
**Parameters**:
- `query` (string): Search query
- `keywords` (list, optional): Exact terms to match
- `pattern` (string, optional): Regex pattern
- `date_range` (dict, optional): Start/end dates
- `limit` (int, optional): Max results
**Returns**: Ranked checkpoint results from multiple search strategies
**Use Case**: Complex memory queries requiring multi-faceted search
**Example**: `hybrid_search_checkpoints("safety", keywords=["paper mode"], limit=5)`

---

#### 10. `signal_completion`

**Purpose**: Mark task or phase as complete in dyad state
**Parameters**:
- `task_id` (string): Task identifier
- `summary` (string): Completion summary
**Returns**: Confirmation
**Use Case**: Phase completion, milestone marking
**Example**: `signal_completion("phase_1", "Documentation unification complete")`

---

#### 11. `propose_focus_shift`

**Purpose**: Suggest change in session focus area
**Parameters**:
- `new_focus` (string): Proposed focus
- `rationale` (string): Why shift focus
**Returns**: Proposal recorded (Captain approval typically needed)
**Use Case**: Strategic pivots, session direction changes
**Example**: `propose_focus_shift("Phase 2 Integration", "Phase 1 complete, ready for next phase")`

---

## memory-mcp (6 Tools)

**Purpose**: Semantic search and statistics for vector memory (Qdrant)
**Protocol**: stdio (local MCP server)
**Location**: `tools/memory-mcp/`
**Backend**: Qdrant localhost:6333, collection `rhiz_memories`
**Status**: ✅ Fully operational

---

### Semantic Search (3 tools)

#### 1. `memory_search`

**Purpose**: Semantic search across checkpoint vectors
**Parameters**:
- `query` (string): Search query
- `limit` (int, optional): Max results (default: 5)
- `threshold` (float, optional): Similarity threshold (default: 0.25)
**Returns**: Ranked memory snippets with similarity scores
**Use Case**: General memory retrieval, contextual queries
**Example**: `memory_search("first trade execution", limit=3)` → returns Dec 26 checkpoint

---

#### 2. `memory_search_by_date`

**Purpose**: Search memories within specific date range
**Parameters**:
- `query` (string): Search query
- `start_date` (string): ISO date (YYYY-MM-DD)
- `end_date` (string): ISO date (YYYY-MM-DD)
- `limit` (int, optional): Max results
**Returns**: Date-filtered memory results
**Use Case**: Temporal queries, finding when something happened
**Example**: `memory_search_by_date("infrastructure", "2026-01-01", "2026-01-10")` → Session 6

---

#### 3. `memory_get_recent_sessions`

**Purpose**: Retrieve N most recent checkpoint memories
**Parameters**:
- `count` (int): Number of recent sessions
**Returns**: Recent checkpoint vectors in chronological order
**Use Case**: Session continuity, recent context loading
**Example**: `memory_get_recent_sessions(5)` → last 5 sessions

---

### Memory Management (3 tools)

#### 4. `memory_store`

**Purpose**: Store new vector embedding in Qdrant
**Parameters**:
- `text` (string): Content to embed
- `metadata` (dict): Associated metadata
- `collection` (string, optional): Target collection (default: rhiz_memories)
**Returns**: Confirmation with vector ID
**Use Case**: Checkpoint ingestion, new memory creation
**Example**: `memory_store("Session 74 focused on documentation", {...})`

---

#### 5. `memory_stats`

**Purpose**: Get memory system statistics
**Parameters**: None
**Returns**:
```json
{
  "total_vectors": 175,
  "collections": {
    "rhiz_memories": 161,
    "rhiz_skills": 6,
    "rhiz_skill_memory": 8
  },
  "avg_quality": 0.73,
  "storage_size": "~50MB"
}
```
**Use Case**: Health monitoring, capacity planning
**Example**: `memory_stats()` → current system state

---

#### 6. `memory_health_check`

**Purpose**: Verify Qdrant connectivity and collection health
**Parameters**: None
**Returns**: Health status report
**Use Case**: System diagnostics, deployment verification
**Example**: `memory_health_check()` → Qdrant operational status

---

## fathom (Phase 1: 8 Tools)

**Purpose**: Kraken exchange integration - account management + market data
**Protocol**: stdio (MCP server)
**Location**: `domains/trading/fathom/`
**Status**: ✅ Phase 1 operational (Phase 2-6 pending)
**First Trade**: Dec 26, 2025 (0.0001 BTC @ $87,420)

---

### Account Management (3 tools)

#### 1. `fathom_health_check`

**Purpose**: Verify Fathom server connectivity and Kraken API status
**Parameters**: None
**Returns**: Health status (server + API)
**Use Case**: System startup, deployment verification
**Example**: `fathom_health_check()` → "Fathom operational, Kraken API connected"

---

#### 2. `fathom_get_balance`

**Purpose**: Retrieve account balances for all assets
**Parameters**:
- `asset` (string, optional): Specific asset (e.g., "BTC", "USD")
**Returns**: Account balances with available/held amounts
**Use Case**: Portfolio monitoring, pre-trade validation
**Example**: `fathom_get_balance("BTC")` → {"BTC": {"balance": 0.0001, "available": 0.0001}}

---

#### 3. `fathom_get_trade_history`

**Purpose**: Retrieve historical trades
**Parameters**:
- `pair` (string, optional): Trading pair (e.g., "XBTUSD")
- `start` (int, optional): Unix timestamp start
- `limit` (int, optional): Max trades to return
**Returns**: List of historical trades
**Use Case**: Performance analysis, audit trail
**Example**: `fathom_get_trade_history("XBTUSD", limit=10)` → recent BTC trades

---

### Market Data (5 tools)

#### 4. `fathom_get_ticker`

**Purpose**: Get current ticker information for trading pair
**Parameters**:
- `pair` (string): Trading pair (e.g., "XBTUSD")
**Returns**: Bid, ask, last price, volume, high/low
**Use Case**: Real-time price monitoring, execution decisions
**Example**: `fathom_get_ticker("XBTUSD")` → current BTC/USD price data

---

#### 5. `fathom_get_orderbook`

**Purpose**: Retrieve order book (bids + asks) for trading pair
**Parameters**:
- `pair` (string): Trading pair
- `depth` (int, optional): Order book depth (default: 10)
**Returns**: Bids and asks with price/volume
**Use Case**: Liquidity analysis, execution strategy
**Example**: `fathom_get_orderbook("XBTUSD", depth=5)` → top 5 bids/asks

---

#### 6. `fathom_get_ohlc`

**Purpose**: Get OHLC (candlestick) data for pair
**Parameters**:
- `pair` (string): Trading pair
- `interval` (int, optional): Candle interval in minutes (default: 1)
- `since` (int, optional): Unix timestamp
**Returns**: OHLC candlestick data
**Use Case**: Technical analysis, pattern recognition
**Example**: `fathom_get_ohlc("XBTUSD", interval=60)` → hourly candles

---

#### 7. `fathom_get_spread`

**Purpose**: Get current bid/ask spread for trading pair
**Parameters**:
- `pair` (string): Trading pair
**Returns**: Bid, ask, spread amount, spread percentage
**Use Case**: Execution cost analysis, liquidity monitoring
**Example**: `fathom_get_spread("XBTUSD")` → current spread in USD and %

---

#### 8. `fathom_get_asset_pairs`

**Purpose**: List all available trading pairs on Kraken
**Parameters**: None
**Returns**: All trading pairs with metadata
**Use Case**: Discovery, validation of pair availability
**Example**: `fathom_get_asset_pairs()` → all Kraken trading pairs

---

### Phase 2-6 Tools (Pending)

**Not Yet Implemented**:
- Phase 2: Trading (place orders, cancel, modify)
- Phase 3: Websockets (real-time market data streaming)
- Phase 4: Staking (earn yield on holdings)
- Phase 5: Funding (margin trading)
- Phase 6: Advanced features (custom strategies)

**Estimated Effort**: 15-20 hours (all phases)
**Priority**: HIGH (Phase 2 needed for trading integration)

---

## fathom-commander (27 Tools)

**Purpose**: Trading workflow orchestration, health monitoring, error recovery
**Protocol**: HTTP (VPS deployed) + stdio (local development)
**Location**: `domains/trading/fathom_commander/`
**Deployment**: VPS production-ready, HTTP Gateway operational
**Status**: ✅ All 27 tools operational

---

### Health & Monitoring (4 tools)

#### 1. `fc_health_check`

**Purpose**: Verify Fathom Commander operational status
**Parameters**: None
**Returns**: System health, service status
**Use Case**: Deployment verification, monitoring
**Example**: `fc_health_check()` → "FC operational, all services healthy"

---

#### 2. `fc_get_system_status`

**Purpose**: Get comprehensive system status (all components)
**Parameters**: None
**Returns**: Status of all subsystems (Fathom, SIL, Qdrant, etc.)
**Use Case**: System overview, troubleshooting
**Example**: `fc_get_system_status()` → all component health states

---

#### 3. `fc_get_metrics`

**Purpose**: Retrieve performance metrics
**Parameters**:
- `metric_type` (string, optional): Specific metric (latency, throughput, errors)
**Returns**: Performance statistics
**Use Case**: Performance monitoring, optimization
**Example**: `fc_get_metrics("latency")` → p50/p95/p99 latencies

---

#### 4. `fc_get_logs`

**Purpose**: Retrieve recent log entries
**Parameters**:
- `level` (string, optional): Log level (info, warn, error)
- `limit` (int, optional): Max entries
**Returns**: Recent log entries
**Use Case**: Debugging, troubleshooting
**Example**: `fc_get_logs(level="error", limit=10)` → recent errors

---

### Workflow Orchestration (8 tools)

#### 5. `fc_create_workflow`

**Purpose**: Define new trading workflow
**Parameters**:
- `workflow_name` (string): Workflow identifier
- `workflow_definition` (dict): Workflow steps and logic
**Returns**: Workflow ID
**Use Case**: Workflow creation, strategy implementation
**Example**: `fc_create_workflow("dca_btc", {...})` → new DCA workflow

---

#### 6. `fc_list_workflows`

**Purpose**: List all defined workflows
**Parameters**:
- `status` (string, optional): Filter by status (active, paused, completed)
**Returns**: Workflow list with metadata
**Use Case**: Workflow management, overview
**Example**: `fc_list_workflows(status="active")` → active workflows

---

#### 7. `fc_get_workflow`

**Purpose**: Get workflow definition and status
**Parameters**:
- `workflow_id` (string): Workflow identifier
**Returns**: Full workflow details
**Use Case**: Workflow inspection, debugging
**Example**: `fc_get_workflow("dca_btc_001")` → workflow definition + state

---

#### 8. `fc_start_workflow`

**Purpose**: Start or resume workflow execution
**Parameters**:
- `workflow_id` (string): Workflow to start
- `parameters` (dict, optional): Execution parameters
**Returns**: Execution ID
**Use Case**: Workflow activation
**Example**: `fc_start_workflow("dca_btc_001", {"amount_usd": 50})` → starts execution

---

#### 9. `fc_pause_workflow`

**Purpose**: Pause running workflow
**Parameters**:
- `workflow_id` (string): Workflow to pause
**Returns**: Confirmation
**Use Case**: Manual intervention, safety
**Example**: `fc_pause_workflow("dca_btc_001")` → pauses execution

---

#### 10. `fc_stop_workflow`

**Purpose**: Stop workflow execution (cannot resume)
**Parameters**:
- `workflow_id` (string): Workflow to stop
- `reason` (string, optional): Stop reason
**Returns**: Confirmation
**Use Case**: Workflow cancellation, errors
**Example**: `fc_stop_workflow("dca_btc_001", reason="Market conditions changed")` → stops permanently

---

#### 11. `fc_get_workflow_status`

**Purpose**: Get current workflow execution status
**Parameters**:
- `workflow_id` (string): Workflow to check
**Returns**: Current state, progress, errors
**Use Case**: Monitoring, debugging
**Example**: `fc_get_workflow_status("dca_btc_001")` → "running, step 2/5"

---

#### 12. `fc_get_workflow_history`

**Purpose**: Get workflow execution history
**Parameters**:
- `workflow_id` (string): Workflow identifier
- `limit` (int, optional): Max executions to return
**Returns**: Past execution records
**Use Case**: Audit, performance analysis
**Example**: `fc_get_workflow_history("dca_btc_001", limit=10)` → last 10 executions

---

### Trading Operations (7 tools)

#### 13. `fc_execute_trade`

**Purpose**: Execute immediate trade (market or limit)
**Parameters**:
- `pair` (string): Trading pair
- `side` (string): "buy" or "sell"
- `amount` (float): Trade amount
- `order_type` (string): "market" or "limit"
- `price` (float, optional): Limit price
**Returns**: Trade execution result
**Use Case**: Manual trade execution
**Example**: `fc_execute_trade("XBTUSD", "buy", 0.0001, "market")` → executes buy

---

#### 14. `fc_schedule_trade`

**Purpose**: Schedule trade for future execution
**Parameters**:
- `pair` (string): Trading pair
- `side` (string): "buy" or "sell"
- `amount` (float): Trade amount
- `execution_time` (string): ISO timestamp
**Returns**: Scheduled trade ID
**Use Case**: Delayed execution, strategy automation
**Example**: `fc_schedule_trade("XBTUSD", "buy", 0.0001, "2026-01-26T12:00:00Z")` → scheduled

---

#### 15. `fc_cancel_scheduled_trade`

**Purpose**: Cancel scheduled trade before execution
**Parameters**:
- `trade_id` (string): Scheduled trade identifier
**Returns**: Confirmation
**Use Case**: Strategy adjustment, cancellation
**Example**: `fc_cancel_scheduled_trade("scheduled_001")` → cancels trade

---

#### 16. `fc_get_active_trades`

**Purpose**: List all active trades (pending, executing)
**Parameters**: None
**Returns**: Active trade list
**Use Case**: Portfolio monitoring, position tracking
**Example**: `fc_get_active_trades()` → current active trades

---

#### 17. `fc_get_trade_details`

**Purpose**: Get detailed information about specific trade
**Parameters**:
- `trade_id` (string): Trade identifier
**Returns**: Full trade details (execution, fills, fees)
**Use Case**: Trade verification, analysis
**Example**: `fc_get_trade_details("trade_20260126_001")` → full trade data

---

#### 18. `fc_simulate_trade`

**Purpose**: Simulate trade execution (paper mode)
**Parameters**:
- `pair` (string): Trading pair
- `side` (string): "buy" or "sell"
- `amount` (float): Trade amount
- `order_type` (string): "market" or "limit"
**Returns**: Simulated execution result (no real trade)
**Use Case**: Strategy testing, validation
**Example**: `fc_simulate_trade("XBTUSD", "buy", 0.001, "market")` → simulated buy

---

#### 19. `fc_get_trading_rules`

**Purpose**: Get current trading rules and limits
**Parameters**: None
**Returns**: MAX_ORDER_USD, DAILY_TRADE_LIMIT, circuit breakers
**Use Case**: Safety verification, compliance
**Example**: `fc_get_trading_rules()` → current limits and thresholds

---

### Risk Management (4 tools)

#### 20. `fc_check_circuit_breaker`

**Purpose**: Check if circuit breaker is triggered
**Parameters**: None
**Returns**: Circuit breaker status (active/inactive)
**Use Case**: Safety monitoring, trading halt detection
**Example**: `fc_check_circuit_breaker()` → "inactive, trading allowed"

---

#### 21. `fc_set_circuit_breaker`

**Purpose**: Manually trigger or reset circuit breaker
**Parameters**:
- `action` (string): "trigger" or "reset"
- `reason` (string): Reason for action
**Returns**: Confirmation
**Use Case**: Emergency halt, manual intervention
**Example**: `fc_set_circuit_breaker("trigger", reason="Market anomaly detected")` → halts trading

---

#### 22. `fc_get_risk_assessment`

**Purpose**: Get current portfolio risk assessment
**Parameters**:
- `strategy` (string, optional): Specific strategy to assess
**Returns**: Risk metrics (exposure, volatility, VAR)
**Use Case**: Risk monitoring, position sizing
**Example**: `fc_get_risk_assessment("dca_btc")` → risk analysis

---

#### 23. `fc_set_risk_limit`

**Purpose**: Update risk limit for strategy or portfolio
**Parameters**:
- `limit_type` (string): "max_position", "max_daily_loss", etc.
- `limit_value` (float): New limit value
**Returns**: Confirmation
**Use Case**: Risk parameter adjustment
**Example**: `fc_set_risk_limit("max_position", 1000.0)` → sets $1000 max position

---

### Integration & Configuration (4 tools)

#### 24. `fc_register_strategy`

**Purpose**: Register new trading strategy with SIL
**Parameters**:
- `strategy_name` (string): Strategy identifier
- `strategy_definition` (dict): Strategy logic and parameters
**Returns**: Strategy ID
**Use Case**: Strategy deployment, intelligence integration
**Example**: `fc_register_strategy("momentum_scalp", {...})` → new strategy registered

---

#### 25. `fc_list_strategies`

**Purpose**: List all registered strategies
**Parameters**:
- `status` (string, optional): Filter by status (active, inactive, testing)
**Returns**: Strategy list with metadata
**Use Case**: Strategy management, overview
**Example**: `fc_list_strategies(status="active")` → active strategies

---

#### 26. `fc_get_strategy_performance`

**Purpose**: Get performance metrics for strategy
**Parameters**:
- `strategy_id` (string): Strategy identifier
- `time_range` (string, optional): "1d", "7d", "30d", "all"
**Returns**: Performance statistics (P&L, win rate, Sharpe)
**Use Case**: Strategy evaluation, optimization
**Example**: `fc_get_strategy_performance("dca_btc", time_range="30d")` → monthly performance

---

#### 27. `fc_update_configuration`

**Purpose**: Update Fathom Commander configuration
**Parameters**:
- `config_key` (string): Configuration parameter
- `config_value` (any): New value
**Returns**: Confirmation
**Use Case**: System configuration, tuning
**Example**: `fc_update_configuration("paper_mode", True)` → enables paper mode

---

## Tool Usage Patterns

### Common Workflows

#### Session Startup
```python
# Automatic (session hooks)
get_dyad_state()  # Load current session context
memory_context("recent work")  # Load relevant memories

# Skills system (if domains active)
# Automatic skill context loading via Mem0
```

---

#### Trading Pipeline (When Phase 2 Complete)
```python
# Market analysis
ticker = fathom_get_ticker("XBTUSD")
spread = fathom_get_spread("XBTUSD")
orderbook = fathom_get_orderbook("XBTUSD", depth=10)

# Intelligence (SIL decision)
# [SIL tools not yet documented - Phase 2 work]

# Orchestration
workflow_id = fc_create_workflow("trade_btc", {...})
fc_start_workflow(workflow_id, {"amount_usd": 50})

# Execution (Fathom Phase 2 - not yet implemented)
# fc_execute_trade would trigger via workflow
```

---

#### Memory Exploration
```python
# Semantic search
results = memory_search("first trade", limit=5)

# Checkpoint search
checkpoints = checkpoint_search("infrastructure deployment")

# Hybrid search (complex queries)
results = hybrid_search_checkpoints(
    query="safety",
    keywords=["paper mode", "circuit breaker"],
    date_range={"start": "2026-01-01", "end": "2026-01-10"},
    limit=10
)
```

---

#### Health Monitoring
```python
# Check all systems
memory_health_check()
fathom_health_check()
fc_health_check()

# Get metrics
memory_stats()
fc_get_metrics("latency")
fc_get_system_status()
```

---

## Topology-Aware Thresholds (Semantic Search)

**Recommendation** (from Session 72-73 threshold tuning):

| Query Type | Threshold | Concept Density | Example Queries |
|------------|-----------|-----------------|-----------------|
| Relational | 0.45+ | Dense (0.50-0.60 similarity) | Partnership, symbiosis, trust |
| Operational | 0.25-0.40 | Medium (0.30-0.50 similarity) | Trading pipeline, deployment, infrastructure |
| Meta-cognitive | 0.15-0.20 | Sparse (0.15-0.30 similarity) | Narrative compression, learning patterns, architectural analysis |

**Usage**:
```python
# Relational query (tight clustering)
memory_search("dyadic partnership evolution", threshold=0.45)

# Operational query (medium spread)
memory_search("VPS deployment", threshold=0.30)

# Meta-cognitive query (sparse concepts)
memory_search("what did we learn about threshold tuning", threshold=0.20)
```

---

## Known Limitations

### Integration Gaps (85/0 Pattern)

**Trading Pipeline**:
- ✅ Fathom Phase 1: Can read market data
- ✅ FC: Can orchestrate workflows
- ✅ SIL: Can make decisions
- ❌ **No connection between systems** (integration workflow missing)

**Skills System**:
- ✅ Skills can route semantically (93.3% accuracy)
- ✅ Skills can load context from Mem0
- ❌ **Skills cannot invoke MCP tools** (binding framework missing)

**Orchestration**:
- ✅ n8n workflows operational (9 active)
- ✅ Cloudflare Workers pattern proven (mooncheck)
- ❌ **Migration incomplete** (9 trading workflows still on n8n)

---

### Phase 2 Blockers

**Fathom Phase 2-6**:
- Cannot place orders (read-only Phase 1)
- Cannot execute trades programmatically
- No websocket streaming (poll-based only)
- Estimated completion: 15-20 hours

**FC HTTP Gateway**:
- Deployed to VPS but integration not wired
- Requires Captain VPS access for validation
- Blocks n8n → Cloudflare Workers migration

**Skill-Tool Binding**:
- Design decision pending (direct invocation vs routing layer)
- Estimated implementation: 3-5 hours

---

## Tool Development Status

### Operational (52 tools)
- ✅ rhiz-mcp: 11/11 tools
- ✅ memory-mcp: 6/6 tools
- ✅ fathom Phase 1: 8/8 tools
- ✅ fathom-commander: 27/27 tools

### In Development (0 tools currently)
- Phase 2 component integration planning underway

### Planned Enhancements
1. **SIL MCP Tools** (Decision engine direct access)
   - Pattern recognition queries
   - Risk assessment API
   - Strategy selection
   - Estimated: 10-15 tools, 5-8 hours

2. **Fathom Phase 2** (Trading operations)
   - Place/cancel/modify orders
   - Position management
   - Estimated: 10-12 tools, 8-10 hours

3. **Skill-Tool Binding Framework** (Auto-invocation)
   - Skill → MCP tool routing
   - Automatic context passing
   - Result storage
   - Estimated: 3-5 hours

---

## Cross-References

**Component Documentation**:
- rhiz-mcp: `tools/rhiz-mcp/README.md`
- memory-mcp: `tools/memory-mcp/README.md`
- fathom: `domains/trading/fathom/ARCHITECTURE_v2.md`
- fathom-commander: `domains/trading/fathom_commander/MCP_COMPLIANCE_REPORT.md`

**Knowledge Base**:
- Memory system: `docs/knowledge_base/components/memory_system.md`
- Skills system: `docs/knowledge_base/components/skills_system.md`
- Trading components: `docs/knowledge_base/components/fathom_*.md`
- Integration gaps: `docs/knowledge_base/integrations/trading_pipeline.md`

**Deployment Guides**:
- VPS topology: `docs/knowledge_base/deployments/vps_topology.md`
- Local development: `docs/knowledge_base/deployments/local_development.md`
- Cloudflare Workers: `docs/knowledge_base/deployments/cloudflare_workers.md`

---

**End of MCP Tools Reference**

*Last Updated: 2026-01-25 (Session 74)*
*Total Tools: 52 (all operational)*
*Next Update: After Phase 2 completion (new tools added)*
