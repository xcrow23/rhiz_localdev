"""
Transparency Module - TRACE_FE Logging and Decision Transparency

Provides:
- Comprehensive decision logging with TRACE_FE protocol
- Human-readable formatted output for Captain review
- Decision history tracking and analysis
- Retrospective decision quality analysis
"""

from transparency.trace_logger import (
    TraceLogger,
    TraceFactor,
    DecisionTrace,
    format_trace_factors,
    create_trace_from_strategy_decision,
    create_trace_from_position_size
)

__all__ = [
    'TraceLogger',
    'TraceFactor',
    'DecisionTrace',
    'format_trace_factors',
    'create_trace_from_strategy_decision',
    'create_trace_from_position_size'
]
