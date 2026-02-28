# Unified Trading Platform Architecture
**Decision Date**: 2026-01-10 (Session 40)
**Decision By**: Captain
**Implementation**: First Mate

## Captain's Directive

> "Ideally hosted on the same platform with intelligence analysis and signals being stored together on that self same hosting platform. The specifics I leave to you but we must have access parity, ease, and elegance as we cannot afford to be debugging constantly."

**Translation**:
- ✅ Single platform for all trading systems
- ✅ Shared intelligence/signals storage
- ✅ Access parity (no credential juggling)
- ✅ Elegant (no constant debugging)
- ❌ Fragmentation across multiple VPS instances

---

## Current State (Fragmented)

### System Distribution
- **Fathom** (Kraken MCP): Local laptop development
- **Fathom Commander** (27 MCP tools): Hostinger VPS (72.62.81.128)
- **Strategic Intelligence Layer**: Hetzner VPS (95.217.51.24)
- **Qdrant**: Split across local + both VPS instances

### Problems
- 3 different hosts (laptop, Hostinger, Hetzner)
- Credential management complexity (3 sets of SSH keys, env vars)
- Data fragmentation (signals stored separately from analysis)
- Debugging nightmare (which VPS has which logs?)
- n8n orchestration failing (502 errors everywhere)

---

## Proposed Architecture: Hetzner VPS Consolidation

### Single Platform: Hetzner VPS (95.217.51.24)

**Why Hetzner**:
- ✅ Already hosts SIL (B+ grade, operational)
- ✅ Already has FastAPI Gateway (Cloudflare Workers support)
- ✅ Already has Qdrant cloud instance
- ✅ More modern infrastructure than Hostinger
- ✅ Better aligned with Cloudflare Workers strategy

**Decommission**: Hostinger VPS (72.62.81.128) trading services

---

## System Layout

```
┌─────────────────────────────────────────────────────────────┐
│           Hetzner VPS (95.217.51.24)                        │
│                                                             │
│  ┌───────────────────────────────────────────────────────┐ │
│  │ Trading Intelligence Stack                            │ │
│  ├───────────────────────────────────────────────────────┤ │
│  │                                                       │ │
│  │  1. Fathom (Kraken MCP)                Port: 8765   │ │
│  │     - Account data, market data                     │ │
│  │     - Phase 1 operational, Phase 2-6 TBD           │ │
│  │                                                       │ │
│  │  2. Fathom Commander           Port: 8766           │ │
│  │     - 27 MCP orchestration tools                    │ │
│  │     - Workflow composition                          │ │
│  │     - Health monitoring                             │ │
│  │                                                       │ │
│  │  3. Strategic Intelligence Layer    Port: 8000      │ │
│  │     - Pattern recognition                           │ │
│  │     - Strategy selection                            │ │
│  │     - Risk assessment                               │ │
│  │                                                       │ │
│  └───────────────────────────────────────────────────────┘ │
│                                                             │
│  ┌───────────────────────────────────────────────────────┐ │
│  │ Shared Data Layer                                     │ │
│  ├───────────────────────────────────────────────────────┤ │
│  │                                                       │ │
│  │  Qdrant (Port 6333)                                  │ │
│  │  ├─ rhiz_memories collection (161 vectors)          │ │
│  │  ├─ moonchecks collection (Cloudflare Workers data) │ │
│  │  └─ trading_signals collection (NEW)                │ │
│  │      ├─ Market analysis embeddings                  │ │
│  │      ├─ Strategy performance history                │ │
│  │      └─ Risk assessment data                        │ │
│  │                                                       │ │
│  │  PostgreSQL/SQLite (NEW - Optional)                 │ │
│  │  └─ Time-series trading data (OHLCV, orders)       │ │
│  │                                                       │ │
│  └───────────────────────────────────────────────────────┘ │
│                                                             │
│  ┌───────────────────────────────────────────────────────┐ │
│  │ API Gateway & Orchestration                           │ │
│  ├───────────────────────────────────────────────────────┤ │
│  │                                                       │ │
│  │  FastAPI Gateway            Port: 8080               │ │
│  │  - REST API for Cloudflare Workers                  │ │
│  │  - Webhook endpoints                                 │ │
│  │  - Health check aggregation                         │ │
│  │                                                       │ │
│  └───────────────────────────────────────────────────────┘ │
│                                                             │
│  Docker Compose Stack:                                     │
│  - fathom-mcp (new)                                        │
│  - fathom-commander (migrated from Hostinger)              │
│  - sil-fastapi (existing)                                  │
│  - qdrant (existing)                                       │
│  - fastapi-gateway (existing)                              │
│  - nginx (reverse proxy for SSL)                           │
│                                                             │
└─────────────────────────────────────────────────────────────┘
                          ▲
                          │
                          │ HTTPS / Webhooks
                          │
┌─────────────────────────────────────────────────────────────┐
│         Cloudflare Workers (Orchestration)                  │
│                                                             │
│  ┌──────────────────────┐  ┌──────────────────────┐        │
│  │ Trading Cron Workers │  │ Event Handlers       │        │
│  ├──────────────────────┤  ├──────────────────────┤        │
│  │ - Daily health check │  │ - Order fills        │        │
│  │ - Weekly DCA         │  │ - Price alerts       │        │
│  │ - Strategy refresh   │  │ - Risk thresholds    │        │
│  └──────────────────────┘  └──────────────────────┘        │
│                                                             │
│  All call FastAPI Gateway → VPS trading stack              │
│                                                             │
└─────────────────────────────────────────────────────────────┘
                          ▲
                          │ MCP Tools
                          │
┌─────────────────────────────────────────────────────────────┐
│           Claude Code (Local Laptop)                        │
│                                                             │
│  Fathom Commander MCP Server                                │
│  - 27 tools for interactive trading workflows              │
│  - Connects to VPS Fathom Commander API                    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Data Flow: Intelligence → Signals → Execution

### 1. Market Data Ingestion (Fathom)
```
Kraken Exchange
    ↓ WebSocket (Phase 3-4)
Fathom MCP (Port 8765)
    ↓ Structured data
Qdrant: trading_signals collection
    ↓ Embeddings
```

### 2. Intelligence Analysis (SIL)
```
Qdrant: trading_signals
    ↓ Pattern recognition
SIL FastAPI (Port 8000)
    ↓ Strategy recommendations
Qdrant: trading_signals (enriched)
```

### 3. Workflow Orchestration (Fathom Commander + Cloudflare)
```
Cloudflare Cron Worker (every 4 hours)
    ↓ HTTPS request
FastAPI Gateway (Port 8080)
    ↓ Route to FC
Fathom Commander (Port 8766)
    ↓ Execute workflow
Fathom MCP → Kraken (order placement)
```

### 4. Logging & Observability
```
All services → stdout/stderr
    ↓ Docker logs
Collected by FastAPI Gateway /logs endpoint
    ↓ Queryable
Claude Code via MCP tools
```

---

## Migration Steps

### Phase 1: Preparation (1 hour)
1. **Backup Hostinger VPS**:
   ```bash
   ssh root@72.62.81.128
   docker-compose -f fathom_commander/docker-compose.yml down
   tar czf fathom_commander_backup.tar.gz fathom_commander/
   scp fathom_commander_backup.tar.gz root@95.217.51.24:/root/
   ```

2. **Prepare Hetzner VPS**:
   ```bash
   ssh root@95.217.51.24
   mkdir -p /opt/rhiz/trading/{fathom,fathom_commander,sil}
   ```

### Phase 2: Deploy Unified Stack (2-3 hours)

1. **Create Unified docker-compose.yml**:
   ```yaml
   # /opt/rhiz/docker-compose.trading.yml
   version: '3.8'

   services:
     fathom-mcp:
       build: ./trading/fathom
       ports:
         - "8765:8765"
       environment:
         - KRAKEN_API_KEY=${KRAKEN_API_KEY}
         - KRAKEN_SECRET_KEY=${KRAKEN_SECRET_KEY}
       networks:
         - trading-net

     fathom-commander:
       build: ./trading/fathom_commander
       ports:
         - "8766:8766"
       depends_on:
         - fathom-mcp
       environment:
         - FATHOM_MCP_URL=http://fathom-mcp:8765
       networks:
         - trading-net

     sil-fastapi:
       build: ./trading/sil
       ports:
         - "8000:8000"
       environment:
         - QDRANT_HOST=qdrant
         - QDRANT_PORT=6333
       depends_on:
         - qdrant
       networks:
         - trading-net

     qdrant:
       image: qdrant/qdrant:latest
       ports:
         - "6333:6333"
       volumes:
         - qdrant-storage:/qdrant/storage
       networks:
         - trading-net

     fastapi-gateway:
       build: ./fastapi_gateway
       ports:
         - "8080:8080"
       environment:
         - FATHOM_COMMANDER_URL=http://fathom-commander:8766
         - SIL_URL=http://sil-fastapi:8000
       networks:
         - trading-net

     nginx:
       image: nginx:alpine
       ports:
         - "80:80"
         - "443:443"
       volumes:
         - ./nginx/nginx.conf:/etc/nginx/nginx.conf
         - ./nginx/ssl:/etc/nginx/ssl
       depends_on:
         - fastapi-gateway
       networks:
         - trading-net

   networks:
     trading-net:
       driver: bridge

   volumes:
     qdrant-storage:
   ```

2. **Deploy**:
   ```bash
   cd /opt/rhiz
   docker-compose -f docker-compose.trading.yml up -d
   ```

3. **Verify**:
   ```bash
   curl http://localhost:8080/health
   curl http://localhost:8765/api/account  # Fathom
   curl http://localhost:8766/health       # FC
   curl http://localhost:8000/health       # SIL
   ```

### Phase 3: Cloudflare Workers (Replaces n8n) (2 hours)

1. **Create Trading Cron Workers**:
   ```javascript
   // infrastructure/cloudflare/trading-cron/daily-health.js
   export default {
     async scheduled(event, env, ctx) {
       const response = await fetch('https://95.217.51.24:8080/trading/health-check', {
         method: 'POST',
         headers: { 'Content-Type': 'application/json' }
       });

       const health = await response.json();

       // Store in D1 or send alert if unhealthy
       if (!health.all_systems_operational) {
         await env.DB.prepare('INSERT INTO alerts (timestamp, service, status) VALUES (?, ?, ?)').bind(
           new Date().toISOString(),
           health.failing_service,
           'UNHEALTHY'
         ).run();
       }
     }
   }
   ```

2. **Deploy Workers**:
   ```bash
   cd infrastructure/cloudflare/trading-cron
   wrangler deploy daily-health.js --schedule "0 */4 * * *"  # Every 4 hours
   wrangler deploy weekly-dca.js --schedule "0 10 * * 1"     # Monday 10am
   ```

### Phase 4: DNS & SSL (30 minutes)

1. **Cloudflare DNS**:
   - Point `trading.dreamthewilderness.com` → 95.217.51.24
   - Enable Cloudflare proxy (orange cloud)

2. **Nginx SSL** (Let's Encrypt via Certbot on VPS)

### Phase 5: Decommission Hostinger (15 minutes)

1. Verify all services operational on Hetzner
2. Download final logs from Hostinger
3. Stop Hostinger VPS services
4. Update CLAUDE.md to reflect single-VPS architecture

---

## Benefits

### Access Parity
- ✅ Single SSH key for all trading systems
- ✅ Single environment variable set (KRAKEN_API_KEY once)
- ✅ Docker network for inter-service communication (no port juggling)

### Ease
- ✅ `docker-compose logs -f` shows all trading logs in one place
- ✅ Single `docker-compose restart` to restart entire stack
- ✅ Health check at one endpoint (/trading/health)

### Elegance
- ✅ Fathom → FC → SIL data flows internally (no VPS-to-VPS calls)
- ✅ Shared Qdrant instance (one source of truth for signals)
- ✅ Cloudflare Workers replace fragile n8n (serverless, reliable)

### No More Debugging Hell
- ✅ All logs centralized
- ✅ Docker networking eliminates port conflicts
- ✅ n8n removed (13 hours of pain eliminated)
- ✅ FastAPI Gateway provides observability endpoint

---

## Integration Points

### Fathom → Fathom Commander
- **Connection**: HTTP (internal Docker network)
- **URL**: `http://fathom-mcp:8765`
- **Data**: Account balances, market data, order placement

### Fathom Commander → SIL
- **Connection**: HTTP (internal Docker network)
- **URL**: `http://sil-fastapi:8000`
- **Data**: Strategy recommendations, risk assessments

### SIL → Qdrant
- **Connection**: gRPC (internal Docker network)
- **URL**: `qdrant:6333`
- **Collections**:
  - `trading_signals`: Market embeddings, pattern analysis
  - `rhiz_memories`: Session context (existing)

### Cloudflare Workers → VPS
- **Connection**: HTTPS (public internet, authenticated)
- **URL**: `https://95.217.51.24:8080` (via FastAPI Gateway)
- **Auth**: Bearer token or API key

---

## Testing Strategy

### Unit Testing (Before Migration)
- Verify Fathom MCP works standalone
- Verify FC can call Fathom locally
- Verify SIL can read from Qdrant

### Integration Testing (During Migration)
- Deploy stack, test health endpoints
- Test FC → Fathom → Kraken (paper trading mode)
- Test SIL → Qdrant → FC data flow

### Production Validation (After Migration)
- Run daily health check Worker manually
- Verify logs flowing to FastAPI Gateway
- Test MCP tools from Claude Code
- Monitor for 48 hours before decommissioning Hostinger

---

## Rollback Plan

If migration fails:
1. Hostinger VPS still running (frozen, not decommissioned)
2. Restore Fathom Commander on Hostinger: `docker-compose up -d`
3. Revert Cloudflare DNS to 72.62.81.128
4. Debug Hetzner issues separately

**Rollback Time**: 15 minutes

---

## Timeline

- **Phase 1** (Preparation): 1 hour
- **Phase 2** (Deployment): 2-3 hours
- **Phase 3** (Cloudflare Workers): 2 hours
- **Phase 4** (DNS/SSL): 30 minutes
- **Phase 5** (Decommission): 15 minutes

**Total**: 6-7 hours (can split across multiple sessions)

---

## Success Criteria

✅ All three systems (Fathom, FC, SIL) running on Hetzner VPS
✅ Single docker-compose stack managing entire trading platform
✅ Shared Qdrant instance with trading_signals collection
✅ Cloudflare Workers replacing n8n (no 502 errors)
✅ MCP tools from Claude Code work seamlessly
✅ Health check aggregation at single endpoint
✅ Hostinger VPS trading services decommissioned

---

## Next Steps

1. **Captain approval** of this architecture
2. **First Mate**: Create unified docker-compose.yml
3. **Captain**: Run `wrangler login` for Cloudflare Workers deployment
4. **First Mate**: Execute Phase 1-2 (VPS preparation + deployment)
5. **Both**: Test integration, verify data flows
6. **First Mate**: Deploy Cloudflare Workers (Phase 3)
7. **First Mate**: DNS/SSL (Phase 4)
8. **Monitor**: 48 hours before Hostinger decommission

---

**Decision**: Unified Hetzner VPS platform
**Rationale**: Access parity, ease, elegance (Captain's directive)
**Risk**: Medium (well-planned migration with rollback)
**Impact**: HIGH (solves H1, H6, and eliminates Hostinger complexity)

**Status**: AWAITING CAPTAIN APPROVAL
