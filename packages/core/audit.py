from __future__ import annotations

import json
import threading
from datetime import datetime, timezone
from pathlib import Path

from packages.core.config import settings
from packages.core.logging import get_logger
from packages.core.schemas.callback import JobCallback

logger = get_logger(__name__)
_write_lock = threading.Lock()


def persist_audit(callback: JobCallback, log_path: Path | None = None) -> Path:
    """Append the callback payload to an audit log as JSON lines."""

    target_path = Path(log_path or settings.audit_log_path)
    target_path.parent.mkdir(parents=True, exist_ok=True)

    record = {
        "stored_at": datetime.now(timezone.utc).isoformat(),
        **callback.model_dump(mode="json"),
    }

    payload = json.dumps(record, separators=(",", ":"), sort_keys=True)

    with _write_lock:
        with target_path.open("a", encoding="utf-8") as fh:
            fh.write(payload + "\n")

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
