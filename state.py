import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field
from schemas import TicketExtraction
from config import get_routing_info


class TicketStatus(str, Enum):
    UNASSIGNED = "UNASSIGNED"
    ROUTED = "ROUTED"
    IN_PROGRESS = "IN_PROGRESS"
    ESCALATED = "ESCALATED"
    RESOLVED = "RESOLVED"


class StatusAuditLog(BaseModel):
    previous_status: TicketStatus
    new_status: TicketStatus
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    reason: str


class IncidentTicket(BaseModel):
    ticket_id: str = Field(default_factory=lambda: f"INC-{uuid.uuid4().hex[:8].upper()}")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    status: TicketStatus = TicketStatus.UNASSIGNED
    
    # Extracted LLM payload
    extraction_data: TicketExtraction
    
    # Routing & SLA metadata
    target_team: Optional[str] = None
    target_channel: Optional[str] = None
    on_call_pager: Optional[str] = None
    sla_minutes: Optional[int] = None
    
    # Audit trail
    history: List[StatusAuditLog] = Field(default_factory=list)

    def transition_to(self, new_status: TicketStatus, reason: str):
        """Transitions the ticket to a new state and records an audit log entry."""
        log_entry = StatusAuditLog(
            previous_status=self.status,
            new_status=new_status,
            reason=reason
        )
        self.status = new_status
        self.history.append(log_entry)

    def assign_routing(self):
        """Populates routing details based on category and urgency level."""
        route_info = get_routing_info(
            category=self.extraction_data.category,
            urgency_level=self.extraction_data.urgency_level
        )
        self.target_team = route_info["team"]
        self.target_channel = route_info["channel"]
        self.on_call_pager = route_info["on_call_pager"]
        self.sla_minutes = route_info["sla_minutes"]
        
        self.transition_to(
            TicketStatus.ROUTED, 
            reason=f"Routed to {self.target_team} ({self.target_channel}) with {self.sla_minutes}m SLA."
        )


if __name__ == "__main__":
    # Test state lifecycle
    sample_extraction = TicketExtraction(
        category="database",
        urgency_level="critical",
        requested_actions=["db_restart"],
        summary="PostgreSQL node down."
    )
    
    ticket = IncidentTicket(extraction_data=sample_extraction)
    print(f"Created Ticket: {ticket.ticket_id} | Initial Status: {ticket.status}")
    
    ticket.assign_routing()
    print(f"Post-Routing Status: {ticket.status}")
    print(f"Assigned Team:       {ticket.target_team}")
    print(f"Audit History Count: {len(ticket.history)}")
    print(f"Latest Audit Reason: {ticket.history[-1].reason}")