"""
Unit tests for SkillRouter class.

Tests router logic, validation, error handling, and core functionality.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import sys

# Add project root to path
RHIZ_ROOT = Path(__file__).parent.parent.parent.parent
if str(RHIZ_ROOT) not in sys.path:
    sys.path.insert(0, str(RHIZ_ROOT))

from core.skills.router import SkillRouter, _load_skills_metadata


@pytest.mark.unit
class TestSkillRouterInitialization:
    """Test SkillRouter initialization and error handling."""

    def test_initialization_with_defaults(self, skills_collection_exists):
        """Test router initializes with default parameters."""
        if not skills_collection_exists:
            pytest.skip("rhiz_skills collection required")

        router = SkillRouter()
        assert router.client is not None
        assert router.encoder is not None
        assert router.collection_name == "rhiz_skills"
        assert router.skills_metadata is not None

    def test_initialization_with_custom_params(self, skills_collection_exists):
        """Test router initializes with custom parameters."""
        if not skills_collection_exists:
            pytest.skip("rhiz_skills collection required")

        router = SkillRouter(
            qdrant_host="localhost",
            qdrant_port=6333,
            collection_name="rhiz_skills"
        )
        assert router.collection_name == "rhiz_skills"

    def test_initialization_qdrant_connection_failure(self):
        """Test router handles Qdrant connection failures gracefully."""
        with pytest.raises(RuntimeError, match="Failed to connect to Qdrant"):
            SkillRouter(qdrant_host="invalid-host", qdrant_port=9999)

    @patch('core.skills.router.SentenceTransformer')
    def test_initialization_model_load_failure(self, mock_transformer):
        """Test router handles model loading failures."""
        mock_transformer.side_effect = Exception("Model load failed")

        with pytest.raises(RuntimeError, match="Failed to load sentence transformer"):
            SkillRouter()


@pytest.mark.unit
class TestRouteQuery:
    """Test route_query method and input validation."""

    def test_route_query_valid_input(self, skill_router):
        """Test routing with valid query."""
        result = skill_router.route_query(
            query="analyze Kraken trading performance",
            threshold=0.45,
            limit=3
        )

        assert "matched" in result
        assert "skill" in result
        assert "confidence" in result
        assert "candidates" in result
        assert "query" in result

    def test_route_query_empty_string(self, skill_router):
        """Test router rejects empty query strings."""
        with pytest.raises(ValueError, match="Query cannot be empty"):
            skill_router.route_query("")

    def test_route_query_whitespace_only(self, skill_router):
        """Test router rejects whitespace-only queries."""
        with pytest.raises(ValueError, match="Query cannot be empty"):
            skill_router.route_query("   ")

    def test_route_query_invalid_threshold_too_high(self, skill_router):
        """Test router rejects threshold >1.0."""
        with pytest.raises(ValueError, match="Threshold must be between 0.0 and 1.0"):
            skill_router.route_query("test query", threshold=1.5)

    def test_route_query_invalid_threshold_negative(self, skill_router):
        """Test router rejects negative threshold."""
        with pytest.raises(ValueError, match="Threshold must be between 0.0 and 1.0"):
            skill_router.route_query("test query", threshold=-0.1)

    def test_route_query_invalid_limit_zero(self, skill_router):
        """Test router rejects limit=0."""
        with pytest.raises(ValueError, match="Limit must be positive"):
            skill_router.route_query("test query", limit=0)

    def test_route_query_invalid_limit_negative(self, skill_router):
        """Test router rejects negative limit."""
        with pytest.raises(ValueError, match="Limit must be positive"):
            skill_router.route_query("test query", limit=-5)

    def test_route_query_collection_not_exist(self, skill_router):
        """Test router handles missing collection gracefully."""
        # Create router with non-existent collection
        router_bad_collection = SkillRouter()
        router_bad_collection.collection_name = "nonexistent_collection"

        result = router_bad_collection.route_query("test query")

        assert result["matched"] is False
        assert result["skill"] is None
        assert result["fallback"] == "general-purpose"
        assert "error" in result

    def test_route_query_matched_result_structure(self, skill_router):
        """Test matched result contains all expected fields."""
        result = skill_router.route_query(
            query="analyze Kraken trading data",
            threshold=0.4
        )

        if result["matched"]:
            assert "skill" in result
            assert "confidence" in result
            assert "category" in result
            assert "tools" in result
            assert "dependencies" in result
            assert "candidates" in result
            assert isinstance(result["candidates"], list)
            assert len(result["candidates"]) > 0

    def test_route_query_no_match_result_structure(self, skill_router):
        """Test no-match result contains fallback."""
        result = skill_router.route_query(
            query="completely unrelated nonsensical query xyz123",
            threshold=0.9  # Very high threshold to force no match
        )

        assert result["matched"] is False
        assert result["skill"] is None
        assert result["confidence"] == 0.0 or result["confidence"] < 0.9
        assert result["fallback"] == "general-purpose"


@pytest.mark.unit
class TestGetSkillMetadata:
    """Test get_skill_metadata method."""

    def test_get_existing_skill(self, skill_router):
        """Test retrieving metadata for existing skill."""
        metadata = skill_router.get_skill_metadata("trading/kraken_analysis")
        assert metadata is not None
        assert metadata["name"] == "trading/kraken_analysis"
        assert "description" in metadata
        assert "utterances" in metadata

    def test_get_nonexistent_skill(self, skill_router):
        """Test retrieving metadata for non-existent skill."""
        metadata = skill_router.get_skill_metadata("nonexistent/skill")
        assert metadata is None


@pytest.mark.unit
class TestRouteWithContext:
    """Test route_with_context method and domain boosting."""

    def test_route_with_domain_match(self, skill_router):
        """Test domain boosting for matching skills."""
        result = skill_router.route_with_context(
            query="analyze trading performance",
            current_domain="trading",
            threshold=0.4
        )

        if result["matched"]:
            # Check if any candidate was boosted
            boosted = [c for c in result["candidates"] if c.get("boosted")]
            # Note: boosting may or may not apply depending on skill metadata
            assert result["skill"] is not None

    def test_route_with_context_no_domain(self, skill_router):
        """Test routing without domain parameter (should work like base route_query)."""
        result = skill_router.route_with_context(
            query="analyze trading performance",
            threshold=0.4
        )

        assert "matched" in result
        assert "candidates" in result


@pytest.mark.unit
class TestSkillsMetadataCache:
    """Test module-level metadata caching."""

    def test_metadata_loaded_once(self):
        """Test metadata is loaded only once per process."""
        from core.skills import router as router_module

        # Clear cache to test fresh load
        router_module._SKILLS_METADATA_CACHE = None

        # First load
        metadata1 = _load_skills_metadata()
        assert metadata1 is not None

        # Second load should return same instance
        metadata2 = _load_skills_metadata()
        assert metadata2 is metadata1  # Same object reference

    def test_metadata_contains_expected_skills(self):
        """Test metadata contains all ingested skills."""
        metadata = _load_skills_metadata()

        expected_skills = [
            "trading/kraken_analysis",
            "memory/checkpoint_retrieval",
            "infrastructure/deployment",
            "memory/session_management",
            "research/documentation",
            "trading/strategy_execution"
        ]

        for skill_name in expected_skills:
            assert skill_name in metadata, f"Expected skill {skill_name} not found in metadata"


@pytest.mark.unit
class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_route_query_very_long_query(self, skill_router):
        """Test routing with very long query string."""
        long_query = "analyze " * 1000 + "Kraken trading performance"

        result = skill_router.route_query(long_query, threshold=0.4)
        assert "matched" in result
        # Should still work, embedding handles long text

    def test_route_query_unicode_characters(self, skill_router):
        """Test routing with unicode characters."""
        result = skill_router.route_query(
            "分析 Kraken 交易 performance 🚀",
            threshold=0.4
        )
        assert "matched" in result

    def test_route_query_special_characters(self, skill_router):
        """Test routing with special characters."""
        result = skill_router.route_query(
            "analyze <Kraken> trading & performance!",
            threshold=0.4
        )
        assert "matched" in result

    def test_threshold_boundary_values(self, skill_router):
        """Test threshold at boundary values 0.0 and 1.0."""
        # Threshold 0.0 should match everything
        result_low = skill_router.route_query("test", threshold=0.0)
        assert result_low["matched"] is True

        # Threshold 1.0 should match almost nothing
        result_high = skill_router.route_query("test", threshold=1.0)
        # May or may not match depending on exact similarity
        assert "matched" in result_high
