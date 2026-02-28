"""
TRACE_FE Logger - Transparency Layer for Strategic Intelligence

Implements SynLang TRACE_FE Protocol:
- Factor-based explanations with confidence weights
- Full reasoning chains for all decisions
- Decision logging for retrospective analysis
- Human-readable formatted output

Every decision made by SIL includes:
1. What action was taken
2. Why that action was chosen (primary reasoning)
3. What alternatives were considered
4. What factors influenced the decision (with confidence)
5. What risks were identified
"""

from typing import List, Dict, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from pathlib import Path
import json
import os


@dataclass
class TraceFactor:
    """
    Individual factor contributing to a decision.

    Follows TRACE_FE format: factor + explanation + confidence
    """
    factor: str  # e.g., "regime_match", "risk_check_passed"
    explanation: str  # Human-readable explanation
    confidence: float  # 0.0 to 1.0
    value: Optional[str] = None  # Optional numeric/string value


@dataclass
class DecisionTrace:
    """
    Complete decision trace with full transparency.

    This is what gets logged for every SIL decision.
    """
    # Decision metadata
    decision_id: str
    timestamp: datetime
    decision_type: str  # "strategy_selection", "position_sizing", "risk_check"

    # Decision outcome
    action: str  # "activate_strategy", "wait", "enter_long", etc.
    confidence: float

    # Reasoning
    primary_reasoning: str
    secondary_reasoning: str
    risk_assessment: str

    # TRACE factors
    trace_factors: List[TraceFactor]

    # Alternatives considered
    alternatives: List[Dict]

    # Context snapshot
    market_context: Dict
    portfolio_state: Optional[Dict] = None

    # Session tracking
    session_id: Optional[str] = None


class TraceLogger:
    """
    Logger for TRACE_FE transparency.

    Logs all decisions to:
    1. JSON files (for archival and analysis)
    2. Memory (Qdrant decision_log collection)
    3. Console (for real-time Captain monitoring)
    """

    def __init__(
        self,
        log_dir: Optional[str] = None,
        console_output: bool = True,
        memory_client: Optional['QdrantMemoryClient'] = None,
        log_retention_days: int = 30
    ):
        """
        Initialize TRACE logger.

        Args:
            log_dir: Directory for JSON log files (default: from LOG_DIR env var or transparency/logs/)
            console_output: Enable console logging (default: True)
            memory_client: QdrantMemoryClient for persistent logging
            log_retention_days: Number of days to keep log files (default: 30, from LOG_RETENTION_DAYS env var)
        """
        if log_dir is None:
            # Try to get from environment variable first
            log_dir = os.getenv('LOG_DIR')
            if log_dir is None:
                # Fall back to default location
                log_dir = Path(__file__).parent / "logs"

        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)

        self.console_output = console_output
        self.memory = memory_client

        # Log rotation settings
        retention_env = os.getenv('LOG_RETENTION_DAYS')
        if retention_env:
            try:
                self.log_retention_days = int(retention_env)
            except ValueError:
                self.log_retention_days = log_retention_days
        else:
            self.log_retention_days = log_retention_days

        # Session tracking
        self.current_session_id: Optional[str] = None
        self.decision_count = 0

    def start_session(self, session_id: str):
        """
        Start a new trading session for decision tracking.

        Args:
            session_id: Unique session identifier
        """
        self.current_session_id = session_id
        self.decision_count = 0
        print(f"[TRACE] Started session: {session_id}")

        # Clean up old log files
        self._cleanup_old_logs()

    def _cleanup_old_logs(self):
        """
        Remove log files older than retention period.

        Keeps logs for the configured retention period (default 30 days).
        This prevents disk fill from indefinite log accumulation.
        """
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=self.log_retention_days)
            deleted_count = 0

            # Find all trace log files
            for log_file in self.log_dir.glob("trace_*.jsonl"):
                try:
                    # Extract date from filename (format: trace_YYYY-MM-DD.jsonl)
                    date_str = log_file.stem.replace("trace_", "")
                    file_date = datetime.strptime(date_str, "%Y-%m-%d")

                    # Delete if older than cutoff
                    if file_date < cutoff_date:
                        log_file.unlink()
                        deleted_count += 1

                except (ValueError, OSError) as e:
                    # Skip files that don't match expected format or can't be deleted
                    print(f"[TRACE] Warning: Could not process log file {log_file.name}: {e}")
                    continue

            if deleted_count > 0:
                print(f"[TRACE] Cleaned up {deleted_count} old log files (retention: {self.log_retention_days} days)")

        except Exception as e:
            # Don't fail session start if cleanup fails
            print(f"[TRACE] Warning: Log cleanup failed: {e}")

    def log_decision(
        self,
        decision_trace: DecisionTrace,
        store_in_memory: bool = True
    ):
        """
        Log a decision with full TRACE_FE transparency.

        Args:
            decision_trace: DecisionTrace object
            store_in_memory: Store in Qdrant memory (default: True)
        """
        # Increment counter
        self.decision_count += 1

        # Add session ID if not set
        if not decision_trace.session_id and self.current_session_id:
            decision_trace.session_id = self.current_session_id

        # 1. Console output (real-time monitoring)
        if self.console_output:
            self._print_trace(decision_trace)

        # 2. JSON file (archival)
        self._save_to_json(decision_trace)

        # 3. Memory (Qdrant)
        if store_in_memory and self.memory:
            self._save_to_memory(decision_trace)

    def _print_trace(self, trace: DecisionTrace):
        """Print formatted TRACE to console."""
        print("\n" + "="*70)
        print(f"[DECISION #{self.decision_count}] {trace.decision_type.upper()}")
        print(f"Time: {trace.timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')}")
        print(f"Decision ID: {trace.decision_id}")
        print("="*70)

        # Action
        print(f"\n🎯 ACTION: {trace.action}")
        print(f"   Confidence: {trace.confidence:.1%}")

        # Reasoning
        print(f"\n💡 PRIMARY REASONING:")
        print(f"   {trace.primary_reasoning}")

        if trace.secondary_reasoning:
            print(f"\n   Secondary: {trace.secondary_reasoning}")

        # Risk assessment
        if trace.risk_assessment:
            print(f"\n⚠️  RISK ASSESSMENT:")
            print(f"   {trace.risk_assessment}")

        # TRACE factors
        if trace.trace_factors:
            print(f"\n📊 TRACE FACTORS:")
            for factor in trace.trace_factors:
                confidence_bar = "█" * int(factor.confidence * 10) + "░" * (10 - int(factor.confidence * 10))
                print(f"   [{confidence_bar}] {factor.confidence:.1%} - {factor.factor}")
                print(f"      {factor.explanation}")
                if factor.value:
                    print(f"      Value: {factor.value}")

        # Alternatives
        if trace.alternatives:
            print(f"\n🔄 ALTERNATIVES CONSIDERED:")
            for i, alt in enumerate(trace.alternatives[:3], 1):  # Show top 3
                print(f"   {i}. {alt.get('strategy', alt.get('action', 'Unknown'))}")
                if 'confidence' in alt:
                    print(f"      Confidence: {alt['confidence']:.1%}")

        # Market context (abbreviated)
        if trace.market_context:
            print(f"\n🌐 MARKET CONTEXT:")
            regime = trace.market_context.get('regime', 'unknown')
            vol_regime = trace.market_context.get('volatility_regime', 'unknown')
            sentiment = trace.market_context.get('sentiment_direction', 'unknown')
            print(f"   Regime: {regime} (vol: {vol_regime}, sentiment: {sentiment})")

        print("="*70 + "\n")

    def _save_to_json(self, trace: DecisionTrace):
        """Save decision trace to JSON file."""
        # Create dated filename
        date_str = trace.timestamp.strftime("%Y-%m-%d")
        log_file = self.log_dir / f"trace_{date_str}.jsonl"

        # Convert to dict
        trace_dict = asdict(trace)

        # Handle datetime serialization
        trace_dict['timestamp'] = trace.timestamp.isoformat()

        # Handle TraceFactor objects
        trace_dict['trace_factors'] = [
            {
                'factor': f.factor,
                'explanation': f.explanation,
                'confidence': f.confidence,
                'value': f.value
            }
            for f in trace.trace_factors
        ]

        # Append to JSONL file (one decision per line)
        with open(log_file, 'a') as f:
            f.write(json.dumps(trace_dict) + '\n')

    def _save_to_memory(self, trace: DecisionTrace):
        """Save decision trace to Qdrant memory."""
        if not self.memory:
            return

        # TODO Phase 2.5: Generate embedding for decision context
        # For now, use placeholder
        import numpy as np
        embedding = np.random.randn(128).astype(np.float32)

        # Log to Qdrant
        self.memory.log_decision(
            decision_id=trace.decision_id,
            session_id=trace.session_id or "unknown",
            action=trace.action,
            strategy_name=trace.market_context.get('active_strategy'),
            confidence=trace.confidence,
            market_regime=trace.market_context.get('regime', 'unknown'),
            reasoning=trace.primary_reasoning,
            risk_check_passed=trace.action != "wait",
            embedding=embedding
        )

    # ========================================
    # Analysis & Reporting
    # ========================================

    def get_session_decisions(self, session_id: str) -> List[DecisionTrace]:
        """
        Retrieve all decisions from a session.

        Args:
            session_id: Session ID to retrieve

        Returns:
            List of DecisionTrace objects
        """
        # Load from JSON files
        decisions = []

        for log_file in self.log_dir.glob("trace_*.jsonl"):
            with open(log_file, 'r') as f:
                for line in f:
                    trace_dict = json.loads(line)
                    if trace_dict.get('session_id') == session_id:
                        # Reconstruct DecisionTrace
                        trace_dict['timestamp'] = datetime.fromisoformat(trace_dict['timestamp'])
                        trace_dict['trace_factors'] = [
                            TraceFactor(**f) for f in trace_dict['trace_factors']
                        ]
                        decisions.append(DecisionTrace(**trace_dict))

        return decisions

    def generate_session_report(self, session_id: str) -> str:
        """
        Generate human-readable report of session decisions.

        Args:
            session_id: Session ID

        Returns:
            Formatted report string
        """
        decisions = self.get_session_decisions(session_id)

        if not decisions:
            return f"No decisions found for session {session_id}"

        report = []
        report.append(f"\n{'='*70}")
        report.append(f"SESSION REPORT: {session_id}")
        report.append(f"{'='*70}")
        report.append(f"Total Decisions: {len(decisions)}")
        report.append("")

        # Action breakdown
        actions = {}
        for d in decisions:
            actions[d.action] = actions.get(d.action, 0) + 1

        report.append("ACTION BREAKDOWN:")
        for action, count in actions.items():
            report.append(f"  {action}: {count}")

        # Average confidence
        avg_confidence = sum(d.confidence for d in decisions) / len(decisions)
        report.append(f"\nAverage Confidence: {avg_confidence:.1%}")

        # Decision timeline
        report.append(f"\nDECISION TIMELINE:")
        for i, d in enumerate(decisions, 1):
            time_str = d.timestamp.strftime("%H:%M:%S")
            report.append(f"  {i}. [{time_str}] {d.action} (confidence: {d.confidence:.1%})")
            report.append(f"     {d.primary_reasoning}")

        report.append(f"\n{'='*70}\n")

        return "\n".join(report)

    def analyze_decision_quality(
        self,
        session_id: str,
        actual_outcomes: Optional[List[Dict]] = None
    ) -> Dict:
        """
        Analyze quality of decisions in retrospect.

        Compares predicted confidence with actual outcomes.

        Args:
            session_id: Session ID
            actual_outcomes: List of actual trade outcomes (optional)

        Returns:
            Analysis dict with calibration metrics
        """
        decisions = self.get_session_decisions(session_id)

        if not decisions:
            return {"error": "No decisions found"}

        analysis = {
            "total_decisions": len(decisions),
            "action_breakdown": {},
            "avg_confidence": sum(d.confidence for d in decisions) / len(decisions),
            "confidence_distribution": {
                "high (>0.8)": 0,
                "medium (0.6-0.8)": 0,
                "low (<0.6)": 0
            }
        }

        # Action breakdown
        for d in decisions:
            action = d.action
            analysis["action_breakdown"][action] = analysis["action_breakdown"].get(action, 0) + 1

            # Confidence distribution
            if d.confidence > 0.8:
                analysis["confidence_distribution"]["high (>0.8)"] += 1
            elif d.confidence >= 0.6:
                analysis["confidence_distribution"]["medium (0.6-0.8)"] += 1
            else:
                analysis["confidence_distribution"]["low (<0.6)"] += 1

        # If outcomes provided, calculate calibration
        if actual_outcomes:
            # Match decisions to outcomes
            # TODO: Implement outcome matching logic
            pass

        return analysis

    def log_event(self, event: Dict):
        """
        Log a miscellaneous event (non-decision).

        Used for logging system events like circuit breaker overrides,
        configuration changes, etc.

        Args:
            event: Dictionary with event details (must include 'event' and 'timestamp' keys)
        """
        if 'event' not in event or 'timestamp' not in event:
            raise ValueError("Event must include 'event' and 'timestamp' keys")

        # Get log file for today
        today = datetime.utcnow().strftime("%Y-%m-%d")
        log_file = self.log_dir / f"events_{today}.jsonl"

        # Append to JSONL file
        with open(log_file, 'a') as f:
            f.write(json.dumps(event) + '\n')

        # Also log to console if enabled
        if self.console_output:
            print(f"[EVENT] {event.get('event')}: {event.get('reason', 'N/A')}")

    def close(self):
        """
        Close the trace logger and clean up resources.

        Currently a no-op since we use immediate file writes with context managers,
        but provided for future-proofing and consistency with resource management patterns.
        """
        # No persistent file handles to close (we use 'with open()' for each write)
        # This method exists for future-proofing if we add buffering or persistent connections
        pass

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
        # Don't suppress exceptions
        return False


# ========================================
# Helper Functions
# ========================================

def format_trace_factors(factors: List[TraceFactor]) -> str:
    """
    Format TRACE factors for display.

    Returns multi-line string with formatted factors.
    """
    lines = []
    for factor in factors:
        confidence_bar = "█" * int(factor.confidence * 10) + "░" * (10 - int(factor.confidence * 10))
        lines.append(f"[{confidence_bar}] {factor.confidence:.1%} - {factor.factor}")
        lines.append(f"   {factor.explanation}")
        if factor.value:
            lines.append(f"   Value: {factor.value}")
    return "\n".join(lines)


def create_trace_from_strategy_decision(
    decision: 'StrategyDecision',
    decision_id: str,
    session_id: Optional[str] = None
) -> DecisionTrace:
    """
    Convert StrategyDecision to DecisionTrace format.

    Args:
        decision: StrategyDecision from strategy selector
        decision_id: Unique decision ID
        session_id: Session ID (optional)

    Returns:
        DecisionTrace object
    """
    # Convert trace factors
    trace_factors = [
        TraceFactor(
            factor=f['factor'],
            explanation=f['explanation'],
            confidence=f['confidence'],
            value=f.get('value')
        )
        for f in decision.trace_factors
    ]

    return DecisionTrace(
        decision_id=decision_id,
        timestamp=decision.timestamp,
        decision_type="strategy_selection",
        action=decision.action,
        confidence=decision.confidence,
        primary_reasoning=decision.reasoning['primary'],
        secondary_reasoning=decision.reasoning.get('secondary', ''),
        risk_assessment=decision.reasoning.get('risk_assessment', ''),
        trace_factors=trace_factors,
        alternatives=decision.alternatives,
        market_context=decision.market_context_snapshot,
        session_id=session_id
    )


def create_trace_from_position_size(
    position_size: 'PositionSize',
    decision_id: str,
    action: str,
    market_context: Dict,
    session_id: Optional[str] = None
) -> DecisionTrace:
    """
    Convert PositionSize to DecisionTrace format.

    Args:
        position_size: PositionSize from risk manager
        decision_id: Unique decision ID
        action: Action taken ("enter_long", "position_rejected", etc.)
        market_context: Market context snapshot
        session_id: Session ID (optional)

    Returns:
        DecisionTrace object
    """
    # Convert trace factors
    trace_factors = [
        TraceFactor(
            factor=f['factor'],
            explanation=f['explanation'],
            confidence=f['confidence'],
            value=f.get('value')
        )
        for f in position_size.trace_factors
    ]

    # Determine confidence based on whether position was approved
    confidence = 0.9 if position_size.size_btc > 0 else 0.1

    return DecisionTrace(
        decision_id=decision_id,
        timestamp=datetime.utcnow(),
        decision_type="position_sizing",
        action=action,
        confidence=confidence,
        primary_reasoning=position_size.reasoning,
        secondary_reasoning=f"Position size: {position_size.size_btc:.6f} BTC (${position_size.size_usd:.2f})",
        risk_assessment=position_size.reasoning if not position_size.approved else "Risk checks passed",
        trace_factors=trace_factors,
        alternatives=[],
        market_context=market_context,
        portfolio_state={
            "position_approved": position_size.approved,
            "risk_percent": position_size.risk_percent
        },
        session_id=session_id
    )
