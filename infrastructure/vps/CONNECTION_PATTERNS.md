# Unified Trading Platform - Connection Patterns
**Deployment**: Hostinger VPS (72.62.81.128)
**Date**: 2026-01-12
**Session**: 42 - Trading Systems Federation

## Service Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Hostinger VPS (72.62.81.128)             │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌─────────────────┐      ┌──────────────────┐             │
│  │  Fathom MCP     │◄─────┤  Claude Code     │ (SSH)       │
│  │  stdio server   │      │  Local Machine   │             │
│  │  Port: 8765*    │      └──────────────────┘             │
│  └─────────────────┘                                         │
│           │                                                   │
│           │ (internal Docker network)                        │
│           ▼                                                   │
│  ┌─────────────────┐                                         │
│  │ Fathom Commander│◄─────┤  Claude Code     │ (SSH)       │
│  │  stdio server   │      │  Local Machine   │             │
│  │  Port: 8766*    │      └──────────────────┘             │
│  └─────────────────┘                                         │
│           │                                                   │
│           │ (calls Fathom via MCP internal)                 │
│           │                                                   │
│           ▼                                                   │
│  ┌─────────────────┐      ┌──────────────────┐             │
│  │      Qdrant     │◄─────┤  HTTP Clients    │             │
│  │  Vector DB      │      │  Port: 6333      │             │
│  │  Port: 6333     │      └──────────────────┘             │
│  └─────────────────┘                                         │
│           ▲                                                   │
│           │                                                   │
│  ┌─────────────────┐      ┌──────────────────┐             │
│  │   SIL FastAPI   │◄─────┤  HTTP Clients    │             │
│  │  Intelligence   │      │  Port: 8001      │             │
│  │  Port: 8001     │      └──────────────────┘             │
│  └─────────────────┘                                         │
│           ▲                                                   │
│           │                                                   │
│  ┌─────────────────┐      ┌──────────────────┐             │
│  │ FastAPI Gateway │◄─────┤  HTTP Clients    │             │
│  │  Unified Router │      │  Port: 8080      │             │
│  │  Port: 8080     │      └──────────────────┘             │
│  └─────────────────┘                                         │
│                                                               │
└─────────────────────────────────────────────────────────────┘

* Ports 8765/8766 are EXPOSED but not for HTTP - these are MCP stdio servers
```

## Connection Patterns by Use Case

### 1. Claude Code MCP Tools (Current Primary Method)

**Fathom MCP Tools**:
```json
// claude_desktop_config.json
{
  "mcpServers": {
    "fathom": {
      "command": "ssh",
      "args": [
        "root@72.62.81.128",
        "docker exec -i fathom-mcp python -m src.server"
      ]
    }
  }
}
```

**Fathom Commander MCP Tools**:
```json
// claude_desktop_config.json
{
  "mcpServers": {
    "fathom-commander": {
      "command": "ssh",
      "args": [
        "root@72.62.81.128",
        "docker exec -i fathom-commander python -u server.py"
      ]
    }
  }
}
```

**Available Tools**:
- **Fathom**: `get_account_balance`, `get_ohlc_data`, `place_order`, `get_order_status`, etc. (25+ tools)
- **FC**: `execute_trade`, `check_spread`, `scan_opportunities`, `get_portfolio_status`, etc. (27 tools)

### 2. Strategic Intelligence Layer (HTTP REST API)

**Direct Access**:
```bash
curl http://72.62.81.128:8001/health
curl http://72.62.81.128:8001/analyze_regime?pair=BTC/USD
```

**Via Gateway** (routes to internal `sil-fastapi:8000`):
```bash
curl http://72.62.81.128:8080/sil/health
curl http://72.62.81.128:8080/sil/analyze_regime?pair=BTC/USD
```

**Available Endpoints**:
- `GET /health` - Service health check
- `POST /analyze_regime` - Market regime detection
- `POST /select_strategy` - Strategy recommendation based on patterns
- `POST /refresh_regimes` - Update regime classifications

### 3. Qdrant Vector Database (HTTP REST API)

**Direct Access**:
```bash
curl http://72.62.81.128:6333/collections
curl http://72.62.81.128:6333/collections/rhiz_memories/points/scroll
```

**Via Gateway** (routes to internal `qdrant:6333`):
```bash
curl http://72.62.81.128:8080/qdrant/collections
```

**Collections**:
- `rhiz_memories`: 174 vectors (session memory)
- `moonchecks`: 9 vectors (iOS shortcut embeddings)
- `trading_signals`: TO BE CREATED (cross-system learning)

### 4. Unified Gateway (HTTP REST API)

**Health Check** (aggregates all services):
```bash
curl http://72.62.81.128:8080/health
```

**Response Structure**:
```json
{
  "gateway": "healthy",
  "overall": "degraded",
  "services": {
    "fathom": {"status": "unreachable", "error": "MCP stdio server"},
    "fc": {"status": "unreachable", "error": "MCP stdio server"},
    "sil": {"status": "healthy", "response_code": 200},
    "qdrant": {"status": "healthy", "response_code": 200}
  }
}
```

**Routing Patterns**:
- `/sil/*` → `http://sil-fastapi:8000/*`
- `/qdrant/*` → `http://qdrant:6333/*`
- `/fathom/*` → Not available (stdio server)
- `/fc/*` → Not available (stdio server)

## Future Integration Patterns

### Phase 2: Cloudflare Workers (Planned)

For Cloudflare Workers to call FC/Fathom, we have two options:

**Option A: Deploy FC HTTP Gateway** (recommended):
```yaml
# Add to docker-compose.yml
fc-http-gateway:
  build:
    context: ./domains/trading/fathom_commander
  container_name: fc-http-gateway
  command: ["python", "-u", "gateway.py", "8767"]
  ports:
    - "8767:8767"
  environment:
    - FATHOM_MCP_URL=http://fathom-mcp:8765  # Won't work, see Option B
```

**Option B: Direct Kraken Integration** (cleaner):
```javascript
// Cloudflare Worker calls Kraken API directly
// FC orchestration logic ported to Worker
// Fathom becomes library, not separate service
```

### Phase 3: Shared Intelligence Integration

FC will query SIL before executing trades:
```bash
# FC (Python) → SIL (HTTP)
response = httpx.post(
    "http://sil-fastapi:8000/select_strategy",
    json={"pair": "BTC/USD", "current_context": reasoning}
)
```

## Container Management

**Start all services**:
```bash
ssh root@72.62.81.128
cd /opt/rhiz_trading
docker compose up -d
```

**View logs**:
```bash
docker logs fathom-mcp
docker logs fathom-commander
docker logs sil-fastapi
docker logs qdrant
docker logs fastapi-gateway
```

**Restart a service**:
```bash
docker compose restart fathom-mcp
```

**Rebuild after code changes**:
```bash
docker compose build fathom-mcp
docker compose up -d fathom-mcp
```

## Important Notes

1. **MCP Stdio vs HTTP**: Fathom and FC run as stdio-based MCP servers. They do NOT expose HTTP endpoints. The exposed ports (8765, 8766) are for documentation only.

2. **Internal Docker Network**: Services communicate on `rhiz_network`. External clients connect via exposed ports on host IP (72.62.81.128).

3. **Environment Variables**: Loaded from `/opt/rhiz_trading/.env` (contains Kraken API credentials).

4. **State Persistence**:
   - Fathom data: `/app/data` (Docker volume `fathom-data`)
   - FC state: `/app/state/commander_state.json` (Docker volume `fc-state`)
   - Qdrant storage: `/qdrant/storage` (Docker volume `qdrant-storage`)

5. **No Health Checks**: Fathom and FC containers have `stdin_open: true` instead of health checks (stdio servers can't respond to HTTP probes).

## Troubleshooting

**Container restarting**:
```bash
# Check logs for errors
docker logs --tail 50 fathom-mcp

# Verify environment variables loaded
docker inspect fathom-mcp | grep -A 5 Env

# Test manually
docker run --rm --env-file /opt/rhiz_trading/.env rhiz_trading-fathom-mcp:latest python -m src.server
```

**MCP tools not working**:
```bash
# Test SSH connection
ssh root@72.62.81.128

# Test Docker exec
docker exec -i fathom-mcp python -c "print('Working')"

# Verify container running
docker ps | grep fathom
```

**Gateway reporting degraded**:
- This is expected! Fathom/FC are stdio servers, not HTTP.
- Only SIL and Qdrant should show "healthy" in gateway response.
