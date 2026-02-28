#!/usr/bin/env python3
"""
Semantic Skill Router for Rhiz

Lightweight semantic router using sentence-transformers + Qdrant
for sub-10ms skill selection based on query similarity.

No external routing packages needed - uses existing stack.

THRESHOLD RATIONALE:
- Default threshold: 0.25 (tuned for multi-component embeddings, Jan 24 2026)
- Skill fingerprints use multi-component embeddings (description + utterances +
  category + tools), which naturally produce lower similarity scores than single-text
  matching due to signal dilution across components
- Empirical data with 97 total utterances (52 added in Session 3) showed:
  * Clear matches: 0.25-0.70 range (multi-component embeddings)
  * Borderline matches: 0.20-0.25 range
  * Poor matches: <0.20
- Threshold progression:
  * 0.70: 85% fallback rate (too conservative)
  * 0.45: 56.7% accuracy (too strict for multi-component)
  * 0.25: 70-80% accuracy (appropriate for diluted signal)
- Compare to memory system thresholds:
  * Memory semantic search: 0.50 (single-text, more precise)
  * Hybrid search: 0.25 (same as skills - handles multi-field matching)
  * Session start: 0.28 (borderline context)
- Multi-component embeddings trade precision for coverage - lower threshold compensates

PERFORMANCE:
- Router initialization: ~500ms (model load + Qdrant connection)
- Query routing: 20-30ms average (includes embedding + vector search)
- Singleton pattern reduces per-query overhead to ~7-15ms
- Skills metadata cached at module level (one-time 5-10ms load)

ARCHITECTURE NOTES:
- Local development only - not deployed to cloud production
- Cloud infrastructure uses deterministic workflows, not semantic routing
- See CLAUDE.md "Deployment Strategy" for rationale
"""

import yaml
from pathlib import Path
from typing import Dict, Optional, List
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient


# Module-level cache for skills metadata (singleton pattern)
_SKILLS_METADATA_CACHE = None


def _load_skills_metadata() -> Dict[str, Dict]:
    """
    Load skills registry once per process (module-level singleton).

    Returns:
        Dict mapping skill names to their metadata

    Raises:
        RuntimeError: If skill registry file not found or invalid
    """
    global _SKILLS_METADATA_CACHE

    if _SKILLS_METADATA_CACHE is not None:
        return _SKILLS_METADATA_CACHE

    skills_file = Path(__file__).parent / "registry" / "skill_fingerprints.yaml"

    try:
        with open(skills_file) as f:
            data = yaml.safe_load(f)

            if not data or "skills" not in data:
                raise ValueError("skill_fingerprints.yaml missing 'skills' key")

            skills = data.get("skills", [])
            if not isinstance(skills, list):
                raise ValueError("skill_fingerprints.yaml: 'skills' must be a list")

            # Build metadata dict
            metadata = {}
            for idx, skill in enumerate(skills):
                if "name" not in skill:
                    raise ValueError(f"Skill #{idx+1} missing 'name' key: {skill}")
                metadata[skill["name"]] = skill

            _SKILLS_METADATA_CACHE = metadata
            return _SKILLS_METADATA_CACHE

    except FileNotFoundError:
        raise RuntimeError(
            f"Skill registry not found at {skills_file}\n"
            f"Expected path: {skills_file.absolute()}\n"
            f"Verify RHIZ_ROOT is correct or run from repo root"
        )
    except yaml.YAMLError as e:
        raise RuntimeError(f"Failed to parse skill_fingerprints.yaml: {e}")
    except ValueError as e:
        raise RuntimeError(f"Invalid skill registry structure: {e}")


class SkillRouter:
    """
    Semantic router for skill selection using Qdrant vector search.

    Routes user queries to appropriate skills based on embedding similarity
    to skill fingerprints (description + utterances + tools).
    """

    def __init__(
        self,
        qdrant_host: str = "localhost",
        qdrant_port: int = 6333,
        collection_name: str = "rhiz_skills"
    ):
        """
        Initialize the skill router.

        Args:
            qdrant_host: Qdrant server host
            qdrant_port: Qdrant server port
            collection_name: Name of skills collection

        Raises:
            RuntimeError: If Qdrant connection fails, model load fails, or skill registry unavailable
        """
        # Connect to Qdrant with error handling
        try:
            self.client = QdrantClient(host=qdrant_host, port=qdrant_port)
            # Verify connection with health check
            self.client.get_collections()
        except Exception as e:
            raise RuntimeError(
                f"Failed to connect to Qdrant at {qdrant_host}:{qdrant_port}\n"
                f"Error: {e}\n"
                f"Verify Qdrant is running: docker ps | grep qdrant"
            )

        self.collection_name = collection_name

        # Load embedding model with error handling
        try:
            self.encoder = SentenceTransformer('all-MiniLM-L6-v2')
        except Exception as e:
            raise RuntimeError(
                f"Failed to load sentence transformer model: {e}\n"
                f"This may indicate missing dependencies or network issues."
            )

        # Load skill registry for metadata (uses module-level cache)
        self.skills_metadata = _load_skills_metadata()

    def route_query(
        self,
        query: str,
        threshold: float = 0.25,
        limit: int = 3
    ) -> Dict:
        """
        Route query to most relevant skill(s).

        Args:
            query: User query to route
            threshold: Minimum similarity score (0-1) for matching
            limit: Number of candidate skills to return

        Returns:
            Dict with routing result:
            {
                "matched": bool,
                "skill": str (best match) or None,
                "confidence": float,
                "candidates": List[Dict] (top-k matches),
                "fallback": str (if no match)
            }

        Raises:
            ValueError: If input validation fails
        """
        # Input validation
        if not query or not query.strip():
            raise ValueError("Query cannot be empty")

        if not 0.0 <= threshold <= 1.0:
            raise ValueError(f"Threshold must be between 0.0 and 1.0, got {threshold}")

        if limit < 1:
            raise ValueError(f"Limit must be positive, got {limit}")

        # Encode query
        query_vector = self.encoder.encode(query).tolist()

        # Search Qdrant for similar skills with error handling
        try:
            results = self.client.query_points(
                collection_name=self.collection_name,
                query=query_vector,
                limit=limit,
                score_threshold=threshold
            ).points
        except Exception as e:
            # Collection doesn't exist or Qdrant error
            return {
                "matched": False,
                "skill": None,
                "confidence": 0.0,
                "candidates": [],
                "fallback": "general-purpose",
                "query": query,
                "error": f"Qdrant query failed: {str(e)}. Verify '{self.collection_name}' collection exists."
            }

        if not results:
            return {
                "matched": False,
                "skill": None,
                "confidence": 0.0,
                "candidates": [],
                "fallback": "general-purpose",
                "query": query
            }

        # Extract best match and candidates
        best_match = results[0]
        candidates = [
            {
                "skill": result.payload["name"],
                "confidence": result.score,
                "category": result.payload["category"],
                "tools": result.payload.get("tools", [])
            }
            for result in results
        ]

        return {
            "matched": True,
            "skill": best_match.payload["name"],
            "confidence": best_match.score,
            "category": best_match.payload["category"],
            "tools": best_match.payload.get("tools", []),
            "dependencies": best_match.payload.get("dependencies", []),
            "candidates": candidates,
            "query": query
        }

    def get_skill_metadata(self, skill_name: str) -> Optional[Dict]:
        """
        Get full metadata for a skill.

        Args:
            skill_name: Name of skill (e.g., "trading/kraken_analysis")

        Returns:
            Skill metadata dict or None if not found
        """
        return self.skills_metadata.get(skill_name)

    def route_with_context(
        self,
        query: str,
        current_domain: Optional[str] = None,
        session_context: Optional[List[str]] = None,
        threshold: float = 0.25
    ) -> Dict:
        """
        Route with additional context for boosting.

        Args:
            query: User query
            current_domain: Active domain (trading/infrastructure/etc)
            session_context: Recent skill names used this session
            threshold: Similarity threshold

        Returns:
            Routing result with context-boosted scores
        """
        base_result = self.route_query(query, threshold)

        if not base_result["matched"]:
            return base_result

        # Boost scores for candidates matching current domain
        if current_domain:
            for candidate in base_result["candidates"]:
                skill_meta = self.get_skill_metadata(candidate["skill"])
                if skill_meta and skill_meta.get("domain") == current_domain:
                    # Boost by 10% for domain match
                    candidate["confidence"] = min(1.0, candidate["confidence"] * 1.1)
                    candidate["boosted"] = "domain_match"

        # Re-sort candidates after boosting
        base_result["candidates"].sort(key=lambda x: x["confidence"], reverse=True)
        base_result["skill"] = base_result["candidates"][0]["skill"]
        base_result["confidence"] = base_result["candidates"][0]["confidence"]

        return base_result


def route_skill(
    query: str,
    threshold: float = 0.25,
    qdrant_host: str = "localhost",
    qdrant_port: int = 6333
) -> Dict:
    """
    Convenience function for skill routing.

    Args:
        query: User query to route
        threshold: Similarity threshold (default: 0.25)
        qdrant_host: Qdrant host
        qdrant_port: Qdrant port

    Returns:
        Routing result dict
    """
    router = SkillRouter(qdrant_host=qdrant_host, qdrant_port=qdrant_port)
    return router.route_query(query, threshold=threshold)


if __name__ == "__main__":
    # Test routing with sample queries
    print("=" * 80)
    print("Rhiz Semantic Skill Router - Test Mode")
    print("=" * 80)

    router = SkillRouter()

    test_queries = [
        "analyze my Kraken trading performance",
        "find sessions about infrastructure deployment",
        "deploy the mooncheck worker to Cloudflare",
        "update dyad state with current focus",
        "write documentation for the memory system",
        "check my recent trading history",
        "what's happening with the trading bot?"
    ]

    for query in test_queries:
        result = router.route_query(query, threshold=0.45, limit=3)

        print(f"\nQuery: '{query}'")
        if result["matched"]:
            print(f"  [OK] Matched: {result['skill']}")
            print(f"    Confidence: {result['confidence']:.3f}")
            print(f"    Category: {result['category']}")
            print(f"    Tools: {', '.join(result['tools'][:3])}")

            if len(result["candidates"]) > 1:
                print(f"    Alternatives:")
                for alt in result["candidates"][1:]:
                    print(f"      - {alt['skill']} ({alt['confidence']:.3f})")
        else:
            print(f"  [FALLBACK] No match (fallback: {result['fallback']})")
        print()
