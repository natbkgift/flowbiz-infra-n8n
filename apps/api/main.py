from fastapi import FastAPI

from apps.api.routes import health
from apps.api.routes.v1 import jobs, meta
from packages.core.config import settings
from packages.core.logging import setup_logging
from packages.core.registry import get_registry

setup_logging()

app = FastAPI(
    title=settings.flowbiz_service_name,
    version=settings.flowbiz_version,
    docs_url="/docs" if settings.app_env == "dev" else None,
    redoc_url="/redoc" if settings.app_env == "dev" else None,
)

app.include_router(health.router)
app.include_router(meta.router)
app.include_router(jobs.router)


@app.on_event("startup")
async def preload_registry() -> None:
    """Fail fast if registry cannot be loaded."""

    get_registry()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=settings.app_env == "dev",
    )
