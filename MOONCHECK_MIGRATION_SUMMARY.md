# Mooncheck Migration Complete - Next Steps

## What's Been Created

All code is ready for deployment. The n8n → Cloudflare Workers migration is complete.

### VPS FastAPI Gateway

**Location**: `infrastructure/vps/`

Files created:
- `fastapi_gateway.py` - Main API service (4 endpoints: health, embed, ingest, search)
- `Dockerfile.fastapi` - Docker image configuration
- `requirements-fastapi.txt` - Python dependencies
- `docker-compose.fastapi.yml` - Docker Compose service definition
- `DEPLOYMENT_GUIDE.md` - Complete VPS deployment instructions

### Cloudflare Worker

**Location**: `C:\Users\dread\documents\rhiz-workers\`

Files created:
- `src/mooncheck.ts` - Worker code (validates, forwards to VPS)
- `package.json` - Dependencies and scripts
- `tsconfig.json` - TypeScript configuration
- `wrangler.toml` - Cloudflare Workers configuration
- `.github/workflows/deploy.yml` - GitHub Actions CI/CD
- `README.md` - Project documentation
- `TESTING.md` - Comprehensive testing guide
- `.gitignore` - Git ignore rules

## Your Next Steps

### Step 1: Deploy VPS FastAPI Gateway

```bash
# SSH into your VPS
ssh root@YOUR_VPS_IP

# Navigate to infrastructure directory
cd /root/rhiz/infrastructure/vps

# If files aren't on VPS yet, git pull or scp them
git pull origin main  # if repo is synced
# OR
# scp files from local machine (see DEPLOYMENT_GUIDE.md)

# Verify network exists
docker network ls | grep rhiz_network
# If not, create it:
docker network create rhiz_network

# Build and start FastAPI
docker-compose -f docker-compose.fastapi.yml build
docker-compose -f docker-compose.fastapi.yml up -d

# Verify health
curl http://localhost:8000/health
```

**Expected**: All services report "healthy"

### Step 2: Configure Cloudflare Tunnel

Follow the detailed guide in `infrastructure/vps/DEPLOYMENT_GUIDE.md`, Phase 2.

Quick summary:
```bash
# On VPS
cloudflared tunnel create rhiz-api
cloudflared tunnel route dns rhiz-api api.dreamthewilderness.com

# Edit ~/.cloudflared/config.yml (see DEPLOYMENT_GUIDE.md for template)

# Test tunnel
cloudflared tunnel run rhiz-api

# If works, install as service
cloudflared service install
systemctl enable cloudflared
systemctl start cloudflared

# Verify from local machine
curl https://api.dreamthewilderness.com/health
```

### Step 3: Create GitHub Repository

```bash
# On local machine
cd C:\Users\dread\documents\rhiz-workers

# Initialize git
git init
git add .
git commit -m "Initial mooncheck Worker implementation"

# Create repo on GitHub (via web or gh CLI)
gh repo create rhiz-workers --public --source=. --remote=origin --push

# OR manually:
# 1. Go to github.com, create new repo "rhiz-workers"
# 2. git remote add origin git@github.com:YOUR_USERNAME/rhiz-workers.git
# 3. git push -u origin main
```

### Step 4: Configure Cloudflare API Token

1. Go to Cloudflare Dashboard → Profile → API Tokens
2. Create token with scopes:
   - Workers Scripts: Edit
   - Workers KV Storage: Edit
   - Account Settings: Read
   - Workers Tail: Read
3. Save token securely

### Step 5: Add GitHub Secret

1. Go to GitHub repo settings → Secrets and variables → Actions
2. Add new secret:
   - Name: `CLOUDFLARE_API_TOKEN`
   - Value: (token from Step 4)

### Step 6: Deploy Worker

Option A - GitHub Actions (Automatic):
```bash
# Just push to main branch
git push origin main

# GitHub Actions will automatically deploy
# Check: Actions tab in GitHub repo
```

Option B - Manual Deploy:
```bash
cd C:\Users\dread\documents\rhiz-workers

# Install dependencies
npm install

# Login to Cloudflare
npx wrangler login

# Deploy
npm run deploy

# Note the Worker URL from output
```

### Step 7: Test End-to-End

Follow the complete testing guide in `rhiz-workers/TESTING.md`.

Quick smoke test:
```bash
# Test Worker forwarding
curl -X POST https://mooncheck-receiver.YOUR_SUBDOMAIN.workers.dev \
  -H "Content-Type: application/json" \
  -d '{
    "transcript": "Complete migration test from edge to VPS to Qdrant",
    "topic_hint": "testing",
    "category": "blog"
  }'

# Should return:
# {
#   "success": true,
#   "mooncheck_id": 1736554800,
#   "timestamp": "2026-01-10T20:20:00.000Z",
#   "message": "Mooncheck captured and stored successfully"
# }
```

### Step 8: Update iPhone Shortcut

1. Open Shortcuts app
2. Edit "Mooncheck" shortcut
3. Update URL to: `https://mooncheck-receiver.YOUR_SUBDOMAIN.workers.dev`
4. Test with voice dictation

### Step 9: Verify & Celebrate

```bash
# Search for your test mooncheck
curl "https://api.dreamthewilderness.com/mooncheck/search?query=migration%20test&limit=1"

# Should return the mooncheck you just created
```

## What You'll Need to Provide

Before starting deployment:

1. **VPS IP/Hostname** - For SSH access
2. **Cloudflare Account ID** - From dashboard URL
3. **Domain Name** - For tunnel DNS routing (api.dreamthewilderness.com or other)
4. **GitHub Account** - For rhiz-workers repository
5. **Cloudflare API Token** - Created in Step 4

## Architecture Benefits

What we achieved:

✅ **Access Parity**: Both you and I can read/modify TypeScript and Python code
✅ **No UI Lock-in**: All configuration in git-versioned files
✅ **Global Performance**: Cloudflare edge network = fast from anywhere
✅ **Zero Cost**: Free tier for Workers + Tunnel
✅ **Observable**: Comprehensive logging at every layer
✅ **Maintainable**: Clean separation of concerns
✅ **Scalable**: Edge handles bursts, VPS handles storage

## Files Reference

### VPS Files (upload/sync to VPS)
```
infrastructure/vps/
├── fastapi_gateway.py
├── Dockerfile.fastapi
├── requirements-fastapi.txt
├── docker-compose.fastapi.yml
└── DEPLOYMENT_GUIDE.md
```

### Local Files (push to GitHub)
```
rhiz-workers/
├── src/mooncheck.ts
├── package.json
├── tsconfig.json
├── wrangler.toml
├── .github/workflows/deploy.yml
├── README.md
├── TESTING.md
└── .gitignore
```

## Rollback Plan

If anything goes wrong:

1. **n8n still works**: Original webhooks still active
2. **iPhone shortcut**: Can switch URL back to n8n instantly
3. **VPS services**: Independent, can stop FastAPI without affecting others
4. **Worker**: Can delete from Cloudflare dashboard with zero VPS impact

## Estimated Time

- VPS Deployment: 15-20 minutes
- Tunnel Setup: 10-15 minutes
- GitHub + Worker: 10 minutes
- Testing: 15-20 minutes
- **Total: ~1 hour** (assuming no blockers)

## Support

If you hit issues:

1. Check relevant logs (see DEPLOYMENT_GUIDE.md)
2. Consult TESTING.md for specific test procedures
3. We can debug together in next session

## What's Different

**Before (n8n)**:
- UI-first workflow builder
- Captain-via-UI, First-Mate-via-broken-API
- Code nodes unreliable
- Webhook registration bugs
- Manual workflow export/import

**After (Cloudflare + FastAPI)**:
- Code-first TypeScript + Python
- Both of us read/write same code
- Git-versioned everything
- Zero n8n complexity
- Programmatic deployment

## Ready to Deploy?

Start with Step 1 (VPS deployment) whenever you're ready. The DEPLOYMENT_GUIDE.md has detailed commands for every step.

Let me know when you begin and I can help troubleshoot any issues that come up.
