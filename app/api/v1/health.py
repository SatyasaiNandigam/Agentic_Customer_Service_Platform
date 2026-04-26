from fastapi import APIRouter
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app.cache.redis_client import ping_redis
from app.config import get_settings
from app.db.session import engine


router = APIRouter()

settings = get_settings()


@router.get(
    "/health",
    summary="Health check endpoint",
    description="Returns 200 if the application process is running. No dependency checks.",
    response_description="Application is alive.",
)
async def health() -> JSONResponse:
    """Liveness probe - always returns 200 while the process is up."""
    
    return JSONResponse(
        status_code=200,
        content={
            "status": "ok",
            "version": settings.app_version,
            "environment": settings.environment,
        },
    )
    
    
@router.get(
    "/ready",
    summary="Readiness probe",
    description=(
        "Returns 200 only when all critical dependencies (PostgreSQL, Redis) "
        "are reachable. Returns 503 if any dependency is down."
    ),
    response_description="All dependencies are healthy.",
)
async def ready() -> JSONResponse:
    """Readiness probe — checks DB and Redis connectivity.

    Returns:
        200 with ``status: ready`` when all checks pass.
        503 with ``status: not_ready`` and per-check details when any fail.
    """
    checks: dict[str, bool] = {}

    # PostgreSQL check
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        checks["db"] = True
    except Exception:
        checks["db"] = False

    # Redis check
    checks["redis"] = await ping_redis()

    # MCP tool registry check — True once at least one role is warmed.
    # Reports the per-role tool counts so operators can verify warmup health.
    # reg = registry_status()
    # checks["tool_registry"] = bool(reg)

    all_ok = all(checks.values())

    return JSONResponse(
        status_code=200 if all_ok else 503,
        content={
            "status": "ready" if all_ok else "not_ready",
            "checks": checks,
            # "tool_registry": reg,
        },
    )
