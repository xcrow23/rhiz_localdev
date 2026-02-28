"""
Shared fixtures and utilities for skill routing tests.
"""

import pytest
import sys
from pathlib import Path

# Add project root to path
RHIZ_ROOT = Path(__file__).parent.parent.parent.parent
if str(RHIZ_ROOT) not in sys.path:
    sys.path.insert(0, str(RHIZ_ROOT))


@pytest.fixture(scope="session")
def qdrant_available():
    """Check if Qdrant is running and accessible."""
    from qdrant_client import QdrantClient

    try:
        client = QdrantClient(host="localhost", port=6333)
        client.get_collections()
        return True
    except Exception:
        return False


@pytest.fixture(scope="session")
def skills_collection_exists(qdrant_available):
    """Check if rhiz_skills collection exists."""
    if not qdrant_available:
        return False

    from qdrant_client import QdrantClient

    try:
        client = QdrantClient(host="localhost", port=6333)
        collections = client.get_collections().collections
        collection_names = [c.name for c in collections]
        return "rhiz_skills" in collection_names
    except Exception:
        return False


@pytest.fixture(scope="session")
def validate_skills_collection(skills_collection_exists):
    """
    Validate rhiz_skills collection has correct content.

    Verifies:
    - Collection has exactly 6 skills
    - All expected skill names present
    - No duplicate skills

    Catches partial ingestion, stale data, and schema issues.
    """
    if not skills_collection_exists:
        pytest.skip("rhiz_skills collection not found")

    from qdrant_client import QdrantClient

    client = QdrantClient(host="localhost", port=6333)

    # Get all points
    points, _ = client.scroll(
        collection_name="rhiz_skills",
        limit=100,
        with_payload=True
    )

    # Expected skills
    expected_skills = {
        "trading/kraken_analysis",
        "memory/checkpoint_retrieval",
        "infrastructure/deployment",
        "memory/session_management",
        "research/documentation",
        "trading/strategy_execution"
    }

    # Extract actual skills
    actual_skills = {p.payload.get("name") for p in points if "name" in p.payload}

    # Validate count
    assert len(points) == 6, \
        f"Expected 6 skills, found {len(points)}. Partial ingestion detected."

    # Validate skill names
    assert actual_skills == expected_skills, \
        f"Skill mismatch. Missing: {expected_skills - actual_skills}. " \
        f"Extra: {actual_skills - expected_skills}. " \
        f"Re-run: python core/skills/scripts/ingest_skills.py"

    return True


@pytest.fixture(scope="session")
def skill_router(validate_skills_collection):
    """
    Create SkillRouter instance (session-scoped for performance).

    Depends on validate_skills_collection to ensure collection is valid.
    Session scope amortizes 500ms router initialization across all tests.
    """
    from core.skills.router import SkillRouter

    return SkillRouter()


@pytest.fixture
def sample_queries():
    """Sample queries for testing router accuracy."""
    return {
        "trading": [
            "analyze my Kraken trading performance",
            "check Kraken portfolio balance",
            "what's my trading history",
            "review market trends for BTC",
            "execute a buy order"
        ],
        "memory": [
            "find sessions about infrastructure",
            "search for trading-related checkpoints",
            "what did we work on last week",
            "retrieve memory of deployment",
            "load session context"
        ],
        "infrastructure": [
            "deploy to VPS",
            "update Cloudflare Worker",
            "check Docker container status",
            "restart Qdrant service",
            "monitor system health"
        ],
        "research": [
            "write documentation for memory system",
            "create research notes",
            "document architectural decisions",
            "analyze skill compression patterns"
        ],
        "general": [
            "what's the weather",
            "tell me a joke",
            "random unrelated query"
        ]
    }


@pytest.fixture
def expected_skills():
    """Expected skill matches for sample queries."""
    return {
        "analyze my Kraken trading performance": "trading/kraken_analysis",
        "find sessions about infrastructure": "memory/checkpoint_retrieval",
        "deploy to VPS": "infrastructure/deployment",
        "write documentation for memory system": "research/documentation",
        "what did we work on last week": "memory/checkpoint_retrieval",
        "check Kraken portfolio balance": "trading/kraken_analysis",
        "update Cloudflare Worker": "infrastructure/deployment",
        "load session context": "memory/session_management",
        "execute a buy order": "trading/strategy_execution"
    }
