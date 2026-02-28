# Fathom Commander Cloud Deployment Plan

**Target**: Hostinger KVM4 VPS (srv1206808.hstgr.cloud)
**Domain**: fathom.dreamthewilderness.com
**Status**: Design Phase
**Date**: 2026-01-03

---

## Objective

Deploy Fathom Commander from local MCP server to cloud HTTP service, enabling 24/7 operation and integration with 9 existing n8n workflows currently failing with 502 errors.

---

## Current State Assessment

### Local Fathom Commander (Source)
**Location**: `domains/trading/fathom_commander/`
**Type**: MCP Server (stdio protocol)
**Status**: Fixed and operational (5 critical issues resolved 2026-01-03)
**Entry Point**: `server.py`
**Tools**: 27 MCP tools across 5 categories
**Safety**: Paper mode default, approval workflow for >$20 trades

### Cloud Target (Destination)
**Infrastructure**: Hostinger KVM4 (16GB RAM, root access)
**Current Services**: n8n (operational)
**Expected Endpoint**: https://fathom.dreamthewilderness.com
**DNS**: Configured via Cloudflare (104.21.19.205, 172.67.190.47)
**Current Status**: 502 Bad Gateway (no origin server)

### Dependent Systems
**n8n Workflows**: 9 active workflows expecting Fathom Commander endpoints
**Integration Points**: All workflows use HTTP requests to `fathom.dreamthewilderness.com`
**Critical Workflows**:
- Weekly DCA Buyer: $15 BTC weekly (LIVE TRADING once deployed)
- Daily Health Monitor: System status checks
- Risk Monitor: Portfolio safety checks

---

## Architecture Transformation

### From: MCP Server (Local)
```python
# server.py
async def main():
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(server_name="fathom-commander")
        )
```
**Protocol**: stdio (Claude Code ↔ MCP)
**Exposure**: Local only, requires Claude Code session
**Transport**: Standard input/output streams

### To: HTTP REST API (Cloud)
```python
# app.py (new)
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

app = FastAPI(title="Fathom Commander API")

@app.get("/")
async def status():
    return state.get_status()

@app.get("/portfolio/summary")
async def portfolio_summary():
    return state.get_portfolio_summary()

@app.post("/trade/execute")
async def execute_trade(trade: TradeRequest):
    return await execute_trade_tool(trade)

# ... 27 endpoints matching current MCP tools
```
**Protocol**: HTTP/REST (n8n ↔ API)
**Exposure**: Public HTTPS via Cloudflare
**Transport**: JSON over HTTP

---

## Migration Strategy

### Phase 1: HTTP API Development (Local)
**Duration**: 1-2 hours
**Tasks**:
1. Create `app.py` with FastAPI framework
2. Map 27 MCP tools to REST endpoints:
   - GET `/` - heartbeat, status_report
   - GET `/market/ticker` - get_ticker
   - GET `/market/ohlc` - get_ohlc
   - GET `/portfolio/summary` - get_summary
   - POST `/trade/execute` - execute_trade
   - POST `/trade/approve` - approve_order
   - etc.
3. Preserve all business logic from MCP tools
4. Add authentication middleware (API key from .env)
5. Test locally: `uvicorn app:app --reload --port 8080`

### Phase 2: Containerization
**Duration**: 30 minutes
**Tasks**:
1. Create `Dockerfile`:
```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8080

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"]
```

2. Create `docker-compose.yml`:
```yaml
version: '3.8'

services:
  fathom-commander:
    build: .
    container_name: fathom_commander
    restart: unless-stopped
    ports:
      - "127.0.0.1:8080:8080"
    environment:
      - KRAKEN_API_KEY=${KRAKEN_API_KEY}
      - KRAKEN_SECRET_KEY=${KRAKEN_SECRET_KEY}
      - MODE=paper
      - MAX_ORDER_USD=50
      - APPROVAL_THRESHOLD_USD=20
    volumes:
      - ./state:/app/state
      - ./logs:/app/logs
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/"]
      interval: 30s
      timeout: 10s
      retries: 3
```

3. Test: `docker compose up` and verify endpoints work

### Phase 3: Deployment to Hostinger
**Duration**: 1 hour
**Tasks**:
1. SCP codebase to Hostinger:
   ```bash
   scp -r domains/trading/fathom_commander/ root@srv1206808.hstgr.cloud:/opt/fathom/
   ```

2. SSH to Hostinger and build:
   ```bash
   ssh root@srv1206808.hstgr.cloud
   cd /opt/fathom
   docker compose build
   docker compose up -d
   ```

3. Verify container running:
   ```bash
   docker ps | grep fathom
   curl http://localhost:8080/
   ```

### Phase 4: Cloudflare Configuration
**Duration**: 30 minutes
**Tasks**:
1. Log in to Cloudflare account
2. Navigate to DNS settings for dreamthewilderness.com
3. Update A record for `fathom` subdomain:
   - Type: A
   - Name: fathom
   - Content: 72.62.81.128 (Hostinger VPS IP)
   - Proxy: Enabled (orange cloud)
   - TTL: Auto

4. Configure origin server in Cloudflare:
   - SSL/TLS mode: Full (strict) or Flexible
   - Origin Server: 72.62.81.128:8080
   - Protocol: HTTP (Cloudflare handles HTTPS termination)

5. Test: `curl https://fathom.dreamthewilderness.com/`
   - Should return: `{"status": "alive", "mode": "paper", ...}`

### Phase 5: n8n Workflow Validation
**Duration**: 1 hour
**Tasks**:
1. Manually trigger each workflow in n8n UI:
   - Daily Health Monitor
   - Weekly DCA Buyer (CAREFUL - verify paper mode first!)
   - Smart DCA
   - Risk Monitor
   - Spread Scanner
   - Portfolio Rebalancer
   - Volatility Sentinel
   - Daily Performance Journal
   - Weekly Strategy Review

2. Check workflow execution logs for errors
3. Verify no live trades execute (paper mode safety check)
4. Confirm all HTTP requests return 200 (not 502)

### Phase 6: Heartbeat Deployment
**Duration**: 30 minutes
**Tasks**:
1. Update `heartbeat_workflow.json` with correct URL:
   ```json
   "url": "https://fathom.dreamthewilderness.com/"
   ```

2. Upload to cloud n8n via API:
   ```bash
   curl -X POST \
     -H "X-N8N-API-KEY: $N8N_API_KEY" \
     -H "Content-Type: application/json" \
     -d @heartbeat_workflow.json \
     https://n8n.srv1206808.hstgr.cloud/api/v1/workflows
   ```

3. Activate workflow in n8n UI
4. Monitor for 60s intervals, verify logs show successful heartbeats

---

## Endpoint Mapping (27 Tools → REST)

### Heartbeat (1)
- `GET /` - heartbeat → `{"status": "alive", "uptime": 12345, ...}`
- `GET /status` - status_report → `{"trading_halted": false, ...}`

### Market (4)
- `GET /market/ticker?pair=XXBTZUSD` - get_ticker
- `GET /market/ohlc?pair=XXBTZUSD&interval=1h` - get_ohlc
- `GET /market/orderbook?pair=XXBTZUSD` - get_orderbook
- `GET /market/analyze?pair=XXBTZUSD` - analyze

### Execution (8)
- `POST /trade/execute` - execute_trade
  - Body: `{"action": "buy", "symbol": "BTC/USD", "amount_usd": 15, "reason": "DCA"}`
- `POST /trade/validate` - validate_trade
- `POST /trade/approve` - approve_order
- `POST /trade/reject` - reject_order
- `DELETE /trade/{order_id}` - cancel_order
- `GET /trade/open` - get_open_orders
- `GET /trade/history` - get_trade_history
- `GET /trade/fees` - estimate_fees

### Portfolio (6)
- `GET /portfolio/balance` - get_balance
- `GET /portfolio/holdings` - get_holdings
- `GET /portfolio/summary` - get_summary
- `GET /portfolio/performance` - get_performance
- `POST /portfolio/track` - track_position
- `POST /portfolio/close` - close_position

### Strategy (5)
- `GET /strategy/list` - list_strategies
- `POST /strategy/activate` - activate_strategy
- `POST /strategy/deactivate` - deactivate_strategy
- `GET /strategy/signal` - get_signal
- `GET /strategy/exits` - check_exits

### Alerts (3)
- `POST /alerts/send` - send_alert
- `GET /alerts/status` - alert_status
- `GET /alerts/history` - alert_history

---

## Safety Mechanisms

### 1. Paper Mode Enforcement
```python
# config.yaml
mode: paper  # NEVER change to 'live' without explicit Captain approval

# app.py
@app.post("/trade/execute")
async def execute_trade(trade: TradeRequest):
    if config.mode != "paper":
        raise HTTPException(403, "Live trading disabled for safety")
    # ... execute in paper mode
```

### 2. Approval Workflow
```python
@app.post("/trade/execute")
async def execute_trade(trade: TradeRequest):
    if trade.amount_usd > APPROVAL_THRESHOLD:
        # Hold in pending state, send alert
        await send_alert(f"Trade pending approval: {trade}")
        return {"status": "pending_approval", "order_id": "..."}
    # ... execute directly if under threshold
```

### 3. Circuit Breaker
```python
@app.get("/")
async def status():
    if state.daily_loss_pct > 10:
        state.trading_halted = True
        state.halt_reason = "Daily loss exceeds 10%"

    return {
        "status": "alive",
        "trading_halted": state.trading_halted,
        "halt_reason": state.halt_reason
    }
```

### 4. Rate Limiting
```python
from slowapi import Limiter
limiter = Limiter(key_func=get_remote_address)

@app.post("/trade/execute")
@limiter.limit("10/day")  # Max 10 trades per day
async def execute_trade(trade: TradeRequest):
    # ...
```

### 5. Authentication
```python
from fastapi import Security, HTTPException
from fastapi.security.api_key import APIKeyHeader

api_key_header = APIKeyHeader(name="X-API-Key")

async def verify_api_key(api_key: str = Security(api_key_header)):
    if api_key != os.getenv("FATHOM_API_KEY"):
        raise HTTPException(403, "Invalid API key")
    return api_key

@app.post("/trade/execute", dependencies=[Depends(verify_api_key)])
async def execute_trade(trade: TradeRequest):
    # Only reachable with valid API key
```

---

## Rollback Plan

If deployment fails or causes issues:

1. **Stop container**:
   ```bash
   ssh root@srv1206808.hstgr.cloud
   cd /opt/fathom
   docker compose down
   ```

2. **Deactivate workflows in n8n** (prevent failed executions)
   - Via n8n UI: Workflows → Deactivate all Rhiz workflows

3. **Revert Cloudflare DNS** (if needed)
   - Remove A record for fathom subdomain

4. **Restore local MCP testing**
   - Continue development locally until issues resolved

---

## Success Criteria

✅ Fathom Commander responds at https://fathom.dreamthewilderness.com/
✅ All 27 endpoints return valid JSON (not 502)
✅ Paper mode confirmed active (no live Kraken trades)
✅ All 9 n8n workflows execute without HTTP errors
✅ Heartbeat workflow polls every 60s successfully
✅ Weekly DCA workflow dry-run completes (no actual BTC purchase)
✅ Circuit breaker triggers correctly on test conditions
✅ Approval workflow holds >$20 trades pending

---

## Monitoring Post-Deployment

### First 24 Hours
- [ ] Check n8n execution logs hourly
- [ ] Monitor Fathom Commander logs for errors
- [ ] Verify no live Kraken API calls (paper mode)
- [ ] Confirm heartbeat steady at 60s intervals

### First Week
- [ ] Daily review of workflow executions
- [ ] Check for any 502/500 errors
- [ ] Validate circuit breaker behavior
- [ ] Review portfolio summary accuracy

### First Month
- [ ] Weekly performance journal review
- [ ] Strategy review workflow outputs
- [ ] Assess if paper mode ready for small live trades
- [ ] Captain approval required before ANY live trading

---

## Open Questions

1. **API Authentication**: Should n8n workflows use API key header or rely on Cloudflare Access for auth?
2. **Logging**: Send logs to cloud logging service (e.g., Grafana Cloud) or keep local?
3. **Alerting**: Slack vs. email for approval workflow notifications?
4. **Backup**: Snapshot state/ directory daily to external storage?
5. **Scaling**: If we add more trading pairs, does current VPS have capacity?

---

## Cost Estimate

**Development Time**: 5-6 hours (First Mate autonomous)
**Infrastructure Cost**: $0 (using existing Hostinger VPS)
**Cloudflare Cost**: $0 (free tier sufficient)
**Risk**: Low (paper mode, approval workflow, circuit breaker)

---

## Dependencies

**Must Have Before Deployment**:
1. ✅ Fathom Commander code fixed (DONE 2026-01-03)
2. ⚠ Cloudflare account access (Captain to provide OR delegate)
3. ⚠ FATHOM_API_KEY generated (for n8n → Fathom auth)
4. ✅ Hostinger SSH access (credentials in .env)
5. ⏸ Captain approval to proceed with deployment

**Nice to Have**:
- Slack webhook for alerts (optional, can use console logs initially)
- Monitoring dashboard (defer to Phase 2)
- Automated tests (can develop post-deployment)

---

**Next Step**: Await Captain's approval, then begin Phase 1 (HTTP API development).

**Estimated Timeline**: 1 day from approval to operational (5-6 hours work, spread across testing/validation)

**Deployment Window**: Recommend off-hours (e.g., Saturday morning) to minimize disruption if issues arise.
