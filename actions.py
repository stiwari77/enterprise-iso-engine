import os
import requests
from typing import Any
from state import TicketStatus

# Load webhook endpoints from environment variables (or fallback to placeholders)
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL", "https://hooks.slack.com/services/T00/B00/X00")
PAGER_WEBHOOK_URL = os.getenv("PAGER_WEBHOOK_URL", "https://events.pagerduty.com/v2/enqueue")

def send_slack_notification(channel: str, message: str) -> bool:
    """
    Sends a real-time notification to a Slack channel via Webhook.
    """
    payload = {
        "channel": channel,
        "text": message,
        "username": "IncidentOpsBot",
        "icon_emoji": ":rotating_light:"
    }
    
    # If using placeholder URL, simulate success during tests
    if "hooks.slack.com" in SLACK_WEBHOOK_URL and "T00" in SLACK_WEBHOOK_URL:
        print(f"[Mock Slack Webhook -> {channel}]: {message}")
        return True

    try:
        response = requests.post(SLACK_WEBHOOK_URL, json=payload, timeout=5)
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        print(f"Failed to dispatch Slack webhook: {str(e)}")
        return False


def trigger_pager_alert(pager_target: str, urgency: str, summary: str) -> bool:
    """
    Triggers a live on-call alert via PagerDuty or an equivalent alerting webhook.
    """
    payload = {
        "routing_key": pager_target,
        "event_action": "trigger",
        "payload": {
            "summary": summary,
            "severity": urgency.lower() if urgency in ["CRITICAL", "HIGH"] else "warning",
            "source": "Enterprise-ISO-Engine"
        }
    }

    if "pagerduty.com" in PAGER_WEBHOOK_URL and "v2" in PAGER_WEBHOOK_URL:
        print(f"[Mock Pager Alert -> {pager_target}]: {summary}")
        return True

    try:
        response = requests.post(PAGER_WEBHOOK_URL, json=payload, timeout=5)
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        print(f"Failed to trigger pager alert: {str(e)}")
        return False


def execute_ticket_workflow(ticket: Any) -> Any:
    """
    Executes automated actions based on ticket routing and urgency rules.
    """
    # 1. Dispatch Slack Notification if a target channel is assigned
    if ticket.target_channel:
        slack_msg = (
            f"*New Incident Ticket Created*\n"
            f"> *ID:* `{ticket.ticket_id}`\n"
            f"> *Status:* `{ticket.status.value}`\n"
            f"> *Team:* `{ticket.target_team}`\n"
            f"> *SLA:* `{ticket.sla_minutes} mins`"
        )
        send_slack_notification(ticket.target_channel, slack_msg)

    # 2. Trigger Pager Alert if urgency is high/critical and an on-call pager is assigned
    if ticket.extraction_data.urgency_level in ["HIGH", "CRITICAL"] and ticket.on_call_pager:
        trigger_pager_alert(
            pager_target=ticket.on_call_pager,
            urgency=ticket.extraction_data.urgency_level,
            summary=ticket.extraction_data.summary
        )

    return ticket