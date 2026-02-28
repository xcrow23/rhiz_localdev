#!/usr/bin/env python3
"""
Rhiz MCP Server Wrapper
Handles path setup and runs the MCP server with correct environment.
"""
import os
import sys
from pathlib import Path

# Set up paths
script_dir = Path(__file__).parent.resolve()
src_dir = script_dir / "src"

# Add src to path for imports
sys.path.insert(0, str(script_dir))

# Set RHIZ_ROOT if not already set
if "RHIZ_ROOT" not in os.environ:
    os.environ["RHIZ_ROOT"] = str(script_dir.parent.parent)

# Validate critical paths exist
rhiz_root = Path(os.environ["RHIZ_ROOT"])
dyad_md_path = rhiz_root / "core" / "daemon" / "dyad.md"
checkpoint_dir = rhiz_root / "core" / "memory" / "checkpoints"

if not dyad_md_path.exists():
    print(f"[rhiz-mcp] WARNING: dyad.md not found at {dyad_md_path}", file=sys.stderr)
    print(f"[rhiz-mcp] Server will continue but some tools may fail", file=sys.stderr)

if not checkpoint_dir.exists():
    print(f"[rhiz-mcp] INFO: Creating checkpoint directory at {checkpoint_dir}", file=sys.stderr)
    checkpoint_dir.mkdir(parents=True, exist_ok=True)

# Import and run server
from src.server import main
import asyncio

if __name__ == "__main__":
    print(f"[rhiz-mcp] Starting server...", file=sys.stderr)
    print(f"[rhiz-mcp] RHIZ_ROOT: {os.environ['RHIZ_ROOT']}", file=sys.stderr)
    asyncio.run(main())
