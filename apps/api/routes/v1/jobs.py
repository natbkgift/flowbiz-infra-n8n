from __future__ import annotations

from datetime import datetime, timezone

import httpx
from fastapi import APIRouter, BackgroundTasks, HTTPException, status

from packages.core.config import settings
from packages.core.logging import get_logger
from packages.core.registry import workflow_exists
from packages.core.schemas.job import JobRequest, JobResponse, JobStatus

router = APIRouter(prefix="/v1")
logger = get_logger(__name__)


@router.post("/jobs", response_model=JobResponse, status_code=status.HTTP_202_ACCEPTED)
async def create_job(request: JobRequest, background_tasks: BackgroundTasks) -> JobResponse:
    """Accept a job request, validate workflow, and dispatch asynchronously."""

    if not workflow_exists(request.workflow_key):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unknown workflow_key",
        )

    accepted_at = datetime.now(timezone.utc)
    response = JobResponse(
        job_id=request.job_id,
        status=JobStatus.PENDING,
        message="accepted",
        accepted_at=accepted_at,
    )

    background_tasks.add_task(dispatch_to_n8n, request)

    logger.info(
        "job accepted",
        extra={
            "job_id": request.job_id,
            "client_id": request.client_id,
            "workflow_key": request.workflow_key,
            "status": response.status,
        },
    )

    return response


async def dispatch_to_n8n(request: JobRequest) -> None:
    """Fire-and-forget call to n8n webhook; failures are logged."""

    webhook_url = f"{settings.n8n_webhook_base_url.rstrip('/')}/{request.workflow_key}"
    payload = request.model_dump()

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            await client.post(webhook_url, json=payload)
    except Exception as exc:  # noqa: BLE001 - log and continue
        logger.error(
            "n8n dispatch failed",
            extra={
                "job_id": request.job_id,
                "client_id": request.client_id,
                "workflow_key": request.workflow_key,
                "status": JobStatus.PENDING,
            },
        )
        logger.debug("dispatch exception", exc_info=exc)