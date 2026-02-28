#!/bin/bash
# Setup SSH connection to Hostinger VPS for Qdrant sync
# This script adds the host key and tests the connection

CLOUD_HOST="72.62.81.128"
CLOUD_USER="root"

echo "========================================"
echo "Rhiz Memory Sync - SSH Setup"
echo "========================================"

# Add host key if not already present
echo "Adding cloud server to known_hosts..."
ssh-keyscan -H $CLOUD_HOST >> ~/.ssh/known_hosts 2>/dev/null

# Test connection
echo "Testing SSH connection to $CLOUD_USER@$CLOUD_HOST..."
if ssh -o BatchMode=yes -o ConnectTimeout=10 $CLOUD_USER@$CLOUD_HOST "echo 'Connection successful'" 2>/dev/null; then
    echo "✓ SSH connection working!"
    echo ""
    echo "You can now run the sync script:"
    echo "  ./sync_now.sh"
else
    echo "✗ SSH connection failed"
    echo ""
    echo "Possible issues:"
    echo "1. SSH key not set up on cloud server"
    echo "2. Firewall blocking connection"
    echo "3. Incorrect credentials"
    echo ""
    echo "To set up SSH key:"
    echo "  ssh-copy-id $CLOUD_USER@$CLOUD_HOST"
    echo ""
    echo "Or test connection manually:"
    echo "  ssh $CLOUD_USER@$CLOUD_HOST"
fi

echo "========================================"
