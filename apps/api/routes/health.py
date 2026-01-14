from fastapi import APIRouter

from packages.core.config import settings
from packages.core.schemas.health import HealthResponse

router = APIRouter()


@router.get("/healthz", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Health check endpoint."""
    return HealthResponse(
        status="ok",
        service=settings.flowbiz_service_name,
        version=settings.flowbiz_version,
    )
