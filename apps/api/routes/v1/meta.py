from fastapi import APIRouter

from packages.core.config import settings
from packages.core.schemas.health import MetaResponse

router = APIRouter(prefix="/v1")


@router.get("/meta", response_model=MetaResponse)
async def get_meta() -> MetaResponse:
    """Get service metadata."""
    return MetaResponse(
        service=settings.flowbiz_service_name,
        environment=settings.app_env,
        version=settings.flowbiz_version,
        build_sha=settings.flowbiz_build_sha,
    )
