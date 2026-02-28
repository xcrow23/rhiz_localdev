"""
Fathom Memory Tools
MCP tools for logging and searching trading memory.
"""

from typing import Any, Optional
from ..memory.logger import FathomMemory


async def fathom_log_decision(
    memory: FathomMemory,
    pair: str,
    side: str,
    decision_type: str,
    reasoning: str,
    hypothesis: Optional[str] = None,
    trade_data: Optional[dict] = None
) -> dict[str, Any]:
    """
    Log a trading decision to memory.

    Args:
        pair: Trading pair (e.g., "BTC/USD")
        side: "buy", "sell", or "observe"
        decision_type: "market", "limit", "observe", "hypothesis"
        reasoning: Why this decision was made
        hypothesis: Optional hypothesis being tested
        trade_data: Optional trade details

    Returns:
        {
            "success": bool,
            "point_id": int,
            "message": str,
            "timestamp": str
        }
    """
    from datetime import datetime

    try:
        result = memory.log_trade_decision(
            pair=pair,
            side=side,
            decision_type=decision_type,
            reasoning=reasoning,
            hypothesis=hypothesis,
            trade_data=trade_data
        )

        if result.get("success"):
            return {
                "success": True,
                "point_id": result["point_id"],
                "message": f"Decision logged successfully for {pair}",
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
        else:
            return {
                "success": False,
                "error": result.get("error", "Unknown error"),
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }


async def fathom_search_memory(
    memory: FathomMemory,
    query: str,
    limit: int = 5,
    pair: Optional[str] = None,
    outcome: Optional[str] = None
) -> dict[str, Any]:
    """
    Search trading memory semantically.

    Args:
        query: Search query (e.g., "successful BTC buys during consolidation")
        limit: Number of results
        pair: Optional filter by trading pair
        outcome: Optional filter by outcome (success, failure, pending)

    Returns:
        {
            "results": [{decision}, ...],
            "count": int,
            "query": str,
            "timestamp": str
        }
    """
    from datetime import datetime

    try:
        # Build filter
        filter_conditions = None
        if pair or outcome:
            must_conditions = []

            if pair:
                must_conditions.append({
                    "key": "pair",
                    "match": {"value": pair}
                })

            if outcome:
                must_conditions.append({
                    "key": "outcome",
                    "match": {"value": outcome}
                })

            if must_conditions:
                filter_conditions = {"must": must_conditions}

        results = memory.search_decisions(
            query=query,
            limit=limit,
            filter_conditions=filter_conditions
        )

        return {
            "results": results,
            "count": len(results),
            "query": query,
            "filters": {"pair": pair, "outcome": outcome} if (pair or outcome) else None,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "success": True
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }


async def fathom_update_outcome(
    memory: FathomMemory,
    point_id: int,
    outcome: str,
    pnl: Optional[float] = None,
    notes: Optional[str] = None
) -> dict[str, Any]:
    """
    Update the outcome of a logged decision.

    Args:
        point_id: Decision ID from fathom_log_decision
        outcome: "success", "failure", "learning", "ongoing"
        pnl: Optional profit/loss amount
        notes: Optional outcome notes

    Returns:
        {
            "success": bool,
            "point_id": int,
            "outcome": str,
            "timestamp": str
        }
    """
    from datetime import datetime

    try:
        outcome_data = {}
        if pnl is not None:
            outcome_data["pnl"] = pnl
        if notes:
            outcome_data["notes"] = notes

        success = memory.update_outcome(
            point_id=point_id,
            outcome=outcome,
            outcome_data=outcome_data if outcome_data else None
        )

        return {
            "success": success,
            "point_id": point_id,
            "outcome": outcome,
            "message": "Outcome updated successfully" if success else "Failed to update outcome",
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }


async def fathom_review_hypothesis(
    memory: FathomMemory,
    hypothesis: str
) -> dict[str, Any]:
    """
    Review outcomes for a specific hypothesis.

    Args:
        hypothesis: Hypothesis text to review

    Returns:
        {
            "hypothesis": str,
            "total_tests": int,
            "success_count": int,
            "failure_count": int,
            "success_rate": float,
            "outcomes": {success: [], failure: [], pending: []},
            "timestamp": str
        }
    """
    from datetime import datetime

    try:
        result = memory.get_hypothesis_outcomes(hypothesis)

        return {
            **result,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "success": True
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }


async def fathom_get_memory_stats(memory: FathomMemory) -> dict[str, Any]:
    """
    Get memory collection statistics.

    Returns:
        {
            "collection": str,
            "total_decisions": int,
            "status": str,
            "timestamp": str
        }
    """
    from datetime import datetime

    try:
        stats = memory.get_stats()

        return {
            **stats,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "success": True
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
