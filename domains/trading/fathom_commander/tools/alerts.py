"""
Fathom Commander - Alert Tools
Notification system for Slack and other channels.
"""

import json
import os
import sys
import urllib.request
from datetime import datetime
from typing import Optional
from dataclasses import dataclass, asdict
from enum import Enum

# Add paths for imports
_this_dir = os.path.dirname(os.path.abspath(__file__))
_parent_dir = os.path.dirname(_this_dir)
sys.path.insert(0, _parent_dir)

try:
    from state import get_state_manager
except ImportError:
    from ..state import get_state_manager


class AlertPriority(Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class AlertType(Enum):
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"
    APPROVAL_REQUEST = "approval_request"


@dataclass
class Alert:
    """Represents an alert/notification."""
    alert_type: str
    priority: str
    title: str
    message: str
    data: Optional[dict] = None
    timestamp: str = ""
    channel: str = "trading"

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.utcnow().isoformat() + "Z"


class SlackNotifier:
    """Handles Slack notifications."""

    def __init__(self, webhook_url: str = None):
        self.webhook_url = webhook_url or os.environ.get("SLACK_WEBHOOK_URL", "")
        self.enabled = bool(self.webhook_url)

    def _get_emoji(self, alert_type: str) -> str:
        """Get emoji for alert type."""
        emojis = {
            "info": ":information_source:",
            "success": ":white_check_mark:",
            "warning": ":warning:",
            "error": ":x:",
            "approval_request": ":question:"
        }
        return emojis.get(alert_type, ":bell:")

    def _get_color(self, alert_type: str) -> str:
        """Get color for Slack attachment."""
        colors = {
            "info": "#2196F3",
            "success": "#4CAF50",
            "warning": "#FF9800",
            "error": "#F44336",
            "approval_request": "#9C27B0"
        }
        return colors.get(alert_type, "#607D8B")

    def send(self, alert: Alert) -> dict:
        """Send alert to Slack."""
        if not self.enabled:
            return {"success": False, "error": "Slack not configured", "alert": asdict(alert)}

        emoji = self._get_emoji(alert.alert_type)
        color = self._get_color(alert.alert_type)

        # Build Slack message
        payload = {
            "channel": f"#{alert.channel}",
            "username": "Fathom Commander",
            "icon_emoji": ":robot_face:",
            "attachments": [
                {
                    "color": color,
                    "fallback": f"{emoji} {alert.title}: {alert.message}",
                    "pretext": f"{emoji} *{alert.title}*" if alert.priority == "urgent" else None,
                    "title": alert.title if alert.priority != "urgent" else None,
                    "text": alert.message,
                    "fields": self._build_fields(alert.data) if alert.data else None,
                    "footer": "Fathom Commander",
                    "ts": int(datetime.utcnow().timestamp())
                }
            ]
        }

        # Remove None values
        payload["attachments"][0] = {k: v for k, v in payload["attachments"][0].items() if v is not None}

        try:
            req = urllib.request.Request(
                self.webhook_url,
                data=json.dumps(payload).encode('utf-8'),
                headers={"Content-Type": "application/json"}
            )
            with urllib.request.urlopen(req, timeout=10) as response:
                return {"success": True, "sent": True}

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _build_fields(self, data: dict) -> list:
        """Build Slack fields from data dict."""
        fields = []
        for key, value in data.items():
            fields.append({
                "title": key.replace("_", " ").title(),
                "value": str(value),
                "short": len(str(value)) < 20
            })
        return fields

    def send_approval_request(
        self,
        approval_id: str,
        pair: str,
        side: str,
        volume: float,
        estimated_usd: float,
        reasoning: str,
        hypothesis: str
    ) -> dict:
        """Send approval request to Slack with interactive buttons."""
        if not self.enabled:
            return {"success": False, "error": "Slack not configured"}

        # Build interactive message
        payload = {
            "channel": "#trading",
            "username": "Fathom Commander",
            "icon_emoji": ":robot_face:",
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": ":question: Trade Approval Required",
                        "emoji": True
                    }
                },
                {
                    "type": "section",
                    "fields": [
                        {"type": "mrkdwn", "text": f"*Pair:*\n{pair}"},
                        {"type": "mrkdwn", "text": f"*Side:*\n{side.upper()}"},
                        {"type": "mrkdwn", "text": f"*Volume:*\n{volume}"},
                        {"type": "mrkdwn", "text": f"*Est. Value:*\n${estimated_usd:.2f}"}
                    ]
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Reasoning:*\n{reasoning}"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Hypothesis:*\n{hypothesis}"
                    }
                },
                {
                    "type": "context",
                    "elements": [
                        {
                            "type": "mrkdwn",
                            "text": f"Approval ID: `{approval_id}` | Expires in 30 minutes"
                        }
                    ]
                },
                {
                    "type": "actions",
                    "elements": [
                        {
                            "type": "button",
                            "text": {"type": "plain_text", "text": "Approve", "emoji": True},
                            "style": "primary",
                            "action_id": f"approve_{approval_id}",
                            "value": approval_id
                        },
                        {
                            "type": "button",
                            "text": {"type": "plain_text", "text": "Reject", "emoji": True},
                            "style": "danger",
                            "action_id": f"reject_{approval_id}",
                            "value": approval_id
                        }
                    ]
                }
            ]
        }

        try:
            req = urllib.request.Request(
                self.webhook_url,
                data=json.dumps(payload).encode('utf-8'),
                headers={"Content-Type": "application/json"}
            )
            with urllib.request.urlopen(req, timeout=10) as response:
                return {"success": True, "sent": True, "approval_id": approval_id}

        except Exception as e:
            return {"success": False, "error": str(e)}


class AlertManager:
    """Manages all alerts and notifications."""

    def __init__(self):
        self.state = get_state_manager()
        self.slack = SlackNotifier()
        self._alert_history: list = []
        self._max_history = 100

    def _record_alert(self, alert: Alert, result: dict):
        """Record alert in history."""
        self._alert_history.append({
            "alert": asdict(alert),
            "result": result,
            "timestamp": alert.timestamp
        })

        # Trim history
        if len(self._alert_history) > self._max_history:
            self._alert_history = self._alert_history[-self._max_history:]

    def send_alert(
        self,
        title: str,
        message: str,
        alert_type: str = "info",
        priority: str = "normal",
        data: dict = None,
        channel: str = "trading"
    ) -> dict:
        """Send an alert."""
        alert = Alert(
            alert_type=alert_type,
            priority=priority,
            title=title,
            message=message,
            data=data,
            channel=channel
        )

        result = self.slack.send(alert)
        self._record_alert(alert, result)

        return {
            "success": result.get("success", False),
            "alert": asdict(alert),
            "slack_sent": result.get("sent", False),
            "error": result.get("error")
        }

    def send_trade_executed(
        self,
        pair: str,
        side: str,
        volume: float,
        price: float,
        txid: str
    ) -> dict:
        """Send trade execution notification."""
        return self.send_alert(
            title="Trade Executed",
            message=f"{side.upper()} {volume} {pair} @ ${price:.2f}",
            alert_type="success",
            priority="normal",
            data={
                "txid": txid,
                "pair": pair,
                "side": side,
                "volume": volume,
                "price": price
            }
        )

    def send_approval_request(
        self,
        approval_id: str,
        pair: str,
        side: str,
        volume: float,
        estimated_usd: float,
        reasoning: str,
        hypothesis: str
    ) -> dict:
        """Send approval request notification."""
        result = self.slack.send_approval_request(
            approval_id, pair, side, volume, estimated_usd, reasoning, hypothesis
        )

        # Also record as regular alert
        alert = Alert(
            alert_type="approval_request",
            priority="high",
            title="Approval Required",
            message=f"{side.upper()} {volume} {pair} (~${estimated_usd:.2f})",
            data={"approval_id": approval_id, "reasoning": reasoning}
        )
        self._record_alert(alert, result)

        return result

    def send_daily_limit_hit(self, limit_type: str, current_value: float, limit: float) -> dict:
        """Alert when daily limit is hit."""
        return self.send_alert(
            title="Daily Limit Reached",
            message=f"{limit_type} limit hit: {current_value:.2f} / {limit:.2f}",
            alert_type="warning",
            priority="high",
            data={
                "limit_type": limit_type,
                "current": current_value,
                "limit": limit
            }
        )

    def send_error_alert(self, error: str, context: str = "") -> dict:
        """Send error notification."""
        return self.send_alert(
            title="Error Occurred",
            message=f"{context}: {error}" if context else error,
            alert_type="error",
            priority="urgent"
        )

    def send_position_closed(
        self,
        pair: str,
        pnl: float,
        exit_reason: str
    ) -> dict:
        """Alert when position is closed."""
        alert_type = "success" if pnl >= 0 else "warning"
        pnl_str = f"+${pnl:.2f}" if pnl >= 0 else f"-${abs(pnl):.2f}"

        return self.send_alert(
            title="Position Closed",
            message=f"{pair}: {pnl_str} ({exit_reason})",
            alert_type=alert_type,
            priority="normal",
            data={
                "pair": pair,
                "pnl": pnl,
                "exit_reason": exit_reason
            }
        )

    def get_alert_history(self, limit: int = 20) -> list:
        """Get recent alert history."""
        return self._alert_history[-limit:]

    def is_slack_configured(self) -> bool:
        """Check if Slack is configured."""
        return self.slack.enabled


# Singleton instance
_alert_manager: Optional[AlertManager] = None


def get_alert_manager() -> AlertManager:
    """Get or create alert manager singleton."""
    global _alert_manager
    if _alert_manager is None:
        _alert_manager = AlertManager()
    return _alert_manager


# =========================
# Tool Functions
# =========================

def alert_send(
    title: str,
    message: str,
    alert_type: str = "info",
    priority: str = "normal"
) -> dict:
    """Send a general alert."""
    manager = get_alert_manager()
    return manager.send_alert(title, message, alert_type, priority)


def alert_trade_executed(
    pair: str,
    side: str,
    volume: float,
    price: float,
    txid: str
) -> dict:
    """Send trade execution alert."""
    manager = get_alert_manager()
    return manager.send_trade_executed(pair, side, volume, price, txid)


def alert_approval_request(
    approval_id: str,
    pair: str,
    side: str,
    volume: float,
    estimated_usd: float,
    reasoning: str,
    hypothesis: str
) -> dict:
    """Send approval request to Captain."""
    manager = get_alert_manager()
    return manager.send_approval_request(
        approval_id, pair, side, volume, estimated_usd, reasoning, hypothesis
    )


def alert_error(error: str, context: str = "") -> dict:
    """Send error alert."""
    manager = get_alert_manager()
    return manager.send_error_alert(error, context)


def alert_history(limit: int = 20) -> dict:
    """Get recent alert history."""
    manager = get_alert_manager()
    return {
        "success": True,
        "alerts": manager.get_alert_history(limit),
        "slack_configured": manager.is_slack_configured()
    }


def alert_status() -> dict:
    """Get alert system status."""
    manager = get_alert_manager()
    return {
        "success": True,
        "slack_configured": manager.is_slack_configured(),
        "alerts_in_history": len(manager._alert_history),
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
