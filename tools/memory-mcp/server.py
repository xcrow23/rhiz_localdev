"""
Rhiz Memory MCP Server
Model Context Protocol server for semantic memory access.
Provides tools for searching, retrieving, and storing memories in Qdrant.
"""

import asyncio
import os
import sys
from pathlib import Path
from typing import Any, Dict, List

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent, Resource
from pydantic import AnyUrl
import json

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "core" / "memory" / "scripts"))

from embeddings import EmbeddingGenerator
from search import MemorySearcher
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct


# Initialize server
app = Server("rhiz-memory")

# Global instances (initialized on startup)
embedder: EmbeddingGenerator = None
searcher: MemorySearcher = None
qdrant_client: QdrantClient = None

# Configuration
QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", "6333"))
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "rhiz_memories")


# =========================
# Tool Definitions
# =========================

TOOLS = [
    Tool(
        name="memory_search",
        description="Search Rhiz memory system semantically. Returns relevant memories ranked by similarity to your query.",
        inputSchema={
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query (semantic, not keyword-based)"
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of results to return (default: 5)",
                    "default": 5
                },
                "section_filter": {
                    "type": "string",
                    "description": "Filter by section type: combined, session_arc, mental_model, hypotheses, questions, decisions, resume_prompt",
                    "enum": ["combined", "session_arc", "mental_model", "hypotheses", "questions", "decisions", "resume_prompt"]
                },
                "score_threshold": {
                    "type": "number",
                    "description": "Minimum similarity score (0-1, default: 0.5)",
                    "default": 0.5,
                    "minimum": 0,
                    "maximum": 1
                }
            },
            "required": ["query"]
        }
    ),
    Tool(
        name="memory_search_by_date",
        description="Search memories from a specific session date. Use format YYYYMMDD (e.g., 20251227).",
        inputSchema={
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query"
                },
                "session_date": {
                    "type": "string",
                    "description": "Session date in YYYYMMDD format"
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of results (default: 5)",
                    "default": 5
                }
            },
            "required": ["query", "session_date"]
        }
    ),
    Tool(
        name="memory_get_recent_sessions",
        description="Get information about recent sessions. Returns session arcs and metadata.",
        inputSchema={
            "type": "object",
            "properties": {
                "limit": {
                    "type": "integer",
                    "description": "Number of recent sessions to retrieve (default: 3)",
                    "default": 3
                }
            },
            "required": []
        }
    ),
    Tool(
        name="memory_store",
        description="Store a new memory in the vector database. Use for important realizations, decisions, or context that should be preserved.",
        inputSchema={
            "type": "object",
            "properties": {
                "content": {
                    "type": "string",
                    "description": "The memory content to store"
                },
                "metadata": {
                    "type": "object",
                    "description": "Metadata about this memory (session_date, section, checkpoint_id, etc.)",
                    "properties": {
                        "session_date": {"type": "string"},
                        "section": {"type": "string"},
                        "checkpoint_id": {"type": "string"},
                        "phase": {"type": "string"},
                        "source_file": {"type": "string"}
                    }
                }
            },
            "required": ["content"]
        }
    ),
    Tool(
        name="memory_stats",
        description="Get statistics about the memory database (collection info, point count, etc.)",
        inputSchema={
            "type": "object",
            "properties": {},
            "required": []
        }
    ),
    Tool(
        name="memory_health_check",
        description="Check health of the memory system (Qdrant connection, embedding model, etc.)",
        inputSchema={
            "type": "object",
            "properties": {},
            "required": []
        }
    )
]


# =========================
# Tool Handlers
# =========================

@app.list_tools()
async def list_tools() -> List[Tool]:
    """List all available memory tools."""
    return TOOLS


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> List[TextContent]:
    """Handle tool calls."""
    try:
        if name == "memory_search":
            return await handle_search(arguments)
        elif name == "memory_search_by_date":
            return await handle_search_by_date(arguments)
        elif name == "memory_get_recent_sessions":
            return await handle_recent_sessions(arguments)
        elif name == "memory_store":
            return await handle_store(arguments)
        elif name == "memory_stats":
            return await handle_stats(arguments)
        elif name == "memory_health_check":
            return await handle_health_check(arguments)
        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]
    except Exception as e:
        return [TextContent(type="text", text=f"Error executing {name}: {str(e)}")]


# =========================
# Resources API
# =========================

@app.list_resources()
async def list_resources() -> List[Resource]:
    """Expose memory data as resources"""
    return [
        Resource(
            uri="memory://recent",
            name="Recent Memory Points",
            description="Last 10 memory points from rhiz_memories collection",
            mimeType="application/json"
        ),
        Resource(
            uri="memory://sessions",
            name="Session Timeline",
            description="All sessions with dates and metadata",
            mimeType="application/json"
        )
    ]


@app.read_resource(uri=AnyUrl)
async def read_resource(uri: AnyUrl) -> str:
    """Serve resource content based on URI"""
    from qdrant_client.models import Filter, FieldCondition, MatchValue

    uri_str = str(uri)

    try:
        if uri_str == "memory://recent":
            # Query last 10 points
            results, _ = qdrant_client.scroll(
                collection_name=COLLECTION_NAME,
                limit=10,
                with_payload=True,
                with_vectors=False
            )

            points = []
            for point in results:
                points.append({
                    "id": str(point.id),
                    "content": point.payload.get("content", ""),
                    "metadata": {
                        "session_date": point.payload.get("session_date"),
                        "section": point.payload.get("section"),
                        "checkpoint_id": point.payload.get("checkpoint_id"),
                        "source_file": point.payload.get("source_file")
                    }
                })

            return json.dumps({
                "total": len(points),
                "points": points
            }, indent=2)

        elif uri_str == "memory://sessions":
            # Get all "combined" section points (one per session)
            results, _ = qdrant_client.scroll(
                collection_name=COLLECTION_NAME,
                scroll_filter=Filter(
                    must=[
                        FieldCondition(
                            key="section",
                            match=MatchValue(value="combined")
                        )
                    ]
                ),
                limit=100,
                with_payload=True,
                with_vectors=False
            )

            sessions = []
            for point in results:
                sessions.append({
                    "checkpoint_id": point.payload.get("checkpoint_id"),
                    "session_date": point.payload.get("session_date"),
                    "session_type": point.payload.get("session_type"),
                    "phase": point.payload.get("phase"),
                    "source_file": point.payload.get("source_file")
                })

            # Sort by date
            sessions.sort(key=lambda x: x.get("session_date", ""))

            return json.dumps({
                "total": len(sessions),
                "sessions": sessions
            }, indent=2)

        else:
            return json.dumps({
                "error": f"Unknown resource URI: {uri_str}",
                "available_uris": [
                    "memory://recent",
                    "memory://sessions"
                ]
            }, indent=2)

    except Exception as e:
        return json.dumps({
            "error": f"Error reading resource {uri_str}: {str(e)}"
        }, indent=2)


async def handle_search(args: Dict) -> List[TextContent]:
    """Handle memory_search tool."""
    query = args["query"]
    limit = args.get("limit", 5)
    section_filter = args.get("section_filter")
    score_threshold = args.get("score_threshold", 0.5)

    memories = searcher.search(
        query=query,
        limit=limit,
        section_filter=section_filter,
        score_threshold=score_threshold
    )

    if not memories:
        return [TextContent(
            type="text",
            text=f"No memories found for query: '{query}' (threshold: {score_threshold})"
        )]

    # Format results
    result_text = f"Found {len(memories)} relevant memories for: '{query}'\n\n"

    for idx, memory in enumerate(memories, 1):
        result_text += f"[{idx}] Score: {memory['score']:.3f}\n"
        result_text += f"Source: {memory['metadata']['source_file']}\n"
        result_text += f"Date: {memory['metadata']['session_date']}\n"
        result_text += f"Section: {memory['metadata']['section']}\n"
        result_text += f"{'=' * 60}\n"

        content = memory['content']
        if isinstance(content, dict):
            for key, value in content.items():
                if value:
                    result_text += f"\n{key.upper()}:\n"
                    if isinstance(value, list):
                        for item in value:
                            result_text += f"  • {item}\n"
                    else:
                        result_text += f"  {value}\n"
        else:
            result_text += f"\n{content}\n"

        result_text += f"\n{'-' * 60}\n\n"

    return [TextContent(type="text", text=result_text)]


async def handle_search_by_date(args: Dict) -> List[TextContent]:
    """Handle memory_search_by_date tool."""
    query = args["query"]
    session_date = args["session_date"]
    limit = args.get("limit", 5)

    memories = searcher.search_by_date(
        query=query,
        session_date=session_date,
        limit=limit
    )

    if not memories:
        return [TextContent(
            type="text",
            text=f"No memories found for date {session_date} matching: '{query}'"
        )]

    result_text = f"Found {len(memories)} memories from {session_date} for: '{query}'\n\n"

    for idx, memory in enumerate(memories, 1):
        result_text += f"[{idx}] Score: {memory['score']:.3f}\n"
        result_text += f"Section: {memory['metadata'].get('section', 'unknown')}\n"
        result_text += f"{'=' * 60}\n"
        result_text += f"\n{memory['content']}\n"
        result_text += f"\n{'-' * 60}\n\n"

    return [TextContent(type="text", text=result_text)]


async def handle_recent_sessions(args: Dict) -> List[TextContent]:
    """Handle memory_get_recent_sessions tool."""
    limit = args.get("limit", 3)

    sessions = searcher.get_recent_sessions(limit=limit)

    if not sessions:
        return [TextContent(type="text", text="No recent sessions found.")]

    result_text = f"Retrieved {len(sessions)} recent sessions:\n\n"

    for idx, session in enumerate(sessions, 1):
        result_text += f"[{idx}] {session['checkpoint_id']}\n"
        result_text += f"Date: {session['session_date']}\n"
        result_text += f"Type: {session.get('session_type', 'unknown')}\n"
        result_text += f"{'=' * 60}\n"

        if isinstance(session.get('content'), dict):
            if 'session_arc' in session['content']:
                result_text += f"\nSession Arc:\n{session['content']['session_arc']}\n"

        result_text += f"\n{'-' * 60}\n\n"

    return [TextContent(type="text", text=result_text)]


async def handle_store(args: Dict) -> List[TextContent]:
    """Handle memory_store tool."""
    content = args["content"]
    metadata = args.get("metadata", {})

    # Generate embedding
    embedding = embedder.embed(content).tolist()

    # Get next point ID
    collection_info = qdrant_client.get_collection(COLLECTION_NAME)
    next_id = collection_info.points_count

    # Prepare payload
    payload = {
        "content": content,
        "source_file": metadata.get("source_file", "cli_manual_entry"),
        "session_date": metadata.get("session_date", "unknown"),
        "section": metadata.get("section", "manual_entry"),
        "checkpoint_id": metadata.get("checkpoint_id", "manual"),
        "phase": metadata.get("phase", "manual")
    }

    # Store in Qdrant
    point = PointStruct(
        id=next_id,
        vector=embedding,
        payload=payload
    )

    qdrant_client.upsert(
        collection_name=COLLECTION_NAME,
        points=[point]
    )

    return [TextContent(
        type="text",
        text=f"Memory stored successfully!\n\nPoint ID: {next_id}\nContent: {content[:100]}...\nMetadata: {payload}"
    )]


async def handle_stats(args: Dict) -> List[TextContent]:
    """Handle memory_stats tool."""
    collection_info = qdrant_client.get_collection(COLLECTION_NAME)

    stats = {
        "collection_name": COLLECTION_NAME,
        "total_points": collection_info.points_count,
        "vector_dimension": collection_info.config.params.vectors.size,
        "status": collection_info.status,
        "optimizer_status": collection_info.optimizer_status
    }

    result_text = "Memory Database Statistics\n"
    result_text += "=" * 60 + "\n\n"
    for key, value in stats.items():
        result_text += f"{key.replace('_', ' ').title()}: {value}\n"

    return [TextContent(type="text", text=result_text)]


async def handle_health_check(args: Dict) -> List[TextContent]:
    """Handle memory_health_check tool."""
    checks = []

    # Check Qdrant connection
    try:
        collection_info = qdrant_client.get_collection(COLLECTION_NAME)
        checks.append(f"✓ Qdrant: Connected ({collection_info.points_count} points)")
    except Exception as e:
        checks.append(f"✗ Qdrant: Failed - {str(e)}")

    # Check embedding model
    try:
        test_embedding = embedder.embed("test")
        checks.append(f"✓ Embedder: Loaded (dim={len(test_embedding)})")
    except Exception as e:
        checks.append(f"✗ Embedder: Failed - {str(e)}")

    # Check searcher
    try:
        test_results = searcher.search("test", limit=1)
        checks.append(f"✓ Searcher: Operational")
    except Exception as e:
        checks.append(f"✗ Searcher: Failed - {str(e)}")

    result_text = "Rhiz Memory System Health Check\n"
    result_text += "=" * 60 + "\n\n"
    result_text += "\n".join(checks)
    result_text += f"\n\nConfiguration:\n"
    result_text += f"  Qdrant: {QDRANT_HOST}:{QDRANT_PORT}\n"
    result_text += f"  Collection: {COLLECTION_NAME}\n"

    return [TextContent(type="text", text=result_text)]


# =========================
# Startup & Main
# =========================

async def init_server():
    """Initialize server components."""
    global embedder, searcher, qdrant_client

    print(f"Initializing Rhiz Memory MCP Server...", file=sys.stderr)
    print(f"Qdrant: {QDRANT_HOST}:{QDRANT_PORT}", file=sys.stderr)
    print(f"Collection: {COLLECTION_NAME}", file=sys.stderr)

    # Initialize components
    embedder = EmbeddingGenerator()
    searcher = MemorySearcher(
        qdrant_host=QDRANT_HOST,
        qdrant_port=QDRANT_PORT,
        collection_name=COLLECTION_NAME
    )
    qdrant_client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)

    print("Memory system initialized successfully!", file=sys.stderr)


async def main():
    """Main entry point for the MCP server."""
    await init_server()

    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
