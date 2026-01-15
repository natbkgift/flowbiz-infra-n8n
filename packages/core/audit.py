from __future__ import annotations

import asyncio
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from packages.core.config import settings
from packages.core.logging import get_logger
from packages.core.schemas.callback import JobCallback

logger = get_logger(__name__)
_write_lock = asyncio.Lock()


def _ensure_schema(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS audit_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            stored_at TEXT NOT NULL,
            job_id TEXT NOT NULL,
            status TEXT NOT NULL,
            payload_json TEXT NOT NULL
        )
        """
    )
    conn.commit()


def _write_row(db_path: Path, record: dict[str, object]) -> None:
    conn = sqlite3.connect(db_path)
    try:
        _ensure_schema(conn)
        conn.execute(
            "INSERT INTO audit_logs (stored_at, job_id, status, payload_json) VALUES (?, ?, ?, ?)",
            (
                record["stored_at"],
                record["job_id"],
                record["status"],
                json.dumps(record, separators=(",", ":"), sort_keys=True),
            ),
        )
        conn.commit()
    finally:
        conn.close()


async def persist_audit(callback: JobCallback, db_path: Path | None = None) -> Path:
    """Persist callback payload to SQLite for centralized audit retention."""

    target_path = Path(db_path or settings.audit_db_path)
    target_path.parent.mkdir(parents=True, exist_ok=True)

    record = {
        "stored_at": datetime.now(timezone.utc).isoformat(),
        **callback.model_dump(mode="json"),
    }

    async with _write_lock:
        await asyncio.to_thread(_write_row, target_path, record)

    logger.info(
        "audit persisted",
        extra={
            "job_id": callback.job_id,
            "client_id": None,
            "workflow_key": None,
            "status": callback.status,
        },
    )

    return target_path
