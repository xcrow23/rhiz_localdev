# n8n MCP Setup - For Future Automation

## Current Status

**Issue**: n8n MCP tools return "Request error" when called
**Cause**: n8n API credentials/endpoint not configured in MCP

## What We Learned

### Attempt 1: Programmatic Workflow Creation
- Tried to use `mcp__n8n__Create_a_workflow` to deploy mooncheck workflow
- Got "Request error" - indicates missing configuration

### Attempt 2: Test API Connectivity
- Tried `mcp__n8n__Retrieve_all_workflows` to verify connection
- Also got "Request error"

**Conclusion**: n8n MCP server needs API credentials before it can interact with Hostinger n8n instance

## Required Configuration

The n8n MCP likely needs these environment variables or config:

```bash
N8N_API_URL=https://[your-hostinger-n8n-domain]
N8N_API_KEY=[your-n8n-api-key]
```

Or in MCP server config (typically `mcp_servers.json` or similar):

```json
{
  "n8n": {
    "url": "https://[your-n8n-domain]",
    "apiKey": "[your-api-key]"
  }
}
```

## How to Get n8n API Credentials

1. Log into Hostinger n8n instance
2. Go to **Settings** → **API**
3. Generate new API key
4. Copy key and base URL
5. Configure in MCP server settings

## Future Automation Plan

Once n8n MCP is configured, we can:

1. **Programmatically create workflows**
   - Define workflow in JSON/YAML
   - Use `Create_a_workflow` tool
   - Auto-deploy to cloud n8n

2. **Manage workflows via code**
   - List/update/delete workflows
   - Activate/deactivate programmatically
   - Version control workflow definitions

3. **Integrate with deployment pipeline**
   - CI/CD for n8n workflows
   - Test workflows in dev, deploy to prod
   - Rollback on failures

## Workaround for Now

**Manual Import** (2 minutes):
1. Log into Hostinger n8n UI
2. Import `docs/blog/mooncheck_workflow_n8n.json`
3. Configure environment variables
4. Activate workflow

**Benefits of manual approach**:
- Visual confirmation of workflow structure
- Easy debugging if issues arise
- Immediate feedback on node configuration

## Action Items

- [ ] Get n8n API key from Hostinger instance
- [ ] Configure n8n MCP with credentials
- [ ] Test API connectivity with `Retrieve_all_workflows`
- [ ] Retry programmatic workflow creation
- [ ] Document successful automation pattern

## Lessons Learned

1. **MCP tools require upfront configuration** - can't use them out of the box
2. **Manual deployment is viable fallback** - don't over-automate prematurely
3. **Test connectivity before complex operations** - should have tested list_workflows first
4. **Document blockers immediately** - this will help future debugging

---

**Status**: Blocked on n8n MCP configuration
**Workaround**: Manual workflow import
**Next**: Configure n8n API credentials, retry automation
**Last Updated**: 2026-01-04
