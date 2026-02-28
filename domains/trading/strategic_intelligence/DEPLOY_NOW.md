# SIL Cloud Deployment - Execute Now! 🚀

**Status:** AUTHORIZED ✓
**Target:** Hostinger VPS (72.62.81.128)
**Mode:** Cloud Production Deployment
**Date:** 2026-01-03

---

## Quick Start (Windows PowerShell)

### Option 1: Automated Deployment (Recommended)

If you have SSH configured to VPS:

```powershell
# Navigate to SIL directory
cd C:\Users\dread\documents\rhiz_localdev\domains\trading\strategic_intelligence

# Run deployment script (requires Git Bash or WSL)
bash deploy.sh cloud
```

### Option 2: Manual Step-by-Step (If SSH issues)

Follow the manual steps below for full control.

---

## Manual Deployment Steps

### Step 1: Test Local Deployment First

```powershell
# Navigate to SIL directory
cd C:\Users\dread\documents\rhiz_localdev\domains\trading\strategic_intelligence

# Build and start locally
docker-compose -f docker-compose.cloud.yaml up -d

# Wait 10 seconds for startup
Start-Sleep -Seconds 10

# Check health
curl http://localhost:8000/health

# Expected output:
# {
#   "status": "healthy",
#   "version": "1.0.0",
#   "components": { ... }
# }
```

**If local test succeeds:** Proceed to Step 2
**If local test fails:** Check Docker Desktop is running, review logs with:
```powershell
docker-compose -f docker-compose.cloud.yaml logs sil-api
```

---

### Step 2: Package Files for Upload

```powershell
# Create deployment package (excludes data/tests)
tar -czf sil_deploy.tar.gz `
  --exclude='data/historical/*.csv' `
  --exclude='data/qdrant/*' `
  --exclude='tests/' `
  --exclude='__pycache__' `
  --exclude='*.pyc' `
  --exclude='.pytest_cache' `
  --exclude='logs/' `
  .

# Verify package created
ls -lh sil_deploy.tar.gz
# Should be ~50-100KB (small!)
```

---

### Step 3: Upload to VPS

**Method A: SCP (if configured)**
```powershell
scp sil_deploy.tar.gz root@72.62.81.128:/tmp/
```

**Method B: Manual Upload via Hostinger File Manager**
1. Open Hostinger hPanel
2. Navigate to File Manager
3. Upload `sil_deploy.tar.gz` to `/tmp/`

---

### Step 4: SSH to VPS and Deploy

```bash
# SSH to VPS
ssh root@72.62.81.128

# Create directory structure
mkdir -p /root/rhiz_localdev/domains/trading/strategic_intelligence
cd /root/rhiz_localdev/domains/trading/strategic_intelligence

# Extract package
tar -xzf /tmp/sil_deploy.tar.gz
rm /tmp/sil_deploy.tar.gz

# Verify files extracted
ls -la
# Should see: api.py, Dockerfile, docker-compose.cloud.yaml, etc.
```

---

### Step 5: Build and Start SIL Container

```bash
# Still on VPS SSH session

# Stop any existing SIL containers
docker-compose -f docker-compose.cloud.yaml down 2>/dev/null || true

# Build SIL container (this may take 2-3 minutes)
docker-compose -f docker-compose.cloud.yaml build

# Start SIL API
docker-compose -f docker-compose.cloud.yaml up -d

# Watch logs in real-time (Ctrl+C to exit)
docker-compose -f docker-compose.cloud.yaml logs -f sil-api
```

**Expected Log Output:**
```
sil-api  | INFO:     Started server process [1]
sil-api  | INFO:     Waiting for application startup.
sil-api  | [Qdrant] Initializing on-disk mode at ./data/qdrant
sil-api  | [SIL] Transparency layer enabled (session: sil_1735939200)
sil-api  | INFO:     Application startup complete.
sil-api  | INFO:     Uvicorn running on http://0.0.0.0:8000
```

---

### Step 6: Verify Health

```bash
# On VPS, check health endpoint
curl http://localhost:8000/health

# Expected output:
# {
#   "status": "healthy",
#   "version": "1.0.0",
#   "components": {
#     "market_context": "operational",
#     "strategy_selector": "operational",
#     "position_sizer": "operational",
#     "memory": "operational",
#     "learning": "disabled"
#   }
# }
```

**If healthy:** 🎉 SIL is deployed!
**If unhealthy:** Check logs for errors

---

### Step 7: Test Strategy Selection Endpoint

```bash
# On VPS, test the main decision endpoint
# (This requires OHLCV data - we'll use a minimal test)

curl -X POST http://localhost:8000/config/strategies

# Should return available strategies for BTC/ETH/SOL
```

---

### Step 8: Configure n8n Integration

**From your Windows machine:**

1. **Open n8n** (already running on VPS)
   - URL: `http://72.62.81.128:5678` (or your n8n port)

2. **Create New Workflow:** "SIL_Health_Check"

3. **Add Nodes:**
   - **Schedule Trigger:** Every 5 minutes
   - **HTTP Request Node:**
     - Method: GET
     - URL: `http://sil-api:8000/health`
     - Note: Use `sil-api:8000` (Docker network name), NOT `localhost`

4. **Test Workflow:**
   - Click "Execute Workflow"
   - Should return healthy status

5. **Save and Activate**

---

## Post-Deployment Checklist

- [ ] SIL API container running (check with `docker ps`)
- [ ] Health endpoint returns "healthy" status
- [ ] Qdrant data directory created (`ls -la data/qdrant/`)
- [ ] Container uses <1GB RAM (check with `docker stats`)
- [ ] n8n can reach `http://sil-api:8000/health`
- [ ] Logs show no errors for 5 minutes

---

## Monitoring Commands

### Check Container Status
```bash
docker ps | grep sil-api
```

### View Live Logs
```bash
cd /root/rhiz_localdev/domains/trading/strategic_intelligence
docker-compose -f docker-compose.cloud.yaml logs -f sil-api
```

### Check Resource Usage
```bash
docker stats --no-stream
```

### Restart SIL (if needed)
```bash
docker-compose -f docker-compose.cloud.yaml restart sil-api
```

### Stop SIL
```bash
docker-compose -f docker-compose.cloud.yaml down
```

---

## Troubleshooting

### Issue: Container won't start
```bash
# Check Docker daemon
systemctl status docker

# Check for port conflicts
netstat -tulpn | grep 8000

# Review build logs
docker-compose -f docker-compose.cloud.yaml build --no-cache
```

### Issue: Health check fails
```bash
# Check if API is listening
curl -v http://localhost:8000/health

# Check container logs
docker-compose -f docker-compose.cloud.yaml logs sil-api | tail -50

# Check Python errors
docker exec -it rhiz-sil-api python -c "import api; print('Import OK')"
```

### Issue: Qdrant errors
```bash
# Check Qdrant data directory permissions
ls -la data/qdrant/

# Recreate Qdrant storage
rm -rf data/qdrant/*
docker-compose -f docker-compose.cloud.yaml restart sil-api
```

---

## Next Steps (After Successful Deployment)

### Immediate (Next 1 hour):
1. ✓ Verify SIL API health for 1 hour (no crashes)
2. Create n8n workflow: `SIL_Hourly_Trading_Decision`
3. Test regime classification with real BTC data
4. Verify Qdrant on-disk storage persists

### Short-Term (Next 48 hours):
5. Monitor RAM usage (should stay <1GB)
6. Test full decision flow: Kraken → n8n → SIL → Hummingbot
7. Configure Slack/Email alerts for errors
8. Paper trade 1 BTC decision cycle

### Medium-Term (Next 1 week):
9. Accumulate decision logs in Qdrant
10. Validate regime confidence calibration
11. Create performance tracking dashboard
12. Document any deployment friction points

---

## Success Criteria

**Deployment is successful when:**
- ✓ SIL API responds to health checks
- ✓ Container runs for 24+ hours without restart
- ✓ RAM usage stays <1GB
- ✓ n8n can call `/strategy/select` endpoint
- ✓ Qdrant stores data persistently
- ✓ Logs show no Python exceptions

---

## Emergency Rollback

If deployment fails critically:

```bash
# Stop SIL container
docker-compose -f docker-compose.cloud.yaml down

# Remove container and volume
docker rm -f rhiz-sil-api
docker volume rm rhiz-sil-qdrant

# Return to local development
# (No harm done - all code still on laptop)
```

---

## Deployment Authorization

**Authorized By:** Captain
**Executed By:** First Mate
**Date:** 2026-01-03
**Session:** #18

**Dyad Status:** Operational ⚡
**Iterative Loops:** Confirmed ✓

---

**Let's ship this, Captain! 🚀**

First command to run:
```powershell
cd C:\Users\dread\documents\rhiz_localdev\domains\trading\strategic_intelligence
docker-compose -f docker-compose.cloud.yaml up -d
```
