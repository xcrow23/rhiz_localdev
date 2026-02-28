# Rhiz Memory Cloud Sync

Automated synchronization of Qdrant vector database between local development machine and Hostinger cloud.

## Overview

Ensures session memories are always backed up to cloud, enabling:
- **Persistence**: Memories survive local machine failures
- **Continuity**: Access from any Claude instance with cloud connection
- **Redundancy**: Dual storage (local + cloud)
- **Automation**: Periodic sync without manual intervention

## Architecture

```
Local Qdrant (localhost:6333)
    ↓ SSH Tunnel (localhost:6335)
    ↓ sync_cloud.py
    ↓
Cloud Qdrant (72.62.81.128:6333)
```

**Sync Direction**: Local → Cloud (default)
**Frequency**: Every 6 hours (automated) or on-demand
**Method**: SSH tunnel + Qdrant REST API

## Quick Start

### 1. Setup SSH Access

```bash
cd tools/memory-sync
./setup_ssh.sh
```

This adds the cloud server to known_hosts. If you don't have SSH key authentication set up:

```bash
ssh-copy-id root@72.62.81.128
# Enter password when prompted
```

### 2. Install Python Dependencies

**WSL (for automated sync)**:
```bash
sudo apt update
sudo apt install python3-pip
pip3 install qdrant-client
```

**Windows (if running manually)**:
```cmd
pip install qdrant-client
```

### 3. Run Manual Sync

```bash
./sync_now.sh
```

Expected output:
```
========================================
Rhiz Memory Cloud Sync
========================================
Local -> Cloud synchronization

✓ All checks passed

Starting sync (with automatic SSH tunnel)...

Local: 161 points
Cloud: 27 points

Retrieved 161 points
Syncing to Cloud...
  Synced 50/161
  Synced 100/161
  Synced 161/161

Cloud after sync: 161 points

✓ Sync completed successfully!
========================================
```

### 4. Enable Automated Sync (Optional)

For systemd-based automation (every 6 hours):

```bash
# Copy service files to systemd
sudo cp rhiz-memory-sync.service /etc/systemd/system/
sudo cp rhiz-memory-sync.timer /etc/systemd/system/

# Reload systemd
sudo systemctl daemon-reload

# Enable and start timer
sudo systemctl enable rhiz-memory-sync.timer
sudo systemctl start rhiz-memory-sync.timer

# Check status
systemctl status rhiz-memory-sync.timer
systemctl list-timers | grep rhiz
```

## Files

- `setup_ssh.sh` - One-time SSH setup
- `sync_now.sh` - Manual sync (interactive)
- `sync_auto.sh` - Automated sync (logs to file)
- `rhiz-memory-sync.service` - Systemd service definition
- `rhiz-memory-sync.timer` - Systemd timer (schedule)
- `sync.log` - Manual sync log
- `sync_auto.log` - Automated sync log

## Configuration

All configuration is in `core/memory/scripts/sync_cloud.py`:
- **Cloud Host**: `72.62.81.128`
- **Cloud Port**: `6333` (tunneled to `localhost:6335`)
- **Collection**: `rhiz_memories`
- **Batch Size**: 50 points per batch

## Troubleshooting

### "SSH connection failed"

**Check**:
1. SSH key authentication set up? `ssh root@72.62.81.128`
2. Server reachable? `ping 72.62.81.128`
3. Firewall blocking? Check Hostinger control panel

**Fix**:
```bash
ssh-keygen -t ed25519  # Generate key if needed
ssh-copy-id root@72.62.81.128  # Add to server
```

### "Local Qdrant not accessible"

**Check**:
```bash
docker ps | grep qdrant
curl http://localhost:6333/collections/rhiz_memories
```

**Fix**:
```bash
cd /mnt/c/Users/dread/documents/rhiz_localdev
docker-compose up -d qdrant
```

### "qdrant-client not installed"

**Fix**:
```bash
pip3 install qdrant-client
```

### Sync fails partway through

**Symptoms**: Partial sync, connection timeouts

**Fix**:
- Check internet connection stability
- Verify SSH tunnel isn't timing out
- Run manual sync to retry: `./sync_now.sh`

### Cloud has more points than local

**Symptoms**: "Cloud: 200 points, Local: 161 points"

**Explanation**: Cloud may have been updated from a different source (n8n, API, etc.)

**Fix** (reverse sync):
```bash
cd /mnt/c/Users/dread/documents/rhiz_localdev/core/memory/scripts
python3 sync_cloud.py --reverse --tunnel
```

## Monitoring

### Check sync status

```bash
# View recent sync logs
tail -50 tools/memory-sync/sync_auto.log

# Check systemd timer
systemctl status rhiz-memory-sync.timer

# View last sync time
systemctl list-timers | grep rhiz
```

### Verify sync success

```bash
# Local count
curl -s http://localhost:6333/collections/rhiz_memories | grep points_count

# Cloud count (requires tunnel)
ssh -L 6335:localhost:6333 -f -N root@72.62.81.128
curl -s http://localhost:6335/collections/rhiz_memories | grep points_count
```

Counts should match after successful sync.

## Sync Strategy

### Current (2025-12-28)
- **Direction**: Local → Cloud (one-way)
- **Frequency**: Every 6 hours
- **Method**: Full sync (overwrite cloud with local)

### Future Enhancements
- [ ] Bidirectional sync with conflict resolution
- [ ] Incremental sync (only new points)
- [ ] Sync status dashboard
- [ ] Webhook notification on sync failure
- [ ] Multi-cloud redundancy (Cloudflare R2, AWS S3)

## Manual Operations

### Force sync now
```bash
./sync_now.sh
```

### Reverse sync (Cloud → Local)
```bash
cd ../../core/memory/scripts
python3 sync_cloud.py --reverse --tunnel
```

### Check sync without running
```bash
python3 ../../core/memory/scripts/sync_cloud.py --help
```

### Establish tunnel only (for manual operations)
```bash
ssh -L 6335:localhost:6333 -f -N root@72.62.81.128
# Now cloud Qdrant accessible at localhost:6335
```

## Integration with Checkpoint System

The sync system integrates with the checkpoint workflow:

1. **Session ends** → Checkpoint created (`core/memory/checkpoints/session_YYYYMMDD.yaml`)
2. **Ingest runs** → Checkpoint embedded and stored in local Qdrant
3. **Sync runs** → Memories uploaded to cloud Qdrant
4. **Next session** → Memories available from both local and cloud

**Recommended workflow**:
- Manual sync after important sessions
- Automated sync handles periodic backups
- Use `sync_now.sh` before system shutdown/maintenance

## Security

- **SSH Key Authentication**: Required for unattended sync
- **No passwords in scripts**: Uses SSH keys only
- **Tunnel encryption**: All data encrypted via SSH
- **Local-first**: Local Qdrant is source of truth

**SSH Key Location**: `~/.ssh/id_ed25519` (or `id_rsa`)

## Related Documentation

- `core/memory/MEMORY_SYSTEM_GUIDE.md` - Memory system overview
- `core/memory/scripts/sync_cloud.py` - Sync implementation
- `CLAUDE.md` - Project architecture
- `infrastructure/cloudflare/` - Cloudflare D1 alternative sync

---

**Status**: Ready to deploy (pending Python environment setup)
**Last Updated**: 2025-12-28
**Maintainer**: Captain & First Mate
