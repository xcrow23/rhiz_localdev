#!/bin/bash
# Unified Trading Platform - Hostinger Deployment
# Date: 2026-01-12
# Session: 42 - Phase 1 Deployment

set -e  # Exit on error

HOSTINGER_IP="72.62.81.128"
DEPLOY_DIR="/opt/rhiz_trading"

echo "========================================="
echo "UNIFIED TRADING PLATFORM DEPLOYMENT"
echo "Target: Hostinger VPS ($HOSTINGER_IP)"
echo "========================================="
echo ""

# Step 1: Create deployment directory on Hostinger
echo "[1/8] Creating deployment directory on Hostinger..."
ssh root@$HOSTINGER_IP "mkdir -p $DEPLOY_DIR/{domains/trading,infrastructure/vps,config}"

# Step 2: Copy Docker Compose stack
echo "[2/8] Copying Docker Compose stack..."
scp docker-compose.trading.yml root@$HOSTINGER_IP:$DEPLOY_DIR/docker-compose.yml

# Step 3: Copy .env file
echo "[3/8] Copying environment configuration..."
scp .env.production root@$HOSTINGER_IP:$DEPLOY_DIR/.env

# Step 4: Copy gateway application
echo "[4/8] Copying gateway application..."
scp gateway_trading.py root@$HOSTINGER_IP:$DEPLOY_DIR/infrastructure/vps/
scp requirements-gateway.txt root@$HOSTINGER_IP:$DEPLOY_DIR/infrastructure/vps/
scp Dockerfile.gateway root@$HOSTINGER_IP:$DEPLOY_DIR/infrastructure/vps/

# Step 5: Copy Fathom source
echo "[5/8] Copying Fathom source code..."
scp -r ../../domains/trading/fathom root@$HOSTINGER_IP:$DEPLOY_DIR/domains/trading/

# Step 6: Copy Fathom Commander source
echo "[6/8] Copying Fathom Commander source code..."
scp -r ../../domains/trading/fathom_commander root@$HOSTINGER_IP:$DEPLOY_DIR/domains/trading/

# Step 7: Copy SIL source
echo "[7/8] Copying Strategic Intelligence Layer source code..."
scp -r ../../domains/trading/strategic_intelligence root@$HOSTINGER_IP:$DEPLOY_DIR/domains/trading/

# Step 8: Gracefully stop old containers (keep as backup)
echo "[8/8] Stopping old individual containers (keeping for rollback)..."
ssh root@$HOSTINGER_IP << 'ENDSSH'
# Stop old containers but don't remove them (rollback capability)
docker stop rhiz_fathom_commander || true
docker stop rhiz-sil-api || true
docker stop rhiz_fastapi_gateway || true

echo ""
echo "Old containers stopped (not deleted). Rollback available if needed."
echo ""
ENDSSH

echo ""
echo "========================================="
echo "FILES COPIED - READY FOR DEPLOYMENT"
echo "========================================="
echo ""
echo "Next steps (run on Hostinger VPS):"
echo "1. ssh root@$HOSTINGER_IP"
echo "2. cd $DEPLOY_DIR"
echo "3. docker-compose up -d --build"
echo "4. docker-compose logs -f"
echo ""
echo "Deployment directory: $DEPLOY_DIR"
