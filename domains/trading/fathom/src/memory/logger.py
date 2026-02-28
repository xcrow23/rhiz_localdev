"""
Fathom Memory Logger
Logs trading decisions and patterns to Qdrant using FastEmbed.
"""

import os
from datetime import datetime
from typing import Any, Optional
from urllib.request import urlopen, Request
import json


class FathomMemory:
    """
    Memory integration using Qdrant's FastEmbed.

    No external embedding dependencies - Qdrant handles it via query API.

    Collections:
    - fathom_trading: Trade decisions, hypotheses, outcomes
    - rhiz_memories: General project memory (shared with other Rhiz components)
    """

    TRADING_COLLECTION = "fathom_trading"
    PROJECT_COLLECTION = "rhiz_memories"

    def __init__(self, qdrant_url: Optional[str] = None, use_shared_collection: bool = False):
        """
        Initialize memory logger.

        Args:
            qdrant_url: Qdrant URL (default: http://localhost:6333)
            use_shared_collection: If True, log to rhiz_memories instead of fathom_trading
        """
        self.qdrant_url = qdrant_url or os.getenv("FATHOM_QDRANT_URL", "http://localhost:6333")
        self.collection = self.PROJECT_COLLECTION if use_shared_collection else self.TRADING_COLLECTION
        self._ensure_collection()

    def _make_request(self, endpoint: str, method: str = "GET", data: dict = None) -> dict:
        """Make HTTP request to Qdrant."""
        url = f"{self.qdrant_url}{endpoint}"
        headers = {"Content-Type": "application/json"}

        request_data = json.dumps(data).encode('utf-8') if data else None
        req = Request(url, data=request_data, headers=headers, method=method)

        try:
            with urlopen(req, timeout=30) as response:
                return json.loads(response.read())
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def _ensure_collection(self):
        """Create collection if not exists."""
        # Check if collection exists
        result = self._make_request("/collections")

        if result.get("status") == "ok":
            collections = [c["name"] for c in result["result"]["collections"]]

            if self.collection not in collections:
                # Create collection with FastEmbed-compatible config
                create_data = {
                    "name": self.collection,
                    "vectors": {
                        "size": 384,  # FastEmbed default (all-MiniLM-L6-v2)
                        "distance": "Cosine"
                    }
                }

                self._make_request(
                    "/collections",
                    method="PUT",
                    data=create_data
                )

    def log_trade_decision(
        self,
        pair: str,
        side: str,
        decision_type: str,
        reasoning: str,
        hypothesis: Optional[str] = None,
        trade_data: Optional[dict] = None,
        outcome: str = "pending"
    ) -> dict:
        """
        Log a trading decision with semantic embedding.

        Args:
            pair: Trading pair (e.g., "BTC/USD")
            side: "buy" or "sell"
            decision_type: "market", "limit", "observe", "hypothesis"
            reasoning: Why this decision was made
            hypothesis: Optional hypothesis being tested
            trade_data: Optional actual trade details (price, volume, etc.)
            outcome: "pending", "success", "failure", "learning"

        Returns:
            {"success": bool, "point_id": int/str}
        """
        timestamp = datetime.utcnow().isoformat() + "Z"

        # Combine text for embedding
        text_parts = [
            f"Trading decision for {pair}",
            f"Action: {side} ({decision_type})",
            f"Reasoning: {reasoning}"
        ]

        if hypothesis:
            text_parts.append(f"Hypothesis: {hypothesis}")

        text = ". ".join(text_parts)

        # Payload
        payload = {
            "type": "trade_decision",
            "pair": pair,
            "side": side,
            "decision_type": decision_type,
            "reasoning": reasoning,
            "hypothesis": hypothesis,
            "outcome": outcome,
            "timestamp": timestamp,
            "ingested_at": timestamp
        }

        if trade_data:
            payload["trade_data"] = trade_data

        # Generate simple hash-based vector (deterministic from text)
        # TODO: Replace with FastEmbed once configured
        point_id = abs(hash(timestamp + pair + side)) % (2**63)

        # Create simple deterministic vector from text hash
        # Each word contributes to vector dimensions
        vector = [0.0] * 384
        words = text.lower().split()
        for i, word in enumerate(words):
            idx = abs(hash(word)) % 384
            vector[idx] += 0.1

        # Normalize
        magnitude = sum(v*v for v in vector) ** 0.5
        if magnitude > 0:
            vector = [v / magnitude for v in vector]

        # Store text for reference
        payload["_text"] = text

        # Upsert point with vector
        upsert_data = {
            "points": [
                {
                    "id": point_id,
                    "vector": vector,
                    "payload": payload
                }
            ]
        }

        result = self._make_request(
            f"/collections/{self.collection}/points",
            method="PUT",
            data=upsert_data
        )

        if result.get("status") == "ok":
            return {"success": True, "point_id": point_id}
        else:
            return {"success": False, "error": result.get("error", "Unknown error")}

    def search_decisions(
        self,
        query: str,
        limit: int = 5,
        filter_conditions: Optional[dict] = None
    ) -> list[dict]:
        """
        Semantic search over trading decisions.

        Args:
            query: Search query (e.g., "successful BTC trades during consolidation")
            limit: Number of results
            filter_conditions: Optional Qdrant filter

        Returns:
            List of matching decisions with scores
        """
        # Use Qdrant's text search (requires FastEmbed or manual embedding)
        # For now, we'll use scroll with payload filtering

        search_data = {
            "limit": limit,
            "with_payload": True,
            "with_vector": False
        }

        if filter_conditions:
            search_data["filter"] = filter_conditions

        result = self._make_request(
            f"/collections/{self.collection}/points/scroll",
            method="POST",
            data=search_data
        )

        if result.get("status") == "ok":
            points = result["result"]["points"]

            # Simple text matching for now (TODO: semantic search with embeddings)
            query_lower = query.lower()
            scored_points = []

            for point in points:
                payload = point.get("payload", {})
                text = payload.get("_text", "")
                reasoning = payload.get("reasoning", "")
                hypothesis = payload.get("hypothesis", "") or ""

                # Simple relevance score
                score = 0.0
                search_text = f"{text} {reasoning} {hypothesis}".lower()

                for word in query_lower.split():
                    if word in search_text:
                        score += 1.0

                if score > 0:
                    scored_points.append({
                        "score": score,
                        "id": point["id"],
                        "payload": payload
                    })

            # Sort by score
            scored_points.sort(key=lambda x: x["score"], reverse=True)
            return scored_points[:limit]

        return []

    def update_outcome(self, point_id: int, outcome: str, outcome_data: Optional[dict] = None):
        """
        Update the outcome of a logged decision.

        Args:
            point_id: Point ID from log_trade_decision
            outcome: "success", "failure", "learning", "ongoing"
            outcome_data: Optional outcome metrics (pnl, duration, etc.)
        """
        # Get existing point
        result = self._make_request(f"/collections/{self.collection}/points/{point_id}")

        if result.get("status") == "ok" and result.get("result"):
            point = result["result"]
            payload = point["payload"]
            vector = point["vector"]  # Must include vector in update

            payload["outcome"] = outcome
            payload["outcome_updated_at"] = datetime.utcnow().isoformat() + "Z"

            if outcome_data:
                payload["outcome_data"] = outcome_data

            # Update - must include both vector and payload
            update_result = self._make_request(
                f"/collections/{self.collection}/points",
                method="PUT",
                data={"points": [{"id": point_id, "vector": vector, "payload": payload}]}
            )

            return update_result.get("status") == "ok"

        return False

    def get_hypothesis_outcomes(self, hypothesis: str) -> dict:
        """
        Get all outcomes for a specific hypothesis.

        Returns success/failure counts and examples.
        """
        filter_data = {
            "must": [
                {"key": "hypothesis", "match": {"value": hypothesis}}
            ]
        }

        search_data = {
            "limit": 100,
            "with_payload": True,
            "with_vector": False,
            "filter": filter_data
        }

        result = self._make_request(
            f"/collections/{self.collection}/points/scroll",
            method="POST",
            data=search_data
        )

        if result.get("status") == "ok":
            points = result["result"]["points"]

            outcomes = {
                "success": [],
                "failure": [],
                "pending": [],
                "learning": []
            }

            for point in points:
                payload = point.get("payload", {})
                outcome = payload.get("outcome", "pending")

                if outcome in outcomes:
                    outcomes[outcome].append(payload)

            return {
                "hypothesis": hypothesis,
                "total_tests": len(points),
                "success_count": len(outcomes["success"]),
                "failure_count": len(outcomes["failure"]),
                "pending_count": len(outcomes["pending"]),
                "success_rate": (
                    len(outcomes["success"]) / (len(outcomes["success"]) + len(outcomes["failure"]))
                    if (len(outcomes["success"]) + len(outcomes["failure"])) > 0
                    else 0.0
                ),
                "outcomes": outcomes
            }

        return {"error": "Failed to retrieve hypothesis outcomes"}

    def get_stats(self) -> dict:
        """Get collection statistics."""
        result = self._make_request(f"/collections/{self.collection}")

        if result.get("status") == "ok":
            info = result["result"]
            return {
                "collection": self.collection,
                "total_decisions": info.get("points_count", 0),
                "vector_size": info.get("config", {}).get("params", {}).get("vectors", {}).get("size", 0),
                "status": "healthy"
            }

        return {"status": "error", "error": result.get("error")}
