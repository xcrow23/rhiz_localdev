#!/bin/bash
# Rollback Script - Trading Systems Migration
# Created: 2026-01-11
# Purpose: Restore Hostinger VPS trading services if Hetzner migration fails

set -e  # Exit on error

echo "=================================="
echo "ROLLBACK TO HOSTINGER VPS"
echo "=================================="
echo ""

# Configuration
HOSTINGER_IP="72.62.81.128"
FC_STATE_BACKUP="$HOME/rhiz_localdev/backups/fc_state_backup_$(date +%Y%m%d).json"
FC_CONTAINER_NAME="rhiz_fathom_commander"

# Check if backup exists
if [ ! -f "$FC_STATE_BACKUP" ]; then
    echo "ERROR: FC state backup not found at $FC_STATE_BACKUP"
    echo "Cannot proceed with rollback without state backup."
    exit 1
fi

echo "Found FC state backup: $FC_STATE_BACKUP"
echo ""

# Step 1: Restart Fathom Commander on Hostinger (if stopped)
echo "[1/4] Ensuring Fathom Commander is running on Hostinger..."
ssh root@$HOSTINGER_IP "docker start $FC_CONTAINER_NAME || docker restart $FC_CONTAINER_NAME"
sleep 5

# Step 2: Restore FC state from backup (directly into Docker container)
echo "[2/4] Restoring FC state from backup to Docker container..."
cat $FC_STATE_BACKUP | ssh root@$HOSTINGER_IP "docker exec -i $FC_CONTAINER_NAME tee /app/state/commander_state.json > /dev/null"
ssh root@$HOSTINGER_IP "docker restart $FC_CONTAINER_NAME"
sleep 5

# Step 3: Restart n8n (if it was stopped)
echo "[3/4] Restarting n8n workflows..."
ssh root@$HOSTINGER_IP "cd /opt/n8n && docker-compose up -d"
sleep 10

# Step 4: Verify services
echo "[4/4] Verifying Hostinger services..."
echo ""

# Check FC health
FC_HEALTH=$(curl -s -o /dev/null -w "%{http_code}" http://$HOSTINGER_IP:8766/health)
if [ "$FC_HEALTH" == "200" ]; then
    echo "✅ Fathom Commander: HEALTHY"
else
    echo "❌ Fathom Commander: UNHEALTHY (HTTP $FC_HEALTH)"
fi

# Check n8n health
N8N_HEALTH=$(curl -s -o /dev/null -w "%{http_code}" http://$HOSTINGER_IP:5678)
if [ "$N8N_HEALTH" == "200" ]; then
    echo "✅ n8n: HEALTHY"
else
    echo "❌ n8n: UNHEALTHY (HTTP $N8N_HEALTH)"
fi

echo ""
echo "=================================="
echo "ROLLBACK COMPLETE"
echo "=================================="
echo ""
echo "Trading services restored to Hostinger VPS ($HOSTINGER_IP)"
echo "Fathom Commander: http://$HOSTINGER_IP:8766"
echo "n8n: http://$HOSTINGER_IP:5678"
echo ""
echo "Next steps:"
echo "1. Verify weekly DCA workflow is operational"
echo "2. Test FC MCP tools from Claude Code"
echo "3. Monitor logs for 30 minutes: ssh root@$HOSTINGER_IP 'docker logs -f fathom-commander'"
echo ""
echo "Migration can be reattempted after resolving issues."
