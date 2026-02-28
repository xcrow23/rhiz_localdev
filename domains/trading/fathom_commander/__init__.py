"""
Fathom Commander
Claude Code's Trading Command Center

An MCP server providing trading tools with safety limits,
approval workflows, and n8n heartbeat monitoring.
"""

__version__ = "1.0.0"
__author__ = "Rhiz Partnership (Captain & First Mate)"

from .state import get_state_manager, StateManager
from .state import Position, PendingApproval, TradeRecord, DailyStats, CommanderState
