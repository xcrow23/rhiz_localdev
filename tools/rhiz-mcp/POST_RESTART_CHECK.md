# Post-Restart Verification Checklist

## After Restarting Claude Code

### Quick MCP Health Check
Run this command in Claude Code to verify rhiz-mcp is operational:

```
Run memory_health_check
```

Expected output:
```
✅ Memory search is available
- sentence_transformers: installed
- Qdrant: connected at localhost:6333
- Collection: rhiz_memories (ready)
```

---

### If Health Check Fails

#### Option 1: Run Full Diagnostic (Recommended)
```bash
cd tools/rhiz-mcp
venv/Scripts/python verify_startup.py
```

This comprehensive script checks:
- ✅ Python package imports (sentence_transformers, qdrant_client, pyyaml)
- ✅ Qdrant connectivity (localhost:6333)
- ✅ Collection status (rhiz_memories)
- ✅ Checkpoint directory
- ✅ Actual memory search functionality

#### Option 2: Manual Checks

**1. Verify Qdrant is running:**
```bash
docker ps | grep qdrant
```
Should show: `rhiz_qdrant` with status `Up` and `(healthy)`

**2. If Qdrant is down, start it:**
```bash
docker-compose up -d qdrant
```

**3. Test Qdrant connection:**
```bash
curl http://localhost:6333/collections
```

**4. Check MCP server logs** (if available in Claude Code settings)

---

### Test Memory Search

Once health check passes, test the actual search:

```
Search checkpoints for "trading setup"
```

Or use the tool directly:
```
mcp__rhiz-mcp__checkpoint_search(
    query="previous session goals",
    limit=3
)
```

---

### What Was Fixed

**Problem:** MCP server couldn't find `sentence_transformers` module

**Solution:**
1. ✅ Installed `sentence-transformers` in rhiz-mcp venv
2. ✅ Installed `qdrant-client` in rhiz-mcp venv
3. ✅ Verified Qdrant container is running (it was already up)
4. ⏳ **Restart required** to load new packages into server process

**Qdrant Status:** Already running and healthy (up for 2 days)

---

### Quick Command Reference

```bash
# Full verification
tools/rhiz-mcp/venv/Scripts/python tools/rhiz-mcp/verify_startup.py

# Check Qdrant
docker ps | grep qdrant

# Start all services
docker-compose up -d

# View Qdrant logs
docker logs rhiz_qdrant --tail 50

# Check MCP venv packages
tools/rhiz-mcp/venv/Scripts/pip list | grep -E "(sentence|qdrant)"
```

---

### Expected First-Time Behavior

When you run `checkpoint_search` for the first time:
- Model `all-MiniLM-L6-v2` will auto-download (~80MB)
- Collection `rhiz_memories` will be auto-created in Qdrant
- First query may take 5-10 seconds (model loading)
- Subsequent queries: <1 second

---

## Verification Complete ✅

Once `memory_health_check` returns ✅, the system is fully operational:
- Session checkpoints can be searched semantically
- Memory context retrieval works across sessions
- Dyad state persistence is functional

**Next Steps:**
1. Load recent checkpoint: `get_resume_context()`
2. Test checkpoint search: `checkpoint_search(query="...")`
3. Verify dyad state: `get_dyad_state()`

---

*Created: 2026-01-05*
*Session: 30*
*Last Update: Pre-restart dependency installation*
