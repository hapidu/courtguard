"""
Simple SQLite database for CourtGuard's audit trail.

SQLite needs no separate server/installation — it's just a file
(courtguard.db) that appears in the backend folder. This is the standard,
appropriate choice for a final-year project (and even many small production
systems); you can mention in your report that PostgreSQL/MySQL would be the
next step for a multi-user production deployment.
"""
import sqlite3
from datetime import datetime
from contextlib import contextmanager

DB_PATH = "courtguard.db"


def init_db():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS analyses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                evidence_name TEXT NOT NULL,
                evidence_type TEXT NOT NULL,
                verdict TEXT NOT NULL,
                confidence_score REAL NOT NULL,
                details TEXT,
                created_at TEXT NOT NULL
            )
        """)
        conn.commit()


@contextmanager
def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def save_analysis(evidence_name: str, evidence_type: str, verdict: str, confidence_score: float, details: str = ""):
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO analyses (evidence_name, evidence_type, verdict, confidence_score, details, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (evidence_name, evidence_type, verdict, confidence_score, details, datetime.now().isoformat()),
        )
        conn.commit()


def get_all_analyses(limit: int = 100):
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM analyses ORDER BY created_at DESC LIMIT ?", (limit,)
        ).fetchall()
        return [dict(row) for row in rows]