# Fathom Commander HTTP Gateway - Deployment Guide

## Overview

This guide walks through deploying the FC HTTP Gateway on the VPS. The gateway provides a REST API interface to Fathom Commander, enabling Cloudflare Workers to execute trades programmatically.

## Architecture

```
Cloudflare Worker (weekly-dca)
    → VPS:8767 (FC HTTP Gateway)
    → Kraken API (execution)
    → Qdrant (memory/logging)
```

## Prerequisites

- VPS SSH access (root@72.62.81.128)
- Kraken API credentials in `.env` file
- Docker and Docker Compose installed
- `rhiz_network` Docker network exists
- Qdrant container running on port 6333

## Deployment Steps

### Step 1: Upload Files to VPS

From your local machine, sync the latest trading infrastructure:

```bash
# Option A: Via Git (recommended if repo is on VPS)
ssh root@72.62.81.128
cd /root/rhiz
git pull origin main

# Option B: Via SCP
scp -r infrastructure/vps/docker-compose.trading.yml root@72.62.81.128:/root/rhiz/infrastructure/vps/
scp -r domains/trading/fathom_commander/ root@72.62.81.128:/root/rhiz/domains/trading/
```

### Step 2: Verify Environment Variables

Ensure `.env` file exists at `/root/rhiz/.env` with:

```bash
# Kraken API Credentials
KRAKEN_API_KEY=your_api_key_here
KRAKEN_SECRET_KEY=your_secret_key_here

# FC HTTP Gateway Authentication
# Generate with: openssl rand -hex 32
FC_HTTP_API_KEY=your_secure_api_key_here

# Health Check Authentication (for Cloudflare Workers)
HEALTH_CHECK_KEY=rhiz-health-monitoring-2026
```

**Generate API Key** (if not already done):
```bash
ssh root@72.62.81.128
cd /root/rhiz

# Generate secure 64-character API key
openssl rand -hex 32

# Add to .env file
echo "FC_HTTP_API_KEY=<generated_key>" >> .env
```

**Verify `.env` is complete**:
```bash
cat /root/rhiz/.env
# Should show all required keys including FC_HTTP_API_KEY
```

### Step 3: Verify Docker Network

```bash
ssh root@72.62.81.128

# Check if rhiz_network exists
docker network ls | grep rhiz_network

# If not, create it
docker network create rhiz_network

# Verify Qdrant is running
docker ps | grep qdrant
# Should show: rhiz_qdrant or qdrant container on ports 6333/6334
```

### Step 4: Build and Deploy FC HTTP Gateway

```bash
ssh root@72.62.81.128
cd /root/rhiz

# Build only the FC HTTP Gateway service
docker-compose -f infrastructure/vps/docker-compose.trading.yml build fc-http-gateway

# Start FC HTTP Gateway (and dependencies if not running)
docker-compose -f infrastructure/vps/docker-compose.trading.yml up -d fc-http-gateway

# Check logs
docker logs fc-http-gateway -f

# Expected output:
# [timestamp] INFO: Starting FC HTTP Gateway on port 8767
# [timestamp] INFO: Connected to Qdrant at http://qdrant:6333
# [timestamp] INFO: Kraken credentials loaded
# [timestamp] INFO: Operating in PAPER mode
```

### Step 5: Verify FC Gateway is Running

```bash
# From VPS
curl http://localhost:8767/heartbeat

# Expected response:
# {
#   "status": "alive",
#   "uptime": "0h 1m 23s",
#   "mode": "paper",
#   "positions": { "count": 0, "pairs": [] },
#   "pending_approvals": { "count": 0, "ids": [] },
#   "today": {
#     "trades": 0,
#     "trades_remaining": 10,
#     "pnl": 0.0,
#     "loss_current": 0.0
#   },
#   "strategy": "momentum_basic",
#   "trading_halted": false,
#   "halt_reason": "",
#   "health": {
#     "kraken_auth": "ok",
#     "memory": "ok",
#     "errors": 0
#   },
#   "timestamp": "2026-01-17T..."
# }
```

### Step 6: Test Trade Execution (Paper Mode)

**Important**: All requests now require API key authentication via `Authorization` header.

```bash
# Get your API key from .env
FC_API_KEY=$(grep FC_HTTP_API_KEY /root/rhiz/.env | cut -d'=' -f2)

# Test USD-based trade endpoint (safe in paper mode)
curl -X POST http://localhost:8767/trade/execute \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $FC_API_KEY" \
  -d '{
    "action": "buy",
    "symbol": "BTC/USD",
    "amount_usd": 15.00,
    "reason": "Test purchase via FC HTTP Gateway"
  }'

# Expected response (paper mode - no real trade):
# {
#   "success": true,
#   "mode": "paper",
#   "message": "Trade simulated in paper mode",
#   "trade_details": {
#     "pair": "XXBTZUSD",
#     "side": "buy",
#     "volume": 0.000156,
#     "price": 96000.0,
#     "total_usd": 15.00,
#     "fee_usd": 0.05
#   },
#   "approval_required": false,
#   "timestamp": "2026-01-17T..."
# }
```

### Step 7: Verify from Cloudflare Workers

The weekly-dca worker should now be able to reach the gateway:

```bash
# From Cloudflare Worker:
# POST http://72.62.81.128:8767/trade/execute
```

Check worker logs in Cloudflare dashboard to verify successful connection.

## Service Management

### View Logs

```bash
# Real-time logs
docker logs fc-http-gateway -f

# Last 100 lines
docker logs fc-http-gateway --tail 100

# Logs with timestamps
docker logs fc-http-gateway -t
```

### Restart Service

```bash
# Restart just FC HTTP Gateway
docker restart fc-http-gateway

# Or rebuild and restart
cd /root/rhiz
docker-compose -f infrastructure/vps/docker-compose.trading.yml up -d --build fc-http-gateway
```

### Stop Service

```bash
docker stop fc-http-gateway

# Or via compose
docker-compose -f infrastructure/vps/docker-compose.trading.yml stop fc-http-gateway
```

### Check Status

```bash
# Container status
docker ps | grep fc-http-gateway

# Health check
docker inspect fc-http-gateway | grep -A 5 Health

# Port bindings
docker port fc-http-gateway
```

## Available Endpoints

All endpoints available at `http://72.62.81.128:8767/`:

### Health & Status
- `GET /heartbeat` or `GET /` - System health and status

### Market Data
- `GET /market/ticker?pairs=XXBTZUSD` - Current prices
- `GET /market/ohlc?pair=XXBTZUSD&interval=5` - OHLCV data
- `GET /market/orderbook?pair=XXBTZUSD&depth=10` - Order book

### Portfolio
- `GET /portfolio/balance` - Account balances
- `GET /portfolio/holdings` - Current holdings with USD values
- `GET /portfolio/summary` - Portfolio overview
- `GET /portfolio/performance` - P&L metrics

### Trading
- `POST /trade/execute` - Execute trade (USD-based)
  ```json
  {
    "action": "buy" | "sell",
    "symbol": "BTC/USD" | "ETH/USD",
    "amount_usd": 15.00,
    "reason": "Weekly DCA"
  }
  ```

- `POST /execute` - Direct trade execution (advanced)
- `POST /validate` - Validate trade without executing
- `POST /approve` - Approve pending order
- `POST /reject` - Reject pending order
- `POST /cancel` - Cancel open order

### Strategy
- `GET /strategy/list` - Available strategies
- `POST /strategy/activate` - Activate strategy
- `GET /strategy/signal?pair=XXBTZUSD` - Get trading signal

### Orders
- `GET /orders/open` - Open orders
- `GET /orders/history` - Trade history

### State Management
- `POST /mode` - Set operational mode (paper/live/disabled)
- `GET /state/summary` - Commander state

### Alerts
- `POST /alert` - Send alert
- `GET /alerts/history` - Alert log
- `GET /alerts/status` - Alert system status

## Configuration

FC HTTP Gateway shares configuration with FC MCP Server via environment variables and `config.yaml`:

**Environment Variables**:
- `FC_MODE` - Operating mode (paper, live, disabled) - default: paper
- `FC_MAX_ORDER_USD` - Maximum order size - default: $50
- `FC_APPROVAL_THRESHOLD_USD` - Require approval above - default: $20
- `FC_MAX_DAILY_TRADES` - Daily trade limit - default: 10
- `FC_DAILY_LOSS_LIMIT` - Stop trading if down - default: $25
- `FC_HTTP_PORT` - HTTP port - default: 8767
- `KRAKEN_API_KEY` - Kraken API key (required)
- `KRAKEN_SECRET_KEY` - Kraken secret key (required)
- `QDRANT_URL` - Qdrant connection - default: http://qdrant:6333

**Shared State**:
FC HTTP Gateway and FC MCP Server share the same state volume (`fc-state:/app/state`), ensuring consistency across both interfaces.

## Security

### API Key Authentication

All HTTP endpoints require API key authentication via the `Authorization` header:

```bash
Authorization: Bearer <your_api_key>
```

**Configuration**:
- Set `FC_HTTP_API_KEY` in `.env` file on VPS
- Generate key with: `openssl rand -hex 32`
- Update Cloudflare Workers with API key

**Behavior**:
- If `FC_HTTP_API_KEY` is not set, gateway allows all requests (insecure - only for local testing)
- If set, all requests must include valid `Authorization: Bearer <key>` header
- Invalid/missing auth returns `401 Unauthorized`

**Example**:
```bash
# From Cloudflare Worker
const response = await fetch('http://72.62.81.128:8767/trade/execute', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${env.FC_HTTP_API_KEY}`
  },
  body: JSON.stringify({...})
});
```

### Rate Limiting

Trade endpoints (`/trade/execute`, `/execute`) are rate-limited to prevent runaway trading:

**Limits**:
- Capacity: 10 requests per minute
- Refill rate: 1 token per 6 seconds
- Token bucket algorithm (allows bursts up to capacity)

**Behavior**:
- Each successful trade request consumes 1 token
- Tokens refill continuously at 1/6 tokens per second
- Exceeding limit returns `429 Too Many Requests`
- Error message includes retry-after time

**Example Error**:
```json
{
  "success": false,
  "error": "Rate limit exceeded",
  "message": "Rate limit exceeded. Try again in 18 seconds."
}
```

**Why this matters**: Even if Cloudflare Worker is compromised, rate limiting prevents attackers from draining funds through rapid trades. Limit is independent of `FC_MAX_DAILY_TRADES` state check.

### Network Exposure

Port 8767 is bound to `127.0.0.1` (localhost only) - not exposed to public internet.

**Access Methods**:
1. **Unified Gateway** (port 8080): Proxies to fc-http-gateway internally
2. **Cloudflare Tunnel**: Secure tunnel from Workers to VPS localhost
3. **Direct SSH**: `ssh -L 8767:localhost:8767 root@72.62.81.128`

**Why this matters**: Binding to localhost prevents unauthorized external access. Only authenticated services on VPS or via Cloudflare Tunnel can reach the gateway.

## Troubleshooting

### Gateway won't start

```bash
# Check container logs
docker logs fc-http-gateway

# Common issues:
# 1. Missing Kraken credentials
docker exec fc-http-gateway env | grep KRAKEN

# 2. Qdrant not running
docker ps | grep qdrant

# 3. Port 8767 already in use
sudo lsof -i :8767
```

### Kraken auth fails

```bash
# Verify credentials are loaded
docker exec fc-http-gateway python -c "
import os
print('API Key loaded:', bool(os.getenv('KRAKEN_API_KEY')))
print('Secret loaded:', bool(os.getenv('KRAKEN_SECRET_KEY')))
"

# Test Kraken connection
curl http://localhost:8767/market/ticker?pairs=XXBTZUSD
```

### Workers can't reach gateway

```bash
# Check firewall (Hostinger may block external access to 8767)
sudo ufw status

# If blocked, allow port 8767
sudo ufw allow 8767/tcp

# Or use Cloudflare Tunnel (more secure)
# See: infrastructure/vps/CLOUDFLARE_TUNNEL_SETUP.md
```

### State file corruption

```bash
# Backup current state
docker exec fc-http-gateway cp /app/state/commander_state.json /app/state/commander_state.backup.json

# Reset state (last resort)
docker exec fc-http-gateway rm /app/state/commander_state.json
docker restart fc-http-gateway
```

## Switching from Paper to Live Mode

**WARNING**: Only switch to live mode when:
1. Thoroughly tested in paper mode
2. Captain has reviewed and approved trading strategy
3. Daily loss limits and safety checks configured
4. Small initial capital allocated ($50-100)

```bash
# Update docker-compose.trading.yml
# Change: FC_MODE=paper → FC_MODE=live

# Rebuild and restart
cd /root/rhiz
docker-compose -f infrastructure/vps/docker-compose.trading.yml up -d --build fc-http-gateway

# Verify mode change
curl http://localhost:8767/heartbeat | grep mode
# Should show: "mode": "live"
```

## Security Notes

1. **API Credentials**: Never commit `.env` to git
2. **Port Exposure**: Port 8767 is exposed on VPS - consider Cloudflare Tunnel for production
3. **Paper Mode**: Always test thoroughly in paper mode before going live
4. **Daily Limits**: Safety limits prevent runaway losses
5. **Approval Workflow**: Orders > $20 require Captain approval

## Next Steps

1. ✅ Deploy FC HTTP Gateway (this guide)
2. Verify weekly-dca worker connects successfully
3. Monitor first automated DCA purchase (Monday 10pm UTC)
4. Implement SIL `refresh_regimes` endpoint (T3)
5. Enable learning feedback loop
6. Consider switching to live mode (with Captain approval)

## Related Documentation

- `domains/trading/fathom_commander/MCP_COMPLIANCE_REPORT.md` - FC tool reference
- `infrastructure/cloudflare/workers/weekly-dca/worker.js` - DCA worker source
- `infrastructure/vps/CONNECTION_PATTERNS.md` - Service topology
- `infrastructure/vps/HEALTH_CHECK_AUTH.md` - Health check authentication
