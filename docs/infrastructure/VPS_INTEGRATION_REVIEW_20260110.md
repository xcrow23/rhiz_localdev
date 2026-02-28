# VPS Infrastructure Integration Review
**Date**: 2026-01-10
**Reviewer**: First Mate (Claude Sonnet 4.5)
**Scope**: Hostinger VPS Docker infrastructure analysis and integration recommendations
**Status**: SSH connection failed - analysis based on documentation and recent checkpoints

---

## Executive Summary

Based on recent deployment documentation and checkpoint data, the VPS infrastructure has **evolved significantly** since the January 3rd deployment summary. Multiple new services have been added (FastAPI Gateway, Embedding Service) while the architecture has shifted from the originally planned Hostinger VPS to a **different VPS** (95.217.51.24). However, **SSH connectivity is currently blocked**, preventing direct infrastructure verification.

**Critical Findings**:
1. **VPS Migration**: Infrastructure moved from Hostinger (72.62.81.128) to new VPS (95.217.51.24)
2. **Service Fragmentation**: Services deployed across multiple Docker Compose files without centralized orchestration
3. **Network Architecture**: Custom Docker network (`rhiz_network`) used but inconsistently applied
4. **Cloudflare Tunnel**: Fathom Commander has Cloudflare integration; newer services lack tunnel exposure
5. **n8n Deprecation**: Planned for removal but dependencies not yet migrated

---

## Current State Analysis

### Known Services (from documentation)

#### 1. **Qdrant Vector Database**
- **Port**: 6333 (REST API), 6334 (gRPC)
- **Collection**: `moonchecks` (mooncheck workflow data)
- **Network**: `rhiz_network`
- **Status**: Operational (per Dec 2025 checkpoint)
- **Data**: 1+ test vectors stored
- **Volume**: `qdrant_data` (persistent storage)

#### 2. **Embedding Service**
- **Port**: 5000
- **Model**: `sentence-transformers/all-MiniLM-L6-v2` (384-dim vectors)
- **Framework**: Flask
- **Network**: `rhiz_network`
- **Status**: Operational (per Dec 2025 checkpoint)
- **Container Name**: `rhiz_embedding` (assumed)
- **Purpose**: Generate embeddings for mooncheck workflow and FastAPI gateway

#### 3. **n8n Workflow Automation** (To Be Removed)
- **Port**: 5678
- **Version**: 2.2.5
- **Network**: `rhiz_network`
- **Access**: SSH tunnel (localhost:5678 → VPS:5678)
- **Status**: Operational via tunnel (per Dec 2025 checkpoint)
- **Volume**: `rhiz_n8n_data` (persistent workflows)
- **Deprecation Plan**: Migrate workflows to alternative orchestration

#### 4. **Rhiz FastAPI Gateway** (Recently Deployed)
- **Port**: 8000 (internal), 8080 (exposed via deployment guide)
- **Purpose**: Mooncheck ingestion, embedding proxy, Qdrant integration
- **Network**: `rhiz_network`
- **Dependencies**: Embedding service, Qdrant
- **Status**: Recently deployed (Jan 10 2026)
- **Health Check**: Multi-service health monitoring
- **Container Name**: `rhiz_fastapi_gateway`

#### 5. **Fathom Commander** (Cloudflare Tunnel Integrated)
- **Port**: 8765 (internal), 8766 (external)
- **Domain**: `fathom.dreamthewilderness.com`
- **Cloudflare Tunnel**: Configured (per docker-compose.cloud.yaml)
- **Network**: `rhiz_rhiz_network` (external reference)
- **Status**: Operational on Hostinger VPS (72.62.81.128) per Jan 3 deployment
- **Purpose**: Trading gateway, Kraken API integration
- **Note**: Separate infrastructure from new VPS (95.217.51.24)

#### 6. **Strategic Intelligence Layer (SIL API)**
- **Port**: 8001 (external), 8000 (internal)
- **Purpose**: Trading strategy selection, market analysis
- **Qdrant Mode**: On-disk (memory optimization)
- **Network**: `rhiz-network` (different from `rhiz_network`!)
- **Resource Limits**: 1GB RAM max, 2 CPU cores
- **Status**: Deployment planned (per docker-compose.cloud.yaml)
- **Volume**: `sil-qdrant-data` (separate from main Qdrant)

---

## Infrastructure Fragmentation Issues

### Problem 1: Multiple Docker Networks
- **`rhiz_network`**: Used by Qdrant, Embedding, n8n, FastAPI Gateway
- **`rhiz-network`**: Used by Strategic Intelligence Layer
- **`rhiz_rhiz_network`**: Referenced by Fathom Commander
- **`n8n_default`**: Used by older Hostinger deployment

**Impact**: Services on different networks cannot discover each other by container name.

**Recommendation**:
- Consolidate to single network: `rhiz_network`
- Update all docker-compose files to use consistent network name
- Use `external: true` to reference shared network

### Problem 2: Separated Docker Compose Files
Current structure:
- `infrastructure/vps/docker-compose.n8n.yml` (n8n only)
- `infrastructure/vps/docker-compose.fastapi.yml` (FastAPI + references to embedding/Qdrant)
- `domains/trading/fathom_commander/docker-compose.cloud.yaml` (Fathom Commander)
- `domains/trading/strategic_intelligence/docker-compose.cloud.yaml` (SIL API)

**Impact**:
- No centralized service orchestration
- Difficult to manage inter-service dependencies
- Services may start in wrong order
- Port conflicts not detected at compose-time

**Recommendation**: Create master docker-compose with all VPS services

### Problem 3: VPS Host Confusion
- **Hostinger VPS** (72.62.81.128): Fathom Commander, n8n (9 workflows), Qdrant (174 vectors)
- **New VPS** (95.217.51.24): FastAPI Gateway, Embedding Service, Qdrant (mooncheck collection), n8n (2.2.5)

**Question**: Are these the same VPS or different infrastructure?
- Hostinger documentation shows comprehensive deployment Jan 3 2026
- Recent checkpoint (Jan 8 2026) references VPS 95.217.51.24 with different services
- SSH connection refused on 95.217.51.24 (port 22 blocked or firewall issue)

**Action Required**: Clarify VPS architecture
- If same VPS: Update deployment docs with correct IP
- If different: Document dual-VPS architecture and service distribution

### Problem 4: Qdrant Instance Duplication
- **Main Qdrant**: Port 6333, `rhiz_memories` collection (174 vectors)
- **SIL Qdrant**: On-disk mode, `sil-qdrant-data` volume, separate collection
- **Mooncheck Qdrant**: Port 6333, `moonchecks` collection

**Ambiguity**: Are these different collections on the same Qdrant instance, or separate instances?

**Recommendation**:
- Use single Qdrant instance with multiple collections:
  - `rhiz_memories` (session checkpoints)
  - `moonchecks` (mooncheck workflow data)
  - `sil_strategies` (strategic intelligence vectors)
- Update SIL API to use server mode pointing to shared Qdrant
- Consolidate volumes and remove duplicate instances

---

## Network Architecture Recommendations

### Proposed Unified Docker Compose Structure

```yaml
version: '3.8'

networks:
  rhiz_network:
    name: rhiz_network
    driver: bridge

volumes:
  qdrant_data:
    name: rhiz_qdrant_data
  n8n_data:
    name: rhiz_n8n_data
  fathom_state:
    name: rhiz_fathom_state

services:
  # ========================================
  # Core Infrastructure
  # ========================================

  qdrant:
    image: qdrant/qdrant:latest
    container_name: rhiz_qdrant
    restart: unless-stopped
    ports:
      - "6333:6333"  # REST API
      - "6334:6334"  # gRPC
    volumes:
      - qdrant_data:/qdrant/storage
    networks:
      - rhiz_network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:6333/collections"]
      interval: 30s
      timeout: 10s
      retries: 3

  embedding:
    build:
      context: ./infrastructure/vps
      dockerfile: Dockerfile.embeddings
    image: rhiz/embedding:latest
    container_name: rhiz_embedding
    restart: unless-stopped
    ports:
      - "5000:5000"
    networks:
      - rhiz_network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  # ========================================
  # API Gateway Layer
  # ========================================

  fastapi-gateway:
    build:
      context: ./infrastructure/vps
      dockerfile: Dockerfile.fastapi
    image: rhiz/fastapi-gateway:latest
    container_name: rhiz_fastapi_gateway
    restart: unless-stopped
    ports:
      - "8080:8000"  # External port 8080
    environment:
      - EMBEDDING_SERVICE_URL=http://embedding:5000
      - QDRANT_HOST=qdrant
      - QDRANT_PORT=6333
      - QDRANT_COLLECTION=moonchecks
    networks:
      - rhiz_network
    depends_on:
      - embedding
      - qdrant
    healthcheck:
      test: ["CMD", "python", "-c", "import requests; requests.get('http://localhost:8000/health')"]
      interval: 30s
      timeout: 10s
      retries: 3

  # ========================================
  # Trading Infrastructure
  # ========================================

  fathom-commander:
    build:
      context: ./domains/trading/fathom_commander
      dockerfile: Dockerfile
    image: rhiz/fathom-commander:latest
    container_name: rhiz_fathom_commander
    restart: unless-stopped
    ports:
      - "127.0.0.1:8765:8765"  # Internal only
    environment:
      - KRAKEN_API_KEY=${KRAKEN_API_KEY}
      - KRAKEN_SECRET_KEY=${KRAKEN_SECRET_KEY}
      - FATHOM_QDRANT_URL=http://qdrant:6333
      - TZ=America/Chicago
    volumes:
      - fathom_state:/app/state
    networks:
      - rhiz_network
    depends_on:
      - qdrant
    healthcheck:
      test: ["CMD", "python", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:8765/')"]
      interval: 30s
      timeout: 10s
      retries: 3

  sil-api:
    build:
      context: ./domains/trading/strategic_intelligence
      dockerfile: Dockerfile
    image: rhiz/sil:latest
    container_name: rhiz_sil_api
    restart: unless-stopped
    ports:
      - "8001:8000"
    environment:
      - QDRANT_MODE=server  # Use shared Qdrant
      - QDRANT_URL=http://qdrant:6333
      - QDRANT_COLLECTION=sil_strategies
    networks:
      - rhiz_network
    depends_on:
      - qdrant
    healthcheck:
      test: ["CMD", "python", "-c", "import requests; requests.get('http://localhost:8000/health')"]
      interval: 30s
      timeout: 10s
      retries: 3

  # ========================================
  # Orchestration (To Be Deprecated)
  # ========================================

  n8n:
    image: n8nio/n8n:latest
    container_name: rhiz_n8n
    restart: unless-stopped
    ports:
      - "0.0.0.0:5678:5678"
    environment:
      - GENERIC_TIMEZONE=America/Chicago
      - N8N_LOG_LEVEL=info
    volumes:
      - n8n_data:/home/node/.n8n
    networks:
      - rhiz_network
```

**Benefits**:
- All services on single network for service discovery
- Clear dependency order (`depends_on`)
- Consolidated health checks
- Shared Qdrant instance with multiple collections
- Single `docker-compose up` deploys entire stack

---

## Cloudflare Tunnel Integration Strategy

### Current State
- **Fathom Commander**: Has Cloudflare Tunnel integration via Traefik labels
- **FastAPI Gateway**: Deployed recently but no tunnel configuration
- **SIL API**: No tunnel configuration
- **Embedding Service**: Internal only (correct - no external exposure needed)

### Tunnel Routing Recommendations

#### Option A: Single Tunnel, Multiple Routes (Recommended)
Use one Cloudflare Tunnel with multiple ingress rules:

```yaml
# ~/.cloudflared/config.yml on VPS
tunnel: <TUNNEL_ID>
credentials-file: /root/.cloudflared/<TUNNEL_ID>.json

ingress:
  # Trading gateway
  - hostname: fathom.dreamthewilderness.com
    service: http://localhost:8765

  # API gateway for moonchecks
  - hostname: api.dreamthewilderness.com
    service: http://localhost:8080

  # Strategic intelligence (if external access needed)
  - hostname: sil.dreamthewilderness.com
    service: http://localhost:8001

  # Catch-all
  - service: http_status:404
```

**DNS Configuration** (Cloudflare dashboard):
- `fathom.dreamthewilderness.com` → CNAME to `<TUNNEL_ID>.cfargotunnel.com`
- `api.dreamthewilderness.com` → CNAME to `<TUNNEL_ID>.cfargotunnel.com`
- `sil.dreamthewilderness.com` → CNAME to `<TUNNEL_ID>.cfargotunnel.com`

**Benefits**:
- Single tunnel daemon to manage
- Centralized logging and monitoring
- Easier credential management
- Lower overhead

#### Option B: Multiple Tunnels (Not Recommended)
Separate tunnel per service.

**Drawbacks**:
- More complex to manage
- More systemd services
- Higher resource usage
- Redundant certificate management

### Services That Should NOT Be Exposed
- **Embedding Service**: Internal only (port 5000) - already correct
- **Qdrant**: Internal only (port 6333/6334) - already correct
- **n8n**: Already exposed via Hostinger subdomain (if still needed)

---

## Port Management Analysis

### Current Port Allocation
| Service | Internal Port | External Port | Conflicts? |
|---------|--------------|---------------|------------|
| Qdrant REST | 6333 | 6333 | ✅ Unique |
| Qdrant gRPC | 6334 | 6334 | ✅ Unique |
| Embedding | 5000 | 5000 | ✅ Unique |
| n8n | 5678 | 5678 | ✅ Unique |
| Fathom Commander | 8765 | 8766 | ⚠️ Two ports |
| FastAPI Gateway | 8000 | 8080 | ✅ Unique |
| SIL API | 8000 | 8001 | ⚠️ Port reuse |

**Issues**:
1. **Fathom Commander dual ports**: 8765 internal, 8766 external - this is intentional for Cloudflare Tunnel vs direct access
2. **Port 8000 reuse**: FastAPI Gateway and SIL API both use internal 8000, exposed as 8080 and 8001 - this works but is confusing

**Recommendations**:
- Standardize internal ports to match service purpose:
  - FastAPI Gateway: Internal 8080, External 8080
  - SIL API: Internal 8001, External 8001
- Update `fastapi_gateway.py` to run on port 8080 instead of 8000
- Reduce confusion in environment variable references

---

## Resource Allocation Review

### FastAPI Gateway
```yaml
deploy:
  resources:
    limits:
      memory: 1G  # Reasonable for FastAPI + Python deps
      cpus: '2.0'
    reservations:
      memory: 512M
      cpus: '1.0'
```
✅ **Appropriate** for workload

### SIL API
```yaml
deploy:
  resources:
    limits:
      memory: 1G
      cpus: '2.0'
    reservations:
      memory: 512M
      cpus: '1.0'
```
✅ **Appropriate** - on-disk Qdrant mode reduces RAM needs

### Missing Resource Limits
- **Qdrant**: No limits set - could consume excessive RAM
- **Embedding Service**: No limits set - model loading could spike RAM
- **n8n**: No limits set
- **Fathom Commander**: No limits set

**Recommendations**:
```yaml
# Qdrant - vector DB can be memory-hungry
deploy:
  resources:
    limits:
      memory: 2G
      cpus: '2.0'
    reservations:
      memory: 1G

# Embedding Service - model is ~400MB
deploy:
  resources:
    limits:
      memory: 1G
      cpus: '1.0'
    reservations:
      memory: 512M

# n8n - workflow engine
deploy:
  resources:
    limits:
      memory: 1G
      cpus: '1.0'

# Fathom Commander - lightweight trading gateway
deploy:
  resources:
    limits:
      memory: 512M
      cpus: '1.0'
```

**Total VPS RAM Budget** (assuming 16GB VPS):
- Qdrant: 2GB
- Embedding: 1GB
- FastAPI Gateway: 1GB
- SIL API: 1GB
- n8n: 1GB
- Fathom Commander: 512MB
- System: 2GB
- **Total**: ~8.5GB (53% utilization - safe margin)

---

## Health Check Strategy

### Current Health Checks
✅ **FastAPI Gateway**: Multi-service health endpoint
✅ **Fathom Commander**: HTTP health check
✅ **SIL API**: HTTP health check
❌ **Qdrant**: No health check
❌ **Embedding Service**: No health check
❌ **n8n**: No health check

### Recommended Health Checks
All services should have Docker health checks for orchestration reliability.

```yaml
# Qdrant
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:6333/collections"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 20s

# Embedding Service
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:5000/health"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 40s  # Model loading takes time

# n8n
healthcheck:
  test: ["CMD", "wget", "--quiet", "--tries=1", "--spider", "http://localhost:5678/healthz"]
  interval: 30s
  timeout: 10s
  retries: 3
```

---

## Logging Strategy Recommendations

### Current State
- **FastAPI Gateway**: JSON file driver, 10MB max, 3 files
- **Other services**: Default Docker logging (unlimited, could fill disk)

### Centralized Logging Architecture
```yaml
# Add to all services
logging:
  driver: "json-file"
  options:
    max-size: "10m"
    max-file: "3"
    labels: "service,environment"
```

**Per-Service Log Locations** (on VPS):
- `/var/lib/docker/containers/<container_id>/<container_id>-json.log`

**Log Rotation**: Built-in via `max-size` and `max-file`

### External Log Aggregation (Future Enhancement)
Consider adding Loki + Promtail for centralized log querying:
```yaml
services:
  loki:
    image: grafana/loki:latest
    ports:
      - "3100:3100"
    volumes:
      - loki_data:/loki
    networks:
      - rhiz_network

  promtail:
    image: grafana/promtail:latest
    volumes:
      - /var/log:/var/log
      - /var/lib/docker/containers:/var/lib/docker/containers:ro
    networks:
      - rhiz_network
    depends_on:
      - loki
```

**Benefit**: Query logs across all services from Grafana dashboard

**Drawback**: Additional resource usage (~500MB RAM)

**Recommendation**: Defer until VPS upgraded or logging becomes pain point

---

## n8n Safe Removal Checklist

### Dependencies to Migrate
Based on documentation, n8n currently orchestrates:

#### 1. Mooncheck Workflow
- **Current**: n8n workflow → FastAPI Gateway → Embedding → Qdrant
- **Migration**: Cloudflare Worker → FastAPI Gateway (direct)
- **Status**: FastAPI Gateway deployed, Cloudflare Worker pending

#### 2. Fathom Commander Workflows (Hostinger VPS)
From Jan 3 deployment:
- Daily Health Monitor (8AM CT)
- Weekly DCA Buyer (Sunday 6PM CT)
- Smart DCA, Risk Monitor, Spread Scanner
- Portfolio Rebalancer, Volatility Sentinel
- Daily Performance Journal, Weekly Strategy Review

**Migration Options**:
1. **Option A: Rewrite as GitHub Actions** (scheduled YAML workflows)
2. **Option B: Deploy simple cron container** (Docker image with cron + curl)
3. **Option C: Move to Cloudflare Workers** (scheduled Durable Objects)

**Recommendation**: Option B (simple cron container)
```yaml
services:
  rhiz-scheduler:
    image: alpine:latest
    container_name: rhiz_scheduler
    restart: unless-stopped
    volumes:
      - ./cron/crontab:/etc/crontabs/root:ro
      - ./cron/scripts:/scripts:ro
    command: crond -f -l 2
    networks:
      - rhiz_network
```

**Example Crontab**:
```cron
# Daily Health Monitor - 8AM CT
0 13 * * * /scripts/health_monitor.sh >> /var/log/cron.log 2>&1

# Weekly DCA - Sunday 6PM CT
0 23 * * 0 /scripts/weekly_dca.sh >> /var/log/cron.log 2>&1
```

**Example Script** (`health_monitor.sh`):
```bash
#!/bin/sh
curl -f http://fathom-commander:8765/ || echo "Fathom Commander down!"
curl -f http://fastapi-gateway:8000/health || echo "FastAPI Gateway down!"
# Send alert via webhook or email if failures
```

### n8n Removal Steps
1. ✅ Export all workflows to JSON (backup)
2. ⏸ Migrate mooncheck workflow to Cloudflare Worker
3. ⏸ Deploy rhiz-scheduler container with cron jobs
4. ⏸ Test scheduled jobs for 1 week
5. ⏸ Deactivate n8n workflows (don't delete yet)
6. ⏸ Monitor for 2 weeks - ensure no missed jobs
7. ⏸ Stop n8n container: `docker stop rhiz_n8n`
8. ⏸ Backup n8n data: `docker cp rhiz_n8n:/home/node/.n8n ./n8n_backup`
9. ⏸ Remove container: `docker rm rhiz_n8n`
10. ⏸ Delete volume (optional): `docker volume rm rhiz_n8n_data`

**Rollback Plan**: Keep n8n image and volume for 30 days in case reactivation needed

---

## Deployment Refactoring Plan

### Phase 1: Consolidation (Week 1)
**Objective**: Unify all VPS services under single docker-compose

**Tasks**:
1. Create `infrastructure/vps/docker-compose.master.yml` with all services
2. Migrate network references to `rhiz_network`
3. Add health checks to all services
4. Add resource limits to all services
5. Standardize logging configuration
6. Test locally with `docker-compose config` (validate syntax)

**Deliverables**:
- Single compose file for entire stack
- Documentation: `infrastructure/vps/DEPLOYMENT_MASTER.md`

### Phase 2: Cloudflare Tunnel Setup (Week 1-2)
**Objective**: Expose FastAPI Gateway and SIL API via secure tunnel

**Prerequisites**:
- SSH access to VPS (currently blocked - needs resolution)
- Cloudflare account access
- DNS control for `dreamthewilderness.com`

**Tasks**:
1. SSH to VPS and install cloudflared
2. Authenticate with Cloudflare
3. Create tunnel: `cloudflared tunnel create rhiz-api`
4. Configure tunnel ingress (multi-route)
5. Set up systemd service
6. Configure DNS records
7. Test external access to all endpoints

**Deliverables**:
- Operational Cloudflare Tunnel
- Updated DNS records
- Tunnel configuration documentation

### Phase 3: n8n Migration (Week 2-3)
**Objective**: Replace n8n with lightweight cron scheduler

**Tasks**:
1. Export all n8n workflows to JSON (backup)
2. Convert workflows to shell scripts
3. Deploy rhiz-scheduler container
4. Test all cron jobs manually
5. Run in parallel with n8n for 1 week
6. Deactivate n8n workflows
7. Monitor for 2 weeks
8. Remove n8n container (keep backup)

**Deliverables**:
- rhiz-scheduler container with all jobs
- Workflow migration documentation
- n8n backup archive

### Phase 4: Monitoring & Optimization (Week 3-4)
**Objective**: Establish operational monitoring

**Tasks**:
1. Set up basic monitoring (health check dashboard)
2. Configure alerting (Slack webhook or email)
3. Review resource usage (adjust limits if needed)
4. Document runbook procedures
5. Test disaster recovery (container restart, volume restore)

**Deliverables**:
- Monitoring dashboard (Grafana or simple HTML)
- Alert configuration
- Runbook documentation

---

## Current State Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    INTERNET (Cloudflare Edge)                    │
│                                                                   │
│  fathom.dreamthewilderness.com ──────┐                          │
│  api.dreamthewilderness.com ─────────┼──► Cloudflare Tunnel     │
│  (planned)                            │    (not yet configured)  │
└────────────────────────────────────┬──┴───────────────────────────┘
                                     │
                    Cloudflare Tunnel│(pending)
                                     │
┌─────────────────────────────────────▼──────────────────────────────┐
│                    VPS: 95.217.51.24 (New)                          │
│                    OR 72.62.81.128 (Hostinger) - UNCLEAR            │
│                                                                      │
│  ┌────────────────────────────────────────────────────────────┐   │
│  │ Docker Network: rhiz_network                               │   │
│  │                                                             │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │   │
│  │  │   Qdrant     │  │  Embedding   │  │  FastAPI     │    │   │
│  │  │   :6333      │◄─┤  Service     │◄─┤  Gateway     │    │   │
│  │  │              │  │  :5000       │  │  :8080       │    │   │
│  │  └──────────────┘  └──────────────┘  └──────────────┘    │   │
│  │         ▲                                                  │   │
│  │         │                                                  │   │
│  │  ┌──────┴───────┐                                         │   │
│  │  │  n8n (TBD)   │                                         │   │
│  │  │  :5678       │                                         │   │
│  │  └──────────────┘                                         │   │
│  └────────────────────────────────────────────────────────────┘   │
│                                                                      │
│  ┌────────────────────────────────────────────────────────────┐   │
│  │ Docker Network: rhiz_rhiz_network (separate!)              │   │
│  │                                                             │   │
│  │  ┌──────────────┐                                          │   │
│  │  │  Fathom Cmd  │───► Kraken API                          │   │
│  │  │  :8765       │     (Trading)                            │   │
│  │  └──────────────┘                                          │   │
│  └────────────────────────────────────────────────────────────┘   │
│                                                                      │
│  ┌────────────────────────────────────────────────────────────┐   │
│  │ Docker Network: rhiz-network (third network!)              │   │
│  │                                                             │   │
│  │  ┌──────────────┐                                          │   │
│  │  │  SIL API     │                                          │   │
│  │  │  :8001       │                                          │   │
│  │  └──────────────┘                                          │   │
│  └────────────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────────────┘

ISSUE: Services fragmented across 3 separate Docker networks!
```

---

## Target State Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    INTERNET (Cloudflare Edge)                    │
│                                                                   │
│  fathom.dreamthewilderness.com ──┐                              │
│  api.dreamthewilderness.com ─────┼──► Cloudflare Tunnel         │
│  sil.dreamthewilderness.com ─────┘    (Single Tunnel)           │
└────────────────────────────────────┬─────────────────────────────┘
                                     │
                    Cloudflare Tunnel│(Encrypted, Zero Trust)
                                     │
┌─────────────────────────────────────▼──────────────────────────────┐
│                    VPS (Unified Infrastructure)                      │
│                                                                      │
│  ┌────────────────────────────────────────────────────────────┐   │
│  │ Docker Network: rhiz_network (Single Unified Network)      │   │
│  │                                                             │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │   │
│  │  │   Qdrant     │  │  Embedding   │  │  FastAPI     │    │   │
│  │  │   :6333      │◄─┤  Service     │◄─┤  Gateway     │    │   │
│  │  │              │  │  :5000       │  │  :8080       │    │   │
│  │  │ Collections: │  │  384-dim     │  │              │    │   │
│  │  │ - memories   │  │  vectors     │  │  Tunnel:     │    │   │
│  │  │ - moonchecks │  │              │  │  api.dream*  │    │   │
│  │  │ - strategies │  └──────────────┘  └──────────────┘    │   │
│  │  └──────┬───────┘                                         │   │
│  │         │                                                  │   │
│  │  ┌──────┴───────┐  ┌──────────────┐  ┌──────────────┐   │   │
│  │  │  Fathom Cmd  │  │   SIL API    │  │  Scheduler   │   │   │
│  │  │  :8765       │  │   :8001      │  │  (cron jobs) │   │   │
│  │  │              │  │              │  │              │   │   │
│  │  │  Tunnel:     │  │  Tunnel:     │  │  Internal    │   │   │
│  │  │  fathom.*    │  │  sil.dream*  │  │  HTTP calls  │   │   │
│  │  └──────┬───────┘  └──────────────┘  └──────────────┘   │   │
│  │         │                                                  │   │
│  └─────────┼──────────────────────────────────────────────────┘   │
│            │                                                        │
│            └──────────► Kraken API (Trading)                      │
└──────────────────────────────────────────────────────────────────────┘

BENEFITS:
- Single Docker network (service discovery works)
- Single Cloudflare Tunnel (simplified ops)
- Shared Qdrant (multiple collections)
- Lightweight cron scheduler (replaces n8n)
- Health checks on all services
- Resource limits prevent runaway containers
```

---

## Action Items

### Immediate (This Week)
1. **Resolve SSH Access**: Debug connection refused on VPS (95.217.51.24)
   - Check firewall rules
   - Verify SSH daemon running
   - Confirm correct IP address

2. **Clarify VPS Architecture**:
   - Is 95.217.51.24 the same as 72.62.81.128?
   - If different, document dual-VPS service distribution
   - Update deployment docs with correct IP addresses

3. **Create Master Docker Compose**:
   - Consolidate all services into single compose file
   - Standardize network to `rhiz_network`
   - Add health checks to all services
   - Add resource limits to prevent runaway containers

### Short-Term (Next 2 Weeks)
4. **Deploy Cloudflare Tunnel**:
   - Configure tunnel for FastAPI Gateway (api.dreamthewilderness.com)
   - Add SIL API route if external access needed
   - Test end-to-end connectivity

5. **Migrate n8n Workflows**:
   - Export all workflows to JSON (backup)
   - Deploy rhiz-scheduler cron container
   - Test parallel execution for 1 week
   - Deactivate n8n (don't delete yet)

6. **Monitoring Setup**:
   - Create simple health dashboard
   - Configure alerting (email or Slack)
   - Document runbook procedures

### Medium-Term (Next Month)
7. **Remove n8n**:
   - After 2 weeks of successful cron operation
   - Backup n8n data before removal
   - Keep backup for 30 days (rollback option)

8. **Optimize Resource Usage**:
   - Monitor container resource consumption
   - Adjust limits based on actual usage
   - Consider log aggregation if needed

9. **Update Documentation**:
   - Comprehensive deployment guide
   - Service interaction diagrams
   - Troubleshooting runbook

---

## Open Questions

1. **VPS Identity**: Is 95.217.51.24 the Hostinger VPS (72.62.81.128) or a different server?
2. **SSH Access**: Why is port 22 connection refused? Firewall? Wrong IP?
3. **Qdrant Instances**: How many Qdrant instances are running? Same or separate?
4. **Fathom Commander Status**: Is it still on Hostinger VPS or migrated to new VPS?
5. **SIL External Access**: Should Strategic Intelligence API be publicly accessible?
6. **Cloudflare Tunnel**: Is existing tunnel configured for Fathom only or multi-service?
7. **n8n Migration Timeline**: When should n8n removal be completed?
8. **Backup Strategy**: Are VPS snapshots configured? Backup frequency?

---

## Summary

The VPS infrastructure has **significant fragmentation** across multiple Docker networks and compose files. The core architecture is sound (Qdrant, Embedding, FastAPI Gateway, Trading services), but **operational integration is incomplete**:

**Strengths**:
✅ Well-designed service separation
✅ Health checks on critical services
✅ Resource limits on newer deployments
✅ Cloudflare Tunnel integration (Fathom Commander)

**Weaknesses**:
❌ Three separate Docker networks (services can't discover each other)
❌ Multiple Docker Compose files (no centralized orchestration)
❌ VPS identity confusion (two different IPs in docs)
❌ SSH access blocked (prevents verification)
❌ n8n deprecation incomplete (workflows still active but should migrate)
❌ Cloudflare Tunnel only configured for one service
❌ Missing health checks on core infrastructure (Qdrant, Embedding)

**Primary Recommendation**:
**Consolidate all services into single docker-compose.master.yml** with unified `rhiz_network`, comprehensive health checks, and resource limits. Then deploy Cloudflare Tunnel with multi-route ingress for all public-facing APIs.

---

**End of Infrastructure Integration Review**
**Next Steps**: Resolve SSH access, clarify VPS architecture, create master compose file
