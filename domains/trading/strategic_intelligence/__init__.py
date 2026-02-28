"""
Strategic Intelligence Layer (SIL)
Rhiz Trading Intelligence Core

Phase 1 Complete:
- Market Context Engine
- Strategy Selection
- Risk Management
- Position Sizing

Usage:
    from strategic_intelligence import SILOrchestrator

    sil = SILOrchestrator()
    decision = sil.analyze_and_decide(ohlcv_data, current_price, portfolio_state)
"""

__version__ = "1.0.0"
__author__ = "Rhiz Dyad (Captain + First Mate)"

from .sil_orchestrator import SILOrchestrator, SILDecision

__all__ = ['SILOrchestrator', 'SILDecision']
