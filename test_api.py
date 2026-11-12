import os
import pytest
from fastapi.testclient import TestClient

# Ensure a clean test database file before importing app/db
DB_FILE = "incidents.db"

from main import app
from database import init_db, get_db_connection

@pytest.fixture(autouse=True)
def setup_database():
    """Initializes a fresh database state before each test."""
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)
    init_db()
    yield
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)

client = TestClient(app)

def test_create_ticket_success():
    """Test successful ingestion, LLM extraction, routing, and persistence."""
    payload = {
        "raw_text": "CRITICAL: Database connection pool exhausted on payment-service-prod. Immediate paging required!"
    }
    response = client.post("/tickets", json=payload)
    assert response.status_code == 201
    
    data = response.json()
    assert "ticket_id" in data
    assert data["status"] == "ESCALATED"
    assert data["category"] == "database"
    assert data["urgency_level"] == "critical"
    assert data["target_team"] == "Database Reliability Engineering"
    assert data["sla_minutes"] == 15

def test_list_tickets():
    """Test listing all ingested tickets."""
    # Create two tickets first
    client.post("/tickets", json={"raw_text": "WARNING: High CPU utilization on cache nodes."})
    client.post("/tickets", json={"raw_text": "INFO: Password reset request for user account."})
    
    response = client.get("/tickets")
    assert response.status_code == 200
    tickets = response.json()
    assert len(tickets) == 2

def test_get_ticket_by_id():
    """Test fetching a single ticket by its ID."""
    create_res = client.post("/tickets", json={"raw_text": "CRITICAL: Payment gateway down."})
    ticket_id = create_res.json()["ticket_id"]
    
    response = client.get(f"/tickets/{ticket_id}")
    assert response.status_code == 200
    assert response.json()["ticket_id"] == ticket_id

def test_get_ticket_not_found():
    """Test 404 handling for a non-existent ticket ID."""
    response = client.get("/tickets/INC-NONEXISTENT")
    assert response.status_code == 404
    assert response.json()["detail"] == "Ticket not found."

def test_audit_logs_endpoint():
    """Test retrieving state transition audit logs for a specific ticket."""
    create_res = client.post("/tickets", json={"raw_text": "CRITICAL: Security breach detected on auth service."})
    ticket_id = create_res.json()["ticket_id"]
    
    response = client.get(f"/tickets/{ticket_id}/audit-logs")
    assert response.status_code == 200
    logs = response.json()
    
    # Should have at least routing and escalation audit records
    assert len(logs) >= 2
    assert logs[0]["ticket_id"] == ticket_id
    assert logs[0]["new_status"] in ["ROUTED", "ESCALATED"]