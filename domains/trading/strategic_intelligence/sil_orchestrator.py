"""
Strategic Intelligence Layer (SIL) Orchestrator
Main entry point that coordinates all SIL components.

This is the interface that Fathom Commander and n8n workflows call.

Flow:
1. Fetch market data (via Fathom Commander)
2. Analyze market context
3. Select optimal strategy
4. Calculate position size
5. Check risk constraints
6. Generate decision with TRACE_FE
7. Return to execution layer
"""

from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Optional, Dict, List
import pandas as pd

# Import SIL components (using absolute imports for Docker compatibility)
from market_context.context_engine import MarketContextEngine, MarketContext
from strategy_selection.strategy_selector import StrategySelector, StrategyDecision
from risk_management.position_sizer import PositionSizer, RiskManager, PositionSize

# Phase 2 imports (optional - graceful degradation if not available)
try:
    from memory import QdrantMemoryClient, TradeOutcome, encode_market_conditions
    from learning import LearningEngine, PerformanceMetrics
    from transparency import (
        TraceLogger, create_trace_from_strategy_decision, create_trace_from_position_size
    )
    PHASE2_AVAILABLE = True
except ImportError:
    PHASE2_AVAILABLE = False
    print("Warning: Phase 2 modules not available (Memory/Learning/Transparency)")


@dataclass
class SILDecision:
    """
    Complete SIL decision output.

    Contains all information needed for execution:
    - What to do (strategy, position)
    - Why (full reasoning chain)
    - Risk parameters (stops, targets)
    - Transparency (TRACE_FE)
    """
    # Decision summary
    action: str  # "enter_long", "enter_short", "hold", "exit", "wait"
    strategy_name: Optional[str]

    # Position details (if entering)
    position: Optional[dict]  # PositionSize as dict

    # Strategy configuration
    strategy_config: Optional[dict]

    # Market analysis
    market_context: dict

    # Reasoning
    reasoning: Dict[str, str]
    confidence: float

    # TRACE_FE transparency
    trace_factors: List[dict]

    # Risk assessment
    risk_check: dict

    # Metadata
    timestamp: datetime
    session_id: str

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)


class SILOrchestrator:
    """
    Main coordinator for Strategic Intelligence Layer.

    Usage:
        sil = SILOrchestrator()

        # Analyze market and generate decision
        decision = sil.analyze_and_decide(
            ohlcv_data=btc_ohlcv,
            current_price=98000,
            portfolio_state={
                "total_value": 52.68,
                "exposure": 23.76,
                "positions": {}
            }
        )

        # Execute based on decision
        if decision.action == "enter_long":
            execute_trade(decision.position)
    """

    def __init__(
        self,
        session_id: Optional[str] = None,
        qdrant_mode: str = "server",
        qdrant_host: str = "localhost",
        qdrant_port: int = 6333,
        qdrant_path: Optional[str] = None,
        enable_memory: bool = False,
        enable_learning: bool = False,
        enable_transparency: bool = True
    ):
        """
        Initialize SIL orchestrator.

        Args:
            session_id: Unique session identifier for tracking
            qdrant_mode: Qdrant connection mode ("server" or "on_disk")
            qdrant_host: Qdrant server host (default: localhost) [server mode only]
            qdrant_port: Qdrant server port (default: 6333) [server mode only]
            qdrant_path: Path for on-disk storage (default: ./data/qdrant) [on_disk mode only]
            enable_memory: Enable Qdrant memory integration
            enable_learning: Enable learning engine (requires memory)
            enable_transparency: Enable TRACE_FE logging (default: True)
        """
        self.session_id = session_id or f"sil_{int(datetime.utcnow().timestamp())}"

        # Initialize Phase 1 components
        self.market_context_engine = MarketContextEngine(crypto_calibrated=True)
        self.strategy_selector = StrategySelector()
        self.position_sizer = PositionSizer(crypto_mode=True)
        self.risk_manager = RiskManager()

        # Initialize Phase 2 components (optional)
        self.memory_client: Optional['QdrantMemoryClient'] = None
        self.learning_engine: Optional['LearningEngine'] = None
        self.trace_logger: Optional['TraceLogger'] = None

        if PHASE2_AVAILABLE:
            # Transparency layer (local logging, no external dependencies)
            if enable_transparency:
                try:
                    self.trace_logger = TraceLogger(
                        console_output=True,
                        memory_client=None  # Will be set after memory init
                    )
                    self.trace_logger.start_session(self.session_id)
                    print(f"[SIL] Transparency layer enabled (session: {self.session_id})")
                except Exception as e:
                    print(f"Warning: Failed to initialize transparency layer: {e}")

            # Memory layer (supports server or on-disk mode)
            if enable_memory:
                try:
                    if qdrant_mode == "on_disk":
                        # On-disk mode (cloud-friendly, low RAM)
                        storage_path = qdrant_path or "./data/qdrant"
                        self.memory_client = QdrantMemoryClient(
                            mode="on_disk",
                            path=storage_path,
                            initialize_collections=True
                        )
                        print(f"[SIL] Memory layer enabled (on-disk mode: {storage_path})")

                    elif qdrant_mode == "server":
                        # Server mode (requires Qdrant server running)
                        self.memory_client = QdrantMemoryClient(
                            mode="server",
                            host=qdrant_host,
                            port=qdrant_port,
                            initialize_collections=True
                        )

                        # Health check: verify Qdrant server connection
                        try:
                            stats = self.memory_client.get_collection_stats()
                            print(f"[SIL] Memory layer enabled (server: {qdrant_host}:{qdrant_port})")
                            print(f"[SIL] Qdrant health check passed: {len(stats)} collections available")
                        except Exception as health_error:
                            print(f"Warning: Qdrant server health check failed: {health_error}")
                            print("Memory client created but connection may be unstable")

                    else:
                        raise ValueError(f"Invalid qdrant_mode: {qdrant_mode}")

                    # Link memory to trace logger
                    if self.trace_logger:
                        self.trace_logger.memory = self.memory_client

                except Exception as e:
                    print(f"Warning: Failed to initialize memory client: {e}")
                    print("Continuing without memory integration")
                    self.memory_client = None

            # Learning engine (requires memory)
            if enable_learning and self.memory_client:
                try:
                    self.learning_engine = LearningEngine(
                        memory_client=self.memory_client,
                        min_trades_for_learning=10,
                        confidence_threshold=0.70
                    )
                    print("[SIL] Learning engine enabled")
                except Exception as e:
                    print(f"Warning: Failed to initialize learning engine: {e}")

        # Track state
        self.last_decision: Optional[SILDecision] = None
        self.decision_count: int = 0

    def analyze_and_decide(
        self,
        ohlcv_data: pd.DataFrame,
        current_price: float,
        portfolio_state: dict,
        orderbook: Optional[dict] = None,
        constraints: Optional[dict] = None
    ) -> SILDecision:
        """
        Perform complete analysis and generate strategic decision.

        Args:
            ohlcv_data: OHLC+V data with columns [timestamp, open, high, low, close, volume]
            current_price: Current BTC price
            portfolio_state: {
                "total_value": float,
                "exposure": float,
                "positions": dict
            }
            orderbook: Optional order book data
            constraints: Optional risk constraints override

        Returns:
            SILDecision with full analysis and recommended action
        """
        self.decision_count += 1

        # Step 0: Validate OHLCV data
        validation_error = self._validate_ohlcv_data(ohlcv_data)
        if validation_error:
            return self._wait_decision(
                reason=f"OHLCV validation failed: {validation_error}",
                market_context=MarketContext(
                    regime="unknown",
                    regime_confidence=0.0,
                    volatility_regime="unknown",
                    sentiment_direction="unknown",
                    data_quality="invalid",
                    warnings=[validation_error]
                ),
                warnings=[validation_error]
            )

        # Step 1: Market Context Analysis
        market_context = self.market_context_engine.analyze(ohlcv_data, orderbook)

        # Check data quality
        if market_context.data_quality in ["insufficient", "marginal"]:
            return self._wait_decision(
                reason=f"Data quality {market_context.data_quality}",
                market_context=market_context,
                warnings=market_context.warnings
            )

        # Step 2: Strategy Selection
        strategy_decision = self.strategy_selector.select(
            market_context=market_context,
            portfolio_state=portfolio_state,
            constraints=constraints or {}
        )

        # If no strategy selected, wait
        if strategy_decision.action in ["wait", "hold"]:
            return self._build_decision(
                action=strategy_decision.action,
                strategy_name=strategy_decision.strategy_name,
                strategy_config=strategy_decision.strategy_config,
                market_context=market_context,
                reasoning=strategy_decision.reasoning,
                confidence=strategy_decision.confidence,
                trace_factors=strategy_decision.trace_factors,
                position=None,
                risk_check={"allowed": False, "reason": strategy_decision.reasoning['primary']}
            )

        # Step 3: Position Sizing
        position = self.position_sizer.calculate(
            strategy_config=strategy_decision.strategy_config,
            market_context=market_context.to_dict(),
            portfolio_state=portfolio_state,
            current_price=current_price,
            confidence=strategy_decision.confidence
        )

        # Step 4: Risk Check
        global_limits = self.strategy_selector.global_settings.get('global_risk_limits', {})
        risk_allowed, risk_reason = self.risk_manager.check_trade_allowed(
            position=position,
            portfolio_state=portfolio_state,
            global_limits=global_limits
        )

        if not risk_allowed:
            return self._build_decision(
                action="wait",
                strategy_name=strategy_decision.strategy_name,
                strategy_config=strategy_decision.strategy_config,
                market_context=market_context,
                reasoning={
                    "primary": "Trade blocked by risk controls",
                    "secondary": risk_reason,
                    "risk_assessment": "Risk limits protecting capital"
                },
                confidence=0.0,
                trace_factors=[{
                    "factor": "risk_blocked",
                    "explanation": risk_reason,
                    "confidence": 1.0
                }],
                position=asdict(position),
                risk_check={"allowed": False, "reason": risk_reason}
            )

        # Step 5: Determine action
        # For now, simplified: if we have a strategy and position, enter long
        # TODO Phase 2: Handle short positions, exits, etc.
        if position.size_usd > 0:
            action = "enter_long"
        else:
            action = "wait"

        # Step 6: Build complete decision
        return self._build_decision(
            action=action,
            strategy_name=strategy_decision.strategy_name,
            strategy_config=strategy_decision.strategy_config,
            market_context=market_context,
            reasoning=strategy_decision.reasoning,
            confidence=strategy_decision.confidence,
            trace_factors=strategy_decision.trace_factors + position.trace_factors,
            position=asdict(position) if position.size_usd > 0 else None,
            risk_check={"allowed": True, "reason": "All risk checks passed"}
        )

    def _build_decision(
        self,
        action: str,
        strategy_name: Optional[str],
        strategy_config: Optional[dict],
        market_context: MarketContext,
        reasoning: Dict[str, str],
        confidence: float,
        trace_factors: List[dict],
        position: Optional[dict],
        risk_check: dict
    ) -> SILDecision:
        """Build SILDecision object and log with TRACE_FE."""
        decision = SILDecision(
            action=action,
            strategy_name=strategy_name,
            position=position,
            strategy_config=strategy_config,
            market_context=market_context.to_dict(),
            reasoning=reasoning,
            confidence=confidence,
            trace_factors=trace_factors,
            risk_check=risk_check,
            timestamp=datetime.utcnow(),
            session_id=self.session_id
        )

        # Log decision with transparency layer
        if self.trace_logger and PHASE2_AVAILABLE:
            try:
                from .transparency import TraceFactor, DecisionTrace

                # Convert to DecisionTrace format
                trace = DecisionTrace(
                    decision_id=f"{self.session_id}_decision_{self.decision_count}",
                    timestamp=decision.timestamp,
                    decision_type="sil_decision",
                    action=action,
                    confidence=confidence,
                    primary_reasoning=reasoning.get('primary', ''),
                    secondary_reasoning=reasoning.get('secondary', ''),
                    risk_assessment=reasoning.get('risk_assessment', ''),
                    trace_factors=[
                        TraceFactor(
                            factor=f['factor'],
                            explanation=f['explanation'],
                            confidence=f['confidence'],
                            value=f.get('value')
                        )
                        for f in trace_factors
                    ],
                    alternatives=[],
                    market_context=decision.market_context,
                    portfolio_state={"position": position} if position else None,
                    session_id=self.session_id
                )

                self.trace_logger.log_decision(trace)
            except Exception as e:
                print(f"Warning: Failed to log decision: {e}")

        self.last_decision = decision
        return decision

    def _wait_decision(
        self,
        reason: str,
        market_context: MarketContext,
        warnings: List[str]
    ) -> SILDecision:
        """Generate a wait decision."""
        return self._build_decision(
            action="wait",
            strategy_name=None,
            strategy_config=None,
            market_context=market_context,
            reasoning={
                "primary": reason,
                "secondary": "; ".join(warnings) if warnings else "Waiting for better conditions",
                "risk_assessment": "No action safer than wrong action"
            },
            confidence=0.0,
            trace_factors=[{
                "factor": "wait_condition",
                "explanation": reason,
                "confidence": 1.0
            }],
            position=None,
            risk_check={"allowed": False, "reason": reason}
        )

    def get_session_stats(self) -> dict:
        """Get statistics for current session."""
        return {
            "session_id": self.session_id,
            "decision_count": self.decision_count,
            "last_decision": self.last_decision.to_dict() if self.last_decision else None,
            "current_strategy": self.strategy_selector.current_strategy,
            "daily_stats": self.risk_manager.daily_stats
        }

    def reset_daily(self):
        """Reset daily statistics (call at start of trading day)."""
        self.risk_manager.reset_daily_stats()

    def captain_override_circuit_breaker(self, reason: str = "Captain manual override"):
        """
        Captain manually overrides the circuit breaker after consecutive losses.

        IMPORTANT: This should only be called after:
        1. Captain reviews the consecutive losses
        2. Captain understands why the strategy failed
        3. Captain adjusts strategy/parameters OR confirms market regime changed
        4. Captain explicitly authorizes resuming trading

        Args:
            reason: Explanation for why override is justified (logged for audit trail)

        Example:
            >>> sil.captain_override_circuit_breaker(
            ...     reason="Regime changed from volatile to stable - mean reversion should work now"
            ... )
        """
        # Log the override attempt for transparency
        if self.trace_logger:
            self.trace_logger.log_event({
                "event": "captain_circuit_breaker_override",
                "timestamp": datetime.utcnow().isoformat(),
                "reason": reason,
                "previous_state": {
                    "circuit_breaker_tripped": self.risk_manager.daily_stats.get('circuit_breaker_tripped'),
                    "circuit_breaker_reason": self.risk_manager.daily_stats.get('circuit_breaker_reason'),
                    "consecutive_losses": self.risk_manager.daily_stats.get('consecutive_losses', 0)
                }
            })

        # Delegate to risk manager
        self.risk_manager.captain_override_circuit_breaker(reason=reason)

        # Return confirmation
        return {
            "status": "circuit_breaker_reset",
            "reason": reason,
            "timestamp": datetime.utcnow().isoformat(),
            "message": "✅ Circuit breaker reset - trading may resume"
        }

    # ========================================
    # Phase 2: Memory & Learning Integration
    # ========================================

    def record_trade_outcome(self, trade_outcome: 'TradeOutcome'):
        """
        Record completed trade in memory for learning.

        Args:
            trade_outcome: TradeOutcome object with full trade details

        Note: Call this when a trade exits (win/loss/breakeven)
        """
        if not self.memory_client or not PHASE2_AVAILABLE:
            print("Warning: Memory client not available, trade outcome not recorded")
            return

        try:
            # Encode market conditions at entry for semantic search
            embedding = encode_market_conditions(
                regime=trade_outcome.market_regime,
                volatility=trade_outcome.avg_volatility_during_trade,
                sentiment=trade_outcome.sentiment_direction,
                price_features={
                    'close': trade_outcome.entry_price,
                    'rsi': 50.0,  # TODO: Add actual RSI if available
                    'bb_position': 0.5,  # TODO: Add actual BB position
                    'volume_ratio': 1.0
                }
            )

            # Store in Qdrant
            trade_id = self.memory_client.store_trade_outcome(trade_outcome, embedding)
            print(f"[SIL] Recorded trade outcome: {trade_id}")

            # Update risk manager with outcome
            self.risk_manager.record_trade_result(
                pnl_percent=trade_outcome.pnl_percent,
                is_win=(trade_outcome.exit_reason.value == 'win')
            )

        except Exception as e:
            print(f"Error recording trade outcome: {e}")

    def get_performance_insights(
        self,
        strategy_name: Optional[str] = None,
        regime: Optional[str] = None,
        days_back: int = 30
    ) -> Dict:
        """
        Get performance insights from learning engine.

        Args:
            strategy_name: Filter by strategy (None = all strategies)
            regime: Filter by regime (None = all regimes)
            days_back: Time window (default 30 days)

        Returns:
            Dict with performance metrics and parameter suggestions
        """
        if not self.learning_engine or not PHASE2_AVAILABLE:
            return {
                "error": "Learning engine not available",
                "message": "Enable learning with enable_learning=True and Qdrant running"
            }

        try:
            insights = {}

            if strategy_name and regime:
                # Get specific strategy-regime performance
                metrics = self.learning_engine.analyze_strategy_performance(
                    strategy_name, regime, days_back
                )
                insights['performance'] = metrics

                # Get parameter suggestions
                suggestions = self.learning_engine.suggest_parameter_adaptations(
                    strategy_name, regime, days_back
                )
                insights['suggestions'] = suggestions

            else:
                # Get all performance
                all_performance = self.learning_engine.get_all_strategy_performance(days_back)
                insights['all_performance'] = all_performance

            # Get regime validation
            regime_scores = self.learning_engine.validate_regime_predictions(days_back)
            insights['regime_accuracy'] = regime_scores

            return insights

        except Exception as e:
            return {
                "error": str(e),
                "message": "Failed to get performance insights"
            }

    def update_performance_snapshots(self, days_back: int = 30):
        """
        Update strategy performance snapshots in memory.

        Call this periodically (e.g., daily) to aggregate recent trades
        into performance snapshots for fast lookup.

        Args:
            days_back: Time window to aggregate (default 30 days)
        """
        if not self.learning_engine or not PHASE2_AVAILABLE:
            print("Warning: Learning engine not available")
            return

        try:
            self.learning_engine.update_performance_snapshots(days_back)
            print(f"[SIL] Updated performance snapshots ({days_back} day window)")
        except Exception as e:
            print(f"Error updating performance snapshots: {e}")

    def get_session_report(self) -> str:
        """
        Generate human-readable report of session decisions.

        Returns:
            Formatted report string
        """
        if not self.trace_logger or not PHASE2_AVAILABLE:
            return "Transparency layer not available"

        try:
            return self.trace_logger.generate_session_report(self.session_id)
        except Exception as e:
            return f"Error generating session report: {e}"

    def _validate_ohlcv_data(self, ohlcv_data: pd.DataFrame) -> Optional[str]:
        """
        Validate OHLCV data quality and schema.

        Args:
            ohlcv_data: DataFrame with OHLC+V data

        Returns:
            Error message if validation fails, None if valid
        """
        # Check if DataFrame is empty
        if ohlcv_data is None or ohlcv_data.empty:
            return "OHLCV data is empty"

        # Check required columns
        required_columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
        missing_columns = [col for col in required_columns if col not in ohlcv_data.columns]
        if missing_columns:
            return f"Missing required columns: {missing_columns}"

        # Check minimum row count
        if len(ohlcv_data) < 20:
            return f"Insufficient data: {len(ohlcv_data)} rows (minimum 20 required)"

        # Check for NaN values in critical columns
        for col in ['open', 'high', 'low', 'close']:
            if ohlcv_data[col].isna().any():
                nan_count = ohlcv_data[col].isna().sum()
                return f"NaN values in {col} column: {nan_count} rows"

        # Validate data types
        for col in ['open', 'high', 'low', 'close', 'volume']:
            if not pd.api.types.is_numeric_dtype(ohlcv_data[col]):
                return f"Column {col} must be numeric, got {ohlcv_data[col].dtype}"

        # Validate OHLC relationships (high >= low, high >= open/close, low <= open/close)
        invalid_rows = (
            (ohlcv_data['high'] < ohlcv_data['low']) |
            (ohlcv_data['high'] < ohlcv_data['open']) |
            (ohlcv_data['high'] < ohlcv_data['close']) |
            (ohlcv_data['low'] > ohlcv_data['open']) |
            (ohlcv_data['low'] > ohlcv_data['close'])
        )
        if invalid_rows.any():
            return f"Invalid OHLC relationships in {invalid_rows.sum()} rows"

        # Check for negative values
        for col in ['open', 'high', 'low', 'close', 'volume']:
            if (ohlcv_data[col] < 0).any():
                return f"Negative values in {col} column"

        # Check for zeros in price columns (volume can be zero)
        for col in ['open', 'high', 'low', 'close']:
            if (ohlcv_data[col] == 0).any():
                return f"Zero values in {col} column"

        # All validations passed
        return None

    def close(self):
        """
        Close and clean up all SIL components.

        Ensures graceful shutdown by:
        1. Closing trace logger (flushes logs)
        2. Closing Qdrant client (closes connections)
        3. Saving final state

        Call this when shutting down the trading system.
        """
        print("[SIL] Shutting down Strategic Intelligence Layer...")

        # Close trace logger
        if self.trace_logger:
            try:
                self.trace_logger.close()
            except Exception as e:
                print(f"[SIL] Warning: Error closing trace logger: {e}")

        # Close memory client
        if self.memory_client:
            try:
                self.memory_client.close()
            except Exception as e:
                print(f"[SIL] Warning: Error closing memory client: {e}")

        print("[SIL] Shutdown complete")

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
        # Don't suppress exceptions
        return False
