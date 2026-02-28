# Cloudflare API Setup Guide for Rhiz Checkpoint Deployment

## C6 Resolution: Required Cloudflare API Access

**Status**: Critical blocker for checkpoint-api Workers deployment
**Current Issue**: 3 API tokens tested, all failed with authentication errors

---

## Two Approaches: Interactive vs. API Token

### Approach 1: Interactive Login (RECOMMENDED - Easiest)

This approach uses OAuth and handles all permissions automatically.

```powershell
# Install wrangler if not already installed
npm install -g wrangler

# Authenticate interactively (opens browser)
wrangler login

# Verify authentication
wrangler whoami

# Test D1 database creation
wrangler d1 create rhiz-checkpoints

# Deploy worker
cd infrastructure/cloudflare/checkpoint-api
wrangler deploy
```

**Pros**:
- No manual token management
- Automatic permission handling
- Browser-based OAuth (familiar flow)

**Cons**:
- Requires browser access during setup
- Session-based (may need re-login periodically)

---

### Approach 2: API Token (More Control)

If you prefer token-based authentication for automation or CI/CD:

#### Step 1: Create API Token in Cloudflare Dashboard

1. Log in to [Cloudflare Dashboard](https://dash.cloudflare.com)
2. Go to **Profile** → **API Tokens** → **Create Token**
3. Choose **"Edit Cloudflare Workers"** template OR **"Create Custom Token"**

#### Step 2: Configure Token Permissions

**Account-Level Permissions** (REQUIRED):
- ✅ **Workers Scripts** → **Edit**
- ✅ **Workers KV Storage** → **Edit** (if using KV, optional for us)
- ✅ **D1** → **Edit**
- ✅ **Account Settings** → **Read** (to retrieve Account ID)

**Zone-Level Permissions** (OPTIONAL - only if deploying to specific domains):
- DNS → Edit (if configuring custom domains for checkpoint-api.workers.dev)

#### Step 3: Token Constraints (Recommended)

- **IP Address Filtering**: Add your VPS and local IPs for security
- **TTL**: Set reasonable expiration (e.g., 1 year) or "Never expires" for long-term deployment
- **Included Accounts**: Select your Rhiz Cloudflare account

#### Step 4: Use Token

After creating the token, you'll see it once. Copy it immediately.

**Option A: Environment Variable**
```powershell
# Windows PowerShell
$env:CLOUDFLARE_API_TOKEN="your-token-here"
wrangler d1 create rhiz-checkpoints

# Linux/WSL
export CLOUDFLARE_API_TOKEN="your-token-here"
wrangler d1 create rhiz-checkpoints
```

**Option B: wrangler.toml Configuration** (NOT RECOMMENDED - security risk)
```toml
# Only for local testing - DO NOT commit to git
account_id = "your-account-id"
# Don't put token in wrangler.toml - use env var instead
```

**Option C: Pass to wrangler via flag**
```powershell
wrangler d1 create rhiz-checkpoints --api-token="your-token-here"
```

---

## Troubleshooting Previous Token Failures

Based on `TOKEN_VERIFICATION_NEEDED.md`, previous attempts failed because:

### Possible Issues
1. **Tokens Truncated**: Dashboard may have shown partial tokens - ensure you copy the FULL token
2. **Wrong Permission Scope**: Tokens may have been zone-specific instead of account-level
3. **Token Type Confusion**: Global API Key ≠ API Token (we need API Token, not Global Key)
4. **Workers Not Enabled**: Check if Workers is enabled on your Cloudflare account plan

### Verification Steps

**Test Token Validity**:
```bash
curl -X GET "https://api.cloudflare.com/client/v4/user/tokens/verify" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

Expected response:
```json
{
  "success": true,
  "errors": [],
  "messages": [],
  "result": {
    "id": "...",
    "status": "active"
  }
}
```

**Test Account Access**:
```bash
curl -X GET "https://api.cloudflare.com/client/v4/accounts" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

Should return list of accounts with your Account ID.

---

## Required Account Information

Once authenticated, you'll need your **Account ID** for wrangler.toml:

```bash
# Get Account ID
wrangler whoami
# OR
curl -X GET "https://api.cloudflare.com/client/v4/accounts" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

Update `infrastructure/cloudflare/checkpoint-api/wrangler.toml`:
```toml
name = "rhiz-checkpoint-api"
main = "worker.js"
compatibility_date = "2024-12-01"
account_id = "YOUR_ACCOUNT_ID_HERE"  # ← Update this

[[d1_databases]]
binding = "DB"
database_name = "rhiz-checkpoints"
database_id = ""  # Will be populated after `wrangler d1 create`
```

---

## Deployment Workflow (After Authentication)

```powershell
cd infrastructure/cloudflare/checkpoint-api

# 1. Create D1 database
wrangler d1 create rhiz-checkpoints
# Copy the database_id from output to wrangler.toml

# 2. Apply schema
wrangler d1 execute rhiz-checkpoints --file=schema.sql

# 3. Test locally (optional)
wrangler dev

# 4. Deploy to production
wrangler deploy

# 5. Test endpoints
curl https://rhiz-checkpoint-api.YOUR_SUBDOMAIN.workers.dev/api/health
```

---

## Security Best Practices

1. **Never Commit Tokens**: Add to `.gitignore`:
   ```
   # .gitignore
   .env
   .dev.vars
   wrangler.toml.local
   **/cloudflare-api-token.txt
   ```

2. **Use Environment Variables**: Store token in system env vars, not files

3. **Rotate Tokens Periodically**: Set expiration dates, rotate every 6-12 months

4. **Principle of Least Privilege**: Only grant permissions actually needed

5. **Monitor Token Usage**: Check Cloudflare audit logs for unexpected API calls

---

## Alternative: Service Tokens (Advanced)

For CI/CD or automated deployments, consider **API Service Tokens**:
- More granular permission control
- Can be scoped to specific namespaces
- Better for automation pipelines

---

## Summary: What Captain Needs to Do

### Quick Path (Recommended)
1. Run `wrangler login` (opens browser, click "Allow")
2. Run `wrangler whoami` to get Account ID
3. Update `wrangler.toml` with Account ID
4. Run `wrangler d1 create rhiz-checkpoints`
5. Update `wrangler.toml` with database_id from output
6. Run `wrangler d1 execute rhiz-checkpoints --file=schema.sql`
7. Run `wrangler deploy`
8. Test: `curl https://rhiz-checkpoint-api.*.workers.dev/api/health`

**Time Estimate**: 10-15 minutes

### Token Path (If Preferred)
1. Cloudflare Dashboard → API Tokens → Create Token
2. Template: "Edit Cloudflare Workers"
3. Permissions: Workers Scripts Edit, D1 Edit, Account Settings Read
4. Create token, copy it immediately
5. Set env var: `$env:CLOUDFLARE_API_TOKEN="token"`
6. Follow deployment workflow above

**Time Estimate**: 15-20 minutes

---

## Post-Deployment

After successful deployment, C6 will be resolved and we can:
- Integrate checkpoint-api with session hooks
- Test cloud checkpoint persistence
- Set up webhook for automatic checkpoint sync
- Enable cross-instance session continuity

---

**Created**: 2026-01-10 (Session 40)
**For**: Captain (C6 resolution)
**Next Action**: Choose approach (interactive login recommended), deploy checkpoint-api
