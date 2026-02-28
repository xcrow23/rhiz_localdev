"""
Integration tests for skill routing MCP tool.

Tests the full stack: MCP server → SkillRouter → Qdrant
"""

import pytest
import json
from pathlib import Path
import sys

# Add project root to path
RHIZ_ROOT = Path(__file__).parent.parent.parent.parent
if str(RHIZ_ROOT) not in sys.path:
    sys.path.insert(0, str(RHIZ_ROOT))


@pytest.mark.integration
class TestMCPRouteToSkill:
    """Test route_to_skill MCP tool integration."""

    @pytest.fixture(scope="class")
    def mcp_server_context(self, skills_collection_exists):
        """Setup MCP server context for integration tests."""
        if not skills_collection_exists:
            pytest.skip("rhiz_skills collection required")

        # Import MCP server module
        tools_path = RHIZ_ROOT / "tools" / "rhiz-mcp" / "src"
        if str(tools_path) not in sys.path:
            sys.path.insert(0, str(tools_path))

        try:
            from server import _get_skill_router
            router, error = _get_skill_router()

            if router is None:
                pytest.skip(f"Skill router unavailable: {error}")

            return {"router": router, "get_router": _get_skill_router}
        except ImportError as e:
            pytest.skip(f"Cannot import MCP server: {e}")

    def test_singleton_pattern(self, mcp_server_context):
        """Test MCP server uses singleton pattern for router."""
        get_router = mcp_server_context["get_router"]

        # First call
        router1, error1 = get_router()
        assert router1 is not None
        assert error1 is None

        # Second call should return same instance
        router2, error2 = get_router()
        assert router2 is router1  # Same object reference
        assert error2 is None

    def test_route_to_skill_basic(self, mcp_server_context):
        """Test basic routing through MCP interface."""
        router = mcp_server_context["router"]

        result = router.route_query(
            query="analyze Kraken trading performance",
            threshold=0.45
        )

        assert result["matched"] is True
        assert result["skill"] == "trading/kraken_analysis"
        assert result["confidence"] >= 0.45

    def test_route_to_skill_with_domain_context(self, mcp_server_context):
        """Test routing with domain context boosting."""
        router = mcp_server_context["router"]

        result = router.route_with_context(
            query="check system status",
            current_domain="infrastructure",
            threshold=0.4
        )

        assert "matched" in result
        assert "candidates" in result

    def test_route_to_skill_fallback(self, mcp_server_context):
        """Test fallback behavior for unmatched queries."""
        router = mcp_server_context["router"]

        result = router.route_query(
            query="completely random unrelated query xyz",
            threshold=0.7
        )

        # Should either match with low confidence or fallback
        if not result["matched"]:
            assert result["skill"] is None
            assert result["fallback"] == "general-purpose"

    def test_route_to_skill_multiple_candidates(self, mcp_server_context):
        """Test router returns multiple candidates."""
        router = mcp_server_context["router"]

        result = router.route_query(
            query="analyze data",
            threshold=0.4,
            limit=3
        )

        assert "candidates" in result
        assert isinstance(result["candidates"], list)
        assert len(result["candidates"]) <= 3

    def test_route_to_skill_candidate_structure(self, mcp_server_context):
        """Test candidate objects have correct structure."""
        router = mcp_server_context["router"]

        result = router.route_query(
            query="analyze Kraken trading",
            threshold=0.4,
            limit=3
        )

        if result["matched"] and result["candidates"]:
            candidate = result["candidates"][0]
            assert "skill" in candidate
            assert "confidence" in candidate
            assert "category" in candidate
            assert "tools" in candidate

    def test_error_handling_collection_missing(self):
        """Test error handling when collection doesn't exist."""
        from core.skills.router import SkillRouter

        router = SkillRouter()
        router.collection_name = "nonexistent_collection"

        result = router.route_query("test query")

        assert result["matched"] is False
        assert "error" in result
        assert "Qdrant query failed" in result["error"]


@pytest.mark.integration
class TestEndToEndRouting:
    """End-to-end routing tests with real queries."""

    def test_trading_queries_route_correctly(self, skill_router):
        """Test trading-related queries route to trading skills."""
        queries = [
            "analyze my Kraken portfolio",
            "check trading performance",
            "what's my account balance",
            "review recent trades"
        ]

        for query in queries:
            result = skill_router.route_query(query, threshold=0.4)
            if result["matched"]:
                assert result["skill"].startswith("trading/"), \
                    f"Query '{query}' routed to {result['skill']} instead of trading/*"

    def test_memory_queries_route_correctly(self, skill_router):
        """Test memory-related queries route to memory skills."""
        queries = [
            "find sessions about deployment",
            "search checkpoints for trading",
            "what did we work on yesterday",
            "retrieve session context"
        ]

        for query in queries:
            result = skill_router.route_query(query, threshold=0.4)
            if result["matched"]:
                assert result["skill"].startswith("memory/"), \
                    f"Query '{query}' routed to {result['skill']} instead of memory/*"

    def test_infrastructure_queries_route_correctly(self, skill_router):
        """Test infrastructure queries route to infrastructure skills."""
        queries = [
            "deploy to VPS",
            "update Cloudflare Worker",
            "check Docker status",
            "restart Qdrant container"
        ]

        for query in queries:
            result = skill_router.route_query(query, threshold=0.4)
            if result["matched"]:
                assert result["skill"].startswith("infrastructure/"), \
                    f"Query '{query}' routed to {result['skill']} instead of infrastructure/*"

    def test_confidence_scores_reasonable(self, skill_router):
        """Test confidence scores are in expected ranges."""
        queries = [
            ("analyze Kraken trading performance", 0.5, 1.0),  # Should be high confidence
            ("check memory", 0.4, 0.7),  # Medium confidence (ambiguous)
            ("random xyz query", 0.0, 0.5)  # Low confidence
        ]

        for query, min_conf, max_conf in queries:
            result = skill_router.route_query(query, threshold=0.0)  # Allow all matches
            if result["matched"]:
                assert min_conf <= result["confidence"] <= max_conf, \
                    f"Confidence {result['confidence']} outside expected range [{min_conf}, {max_conf}] for '{query}'"

    def test_limit_parameter_respected(self, skill_router):
        """Test limit parameter controls number of candidates."""
        for limit in [1, 3, 5]:
            result = skill_router.route_query(
                "analyze data",
                threshold=0.3,
                limit=limit
            )

            if result["matched"]:
                assert len(result["candidates"]) <= limit, \
                    f"Got {len(result['candidates'])} candidates but limit was {limit}"

    def test_threshold_parameter_filters_results(self, skill_router):
        """Test threshold parameter filters low-confidence matches."""
        query = "analyze something"

        # Low threshold - should match
        result_low = skill_router.route_query(query, threshold=0.3)

        # High threshold - might not match
        result_high = skill_router.route_query(query, threshold=0.8)

        if result_low["matched"] and not result_high["matched"]:
            # This is expected - higher threshold is more selective
            assert result_low["confidence"] < 0.8

    def test_query_performance(self, skill_router):
        """Test routing performance is within acceptable bounds."""
        import time

        query = "analyze Kraken trading performance"

        # Test actual performance
        start = time.time()
        result = skill_router.route_query(query, threshold=0.45)
        elapsed_ms = (time.time() - start) * 1000

        # Verify result is valid
        assert "matched" in result

        # Performance target: <3000ms (realistic for CPU-bound Dell Inspiron)
        # Note: Production systems with GPU/better CPU will be much faster
        assert elapsed_ms < 3000, f"Routing took {elapsed_ms:.2f}ms, expected <3000ms (CPU-bound limit)"


@pytest.mark.integration
@pytest.mark.slow
class TestStressAndEdgeCases:
    """Stress tests and edge case integration scenarios."""

    def test_concurrent_routing_requests(self, skill_router):
        """Test router handles concurrent requests correctly."""
        import concurrent.futures

        queries = [
            "analyze Kraken trading",
            "find infrastructure sessions",
            "deploy to cloud",
            "check memory context",
            "execute trading strategy"
        ] * 5  # 25 concurrent requests

        def route_query(q):
            return skill_router.route_query(q, threshold=0.4)

        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            results = list(executor.map(route_query, queries))

        # All requests should complete successfully
        assert len(results) == len(queries)
        for result in results:
            assert "matched" in result

    def test_routing_after_skill_registry_change(self, skill_router):
        """Test router behavior if skill registry changes during runtime."""
        # First query
        result1 = skill_router.route_query("analyze trading", threshold=0.4)

        # Note: Actual registry change would require file modification and cache clear
        # This test documents the expected behavior

        # Second query should still work with cached metadata
        result2 = skill_router.route_query("analyze trading", threshold=0.4)

        assert result1["skill"] == result2["skill"]
        # In production, metadata is cached - changes require process restart
