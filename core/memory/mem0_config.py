#!/usr/bin/env python3
"""
Mem0 Configuration for Rhiz Skill Context Memory

Initializes Mem0 with existing Qdrant instance for skill-specific
context memory and retrieval-augmented activation.

ARCHITECTURE:
- Uses existing Qdrant instance (localhost:6333)
- Separate collection: rhiz_skill_memory (isolated from rhiz_memories)
- Embeddings: sentence-transformers all-MiniLM-L6-v2 (384-dim, CPU-optimized)
- Memory types: skill context, execution results, user preferences

USAGE:
    from core.memory.mem0_config import initialize_mem0

    memory = initialize_mem0()
    memory.add(
        "User prefers concise technical explanations",
        user_id="captain",
        metadata={"skill_context": "communication_style"}
    )

    relevant = memory.search(
        query="analyze trading performance",
        user_id="captain",
        limit=3
    )
"""

from mem0 import Memory
from typing import Optional


def initialize_mem0(
    qdrant_host: str = "localhost",
    qdrant_port: int = 6333,
    collection_name: str = "rhiz_skill_memory"
) -> Memory:
    """
    Initialize Mem0 with existing Qdrant instance.

    Args:
        qdrant_host: Qdrant server host
        qdrant_port: Qdrant server port
        collection_name: Collection name for skill memories

    Returns:
        Configured Memory instance

    Raises:
        RuntimeError: If Mem0 initialization fails
    """
    try:
        config = {
            "vector_store": {
                "provider": "qdrant",
                "config": {
                    "host": qdrant_host,
                    "port": qdrant_port,
                    "collection_name": collection_name,
                    "embedding_model_dims": 384  # all-MiniLM-L6-v2 dimension
                }
            },
            "llm": {
                "provider": "ollama",
                "config": {
                    "model": "qwen2.5-coder:7b",
                    "ollama_base_url": "http://localhost:11434"
                }
            },
            "embedder": {
                "provider": "huggingface",
                "config": {
                    "model": "sentence-transformers/all-MiniLM-L6-v2"
                }
            },
            "version": "v1.1"
        }

        memory = Memory.from_config(config)
        return memory

    except Exception as e:
        raise RuntimeError(
            f"Failed to initialize Mem0: {e}\n"
            f"Verify Qdrant is running at {qdrant_host}:{qdrant_port}\n"
            f"Check sentence-transformers is installed"
        )


def add_skill_memory(
    memory: Memory,
    content: str,
    skill: str,
    user_id: str = "captain",
    memory_type: str = "context"
) -> dict:
    """
    Add skill-specific memory.

    Args:
        memory: Mem0 Memory instance
        content: Memory content to store
        skill: Skill name (e.g., "trading/kraken_analysis")
        user_id: User identifier
        memory_type: Memory type (context|execution_result|preference)

    Returns:
        Memory add result with ID

    Example:
        add_skill_memory(
            memory,
            "Include circuit breaker status in trading analysis",
            skill="trading/kraken_analysis",
            memory_type="context"
        )
    """
    return memory.add(
        content,
        user_id=user_id,
        metadata={
            "skill": skill,
            "memory_type": memory_type
        }
    )


def search_skill_memory(
    memory: Memory,
    query: str,
    skill: Optional[str] = None,
    user_id: str = "captain",
    limit: int = 3
) -> list:
    """
    Search skill memories.

    Args:
        memory: Mem0 Memory instance
        query: Search query
        skill: Optional skill filter
        user_id: User identifier
        limit: Max results to return

    Returns:
        List of relevant memories

    Example:
        memories = search_skill_memory(
            memory,
            query="analyze trading performance",
            skill="trading/kraken_analysis",
            limit=3
        )
    """
    filters = None
    if skill:
        filters = {"skill": skill}

    result = memory.search(
        query=query,
        user_id=user_id,
        limit=limit,
        filters=filters
    )

    # Extract results list from dict response
    if isinstance(result, dict) and 'results' in result:
        return result['results']
    return []


if __name__ == "__main__":
    # Test Mem0 initialization
    print("=" * 80)
    print("Mem0 Configuration Test")
    print("=" * 80)

    try:
        # Initialize
        memory = initialize_mem0()
        print("[OK] Mem0 initialized successfully")

        # Add test memory
        result = add_skill_memory(
            memory,
            "User prefers concise technical explanations",
            skill="communication",
            memory_type="preference"
        )
        print(f"[OK] Added test memory: {result}")

        # Search test
        results = search_skill_memory(
            memory,
            query="how should I communicate?",
            limit=1
        )
        print(f"[OK] Search test: {len(results)} results")
        if results:
            for mem in results:
                print(f"  - {mem.get('memory', 'N/A')}")

        print("\n" + "=" * 80)
        print("Mem0 test complete")
        print("=" * 80)

    except Exception as e:
        print(f"[FAIL] Mem0 test failed: {e}")
        raise
