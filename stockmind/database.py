"""Tiny SQLite event store used by the dashboard and demonstrations."""
from __future__ import annotations
import sqlite3
from pathlib import Path
from typing import Any

class EventStore:
    def __init__(self, database_path: str | Path = "data/stockmind.db"):
        self.path = Path(database_path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as connection:
            connection.execute("CREATE TABLE IF NOT EXISTS events (id INTEGER PRIMARY KEY AUTOINCREMENT, event_type TEXT NOT NULL, details TEXT NOT NULL, created_at TEXT DEFAULT CURRENT_TIMESTAMP)")

    def _connect(self):
        return sqlite3.connect(self.path)

    def add_event(self, event_type: str, details: str) -> None:
        with self._connect() as connection:
            connection.execute("INSERT INTO events(event_type, details) VALUES (?, ?)", (event_type, details))

    def latest_events(self, limit: int = 100) -> list[dict[str, Any]]:
        with self._connect() as connection:
            rows = connection.execute("SELECT id, event_type, details, created_at FROM events ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
        return [{"id": r[0], "event_type": r[1], "details": r[2], "created_at": r[3]} for r in rows]
