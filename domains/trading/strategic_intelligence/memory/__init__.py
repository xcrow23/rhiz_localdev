"""
Memory Module - Persistent Learning for Strategic Intelligence Layer

Provides:
- Qdrant vector database integration
- Trade outcome storage and retrieval
- Strategy performance tracking
- Semantic search over historical trades
"""

from memory.qdrant_schema import (
    TradeOutcome,
    StrategyPerformanceSnapshot,
    QdrantCollections,
    OutcomeType,
    trade_outcome_to_dict,
    dict_to_trade_outcome
)

from memory.qdrant_client import (
    QdrantMemoryClient,
    encode_market_conditions,
    encode_regime_characteristics
)

__all__ = [
    'TradeOutcome',
    'StrategyPerformanceSnapshot',
    'QdrantCollections',
    'OutcomeType',
    'trade_outcome_to_dict',
    'dict_to_trade_outcome',
    'QdrantMemoryClient',
    'encode_market_conditions',
    'encode_regime_characteristics'
]
