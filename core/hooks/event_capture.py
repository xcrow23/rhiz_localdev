#!/usr/bin/env python3
"""
Event Capture Hook

Captures significant events during sessions for:
- Pattern usage tracking
- Metric collection
- Learning extraction

Future enhancement: Feed into observability dashboard
"""

import sys
import os
import json
from datetime import datetime
from pathlib import Path

# Add tools directory to path to import DyadState
RHIZ_ROOT = Path(os.environ.get("RHIZ_ROOT", Path(__file__).parent.parent.parent))
sys.path.insert(0, str(RHIZ_ROOT / "tools" / "rhiz-mcp" / "src"))

from dyad_state import DyadState


def capture_event(event_data):
    """Capture and process an event"""
    try:
        timestamp = datetime.now().isoformat()

        # Log event for now (future: write to event log, update metrics)
        print(f"[event_capture] {event_data.get('type', 'unknown')}")
        print(f"  Timestamp: {timestamp}")
        print(f"  Data: {json.dumps(event_data, indent=2)}")

        # If this is a pattern invocation, increment pattern usage metric
        if event_data.get('pattern'):
            dyad = DyadState()
            dyad.increment_metric('pattern_usage_count')
            print(f"[event_capture] Pattern invoked: {event_data['pattern']}")

        # If this is a tool call to rhiz-mcp, track it
        if event_data.get('tool', '').startswith('rhiz_'):
            print(f"[event_capture] Dyad tool used: {event_data['tool']}")

        return True

    except Exception as e:
        print(f"[event_capture] Error: {e}", file=sys.stderr)
        return False


if __name__ == "__main__":
    # Parse event data from args or stdin
    event_data = {}

    if len(sys.argv) > 1:
        # Event data passed as JSON argument
        try:
            event_data = json.loads(sys.argv[1])
        except json.JSONDecodeError:
            print("[event_capture] Invalid event data JSON", file=sys.stderr)
            sys.exit(1)
    else:
        # Default minimal event
        event_data = {
            "type": "unknown",
            "timestamp": datetime.now().isoformat()
        }

    # Execute
    success = capture_event(event_data)
    sys.exit(0 if success else 1)
