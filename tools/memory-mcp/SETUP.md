# Memory MCP Server Setup Guide

## Current Status

✅ **Server Code**: Complete and ready (server.py)
✅ **Documentation**: README.md created
✅ **Requirements**: Defined in requirements.txt
⚠️ **Python Environment**: Needs setup (WSL Python missing pip)

## Installation Steps

### Option 1: Windows Python (Recommended for Claude Desktop)

If you're using Claude Desktop (not CLI), you'll want to run the MCP server using Windows Python:

1. **Install Python on Windows** (if not already installed):
   - Download from https://python.org
   - Ensure "Add to PATH" is checked during installation

2. **Install dependencies** (from Windows Command Prompt or PowerShell):
   ```cmd
   cd C:\Users\dread\documents\Rhiz\origin\tools\memory-mcp
   pip install -r requirements.txt
   ```

3. **Test the server**:
   ```cmd
   python server.py
   ```

4. **Configure Claude Desktop**:
   Edit Claude Desktop MCP config (location varies by OS):

   ```json
   {
     "mcpServers": {
       "rhiz-memory": {
         "command": "python",
         "args": ["C:\\Users\\dread\\documents\\Rhiz\\origin\\tools\\memory-mcp\\server.py"],
         "env": {
           "QDRANT_HOST": "localhost",
           "QDRANT_PORT": "6333"
         }
       }
     }
   }
   ```

### Option 2: WSL Python (For CLI Usage)

If you're running Claude Code CLI in WSL:

1. **Install pip** in WSL:
   ```bash
   sudo apt update
   sudo apt install python3-pip
   ```

2. **Install dependencies**:
   ```bash
   cd /mnt/c/Users/dread/documents/Rhiz/origin/tools/memory-mcp
   pip3 install -r requirements.txt
   ```

3. **Test the server**:
   ```bash
   python3 server.py
   ```

### Option 3: Docker Container (Future Enhancement)

For a fully isolated environment, we could containerize the Memory MCP server. This would require:
- Creating a Dockerfile
- Adding memory-mcp service to docker-compose.yml
- Exposing MCP over stdio or HTTP

## Verification

Once installed, test with:

```bash
# Start the server (it will wait for MCP client connection)
python server.py

# In another terminal, you can test Qdrant connectivity:
python -c "from qdrant_client import QdrantClient; c = QdrantClient('localhost', 6333); print(c.get_collection('rhiz_memories'))"
```

Expected output should show collection info with 161+ points.

## Troubleshooting

### "No module named 'mcp'"
- Run: `pip install mcp` or `pip3 install mcp`

### "Qdrant connection failed"
- Ensure Docker container is running: `docker ps | grep qdrant`
- Start if needed: `docker-compose up -d qdrant`
- Check port: `curl http://localhost:6333/collections/rhiz_memories`

### "sentence_transformers download failed"
- Requires ~80MB download on first run (model: all-MiniLM-L6-v2)
- Ensure internet connectivity
- Model cached to `~/.cache/huggingface/`

### "Permission denied" in WSL
- Check file permissions: `ls -la server.py`
- Make executable: `chmod +x server.py`
- Try with sudo: `sudo python3 server.py` (not recommended for production)

## Current Environment Detection

As of 2025-12-28:
- ✅ WSL Python 3.12.3 detected at `/usr/bin/python3`
- ❌ pip not available in WSL Python
- ✅ Qdrant running in Docker (localhost:6333)
- ✅ 161 memory points in collection

**Recommendation**: Install pip in WSL for CLI usage, or use Windows Python for Claude Desktop integration.

## Next Steps

1. Choose installation method (Windows Python vs WSL)
2. Install dependencies
3. Test server startup
4. Configure Claude Code/Desktop MCP settings
5. Test memory search from Claude

## Questions?

If you encounter issues not covered here, check:
- `README.md` - Full documentation
- `core/memory/scripts/` - Example of how memory system is used
- Docker logs: `docker logs rhiz_qdrant`

---

**Created**: 2025-12-28
**Status**: Awaiting environment setup
