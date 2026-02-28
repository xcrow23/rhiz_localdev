# Rhiz Deployment Procedures

**Purpose**: Operational checklists for deploying components to production
**Last Updated**: 2026-01-25 (Session 74)
**Scope**: VPS, Cloudflare Workers, MCP servers, Skills, Infrastructure

---

## Quick Index

| Deployment Type | Effort | Frequency | Last Updated |
|-----------------|--------|-----------|--------------|
| [VPS Deployment](#vps-deployment) | 2-4 hours | Once per component | Jan 25, 2026 |
| [Cloudflare Workers](#cloudflare-workers-deployment) | 30-60 min | Per worker | Jan 25, 2026 |
| [MCP Server](#mcp-server-deployment) | 1-2 hours | Once per server | Jan 25, 2026 |
| [Skill Deployment](#skill-deployment) | 30 min | Per skill | Jan 24, 2026 |
| [Infrastructure Updates](#infrastructure-updates) | Varies | As needed | Jan 25, 2026 |

---

## VPS Deployment

**Target**: Hostinger VPS (72.62.81.128)
**OS**: Ubuntu 22.04 LTS
**Container Runtime**: Docker + Docker Compose
**Reverse Proxy**: Traefik
**Current Services**: 9 containers operational

---

### Pre-Flight Checklist

**Requirements**:
- [ ] Captain VPS SSH credentials (required for deployment)
- [ ] Component Docker image built and tested locally
- [ ] Component documentation complete (README, architecture)
- [ ] Health check endpoint implemented
- [ ] Environment variables defined (document in .env.example)
- [ ] Traefik labels configured (if HTTP service)
- [ ] Integration points identified (what depends on this, what this depends on)

**Risk Assessment**:
- [ ] Will this change affect running services?
- [ ] Is rollback plan documented?
- [ ] Are database migrations reversible?
- [ ] Is paper mode enforced (if trading-related)?

---

### Deployment Steps

#### Step 1: SSH Access

```bash
# SSH into VPS (requires Captain credentials)
ssh username@72.62.81.128

# Verify current working directory
pwd
# Should be: /home/username or similar

# Navigate to deployment directory
cd /opt/rhiz  # Or wherever docker-compose.yml lives
```

**Verification**: Can access VPS and deployment directory exists

---

#### Step 2: Update Docker Compose Configuration

```bash
# Backup current configuration
cp docker-compose.yml docker-compose.yml.backup.$(date +%Y%m%d_%H%M%S)

# Edit docker-compose.yml
nano docker-compose.yml

# Add new service
# Example for new component:
services:
  new_component:
    image: rhiz/new_component:latest
    container_name: new_component
    restart: unless-stopped
    networks:
      - traefik_public
      - internal
    environment:
      - ENV_VAR_1=value1
      - ENV_VAR_2=value2
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.new_component.entrypoints=websecure"
      - "traefik.http.routers.new_component.rule=Host(`component.example.com`)"
      - "traefik.http.routers.new_component.tls=true"
      - "traefik.http.services.new_component.loadbalancer.server.port=8000"
    volumes:
      - ./new_component_data:/data
    depends_on:
      - redis
      - postgresql
```

**Verification**: docker-compose.yml syntax valid

```bash
# Validate syntax
docker-compose config
# Should show parsed configuration without errors
```

---

#### Step 3: Environment Variables & Secrets

```bash
# Edit .env file (if using env_file in docker-compose)
nano .env

# Add new component's environment variables
NEW_COMPONENT_API_KEY=secret_value_here
NEW_COMPONENT_DATABASE_URL=postgresql://user:pass@postgresql:5432/db

# Or use Docker secrets (more secure)
echo "secret_value_here" | docker secret create new_component_api_key -
```

**Security Note**: NEVER commit .env files to git. Use .env.example as template.

**Verification**: Secrets are set and accessible

```bash
# For .env file
cat .env | grep NEW_COMPONENT
# Should show variables (be careful in logs)

# For Docker secrets
docker secret ls
# Should show new_component_api_key
```

---

#### Step 4: Network Configuration

```bash
# Verify networks exist
docker network ls | grep traefik_public
docker network ls | grep internal

# If traefik_public doesn't exist, create it
docker network create traefik_public

# Internal network is created by docker-compose automatically
```

**Verification**: Required networks exist

---

#### Step 5: Deploy Container

```bash
# Pull latest images
docker-compose pull new_component

# Start new service (detached mode)
docker-compose up -d new_component

# Watch logs for startup
docker logs -f new_component
# Look for:
# - "Server started" or equivalent
# - Health check endpoint responding
# - No error messages
```

**Verification**: Container running and healthy

```bash
# Check container status
docker ps | grep new_component
# Should show status "Up X minutes (healthy)" or similar

# Check container logs
docker logs new_component --tail 50
# Should show successful startup
```

---

#### Step 6: Health Check Verification

```bash
# Test health endpoint (inside container network)
docker exec traefik curl http://new_component:8000/health
# Should return: {"status":"ok"} or equivalent

# Test external routing (via Traefik)
curl https://component.example.com/health
# Should return: {"status":"ok"}
```

**Verification**: Health check passes both internally and externally

---

#### Step 7: Integration Testing

**Test Connections**:
```bash
# If depends on Redis
docker exec new_component redis-cli -h redis ping
# Should return: PONG

# If depends on PostgreSQL
docker exec new_component psql -h postgresql -U user -d db -c "SELECT 1"
# Should return: 1

# If depends on other services
docker exec new_component curl http://other_service:port/health
# Should return service health
```

**Verification**: All dependencies accessible

---

#### Step 8: DNS Configuration (if new domain)

**Cloudflare DNS**:
1. Log in to Cloudflare dashboard
2. Select domain: dreamthewilderness.com
3. Add DNS record:
   - Type: A
   - Name: component (or subdomain)
   - Content: 72.62.81.128
   - Proxy: Enabled (orange cloud)
   - TTL: Auto
4. Save

**Verification**: DNS resolves correctly

```bash
# From local machine
nslookup component.dreamthewilderness.com
# Should return: 72.62.81.128 (via Cloudflare proxy)

# Wait 30-60 seconds for DNS propagation
sleep 60

# Test HTTPS access
curl -I https://component.dreamthewilderness.com/health
# Should return: HTTP/2 200 OK
```

---

#### Step 9: Monitoring & Alerts (Optional)

```bash
# Add to monitoring dashboard (if using)
# Add Prometheus scrape config
# Add Grafana dashboard
# Configure alerts (if critical service)
```

**Verification**: Monitoring configured and collecting metrics

---

#### Step 10: Documentation Update

**Update Files**:
- [ ] `docs/knowledge_base/deployments/vps_topology.md` (add new service to container inventory)
- [ ] `docs/CURRENT_STATE.md` (update component status to deployed)
- [ ] Write checkpoint documenting deployment (session_end)

**Verification**: Documentation accurate and current

---

### Post-Deployment Verification

**24-Hour Checklist**:
- [ ] Container still running (no crashes)
- [ ] Health check still passing
- [ ] Logs show expected behavior
- [ ] No error spikes
- [ ] Integration points functional
- [ ] Resource usage normal (CPU, RAM, disk)

**Rollback Plan** (if issues):
```bash
# Stop new service
docker-compose stop new_component

# Remove container
docker-compose rm new_component

# Restore previous configuration
cp docker-compose.yml.backup.YYYYMMDD_HHMMSS docker-compose.yml

# Restart services
docker-compose up -d
```

---

### Example: Fathom Commander Deployment

**Reference**: Session 6 (Jan 3, 2026) - Infrastructure operational

**Pre-Flight**:
- [x] Captain VPS access confirmed
- [x] FC Docker image built (`rhiz/fathom_commander:latest`)
- [x] README complete (27 MCP tools documented)
- [x] Health check endpoint: `/api/health`
- [x] Environment variables: KRAKEN_API_KEY, REDIS_URL, DATABASE_URL
- [x] Traefik labels configured for `fc.dreamthewilderness.com`

**Deployment**:
1. SSH to VPS ✅
2. Updated docker-compose.yml with FC service ✅
3. Set environment variables in .env ✅
4. Verified traefik_public network ✅
5. `docker-compose up -d fathom_commander` ✅
6. Health check passed: `curl http://fc:8000/api/health` ✅
7. External routing: `curl https://fc.dreamthewilderness.com/api/health` ✅
8. Integration test: FC → Fathom connection validated ✅
9. DNS already configured (fc.dreamthewilderness.com → 72.62.81.128) ✅
10. Documentation updated ✅

**Outcome**: FC operational, 27 MCP tools accessible

---

## Cloudflare Workers Deployment

**Target**: Cloudflare Edge (300+ global data centers)
**Account**: dream_the_wilderness
**Plan**: Free tier (100,000 requests/day)
**Deployment Tool**: wrangler CLI

---

### Pre-Flight Checklist

**Requirements**:
- [ ] Worker code written (TypeScript recommended)
- [ ] wrangler CLI installed (`npm install -g wrangler`)
- [ ] Cloudflare account authenticated (`wrangler login`)
- [ ] wrangler.toml configured
- [ ] Environment variables defined (use wrangler secrets)
- [ ] VPS endpoints accessible (if calling backend)
- [ ] Testing complete (local dev server: `wrangler dev`)

---

### Deployment Steps

#### Step 1: Install & Authenticate wrangler

```bash
# Install wrangler globally
npm install -g wrangler

# Authenticate with Cloudflare
wrangler login
# Opens browser for OAuth flow

# Verify authentication
wrangler whoami
# Should show account email and account ID
```

**Verification**: wrangler authenticated

---

#### Step 2: Write Worker Code

```typescript
// worker.ts - Example scheduled worker (cron)
export default {
  async scheduled(event, env, ctx) {
    // Step 1: Call VPS backend
    const response = await fetch(
      `${env.BACKEND_URL}/api/endpoint`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${env.API_TOKEN}`
        },
        body: JSON.stringify({ data: "value" })
      }
    );

    const result = await response.json();

    // Step 2: Post to Slack (if configured)
    if (env.SLACK_WEBHOOK_URL) {
      await fetch(env.SLACK_WEBHOOK_URL, {
        method: "POST",
        body: JSON.stringify({
          text: `Result: ${result.message}`
        })
      });
    }

    return new Response(JSON.stringify(result));
  }
};
```

**Verification**: Worker code compiles without errors

---

#### Step 3: Configure wrangler.toml

```toml
name = "example-worker"
main = "worker.ts"
compatibility_date = "2024-01-01"

# Cron triggers (optional)
[triggers]
crons = ["0 8,20 * * *"]  # 8AM & 8PM daily

# Environment variables (non-secret)
[vars]
BACKEND_URL = "http://95.217.51.24:8000"

# Secrets (set via wrangler secret put, not committed)
# API_TOKEN
# SLACK_WEBHOOK_URL
```

**Verification**: wrangler.toml syntax valid

```bash
# Validate configuration
wrangler dev
# Should start local development server without errors
```

---

#### Step 4: Set Secrets

```bash
# Set API token
wrangler secret put API_TOKEN
# Enter secret value when prompted (not echoed)

# Set Slack webhook (if using)
wrangler secret put SLACK_WEBHOOK_URL
# Enter webhook URL

# List secrets (values not shown)
wrangler secret list
# Should show: API_TOKEN, SLACK_WEBHOOK_URL
```

**Verification**: Secrets configured

---

#### Step 5: Test Locally

```bash
# Start local development server
wrangler dev

# Trigger scheduled event manually (in another terminal)
curl http://localhost:8787/__scheduled
# Should execute worker and return response

# Check logs
# Logs appear in wrangler dev terminal
```

**Verification**: Worker executes successfully locally

---

#### Step 6: Deploy to Production

```bash
# Deploy worker
wrangler deploy

# Output will show:
# - Total Upload size
# - Published worker name
# - Worker URL: https://example-worker.dream-the-wilderness.workers.dev
# - Deployment ID
```

**Verification**: Deployment successful

```bash
# Check deployment status
wrangler deployments list example-worker

# Should show latest deployment with timestamp
```

---

#### Step 7: Test Production Endpoint

```bash
# Test HTTP endpoint (if worker has fetch handler)
curl https://example-worker.dream-the-wilderness.workers.dev

# For scheduled workers, wait for cron trigger or check logs
wrangler tail example-worker --format pretty

# Trigger scheduled worker manually (testing only)
# Use Cloudflare dashboard -> Workers -> example-worker -> Triggers -> Test
```

**Verification**: Worker responding in production

---

#### Step 8: Monitor Logs

```bash
# Live tail logs
wrangler tail example-worker --format pretty

# Keep running to see executions
# Press Ctrl+C to stop
```

**Verification**: Logs show expected behavior

---

### Post-Deployment Verification

**24-Hour Checklist**:
- [ ] Cron triggers firing on schedule (check logs)
- [ ] No 5xx errors (check Cloudflare dashboard)
- [ ] Execution time within limits (<10ms free tier)
- [ ] Request count within quota (100k/day free tier)
- [ ] VPS endpoints responding (if calling backend)
- [ ] Slack notifications working (if configured)

**Rollback Plan**:
```bash
# List deployments
wrangler deployments list example-worker

# Rollback to previous deployment (get ID from list)
wrangler rollback example-worker --deployment-id <previous_deployment_id>
```

---

### Example: Mooncheck Deployment

**Reference**: Session 40 (Jan 11, 2026) - Mooncheck migration complete

**Pre-Flight**:
- [x] Worker code: 70 lines TypeScript (vs 2,847 lines n8n JSON)
- [x] wrangler authenticated ✅
- [x] wrangler.toml configured (cron: 0 8,20 * * *) ✅
- [x] Secrets: MOONCHECK_TOKEN, SLACK_WEBHOOK_URL ✅
- [x] VPS endpoint: http://95.217.51.24:8000/mooncheck/trigger ✅
- [x] Local testing: ✅

**Deployment**:
1. `wrangler deploy` ✅
2. Deployment URL: https://mooncheck.dream-the-wilderness.workers.dev ✅
3. Cron configured: 8AM & 8PM CT ✅
4. Production test: Manual trigger via dashboard ✅
5. VPS call successful ✅
6. Slack notification posted ✅
7. 24-hour monitoring: No errors ✅

**Outcome**: Mooncheck operational, 100% reliability since deployment

---

## MCP Server Deployment

**Target**: Local development environment (Dell Inspiron)
**Protocol**: stdio (Model Context Protocol)
**Configuration**: Claude Code `.mcp.json`

---

### Pre-Flight Checklist

**Requirements**:
- [ ] MCP server code complete (Python recommended)
- [ ] Tool definitions follow MCP schema
- [ ] README documentation complete
- [ ] Testing complete (unit tests + integration tests)
- [ ] Health check implemented
- [ ] Environment variables documented
- [ ] Dependencies listed (requirements.txt or package.json)

---

### Deployment Steps

#### Step 1: Install Dependencies

```bash
# Navigate to MCP server directory
cd tools/example-mcp

# Create virtual environment (Python)
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

**Verification**: Dependencies installed

```bash
pip list
# Should show all required packages
```

---

#### Step 2: Test Server Standalone

```bash
# Run server in test mode
python server.py --test

# Should output available tools and health status
```

**Verification**: Server starts without errors

---

#### Step 3: Configure Claude Code

```json
// .mcp.json (in Claude Code config directory)
{
  "mcpServers": {
    "example-mcp": {
      "command": "python",
      "args": ["C:\\Users\\dread\\documents\\rhiz_localdev\\tools\\example-mcp\\server.py"],
      "env": {
        "RHIZ_ROOT": "C:\\Users\\dread\\documents\\rhiz_localdev",
        "QDRANT_HOST": "localhost",
        "QDRANT_PORT": "6333"
      }
    }
  }
}
```

**Verification**: Configuration syntax valid (JSON lint)

---

#### Step 4: Test MCP Integration

```bash
# Restart Claude Code (reload config)
# Open new session

# Test tool availability
# In Claude Code prompt:
# "Use example_tool from example-mcp"

# Claude should recognize tool and use it
```

**Verification**: Claude Code can invoke MCP tools

---

#### Step 5: Integration Testing

**Test Each Tool**:
1. Call tool with valid parameters
2. Verify expected output
3. Test error handling (invalid params)
4. Test edge cases

**Example**:
```python
# Test get_data tool
example_get_data(query="test")  # Should return test data
example_get_data(query="")      # Should handle empty query
example_get_data(query=None)    # Should handle null
```

**Verification**: All tools functional

---

### Post-Deployment Verification

**Session Start Checklist**:
- [ ] MCP server starts automatically (session hook)
- [ ] All tools available (check tool list)
- [ ] Health check passes
- [ ] No startup errors in logs

**Ongoing Monitoring**:
- [ ] Tool invocations successful
- [ ] Response times acceptable (<1s for most tools)
- [ ] Error rate low (<1%)

---

### Example: rhiz-mcp Deployment

**Reference**: Sessions 1-73 (Dec 17, 2025 - Jan 25, 2026)

**Pre-Flight**:
- [x] 11 tools implemented (dyad state, checkpoints, memory context)
- [x] README complete (tool catalog)
- [x] Testing: All tools validated
- [x] Health check: `get_dyad_state()` as health indicator
- [x] Environment: RHIZ_ROOT set in .mcp.json
- [x] Dependencies: pyyaml, qdrant-client

**Deployment**:
1. Dependencies installed: `pip install -r requirements.txt` ✅
2. Standalone test: `python server.py --test` ✅
3. .mcp.json configured with rhiz-mcp entry ✅
4. Claude Code restarted ✅
5. Tool availability verified ✅
6. Integration test: `get_dyad_state()` successful ✅

**Outcome**: rhiz-mcp operational, 11 tools available in all sessions

---

## Skill Deployment

**Target**: Local Qdrant (localhost:6333)
**Collection**: rhiz_skills
**Accuracy Target**: >85% (currently 93.3%)

---

### Pre-Flight Checklist

**Requirements**:
- [ ] Skill definition complete (YAML format)
- [ ] Utterances defined (20-100 examples)
- [ ] Primitives identified (skill building blocks)
- [ ] Category assigned (trading, memory, infrastructure, research)
- [ ] Testing complete (routing accuracy validation)
- [ ] Mem0 memories ready (if memory-augmented)

---

### Deployment Steps

#### Step 1: Create Skill Definition

```yaml
# File: core/skills/registry/domain_skillname.yaml
name: domain/skillname
description: |
  Brief description of what this skill does.
  Multi-line if needed.

category: domain_name  # trading, memory, infrastructure, research

utterances:
  - example query 1
  - example query 2
  - example query 3
  # ... 20-100 utterances recommended

primitives:
  - primitive_1: Description of building block 1
  - primitive_2: Description of building block 2

tools:
  - tool_name_1  # MCP tool this skill uses
  - tool_name_2

metadata:
  created_at: 2026-01-25
  version: 1.0.0
  accuracy_target: 0.85
```

**Verification**: YAML syntax valid

```bash
python -c "import yaml; yaml.safe_load(open('core/skills/registry/domain_skillname.yaml'))"
# Should parse without errors
```

---

#### Step 2: Generate Skill Fingerprint

```bash
# Navigate to skills directory
cd core/skills

# Generate fingerprint embedding
python generate_fingerprints.py --skill domain/skillname

# Output will show:
# - Skill name
# - Fingerprint dimension (should be 384)
# - Generated embedding vector
# - Stored in Qdrant collection: rhiz_skills
```

**Verification**: Fingerprint stored in Qdrant

```bash
# Check Qdrant collection
curl http://localhost:6333/collections/rhiz_skills
# Should show count incremented by 1
```

---

#### Step 3: Test Routing Accuracy

```bash
# Create test queries for this skill
# File: core/skills/test_queries.yaml
test_queries:
  domain/skillname:
    - query: "Test query 1"
      expected_skill: domain/skillname
    - query: "Test query 2"
      expected_skill: domain/skillname
    # ... 5-10 test queries

# Run routing accuracy test
python test_routing_accuracy.py --skill domain/skillname

# Should show:
# - Queries tested: 10
# - Correct routing: 9
# - Accuracy: 90%
# - Target: >85% ✅
```

**Verification**: Accuracy >85%

---

#### Step 4: Create Mem0 Memories (Optional)

```python
# If skill is memory-augmented
from mem0 import Memory

mem0 = Memory()

# Add skill-specific memories
mem0.add(
    "Skill domain/skillname was used to accomplish X in session Y",
    user_id="domain/skillname",
    metadata={"session": "session_74", "outcome": "successful"}
)

# Verify memories stored
memories = mem0.get_all(user_id="domain/skillname")
print(f"Stored {len(memories)} memories for skill")
```

**Verification**: Memories stored in rhiz_skill_memory collection

---

#### Step 5: Update Skill Registry

```python
# File: core/skills/router.py
# Registry updated automatically by generate_fingerprints.py
# Verify skill appears in registry:

from core.skills.router import SkillRouter
router = SkillRouter()
router.load_skills()

print([skill.name for skill in router.skills])
# Should include: domain/skillname
```

**Verification**: Skill in active registry

---

#### Step 6: Integration Test

```bash
# Test end-to-end routing
python -c "
from core.skills.router import SkillRouter

router = SkillRouter()
result = router.route('test query for new skill')

print(f'Routed to: {result.skill_name}')
print(f'Confidence: {result.score:.2f}')
print(f'Expected: domain/skillname')
"

# Should route to domain/skillname with score >0.25
```

**Verification**: Routing works end-to-end

---

### Post-Deployment Verification

**24-Hour Checklist**:
- [ ] Skill routes correctly in real sessions
- [ ] Memory-augmented activation works (if applicable)
- [ ] Accuracy maintained across diverse queries
- [ ] No false positives (routing when shouldn't)

---

### Example: trading/kraken_analysis Deployment

**Reference**: Sessions 71-72 (Jan 24, 2026)

**Pre-Flight**:
- [x] Skill definition: core/skills/registry/trading_kraken_analysis.yaml
- [x] Utterances: 97 examples (expanded from 45)
- [x] Primitives: market_analysis, price_monitoring, trade_decision
- [x] Category: trading
- [x] Testing: 93.3% accuracy (28/30 correct)
- [x] Mem0 memories: 3 stored from session activations

**Deployment**:
1. YAML definition created ✅
2. Fingerprint generated: `python generate_fingerprints.py` ✅
3. Routing test: 93.3% accuracy (exceeds 85% target) ✅
4. Mem0 memories: 3 stored ✅
5. Registry updated: trading/kraken_analysis active ✅
6. Integration test: Routes correctly ✅

**Outcome**: trading/kraken_analysis operational, 100% test queries correct (8/8)

---

## Infrastructure Updates

### Docker Container Updates

```bash
# Pull latest images
docker-compose pull

# Restart services with new images
docker-compose up -d

# Verify no errors
docker-compose logs --tail 50
```

---

### Qdrant Collection Updates

```bash
# Backup collection before updates
curl -X POST http://localhost:6333/collections/rhiz_memories/snapshots

# Update collection settings (if needed)
curl -X PATCH http://localhost:6333/collections/rhiz_memories \
  -H "Content-Type: application/json" \
  -d '{
    "optimizers_config": {
      "indexing_threshold": 20000
    }
  }'
```

---

### Cloudflare DNS Updates

1. Log in to Cloudflare dashboard
2. Select domain: dreamthewilderness.com
3. Update DNS record (edit existing or add new)
4. Wait 30-60 seconds for propagation
5. Verify: `nslookup subdomain.dreamthewilderness.com`

---

## Common Issues & Resolutions

### Issue: Container Won't Start

**Symptom**: `docker-compose up -d` fails

**Diagnosis**:
```bash
# Check logs
docker-compose logs service_name

# Common causes:
# - Port already in use
# - Missing environment variables
# - Volume mount permission denied
# - Dependency service not running
```

**Resolution**: Fix identified issue, retry deployment

---

### Issue: Health Check Fails

**Symptom**: `curl http://service/health` returns error

**Diagnosis**:
```bash
# Check if service is running
docker ps | grep service_name

# Check logs
docker logs service_name

# Test from inside container
docker exec service_name curl http://localhost:port/health
```

**Resolution**: Fix service startup issue, redeploy

---

### Issue: Traefik Routing Not Working

**Symptom**: External URL returns 404 or 502

**Diagnosis**:
```bash
# Check Traefik dashboard
http://localhost:8080

# Verify router exists
curl http://localhost:8080/api/http/routers

# Check service labels
docker inspect service_name | grep -A 20 Labels
```

**Resolution**: Fix Traefik labels in docker-compose.yml, restart

---

## Related Documentation

**Component Deployment**:
- VPS topology: `docs/knowledge_base/deployments/vps_topology.md`
- Cloudflare Workers: `docs/knowledge_base/deployments/cloudflare_workers.md`
- Local development: `docs/knowledge_base/deployments/local_development.md`

**Troubleshooting**:
- Comprehensive guide: `docs/TROUBLESHOOTING.md`
- Failure genealogy: `docs/knowledge_base/decisions/failure_genealogy.md`

**Architecture**:
- VPS infrastructure: `docs/architecture/vps_infrastructure_topology.md`
- Skills system: `docs/knowledge_base/components/skills_system.md`
- Memory system: `docs/knowledge_base/components/memory_system.md`

---

**End of Deployment Procedures**

*Last Updated: 2026-01-25 (Session 74)*
*Coverage: VPS, Cloudflare Workers, MCP Servers, Skills, Infrastructure*
*Next Update: After Phase 2 deployments (integration workflows)*
