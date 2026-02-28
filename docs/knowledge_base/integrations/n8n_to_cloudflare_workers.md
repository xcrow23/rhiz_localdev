---
integration: n8n-to-cloudflare-workers
status: partial
completion: 33%
mooncheck_complete: true
trading_workflows_pending: true
gap_identified: session_40_20260111
components_exist: true
migration_started: true
pattern: code_first_architecture_vs_visual_workflows
blocks:
  - trading_workflow_migration: not_started_awaiting_fc_gateway
  - n8n_deprecation: pending_full_migration
required_components:
  - cloudflare_workers: operational_mooncheck
  - fastapi_gateway_vps: operational_mooncheck
  - n8n_hostinger: still_running_9_workflows
  - fathom_commander: deployed_not_migrated
semantic_cluster: infrastructure_domain
vector_density: medium
threshold_recommendation: 0.30-0.40
last_updated: 2026-01-25
---

# n8n to Cloudflare Workers Migration

**Integration Type**: Orchestration Layer Migration
**Status**: ⚠️ **PARTIAL** (mooncheck complete, trading pending)
**Rationale**: Code-first architecture vs visual workflow dependency

---

## Overview

This integration represents a **strategic architectural pivot** from n8n (visual workflow builder) to Cloudflare Workers (serverless code-first).

**Completed**: Mooncheck workflow migrated successfully (Session 40)

**Pending**: 9 trading workflows still running on n8n

**Timeline**:
- Dec 2025: n8n Hostinger instance discovered with 9 active workflows
- Jan 11, 2026: Migration plan documented, mooncheck migrated
- Jan 25, 2026: Trading workflows pending FC HTTP Gateway deployment

---

## Rationale for Migration

### Why Migrate from n8n?

**n8n Strengths**:
- Visual workflow builder (low-code/no-code)
- Extensive integrations (200+ services)
- Self-hosted (data control)
- Active development

**n8n Limitations for Rhiz**:
1. **Workflow as UI artifact**: JSON exports are massive, hard to review, version-unfriendly
2. **Testing difficulty**: Cannot unit test workflow logic easily
3. **Debugging complexity**: Black-box execution, limited error context
4. **Vendor lock-in**: Workflow logic tied to n8n platform
5. **Git workflow friction**: 3,000-line JSON files don't diff well

**Example**: Mooncheck workflow JSON export = 2,847 lines (mostly UI metadata)

### Why Cloudflare Workers?

**Cloudflare Workers Strengths**:
1. **Code-first**: Workflows as TypeScript/JavaScript code
2. **Git-friendly**: Clear diffs, reviewable, mergeable
3. **Testable**: Unit tests for workflow logic
4. **Serverless**: No server management, auto-scaling
5. **Edge execution**: Low latency globally
6. **Free tier**: 100,000 requests/day (sufficient for Rhiz)

**Trade-off**: Requires coding vs visual builder. Not an issue for AI-human dyad (coding is strength).

---

## Architecture Comparison

### n8n Architecture (Current - 9 Workflows)

```
┌─────────────────────────────────────────────────────┐
│          n8n Hostinger Instance                      │
│  ┌────────────────────────────────────────────────┐  │
│  │ Visual Workflow Builder (UI)                   │  │
│  │  ↓                                              │  │
│  │ Workflow JSON Export (2,000-4,000 lines)       │  │
│  │  ↓                                              │  │
│  │ n8n Execution Engine                           │  │
│  │  • Cron triggers                               │  │
│  │  • HTTP webhooks                               │  │
│  │  • Service integrations                        │  │
│  └────────────────────────────────────────────────┘  │
│          ↓ Calls                                     │
│  ┌────────────────────────────────────────────────┐  │
│  │ External Services                              │  │
│  │  • Fathom Commander (fathom.dreamthewilderness)│  │
│  │  • Kraken API                                  │  │
│  │  • Slack webhooks                              │  │
│  │  • Email (SendGrid)                            │  │
│  └────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────┘
```

### Cloudflare Workers Architecture (Target)

```
┌─────────────────────────────────────────────────────┐
│        Cloudflare Workers (Serverless)               │
│  ┌────────────────────────────────────────────────┐  │
│  │ Workflow Code (TypeScript)                     │  │
│  │  • mooncheck.ts (70 lines, readable)           │  │
│  │  • dca_buyer.ts (pending)                      │  │
│  │  • health_monitor.ts (pending)                 │  │
│  │  ↓                                              │  │
│  │ Cron Triggers (cron.yaml)                      │  │
│  │  • mooncheck: 0 8,20 * * * (8AM & 8PM CT)      │  │
│  │  ↓                                              │  │
│  │ Cloudflare Workers Runtime                     │  │
│  └────────────────────────────────────────────────┘  │
│          ↓ Calls                                     │
│  ┌────────────────────────────────────────────────┐  │
│  │ FastAPI Gateway (VPS - 95.217.51.24)          │  │
│  │  • /mooncheck/trigger (POST)                   │  │
│  │  • /mooncheck/status (GET)                     │  │
│  │  ↓                                              │  │
│  │ Backend Services                               │  │
│  │  • Kraken API                                  │  │
│  │  • Qdrant (memory logging)                     │  │
│  │  • Email notifications                         │  │
│  └────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────┘
```

**Key Difference**: Code (70 lines TS) vs JSON (2,847 lines). Code is reviewable, testable, git-friendly.

---

## Migration Status

### ✅ Complete: Mooncheck Workflow

**Original** (n8n):
- Trigger: Cron (daily 8AM CT)
- Action: Check lunar phase, post to #mooncheck Slack channel
- Export: 2,847-line JSON file
- Testing: Manual execution in n8n UI

**Migrated** (Cloudflare Workers):
- Code: `mooncheck.ts` (70 lines TypeScript)
- Trigger: Cron (`0 8,20 * * *` - 8AM & 8PM CT)
- Backend: FastAPI Gateway on VPS (95.217.51.24)
- Testing: Unit tests + integration tests
- Deployment: `wrangler deploy`

**Result**: ✅ SUCCESS - Mooncheck running on Cloudflare Workers since Jan 11

**Files**:
- `infrastructure/cloudflare/mooncheck/mooncheck.ts` - Worker code
- `infrastructure/cloudflare/mooncheck/wrangler.toml` - Cloudflare config
- `infrastructure/vps/mooncheck_gateway/main.py` - FastAPI backend

---

### ⏳ Pending: Trading Workflows (9 total)

**Active n8n Workflows** (still running):
1. **Rhiz Daily Health Monitor** (8AM CT)
   - Polls Fathom Commander heartbeat
   - Checks account balance
   - Logs to memory
   - Status: ⚠️ Pending migration

2. **Rhiz Weekly DCA Buyer** (Sunday 6PM CT, $15 BTC)
   - Automated DCA purchase
   - Safety checks
   - Captain approval if needed
   - Status: ⚠️ Blocked (FC HTTP Gateway not deployed)

3. **Rhiz Smart DCA**
   - Volatility-aware DCA adjustments
   - Status: ⚠️ Pending migration

4. **Rhiz Risk Monitor**
   - Continuous position size checks
   - Exposure monitoring
   - Status: ⚠️ Pending migration

5. **Rhiz Spread Opportunity Scanner**
   - Monitors for favorable spreads
   - Status: ⚠️ Pending migration

6. **Rhiz Portfolio Rebalancer**
   - Maintains target allocations
   - Status: ⚠️ Pending migration

7. **Rhiz Volatility Sentinel**
   - Halts trading during extreme volatility
   - Status: ⚠️ Pending migration

8. **Rhiz Daily Performance Journal**
   - End-of-day summary
   - Status: ⚠️ Pending migration

9. **Rhiz Weekly Strategy Review**
   - Sunday performance analysis
   - Status: ⚠️ Pending migration

**Blocker**: FC HTTP Gateway not deployed (requires Captain VPS access)

**Dependency**: Trading workflows cannot migrate until FC endpoints accessible

---

## Migration Blueprint (Trading Workflows)

### Example: Weekly DCA Buyer

**Current n8n Workflow** (conceptual flow):
```
Trigger: Cron (Sunday 6PM CT)
  ↓
HTTP Request: GET fathom.dreamthewilderness.com/tools/get_ticker
  ↓
If price < $100k:
  ↓
  HTTP Request: POST fathom.dreamthewilderness.com/tools/execute_trade
    {
      "pair": "XXBTZUSD",
      "side": "buy",
      "order_type": "market",
      "volume_usd": 15,
      "reasoning": "Weekly DCA"
    }
  ↓
  If order_value > $20:
    ↓
    Slack: Request Captain approval
    ↓
    Wait for Captain response
  ↓
  Execute trade
  ↓
  Log to Qdrant memory
  ↓
  Slack: Notify completion
```

**Migrated Cloudflare Worker** (planned):
```typescript
// weekly_dca_buyer.ts

export default {
  async scheduled(event, env, ctx) {
    // Step 1: Get current BTC price
    const ticker = await fetch(
      "http://95.217.51.24:8000/fathom/ticker?pair=XXBTZUSD"
    ).then(r => r.json());

    if (ticker.price > 100000) {
      await notifySlack("BTC > $100k, skipping DCA");
      return;
    }

    // Step 2: Calculate volume ($15 target)
    const volume = 15 / ticker.price;

    // Step 3: Submit trade to FC
    const trade = await fetch(
      "http://95.217.51.24:8000/fc/execute_trade",
      {
        method: "POST",
        body: JSON.stringify({
          pair: "XXBTZUSD",
          side: "buy",
          order_type: "market",
          volume: volume,
          reasoning: "Weekly DCA - Sunday 6PM CT",
          hypothesis: "Long-term BTC accumulation"
        })
      }
    ).then(r => r.json());

    // Step 4: Handle approval if needed (>$20)
    if (trade.requires_approval) {
      await requestCaptainApproval(trade);
      // Approval workflow handled by FC
    }

    // Step 5: Log outcome
    await logToMemory(trade);

    // Step 6: Notify
    await notifySlack(`DCA executed: ${volume} BTC @ ${ticker.price}`);
  }
};
```

**Advantages**:
- 70 lines readable TypeScript vs 3,000-line JSON
- Unit testable (`vitest weekly_dca_buyer.test.ts`)
- Git-friendly diffs
- Type-safe (TypeScript compiler catches errors)
- Debuggable (console.log works, stack traces clear)

---

## Migration Effort Estimate

### Per-Workflow Effort

**Low Complexity** (Health Monitor, Performance Journal):
- Estimate: 1-2 hours
- Reason: Simple HTTP requests, no trading logic

**Medium Complexity** (DCA workflows, Rebalancer):
- Estimate: 3-4 hours
- Reason: Trading logic, safety checks, approval workflows

**High Complexity** (Volatility Sentinel, Risk Monitor):
- Estimate: 5-6 hours
- Reason: Complex logic, circuit breaker integration, real-time monitoring

### Total Migration Estimate

| Workflow | Complexity | Estimate | Status |
|----------|-----------|----------|--------|
| Mooncheck | Low | 2h | ✅ Complete |
| Daily Health Monitor | Low | 2h | ⏳ Pending |
| Weekly DCA Buyer | Medium | 4h | ⏳ Blocked |
| Smart DCA | Medium | 4h | ⏳ Blocked |
| Portfolio Rebalancer | Medium | 3h | ⏳ Blocked |
| Daily Performance Journal | Low | 2h | ⏳ Pending |
| Weekly Strategy Review | Low | 2h | ⏳ Pending |
| Risk Monitor | High | 6h | ⏳ Blocked |
| Volatility Sentinel | High | 5h | ⏳ Blocked |
| Spread Scanner | Medium | 3h | ⏳ Blocked |

**Total**: ~33 hours (8-9 sessions)

**Critical Path**: FC HTTP Gateway deployment (unblocks 6/9 blocked workflows)

---

## Blockers to Full Migration

### Blocker 1: FC HTTP Gateway Not Deployed
**Impact**: Cannot migrate trading workflows (6/9 blocked)
**Resolution**: Captain VPS access session to configure FC endpoints
**Estimate**: 1 session

### Blocker 2: Token Verification Issue
**Status**: OPEN
**File**: `infrastructure/cloudflare/checkpoint-api/TOKEN_VERIFICATION_NEEDED.md`
**Impact**: Cloudflare Workers cannot authenticate to VPS endpoints
**Resolution**: Implement token-based auth for VPS FastAPI gateways
**Estimate**: 1 session

### Blocker 3: n8n Workflow Complexity Unknown
**Impact**: JSON exports difficult to reverse-engineer
**Resolution**: Manual inspection + testing of each workflow
**Estimate**: 1-2 hours per workflow

---

## Migration Priority

**Highest Priority** (Session 75-76):
1. **Deploy FC HTTP Gateway** (unblocks 6 workflows)
2. **Migrate Daily Health Monitor** (simple, high value)
3. **Migrate Weekly DCA Buyer** (validates trading workflow pattern)

**Medium Priority** (Session 77-79):
4. Migrate Smart DCA
5. Migrate Portfolio Rebalancer
6. Migrate Daily Performance Journal
7. Migrate Weekly Strategy Review

**Lower Priority** (Session 80+):
8. Migrate Risk Monitor (complex, needs integration testing)
9. Migrate Volatility Sentinel (complex, real-time monitoring)
10. Migrate Spread Scanner (lowest usage)

**Deferred**:
- n8n Hostinger instance shutdown (after all workflows migrated + validated)

---

## Architectural Learning

### Pattern: Code-First > Visual Workflows (for AI-Human Dyad)

**Discovery**: n8n excellent for non-technical users. Not optimal for AI-augmented development.

**Rationale**:
1. **AI can write code** (TypeScript workflow) faster than navigating UI
2. **Code is reviewable** (git diff shows logic changes)
3. **Code is testable** (unit tests, integration tests)
4. **Code is debuggable** (stack traces, console.log)
5. **Code is portable** (not tied to n8n platform)

**Alternative Considered**: Keep n8n for all workflows
- **Rejected**: JSON export friction, testing difficulty, debugging complexity

**Pivot**: Migrate to code-first Cloudflare Workers

**Outcome**: Mooncheck migration validated hypothesis (70 lines TS vs 2,847 lines JSON)

---

## Future State (Post-Migration)

### Target Architecture

```
Cloudflare Workers (Serverless Edge)
    ↓ HTTPS
VPS FastAPI Gateway (95.217.51.24)
    ↓ Internal Network
Fathom Commander + SIL + Fathom MCP
    ↓
Kraken API + Qdrant Memory
```

**Benefits**:
- **Serverless**: No server management, auto-scaling
- **Edge execution**: Low latency globally (Cloudflare has 300+ data centers)
- **Code-first**: Git-friendly, testable, reviewable
- **Free tier**: 100,000 req/day (sufficient for Rhiz)
- **Monitoring**: Cloudflare dashboard (request logs, errors, performance)

**Trade-offs**:
- **No visual builder**: Must write code (not an issue for dyad)
- **Cold starts**: ~10ms (negligible for cron workflows)
- **Platform lock-in**: Cloudflare Workers (mitigated by code portability—can run locally/VPS if needed)

---

## Cross-References

**Source Code**:
- `infrastructure/cloudflare/mooncheck/` - Completed migration
- `infrastructure/vps/mooncheck_gateway/` - FastAPI backend
- `domains/trading/fathom_commander/n8n/` - n8n workflow exports

**Architecture**:
- `docs/architecture/vps_infrastructure_topology.md` - VPS deployment with 9 n8n workflows
- `docs/knowledge_base/components/fathom_commander.md` - FC deployment details

**Migration Docs**:
- `infrastructure/cloudflare/N8N_CLOUDFLARE_MIGRATION_STATUS.md` - Migration tracking

**Checkpoints**:
- `core/memory/checkpoints/session_20260111_session_42_phase1_complete.yaml` - Migration plan documented

---

**End of Integration Documentation**

*Last Updated: 2026-01-25 (Session 74)*
*Status: Partial (mooncheck complete, trading pending FC Gateway)*
*Next Step: Deploy FC HTTP Gateway, migrate Daily Health Monitor*
