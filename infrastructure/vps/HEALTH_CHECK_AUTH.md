# Health Check Authentication

**Purpose**: Bypass Hostinger cloud-level firewall that blocks Cloudflare Worker IPs from accessing VPS health endpoints.

**Created**: 2026-01-12 (Session 43)
**Issue**: Cloudflare Workers receiving 403 Forbidden from VPS health checks
**Solution**: Shared API key authentication via `X-Health-Check-Key` header

---

## Architecture

Health checks require `X-Health-Check-Key` header to authenticate:

```
Cloudflare Worker (every 4h)
  ↓ X-Health-Check-Key: <shared-secret>
VPS Services (Gateway, SIL)
  ↓ Validates header
  ↓ Returns 200 OK (healthy) or 503 (unhealthy)
Worker logs to D1 database
```

**Why**: Hostinger cloud firewall blocks Cloudflare IP ranges by default. IP whitelisting is unreliable (Cloudflare IPs change). Authentication bypass is more robust.

---

## Configuration

### VPS Services

**Location**: `.env.production` (root of VPS deployment)

```bash
HEALTH_CHECK_KEY=rhiz-health-monitoring-2026
```

**Environment variable injection**: `docker-compose.trading.yml` passes to `sil-fastapi` and `fastapi-gateway` containers.

**Validation**: Both services will fail to start if `HEALTH_CHECK_KEY` is not set (explicit configuration enforcement).

### Cloudflare Worker

**Location**: `wrangler.toml` in `infrastructure/cloudflare/workers/daily-health-check/`

```toml
[vars]
HEALTH_CHECK_KEY = "rhiz-health-monitoring-2026"
```

**Validation**: Worker will throw error on first health check if `HEALTH_CHECK_KEY` not configured.

---

## Deployment

### Initial Setup

```bash
# 1. VPS Deployment
ssh root@72.62.81.128
cd /opt/rhiz_trading

# Verify .env.production has HEALTH_CHECK_KEY
grep HEALTH_CHECK_KEY .env.production

# Rebuild containers with new environment variable
docker-compose -f docker-compose.trading.yml build sil-fastapi fastapi-gateway

# Restart services
docker-compose -f docker-compose.trading.yml restart sil-fastapi fastapi-gateway

# Verify services started successfully
docker-compose -f docker-compose.trading.yml ps
docker-compose logs --tail=20 sil-fastapi fastapi-gateway | grep -i "error\|health"

# 2. Cloudflare Worker Deployment
cd infrastructure/cloudflare/workers/daily-health-check
wrangler deploy

# 3. Verification (5-10 minutes after deployment)
# Query D1 for latest health check results
wrangler d1 execute rhiz-trading --command \
  "SELECT * FROM health_checks ORDER BY timestamp DESC LIMIT 5"

# Expected: status='healthy' for all 3 services (sil, qdrant, gateway)
```

---

## Key Rotation

**When**: Every 90 days or if key is compromised

**Procedure**:

1. Generate new key: `openssl rand -hex 32`
2. Update VPS: Modify `.env.production`, rebuild/restart containers
3. Update Cloudflare: Modify `wrangler.toml`, run `wrangler deploy`
4. **Coordinate timing**: Both must use same key. Consider:
   - Update VPS first, wait 5 minutes for containers to restart
   - Update Worker second, deploy immediately
   - Verify health checks succeed within 4 hours (next cron run)

**Alternative (zero-downtime rotation)**:
- Temporarily accept both old and new keys in VPS code
- Deploy new key to Worker
- Wait 24 hours (6 cron cycles)
- Remove old key from VPS
- Rebuild/restart containers

---

## Security Posture

**Sensitivity Level**: Monitoring-grade (not execution-grade)

- **What this protects**: Health check endpoints from unauthorized access
- **What this doesn't protect**: Trading execution, Kraken API, internal service-to-service communication
- **Exposure**: Key visible in `wrangler.toml` (plaintext) and `.env.production` (plaintext)
- **Mitigation**: Both files are in `.gitignore`, not committed to repository
- **Risk if compromised**: Attacker can read health status, cannot execute trades or access sensitive data

**Why shared secret is acceptable**:
- Health checks return status only (no PII, no financial data)
- Alternative (mutual TLS) adds complexity without significant security gain
- Rotation procedure is straightforward
- Monitoring != Execution (different security requirements)

---

## Troubleshooting

### Worker logs "degraded" status

**Symptom**: `worker_executions` table shows `execution_status='degraded'`

**Check**:
```bash
# Get latest health check details
wrangler d1 execute rhiz-trading --command \
  "SELECT service, status, details FROM health_checks
   ORDER BY timestamp DESC LIMIT 3"
```

**Common causes**:
1. **403 Forbidden**: Key mismatch between Worker and VPS
   - Fix: Verify `wrangler.toml` and `.env.production` have identical key
2. **Connection timeout**: VPS containers not running
   - Fix: `docker-compose ps`, restart services
3. **500 Internal Server Error**: Service crashed
   - Fix: `docker-compose logs sil-fastapi` or `fastapi-gateway`, check error messages

### Services fail to start

**Symptom**: `docker-compose up` fails with "HEALTH_CHECK_KEY environment variable is required"

**Fix**: Ensure `.env.production` exists and contains `HEALTH_CHECK_KEY=<value>`

### Worker fails to deploy

**Symptom**: `wrangler deploy` succeeds but first cron execution logs "HEALTH_CHECK_KEY not configured"

**Fix**: Add `[vars]` section with `HEALTH_CHECK_KEY` to `wrangler.toml`

---

## Files Modified (Session 43)

- `infrastructure/vps/gateway_trading.py` - Added auth check to `/health` endpoint
- `domains/trading/strategic_intelligence/api.py` - Added auth check to `/health` endpoint
- `infrastructure/cloudflare/workers/daily-health-check/worker.js` - Send header in fetch
- `infrastructure/cloudflare/workers/daily-health-check/wrangler.toml` - Added env var
- `infrastructure/vps/docker-compose.trading.yml` - Pass env var to containers
- `infrastructure/vps/.env.production` - Added `HEALTH_CHECK_KEY`

---

**Revision**: 1.0
**Date**: 2026-01-12
**Author**: First Mate (Session 43)
**Status**: Ready for deployment
