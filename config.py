from typing import Dict, Any

# 1. Routing Table: Maps category -> targeted operational team & slack channel
ROUTING_TABLE: Dict[str, Dict[str, str]] = {
    "database": {
        "team": "Database Reliability Engineering",
        "channel": "#db-ops",
        "on_call_pager": "pagerduty-db-primary"
    },
    "account_access": {
        "team": "Identity & Access Management",
        "channel": "#sec-ops",
        "on_call_pager": "pagerduty-iam-primary"
    },
    "billing": {
        "team": "Finance Operations",
        "channel": "#billing-support",
        "on_call_pager": "email-billing-lead"
    },
    "network": {
        "team": "Core Infrastructure & Networking",
        "channel": "#net-ops",
        "on_call_pager": "pagerduty-net-primary"
    },
    "other": {
        "team": "Tier-1 Support Operations",
        "channel": "#general-support",
        "on_call_pager": "slack-notify-triage"
    }
}

# 2. SLA Matrix: Maps urgency level -> maximum allowed response time (in minutes)
SLA_MATRIX_MINUTES: Dict[str, int] = {
    "critical": 15,    # 15-minute SLA threshold for P0 incidents
    "high": 60,        # 1-hour SLA threshold for P1 incidents
    "medium": 240,     # 4-hour SLA threshold for P2 requests
    "low": 1440        # 24-hour SLA threshold for P3 requests
}

def get_routing_info(category: str, urgency_level: str) -> Dict[str, Any]:
    """
    Returns the target team, target notification channel, on-call pager reference,
    and SLA response limit in minutes for a given ticket.
    """
    # Default to 'other' if an unexpected category is supplied
    route = ROUTING_TABLE.get(category, ROUTING_TABLE["other"])
    
    # Default to 'low' if an unexpected urgency level is supplied
    sla_minutes = SLA_MATRIX_MINUTES.get(urgency_level, SLA_MATRIX_MINUTES["low"])
    
    return {
        "team": route["team"],
        "channel": route["channel"],
        "on_call_pager": route["on_call_pager"],
        "sla_minutes": sla_minutes
    }


if __name__ == "__main__":
    # Quick sanity check
    sample_route = get_routing_info(category="database", urgency_level="critical")
    print("--- SAMPLE ROUTING CONFIGURATION ---")
    print(f"Target Team:   {sample_route['team']}")
    print(f"Target Channel: {sample_route['channel']}")
    print(f"On-Call Pager:  {sample_route['on_call_pager']}")
    print(f"SLA Window:     {sample_route['sla_minutes']} minutes")