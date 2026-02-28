# Mooncheck VPS Deployment Guide

## Overview

This guide walks through deploying the FastAPI Gateway on your VPS and configuring Cloudflare Tunnel to expose it securely.

## Architecture

```
iPhone → Cloudflare Worker (edge) → Cloudflare Tunnel → FastAPI (VPS:8000) → Embedding (VPS:5000) → Qdrant (VPS:6333)
```

## Prerequisites

- VPS with Docker and Docker Compose installed
- Cloudflare account with domain configured
- SSH access to VPS
- Existing services running: embedding service (port 5000), Qdrant (port 6333)

## Phase 1: Deploy FastAPI Gateway on VPS

### Step 1: Upload Files to VPS

Transfer the following files to your VPS at `/root/rhiz/infrastructure/vps/`:

```bash
# From local machine
scp infrastructure/vps/fastapi_gateway.py root@YOUR_VPS:/root/rhiz/infrastructure/vps/
scp infrastructure/vps/Dockerfile.fastapi root@YOUR_VPS:/root/rhiz/infrastructure/vps/
scp infrastructure/vps/requirements-fastapi.txt root@YOUR_VPS:/root/rhiz/infrastructure/vps/
scp infrastructure/vps/docker-compose.fastapi.yml root@YOUR_VPS:/root/rhiz/infrastructure/vps/
```

Or use git if the repo is synced to VPS:
```bash
ssh root@YOUR_VPS
cd /root/rhiz
git pull origin main
```

### Step 2: Verify Network and Dependencies

Ensure the `rhiz_network` Docker network exists and embedding/Qdrant services are running:

```bash
# Check network
docker network ls | grep rhiz_network

# If network doesn't exist, create it
docker network create rhiz_network

# Check running services
docker ps | grep -E "embedding|qdrant"

# Expected output should show containers for:
# - rhiz_embedding (or similar) on port 5000
# - rhiz_qdrant on ports 6333/6334
```

### Step 3: Build and Deploy FastAPI Gateway

```bash
cd /root/rhiz/infrastructure/vps

# Build the Docker image
docker-compose -f docker-compose.fastapi.yml build

# Start the service
docker-compose -f docker-compose.fastapi.yml up -d

# Check logs
docker logs rhiz_fastapi_gateway -f
```

### Step 4: Verify FastAPI is Running

```bash
# Health check
curl http://localhost:8000/health

# Expected response:
# {
#   "status": "healthy",
#   "services": {
#     "embedding_service": "healthy",
#     "qdrant": "healthy",
#     "fastapi": "healthy"
#   },
#   "timestamp": "2026-01-10T..."
# }

# Test embedding endpoint
curl -X POST http://localhost:8000/embed \
  -H "Content-Type: application/json" \
  -d '{"text": "test embedding"}'

# Test mooncheck ingest
curl -X POST http://localhost:8000/mooncheck/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "transcript": "VPS deployment test mooncheck",
    "topic_hint": "infrastructure",
    "category": "blog"
  }'
```

## Phase 2: Configure Cloudflare Tunnel

### Step 1: Verify Cloudflared Installation

```bash
# Check if cloudflared is installed
cloudflared --version

# If not installed, install it:
# For Debian/Ubuntu:
wget -q https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
dpkg -i cloudflared-linux-amd64.deb

# For other Linux:
wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64
mv cloudflared-linux-amd64 /usr/local/bin/cloudflared
chmod +x /usr/local/bin/cloudflared
```

### Step 2: Authenticate with Cloudflare

```bash
# This will open a browser window for authentication
cloudflared tunnel login

# This creates a cert.pem file at ~/.cloudflared/cert.pem
ls -la ~/.cloudflared/
```

### Step 3: Create Tunnel

```bash
# Create a new tunnel named "rhiz-api"
cloudflared tunnel create rhiz-api

# Note the Tunnel ID from the output (something like: 12345678-1234-1234-1234-123456789abc)
# This creates a credentials file at: ~/.cloudflared/TUNNEL_ID.json
```

### Step 4: Configure DNS Routing

```bash
# Route your subdomain to the tunnel
# Replace TUNNEL_ID with the ID from step 3
cloudflared tunnel route dns rhiz-api api.dreamthewilderness.com

# Verify the route was created
cloudflared tunnel route dns list
```

### Step 5: Create Tunnel Configuration

Create the tunnel config file:

```bash
# Replace TUNNEL_ID with your actual tunnel ID
nano ~/.cloudflared/config.yml
```

Add this configuration:

```yaml
tunnel: YOUR_TUNNEL_ID_HERE
credentials-file: /root/.cloudflared/YOUR_TUNNEL_ID_HERE.json

ingress:
  # Route api.dreamthewilderness.com to FastAPI
  - hostname: api.dreamthewilderness.com
    service: http://localhost:8000
  # Catch-all rule (required)
  - service: http_status:404
```

### Step 6: Test the Tunnel

```bash
# Run tunnel in foreground to test
cloudflared tunnel run rhiz-api

# In another terminal, test from outside VPS:
curl https://api.dreamthewilderness.com/health
```

If the health check returns successfully, the tunnel is working!

### Step 7: Install as Systemd Service

```bash
# Install cloudflared as a system service
cloudflared service install

# Enable to start on boot
systemctl enable cloudflared

# Start the service
systemctl start cloudflared

# Check status
systemctl status cloudflared

# View logs
journalctl -u cloudflared -f
```

### Step 8: Verify Tunnel is Accessible

From your local machine or phone:

```bash
# Health check via tunnel
curl https://api.dreamthewilderness.com/health

# Test mooncheck ingest via tunnel
curl -X POST https://api.dreamthewilderness.com/mooncheck/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "transcript": "Tunnel test mooncheck from external network",
    "topic_hint": "testing",
    "category": "blog"
  }'

# Expected response:
# {
#   "success": true,
#   "mooncheck_id": 1736553600,
#   "timestamp": "2026-01-10T20:00:00.000Z",
#   "message": "Mooncheck captured and stored successfully"
# }
```

## Troubleshooting

### FastAPI Gateway Issues

**Container won't start:**
```bash
# Check logs
docker logs rhiz_fastapi_gateway

# Common issues:
# - Embedding service not reachable → verify container name and network
# - Qdrant not reachable → verify container name and network
# - Port 8000 already in use → check with: netstat -tlnp | grep 8000
```

**Health check fails:**
```bash
# Check if embedding service is healthy
curl http://localhost:5000/health

# Check if Qdrant is healthy
curl http://localhost:6333/collections

# Check Docker network
docker network inspect rhiz_network
```

### Cloudflare Tunnel Issues

**Tunnel won't start:**
```bash
# Check config syntax
cloudflared tunnel info rhiz-api

# Verify credentials file exists
ls -la ~/.cloudflared/*.json

# Check if port 8000 is actually listening
netstat -tlnp | grep 8000
```

**DNS not resolving:**
```bash
# Verify route is created
cloudflared tunnel route dns list

# Check Cloudflare dashboard → DNS records
# Should see a CNAME record: api.dreamthewilderness.com → TUNNEL_ID.cfargotunnel.com
```

**403 Forbidden errors:**
- Check Cloudflare dashboard → SSL/TLS settings → should be "Full" or "Flexible"
- Verify tunnel credentials match the tunnel ID

### Qdrant Issues

**Collection doesn't exist:**
```bash
# FastAPI will auto-create the collection, but you can manually create it:
curl -X PUT http://localhost:6333/collections/moonchecks \
  -H "Content-Type: application/json" \
  -d '{
    "vectors": {
      "size": 384,
      "distance": "Cosine"
    }
  }'
```

## Maintenance

### View Service Logs

```bash
# FastAPI logs
docker logs rhiz_fastapi_gateway -f

# Cloudflare tunnel logs
journalctl -u cloudflared -f

# Embedding service logs
docker logs rhiz_embedding -f

# Qdrant logs
docker logs rhiz_qdrant -f
```

### Restart Services

```bash
# Restart FastAPI
docker restart rhiz_fastapi_gateway

# Restart tunnel
systemctl restart cloudflared

# Restart all VPS services
cd /root/rhiz/infrastructure/vps
docker-compose -f docker-compose.fastapi.yml restart
```

### Update FastAPI Code

```bash
# Pull latest code
cd /root/rhiz
git pull origin main

# Rebuild and restart
cd infrastructure/vps
docker-compose -f docker-compose.fastapi.yml build
docker-compose -f docker-compose.fastapi.yml up -d
```

## Security Notes

- FastAPI gateway only listens on localhost (0.0.0.0:8000 inside container, but only accessible via tunnel)
- Cloudflare Tunnel provides encrypted connection without exposing VPS ports
- No firewall rules needed - tunnel is outbound connection only
- All communication is HTTPS via Cloudflare's edge network

## Next Steps

Once VPS deployment is complete:
1. Create GitHub repository for Cloudflare Worker (`rhiz-workers`)
2. Deploy Worker code that forwards requests to `https://api.dreamthewilderness.com`
3. Update iPhone shortcut to use Worker URL
4. Test end-to-end flow

## Quick Reference Commands

```bash
# Service status
docker ps | grep rhiz
systemctl status cloudflared

# Health checks
curl http://localhost:8000/health
curl https://api.dreamthewilderness.com/health

# Logs
docker logs rhiz_fastapi_gateway -f
journalctl -u cloudflared -f

# Restart
docker restart rhiz_fastapi_gateway
systemctl restart cloudflared
```
