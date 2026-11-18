"""SQLite storage: one file, no setup. The report itself is stored as JSON."""

import os
import sqlite3
from contextlib import closing
from datetime import datetime, timezone
from pathlib import Path

from app.models import Report, ReportCreate, ReportItem

DEFAULT_PATH = Path(__file__).resolve().parent.parent / "reports.db"


class ReportStore:
    def __init__(self, path: str | Path) -> None:
        self._path = str(path)
        with closing(self._connect()) as connection, connection:
            connection.execute(
                """CREATE TABLE IF NOT EXISTS reports (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    created_at TEXT NOT NULL,
                    transcript TEXT NOT NULL,
                    report TEXT NOT NULL
                )"""
            )

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self._path)
        connection.row_factory = sqlite3.Row
        return connection

    def save(self, item: ReportCreate) -> ReportItem:
        created_at = datetime.now(timezone.utc)
        with closing(self._connect()) as connection, connection:
            cursor = connection.execute(
                "INSERT INTO reports (created_at, transcript, report) VALUES (?, ?, ?)",
                (created_at.isoformat(), item.transcript, item.report.model_dump_json(exclude={"missing_fields"})),
            )
        return ReportItem(id=cursor.lastrowid, created_at=created_at, transcript=item.transcript, report=item.report)

    def list(self) -> list[ReportItem]:
        """All saved reports, newest first."""
        with closing(self._connect()) as connection:
            rows = connection.execute("SELECT * FROM reports ORDER BY id DESC").fetchall()
        return [
            ReportItem(
                id=row["id"],
                created_at=datetime.fromisoformat(row["created_at"]),
                transcript=row["transcript"],
                report=Report.model_validate_json(row["report"]),
            )
            for row in rows
        ]


def get_store() -> ReportStore:
    return ReportStore(os.getenv("DB_PATH", DEFAULT_PATH))
