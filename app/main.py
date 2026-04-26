import os
from contextlib import asynccontextmanager
from typing import AsyncIterator

import structlog
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from sqlalchemy import text

from app.api.router import api_router
from app.cache.redis_client import close_redis_pool, ping_redis

from app.config import get_settings
from app.db.session import engine
from app.mcp_client.tool_registry import (
    clear_tool_registry,
    registry_status,
    warmup_tool_registry
)


settings = get_settings()


def _configure_logging() -> None:
    """Configure structlog processors for the current environment.

    JSON mode  (production)  → newline-delimited JSON, machine-parseable.
    Console mode (development) → colourised, human-readable output.
    """
    renderer = (
        structlog.processors.JSONRenderer()
        if settings.structured_log_format == "json"
        else structlog.dev.ConsoleRenderer(colors=True)
    )
    structlog.configure(
        processors=[
            structlog.stdlib.add_log_level,
            structlog.processors.TimeStamper(fmt="iso", utc=True),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            renderer,
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )


_configure_logging()
logger = structlog.get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Manage startup and shutdown of shared resources.

    Startup:
    - Configure LangSmith tracing environment variables (if enabled).
    - Verify PostgreSQL connectivity (fail fast — don't start broken).
    - Verify Redis connectivity (warn only — app can run degraded without it).

    Shutdown:
    - Dispose the SQLAlchemy engine (drains the connection pool).
    - Close the Redis connection pool gracefully.
    """
    # ----- Startup -----
    logger.info(
        "app.startup",
        name=settings.app_name,
        version=settings.app_version,
        environment=settings.environment,
    )
    
    if settings.langchain_tracing_v2:
        os.environ["LANGCHAIN_TRACING_V2"] = "true"
        os.environ["LANGCHAIN_API_KEY"] = settings.langchain_api_key
        os.environ["LANGCHAIN_PROJECT"] = settings.langchain_project
        os.environ["LANGCHAIN_ENDPOINT"] = str(settings.langchain_endpoint)
        logger.info(
            "langsmith.tracing_enabled",
            project=settings.langchain_project,
            endpoint=str(settings.langchain_endpoint),
        )

    # PostgreSQL — fail hard on startup if unreachable
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        logger.info("db.connected")
    except Exception as exc:
        logger.error("db.connection_failed", error=str(exc))
        raise RuntimeError(f"Cannot connect to PostgreSQL on startup: {exc}") from exc
    
    
    
    # Redis — warn only; cache miss degrades gracefully to DB
    redis_ok = await ping_redis()
    if redis_ok:
        logger.info("redis.connected")
    else:
        logger.warning(
            "redis.connection_failed",
            detail="Cache and rate-limiting will be unavailable.",
        )
        
     # MCP tool registry — pre-warm LangChain tool schemas for all roles.
    # Non-fatal: if the MCP tools service is not yet up (e.g. slow container
    # start), the registry falls back to a live per-request fetch.
    try:
        await warmup_tool_registry()
        logger.info("tool_registry.warmed", roles=registry_status())
    except Exception as exc:
        logger.warning(
            "tool_registry.warmup_failed",
            error=str(exc),
            detail="Tool schemas will be fetched live on first request per role.",
        )
    
    yield

    # ----- Shutdown -----
    logger.info("app.shutdown")
    clear_tool_registry()
    logger.info("tool_registry.cleared")
    await engine.dispose()
    logger.info("db.pool_disposed")
    await close_redis_pool()
    logger.info("redis.pool_closed")
    logger.info("app.shutdown_complete")
    
    

def create_app() -> FastAPI:
    """Construct and configure the FastAPI application.

    Centralised factory makes the app importable for tests and ASGI runners
    without side-effects at import time.

    Returns:
        Fully configured FastAPI instance.
    """
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description=(
            "AI-powered customer service agent for ecommerce. "
            "Handles order tracking, refunds, product search, and more "
            "using LangGraph + Claude."
        ),
        # Disable interactive docs in production to reduce attack surface
        docs_url="/docs" if settings.is_development else None,
        redoc_url="/redoc" if settings.is_development else None,
        openapi_url="/openapi.json" if settings.is_development else None,
        lifespan=lifespan,
    )

    _register_middleware(app)
    _register_routes(app)
    _register_exception_handlers(app)

    return app

def _register_middleware(app: FastAPI) -> None:
    """Attach middleware to the application.

    Note: FastAPI/Starlette applies middleware in reverse registration order
    (LIFO). CORS is registered last so it wraps the outermost layer.
    """
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_allowed_origins,
        allow_credentials=settings.cors_allow_credentials,
        allow_methods=settings.cors_allowed_methods,
        allow_headers=settings.cors_allowed_headers,
    )

def _register_routes(app: FastAPI) -> None:
    """Mount all API routers and auxiliary ASGI apps."""
    # Main versioned API
    app.include_router(api_router, prefix="/api")

    # Prometheus metrics — scraped by Prometheus at /metrics
    # Mounted as a sub-ASGI app so it bypasses FastAPI middleware overhead
    # metrics_app = make_asgi_app()
    # app.mount("/metrics", metrics_app)


def _register_exception_handlers(app: FastAPI) -> None:
    """Register global exception handlers for uncaught errors."""

    @app.exception_handler(Exception)
    async def _unhandled_exception_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        logger.exception(
            "unhandled_exception",
            path=str(request.url.path),
            method=request.method,
            error=str(exc),
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "detail": "An unexpected error occurred. Please try again later.",
            },
        )


app = create_app()
