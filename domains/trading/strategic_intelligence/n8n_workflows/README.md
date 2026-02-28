# SIL n8n Workflows

This directory contains n8n workflow definitions for integrating the Strategic Intelligence Layer (SIL) with the Rhiz trading system.

## Workflows

### 1. SIL Health Monitor (`SIL_Health_Monitor.json`)
**Purpose:** Continuous health monitoring of the SIL API
**Trigger:** Every 5 minutes
**Endpoints Called:** `GET http://sil-api:8000/health`

**What it does:**
- Checks SIL API health status every 5 minutes
- Logs component status (market_context, strategy_selector, position_sizer, memory, learning)
- Alerts if any component becomes unhealthy

**Use case:** Production monitoring to ensure SIL is operational

---

### 2. SIL Strategy Selection (`SIL_Strategy_Selection.json`)
**Purpose:** Hourly strategy recommendations based on market conditions
**Trigger:** Every hour
**Endpoints Called:** `POST http://sil-api:8000/strategy/select`

**Workflow:**
1. **Build Market Context** - Prepares market regime, volatility, sentiment data
2. **Call SIL** - Requests strategy selection from SIL API
3. **Process Response** - Extracts strategy recommendation and position sizing
4. **Filter by Confidence** - Only acts on high-confidence strategies (>70%)
5. **Log Action** - Logs execution decision

**Output:**
- **High Confidence (≥70%):** Logs strategy for Hummingbot execution
- **Low Confidence (<70%):** Logs strategy for monitoring only

**Current Status:** Paper trading mode (logging only)
**Future:** Will send high-confidence strategies directly to Hummingbot API

---

## Installation

### Option 1: Manual Import (Recommended)
1. Log into n8n at Hostinger VPS
2. Click **"Add workflow"** → **"Import from File"**
3. Upload `SIL_Health_Monitor.json` and `SIL_Strategy_Selection.json`
4. Activate both workflows

### Option 2: API Import
```bash
# Set n8n API credentials
export N8N_API_KEY="your_api_key"
export N8N_HOST="http://72.62.81.128:5678"

# Import health monitor
curl -X POST "$N8N_HOST/api/v1/workflows" \
  -H "X-N8N-API-KEY: $N8N_API_KEY" \
  -H "Content-Type: application/json" \
  -d @SIL_Health_Monitor.json

# Import strategy selection
curl -X POST "$N8N_HOST/api/v1/workflows" \
  -H "X-N8N-API-KEY: $N8N_API_KEY" \
  -H "Content-Type: application/json" \
  -d @SIL_Strategy_Selection.json
```

---

## Verification

After importing, verify workflows are running:

```bash
# Check SIL health endpoint
curl http://72.62.81.128:8001/health

# Check n8n workflow executions
# (via n8n UI → Executions tab)
```

**Expected Results:**
- Health monitor should execute every 5 minutes
- Strategy selection should execute every hour
- Both should log to n8n execution history

---

## Integration with Hummingbot

### Current State (Phase 1)
- SIL provides strategy recommendations
- n8n logs recommendations (paper trading)
- No automatic execution

### Next Steps (Phase 2)
- Add Hummingbot API endpoint to workflow
- Send high-confidence strategies to Hummingbot
- Implement position entry/exit automation

### Future Enhancements (Phase 3)
- Real-time market data ingestion (WebSocket)
- Adaptive strategy selection based on performance feedback
- Multi-asset portfolio optimization

---

## Network Configuration

**Important:** These workflows assume SIL API is accessible at `http://sil-api:8000` within the Docker network.

Verify network connectivity:
```bash
# From n8n container
docker exec -it <n8n-container> curl http://sil-api:8000/health

# From VPS host
curl http://localhost:8001/health
```

If using external access:
- Replace `http://sil-api:8000` with `http://72.62.81.128:8001`
- Ensure firewall allows port 8001

---

## Troubleshooting

### Workflow Fails with "Could not resolve host"
**Solution:** Ensure both n8n and SIL are on the same Docker network (`rhiz-network`)

```bash
docker network inspect rhiz-network
# Should show both n8n and sil-api containers
```

### SIL Returns 500 Error
**Solution:** Check SIL logs for import errors or missing dependencies

```bash
docker compose -f docker-compose.cloud.yaml logs sil-api
```

### Strategy Selection Returns Low Confidence
**Expected behavior** - SIL is conservative by default. Adjust confidence threshold in workflow if needed.

---

## Monitoring

View workflow execution history in n8n:
1. Navigate to **Executions** tab
2. Filter by workflow name
3. Inspect execution logs for strategy recommendations

Key metrics to monitor:
- **Health check success rate** (should be 100%)
- **Strategy confidence distribution** (track average confidence over time)
- **API latency** (should be <500ms for strategy selection)

---

## Phase Progression

### ✅ Phase 1: SIL Deployment (Current)
- SIL API operational on VPS
- Health monitoring active
- Strategy selection tested
- Paper trading validation in progress

### 📋 Phase 2: Hummingbot Integration
- Connect n8n workflows to Hummingbot API
- Implement position entry automation
- Add risk management checks

### 🔮 Phase 3: Adaptive Learning
- Feedback loop from trade outcomes
- Performance-based strategy weighting
- Backtesting framework integration

---

## Support

For issues or questions:
- Check SIL logs: `docker compose -f docker-compose.cloud.yaml logs -f sil-api`
- Review n8n execution history
- Consult `DEPLOY_NOW.md` for deployment procedures
