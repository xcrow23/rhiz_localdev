# Rhiz Infrastructure Expansion Plan
## December 24, 2025 - Moment 2 Architecture Session

---

## Current State

### Local (Inspiron 15)
| Service | Status | Port |
|---------|--------|------|
| Qdrant | ✅ Healthy | 6333/6334 |
| Redis | ✅ Running | 6379 |
| Hummingbot CLI | ❌ Wrong architecture | - |
| LocalAI | ⏸️ Stopped | 8080 |

### Cloud
| Platform | Status | Resources |
|----------|--------|-----------|
| Cloudflare | ✅ Connected | 1 Worker (permaculture-ai), no D1/KV |
| Hostinger | 🔧 Available | VPS + n8n (needs verification) |
| GitHub | 🔧 Available | Repos accessible |

### MCP Connectors (Claude Desktop)
- ✅ Cloudflare Developer Platform
- ✅ Desktop Commander
- ✅ Windows-MCP
- ✅ Filesystem
- ⏸️ Hummingbot (needs API stack)

---

## Target Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           RHIZ INFRASTRUCTURE                           │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                    LOCAL (Inspiron 15)                          │   │
│  │                                                                  │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │   │
│  │  │   Qdrant     │  │    Redis     │  │   LocalAI    │          │   │
│  │  │  (vectors)   │  │   (cache)    │  │  (inference) │          │   │
│  │  │  :6333-6334  │  │    :6379     │  │    :8080     │          │   │
│  │  └──────────────┘  └──────────────┘  └──────────────┘          │   │
│  │                                                                  │   │
│  │  ┌──────────────────────────────────────────────────────────┐   │   │
│  │  │              HUMMINGBOT API STACK (NEW)                  │   │   │
│  │  │                                                          │   │   │
│  │  │  ┌─────────┐ ┌─────────┐ ┌──────────┐ ┌─────────────┐   │   │   │
│  │  │  │  EMQX   │ │Postgres │ │ Backend  │ │  Dashboard  │   │   │   │
│  │  │  │ broker  │ │   DB    │ │   API    │ │  (Web UI)   │   │   │   │
│  │  │  │ :1883   │ │ :5432   │ │  :8000   │ │   :8501     │   │   │   │
│  │  │  └─────────┘ └─────────┘ └──────────┘ └─────────────┘   │   │   │
│  │  │                    ↑                                     │   │   │
│  │  │                    │ MCP Connection                      │   │   │
│  │  │                    ↓                                     │   │   │
│  │  │  ┌──────────────────────────────────────────────────┐   │   │   │
│  │  │  │           HUMMINGBOT MCP SERVER                  │   │   │   │
│  │  │  │  (hummingbot/hummingbot-mcp:latest)              │   │   │   │
│  │  │  │  → Tools: setup_connector, deploy_bot,           │   │   │   │
│  │  │  │    get_portfolio, place_order, etc.              │   │   │   │
│  │  │  └──────────────────────────────────────────────────┘   │   │   │
│  │  └──────────────────────────────────────────────────────────┘   │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                              ↑                                          │
│                              │ Webhooks / API                           │
│                              ↓                                          │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                      HOSTINGER VPS                              │   │
│  │                                                                  │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │   │
│  │  │     n8n      │  │   Webhook    │  │   Cron/      │          │   │
│  │  │ orchestrator │←→│   Receiver   │  │  Scheduled   │          │   │
│  │  │              │  │              │  │    Tasks     │          │   │
│  │  └──────────────┘  └──────────────┘  └──────────────┘          │   │
│  │                                                                  │   │
│  │  Future: Mirror of Hummingbot API for 24/7 operation            │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                              ↑                                          │
│                              │ Edge Functions                           │
│                              ↓                                          │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                      CLOUDFLARE EDGE                            │   │
│  │                                                                  │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │   │
│  │  │   Workers    │  │      D1      │  │      KV      │          │   │
│  │  │  (compute)   │  │  (database)  │  │   (cache)    │          │   │
│  │  └──────────────┘  └──────────────┘  └──────────────┘          │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                              ↑                                          │
│                              │ CI/CD                                    │
│                              ↓                                          │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                         GITHUB                                  │   │
│  │                                                                  │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │   │
│  │  │  Rhiz Repo   │  │   Strategy   │  │   Actions    │          │   │
│  │  │   (main)     │  │   Configs    │  │   (CI/CD)    │          │   │
│  │  └──────────────┘  └──────────────┘  └──────────────┘          │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Implementation Phases

### Phase 1: Hummingbot API Stack (Local) — TODAY
**Goal**: Replace CLI container with full API stack for MCP access

1. Clone hummingbot/deploy repo
2. Run setup.sh to create:
   - EMQX broker
   - PostgreSQL database  
   - Backend API (port 8000)
   - Dashboard (port 8501)
3. Configure MCP server in Claude Desktop config
4. Test Kraken connector setup via MCP tools

**Result**: Full trading capability via NLP/tools

### Phase 2: GitHub Integration — THIS WEEK
**Goal**: Version control for strategies and configs

1. Initialize git in Rhiz_LocalDev (if not done)
2. Create private repo on GitHub
3. Push current state
4. Set up .gitignore for secrets

**Result**: Backup, history, collaboration-ready

### Phase 3: Hostinger Verification — THIS WEEK  
**Goal**: Confirm n8n is operational, create webhook endpoints

1. SSH into Hostinger VPS
2. Verify n8n installation
3. Create test webhook workflow
4. Test Claude → n8n → response flow

**Result**: Cloud orchestration capability

### Phase 4: Cross-Platform Integration — NEXT WEEK
**Goal**: Connect all pieces

1. n8n workflow: Scheduled portfolio checks
2. Cloudflare Worker: Lightweight API gateway
3. GitHub Actions: Deploy strategy updates
4. Webhook chain: Alert → n8n → Local API

---

## Hummingbot MCP Configuration

Once API stack is running, add to Claude Desktop config:

```json
{
  "mcpServers": {
    "hummingbot": {
      "command": "docker",
      "args": [
        "run", "--rm", "-i",
        "-e", "HUMMINGBOT_API_URL=http://host.docker.internal:8000",
        "-v", "hummingbot_mcp:/root/.hummingbot_mcp",
        "hummingbot/hummingbot-mcp:latest"
      ]
    }
  }
}
```

---

## Tool Access Matrix (Post-Implementation)

| Action | Method | Automation Level |
|--------|--------|------------------|
| Check portfolio | MCP tool | Direct prompt |
| Place order | MCP tool | Direct prompt |
| Deploy strategy | MCP tool + config | Semi-automated |
| Rebalance | n8n webhook + MCP | Fully automated |
| Risk alerts | n8n scheduled | Fully automated |
| Strategy backtest | Dashboard UI | Manual |

---

## Security Considerations

1. **API Credentials**: Already in .env (Kraken configured)
2. **Hummingbot Auth**: Set strong password in deploy/.env
3. **n8n Webhooks**: Use authentication tokens
4. **GitHub**: Private repo, no secrets in commits
5. **Cloudflare**: API tokens scoped to minimum permissions

---

## Questions for Captain

1. **Hostinger Access**: Can you confirm SSH access and n8n status?
2. **GitHub Repo**: Create new or use existing? Public or private?
3. **24/7 Requirement**: Do we need Hummingbot running on VPS eventually?
4. **Strategy Priority**: Which Kraken pairs/strategies first?

---

*Document created: December 24, 2025*
*Contributors: Alexander Chandrea & Claude Opus 4.5*
