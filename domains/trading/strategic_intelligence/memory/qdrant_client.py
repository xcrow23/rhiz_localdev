"""
Qdrant Memory Client for Strategic Intelligence Layer
Handles storage and retrieval of trade outcomes and strategy performance.

This enables the Learning Engine to:
- Store complete trade history with market context
- Query performance by strategy and regime
- Find similar historical trades via semantic search
- Track confidence calibration over time
"""

from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import asdict
import numpy as np

try:
    from qdrant_client import QdrantClient
    from qdrant_client.models import (
        Distance, VectorParams, PointStruct,
        Filter, FieldCondition, MatchValue, Range
    )
    QDRANT_AVAILABLE = True
except ImportError:
    QDRANT_AVAILABLE = False
    print("Warning: qdrant-client not installed. Install with: pip install qdrant-client")

from memory.qdrant_schema import (
    TradeOutcome, StrategyPerformanceSnapshot, QdrantCollections,
    trade_outcome_to_dict, dict_to_trade_outcome
)


class QdrantMemoryClient:
    """
    Client for interacting with Qdrant vector database.

    Handles persistence of:
    1. Trade outcomes (individual trades)
    2. Strategy performance snapshots (aggregated metrics)
    3. Decision log (all SIL decisions, including "wait")
    """

    def __init__(
        self,
        mode: str = "server",
        host: str = "localhost",
        port: int = 6333,
        api_key: Optional[str] = None,
        path: Optional[str] = None,
        initialize_collections: bool = True
    ):
        """
        Initialize Qdrant client.

        Supports two modes:
        1. Server mode: Connects to Qdrant server (requires 2GB+ RAM)
        2. On-disk mode: Direct file-based storage (requires <200MB RAM)

        Args:
            mode: Connection mode ("server" or "on_disk")
            host: Qdrant server host (default: localhost) [server mode only]
            port: Qdrant server port (default: 6333) [server mode only]
            api_key: API key for Qdrant Cloud (optional) [server mode only]
            path: Path to on-disk storage directory (default: ./data/qdrant) [on_disk mode only]
            initialize_collections: Create collections if they don't exist
        """
        if not QDRANT_AVAILABLE:
            raise ImportError(
                "qdrant-client not installed. Install with: pip install qdrant-client"
            )

        self.mode = mode

        if mode == "on_disk":
            # On-disk mode: Direct file-based storage (cloud-friendly)
            storage_path = path or "./data/qdrant"
            print(f"[Qdrant] Initializing on-disk mode at {storage_path}")
            self.client = QdrantClient(path=storage_path)
            self.on_disk = True

        elif mode == "server":
            # Server mode: Connect to Qdrant server
            print(f"[Qdrant] Connecting to server at {host}:{port}")
            self.client = QdrantClient(host=host, port=port, api_key=api_key)
            self.on_disk = False

        else:
            raise ValueError(f"Invalid mode: {mode}. Must be 'server' or 'on_disk'")

        if initialize_collections:
            self._initialize_collections()

    def _initialize_collections(self):
        """
        Create Qdrant collections if they don't exist.

        Handles race conditions where multiple instances might try to create
        the same collection simultaneously by catching "already exists" errors.
        """
        import time

        max_retries = 3
        retry_delay = 0.5  # seconds

        for attempt in range(max_retries):
            try:
                collections = self.client.get_collections().collections
                collection_names = [c.name for c in collections]

                # Initialize trade outcomes collection
                if QdrantCollections.TRADE_OUTCOMES not in collection_names:
                    self._create_collection_safe(
                        QdrantCollections.get_trade_outcome_schema()
                    )

                # Initialize strategy performance collection
                if QdrantCollections.STRATEGY_PERFORMANCE not in collection_names:
                    self._create_collection_safe(
                        QdrantCollections.get_strategy_performance_schema()
                    )

                # Initialize decision log collection
                if QdrantCollections.DECISION_LOG not in collection_names:
                    self._create_collection_safe(
                        QdrantCollections.get_decision_log_schema()
                    )

                # Success - break retry loop
                break

            except Exception as e:
                if attempt < max_retries - 1:
                    print(f"Collection initialization failed (attempt {attempt + 1}/{max_retries}): {e}")
                    time.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                else:
                    raise Exception(f"Failed to initialize collections after {max_retries} attempts: {e}")

    def _create_collection_safe(self, schema: dict):
        """
        Create a collection with error handling for race conditions.

        Args:
            schema: Collection schema dict with collection_name and vector_size
        """
        try:
            self.client.create_collection(
                collection_name=schema["collection_name"],
                vectors_config=VectorParams(
                    size=schema["vector_size"],
                    distance=Distance.COSINE
                )
            )
            print(f"Created collection: {schema['collection_name']}")

        except Exception as e:
            # Check if error is "already exists" - this is fine (race condition)
            error_msg = str(e).lower()
            if "already exists" in error_msg or "exist" in error_msg:
                print(f"Collection {schema['collection_name']} already exists (created by another instance)")
            else:
                # Re-raise if it's a different error
                raise

    # ========================================
    # Trade Outcome Storage & Retrieval
    # ========================================

    def store_trade_outcome(
        self,
        trade_outcome: TradeOutcome,
        embedding: np.ndarray
    ) -> str:
        """
        Store a completed trade in Qdrant.

        Args:
            trade_outcome: TradeOutcome object
            embedding: 128-dim vector encoding market conditions at entry

        Returns:
            Point ID (UUID string)
        """
        payload = trade_outcome_to_dict(trade_outcome)

        # Create point
        point = PointStruct(
            id=trade_outcome.trade_id,
            vector=embedding.tolist(),
            payload=payload
        )

        # Store in Qdrant
        self.client.upsert(
            collection_name=QdrantCollections.TRADE_OUTCOMES,
            points=[point]
        )

        return trade_outcome.trade_id

    def get_trade_outcome(self, trade_id: str) -> Optional[TradeOutcome]:
        """
        Retrieve a specific trade by ID.

        Args:
            trade_id: Trade ID

        Returns:
            TradeOutcome object or None if not found
        """
        result = self.client.retrieve(
            collection_name=QdrantCollections.TRADE_OUTCOMES,
            ids=[trade_id]
        )

        if not result:
            return None

        return dict_to_trade_outcome(result[0].payload)

    def find_similar_trades(
        self,
        current_market_embedding: np.ndarray,
        strategy_name: Optional[str] = None,
        regime: Optional[str] = None,
        limit: int = 10
    ) -> List[Tuple[TradeOutcome, float]]:
        """
        Find historical trades with similar market conditions.

        This is the core semantic search capability: "What happened
        in similar market conditions?"

        Args:
            current_market_embedding: 128-dim vector of current market
            strategy_name: Filter by strategy (optional)
            regime: Filter by regime (optional)
            limit: Max results to return

        Returns:
            List of (TradeOutcome, similarity_score) tuples
        """
        # Build filter
        must_conditions = []

        if strategy_name:
            must_conditions.append(
                FieldCondition(
                    key="strategy_name",
                    match=MatchValue(value=strategy_name)
                )
            )

        if regime:
            must_conditions.append(
                FieldCondition(
                    key="market_regime",
                    match=MatchValue(value=regime)
                )
            )

        filter_obj = Filter(must=must_conditions) if must_conditions else None

        # Search
        results = self.client.search(
            collection_name=QdrantCollections.TRADE_OUTCOMES,
            query_vector=current_market_embedding.tolist(),
            query_filter=filter_obj,
            limit=limit
        )

        # Convert to TradeOutcome objects
        trades_with_scores = []
        for hit in results:
            trade = dict_to_trade_outcome(hit.payload)
            trades_with_scores.append((trade, hit.score))

        return trades_with_scores

    def get_trades_by_strategy_and_regime(
        self,
        strategy_name: str,
        regime: str,
        days_back: int = 30,
        limit: int = 100,
        offset: Optional[str] = None
    ) -> Dict:
        """
        Get trades for a strategy in a specific regime with pagination support.

        Args:
            strategy_name: Strategy name (e.g., "mean_reversion")
            regime: Regime name (e.g., "ranging_low_vol")
            days_back: How far back to search (default 30 days)
            limit: Maximum results per page (default 100, max 1000)
            offset: Pagination offset from previous response (None = first page)

        Returns:
            Dict with:
                - trades: List of TradeOutcome objects
                - nextCursor: Offset for next page (None if no more results)
                - total: Total matching trades
                - hasMore: Boolean indicating more results available
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days_back)

        filter_obj = Filter(
            must=[
                FieldCondition(
                    key="strategy_name",
                    match=MatchValue(value=strategy_name)
                ),
                FieldCondition(
                    key="market_regime",
                    match=MatchValue(value=regime)
                ),
                FieldCondition(
                    key="timestamp_entry",
                    range=Range(gte=cutoff_date.isoformat())
                )
            ]
        )

        # Scroll with pagination
        results, next_offset = self.client.scroll(
            collection_name=QdrantCollections.TRADE_OUTCOMES,
            scroll_filter=filter_obj,
            limit=min(limit, 1000),  # Cap at 1000 for safety
            offset=offset
        )

        trades = [dict_to_trade_outcome(point.payload) for point in results]

        return {
            "trades": trades,
            "nextCursor": next_offset,
            "total": len(results),  # Current page count
            "hasMore": next_offset is not None
        }

    def iter_trades_by_strategy_and_regime(
        self,
        strategy_name: str,
        regime: str,
        days_back: int = 30,
        batch_size: int = 100
    ):
        """
        Iterator for all trades matching criteria (handles pagination automatically).

        Yields batches of trades, automatically fetching next pages.

        Args:
            strategy_name: Strategy name
            regime: Regime name
            days_back: Time window
            batch_size: Results per batch

        Yields:
            List[TradeOutcome] for each batch
        """
        offset = None

        while True:
            result = self.get_trades_by_strategy_and_regime(
                strategy_name=strategy_name,
                regime=regime,
                days_back=days_back,
                limit=batch_size,
                offset=offset
            )

            if result["trades"]:
                yield result["trades"]

            if not result["hasMore"]:
                break

            offset = result["nextCursor"]

    # ========================================
    # Strategy Performance Snapshots
    # ========================================

    def store_strategy_performance(
        self,
        snapshot: StrategyPerformanceSnapshot,
        embedding: np.ndarray
    ) -> str:
        """
        Store aggregated strategy performance snapshot.

        These are updated periodically (e.g., daily or after N trades)
        to enable fast performance lookups without scanning all trades.

        Args:
            snapshot: StrategyPerformanceSnapshot object
            embedding: 64-dim vector encoding regime characteristics

        Returns:
            Point ID
        """
        payload = asdict(snapshot)

        # Convert datetime to ISO string
        payload['start_date'] = snapshot.start_date.isoformat()
        payload['end_date'] = snapshot.end_date.isoformat()
        payload['last_updated'] = snapshot.last_updated.isoformat()

        # Create unique ID: strategy_regime_date
        point_id = f"{snapshot.strategy_name}_{snapshot.regime}_{snapshot.end_date.strftime('%Y%m%d')}"

        point = PointStruct(
            id=point_id,
            vector=embedding.tolist(),
            payload=payload
        )

        self.client.upsert(
            collection_name=QdrantCollections.STRATEGY_PERFORMANCE,
            points=[point]
        )

        return point_id

    def get_strategy_performance(
        self,
        strategy_name: str,
        regime: str
    ) -> Optional[StrategyPerformanceSnapshot]:
        """
        Get latest performance snapshot for strategy-regime combination.

        Args:
            strategy_name: Strategy name
            regime: Regime name

        Returns:
            StrategyPerformanceSnapshot or None
        """
        filter_obj = Filter(
            must=[
                FieldCondition(
                    key="strategy_name",
                    match=MatchValue(value=strategy_name)
                ),
                FieldCondition(
                    key="regime",
                    match=MatchValue(value=regime)
                )
            ]
        )

        # Get most recent snapshot
        results, _ = self.client.scroll(
            collection_name=QdrantCollections.STRATEGY_PERFORMANCE,
            scroll_filter=filter_obj,
            limit=1,
            order_by="last_updated"
        )

        if not results:
            return None

        payload = results[0].payload

        # Convert ISO strings back to datetime with error handling
        try:
            payload['start_date'] = datetime.fromisoformat(payload['start_date'])
            payload['end_date'] = datetime.fromisoformat(payload['end_date'])
            payload['last_updated'] = datetime.fromisoformat(payload['last_updated'])
        except (ValueError, TypeError, KeyError) as e:
            print(f"Warning: Failed to parse datetime in performance snapshot: {e}")
            return None

        return StrategyPerformanceSnapshot(**payload)

    # ========================================
    # Decision Log
    # ========================================

    def log_decision(
        self,
        decision_id: str,
        session_id: str,
        action: str,  # "enter_long", "wait", etc.
        strategy_name: Optional[str],
        confidence: float,
        market_regime: str,
        reasoning: str,
        risk_check_passed: bool,
        embedding: np.ndarray
    ) -> str:
        """
        Log a SIL decision (including "wait" decisions).

        This enables analysis of what we DIDN'T trade and why.

        Args:
            decision_id: Unique decision ID
            session_id: Trading session ID
            action: Action taken ("enter_long", "wait", etc.)
            strategy_name: Strategy that would be used (or None if waiting)
            confidence: Decision confidence
            market_regime: Current regime
            reasoning: Text explanation of decision
            risk_check_passed: Whether risk checks passed
            embedding: 128-dim vector of market conditions

        Returns:
            Point ID
        """
        payload = {
            "decision_id": decision_id,
            "session_id": session_id,
            "timestamp": datetime.utcnow().isoformat(),
            "action": action,
            "strategy_name": strategy_name,
            "confidence": confidence,
            "market_regime": market_regime,
            "reasoning": reasoning,
            "risk_check_passed": risk_check_passed
        }

        point = PointStruct(
            id=decision_id,
            vector=embedding.tolist(),
            payload=payload
        )

        self.client.upsert(
            collection_name=QdrantCollections.DECISION_LOG,
            points=[point]
        )

        return decision_id

    # ========================================
    # Analytics & Learning
    # ========================================

    def calculate_actual_win_rate(
        self,
        current_market_embedding: np.ndarray,
        strategy_name: str,
        n_similar: int = 20
    ) -> Tuple[float, int]:
        """
        Calculate actual win rate based on similar historical trades.

        This is how we ground SIL confidence in reality:
        "In similar market conditions, this strategy won X% of the time."

        Args:
            current_market_embedding: Current market conditions
            strategy_name: Strategy being considered
            n_similar: Number of similar trades to analyze

        Returns:
            (actual_win_rate, sample_size) tuple
        """
        similar_trades = self.find_similar_trades(
            current_market_embedding,
            strategy_name=strategy_name,
            limit=n_similar
        )

        if not similar_trades:
            return 0.0, 0

        # Count wins
        wins = sum(
            1 for trade, _ in similar_trades
            if trade.exit_reason.value in ['win']
        )

        total = len(similar_trades)
        win_rate = wins / total if total > 0 else 0.0

        return win_rate, total

    def calculate_calibration_error(
        self,
        strategy_name: str,
        regime: str,
        days_back: int = 30
    ) -> Tuple[float, float, float]:
        """
        Calculate confidence calibration error.

        Compares what SIL predicted (expected_win_rate) vs what actually
        happened (actual_win_rate).

        Args:
            strategy_name: Strategy to analyze
            regime: Regime to analyze
            days_back: Time window

        Returns:
            (predicted_win_rate, actual_win_rate, calibration_error) tuple
        """
        trades = self.get_trades_by_strategy_and_regime(
            strategy_name,
            regime,
            days_back
        )

        if not trades:
            return 0.0, 0.0, 0.0

        # Calculate average predicted win rate
        avg_predicted = sum(t.expected_win_rate for t in trades) / len(trades)

        # Calculate actual win rate
        wins = sum(1 for t in trades if t.exit_reason.value == 'win')
        actual = wins / len(trades)

        # Calibration error (absolute difference)
        error = abs(avg_predicted - actual)

        return avg_predicted, actual, error

    def get_strategy_stats_by_regime(
        self,
        strategy_name: str,
        days_back: int = 30,
        max_trades: int = 10000
    ) -> Dict[str, dict]:
        """
        Get performance stats for a strategy across all regimes.

        Returns dict like:
        {
            "ranging_low_vol": {
                "trades": 15,
                "win_rate": 0.60,
                "avg_rr": 1.8,
                "calibration_error": 0.05
            },
            ...
        }

        Args:
            strategy_name: Strategy to analyze
            days_back: Time window
            max_trades: Maximum trades to fetch (default 10000, prevents excessive memory use)

        Returns:
            Dict mapping regime -> stats
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days_back)

        filter_obj = Filter(
            must=[
                FieldCondition(
                    key="strategy_name",
                    match=MatchValue(value=strategy_name)
                ),
                FieldCondition(
                    key="timestamp_entry",
                    range=Range(gte=cutoff_date.isoformat())
                )
            ]
        )

        # Fetch all trades with pagination to handle large datasets
        all_trades = []
        offset = None
        batch_size = 1000

        while len(all_trades) < max_trades:
            results, next_offset = self.client.scroll(
                collection_name=QdrantCollections.TRADE_OUTCOMES,
                scroll_filter=filter_obj,
                limit=batch_size,
                offset=offset
            )

            if not results:
                break

            all_trades.extend([dict_to_trade_outcome(point.payload) for point in results])

            if next_offset is None:
                break  # No more results

            offset = next_offset

        if len(all_trades) >= max_trades:
            print(f"Warning: Hit max_trades limit ({max_trades}). Stats may be incomplete.")

        trades = all_trades

        # Group by regime
        regime_stats = {}
        for regime in set(t.market_regime for t in trades):
            regime_trades = [t for t in trades if t.market_regime == regime]

            wins = sum(1 for t in regime_trades if t.exit_reason.value == 'win')
            win_rate = wins / len(regime_trades)

            avg_rr = sum(t.actual_rr_ratio for t in regime_trades) / len(regime_trades)

            # Calibration
            avg_predicted = sum(t.expected_win_rate for t in regime_trades) / len(regime_trades)
            calibration_error = abs(avg_predicted - win_rate)

            regime_stats[regime] = {
                "trades": len(regime_trades),
                "win_rate": win_rate,
                "avg_rr": avg_rr,
                "calibration_error": calibration_error,
                "avg_predicted_wr": avg_predicted
            }

        return regime_stats

    # ========================================
    # Maintenance
    # ========================================

    def delete_old_trades(self, days_to_keep: int = 365):
        """
        Delete trades older than specified days.

        Args:
            days_to_keep: Keep trades from last N days (default: 1 year)
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)

        filter_obj = Filter(
            must=[
                FieldCondition(
                    key="timestamp_entry",
                    range=Range(lt=cutoff_date.isoformat())
                )
            ]
        )

        self.client.delete(
            collection_name=QdrantCollections.TRADE_OUTCOMES,
            points_selector=filter_obj
        )

        print(f"Deleted trades older than {days_to_keep} days")

    def get_collection_stats(self) -> Dict[str, int]:
        """
        Get count of points in each collection.

        Returns:
            Dict mapping collection_name -> count
        """
        stats = {}

        for collection_name in [
            QdrantCollections.TRADE_OUTCOMES,
            QdrantCollections.STRATEGY_PERFORMANCE,
            QdrantCollections.DECISION_LOG
        ]:
            collection_info = self.client.get_collection(collection_name)
            stats[collection_name] = collection_info.points_count

        return stats

    def close(self):
        """
        Close the Qdrant client and clean up resources.

        Closes the connection to the Qdrant server.
        """
        try:
            if hasattr(self, 'client') and self.client:
                # The Qdrant client doesn't have an explicit close method,
                # but we can delete the client to release resources
                del self.client
                print("[Qdrant] Connection closed")
        except Exception as e:
            print(f"[Qdrant] Warning: Error closing connection: {e}")

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
        # Don't suppress exceptions
        return False


# ========================================
# Embedding Generation (Placeholder)
# ========================================

def encode_market_conditions(
    regime: str,
    volatility: float,
    sentiment: str,
    price_features: Optional[Dict] = None
) -> np.ndarray:
    """
    Encode market conditions into 128-dim embedding.

    TODO Phase 2.5: Replace with proper embedding model (sentence-transformers)

    For now, using simple feature concatenation + padding.

    Args:
        regime: Market regime (e.g., "ranging_low_vol")
        volatility: Volatility value (e.g., 0.025)
        sentiment: Sentiment direction (e.g., "neutral")
        price_features: Optional dict of price-based features

    Returns:
        128-dim numpy array
    """
    # Regime one-hot encoding (6 regimes)
    regimes = ["trending_bull", "trending_bear", "ranging_low_vol",
               "ranging_high_vol", "breakout_pending", "crash_recovery"]
    regime_vec = [1.0 if r == regime else 0.0 for r in regimes]

    # Sentiment one-hot (3 sentiments)
    sentiments = ["bullish", "neutral", "bearish"]
    sentiment_vec = [1.0 if s == sentiment else 0.0 for s in sentiments]

    # Volatility (1 feature)
    vol_vec = [volatility]

    # Price features (if available)
    if price_features:
        price_vec = [
            price_features.get('close', 0.0),
            price_features.get('rsi', 50.0) / 100.0,  # Normalize to 0-1
            price_features.get('bb_position', 0.5),
            price_features.get('volume_ratio', 1.0)
        ]
    else:
        price_vec = [0.0] * 4

    # Concatenate
    feature_vec = regime_vec + sentiment_vec + vol_vec + price_vec

    # Pad to 128 dimensions
    padding = [0.0] * (128 - len(feature_vec))
    embedding = np.array(feature_vec + padding, dtype=np.float32)

    return embedding


def encode_regime_characteristics(regime: str) -> np.ndarray:
    """
    Encode regime into 64-dim embedding for strategy performance snapshots.

    TODO Phase 2.5: Replace with proper embedding

    Args:
        regime: Regime name

    Returns:
        64-dim numpy array
    """
    # Simple one-hot + padding for now
    regimes = ["trending_bull", "trending_bear", "ranging_low_vol",
               "ranging_high_vol", "breakout_pending", "crash_recovery"]
    regime_vec = [1.0 if r == regime else 0.0 for r in regimes]

    # Pad to 64 dimensions
    padding = [0.0] * (64 - len(regime_vec))
    embedding = np.array(regime_vec + padding, dtype=np.float32)

    return embedding
