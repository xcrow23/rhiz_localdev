#!/bin/bash
# FC HTTP Gateway - Quick Deployment Script
# Run this on VPS: bash /root/rhiz/infrastructure/vps/DEPLOY_FC_QUICKSTART.sh

set -e

echo "=================================="
echo "FC HTTP Gateway - Quick Deployment"
echo "=================================="
echo ""

# Check we're on VPS
if [ ! -f "/root/rhiz/.env" ]; then
    echo "ERROR: /root/rhiz/.env not found. Are you on the VPS?"
    exit 1
fi

# Check for required API key
if ! grep -q "FC_HTTP_API_KEY" /root/rhiz/.env; then
    echo "WARNING: FC_HTTP_API_KEY not found in .env"
    echo "Gateway will accept unauthenticated requests (insecure!)"
    echo ""
    echo "Generate API key now? (y/n)"
    read -r response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        echo "Generating secure API key..."
        API_KEY=$(openssl rand -hex 32)
        echo "FC_HTTP_API_KEY=$API_KEY" >> /root/rhiz/.env
        echo ""
        echo "✓ API key generated and saved to .env (not displayed for security)"
        echo "  Retrieve with: grep FC_HTTP_API_KEY /root/rhiz/.env | cut -d'=' -f2"
        echo "  IMPORTANT: Update Cloudflare Workers with this key!"
        unset API_KEY  # Clear from shell memory
        echo ""
    else
        echo "Continuing without API key (INSECURE - only for testing)"
        echo ""
    fi
fi

cd /root/rhiz

echo "Step 1: Pull latest code"
git pull origin main || echo "Warning: git pull failed, continuing with existing code"

echo ""
echo "Step 2: Verify Docker network"
docker network inspect rhiz_network >/dev/null 2>&1 || {
    echo "Creating rhiz_network..."
    docker network create rhiz_network
}

echo ""
echo "Step 3: Check Qdrant is running"
if ! docker ps | grep -q qdrant; then
    echo "WARNING: Qdrant container not running"
    echo "FC HTTP Gateway requires Qdrant. Start it first:"
    echo "  docker-compose -f infrastructure/vps/docker-compose.trading.yml up -d qdrant"
    exit 1
fi

echo ""
echo "Step 4: Build FC HTTP Gateway"
docker-compose -f infrastructure/vps/docker-compose.trading.yml build fc-http-gateway

echo ""
echo "Step 5: Start FC HTTP Gateway"
docker-compose -f infrastructure/vps/docker-compose.trading.yml up -d fc-http-gateway

echo ""
echo "Step 6: Wait for service to be healthy (30 seconds)"
sleep 30

echo ""
echo "Step 7: Test health endpoint (unauthenticated)"
echo "Testing: http://localhost:8767/health"
curl -s http://localhost:8767/health | python3 -m json.tool || {
    echo ""
    echo "ERROR: Health endpoint not responding"
    echo "Check logs: docker logs fc-http-gateway"
    exit 1
}

echo ""
echo "Step 8: Verify authentication enforcement"

# Test unauthenticated request (should fail if API key configured)
if grep -q "FC_HTTP_API_KEY" /root/rhiz/.env; then
    echo "Testing unauthenticated request (should fail with 401)..."
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8767/heartbeat)

    if [ "$HTTP_CODE" -eq 401 ]; then
        echo "  ✓ Authentication correctly enforced (unauthenticated request rejected)"
    elif [ "$HTTP_CODE" -eq 200 ]; then
        echo "  ⚠ WARNING: Authentication NOT enforced (request succeeded without API key)"
        echo "  This indicates FC_HTTP_API_KEY may not be loaded properly"
        echo "  Check logs: docker logs fc-http-gateway"
    else
        echo "  Unexpected HTTP code: $HTTP_CODE"
    fi

    echo "Testing authenticated request (should succeed)..."
    FC_API_KEY=$(grep FC_HTTP_API_KEY /root/rhiz/.env | cut -d'=' -f2)
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" -H "Authorization: Bearer $FC_API_KEY" http://localhost:8767/heartbeat)
    unset FC_API_KEY  # Clear from memory

    if [ "$HTTP_CODE" -eq 200 ]; then
        echo "  ✓ Authenticated request succeeded"
    else
        echo "  ✗ Authenticated request failed with HTTP $HTTP_CODE"
        echo "  Check logs: docker logs fc-http-gateway"
        exit 1
    fi
else
    echo "⚠ WARNING: FC_HTTP_API_KEY not configured"
    echo "  Gateway running in INSECURE mode (no authentication)"
    echo "  This is acceptable for paper mode testing ONLY"
fi

echo ""
echo ""
echo "=================================="
echo "✓ FC HTTP Gateway Deployed!"
echo "=================================="
echo ""
echo "Service Status:"
docker ps --filter "name=fc-http-gateway" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
echo ""
echo "Test endpoints:"
echo "  Heartbeat: http://72.62.81.128:8767/heartbeat"
echo "  Ticker:    http://72.62.81.128:8767/market/ticker?pairs=XXBTZUSD"
echo ""
echo "Next Steps:"
echo "  1. Test from Cloudflare Worker (weekly-dca)"
echo "  2. Monitor logs: docker logs fc-http-gateway -f"
echo "  3. Check health: curl http://localhost:8767/heartbeat"
echo ""
echo "See full guide: infrastructure/vps/FC_GATEWAY_DEPLOYMENT.md"
echo ""
