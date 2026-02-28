# n8n → Cloudflare Workers Migration Plan
**Decision Date**: 2026-01-10 (Session 40)
**Decision By**: Captain
**Quote**: "Abandon all hope ye who use n8n!"

## Executive Summary

**Problem**: n8n has cost 13 hours of work with tons of failure points (502 errors, auth issues, deployment complexity)

**Solution**: Abandon n8n entirely, migrate all workflows to Cloudflare Workers

**Benefit**: Serverless, reliable, zero-maintenance orchestration

---

## Current n8n Deployments (TO BE DECOMMISSIONED)

### Hostinger VPS (72.62.81.128)
- 9 workflows (all failing with 502 Bad Gateway)
- Fathom Commander orchestration
- Health monitoring
- Strategy execution

### Hetzner VPS (95.217.51.24)
- n8n 2.2.5 installed
- 2-3 SIL workflows (health monitor, strategy selection)
- Status: Partially operational

### Local (Laptop)
- n8n dev instance for testing
- Status: Occasionally used

---

## n8n Workflows to Migrate

### 1. Daily Health Check Workflow
**Current**: n8n workflow hitting Fathom Commander /health endpoint every 4 hours
**n8n Complexity**: 502 errors, webhook configuration, auth token management
**Cloudflare Replacement**: Single cron Worker, 20 lines of code

### 2. Weekly DCA Workflow
**Current**: n8n workflow executing dollar-cost averaging strategy weekly
**n8n Complexity**: Schedule reliability issues, state management
**Cloudflare Replacement**: Cron Worker + D1 for state, 50 lines of code

### 3. Strategy Refresh Workflow
**Current**: n8n workflow querying SIL for updated strategy recommendations
**n8n Complexity**: Multiple HTTP nodes, data transformation
**Cloudflare Replacement**: Single Worker calling SIL API, 30 lines of code

### 4. Price Alert Workflow
**Current**: n8n listening for Kraken price alerts (not yet implemented)
**n8n Complexity**: WebSocket handling, persistence
**Cloudflare Replacement**: Worker + Durable Objects for WebSocket state

### 5. Order Fill Notification Workflow
**Current**: n8n monitoring order fills, sending alerts
**n8n Complexity**: Polling vs webhook confusion
**Cloudflare Replacement**: Webhook Worker, instant notifications

---

## Cloudflare Workers Architecture

### Workflow Types

#### 1. Cron Workers (Scheduled)
```javascript
// infrastructure/cloudflare/trading-cron/daily-health.js
export default {
  async scheduled(event, env, ctx) {
    try {
      const response = await fetch('https://95.217.51.24:8080/trading/health', {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${env.TRADING_API_KEY}`
        }
      });

      const health = await response.json();

      // Log to D1
      await env.DB.prepare(
        'INSERT INTO health_checks (timestamp, status, details) VALUES (?, ?, ?)'
      ).bind(
        new Date().toISOString(),
        health.all_systems_operational ? 'OK' : 'DEGRADED',
        JSON.stringify(health)
      ).run();

      // Alert if unhealthy
      if (!health.all_systems_operational) {
        await fetch(env.ALERT_WEBHOOK_URL, {
          method: 'POST',
          body: JSON.stringify({
            alert: 'Trading system unhealthy',
            details: health
          })
        });
      }

      return new Response('Health check complete', { status: 200 });
    } catch (error) {
      console.error('Health check failed:', error);
      return new Response('Error', { status: 500 });
    }
  }
}
```

**wrangler.toml**:
```toml
name = "trading-daily-health"
main = "daily-health.js"
compatibility_date = "2024-12-01"

[triggers]
crons = ["0 */4 * * *"]  # Every 4 hours

[[d1_databases]]
binding = "DB"
database_name = "rhiz-trading"
database_id = "xxx"

[vars]
ALERT_WEBHOOK_URL = "https://discord.com/api/webhooks/..."

[env.production.vars]
# TRADING_API_KEY set via: wrangler secret put TRADING_API_KEY
```

#### 2. Webhook Workers (Event-Driven)
```javascript
// infrastructure/cloudflare/trading-webhooks/order-fill.js
export default {
  async fetch(request, env, ctx) {
    if (request.method !== 'POST') {
      return new Response('Method not allowed', { status: 405 });
    }

    const orderFill = await request.json();

    // Validate signature (if from Kraken webhook)
    // ... signature verification ...

    // Store in D1
    await env.DB.prepare(
      'INSERT INTO order_fills (timestamp, order_id, price, volume) VALUES (?, ?, ?, ?)'
    ).bind(
      orderFill.timestamp,
      orderFill.order_id,
      orderFill.price,
      orderFill.volume
    ).run();

    // Send notification
    await fetch(env.DISCORD_WEBHOOK, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        content: `Order filled: ${orderFill.volume} @ ${orderFill.price}`
      })
    });

    return new Response('Order fill processed', { status: 200 });
  }
}
```

#### 3. Durable Objects (Stateful Workers)
```javascript
// infrastructure/cloudflare/trading-durable/price-monitor.js
export class PriceMonitor {
  constructor(state, env) {
    this.state = state;
    this.env = env;
  }

  async fetch(request) {
    const url = new URL(request.url);

    if (url.pathname === '/subscribe') {
      // WebSocket connection for real-time price updates
      const [client, server] = Object.values(new WebSocketPair());

      this.state.acceptWebSocket(server);

      return new Response(null, {
        status: 101,
        webSocket: client,
      });
    }

    if (url.pathname === '/price-update') {
      const { pair, price } = await request.json();

      // Broadcast to all connected clients
      this.state.getWebSockets().forEach(ws => {
        ws.send(JSON.stringify({ pair, price }));
      });

      return new Response('Price broadcast', { status: 200 });
    }
  }
}
```

---

## Migration Steps

### Phase 1: Infrastructure Setup (30 minutes)

1. **Create D1 Database**:
   ```bash
   wrangler d1 create rhiz-trading
   # Copy database_id to wrangler.toml
   ```

2. **Apply Schema**:
   ```sql
   -- infrastructure/cloudflare/trading-cron/schema.sql
   CREATE TABLE health_checks (
     id INTEGER PRIMARY KEY AUTOINCREMENT,
     timestamp TEXT NOT NULL,
     status TEXT NOT NULL,
     details TEXT
   );

   CREATE TABLE order_fills (
     id INTEGER PRIMARY KEY AUTOINCREMENT,
     timestamp TEXT NOT NULL,
     order_id TEXT NOT NULL,
     price REAL NOT NULL,
     volume REAL NOT NULL
   );

   CREATE TABLE strategy_executions (
     id INTEGER PRIMARY KEY AUTOINCREMENT,
     timestamp TEXT NOT NULL,
     strategy_name TEXT NOT NULL,
     outcome TEXT,
     notes TEXT
   );
   ```

   ```bash
   wrangler d1 execute rhiz-trading --file=schema.sql
   ```

3. **Set Secrets**:
   ```bash
   wrangler secret put TRADING_API_KEY
   wrangler secret put KRAKEN_API_KEY
   wrangler secret put KRAKEN_SECRET_KEY
   wrangler secret put DISCORD_WEBHOOK
   ```

### Phase 2: Deploy Cron Workers (1 hour)

1. **Daily Health Check**:
   ```bash
   cd infrastructure/cloudflare/trading-cron
   wrangler deploy daily-health.js --schedule "0 */4 * * *"
   ```

2. **Weekly DCA**:
   ```bash
   wrangler deploy weekly-dca.js --schedule "0 10 * * 1"  # Monday 10am
   ```

3. **Strategy Refresh**:
   ```bash
   wrangler deploy strategy-refresh.js --schedule "0 6 * * *"  # Daily 6am
   ```

### Phase 3: Deploy Webhook Workers (30 minutes)

1. **Order Fill Handler**:
   ```bash
   cd infrastructure/cloudflare/trading-webhooks
   wrangler deploy order-fill.js
   # Get URL: https://order-fill.YOUR_SUBDOMAIN.workers.dev
   ```

2. **Price Alert Handler**:
   ```bash
   wrangler deploy price-alert.js
   ```

### Phase 4: Deploy Durable Objects (1 hour - if needed)

1. **Price Monitor** (for WebSocket connections):
   ```bash
   cd infrastructure/cloudflare/trading-durable
   wrangler deploy price-monitor.js
   ```

### Phase 5: Verification (30 minutes)

1. **Test Cron Workers**:
   ```bash
   # Trigger manually to test
   wrangler tail trading-daily-health
   curl https://api.cloudflare.com/client/v4/accounts/ACCOUNT_ID/workers/scripts/trading-daily-health/schedules/trigger
   ```

2. **Test Webhook Workers**:
   ```bash
   curl -X POST https://order-fill.YOUR_SUBDOMAIN.workers.dev \
     -H "Content-Type: application/json" \
     -d '{"order_id": "test", "price": 100, "volume": 0.5, "timestamp": "2026-01-10T12:00:00Z"}'
   ```

3. **Check D1 Data**:
   ```bash
   wrangler d1 execute rhiz-trading --command "SELECT * FROM health_checks ORDER BY timestamp DESC LIMIT 5"
   ```

### Phase 6: Decommission n8n (15 minutes)

1. **Stop n8n on Hostinger**:
   ```bash
   ssh root@72.62.81.128
   docker stop n8n
   docker rm n8n
   ```

2. **Stop n8n on Hetzner**:
   ```bash
   ssh root@95.217.51.24
   docker stop n8n
   docker rm n8n
   ```

3. **Archive n8n Workflow Exports**:
   ```bash
   mkdir -p docs/archive/n8n_workflows_deprecated
   mv domains/trading/fathom_commander/n8n/*.json docs/archive/n8n_workflows_deprecated/
   mv domains/trading/strategic_intelligence/n8n_workflows/*.json docs/archive/n8n_workflows_deprecated/
   ```

4. **Update Documentation**:
   - Add deprecation notice to all n8n references
   - Update CLAUDE.md to remove n8n mentions
   - Document Cloudflare Workers as orchestration layer

---

## Benefits

### Reliability
- ✅ No more 502 errors (serverless, auto-scaling)
- ✅ No more auth token expiration issues
- ✅ Cloudflare's 99.99% uptime SLA

### Simplicity
- ✅ 20-50 lines of JavaScript vs. complex n8n GUI workflows
- ✅ Version control (workflows are code, not JSON exports)
- ✅ Easy to test locally (`wrangler dev`)

### Cost
- ✅ Free tier: 100,000 requests/day (more than enough for trading cron jobs)
- ✅ D1: 100,000 reads/day free
- ✅ No VPS resources wasted on n8n containers

### Maintainability
- ✅ Standard JavaScript (no n8n-specific knowledge needed)
- ✅ Clear error messages (not buried in n8n logs)
- ✅ Deployed in seconds (`wrangler deploy`)

---

## Comparison: n8n vs Cloudflare Workers

| Aspect | n8n | Cloudflare Workers |
|--------|-----|-------------------|
| **Reliability** | 502 errors common | 99.99% uptime |
| **Deployment** | Docker, port conflicts | `wrangler deploy` |
| **Auth** | Token management hell | Cloudflare handles auth |
| **Debugging** | Container logs, restarts | `wrangler tail` live logs |
| **Version Control** | JSON exports | Native Git |
| **Testing** | Manual via UI | `wrangler dev` locally |
| **Cost** | VPS resources (~5% CPU/RAM) | Free tier sufficient |
| **Time Wasted** | 13 hours (Captain's quote) | 0 hours |

---

## Workflow Migration Checklist

- [ ] Phase 1: Infrastructure setup (D1 database, secrets)
- [ ] Phase 2: Deploy cron Workers (health, DCA, strategy refresh)
- [ ] Phase 3: Deploy webhook Workers (order fill, price alert)
- [ ] Phase 4: Deploy Durable Objects (if WebSocket needed)
- [ ] Phase 5: Verification (test all Workers, check D1 data)
- [ ] Phase 6: Decommission n8n (stop containers, archive workflows)
- [ ] Update CLAUDE.md (remove n8n, add Cloudflare Workers)
- [ ] Update architecture docs (orchestration layer change)

---

## Rollback Plan

If Cloudflare Workers fail unexpectedly:
1. n8n containers still available (stopped, not deleted)
2. Restart n8n: `docker start n8n`
3. Import workflows from `docs/archive/n8n_workflows_deprecated/`
4. Debug Workers separately

**Rollback Time**: 10 minutes

---

## Timeline

- **Phase 1** (Infrastructure): 30 minutes
- **Phase 2** (Cron Workers): 1 hour
- **Phase 3** (Webhook Workers): 30 minutes
- **Phase 4** (Durable Objects): 1 hour (optional)
- **Phase 5** (Verification): 30 minutes
- **Phase 6** (Decommission): 15 minutes

**Total**: 3-4 hours (can be done in single session after unified platform migration)

---

## Success Criteria

✅ All trading workflows (health, DCA, strategy) running on Cloudflare Workers
✅ Zero 502 errors for 48 hours
✅ Cron schedules firing reliably
✅ D1 database receiving data from Workers
✅ n8n containers stopped and archived
✅ Documentation updated

---

## Next Steps

1. **Captain**: Approve this n8n decommission plan
2. **Captain**: Run `wrangler login` (enables deployment)
3. **First Mate**: Execute Phase 1-2 (infrastructure + cron Workers)
4. **First Mate**: Test cron Workers (trigger manually)
5. **First Mate**: Deploy webhook Workers (Phase 3)
6. **Both**: Monitor for 48 hours
7. **First Mate**: Decommission n8n (Phase 6)

---

**Decision**: Abandon n8n, migrate to Cloudflare Workers
**Rationale**: 13 hours wasted on n8n failures (Captain's directive)
**Risk**: LOW (Cloudflare Workers proven reliable for mooncheck)
**Impact**: HIGH (eliminates H6, improves reliability, reduces VPS load)

**Status**: AWAITING CAPTAIN APPROVAL + wrangler login
