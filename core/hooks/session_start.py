#!/usr/bin/env python3
"""
Session Start Hook

Executes when a Claude Code session starts.
Updates dyad state with session initialization.
Loads relevant memory context for session continuity.
"""

import sys
import os
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

# Add tools directory to path to import DyadState and memory search
RHIZ_ROOT = Path(os.environ.get("RHIZ_ROOT", Path(__file__).parent.parent.parent))
sys.path.insert(0, str(RHIZ_ROOT / "tools" / "rhiz-mcp" / "src"))
sys.path.insert(0, str(RHIZ_ROOT / "core" / "memory" / "scripts"))
sys.path.insert(0, str(RHIZ_ROOT))  # For core.skills imports

from dyad_state import DyadState
from checkpoint_manager import CheckpointManager
from search import MemorySearcher


def initialize_memory_search() -> Optional['MemorySearcher']:
    """
    Initialize memory search with retry logic and connectivity check.
    Returns MemorySearcher instance if successful, None if failed.
    """
    max_retries = 3
    retry_delay = 1.0

    for attempt in range(max_retries):
        try:
            # Test Qdrant connectivity first
            from qdrant_client import QdrantClient

            test_client = QdrantClient(host="localhost", port=6333)
            collections = test_client.get_collections()  # Raises if unreachable

            # Verify rhiz_memories collection exists
            collection_names = [c.name for c in collections.collections]
            if "rhiz_memories" not in collection_names:
                print(f"[session_start] Warning: Collection 'rhiz_memories' not found", file=sys.stderr)
                return None

            # Initialize searcher
            searcher = MemorySearcher(
                qdrant_host="localhost",
                qdrant_port=6333,
                collection_name="rhiz_memories"
            )

            print(f"[session_start] [OK] Memory search initialized (attempt {attempt + 1})")
            return searcher

        except Exception as e:
            if attempt < max_retries - 1:
                print(f"[session_start] Memory search initialization failed (attempt {attempt + 1}), retrying in {retry_delay}s...", file=sys.stderr)
                time.sleep(retry_delay)
                retry_delay *= 2
            else:
                print(f"[session_start] [FAIL] Memory search unavailable after {max_retries} attempts: {e}", file=sys.stderr)
                return None

    return None


def load_memory_context():
    """
    Load relevant memory context from past sessions.
    Writes context to temp file for First Mate to display.
    Non-fatal: Returns partial context if memory search unavailable.
    """
    try:
        # Get most recent checkpoint
        checkpoints_dir = RHIZ_ROOT / "core" / "memory" / "checkpoints"
        checkpoint_files = sorted(checkpoints_dir.glob("session_*.yaml"), reverse=True)

        if not checkpoint_files:
            return None

        # Load most recent checkpoint to extract session topic
        checkpoint_mgr = CheckpointManager()
        latest_checkpoint = checkpoint_mgr.load_checkpoint(checkpoint_files[0].name)

        # Extract topic from resume context or session arc
        topic = ""
        if 'resume_context' in latest_checkpoint:
            resume = latest_checkpoint['resume_context']
            topic = resume.get('suggested_resume_prompt', '')[:200]
        elif 'session_arc' in latest_checkpoint:
            topic = latest_checkpoint['session_arc'][:200]

        if not topic:
            # Fallback: use generic "recent work" query
            topic = "recent session work, active domains, pending tasks"

        # Initialize memory search with retry logic
        searcher = initialize_memory_search()

        # Build context object (works with or without memory search)
        context = {
            "search_topic": topic,
            "memory_available": searcher is not None,
            "memories_found": 0,
            "relevant_sessions": []
        }

        if searcher:
            try:
                # Search for relevant memories
                memories = searcher.search(
                    query=topic,
                    limit=3,
                    section_filter="combined",
                    score_threshold=0.28  # Lowered from 0.3 to catch borderline matches
                )

                context["memories_found"] = len(memories)

                for mem in memories:
                    context["relevant_sessions"].append({
                        "similarity": round(mem["score"], 3),
                        "session": mem["metadata"].get("session_date", "unknown"),
                        "source": mem["metadata"].get("source_file", "unknown"),
                        "preview": mem["content"][:300] + "..." if len(mem["content"]) > 300 else mem["content"]
                    })

            except Exception as e:
                print(f"[session_start] Warning: Memory search failed: {e}", file=sys.stderr)
                context["error"] = str(e)
        else:
            context["error"] = "Memory search unavailable (Qdrant not reachable)"

        # Write context file for MCP server (always write, even if memory unavailable)
        context_file = RHIZ_ROOT / "core" / "memory" / ".session_context.json"
        context_file.write_text(json.dumps(context, indent=2))

        return context

    except Exception as e:
        print(f"[session_start] Error loading memory context: {e}", file=sys.stderr)

        # Write error context file
        error_context = {
            "search_topic": "unknown",
            "memory_available": False,
            "memories_found": 0,
            "relevant_sessions": [],
            "error": str(e)
        }

        try:
            context_file = RHIZ_ROOT / "core" / "memory" / ".session_context.json"
            context_file.write_text(json.dumps(error_context, indent=2))
        except Exception as e:
            print(f"[session_start] Failed to write error context file: {e}", file=sys.stderr)

        return None


def load_skill_context_memory():
    """
    Load skill-specific context memories using Self-RAG.

    Determines likely skill domains from recent checkpoint,
    loads relevant skill memories for session initialization.

    Returns dict with skill context if successful, None if unavailable.
    """
    try:
        # Import Self-RAG (inside function to avoid import errors if not available)
        try:
            from core.skills.self_rag import SelfRAGExecutor
        except ImportError as e:
            print(f"[session_start] Skill context unavailable: {e}", file=sys.stderr)
            return None

        # Get most recent checkpoint to infer likely domains
        checkpoints_dir = RHIZ_ROOT / "core" / "memory" / "checkpoints"
        checkpoint_files = sorted(checkpoints_dir.glob("session_*.yaml"), reverse=True)

        if not checkpoint_files:
            return None

        # Load latest checkpoint
        checkpoint_mgr = CheckpointManager()
        latest_checkpoint = checkpoint_mgr.load_checkpoint(checkpoint_files[0].name)

        # Extract likely domains from frontmatter or session arc
        domains = []
        if 'frontmatter' in latest_checkpoint and 'domains' in latest_checkpoint['frontmatter']:
            domains = latest_checkpoint['frontmatter']['domains']

        # Fallback: infer from session topic
        session_topic = latest_checkpoint.get('session_arc', '')

        # Map domains to skills (simple heuristic)
        skill_candidates = []
        if 'trading' in domains or 'trading' in session_topic.lower():
            skill_candidates.append("trading/kraken_analysis")
        if 'infrastructure' in domains or 'infrastructure' in session_topic.lower():
            skill_candidates.append("infrastructure/deployment")
        if 'memory' in domains or 'memory' in session_topic.lower():
            skill_candidates.append("memory/session_management")
        if 'research' in domains or 'documentation' in session_topic.lower():
            skill_candidates.append("research/documentation")

        # Default: load trading context (most common domain)
        if not skill_candidates:
            skill_candidates.append("trading/kraken_analysis")

        # Initialize Self-RAG executor
        executor = SelfRAGExecutor()

        # Load skill context for each candidate
        skill_context = {
            "skills_loaded": [],
            "total_memories": 0
        }

        for skill in skill_candidates:
            try:
                result = executor.execute_with_memory(
                    query=session_topic if session_topic else "recent work",
                    skill=skill,
                    limit=2  # Load 2 most relevant memories per skill
                )

                if result["retrieved"] and result["context"]["memories_retrieved"] > 0:
                    skill_context["skills_loaded"].append({
                        "skill": skill,
                        "memories_count": result["context"]["memories_retrieved"],
                        "memories": result["context"]["memories"]
                    })
                    skill_context["total_memories"] += result["context"]["memories_retrieved"]

            except Exception as e:
                print(f"[session_start] Warning: Failed to load context for {skill}: {e}", file=sys.stderr)

        if skill_context["total_memories"] > 0:
            return skill_context

        return None

    except Exception as e:
        print(f"[session_start] Error loading skill context: {e}", file=sys.stderr)
        return None


def update_dyad_state():
    """Update dyad state on session start"""
    try:
        dyad = DyadState()

        # Generate session ID
        session_id = f"session_{int(datetime.now().timestamp() * 1000)}"
        timestamp = datetime.now().isoformat()

        # Increment session count
        state = dyad.load_state(force_reload=True)
        dyad_state_section = state.get('dyad_state', {})
        session_count = dyad_state_section.get('session_count', 0) + 1

        # Update dyad state section (session count and last_sync)
        dyad_state_section['session_count'] = session_count
        dyad_state_section['last_sync'] = timestamp
        dyad._write_section_update('DYAD_STATE', dyad_state_section)

        # Update First Mate state
        dyad.update_first_mate_state(
            session_id=session_id
        )

        print(f"[session_start] Dyad state updated")
        print(f"  Session ID: {session_id}")
        print(f"  Session Count: {session_count}")
        print(f"  Timestamp: {timestamp}")

        # Load memory context
        mem_context = load_memory_context()
        if mem_context and mem_context["memories_found"] > 0:
            print(f"  Memory Context: {mem_context['memories_found']} relevant sessions loaded")

        # Load skill context memory
        skill_context = load_skill_context_memory()
        if skill_context and skill_context["total_memories"] > 0:
            print(f"  Skill Context: {skill_context['total_memories']} skill memories loaded")
            for skill_data in skill_context["skills_loaded"]:
                print(f"    - {skill_data['skill']}: {skill_data['memories_count']} memories")

        return True

    except Exception as e:
        print(f"[session_start] Error updating dyad state: {e}", file=sys.stderr)
        return False


if __name__ == "__main__":
    success = update_dyad_state()
    sys.exit(0 if success else 1)
