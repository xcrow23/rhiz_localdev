# Memory Infrastructure Deployment Checklist

**Built**: December 28, 2025
**Status**: Ready for activation
**Time Required**: 15-30 minutes

---

## Prerequisites

- [ ] Docker running (Qdrant container up)
- [ ] SSH access to Hostinger VPS (72.62.81.128)
- [ ] Python 3 with pip available

---

## Step 1: Python Environment Setup

Choose **ONE** based on your preferred Claude interface:

### Option A: Windows Python (for Claude Desktop)

```cmd
:: Test if Python and pip are available
python --version
pip --version

:: Install Memory MCP dependencies
cd C:\Users\dread\documents\rhiz_localdev\tools\memory-mcp
pip install -r requirements.txt

:: Install sync dependencies
pip install qdrant-client
```

### Option B: WSL Python (for Claude Code CLI)

```bash
# Install pip if needed
sudo apt update
sudo apt install python3-pip

# Install Memory MCP dependencies
cd /mnt/c/Users/dread/documents/rhiz_localdev/tools/memory-mcp
pip3 install -r requirements.txt

# Install sync dependencies
pip3 install qdrant-client
```

**Verify installation**:
```bash
python3 -c "from qdrant_client import QdrantClient; import mcp; import sentence_transformers; print('✓ All dependencies installed')"
```

---

## Step 2: Test Memory MCP Server

```bash
cd tools/memory-mcp
python3 server.py
```

**Expected output**:
```
Initializing Rhiz Memory MCP Server...
Qdrant: localhost:6333
Collection: rhiz_memories
Loading embedding model: all-MiniLM-L6-v2...
Model loaded. Embedding dimension: 384
Memory system initialized successfully!
```

Press `Ctrl+C` to stop. ✅ If you see this, MCP server works!

---

## Step 3: Setup SSH Access

```bash
cd tools/memory-sync
./setup_ssh.sh
```

**If prompted for SSH key**:
```bash
# Generate key if you don't have one
ssh-keygen -t ed25519

# Copy to server
ssh-copy-id root@72.62.81.128
# Enter password when prompted
```

**Verify SSH**:
```bash
ssh root@72.62.81.128 "echo 'SSH works!'"
```

---

## Step 4: Run First Cloud Sync

```bash
cd tools/memory-sync
./sync_now.sh
```

**Expected output**:
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
  Synced 161/161

Cloud after sync: 161 points

✓ Sync completed successfully!
```

---

## Step 5: Verify Cloud Has Memories

```bash
# Establish tunnel to cloud Qdrant
ssh -L 6335:localhost:6333 -f -N root@72.62.81.128

# Check cloud point count
curl -s http://localhost:6335/collections/rhiz_memories | grep points_count

# Should show: "points_count": 161
```

---

## Step 6: Enable Automated Sync (Optional)

**For 6-hourly automatic cloud backup**:

```bash
cd tools/memory-sync

# Copy systemd files
sudo cp rhiz-memory-sync.service /etc/systemd/system/
sudo cp rhiz-memory-sync.timer /etc/systemd/system/

# Reload systemd
sudo systemctl daemon-reload

# Enable and start
sudo systemctl enable rhiz-memory-sync.timer
sudo systemctl start rhiz-memory-sync.timer

# Verify it's scheduled
systemctl list-timers | grep rhiz
```

**Expected output**:
```
NEXT                         LEFT          LAST  PASSED  UNIT                       ACTIVATES
Sat 2025-12-28 18:00:00 EST  5h left       n/a   n/a     rhiz-memory-sync.timer     rhiz-memory-sync.service
```

---

## Step 7: Configure Claude Code MCP (CLI Usage)

**Find your Claude Code MCP config file** (location varies):
- Linux: `~/.config/claude/mcp.json`
- macOS: `~/Library/Application Support/Claude/mcp.json`
- Windows: `%APPDATA%\Claude\mcp.json`

**Add Memory MCP server**:
```json
{
  "mcpServers": {
    "rhiz-memory": {
      "command": "python3",
      "args": ["/mnt/c/Users/dread/documents/rhiz_localdev/tools/memory-mcp/server.py"],
      "env": {
        "QDRANT_HOST": "localhost",
        "QDRANT_PORT": "6333"
      }
    }
  }
}
```

**Restart Claude Code** to load the server.

---

## Step 8: Test Memory Search

In Claude Code CLI, you should now have access to memory tools:

```
"Search my memories for 'Fathom implementation'"
```

Claude should be able to use the `memory_search` tool and return relevant session history!

---

## Troubleshooting

### "No module named 'mcp'"
```bash
pip3 install mcp
```

### "Qdrant connection failed"
```bash
# Check Qdrant is running
docker ps | grep qdrant

# Start if needed
docker-compose up -d qdrant

# Test connection
curl http://localhost:6333/collections/rhiz_memories
```

### "SSH tunnel failed"
```bash
# Verify SSH works
ssh root@72.62.81.128

# Check firewall settings on Hostinger
# Ensure port 22 is open
```

### Sync shows "0 points"
```bash
# Check local Qdrant has memories
curl http://localhost:6333/collections/rhiz_memories | grep points_count

# If 0, need to run ingest
cd core/memory/scripts
python3 ingest.py
```

---

## Verification Commands

**Check everything is working**:

```bash
# 1. Local Qdrant running
docker ps | grep qdrant

# 2. Local has memories
curl -s http://localhost:6333/collections/rhiz_memories | grep points_count

# 3. Cloud reachable
ssh root@72.62.81.128 "echo 'Cloud accessible'"

# 4. Memory MCP dependencies
python3 -c "import mcp, qdrant_client, sentence_transformers; print('✓')"

# 5. Sync logs
tail -20 tools/memory-sync/sync.log

# 6. Systemd timer (if enabled)
systemctl status rhiz-memory-sync.timer
```

---

## Success Criteria

✅ Memory MCP server starts without errors
✅ Cloud sync completes: Local 161 → Cloud 161
✅ Automated sync timer scheduled (if enabled)
✅ Claude Code can use `memory_search` tool
✅ SSH tunnel to cloud Qdrant works

---

## Next Steps After Deployment

1. **Test memory search** - Ask Claude to find past sessions
2. **Monitor first auto-sync** - Check logs after 6 hours
3. **Export n8n workflows** - Version control automation
4. **Build skill router** - Enable pattern-based skills
5. **Setup local models** - Ollama configs for Qwen/DeepSeek

---

## Need Help?

**Documentation**:
- `tools/memory-mcp/README.md` - Memory MCP full docs
- `tools/memory-mcp/SETUP.md` - Installation guide
- `tools/memory-sync/README.md` - Sync system docs
- `docs/sessions/SESSION_20251228_MEMORY_INFRASTRUCTURE_BUILD.md` - Build session notes

**Key Files**:
- `tools/memory-mcp/server.py` - MCP server implementation
- `tools/memory-sync/sync_now.sh` - Manual sync script
- `core/memory/scripts/sync_cloud.py` - Sync implementation

---

**Last Updated**: 2025-12-28
**Estimated Time**: 15-30 minutes
**Difficulty**: Moderate (requires Python and SSH setup)
