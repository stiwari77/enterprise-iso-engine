from datetime import datetime, timezone, timedelta
from state import IncidentTicket, TicketStatus


def process_and_route_ticket(ticket: IncidentTicket) -> IncidentTicket:
    """
    Initializes routing for an incoming ticket based on category and urgency.
    """
    if ticket.status == TicketStatus.UNASSIGNED:
        ticket.assign_routing()
    return ticket


def check_and_escalate_sla(ticket: IncidentTicket, simulated_now: datetime = None) -> IncidentTicket:
    """
    Evaluates whether a ticket has breached its SLA response window or requires
    immediate escalation due to critical urgency.
    """
    now = simulated_now or datetime.now(timezone.utc)
    
    # 1. Immediate escalation rule for critical incidents
    if ticket.extraction_data.urgency_level == "critical" and ticket.status != TicketStatus.ESCALATED:
        ticket.transition_to(
            TicketStatus.ESCALATED,
            reason=f"AUTOMATIC ESCALATION: Critical urgency incident requires immediate executive on-call page."
        )
        return ticket

    # 2. SLA Breach Rule: Check if elapsed time exceeds SLA window
    if ticket.sla_minutes:
        elapsed_minutes = (now - ticket.created_at).total_seconds() / 60.0
        if elapsed_minutes > ticket.sla_minutes and ticket.status not in [TicketStatus.RESOLVED, TicketStatus.ESCALATED]:
            ticket.transition_to(
                TicketStatus.ESCALATED,
                reason=f"SLA BREACH ESCALATION: Ticket unhandled after {int(elapsed_minutes)}m (SLA Limit: {ticket.sla_minutes}m)."
            )

    return ticket


if __name__ == "__main__":
    from schemas import TicketExtraction

    # Test Case 1: Critical Ticket Auto-Escalation
    critical_payload = TicketExtraction(
        category="database",
        urgency_level="critical",
        requested_actions=["db_restart"],
        summary="Database cluster node down."
    )
    
    ticket = IncidentTicket(extraction_data=critical_payload)
    ticket = process_and_route_ticket(ticket)
    ticket = check_and_escalate_sla(ticket)
    
    print("--- TEST CASE 1: CRITICAL AUTO-ESCALATION ---")
    print(f"Ticket ID: {ticket.ticket_id}")
    print(f"Status:    {ticket.status}")
    print(f"Reason:    {ticket.history[-1].reason}\n")

    # Test Case 2: SLA Time Breach Escalation
    medium_payload = TicketExtraction(
        category="billing",
        urgency_level="medium",
        requested_actions=["refund_request"],
        summary="User double charged for subscription."
    )
    
    ticket_sla = IncidentTicket(extraction_data=medium_payload)
    ticket_sla = process_and_route_ticket(ticket_sla)
    
    # Simulate time 5 hours (300 mins) into the future (over the 240 min SLA limit)
    simulated_future_time = ticket_sla.created_at + timedelta(minutes=300)
    ticket_sla = check_and_escalate_sla(ticket_sla, simulated_now=simulated_future_time)

    print("--- TEST CASE 2: SLA BREACH ESCALATION ---")
    print(f"Ticket ID: {ticket_sla.ticket_id}")
    print(f"Status:    {ticket_sla.status}")
    print(f"Reason:    {ticket_sla.history[-1].reason}")