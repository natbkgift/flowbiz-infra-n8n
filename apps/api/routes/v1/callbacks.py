from __future__ import annotations

import hashlib
import hmac

from fastapi import APIRouter, HTTPException, Request, status
from pydantic import ValidationError

from packages.core.config import settings
from packages.core.logging import get_logger
from packages.core.schemas.callback import JobCallback

router = APIRouter(prefix="/v1")
logger = get_logger(__name__)
_SIGNATURE_HEADER = "x-callback-signature"


def _compute_signature(secret: str, body: bytes) -> str:
    """Return hex-encoded HMAC-SHA256 signature for the given body."""

    return hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()


def _verify_signature(body: bytes, provided: str | None, job_id: str | None) -> None:
    """Validate callback signature when secret is configured."""

    if not settings.callback_signing_secret:
        logger.warning(
            "callback signature not validated (secret missing)",
            extra={"job_id": job_id, "status": None, "workflow_key": None, "client_id": None},
        )
        return

    if not provided:
        logger.warning(
            "callback signature missing",
            extra={"job_id": job_id, "status": None, "workflow_key": None, "client_id": None},
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing callback signature",
        )

    expected = _compute_signature(settings.callback_signing_secret, body)
    if not hmac.compare_digest(provided, expected):
        logger.warning(
            "callback signature invalid",
            extra={"job_id": job_id, "status": None, "workflow_key": None, "client_id": None},
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid callback signature",
        )


@router.post("/callbacks/n8n", status_code=status.HTTP_200_OK)
async def receive_callback(request: Request) -> dict[str, str]:
    """Accept callback payloads from n8n and acknowledge receipt."""

    raw_body = await request.body()

    _verify_signature(raw_body, request.headers.get(_SIGNATURE_HEADER), job_id=None)

    try:
        callback = JobCallback.model_validate_json(raw_body)
    except ValidationError as exc:  # pragma: no cover - fastapi will surface detail
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid callback payload",
        ) from exc

    logger.info(
        "callback received",
        extra={
            "job_id": callback.job_id,
            "client_id": None,
            "workflow_key": None,
            "status": callback.status,
            "execution_id": callback.execution_id,
        },
    )

    return {"status": "ok"}
