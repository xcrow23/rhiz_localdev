#!/bin/bash
#
# Strategic Intelligence Layer - Cloud Deployment Script
# Deploys SIL API to Hostinger VPS (72.62.81.128)
#
# Usage: bash deploy.sh [target_env]
#   target_env: local (default) or cloud
#
# Prerequisites:
# - SSH access to VPS configured
# - Docker and docker-compose installed on VPS
# - Hostinger VPS running at 72.62.81.128

set -e  # Exit on error

# Configuration
VPS_HOST="${VPS_HOST:-72.62.81.128}"
VPS_USER="${VPS_USER:-root}"
VPS_PATH="${VPS_PATH:-/root/rhiz_localdev/domains/trading/strategic_intelligence}"
TARGET_ENV="${1:-local}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Deployment functions
deploy_local() {
    log_info "Deploying SIL API locally..."

    # Stop existing containers
    log_info "Stopping existing containers..."
    docker compose -f docker-compose.cloud.yaml down 2>/dev/null || true

    # Build and start
    log_info "Building SIL container..."
    docker compose -f docker-compose.cloud.yaml build

    log_info "Starting SIL API..."
    docker compose -f docker-compose.cloud.yaml up -d

    # Wait for startup
    log_info "Waiting for container startup (10s)..."
    sleep 10

    # Health check
    log_info "Checking health endpoint..."
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        log_success "SIL API is healthy!"
        curl http://localhost:8000/health | jq .
    else
        log_error "Health check failed!"
        docker compose -f docker-compose.cloud.yaml logs sil-api
        exit 1
    fi

    log_success "Local deployment complete!"
    log_info "Access SIL API at: http://localhost:8000"
    log_info "View logs: docker compose -f docker-compose.cloud.yaml logs -f sil-api"
}

deploy_cloud() {
    log_info "Deploying SIL API to Hostinger VPS ($VPS_HOST)..."

    # Check SSH access
    log_info "Testing SSH access to $VPS_USER@$VPS_HOST..."
    if ! ssh -o ConnectTimeout=5 "$VPS_USER@$VPS_HOST" "echo 'SSH connection successful'" > /dev/null 2>&1; then
        log_error "Cannot connect to VPS. Check SSH configuration."
        exit 1
    fi
    log_success "SSH connection verified"

    # Create remote directory
    log_info "Creating remote directory structure..."
    ssh "$VPS_USER@$VPS_HOST" "mkdir -p $VPS_PATH"

    # Upload files
    log_info "Uploading SIL files to VPS..."

    # Create temporary deployment package (exclude data, tests, __pycache__)
    log_info "Creating deployment package..."
    tar -czf /tmp/sil_deploy.tar.gz \
        --exclude='data/historical/*.csv' \
        --exclude='data/qdrant/*' \
        --exclude='tests/' \
        --exclude='__pycache__' \
        --exclude='*.pyc' \
        --exclude='.pytest_cache' \
        --exclude='logs/' \
        .

    log_info "Uploading package (this may take a minute)..."
    scp /tmp/sil_deploy.tar.gz "$VPS_USER@$VPS_HOST:/tmp/"

    # Extract on VPS
    log_info "Extracting files on VPS..."
    ssh "$VPS_USER@$VPS_HOST" "cd $VPS_PATH && tar -xzf /tmp/sil_deploy.tar.gz && rm /tmp/sil_deploy.tar.gz"

    # Clean up local temp file
    rm /tmp/sil_deploy.tar.gz

    log_success "Files uploaded successfully"

    # Deploy on VPS
    log_info "Building and starting SIL container on VPS..."
    ssh "$VPS_USER@$VPS_HOST" << 'ENDSSH'
        cd /root/rhiz_localdev/domains/trading/strategic_intelligence

        # Stop existing containers
        echo "[VPS] Stopping existing containers..."
        docker compose -f docker-compose.cloud.yaml down 2>/dev/null || true

        # Build container
        echo "[VPS] Building SIL container..."
        docker compose -f docker-compose.cloud.yaml build

        # Start container
        echo "[VPS] Starting SIL API..."
        docker compose -f docker-compose.cloud.yaml up -d

        # Wait for startup
        echo "[VPS] Waiting for container startup (15s)..."
        sleep 15

        # Check health
        echo "[VPS] Checking health endpoint..."
        curl -f http://localhost:8001/health || {
            echo "[VPS] Health check failed! Showing logs:"
            docker compose -f docker-compose.cloud.yaml logs sil-api
            exit 1
        }
ENDSSH

    log_success "VPS deployment complete!"

    # Final health check from local machine
    log_info "Testing VPS endpoint from local machine..."
    if curl -f "http://$VPS_HOST:8001/health" > /dev/null 2>&1; then
        log_success "SIL API is accessible remotely!"
        curl "http://$VPS_HOST:8001/health" | jq .
    else
        log_warn "Remote health check failed (may be expected if port 8001 not exposed)"
        log_info "SIL API is accessible within Docker network at: http://sil-api:8000"
    fi

    log_success "Cloud deployment complete!"
    log_info "SSH to VPS: ssh $VPS_USER@$VPS_HOST"
    log_info "View logs: ssh $VPS_USER@$VPS_HOST 'cd $VPS_PATH && docker compose -f docker-compose.cloud.yaml logs -f sil-api'"
    log_info "Health check: curl http://$VPS_HOST:8001/health"
}

# Main deployment logic
main() {
    log_info "========================================"
    log_info "SIL Cloud Deployment Script"
    log_info "========================================"
    log_info "Target: $TARGET_ENV"
    log_info ""

    case "$TARGET_ENV" in
        local)
            deploy_local
            ;;
        cloud)
            deploy_cloud
            ;;
        *)
            log_error "Invalid target: $TARGET_ENV"
            log_info "Usage: bash deploy.sh [local|cloud]"
            exit 1
            ;;
    esac

    log_info ""
    log_success "========================================"
    log_success "Deployment Complete!"
    log_success "========================================"
}

# Run deployment
main
