import sqlite3
from datetime import datetime
from pathlib import Path

import pytest

from synapse_qr_print.db import init_db, mark_printed, save_message

SENT_AT = datetime(2026, 10, 7, 11, 20, 5)

@pytest.fixture
def db_path(tmp_path):
    path = str(tmp_path / "data" / "messages.db")  # папки data ещё нет
    init_db(path)
    return path

def save(db_path, event_id="$ev1"):
    return save_message(
        db_path,
        event_id=event_id,
        room_id="!room:localhost",
        sender="@petr:localhost",
        sent_at=SENT_AT,
        body="Привет",
        pdf_path=Path("/var/lib/qr-print/pdf/2026-10-07/112005__ev1.pdf"),
    )

def rows(db_path):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    result = [dict(r) for r in conn.execute("SELECT * FROM messages ORDER BY id")]
    conn.close()
    return result

def test_init_creates_folder_and_table(db_path):
    assert Path(db_path).exists()
    assert rows(db_path) == []

def test_init_twice_is_safe(db_path):
    init_db(db_path)  # повторный запуск Synapse не должен ломать базу
    assert rows(db_path) == []

def test_save_message_stores_all_fields(db_path):
    assert save(db_path) is True
    [row] = rows(db_path)
    assert row["event_id"] == "$ev1"
    assert row["room_id"] == "!room:localhost"
    assert row["sender"] == "@petr:localhost"
    assert row["sent_at"] == "2026-10-07 11:20:05"
    assert row["body"] == "Привет"
    assert row["pdf_path"] == "/var/lib/qr-print/pdf/2026-10-07/112005__ev1.pdf"
    assert row["printed"] == 0

def test_duplicate_event_is_not_saved_twice(db_path):
    assert save(db_path) is True
    assert save(db_path) is False
    assert len(rows(db_path)) == 1

def test_mark_printed(db_path):
    save(db_path, "$ev1")
    save(db_path, "$ev2")
    mark_printed(db_path, "$ev1")
    printed = {r["event_id"]: r["printed"] for r in rows(db_path)}
    assert printed == {"$ev1": 1, "$ev2": 0}