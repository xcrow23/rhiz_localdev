#!/usr/bin/env python3
"""
Self-RAG Pattern for Rhiz Skill Execution

Simplified Self-RAG implementation using heuristic-based retrieval decisions.
Determines when to augment skill execution with memory retrieval based on
query complexity and skill characteristics.

ARCHITECTURE:
- [RISK_CHECK] - Heuristic evaluation of query complexity
- [RETRIEVE] - Load relevant skill context from Mem0 if needed
- [EXECUTE] - Run skill with or without augmented context
- [STORE] - Persist successful execution results as skill memory

USAGE:
    from core.skills.self_rag import SelfRAGExecutor

    executor = SelfRAGExecutor()

    result = executor.execute_with_memory(
        query="analyze my trading performance over last month",
        skill="trading/kraken_analysis"
    )

    if result["retrieved"]:
        print(f"Used context: {result['context']}")
"""

import sys
from pathlib import Path
from typing import Optional, Dict, List

# Add project root to path
RHIZ_ROOT = Path(__file__).parent.parent.parent
if str(RHIZ_ROOT) not in sys.path:
    sys.path.insert(0, str(RHIZ_ROOT))

from core.memory.mem0_config import initialize_mem0, search_skill_memory, add_skill_memory


class SelfRAGExecutor:
    """
    Simplified Self-RAG pattern for skill execution.

    Uses heuristic-based retrieval decisions to augment skill
    activation with relevant context memories.
    """

    def __init__(self):
        """Initialize Self-RAG executor with Mem0 backend."""
        self.memory = initialize_mem0()

        # Complexity keywords that trigger retrieval
        self.complexity_keywords = [
            "analyze", "compare", "history", "trend", "performance",
            "review", "assess", "evaluate", "track", "patterns",
            "over time", "last", "recent", "historical", "summary"
        ]

        # Skill-specific retrieval preferences
        self.skill_retrieval_config = {
            "trading/kraken_analysis": {
                "default_retrieve": True,  # Always retrieve for analysis
                "context_types": ["preference", "context", "execution_result"]
            },
            "trading/strategy_execution": {
                "default_retrieve": False,  # Simple execution, no context needed
                "context_types": ["preference"]  # Only user prefs
            },
            "memory/checkpoint_retrieval": {
                "default_retrieve": False,  # Already retrieves by nature
                "context_types": []
            },
            "memory/session_management": {
                "default_retrieve": True,  # Session context benefits from history
                "context_types": ["context", "execution_result"]
            },
            "infrastructure/deployment": {
                "default_retrieve": True,  # Deployment needs config context
                "context_types": ["context", "preference"]
            },
            "research/documentation": {
                "default_retrieve": True,  # Documentation benefits from patterns
                "context_types": ["context", "preference"]
            }
        }

    def should_retrieve(self, query: str, skill: str) -> bool:
        """
        Decide if retrieval needed for this query/skill combo.

        Uses heuristics:
        1. Skill-specific default (from skill_retrieval_config)
        2. Query complexity (presence of complexity keywords)
        3. Query length (longer queries = more complex)

        Args:
            query: User query
            skill: Skill name

        Returns:
            True if retrieval recommended, False otherwise
        """
        query_lower = query.lower()

        # Check skill-specific default
        skill_config = self.skill_retrieval_config.get(skill, {})
        default_retrieve = skill_config.get("default_retrieve", False)

        # Check complexity keywords
        has_complexity_keyword = any(
            kw in query_lower for kw in self.complexity_keywords
        )

        # Check query length (>8 words suggests complexity)
        word_count = len(query.split())
        is_complex_query = word_count > 8

        # Decision logic: [RISK_CHECK]
        if default_retrieve:
            return True  # Skill benefits from context by default

        if has_complexity_keyword or is_complex_query:
            return True  # Query complexity suggests retrieval needed

        return False  # Simple query, no retrieval needed

    def execute_with_memory(
        self,
        query: str,
        skill: str,
        user_id: str = "captain",
        limit: int = 3
    ) -> Dict:
        """
        Execute skill with memory augmentation if needed.

        Args:
            query: User query
            skill: Skill name (e.g., "trading/kraken_analysis")
            user_id: User identifier
            limit: Max memories to retrieve

        Returns:
            Execution plan dict with:
            - skill: Skill name
            - retrieved: Whether retrieval occurred
            - context: Retrieved memories (if any)
            - action: Execution recommendation
        """
        # [RISK_CHECK] - Determine if retrieval needed
        if self.should_retrieve(query, skill):
            # [RETRIEVE] - Get relevant context
            memories = search_skill_memory(
                self.memory,
                query=query,
                skill=skill,
                user_id=user_id,
                limit=limit
            )

            context = {
                "memories_retrieved": len(memories),
                "memories": [
                    {
                        "content": m.get("memory", ""),
                        "type": m.get("metadata", {}).get("memory_type", "unknown"),
                        "score": m.get("score", 0.0)
                    }
                    for m in memories
                ]
            }

            return {
                "skill": skill,
                "query": query,
                "retrieved": True,
                "context": context,
                "action": "Execute with augmented context",
                "risk_check": "complexity_detected"
            }
        else:
            return {
                "skill": skill,
                "query": query,
                "retrieved": False,
                "context": None,
                "action": "Execute with base capability",
                "risk_check": "simple_query"
            }

    def store_execution_result(
        self,
        skill: str,
        result: str,
        user_id: str = "captain",
        memory_type: str = "execution_result"
    ) -> Dict:
        """
        Store successful execution as skill memory.

        Args:
            skill: Skill name
            result: Execution result to store
            user_id: User identifier
            memory_type: Type of memory (execution_result|context|preference)

        Returns:
            Storage result from Mem0
        """
        return add_skill_memory(
            self.memory,
            content=result,
            skill=skill,
            user_id=user_id,
            memory_type=memory_type
        )

    def add_skill_context(
        self,
        skill: str,
        context: str,
        user_id: str = "captain"
    ) -> Dict:
        """
        Add persistent skill context memory.

        Args:
            skill: Skill name
            context: Context to remember
            user_id: User identifier

        Returns:
            Storage result from Mem0
        """
        return self.store_execution_result(
            skill=skill,
            result=context,
            user_id=user_id,
            memory_type="context"
        )

    def add_skill_preference(
        self,
        skill: str,
        preference: str,
        user_id: str = "captain"
    ) -> Dict:
        """
        Add user preference for skill execution.

        Args:
            skill: Skill name
            preference: Preference to remember
            user_id: User identifier

        Returns:
            Storage result from Mem0
        """
        return self.store_execution_result(
            skill=skill,
            result=preference,
            user_id=user_id,
            memory_type="preference"
        )


if __name__ == "__main__":
    # Test Self-RAG execution
    print("=" * 80)
    print("Self-RAG Executor Test")
    print("=" * 80)

    executor = SelfRAGExecutor()

    # Test queries
    test_cases = [
        {
            "query": "check Kraken portfolio",
            "skill": "trading/kraken_analysis",
            "expected_retrieve": True  # Skill default
        },
        {
            "query": "analyze trading performance over last month",
            "skill": "trading/kraken_analysis",
            "expected_retrieve": True  # Complexity + skill default
        },
        {
            "query": "place market buy order",
            "skill": "trading/strategy_execution",
            "expected_retrieve": False  # Simple execution, no default
        },
        {
            "query": "deploy mooncheck worker",
            "skill": "infrastructure/deployment",
            "expected_retrieve": True  # Skill default
        },
        {
            "query": "analyze patterns in our collaboration over the last 10 sessions",
            "skill": "research/documentation",
            "expected_retrieve": True  # Complexity (analyze, patterns, over, last) + skill default
        }
    ]

    print("\nRetrieval Decision Tests:")
    print("-" * 80)

    for test in test_cases:
        result = executor.execute_with_memory(
            query=test["query"],
            skill=test["skill"]
        )

        status = "[OK]" if result["retrieved"] == test["expected_retrieve"] else "[FAIL]"

        print(f"\n{status} Query: \"{test['query']}\"")
        print(f"    Skill: {test['skill']}")
        print(f"    Retrieved: {result['retrieved']} (expected: {test['expected_retrieve']})")
        print(f"    Risk Check: {result['risk_check']}")
        print(f"    Action: {result['action']}")

        if result["retrieved"] and result["context"]:
            print(f"    Memories: {result['context']['memories_retrieved']}")

    # Test memory storage
    print("\n" + "-" * 80)
    print("Memory Storage Test:")
    print("-" * 80)

    storage_result = executor.add_skill_context(
        skill="trading/kraken_analysis",
        context="Include circuit breaker status in all trading analysis reports"
    )
    print(f"\n[OK] Stored skill context: {storage_result}")

    # Test retrieval of stored context
    result = executor.execute_with_memory(
        query="analyze Kraken trading performance",
        skill="trading/kraken_analysis"
    )

    if result["retrieved"]:
        print(f"\n[OK] Retrieved context for trading analysis:")
        for mem in result["context"]["memories"]:
            print(f"  - {mem['content'][:80]}... (score: {mem['score']:.3f})")

    print("\n" + "=" * 80)
    print("Self-RAG test complete")
    print("=" * 80)
