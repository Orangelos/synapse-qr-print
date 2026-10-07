import sqlite3
from contextlib import closing
from datetime import datetime
from pathlib import Path

SCHEMA = """
CREATE TABLE IF NOT EXISTS messages (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    event_id   TEXT UNIQUE NOT NULL,
    room_id    TEXT NOT NULL,
    sender     TEXT NOT NULL,
    sent_at    TEXT NOT NULL,
    body       TEXT NOT NULL,
    pdf_path   TEXT NOT NULL,
    printed    INTEGER NOT NULL DEFAULT 0
)
"""

def _connect(db_path):
    return sqlite3.connect(db_path, timeout=10)

def init_db(db_path: str):
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    with closing(_connect(db_path)) as conn, conn:
        conn.execute(SCHEMA)

def save_message(
    db_path: str,
    event_id: str,
    room_id: str,
    sender: str,
    sent_at: datetime,
    body: str,
    pdf_path: Path,
):
    with closing(_connect(db_path)) as conn, conn:
        cur = conn.execute(
            "INSERT OR IGNORE INTO messages "
            "(event_id, room_id, sender, sent_at, body, pdf_path) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (event_id, room_id, sender, sent_at.isoformat(sep=" "), body, str(pdf_path)),
        )
        return cur.rowcount == 1

def mark_printed(db_path: str, event_id: str):
    with closing(_connect(db_path)) as conn, conn:
        conn.execute("UPDATE messages SET printed = 1 WHERE event_id = ?", (event_id,))