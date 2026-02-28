#!/usr/bin/env python3
"""
Rhiz MCP Server

Unified Model Context Protocol server for the Rhiz dyad.
Exposes tools for:
- Dyad state management (daemon layer)
- Pattern operations
- Memory integration (delegates to memory-mcp)
- Trading operations (delegates to Fathom)

This server enables bidirectional state management between Captain and First Mate.
"""

import asyncio
import json
import sys
from typing import Any
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent, Resource
from pydantic import AnyUrl

try:
    # Try relative imports (when run as module)
    from .dyad_state import DyadState
    from .checkpoint_manager import CheckpointManager
    from .memory_search import MemorySearchInterface
except ImportError:
    # Fall back to direct imports (when run as script with src/ in path)
    from dyad_state import DyadState
    from checkpoint_manager import CheckpointManager
    from memory_search import MemorySearchInterface

# Initialize state manager
dyad_state = DyadState()
checkpoint_manager = CheckpointManager()

# Lazy initialization for memory search (don't fail server startup if Qdrant unavailable)
_memory_search_instance = None
_memory_search_last_error = None
_memory_search_retry_count = 0

def _get_memory_search():
    """
    Lazy initialization of memory search with automatic retry.
    Returns (instance, error_message) tuple.
    If instance is None, error_message explains why.
    Self-healing: will retry on every call until successful.
    """
    global _memory_search_instance, _memory_search_last_error, _memory_search_retry_count

    # Return cached instance if available
    if _memory_search_instance is not None:
        return (_memory_search_instance, None)

    # Attempt initialization
    try:
        _memory_search_instance = MemorySearchInterface()
        _memory_search_retry_count = 0
        print(f"[rhiz-mcp] Memory search initialized successfully", file=sys.stderr)
        return (_memory_search_instance, None)
    except Exception as e:
        _memory_search_retry_count += 1
        error_msg = (
            f"Memory search unavailable (attempt {_memory_search_retry_count}): {str(e)}\n"
            f"Verify Qdrant is running on localhost:6333 and collection 'rhiz_memories' exists.\n"
            f"The system will automatically retry on next use."
        )
        _memory_search_last_error = error_msg
        print(f"[rhiz-mcp] {error_msg}", file=sys.stderr)
        return (None, error_msg)


# Skill Router singleton (lazy initialization)
_skill_router_instance = None
_skill_router_retry_count = 0
_skill_router_last_error = None

def _get_skill_router():
    """
    Get or create skill router instance (singleton pattern).
    Returns: (SkillRouter instance or None, error message or None)
    """
    global _skill_router_instance, _skill_router_retry_count, _skill_router_last_error

    if _skill_router_instance is not None:
        return (_skill_router_instance, None)

    try:
        import sys
        from pathlib import Path
        rhiz_root = Path(__file__).parent.parent.parent.parent
        if str(rhiz_root) not in sys.path:
            sys.path.insert(0, str(rhiz_root))

        from core.skills.router import SkillRouter

        _skill_router_instance = SkillRouter()
        _skill_router_retry_count = 0
        print(f"[rhiz-mcp] Skill router initialized successfully", file=sys.stderr)
        return (_skill_router_instance, None)
    except Exception as e:
        _skill_router_retry_count += 1
        error_msg = (
            f"Skill router unavailable (attempt {_skill_router_retry_count}): {str(e)}\n"
            f"Verify Qdrant is running and 'rhiz_skills' collection exists.\n"
            f"Run: python core/skills/scripts/initialize_skills_collection.py\n"
            f"     python core/skills/scripts/ingest_skills.py\n"
            f"The system will automatically retry on next use."
        )
        _skill_router_last_error = error_msg
        print(f"[rhiz-mcp] {error_msg}", file=sys.stderr)
        return (None, error_msg)


# Create MCP server
app = Server("rhiz-mcp")


# ========================================
# DAEMON LAYER TOOLS
# ========================================

@app.list_tools()
async def list_tools() -> list[Tool]:
    """List all available tools"""
    return [
        # Dyad State Query Tools
        Tool(
            name="get_dyad_state",
            description="Get complete dyad state including both partners' status, shared focus, and metrics",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="get_captain_state",
            description="Get current Captain state (availability, focus, energy, physical context)",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="get_shared_focus",
            description="Get current shared focus (domain, objective, blockers, next action)",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="get_dyad_summary",
            description="Get human-readable summary of dyad state for display",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),

        # Captain → First Mate Tools
        Tool(
            name="set_captain_state",
            description="Update Captain's current state (Captain invokes)",
            inputSchema={
                "type": "object",
                "properties": {
                    "availability": {
                        "type": "string",
                        "enum": ["engaged", "available", "away"],
                        "description": "Current availability status"
                    },
                    "focus": {
                        "type": "string",
                        "description": "Current focus area or task"
                    },
                    "energy": {
                        "type": "string",
                        "enum": ["high", "medium", "low"],
                        "description": "Current energy level"
                    },
                    "physical_context": {
                        "type": "string",
                        "description": "Physical location or constraints"
                    }
                },
                "required": []
            }
        ),

        # First Mate → Captain Tools
        Tool(
            name="propose_focus_shift",
            description="First Mate proposes changing focus domain or objective",
            inputSchema={
                "type": "object",
                "properties": {
                    "new_domain": {
                        "type": "string",
                        "enum": ["trading", "research", "development", "planning", "infrastructure"],
                        "description": "Proposed domain"
                    },
                    "rationale": {
                        "type": "string",
                        "description": "Why this shift makes sense"
                    }
                },
                "required": ["new_domain", "rationale"]
            }
        ),
        Tool(
            name="signal_completion",
            description="First Mate signals completion of objective",
            inputSchema={
                "type": "object",
                "properties": {
                    "objective": {
                        "type": "string",
                        "description": "What was completed"
                    },
                    "outcome": {
                        "type": "string",
                        "description": "Result or deliverable"
                    }
                },
                "required": ["objective", "outcome"]
            }
        ),

        # Mutual Tools
        Tool(
            name="update_shared_focus",
            description="Update the dyad's shared focus (either partner)",
            inputSchema={
                "type": "object",
                "properties": {
                    "domain": {
                        "type": "string",
                        "enum": ["trading", "research", "development", "planning", "infrastructure"],
                        "description": "Active domain"
                    },
                    "objective": {
                        "type": "string",
                        "description": "Current objective"
                    },
                    "blockers": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Known blockers"
                    },
                    "next_action": {
                        "type": "string",
                        "description": "Immediate next step"
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="update_active_domain",
            description="Update status of an active domain",
            inputSchema={
                "type": "object",
                "properties": {
                    "domain": {
                        "type": "string",
                        "description": "Domain name (e.g., 'trading', 'memory')"
                    },
                    "status": {
                        "type": "string",
                        "enum": ["disconnected", "configured", "connected", "operational", "error"],
                        "description": "Current status"
                    },
                    "details": {
                        "type": "string",
                        "description": "Status details or error message"
                    }
                },
                "required": ["domain", "status"]
            }
        ),
        Tool(
            name="append_dyad_note",
            description="Add a note to strengths, friction points, or evolution suggestions",
            inputSchema={
                "type": "object",
                "properties": {
                    "category": {
                        "type": "string",
                        "enum": ["strengths_observed", "friction_points", "evolution_suggestions"],
                        "description": "Note category"
                    },
                    "note": {
                        "type": "string",
                        "description": "Note content"
                    }
                },
                "required": ["category", "note"]
            }
        ),
        Tool(
            name="signal_blocker",
            description="Signal a blocker preventing progress",
            inputSchema={
                "type": "object",
                "properties": {
                    "description": {
                        "type": "string",
                        "description": "What is blocked and why"
                    },
                    "severity": {
                        "type": "string",
                        "enum": ["minor", "moderate", "blocking"],
                        "description": "How much this blocks progress"
                    }
                },
                "required": ["description"]
            }
        ),

        # Checkpoint Tools (Session Continuity)
        Tool(
            name="list_checkpoints",
            description="List recent session checkpoints",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "number",
                        "description": "Maximum number of checkpoints to return (default: 10)"
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="load_checkpoint",
            description="Load a session checkpoint for context (loads most recent if no filename specified)",
            inputSchema={
                "type": "object",
                "properties": {
                    "filename": {
                        "type": "string",
                        "description": "Checkpoint filename to load (e.g., 'session_20251226_wave1.yaml'). Omit to load most recent."
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="get_resume_context",
            description="Get formatted resume context from checkpoint for session handshake",
            inputSchema={
                "type": "object",
                "properties": {
                    "filename": {
                        "type": "string",
                        "description": "Checkpoint filename. Omit to use most recent."
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="write_checkpoint",
            description="Write a new session checkpoint",
            inputSchema={
                "type": "object",
                "properties": {
                    "checkpoint_data": {
                        "type": "object",
                        "description": "Checkpoint data following the session schema"
                    },
                    "description": {
                        "type": "string",
                        "description": "Brief description for filename (e.g., 'wave2_completion')"
                    }
                },
                "required": ["checkpoint_data"]
            }
        ),

        # Memory Search Tools (Semantic Retrieval)
        # Skill: memory_search (core/skills/registry/memory_search.yaml)
        Tool(
            name="checkpoint_search",
            description="Semantic search using vector similarity (all-MiniLM-L6-v2). Use for fuzzy/conceptual queries. For precision filtering by domain/keyword/pattern, use hybrid_search_checkpoints instead. Default threshold: 0.5 (higher threshold for pure semantic search ensures quality). Use 0.25-0.3 with hybrid_search when keyword filters provide additional relevance signals.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query describing what to find"
                    },
                    "limit": {
                        "type": "number",
                        "description": "Maximum results to return (default: 5)"
                    },
                    "section": {
                        "type": "string",
                        "enum": ["combined", "session_arc", "mental_model", "decisions_made", "hypotheses"],
                        "description": "Filter by checkpoint section (optional)"
                    },
                    "threshold": {
                        "type": "number",
                        "description": "Minimum similarity score 0-1 (default: 0.5)"
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="memory_context",
            description="Get relevant memories for current session topic (automatic context retrieval at session start). Uses semantic search with 0.30 threshold for higher precision. Future: will support domain filtering.",
            inputSchema={
                "type": "object",
                "properties": {
                    "topic": {
                        "type": "string",
                        "description": "Current session topic or focus area"
                    },
                    "limit": {
                        "type": "number",
                        "description": "Number of memories to retrieve (default: 3)"
                    }
                },
                "required": ["topic"]
            }
        ),
        Tool(
            name="hybrid_search_checkpoints",
            description="Hybrid 'doubled up' search combining semantic similarity with keyword filtering. Use when you need precision: find sessions by domain (trading/infrastructure/memory), keywords (qdrant/kraken/cloudflare), patterns used (context_alignment), or decision types (architectural/technical). Filters use AND logic across types, OR within arrays. See skill: memory_search for usage patterns.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Semantic search query text"
                    },
                    "limit": {
                        "type": "number",
                        "description": "Maximum results to return (default: 5)"
                    },
                    "domains": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Filter by domain tags (e.g., ['trading', 'infrastructure'])"
                    },
                    "keywords": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Filter by keywords"
                    },
                    "patterns": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Filter by dyadic patterns used"
                    },
                    "threshold": {
                        "type": "number",
                        "description": "Minimum similarity score 0-1 (default: 0.25)"
                    },
                    "date_from": {
                        "type": "string",
                        "description": "Start date for range filter (ISO format: 2025-12-17)"
                    },
                    "date_to": {
                        "type": "string",
                        "description": "End date for range filter (ISO format: 2026-01-10)"
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="get_session_context",
            description="Get automatically loaded session context from startup hook (shows relevant memories)",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="memory_health_check",
            description="Check memory search system health and force initialization if needed",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="route_to_skill",
            description="Route query to appropriate skill using semantic similarity (sub-10ms). Returns matched skill with confidence score, tools, and alternatives. Use for skill selection/activation. Default threshold: 0.25 (tuned for multi-component embeddings). Falls back to 'general-purpose' if no match.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Query describing desired action or capability"
                    },
                    "threshold": {
                        "type": "number",
                        "description": "Minimum similarity score 0-1 (default: 0.45)"
                    },
                    "limit": {
                        "type": "number",
                        "description": "Number of candidate skills to return (default: 3)"
                    },
                    "current_domain": {
                        "type": "string",
                        "description": "Current active domain for context boosting (optional)"
                    }
                },
                "required": ["query"]
            }
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Handle tool calls"""

    try:
        # Query Tools
        if name == "get_dyad_state":
            state = dyad_state.get_full_state()
            return [TextContent(type="text", text=json.dumps(state, indent=2, default=str))]

        elif name == "get_captain_state":
            captain = dyad_state.get_captain_state()
            return [TextContent(type="text", text=json.dumps(captain, indent=2, default=str))]

        elif name == "get_shared_focus":
            focus = dyad_state.get_shared_focus()
            return [TextContent(type="text", text=json.dumps(focus, indent=2, default=str))]

        elif name == "get_dyad_summary":
            summary = dyad_state.get_dyad_summary()
            return [TextContent(type="text", text=summary)]

        # Update Tools
        elif name == "set_captain_state":
            result = dyad_state.update_captain_state(
                availability=arguments.get("availability"),
                focus=arguments.get("focus"),
                energy=arguments.get("energy"),
                physical_context=arguments.get("physical_context")
            )
            return [TextContent(
                type="text",
                text=f"Captain state updated:\n{json.dumps(result, indent=2, default=str)}"
            )]

        elif name == "propose_focus_shift":
            # This is a proposal, not a direct update
            proposal = (
                f"## Focus Shift Proposal\n\n"
                f"**Proposed Domain**: {arguments['new_domain']}\n"
                f"**Rationale**: {arguments['rationale']}\n\n"
                f"Captain: Do you approve this focus shift?"
            )
            return [TextContent(type="text", text=proposal)]

        elif name == "signal_completion":
            # Increment completion metric and report
            dyad_state.increment_metric("successful_completions")

            report = (
                f"## Objective Completed\n\n"
                f"**Objective**: {arguments['objective']}\n"
                f"**Outcome**: {arguments['outcome']}\n\n"
                f"Completion recorded in dyad metrics."
            )
            return [TextContent(type="text", text=report)]

        elif name == "update_shared_focus":
            result = dyad_state.update_shared_focus(
                domain=arguments.get("domain"),
                objective=arguments.get("objective"),
                blockers=arguments.get("blockers"),
                next_action=arguments.get("next_action")
            )
            return [TextContent(
                type="text",
                text=f"Shared focus updated:\n{json.dumps(result, indent=2, default=str)}"
            )]

        elif name == "update_active_domain":
            result = dyad_state.update_active_domain(
                domain=arguments["domain"],
                status=arguments["status"],
                details=arguments.get("details")
            )
            return [TextContent(
                type="text",
                text=f"Domain '{arguments['domain']}' updated:\n{json.dumps(result, indent=2, default=str)}"
            )]

        elif name == "append_dyad_note":
            dyad_state.append_note(
                category=arguments["category"],
                note=arguments["note"]
            )
            return [TextContent(
                type="text",
                text=f"Note added to {arguments['category']}"
            )]

        elif name == "signal_blocker":
            # Add blocker to shared focus
            focus = dyad_state.get_shared_focus()
            current_blockers = focus.get('blockers', [])

            severity = arguments.get('severity', 'moderate')
            blocker_text = f"[{severity.upper()}] {arguments['description']}"

            if blocker_text not in current_blockers:
                current_blockers.append(blocker_text)
                dyad_state.update_shared_focus(blockers=current_blockers)

            return [TextContent(
                type="text",
                text=f"Blocker recorded: {blocker_text}"
            )]

        # Checkpoint Tools
        elif name == "list_checkpoints":
            limit = arguments.get("limit", 10)
            checkpoints = checkpoint_manager.list_checkpoints(limit=limit)
            return [TextContent(
                type="text",
                text=json.dumps(checkpoints, indent=2, default=str)
            )]

        elif name == "load_checkpoint":
            filename = arguments.get("filename")
            checkpoint = checkpoint_manager.load_checkpoint(filename)
            return [TextContent(
                type="text",
                text=json.dumps(checkpoint, indent=2, default=str)
            )]

        elif name == "get_resume_context":
            filename = arguments.get("filename")
            context = checkpoint_manager.get_resume_context(filename)
            return [TextContent(
                type="text",
                text=context
            )]

        elif name == "write_checkpoint":
            result = checkpoint_manager.write_checkpoint(
                checkpoint_data=arguments["checkpoint_data"],
                description=arguments.get("description"),
                validate=arguments.get("validate", True)
            )

            # Handle tuple return (filename, validation_report)
            if isinstance(result, tuple):
                filename, validation_report = result
                message = f"Checkpoint written: {filename}"
                if validation_report:
                    quality = validation_report['quality_score']
                    level = validation_report['quality_level']
                    message += f"\nQuality: {quality:.3f} ({level})"
                    if quality < 0.5:
                        message += f"\n⚠️  WARNING: Quality below threshold - see logs for details"
                return [TextContent(type="text", text=message)]
            else:
                # Legacy return (backward compatibility)
                return [TextContent(type="text", text=f"Checkpoint written: {result}")]

        # Memory Search Tools (with lazy initialization)
        elif name == "checkpoint_search":
            memory_search, error = _get_memory_search()
            if memory_search is None:
                return [TextContent(type="text", text=error)]

            result = memory_search.search_checkpoints(
                query=arguments["query"],
                limit=arguments.get("limit", 5),
                section=arguments.get("section"),
                threshold=arguments.get("threshold", 0.5)
            )
            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2, default=str)
            )]

        elif name == "memory_context":
            memory_search, error = _get_memory_search()
            if memory_search is None:
                return [TextContent(type="text", text=error)]

            result = memory_search.get_memory_context(
                current_session_topic=arguments["topic"],
                limit=arguments.get("limit", 3)
            )
            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2, default=str)
            )]

        elif name == "hybrid_search_checkpoints":
            memory_search, error = _get_memory_search()
            if memory_search is None:
                return [TextContent(type="text", text=error)]

            # Validate date parameters before passing to search layer
            date_from = arguments.get("date_from")
            date_to = arguments.get("date_to")

            if date_from:
                try:
                    # Validate ISO format
                    from datetime import datetime
                    datetime.fromisoformat(date_from)
                except ValueError:
                    return [TextContent(
                        type="text",
                        text=f"Error: date_from must be in ISO format (YYYY-MM-DD), got: {date_from}"
                    )]

            if date_to:
                try:
                    datetime.fromisoformat(date_to)
                except ValueError:
                    return [TextContent(
                        type="text",
                        text=f"Error: date_to must be in ISO format (YYYY-MM-DD), got: {date_to}"
                    )]

            # Date range logic validation
            if date_from and date_to and date_from > date_to:
                return [TextContent(
                    type="text",
                    text=f"Error: date_from ({date_from}) is after date_to ({date_to})"
                )]

            result = memory_search.hybrid_search_checkpoints(
                query=arguments["query"],
                limit=arguments.get("limit", 5),
                domains=arguments.get("domains"),
                keywords=arguments.get("keywords"),
                patterns=arguments.get("patterns"),
                threshold=arguments.get("threshold", 0.25),
                date_from=date_from,
                date_to=date_to
            )
            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2, default=str)
            )]

        elif name == "get_session_context":
            # Read session context file written by session_start hook
            from pathlib import Path
            import os

            rhiz_root = Path(os.environ.get("RHIZ_ROOT", Path(__file__).parent.parent.parent.parent))
            context_file = rhiz_root / "core" / "memory" / ".session_context.json"

            if not context_file.exists():
                return [TextContent(
                    type="text",
                    text="No session context available. This is normal for first-time sessions."
                )]

            try:
                context = json.loads(context_file.read_text())

                # Format for display
                output = ["## Session Context (Auto-Loaded)\n"]
                output.append(f"**Search Topic**: {context.get('search_topic', 'N/A')}\n")
                output.append(f"**Relevant Memories Found**: {context.get('memories_found', 0)}\n\n")

                if context.get("relevant_sessions"):
                    output.append("### Relevant Past Sessions\n")
                    for mem in context["relevant_sessions"]:
                        output.append(f"**Session**: {mem.get('session', 'unknown')} (similarity: {mem.get('similarity', 0.0)})\n")
                        output.append(f"**Source**: {mem.get('source', 'unknown')}\n")
                        output.append(f"**Preview**: {mem.get('preview', 'N/A')}\n\n")
                        output.append("---\n\n")

                return [TextContent(type="text", text="".join(output))]

            except Exception as e:
                return [TextContent(
                    type="text",
                    text=f"Error reading session context: {str(e)}"
                )]

        elif name == "memory_health_check":
            memory_search, error = _get_memory_search()

            if memory_search is None:
                return [TextContent(
                    type="text",
                    text=f"❌ Memory search is NOT available\n\n{error}"
                )]

            # Verify we can actually query Qdrant
            try:
                test_result = memory_search.search_checkpoints(
                    query="test",
                    limit=1,
                    threshold=0.0
                )

                status_report = (
                    "✅ Memory search system is HEALTHY\n\n"
                    f"- Qdrant connection: active\n"
                    f"- Collection: rhiz_memories\n"
                    f"- Test query: successful\n"
                    f"- Retry count: {_memory_search_retry_count}\n"
                    f"- Total points available: {test_result.get('count', 'unknown')}"
                )

                return [TextContent(type="text", text=status_report)]
            except Exception as e:
                return [TextContent(
                    type="text",
                    text=f"⚠️ Memory search initialized but query failed:\n{str(e)}"
                )]

        elif name == "route_to_skill":
            # Get skill router singleton
            router, error = _get_skill_router()

            if router is None:
                return [TextContent(type="text", text=error)]

            try:
                # Route the query
                result = router.route_query(
                    query=arguments["query"],
                    threshold=arguments.get("threshold", 0.25),
                    limit=arguments.get("limit", 3)
                )

                # Apply context boosting if domain provided (reuses base result to avoid double-routing)
                if arguments.get("current_domain") and result["matched"]:
                    result = router.route_with_context(
                        query=arguments["query"],
                        current_domain=arguments["current_domain"],
                        threshold=arguments.get("threshold", 0.25)
                    )

                return [TextContent(
                    type="text",
                    text=json.dumps(result, indent=2)
                )]

            except ValueError as e:
                # Input validation error
                return [TextContent(
                    type="text",
                    text=f"Invalid input: {str(e)}"
                )]
            except Exception as e:
                return [TextContent(
                    type="text",
                    text=f"Error in skill routing: {str(e)}\n\nVerify:\n- rhiz_skills collection exists in Qdrant\n- Skills have been ingested (run core/skills/scripts/ingest_skills.py)"
                )]

        else:
            return [TextContent(
                type="text",
                text=f"Unknown tool: {name}"
            )]

    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Error executing {name}: {str(e)}"
        )]


# ========================================
# RESOURCES API
# ========================================

@app.list_resources()
async def list_resources() -> list[Resource]:
    """Expose dyad state, checkpoints, and memory stats as resources"""
    return [
        Resource(
            uri="dyad://state",
            name="Current Dyad State",
            description="Captain state, First Mate state, shared focus, and metrics",
            mimeType="application/json"
        ),
        Resource(
            uri="checkpoint://latest",
            name="Latest Session Checkpoint",
            description="Most recent session checkpoint (YAML)",
            mimeType="application/x-yaml"
        ),
        Resource(
            uri="checkpoint://list",
            name="Available Checkpoints",
            description="List all session checkpoints with metadata",
            mimeType="application/json"
        ),
        Resource(
            uri="memory://stats",
            name="Memory System Statistics",
            description="Qdrant collection stats, point counts, and health status",
            mimeType="application/json"
        )
    ]


@app.read_resource()
async def read_resource(uri: AnyUrl) -> str:
    """Serve resource content based on URI scheme"""
    import os
    from pathlib import Path

    uri_str = str(uri)

    try:
        if uri_str == "dyad://state":
            # Return complete dyad state as JSON
            state = dyad_state.get_full_state()
            return json.dumps(state, indent=2)

        elif uri_str == "checkpoint://latest":
            # Return most recent checkpoint YAML
            from pathlib import Path
            import os

            rhiz_root = Path(os.environ.get("RHIZ_ROOT", Path(__file__).parent.parent.parent.parent))
            checkpoints_dir = rhiz_root / "core" / "memory" / "checkpoints"

            if not checkpoints_dir.exists():
                return "Error: Checkpoints directory not found"

            checkpoints = sorted(checkpoints_dir.glob("*.yaml"))
            if checkpoints:
                return checkpoints[-1].read_text()
            return "No checkpoints found"

        elif uri_str == "checkpoint://list":
            # Return list of all checkpoints with metadata
            from pathlib import Path
            import os

            rhiz_root = Path(os.environ.get("RHIZ_ROOT", Path(__file__).parent.parent.parent.parent))
            checkpoints_dir = rhiz_root / "core" / "memory" / "checkpoints"

            if not checkpoints_dir.exists():
                return json.dumps({"error": "Checkpoints directory not found"}, indent=2)

            checkpoints = []
            for cp in sorted(checkpoints_dir.glob("*.yaml")):
                checkpoints.append({
                    "filename": cp.name,
                    "modified": cp.stat().st_mtime,
                    "size": cp.stat().st_size
                })

            return json.dumps({
                "total": len(checkpoints),
                "checkpoints": checkpoints
            }, indent=2)

        elif uri_str == "memory://stats":
            # Return memory system statistics
            memory_search, error = _get_memory_search()

            if memory_search is None:
                stats = {
                    "status": "unavailable",
                    "error": error or "Memory search not initialized"
                }
            else:
                try:
                    # Query Qdrant for collection info
                    from qdrant_client import QdrantClient

                    client = QdrantClient(host="localhost", port=6333)
                    collection_info = client.get_collection("rhiz_memories")

                    stats = {
                        "status": "healthy",
                        "collection": "rhiz_memories",
                        "points_count": collection_info.points_count,
                        "vectors_count": collection_info.vectors_count if hasattr(collection_info, 'vectors_count') else None,
                        "indexed_vectors_count": collection_info.indexed_vectors_count if hasattr(collection_info, 'indexed_vectors_count') else None
                    }
                except Exception as e:
                    stats = {
                        "status": "error",
                        "error": str(e)
                    }

            return json.dumps(stats, indent=2)

        else:
            return json.dumps({
                "error": f"Unknown resource URI: {uri_str}",
                "available_uris": [
                    "dyad://state",
                    "checkpoint://latest",
                    "checkpoint://list",
                    "memory://stats"
                ]
            }, indent=2)

    except Exception as e:
        return json.dumps({
            "error": f"Error reading resource {uri_str}: {str(e)}"
        }, indent=2)


async def main():
    """Main server entry point"""
    import sys
    try:
        async with stdio_server() as (read_stream, write_stream):
            await app.run(
                read_stream,
                write_stream,
                app.create_initialization_options()
            )
    except Exception as e:
        print(f"[rhiz-mcp] Fatal error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        raise


if __name__ == "__main__":
    asyncio.run(main())
