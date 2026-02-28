# Dockerfile Creation Summary
**Date**: 2026-01-11
**Session**: 42 - Unified Trading Platform Migration
**Status**: ✅ Complete (4/4 Dockerfiles created)

## Dockerfiles Created

### 1. Fathom MCP Server ✅
**Location**: `domains/trading/fathom/Dockerfile`
**Base Image**: python:3.11-slim
**Port**: 8765
**Entry Point**: `python src/server.py`
**Dependencies**:
- mcp>=1.0.0
- httpx>=0.27.0
- websockets>=12.0
- qdrant-client[fastembed]>=1.7.0
- pydantic>=2.0.0
- pyyaml>=6.0
- python-dotenv>=1.0.0

**Key Features**:
- Non-root user (fathom:1000)
- Health check via HTTP /health endpoint
- Volume mounts for /app/data and /app/logs
- Excludes __pycache__ and test files

### 2. Fathom Commander ✅
**Location**: `domains/trading/fathom_commander/Dockerfile`
**Base Image**: python:3.11-slim
**Port**: 8766
**Entry Point**: `python -u server.py`
**Dependencies** (from requirements.txt + additions):
- mcp>=0.1.0
- pyyaml>=6.0
- python-dotenv>=1.0
- qdrant-client[fastembed]>=1.7.0
- httpx>=0.27.0

**Changes from Original**:
- Updated from python:3.12-slim to 3.11-slim (consistency)
- Changed entry point from gateway.py to server.py (MCP protocol)
- Updated port from 8765 to 8766 (avoid conflict with Fathom)
- Added non-root user (fc:1000)
- Added qdrant-client and httpx dependencies
- Updated environment variables for unified platform
- Changed health check to use requests library

**Key Features**:
- Copies both server.py and gateway.py (backwards compatibility)
- Volume mounts for /app/state and /app/logs
- Paper mode by default (FC_MODE=paper)
- Approval threshold $20, max order $50

### 3. Strategic Intelligence Layer ✅
**Location**: `domains/trading/strategic_intelligence/Dockerfile`
**Base Image**: python:3.11-slim
**Port**: 8000
**Entry Point**: `uvicorn api:app --host 0.0.0.0 --port 8000`
**Dependencies** (from requirements.txt):
- fastapi
- uvicorn
- qdrant-client
- sentence-transformers (for embeddings)
- pandas, numpy (data processing)
- Other SIL-specific dependencies

**Changes from Original**:
- Added non-root user (sil:1000)
- Updated environment variables for unified platform
- Changed health check from requests to curl (more lightweight)
- Added QDRANT_HOST, QDRANT_PORT env vars
- Added SIL_ENABLE_MEMORY and SIL_LEARNING_ENABLED flags
- Added EMBEDDING_MODEL environment variable

**Key Features**:
- Learning engine disabled by default (enabled in Phase 3)
- Qdrant memory integration ready
- Volume mounts for /app/data and /app/logs

### 4. FastAPI Gateway ✅
**Location**: `infrastructure/vps/Dockerfile.gateway`
**Base Image**: python:3.11-slim
**Port**: 8080
**Entry Point**: `uvicorn gateway_trading:app --host 0.0.0.0 --port 8080`
**Dependencies** (new file: `requirements-gateway.txt`):
- fastapi>=0.109.0
- uvicorn[standard]>=0.27.0
- httpx>=0.27.0
- requests>=2.31.0
- pydantic>=2.5.0
- qdrant-client>=1.7.0
- python-json-logger>=2.0.7

**Key Features**:
- Non-root user (gateway:1000)
- Routes requests to all three trading services
- Unified REST API interface
- Health check aggregation
- Volume mount for /app/logs

**⚠️ NOTE**: `gateway_trading.py` does not exist yet. Must be created during Phase 1 deployment.

## Files Created This Session

1. `domains/trading/fathom/Dockerfile` - NEW
2. `domains/trading/fathom_commander/Dockerfile` - UPDATED
3. `domains/trading/strategic_intelligence/Dockerfile` - UPDATED
4. `infrastructure/vps/Dockerfile.gateway` - NEW
5. `infrastructure/vps/requirements-gateway.txt` - NEW
6. `infrastructure/vps/docker-compose.trading.yml` - CREATED EARLIER
7. `infrastructure/vps/rollback_to_hostinger.sh` - CREATED EARLIER
8. `docs/archive/n8n_workflows_final/EXPORT_COMMANDS.md` - CREATED EARLIER
9. `docs/architecture/QDRANT_STATE_PRE_MIGRATION.md` - CREATED EARLIER

## Still Needed for Phase 1 Deployment

### Code Files
1. **gateway_trading.py** - Unified API gateway routing logic
   - Routes to Fathom (execution), FC (orchestration), SIL (intelligence)
   - Health check aggregation
   - Request/response proxying
   - Authentication/authorization (if needed)

### Configuration Files
2. **nginx/nginx.conf** - Nginx reverse proxy configuration
   - SSL termination
   - Proxy pass to gateway:8080
   - Static file serving (if needed)
   - WebSocket support (for future live updates)

3. **nginx/ssl/** - SSL certificates directory
   - Let's Encrypt certificates (or self-signed for testing)
   - Certificate renewal configuration

### Environment Files
4. **.env** - Environment variables for docker-compose
   ```bash
   KRAKEN_API_KEY=<from_captain>
   KRAKEN_SECRET_KEY=<from_captain>
   ```

## Pre-Migration Blocker

**FC State Backup** - ⚠️ BLOCKED

The expected Fathom Commander state file does not exist on Hostinger VPS:
```bash
# Expected path: /opt/fathom_commander/state.json
# Error: cat: /opt/fathom_commander/state.json: No such file or directory
```

**Next Steps to Resolve**:
1. SSH to Hostinger VPS: `ssh root@72.62.81.128`
2. List /opt directory: `ls -la /opt/`
3. Check running containers: `docker ps -a`
4. Search for FC deployment: `find /opt -name "*fathom*" -type d`
5. Search for state files: `find /opt -name "state.json" 2>/dev/null`

**Possible Outcomes**:
- FC is deployed but state file is elsewhere → Update backup path
- FC is not deployed on Hostinger → Skip backup, proceed with migration
- FC is deployed but state is in Docker volume → Extract from volume

## Docker Compose Validation

The `docker-compose.trading.yml` file references all 4 Dockerfiles correctly:
- ✅ fathom-mcp → `domains/trading/fathom/Dockerfile`
- ✅ fathom-commander → `domains/trading/fathom_commander/Dockerfile`
- ✅ sil-fastapi → `domains/trading/strategic_intelligence/Dockerfile`
- ✅ fastapi-gateway → `infrastructure/vps/Dockerfile.gateway`
- ✅ qdrant → official image `qdrant/qdrant:v1.7.4`
- ✅ nginx → official image `nginx:alpine`

## Next Phase: Deployment to Hetzner

Once FC state backup is resolved (or confirmed unnecessary), proceed with:

1. **Create gateway_trading.py** - Unified API routing logic
2. **Create nginx configuration** - Reverse proxy setup
3. **Copy files to Hetzner VPS** - Use SCP/rsync
4. **Create .env file** - Kraken API credentials
5. **Build and start stack** - `docker-compose up -d --build`
6. **Verify all services** - Health checks, logs, connectivity
7. **Create trading_signals collection** - Qdrant schema setup
8. **Test MCP tools** - Claude Code integration

**Estimated Time for Deployment**: 6-7 hours (per original plan)
