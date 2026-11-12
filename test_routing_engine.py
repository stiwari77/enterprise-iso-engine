import pytest
from datetime import datetime, timezone, timedelta
from schemas import TicketExtraction
from state import IncidentTicket, TicketStatus
from router import process_and_route_ticket, check_and_escalate_sla
from actions import execute_ticket_workflow


def test_end_to_end_critical_incident_remediation():
    """Verify that a critical database incident routes, escalates, remediates, and resolves automatically."""
    payload = TicketExtraction(
        category="database",
        urgency_level="critical",
        requested_actions=["db_restart"],
        summary="Production DB crashing."
    )
    
    ticket = IncidentTicket(extraction_data=payload)
    ticket = process_and_route_ticket(ticket)
    
    assert ticket.status == TicketStatus.ROUTED
    assert ticket.target_team == "Database Reliability Engineering"
    assert ticket.target_channel == "#db-ops"
    assert ticket.sla_minutes == 15
    
    ticket = check_and_escalate_sla(ticket)
    assert ticket.status == TicketStatus.ESCALATED
    
    ticket = execute_ticket_workflow(ticket)
    assert ticket.status == TicketStatus.ESCALATED
    assert len(ticket.history) == 2


def test_sla_time_breach_escalation():
    """Verify that a non-critical ticket escalates when time exceeds the SLA limit."""
    payload = TicketExtraction(
        category="billing",
        urgency_level="medium",
        requested_actions=[],
        summary="User payment dispute."
    )
    
    ticket = IncidentTicket(extraction_data=payload)
    ticket = process_and_route_ticket(ticket)
    
    assert ticket.status == TicketStatus.ROUTED
    assert ticket.sla_minutes == 240  # 4 hours
    
    # Simulate time 5 hours (300 mins) into the future
    future_time = ticket.created_at + timedelta(minutes=300)
    ticket = check_and_escalate_sla(ticket, simulated_now=future_time)
    
    assert ticket.status == TicketStatus.ESCALATED
    assert "SLA BREACH ESCALATION" in ticket.history[-1].reason


def test_unhandled_category_defaults_to_tier1():
    """Verify that unrecognized ticket categories cleanly route to general support."""
    payload = TicketExtraction(
        category="other",
        urgency_level="low",
        requested_actions=[],
        summary="General question regarding service access."
    )
    
    ticket = IncidentTicket(extraction_data=payload)
    ticket = process_and_route_ticket(ticket)
    
    assert ticket.target_team == "Tier-1 Support Operations"
    assert ticket.target_channel == "#general-support"
    assert ticket.sla_minutes == 1440  # 24 hours