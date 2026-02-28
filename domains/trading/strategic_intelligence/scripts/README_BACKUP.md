# Qdrant Backup and Restore Guide

## Overview

The `qdrant_backup.py` utility provides comprehensive backup and restore capabilities for all SIL Qdrant collections.

**Backed Up Collections:**
- `sil_trade_outcomes` - All trade history with full context
- `sil_strategy_performance` - Aggregated strategy performance metrics
- `sil_decision_log` - All SIL decisions (including "wait" decisions)

---

## Quick Start

### Create a Backup

```bash
cd scripts
python qdrant_backup.py backup --output-dir ../backups
```

Output:
```
[Backup] Starting backup to ../backups/sil_backup_2026-01-03_14-30-00.json
[Backup] Backing up sil_trade_outcomes...
[Backup] ✓ sil_trade_outcomes: 47 points
[Backup] Backing up sil_strategy_performance...
[Backup] ✓ sil_strategy_performance: 12 points
[Backup] Backing up sil_decision_log...
[Backup] ✓ sil_decision_log: 203 points
[Backup] Complete! Backup saved: ../backups/sil_backup_2026-01-03_14-30-00.json (0.45 MB)
```

### Restore from Backup

```bash
python qdrant_backup.py restore --backup-file ../backups/sil_backup_2026-01-03_14-30-00.json
```

**⚠️ Warning**: This appends to existing collections. Use `--overwrite` to replace.

### List Available Backups

```bash
python qdrant_backup.py list --backup-dir ../backups
```

### Verify Backup Integrity

```bash
python qdrant_backup.py verify --backup-file ../backups/sil_backup_2026-01-03_14-30-00.json
```

Output:
```json
{
  "status": "ok",
  "backup_timestamp": "2026-01-03T14:30:00.000Z",
  "total_points": 262,
  "collections": {
    "sil_trade_outcomes": {
      "status": "ok",
      "points": 47
    },
    "sil_strategy_performance": {
      "status": "ok",
      "points": 12
    },
    "sil_decision_log": {
      "status": "ok",
      "points": 203
    }
  },
  "file_size_mb": 0.45
}
```

### Clean Up Old Backups

```bash
# Delete backups older than 90 days (default)
python qdrant_backup.py cleanup --backup-dir ../backups

# Custom retention period
python qdrant_backup.py cleanup --backup-dir ../backups --retention-days 30
```

---

## Advanced Usage

### Remote Qdrant Instance

```bash
# Backup from remote Qdrant
python qdrant_backup.py backup \
  --output-dir ../backups \
  --host qdrant.example.com \
  --port 6333

# Or use environment variables
export QDRANT_HOST=qdrant.example.com
export QDRANT_PORT=6333
export QDRANT_API_KEY=your_api_key_here

python qdrant_backup.py backup --output-dir ../backups
```

### Restore with Overwrite

```bash
# ⚠️ DANGER: This DELETES existing collections before restore
python qdrant_backup.py restore \
  --backup-file ../backups/sil_backup_2026-01-03.json \
  --overwrite
```

**Use Case**: Disaster recovery, resetting to known good state.

---

## Scheduled Backups

### Option 1: Cron (Linux/Mac)

```bash
# Edit crontab
crontab -e

# Add daily backup at 2 AM
0 2 * * * cd /path/to/strategic_intelligence/scripts && python qdrant_backup.py backup --output-dir ../backups

# Add weekly cleanup (Sundays at 3 AM)
0 3 * * 0 cd /path/to/strategic_intelligence/scripts && python qdrant_backup.py cleanup --backup-dir ../backups --retention-days 90
```

### Option 2: Windows Task Scheduler

1. Open Task Scheduler
2. Create Basic Task
3. Set trigger: Daily at 2:00 AM
4. Action: Start a program
   - Program: `python`
   - Arguments: `qdrant_backup.py backup --output-dir ../backups`
   - Start in: `C:\path\to\strategic_intelligence\scripts`

### Option 3: Docker (Recommended for Production)

```dockerfile
# Add to docker-compose.yml
services:
  qdrant-backup:
    image: python:3.10-slim
    volumes:
      - ./strategic_intelligence:/app
      - ./backups:/backups
    working_dir: /app/scripts
    environment:
      - QDRANT_HOST=qdrant
      - QDRANT_PORT=6333
    command: >
      sh -c "pip install qdrant-client numpy pandas &&
             while true; do
               python qdrant_backup.py backup --output-dir /backups &&
               python qdrant_backup.py cleanup --backup-dir /backups --retention-days 90 &&
               sleep 86400;
             done"
```

---

## Backup File Format

Backups are stored as JSON with the following structure:

```json
{
  "timestamp": "2026-01-03T14:30:00.000Z",
  "collections": {
    "sil_trade_outcomes": [
      {
        "id": "trade_20260103_001",
        "vector": [0.1, 0.2, ...],
        "payload": {
          "trade_id": "trade_20260103_001",
          "strategy_name": "mean_reversion",
          "pnl_percent": 1.23,
          ...
        }
      },
      ...
    ],
    "sil_strategy_performance": [...],
    "sil_decision_log": [...]
  }
}
```

**Storage Requirements**:
- ~1 KB per trade outcome
- ~500 bytes per strategy performance snapshot
- ~200 bytes per decision log entry
- **Typical backup size**: 0.5-2 MB for 100 trades

---

## Best Practices

### 1. Backup Frequency

| Environment | Frequency | Retention |
|------------|-----------|-----------|
| Development | Weekly | 30 days |
| Paper Trading | Daily | 90 days |
| Small Capital Live | Daily | 180 days |
| Production | Daily | 365 days |

### 2. Backup Storage

**Local Development**:
```bash
backups/
├── sil_backup_2026-01-01_02-00-00.json
├── sil_backup_2026-01-02_02-00-00.json
└── sil_backup_2026-01-03_02-00-00.json
```

**Production (Cloud)**:
- Store in S3/Backblaze for redundancy
- Use versioning to prevent accidental deletion
- Encrypt backups containing real trading data

### 3. Disaster Recovery Workflow

**Scenario**: Qdrant data corrupted or lost

1. **Stop trading**:
   ```python
   # In trading script
   sil.close()
   ```

2. **Verify backup**:
   ```bash
   python qdrant_backup.py verify --backup-file ../backups/latest.json
   ```

3. **Restore**:
   ```bash
   python qdrant_backup.py restore --backup-file ../backups/latest.json --overwrite
   ```

4. **Verify restoration**:
   ```python
   from memory.qdrant_client import QdrantMemoryClient
   client = QdrantMemoryClient()
   stats = client.get_collection_stats()
   print(stats)
   ```

5. **Resume trading** (only after verification)

### 4. Pre-Deployment Checklist

Before enabling learning/memory features:

- [ ] Create initial backup
- [ ] Test restore on dev environment
- [ ] Set up scheduled backups
- [ ] Configure backup retention
- [ ] Document restore procedure
- [ ] Test disaster recovery workflow

---

## Troubleshooting

### Error: "Connection refused"

**Cause**: Qdrant not running.

**Fix**:
```bash
# Check if Qdrant is running
curl http://localhost:6333/collections

# If not, start it
docker run -p 6333:6333 qdrant/qdrant
```

### Error: "Collection not found"

**Cause**: Collections haven't been created yet.

**Fix**: Run SIL with memory enabled once to initialize collections:
```python
from strategic_intelligence import SILOrchestrator
sil = SILOrchestrator(enable_memory=True)
# Collections are now created
```

### Backup File is Huge (>100 MB)

**Cause**: Too many decision log entries (likely logging every market tick).

**Fix**: Implement decision log cleanup:
```python
# Delete decision logs older than 30 days
client.delete_old_decisions(days_to_keep=30)
```

### Restore Takes Very Long

**Cause**: Large number of points (>10,000).

**Fix**: The utility uses batching (100 points at a time). This is normal. For very large restores (>100K points), consider:
1. Increasing batch size in code
2. Using Qdrant's snapshot feature (native Qdrant backups)

---

## Security Considerations

### 1. Backup Encryption

Backups contain trading data (entry prices, PnL, strategy parameters). For live trading:

```bash
# Encrypt backup
gpg --symmetric --cipher-algo AES256 ../backups/sil_backup_2026-01-03.json

# Decrypt for restore
gpg ../backups/sil_backup_2026-01-03.json.gpg
python qdrant_backup.py restore --backup-file ../backups/sil_backup_2026-01-03.json
```

### 2. Backup Access Control

```bash
# Restrict backup directory permissions
chmod 700 ../backups
```

### 3. Cloud Storage (Production)

```bash
# Upload to S3 after backup
aws s3 cp ../backups/sil_backup_2026-01-03.json \
  s3://my-sil-backups/backups/ \
  --sse AES256
```

---

## Integration with SIL

### Backup Before Major Changes

```python
from strategic_intelligence.scripts.qdrant_backup import QdrantBackup

# Before changing strategies or learning parameters
backup = QdrantBackup()
backup_file = backup.backup_all_collections(Path("./backups"))
print(f"Pre-change backup: {backup_file}")

# Make changes...

# If something goes wrong, restore
# backup.restore_from_backup(backup_file, overwrite=True)
```

### Automated Backup on Shutdown

```python
# In trading script
import atexit
from strategic_intelligence.scripts.qdrant_backup import QdrantBackup

def backup_on_exit():
    backup = QdrantBackup()
    backup.backup_all_collections(Path("./backups"))
    print("Backup complete - safe to shutdown")

atexit.register(backup_on_exit)
```

---

## Next Steps

1. **Test backup now**:
   ```bash
   python qdrant_backup.py backup --output-dir ../backups
   ```

2. **Set up scheduled backups** (choose method above)

3. **Test restore procedure** on development environment

4. **Document your backup location** in `.env` or README

5. **Set calendar reminder** to verify backups monthly

---

**Backup Status**: Ready for production use ✅
**Last Updated**: 2026-01-03
