"""
Memory Search Integration for Rhiz MCP Server

Wraps the core memory search functionality for MCP tool exposure.
"""

import sys
from pathlib import Path
from typing import List, Dict, Optional

# Add core memory scripts to path
RHIZ_ROOT = Path(__file__).parent.parent.parent.parent
MEMORY_SCRIPTS = RHIZ_ROOT / "core" / "memory" / "scripts"
sys.path.insert(0, str(MEMORY_SCRIPTS))

try:
    from search import MemorySearcher
except ImportError as e:
    # Graceful fallback if memory system not available
    MemorySearcher = None
    _import_error = str(e)


class MemorySearchInterface:
    """MCP-compatible interface for memory search operations"""

    def __init__(self):
        if MemorySearcher is None:
            raise RuntimeError(f"Memory search system not available: {_import_error}")

        # Initialize with default Qdrant connection (localhost)
        self.searcher = MemorySearcher(
            qdrant_host="localhost",
            qdrant_port=6333,
            collection_name="rhiz_memories"
        )

    def search_checkpoints(
        self,
        query: str,
        limit: int = 5,
        section: Optional[str] = None,
        threshold: float = 0.5
    ) -> Dict:
        """
        Search checkpoints for relevant memories.

        Args:
            query: Search query text
            limit: Max results (default 5)
            section: Filter by section type (optional)
            threshold: Minimum similarity score 0-1 (default 0.5)

        Returns:
            Dict with results array and metadata
        """
        try:
            memories = self.searcher.search(
                query=query,
                limit=limit,
                section_filter=section,
                score_threshold=threshold
            )

            return {
                "success": True,
                "query": query,
                "count": len(memories),
                "results": memories
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "query": query
            }

    def get_memory_context(
        self,
        current_session_topic: str,
        limit: int = 3
    ) -> Dict:
        """
        Get relevant memory context for current session.

        Designed for automatic retrieval at session start.
        Returns compressed, high-relevance memories.

        Args:
            current_session_topic: Topic/focus of current session
            limit: Number of memories to retrieve (default 3)

        Returns:
            Dict with context summary and relevant memories
        """
        try:
            # Search for combined sections (full checkpoint context)
            memories = self.searcher.search(
                query=current_session_topic,
                limit=limit,
                section_filter="combined",
                score_threshold=0.30  # Tuned for all-MiniLM-L6-v2 similarity scores
            )

            # Format for session handshake
            context = {
                "success": True,
                "topic": current_session_topic,
                "memories_found": len(memories),
                "relevant_sessions": []
            }

            for mem in memories:
                context["relevant_sessions"].append({
                    "similarity": round(mem["score"], 3),
                    "session": mem["metadata"]["session_date"],
                    "source": mem["metadata"]["source_file"],
                    "preview": mem["content"][:200] + "..." if len(mem["content"]) > 200 else mem["content"]
                })

            return context
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "topic": current_session_topic
            }

    def hybrid_search_checkpoints(
        self,
        query: str,
        limit: int = 5,
        domains: Optional[List[str]] = None,
        keywords: Optional[List[str]] = None,
        patterns: Optional[List[str]] = None,
        threshold: float = 0.25,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None
    ) -> Dict:
        """
        Hybrid semantic + keyword search with frontmatter filtering.

        Combines vector similarity with structured metadata for precision.

        Args:
            query: Semantic search query
            limit: Max results (default 5)
            domains: Filter by domain tags (e.g., ["trading"])
            keywords: Filter by keywords
            patterns: Filter by dyadic patterns used
            threshold: Minimum similarity score (default 0.25)

        Returns:
            Dict with results array and metadata
        """
        try:
            # Construct date_range tuple if both dates provided
            date_range = None
            if date_from and date_to:
                date_range = (date_from, date_to)

            memories = self.searcher.hybrid_search(
                query=query,
                limit=limit,
                score_threshold=threshold,
                domains=domains,
                keywords=keywords,
                patterns=patterns,
                date_range=date_range
            )

            return {
                "success": True,
                "query": query,
                "filters": {
                    "domains": domains or [],
                    "keywords": keywords or [],
                    "patterns": patterns or []
                },
                "count": len(memories),
                "results": memories
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "query": query
            }
