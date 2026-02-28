"""
Semantic Search for Rhiz Memory System
Query the vector database to retrieve relevant memories.
"""

from typing import List, Dict, Optional
from datetime import datetime
from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue, MatchAny, Range

from embeddings import EmbeddingGenerator


def _validate_date_format(date_str: str) -> tuple[bool, str]:
    """
    Validate ISO date format (YYYY-MM-DD).

    Returns:
        (is_valid, normalized_date_or_error_msg)
    """
    try:
        # Parse and normalize to ISO format
        dt = datetime.fromisoformat(date_str)
        return (True, dt.date().isoformat())
    except (ValueError, TypeError):
        return (False, f"Invalid date format: {date_str}. Expected YYYY-MM-DD")


class MemorySearcher:
    """
    Semantic search interface for Rhiz memory system.
    Retrieves relevant memories based on query context.
    """

    def __init__(
        self,
        qdrant_host: str = "localhost",
        qdrant_port: int = 6333,
        collection_name: str = "rhiz_memories"
    ):
        """
        Initialize the memory searcher.

        Args:
            qdrant_host: Qdrant server host
            qdrant_port: Qdrant server port
            collection_name: Name of the Qdrant collection
        """
        self.client = QdrantClient(host=qdrant_host, port=qdrant_port)
        self.collection_name = collection_name
        self.embedder = EmbeddingGenerator()

    def search(
        self,
        query: str,
        limit: int = 5,
        section_filter: Optional[str] = None,
        score_threshold: float = 0.25
    ) -> List[Dict]:
        """
        Search for memories relevant to the query.

        Args:
            query: Search query text
            limit: Maximum number of results to return
            section_filter: Filter by section type (e.g., "combined", "session_arc", "mental_model")
            score_threshold: Minimum similarity score (0-1)

        Returns:
            List of matching memory dictionaries with metadata and scores
        """
        # Generate query embedding
        query_vector = self.embedder.embed(query).tolist()

        # Build filter if section specified
        search_filter = None
        if section_filter:
            search_filter = Filter(
                must=[
                    FieldCondition(
                        key="section",
                        match=MatchValue(value=section_filter)
                    )
                ]
            )

        # Search Qdrant
        results = self.client.query_points(
            collection_name=self.collection_name,
            query=query_vector,
            limit=limit,
            query_filter=search_filter,
            score_threshold=score_threshold
        ).points

        # Format results
        memories = []
        for result in results:
            memory = {
                "score": result.score,
                "content": result.payload.get("content", ""),
                "metadata": {
                    "source_file": result.payload.get("source_file", "unknown"),
                    "session_date": result.payload.get("session_date", "unknown"),
                    "section": result.payload.get("section", "unknown"),
                    "checkpoint_id": result.payload.get("checkpoint_id", "unknown"),
                    "phase": result.payload.get("phase", "unknown")
                },
                "point_id": result.id
            }
            memories.append(memory)

        return memories

    def hybrid_search(
        self,
        query: str,
        limit: int = 5,
        score_threshold: float = 0.25,
        # Frontmatter filters
        domains: Optional[List[str]] = None,
        keywords: Optional[List[str]] = None,
        patterns: Optional[List[str]] = None,
        decision_types: Optional[List[str]] = None,
        session_type: Optional[str] = None,
        section_filter: Optional[str] = None,
        is_notable: Optional[bool] = None,
        date_range: Optional[tuple] = None  # NEW: (start_date, end_date)
    ) -> List[Dict]:
        """
        Hybrid semantic + keyword search with frontmatter filtering.

        Combines vector similarity with structured metadata filtering
        for "doubled up searching" - precision through both approaches.

        Args:
            query: Semantic search query text
            limit: Maximum number of results
            score_threshold: Minimum similarity score (0-1)
            domains: Filter by domain tags (e.g., ["trading", "infrastructure"])
            keywords: Filter by keywords (matches any)
            patterns: Filter by dyadic patterns used
            decision_types: Filter by decision types made
            session_type: Filter by session type (primary)
            section_filter: Filter by section type (combined, session_arc, etc.)
            is_notable: Filter by notable flag

        Returns:
            List of matching memories with metadata and scores
        """
        # Generate query embedding
        query_vector = self.embedder.embed(query).tolist()

        # Build filter conditions
        filter_conditions = []

        if section_filter:
            filter_conditions.append(
                FieldCondition(key="section", match=MatchValue(value=section_filter))
            )

        if domains:
            filter_conditions.append(
                FieldCondition(key="domains", match=MatchAny(any=domains))
            )

        if keywords:
            filter_conditions.append(
                FieldCondition(key="keywords", match=MatchAny(any=keywords))
            )

        if patterns:
            filter_conditions.append(
                FieldCondition(key="patterns_used", match=MatchAny(any=patterns))
            )

        if decision_types:
            filter_conditions.append(
                FieldCondition(key="decision_types", match=MatchAny(any=decision_types))
            )

        if session_type:
            filter_conditions.append(
                FieldCondition(key="session_type_primary", match=MatchValue(value=session_type))
            )

        if is_notable is not None:
            filter_conditions.append(
                FieldCondition(key="is_notable", match=MatchValue(value=is_notable))
            )

        if date_range:
            start_date, end_date = date_range

            # Validate start date
            valid_start, normalized_start = _validate_date_format(start_date)
            if not valid_start:
                raise ValueError(normalized_start)

            # Validate end date
            valid_end, normalized_end = _validate_date_format(end_date)
            if not valid_end:
                raise ValueError(normalized_end)

            # Ensure logical ordering
            if normalized_start > normalized_end:
                raise ValueError(
                    f"Invalid date range: start_date ({normalized_start}) is after end_date ({normalized_end})"
                )

            filter_conditions.append(
                FieldCondition(
                    key="session_date",
                    range=Range(
                        gte=normalized_start,
                        lte=normalized_end
                    )
                )
            )

        # Combine filters with AND logic
        search_filter = None
        if filter_conditions:
            search_filter = Filter(must=filter_conditions)

        # Execute hybrid search
        results = self.client.query_points(
            collection_name=self.collection_name,
            query=query_vector,
            limit=limit,
            query_filter=search_filter,
            score_threshold=score_threshold
        ).points

        # Format results
        memories = []
        for result in results:
            memory = {
                "score": result.score,
                "content": result.payload.get("content", ""),
                "metadata": {
                    "source_file": result.payload.get("source_file", "unknown"),
                    "session_date": result.payload.get("session_date", "unknown"),
                    "section": result.payload.get("section", "unknown"),
                    "checkpoint_id": result.payload.get("checkpoint_id", "unknown"),
                    "phase": result.payload.get("phase", "unknown"),
                    # Frontmatter metadata
                    "domains": result.payload.get("domains", []),
                    "keywords": result.payload.get("keywords", []),
                    "patterns_used": result.payload.get("patterns_used", []),
                    "decision_types": result.payload.get("decision_types", []),
                    "is_notable": result.payload.get("is_notable", False)
                },
                "point_id": result.id
            }
            memories.append(memory)

        return memories

    def search_by_date(
        self,
        query: str,
        session_date: str,
        limit: int = 5
    ) -> List[Dict]:
        """
        Search for memories from a specific session date.

        Args:
            query: Search query text
            session_date: Session date to filter by
            limit: Maximum number of results

        Returns:
            List of matching memories from that date
        """
        query_vector = self.embedder.embed(query).tolist()

        search_filter = Filter(
            must=[
                FieldCondition(
                    key="session_date",
                    match=MatchValue(value=session_date)
                )
            ]
        )

        results = self.client.query_points(
            collection_name=self.collection_name,
            query=query_vector,
            limit=limit,
            query_filter=search_filter
        ).points

        memories = []
        for result in results:
            memories.append({
                "score": result.score,
                "content": result.payload.get("content", ""),
                "metadata": result.payload,
                "point_id": result.id
            })

        return memories

    def get_recent_sessions(self, limit: int = 3) -> List[Dict]:
        """
        Retrieve information about recent sessions.

        Args:
            limit: Number of recent sessions to retrieve

        Returns:
            List of recent session metadata
        """
        # Scroll through collection to get recent session arcs
        results, _ = self.client.scroll(
            collection_name=self.collection_name,
            scroll_filter=Filter(
                must=[
                    FieldCondition(
                        key="section",
                        match=MatchValue(value="combined")
                    )
                ]
            ),
            limit=limit,
            with_payload=True,
            with_vectors=False
        )

        sessions = []
        for point in results:
            sessions.append({
                "checkpoint_id": point.payload.get("checkpoint_id", "unknown"),
                "session_date": point.payload.get("session_date", "unknown"),
                "session_type": point.payload.get("session_type", "unknown"),
                "content": point.payload.get("content", {})
            })

        return sessions

    def format_results(self, memories: List[Dict], include_scores: bool = True) -> str:
        """
        Format search results for display.

        Args:
            memories: List of memory dictionaries
            include_scores: Whether to include similarity scores

        Returns:
            Formatted string representation
        """
        if not memories:
            return "No relevant memories found."

        output = []
        output.append("=" * 80)
        output.append(f"Found {len(memories)} relevant memories:")
        output.append("=" * 80)

        for idx, memory in enumerate(memories, 1):
            output.append(f"\n[{idx}] {memory['metadata']['source_file']} ({memory['metadata']['session_date']})")
            if include_scores:
                output.append(f"Similarity: {memory['score']:.3f}")
            output.append(f"Section: {memory['metadata']['section']}")
            output.append("-" * 80)

            # Format content
            content = memory['content']
            if isinstance(content, dict):
                for key, value in content.items():
                    if value:
                        output.append(f"\n{key.upper()}:")
                        if isinstance(value, list):
                            for item in value:
                                output.append(f"  - {item}")
                        else:
                            output.append(f"  {value}")
            else:
                output.append(f"\n{content}")

            output.append("")

        return "\n".join(output)


def search_memories(
    query: str,
    limit: int = 5,
    section: Optional[str] = None,
    qdrant_host: str = "localhost",
    qdrant_port: int = 6333
):
    """
    Convenience function for memory search.

    Args:
        query: Search query text
        limit: Maximum results to return
        section: Optional section filter
        qdrant_host: Qdrant server host
        qdrant_port: Qdrant server port
    """
    searcher = MemorySearcher(qdrant_host=qdrant_host, qdrant_port=qdrant_port)
    memories = searcher.search(query, limit=limit, section_filter=section)
    print(searcher.format_results(memories))
    return memories


def hybrid_search_memories(
    query: str,
    limit: int = 5,
    domains: Optional[List[str]] = None,
    keywords: Optional[List[str]] = None,
    patterns: Optional[List[str]] = None,
    qdrant_host: str = "localhost",
    qdrant_port: int = 6333
):
    """
    Convenience function for hybrid semantic + keyword search.

    Args:
        query: Semantic search query text
        limit: Maximum results to return
        domains: Filter by domain tags
        keywords: Filter by keywords
        patterns: Filter by dyadic patterns
        qdrant_host: Qdrant server host
        qdrant_port: Qdrant server port
    """
    searcher = MemorySearcher(qdrant_host=qdrant_host, qdrant_port=qdrant_port)
    memories = searcher.hybrid_search(
        query=query,
        limit=limit,
        domains=domains,
        keywords=keywords,
        patterns=patterns
    )
    print(searcher.format_results(memories))
    return memories


if __name__ == "__main__":
    import sys

    # Interactive search mode
    print("=" * 80)
    print("Rhiz Memory System - Semantic Search")
    print("=" * 80)

    searcher = MemorySearcher()

    if len(sys.argv) > 1:
        # Command-line query
        query = " ".join(sys.argv[1:])
        print(f"\nQuery: {query}\n")
        memories = searcher.search(query, limit=5)
        print(searcher.format_results(memories))
    else:
        # Interactive mode
        print("\nEnter search queries (or 'quit' to exit)")
        print("Commands:")
        print("  search <query>     - Search for memories")
        print("  recent             - Show recent sessions")
        print("  quit               - Exit")
        print("")

        while True:
            try:
                user_input = input("search> ").strip()

                if not user_input:
                    continue

                if user_input.lower() in ["quit", "exit", "q"]:
                    print("Goodbye!")
                    break

                if user_input.lower() == "recent":
                    sessions = searcher.get_recent_sessions(limit=5)
                    print("\nRecent Sessions:")
                    print("=" * 80)
                    for session in sessions:
                        print(f"\n{session['checkpoint_id']} ({session['session_date']})")
                        print(f"Type: {session['session_type']}")
                        if 'session_arc' in session['content']:
                            print(f"Arc: {session['content']['session_arc'][:200]}...")
                    print("")
                    continue

                # Search
                memories = searcher.search(user_input, limit=5)
                print(searcher.format_results(memories))

            except KeyboardInterrupt:
                print("\n\nGoodbye!")
                break
            except Exception as e:
                print(f"Error: {e}")
