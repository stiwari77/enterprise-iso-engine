import sqlite3

DB_FILE = "incidents.db"

def get_db_connection():
    """Returns a standard SQLite connection with row factory enabled."""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = sqlite3.connect("incidents.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tickets (
            ticket_id TEXT PRIMARY KEY,
            created_at TEXT,
            status TEXT,
            category TEXT,
            urgency_level TEXT,
            target_team TEXT,
            target_channel TEXT,
            on_call_pager TEXT,
            sla_minutes INTEGER,
            summary TEXT,
            requested_actions TEXT,
            processing_latency_ms REAL DEFAULT 0.0,
            token_usage INTEGER DEFAULT 0
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS audit_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticket_id TEXT,
            previous_status TEXT,
            new_status TEXT,
            timestamp TEXT,
            reason TEXT
        )
    """)
    conn.commit()
    conn.close()

if __name__ == "__main__":
    print("Initializing native SQLite database...")
    init_db()
    print("Database 'incidents.db' successfully created.")