import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional

from database import init_db, get_db_connection
from sanitizer import sanitize_text
from extractor import process_ticket
from router import process_and_route_ticket, check_and_escalate_sla
from actions import execute_ticket_workflow
from state import IncidentTicket

app = FastAPI(
    title="Enterprise Incident & Support Operations Engine",
    description="Autonomous routing, SLA tracking, and audit logging API.",
    version="1.0.0"
)

@app.on_event("startup")
def startup_event():
    """Initializes the SQLite database tables on startup."""
    init_db()

class TicketPayload(BaseModel):
    raw_text: str

class TicketResponse(BaseModel):
    ticket_id: str
    created_at: str
    status: str
    category: str
    urgency_level: str
    target_team: str
    target_channel: Optional[str] = None
    on_call_pager: Optional[str] = None
    sla_minutes: int
    summary: str

    class Config:
        from_attributes = True


@app.post("/tickets", status_code=201, response_model=TicketResponse)
def create_ticket(payload: TicketPayload):
    """Ingests raw text, sanitizes PII, extracts structure, routes, and persists to SQLite."""
    # 1. Run pipeline (Sanitizer -> Extractor -> Router -> Escalation -> Workflow)
    sanitized_text = sanitize_text(payload.raw_text)
    extraction = process_ticket(sanitized_text)
    
    ticket = IncidentTicket(extraction_data=extraction)
    ticket = process_and_route_ticket(ticket)
    ticket = check_and_escalate_sla(ticket)
    ticket = execute_ticket_workflow(ticket)
    
    # 2. Persist ticket to SQLite database
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO tickets (ticket_id, created_at, status, category, urgency_level, target_team, target_channel, on_call_pager, sla_minutes, summary, requested_actions)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        ticket.ticket_id,
        ticket.created_at.isoformat(),
        ticket.status.value,
        ticket.extraction_data.category,
        ticket.extraction_data.urgency_level,
        ticket.target_team,
        ticket.target_channel,
        ticket.on_call_pager,
        ticket.sla_minutes,
        ticket.extraction_data.summary,
        str(ticket.extraction_data.requested_actions)
    ))
    
    # 3. Persist audit logs to SQLite
    for log in ticket.history:
        cursor.execute("""
            INSERT INTO audit_logs (ticket_id, previous_status, new_status, timestamp, reason)
            VALUES (?, ?, ?, ?, ?)
        """, (
            ticket.ticket_id,
            log.previous_status.value,
            log.new_status.value,
            log.timestamp.isoformat(),
            log.reason
        ))
        
    conn.commit()
    conn.close()
    
    # 4. Return flattened response dictionary matching TicketResponse schema
    return {
        "ticket_id": ticket.ticket_id,
        "created_at": ticket.created_at.isoformat(),
        "status": ticket.status.value,
        "category": ticket.extraction_data.category,
        "urgency_level": ticket.extraction_data.urgency_level,
        "target_team": ticket.target_team,
        "target_channel": ticket.target_channel,
        "on_call_pager": ticket.on_call_pager,
        "sla_minutes": ticket.sla_minutes,
        "summary": ticket.extraction_data.summary
    }

class Config:
    from_attributes = True


import time

@app.post("/tickets", status_code=201, response_model=TicketResponse)
def create_ticket(payload: TicketPayload):
    start_time = time.time()
    
    # 1. Run pipeline
    sanitized_text = sanitize_text(payload.raw_text)
    extraction = process_ticket(sanitized_text)
    
    ticket = IncidentTicket(extraction_data=extraction)
    ticket = process_and_route_ticket(ticket)
    ticket = check_and_escalate_sla(ticket)
    ticket = execute_ticket_workflow(ticket)
    
    # Calculate latency in milliseconds and estimate token usage based on text length
    latency_ms = (time.time() - start_time) * 1000.0
    estimated_tokens = len(payload.raw_text.split()) * 4  # rough heuristic or OpenAI response usage
    
    # 2. Persist ticket with metrics
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO tickets (ticket_id, created_at, status, category, urgency_level, target_team, target_channel, on_call_pager, sla_minutes, summary, requested_actions, processing_latency_ms, token_usage)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        ticket.ticket_id,
        ticket.created_at.isoformat(),
        ticket.status.value,
        ticket.extraction_data.category,
        ticket.extraction_data.urgency_level,
        ticket.target_team,
        ticket.target_channel,
        ticket.on_call_pager,
        ticket.sla_minutes,
        ticket.extraction_data.summary,
        str(ticket.extraction_data.requested_actions),
        latency_ms,
        estimated_tokens
    ))
    
    # 3. Persist audit logs
    for log in ticket.history:
        cursor.execute("""
            INSERT INTO audit_logs (ticket_id, previous_status, new_status, timestamp, reason)
            VALUES (?, ?, ?, ?, ?)
        """, (
            ticket.ticket_id,
            log.previous_status.value,
            log.new_status.value,
            log.timestamp.isoformat(),
            log.reason
        ))
        
    conn.commit()
    conn.close()
    
    return {
        "ticket_id": ticket.ticket_id,
        "created_at": ticket.created_at.isoformat(),
        "status": ticket.status.value,
        "category": ticket.extraction_data.category,
        "urgency_level": ticket.extraction_data.urgency_level,
        "target_team": ticket.target_team,
        "target_channel": ticket.target_channel,
        "on_call_pager": ticket.on_call_pager,
        "sla_minutes": ticket.sla_minutes,
        "summary": ticket.extraction_data.summary
    }

class AuditLogResponse(BaseModel):
    ticket_id: str
    previous_status: str
    new_status: str
    timestamp: str
    reason: str

    class Config:
        from_attributes = True

@app.post("/tickets", status_code=201, response_model=TicketResponse)
def create_ticket(payload: TicketPayload):
    """Ingests raw text, sanitizes PII, extracts structure, routes, and persists to SQLite."""
    # 1. Run pipeline (Sanitizer -> Extractor -> Router -> Escalation -> Workflow)
    sanitized_text = sanitize_text(payload.raw_text)
    extraction = process_ticket(sanitized_text)
    
    ticket = IncidentTicket(extraction_data=extraction)
    ticket = process_and_route_ticket(ticket)
    ticket = check_and_escalate_sla(ticket)
    ticket = execute_ticket_workflow(ticket)
    
    # 2. Persist ticket to SQLite database
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO tickets (ticket_id, created_at, status, category, urgency_level, target_team, target_channel, on_call_pager, sla_minutes, summary, requested_actions)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        ticket.ticket_id,
        ticket.created_at.isoformat(),
        ticket.status.value,
        ticket.extraction_data.category,
        ticket.extraction_data.urgency_level,
        ticket.target_team,
        ticket.target_channel,
        ticket.on_call_pager,
        ticket.sla_minutes,
        ticket.extraction_data.summary,
        str(ticket.extraction_data.requested_actions)
    ))
    
    # 3. Persist audit logs to SQLite
    for log in ticket.history:
        cursor.execute("""
            INSERT INTO audit_logs (ticket_id, previous_status, new_status, timestamp, reason)
            VALUES (?, ?, ?, ?, ?)
        """, (
            ticket.ticket_id,
            log.previous_status.value,
            log.new_status.value,
            log.timestamp.isoformat(),
            log.reason
        ))
        
    conn.commit()
    conn.close()
    
    return ticket


@app.get("/tickets", response_model=List[TicketResponse])
def list_tickets():
    """Retrieves all ingested incident tickets from SQLite."""
    conn = get_db_connection()
    cursor = conn.cursor()
    rows = cursor.execute("SELECT * FROM tickets").fetchall()
    conn.close()
    return [dict(row) for row in rows]


@app.get("/tickets/{ticket_id}", response_model=TicketResponse)
def get_ticket(ticket_id: str):
    """Fetches a single incident ticket by its unique ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    row = cursor.execute("SELECT * FROM tickets WHERE ticket_id = ?", (ticket_id,)).fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Ticket not found.")
    return dict(row)


@app.get("/tickets/{ticket_id}/audit-logs", response_model=List[AuditLogResponse])
def get_audit_logs(ticket_id: str):
    """Retrieves all state transition audit logs for a specific ticket."""
    conn = get_db_connection()
    cursor = conn.cursor()
    rows = cursor.execute("SELECT * FROM audit_logs WHERE ticket_id = ?", (ticket_id,)).fetchall()
    conn.close()
    if not rows:
        raise HTTPException(status_code=404, detail="Audit logs not found for ticket.")
    return [dict(row) for row in rows]


@app.get("/observability/metrics")
def get_observability_metrics():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Total incidents
    total = cursor.execute("SELECT COUNT(*) FROM tickets").fetchone()[0]
    
    if total == 0:
        conn.close()
        return {
            "total_incidents_processed": 0,
            "status_distribution": {},
            "category_distribution": {},
            "average_processing_latency_ms": 0.0,
            "total_tokens_consumed": 0
        }
        
    # Status distribution
    statuses = cursor.execute("SELECT status, COUNT(*) FROM tickets GROUP BY status").fetchall()
    status_dist = {row[0]: row[1] for row in statuses}
    
    # Category distribution
    categories = cursor.execute("SELECT category, COUNT(*) FROM tickets GROUP BY category").fetchall()
    cat_dist = {row[0]: row[1] for row in categories}
    
    # Average latency and total tokens
    avg_latency = cursor.execute("SELECT AVG(processing_latency_ms) FROM tickets").fetchone()[0] or 0.0
    total_tokens = cursor.execute("SELECT SUM(token_usage) FROM tickets").fetchone()[0] or 0
    
    conn.close()
    
    return {
        "total_incidents_processed": total,
        "status_distribution": status_dist,
        "category_distribution": cat_dist,
        "average_processing_latency_ms": round(avg_latency, 2),
        "total_tokens_consumed": total_tokens
    }