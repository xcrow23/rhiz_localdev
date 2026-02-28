# n8n & Hostinger MCP Audit - Session 25

**Date**: 2026-01-05
**Auditor**: First Mate Daemon
**n8n Server**: https://n8n.srv1206808.hstgr.cloud
**Hostinger API**: Via CLI MCP server

---

## Executive Summary

Both n8n and Hostinger API MCPs are operational and responding. n8n shows 10+ workflows deployed (7 active), including the newly created Mooncheck workflow. Hostinger API provides cloud infrastructure management capabilities.

**Status**:
- ✅ n8n MCP: Connected, operational
- ✅ Hostinger API MCP: Connected, operational
- 📋 Mooncheck workflow: Created but inactive (ready to activate)
- 🔍 MCP endpoint discovery: Custom endpoint `/mcp-server/http` documented but not yet tested

---

## n8n MCP Server

### Connection Info
**Host**: `https://n8n.srv1206808.hstgr.cloud`
**Auth**: N8N_API_KEY environment variable
**MCP Type**: stdio (CLI executable)
**Command**: `n8n-mcp-server.exe`

### Current Workflows (10 visible, more exist)

| ID | Name | Status | Created | Purpose |
|----|------|--------|---------|---------|
| 7adc34e895274222 | Rhiz Weekly Strategy Review | ✅ Active | 2025-12-29 | Weekly trading strategy analysis |
| 80UHC4upU5EodhKY | SIL Strategy Selection (Fixed) | ✅ Active | 2026-01-04 | Strategic Intelligence Layer strategy picker |
| 929455ca7da34cb4 | Rhiz Portfolio Rebalancer | ✅ Active | 2025-12-29 | Automated portfolio rebalancing |
| 97807e32675f4ac7 | Rhiz Volatility Sentinel | ✅ Active | 2025-12-29 | Volatility monitoring and alerts |
| AKIJQerSeilq4xjF | Rhiz Risk Monitor | ✅ Active | 2025-12-29 | Risk threshold monitoring |
| GAgiQDdHKLjgT85k | Rhiz Smart DCA | ✅ Active | 2025-12-29 | Dollar-cost averaging automation |
| LfO8CCuyrjj45z4P | Rhiz Daily Health Monitor | ✅ Active | 2025-12-28 | System health checks |
| BcoxdWWb7wbAsQZR | **Mooncheck - Blog Transcript Capture** | ⚠️ Inactive | 2026-01-05 | Voice transcript → Qdrant (NEW) |
| RhczIyo6Lyr3L83Q | SIL Strategy Selection | 🗃️ Archived | 2026-01-04 | Deprecated version |
| WS6MuoyOXxaiBIwy | SIL Strategy Selection (Fixed) | 🗃️ Archived | 2026-01-04 | Deprecated duplicate |

**Note**: Pagination cursor indicates more workflows exist beyond this first page.

### MCP Tools Available

The n8n MCP provides extensive workflow management capabilities. Key tools tested:

#### Workflow Management
- ✅ `list_workflows_minimal` - List workflows without full node data (TESTED)
- ⚠️ `Retrieve_all_workflows` - Full workflow retrieval with nodes/connections (UNTESTED)
- ⚠️ `get_workflow_summary` - Workflow metadata without node details (UNTESTED)
- ⚠️ `Create_a_workflow` - Create new workflow (UNTESTED - use with caution)
- ⚠️ `Update_a_workflow` - Update existing workflow (UNTESTED)
- ⚠️ `partial_update_workflow` - Update specific nodes (UNTESTED)
- ⚠️ `add_nodes_to_workflow` - Add nodes and rewire connections (UNTESTED)

#### File-Based Operations
- ⚠️ `create_workflow_from_file` - Import workflow from JSON file (UNTESTED)
- ⚠️ `update_workflow_from_file` - Update from JSON file (UNTESTED)
- ⚠️ `export_workflow_to_file` - Export to JSON file (UNTESTED)

#### Workflow Control
- ⚠️ `Activate_a_workflow` - Enable workflow execution (NEEDED for Mooncheck)
- ⚠️ `Deactivate_a_workflow` - Disable workflow (UNTESTED)

#### Execution Monitoring
- ⚠️ `Retrieve_all_executions` - Get execution history (UNTESTED)
- ⚠️ `Retrieve_an_execution` - Get specific execution details (UNTESTED)

### Known Issues

#### MCP Endpoint Discovery (Session 24)
**Issue**: n8n has a custom MCP-specific endpoint at `/mcp-server/http` distinct from the standard API endpoint.
**Status**: Documented but not yet integrated with programmatic workflow deployment.
**Blocker**: MCP client configuration location unknown.
**Impact**: Manual workflow import required (programmatic deployment not yet automated).

**From Session 24**:
- Attempted programmatic workflow deployment via MCP tools
- Hit schema validation errors
- Discovered custom endpoint requires specific JWT token configuration
- Deferred automation, created manual workflow JSON instead

### Mooncheck Workflow Status

**Created**: 2026-01-05 03:48:02 (Session 24)
**ID**: BcoxdWWb7wbAsQZR
**Status**: Inactive (ready to activate)

**Purpose**: Capture voice transcripts from iPhone → iOS Shortcut → n8n webhook → Qdrant moonchecks collection

**Activation Required**:
1. Test webhook endpoint with curl
2. Activate workflow via n8n UI or MCP tool
3. Configure iOS Shortcut (guide: docs/blog/mooncheck_setup_guide.md)
4. Test end-to-end flow

**Next Steps** (Deferred from Session 24):
- [ ] Activate Mooncheck workflow
- [ ] Test webhook with sample payload
- [ ] Configure iOS Shortcut on Captain's device
- [ ] Capture first real transcript

---

## Hostinger API MCP Server

### Connection Info
**MCP Type**: stdio (CLI)
**Command**: `hostinger-api-mcp`
**Auth**: HOSTINGER_API_TOKEN environment variable

### Test Results

#### Domain Management
✅ `domains_getDomainListV1` - TESTED, working
**Result**: 1 free domain in "pending_setup" status
- ID: 27437517
- Type: free_domain
- Created: 2025-12-18
- Status: pending_setup
- No domain name assigned yet

### Available Capabilities (Untested)

#### Hosting Management
- `hosting_listOrdersV1` - List hosting orders
- `hosting_listWebsitesV1` - List websites
- `hosting_createWebsiteV1` - Create new website
- `hosting_listAvailableDatacentersV1` - List datacenter options
- `hosting_generateAFreeSubdomainV1` - Generate free subdomain
- `hosting_verifyDomainOwnershipV1` - Verify domain ownership
- `hosting_deployWordpressPlugin` - Deploy WordPress plugin
- `hosting_deployWordpressTheme` - Deploy WordPress theme
- `hosting_deployJsApplication` - Deploy JS app (Next.js, etc.)
- `hosting_deployStaticWebsite` - Deploy static site

#### VPS Management
- `VPS_getVirtualMachinesV1` - List VPS instances
- `VPS_getVirtualMachineDetailsV1` - Get VPS details
- `VPS_startVirtualMachineV1` - Start VPS
- `VPS_stopVirtualMachineV1` - Stop VPS
- `VPS_restartVirtualMachineV1` - Restart VPS
- Docker project management tools (30+ tools for docker-compose on VPS)

#### DNS Management
- `DNS_getDNSRecordsV1` - Get DNS records
- `DNS_updateDNSRecordsV1` - Update DNS
- `DNS_validateDNSRecordsV1` - Validate before update
- `DNS_resetDNSRecordsV1` - Reset to defaults

#### Domain Operations
- `domains_checkDomainAvailabilityV1` - Check domain availability
- `domains_purchaseNewDomainV1` - Buy domain
- `domains_getDomainDetailsV1` - Get domain info
- `domains_updateDomainNameserversV1` - Update nameservers

### Infrastructure Context

**Current Deployment**: n8n running on Hostinger VPS
- Server: srv1206808.hstgr.cloud
- Services: n8n + Fathom analytics
- Docker containers managed via Traefik reverse proxy
- Cloudflare tunnels for external access

**Potential Use Cases**:
1. Programmatic VPS management for n8n instance
2. Docker project deployment (e.g., deploy Qdrant to cloud)
3. DNS record updates for domains
4. Static site deployment for blog/docs

---

## Integration Architecture

```
Claude Code (Local)
    │
    ├─── n8n MCP ───────────┐
    │                       │
    └─── Hostinger API ─────┤
                            │
                            ▼
                   Hostinger Cloud VPS
                   (srv1206808.hstgr.cloud)
                            │
                            ├─── n8n (Docker)
                            │    ├─── 7 Active Trading Workflows
                            │    ├─── Mooncheck (Inactive)
                            │    └─── MCP Endpoint: /mcp-server/http
                            │
                            ├─── Fathom Analytics (Docker)
                            │
                            ├─── Traefik (Reverse Proxy)
                            │
                            └─── Qdrant (Docker) [Assumed, not verified]
```

---

## Recommendations

### Immediate Actions
1. **Activate Mooncheck Workflow**: Use n8n MCP or UI to activate workflow BcoxdWWb7wbAsQZR
2. **Test n8n Webhook**: Curl test to verify endpoint responds
3. **Verify Qdrant Deployment**: Check if Qdrant container running on Hostinger VPS

### Short-Term (This Session)
1. Test `export_workflow_to_file` to backup active workflows
2. Verify VPS status via `VPS_getVirtualMachinesV1`
3. Check DNS configuration for n8n subdomain

### Medium-Term (Future Sessions)
1. Resolve MCP client config issue for programmatic workflow deployment
2. Deploy Qdrant to cloud if not already present
3. Create n8n workflow for automatic checkpoint ingestion
4. Set up DNS records for custom domains

### Long-Term Integration
1. Automate workflow backup via MCP + cron
2. VPS monitoring via Hostinger API
3. Programmatic deployment pipeline (local dev → cloud deploy)
4. Unified infrastructure dashboard

---

## Test Plan (Post-Restart)

### n8n MCP
- [ ] List all workflows (with pagination)
- [ ] Get workflow details for Mooncheck
- [ ] Export Mooncheck workflow to local file
- [ ] Activate Mooncheck workflow
- [ ] Test webhook endpoint
- [ ] Retrieve execution history for Daily Health Monitor

### Hostinger API
- [ ] List VPS instances (verify n8n server)
- [ ] Get VPS details (resource usage, uptime)
- [ ] List DNS records for srv1206808.hstgr.cloud
- [ ] Verify Docker containers on VPS
- [ ] Check domain status

---

## Notes

- **n8n Access**: Both UI (https://n8n.srv1206808.hstgr.cloud) and MCP available
- **MCP vs UI**: Some operations easier via UI (visual workflow editing), others via MCP (bulk operations, automation)
- **Authentication**: All API keys stored in environment variables (secure)
- **Workflow Versioning**: n8n tracks version IDs, consider exporting critical workflows to git
- **Cloud Cost**: Hostinger basic tier, budget-conscious deployment

---

## Session 24 Context

From the Moonfire Manifest launch session:
- Designed complete mooncheck system architecture
- Created n8n workflow JSON for transcript capture
- Wrote iOS Shortcut setup guide
- Hit blocker: MCP client config for programmatic deployment
- Decision: Manual workflow import acceptable, defer automation
- Result: Mooncheck workflow deployed but inactive, awaiting testing
