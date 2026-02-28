---
component: sil-decision-engine
status: deployed
completion: 81.3%
grade: B+
deployed_at: session_42_20260111
depends_on:
  - qdrant: operational_on_disk_mode
  - docker: operational
  - vps_hostinger: operational
blocks:
  - trading_workflow_integration: no_connection_to_fc
  - real_trade_execution: awaiting_phase2_integration
integration_endpoints:
  - endpoint: fastapi_http
    port: 8000
    status: operational
    routes: ["/health", "/regime", "/strategy"]
related_components:
  - fathom_mcp_server: deployed_no_workflow_connection
  - fathom_commander: deployed_no_workflow_connection
  - memory_system: operational
failure_history:
  - approach: llm_based_self_rag
    failed_at: session_72
    reason: 2-5s_latency_unacceptable
    pivot: heuristic_self_rag
    outcome: sub_5ms_100_percent_accuracy
semantic_cluster: trading_domain
vector_density: medium
threshold_recommendation: 0.25-0.40
last_updated: 2026-01-25
---

# Strategic Intelligence Layer (SIL)

**Component Type**: Trading Decision Engine
**Protocol**: FastAPI HTTP + Python API
**Deployment**: VPS (Hostinger) + Docker containerized
**Status**: Deploy-ready (B+ grade, 81.3/100), awaiting workflow integration

---

## Purpose

SIL is the **intelligence layer** in Rhiz's three-tier trading architecture, providing:

1. **Regime classification** (volatility/trend/consolidation detection)
2. **Strategy selection** (momentum, mean reversion, volatility-based)
3. **Risk framework** (position sizing, exposure limits, stop-loss)
4. **Pattern recognition** (historical regime matching)
5. **Decision logging** (full TRACE_FE reasoning trails)

**Design Philosophy**: AI-augmented intelligence, not autonomous trading. SIL recommends strategies based on market conditions; Captain approves execution.

---

## Deployment Status

### Cloud Deployment (Session 42 - 2026-01-11)

✅ **Containerized**: Docker with FastAPI HTTP endpoints
✅ **Qdrant Integration**: On-disk mode (<200MB RAM vs 2GB server mode)
✅ **Resource Optimized**: 512MB-1GB RAM, 1-2 vCPU (4GB VPS allocation)
✅ **n8n Ready**: Workflow templates documented
✅ **Regime Validation**: Dec 2025 baseline established
✅ **Deployment Readiness**: B+ grade (81.3/100)

**Key Achievement**: Intelligence Federation deployment—three-layer architecture (Fathom/FC/SIL) now exists as separate containers, awaiting workflow connection.

---

## Architecture

### Decision Flow

```
Market Data (Fathom)
    ↓
Regime Classification (SIL)
    ↓
Strategy Selection (SIL)
    ↓
Risk Assessment (SIL)
    ↓
Recommendation + TRACE_FE
    ↓
[WORKFLOW MISSING - 85/0 Pattern]
    ↓
Orchestration (FC - awaiting connection)
    ↓
Execution (Fathom Phase 3 - not implemented)
```

### Core Components

**1. Regime Classifier**:
- Volatility detection (ATR-based)
- Trend identification (SMA crossovers)
- Consolidation recognition (Bollinger Bands)
- Output: {regime_type, confidence, characteristics}

**2. Strategy Selector**:
- Momentum strategies (trend-following)
- Mean reversion (range-bound)
- Volatility-based (breakout/breakdown)
- Output: {strategy, parameters, expected_edge}

**3. Risk Framework**:
- Position sizing (Kelly criterion, fixed fractional)
- Exposure limits (max 20% portfolio per trade)
- Stop-loss placement (ATR-based, regime-aware)
- Output: {position_size, stop_loss, take_profit}

**4. Memory Integration**:
- Historical regime matching (Qdrant similarity search)
- Pattern recognition (past outcomes for similar conditions)
- Decision logging (full reasoning trail)

---

## API Endpoints

### Health Check
```http
GET /health
```
Response:
```json
{
  "status": "operational",
  "components": {
    "qdrant": "connected",
    "regime_classifier": "ready",
    "strategy_selector": "ready",
    "risk_framework": "ready"
  },
  "memory_stats": {
    "vectors": 8234,
    "collections": ["regime_patterns", "strategy_outcomes"]
  }
}
```

### Regime Classification
```http
POST /regime
Content-Type: application/json

{
  "pair": "XXBTZUSD",
  "timeframe": "1h",
  "lookback_periods": 100
}
```

Response:
```json
{
  "regime": "high_volatility_bullish_trend",
  "confidence": 0.87,
  "characteristics": {
    "volatility_percentile": 89,
    "trend_strength": 0.72,
    "atr_14": 2834.5
  },
  "historical_matches": 12,
  "trace": "TRACE_FE reasoning trail..."
}
```

### Strategy Selection
```http
POST /strategy
Content-Type: application/json

{
  "regime": "high_volatility_bullish_trend",
  "portfolio_value": 50.68,
  "max_risk_pct": 2.0
}
```

Response:
```json
{
  "recommended_strategy": "momentum_breakout",
  "parameters": {
    "entry_trigger": "15min_close_above_resistance",
    "position_size_usd": 10.14,
    "stop_loss_pct": 3.5,
    "take_profit_pct": 8.0
  },
  "expected_edge": 0.23,
  "risk_reward_ratio": 2.29,
  "trace": "TRACE_FE reasoning trail..."
}
```

---

## Deployment Configuration

### Docker Compose (VPS)

```yaml
services:
  sil:
    build: ./domains/trading/strategic_intelligence
    container_name: rhiz_sil
    restart: unless-stopped
    ports:
      - "8000:8000"
    environment:
      - QDRANT_MODE=on_disk
      - QDRANT_PATH=/app/data/qdrant
      - SIL_CONFIG_DIR=/app/config
      - LOG_LEVEL=INFO
    volumes:
      - ./sil_data:/app/data
      - ./sil_config:/app/config
      - ./sil_logs:/app/logs
    networks:
      - rhiz_rhiz_network
    mem_limit: 1g
    mem_reservation: 512m
    cpus: 2
```

### Qdrant On-Disk Mode

**Memory Savings**:
- Server mode: 2GB+ RAM (requires separate Qdrant container)
- On-disk mode: <200MB RAM (embedded storage)

**Trade-offs**:
- On-disk: ~135MB storage, <10k vectors, single-node
- Server: Scalable, distributed, but requires 2GB+ RAM

**Configuration**: VPS has limited RAM (4GB shared across 9 containers), on-disk mode critical for resource efficiency.

---

## Integration Points

### Qdrant Collections

**regime_patterns** (3,421 vectors):
- Historical market regimes (BTC, ETH, ADA, SOL)
- Regime characteristics (volatility, trend, volume)
- Outcomes (strategy performance in each regime)

**strategy_outcomes** (4,813 vectors):
- Strategy execution results
- Risk/reward ratios
- Win rates, max drawdown, Sharpe ratios

**trading_signals** (0 vectors - awaiting Phase 2):
- Cross-system learning collection (Intelligence Federation)
- Designed for FC → SIL → Fathom signal sharing
- Not yet populated (no workflow integration)

---

## Deployment Readiness Assessment

**Date**: 2026-01-03
**Grade**: B+ (81.3/100)

### Component Scores

| Component | Score | Status |
|-----------|-------|--------|
| Regime Classifier | 88/100 | ✅ Production-ready |
| Strategy Selector | 85/100 | ✅ Production-ready |
| Risk Framework | 79/100 | ✅ Functional, needs tuning |
| Memory Integration | 75/100 | ⚠️ Qdrant working, needs more data |
| API Endpoints | 90/100 | ✅ Fully functional |
| Docker/Cloud | 87/100 | ✅ Deploy-ready |

### Critical Gaps

1. **No workflow integration** (85/0 pattern) - SIL deployed but not connected to FC/Fathom
2. **Limited historical data** - Only Dec 2025 regime baseline
3. **Strategy backtesting incomplete** - Need empirical validation
4. **Risk tuning needed** - Position sizing heuristics, not optimized

---

## Self-RAG Pattern (Session 72)

### Rejected: LLM-Based Self-RAG

**Approach**: Use LLM to decide whether to retrieve context for decision
**Reason**: 2-5s latency per decision unacceptable for trading
**Pivot**: Heuristic Self-RAG (skill-specific defaults + complexity keywords)
**Outcome**: <5ms decision time, 100% accuracy (5/5 test cases)

### Heuristic Rules

```python
def should_retrieve_memory(decision_type: str, query: str) -> bool:
    # Trading always retrieves (historical regime patterns critical)
    if decision_type == "regime_classification":
        return True

    if decision_type == "strategy_selection":
        return True

    # Complex queries retrieve
    if len(query.split()) > 15:
        return True

    complexity_keywords = ["analyze", "compare", "historical", "pattern"]
    if any(kw in query.lower() for kw in complexity_keywords):
        return True

    return False  # Default: no retrieval
```

**Learning**: YAGNI for LLM-based retrieval. Heuristics achieve same accuracy at orders of magnitude faster speed.

---

## Known Issues & Gaps

### Issue 1: 85/0 Pattern - No Workflow Integration
**Status**: OPEN (Blocker for Phase 2)
**Problem**: SIL deployed but not connected to FC/Fathom
**Impact**: Cannot execute automated trading strategies
**Resolution**: Phase 2 Component Integration (Session 75-76+)

### Issue 2: Limited Historical Data
**Status**: OPEN (Low Priority)
**Problem**: Only Dec 2025 baseline in regime_patterns
**Impact**: Pattern recognition limited
**Resolution**: Backfill 2024-2025 historical data

### Issue 3: Strategy Backtesting Incomplete
**Status**: OPEN (Medium Priority)
**Problem**: Strategy recommendations not empirically validated
**Impact**: Unknown edge, unproven performance
**Resolution**: Implement backtesting framework (Fathom Phase 6)

---

## Cross-References

**Source Code**:
- `domains/trading/strategic_intelligence/` - Main codebase
- `domains/trading/strategic_intelligence/DEPLOYMENT_READINESS.md` - B+ grade assessment

**Related Documentation**:
- `docs/architecture/trading_intelligence_federation_phase1.md` - Three-tier architecture
- `docs/research/semantic_routing_accuracy_optimization.md` - Self-RAG heuristics

**Integration Points**:
- `docs/knowledge_base/components/fathom_mcp_server.md` - Execution layer
- `docs/knowledge_base/components/fathom_commander.md` - Orchestration layer
- `docs/knowledge_base/integrations/trading_pipeline.md` - Integration gap documentation

**Checkpoints**:
- `core/memory/checkpoints/session_20260111_session_42_phase1_complete.yaml` - Intelligence Federation deployment

---

**End of Component Documentation**

*Last Updated: 2026-01-25 (Session 74)*
*Status: Deployed and operational, awaiting workflow integration*
