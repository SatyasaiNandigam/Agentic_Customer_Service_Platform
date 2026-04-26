"""FastMCP tools service — entry point.

Runs as a dedicated Docker container on port 8001 (internal only in production).
The LangGraph agent connects over HTTP/SSE using langchain-mcp-adapters.

Startup sequence:
  1. Verify PostgreSQL connectivity (fail hard — don't serve broken tools).
  2. Verify Redis connectivity (warn only — queries degrade to DB on cache miss).
  3. Register all 10 ecommerce tool modules onto the shared FastMCP instance.
  4. Serve MCP protocol over SSE.

Transport: SSE (Server-Sent Events) — agent connects to http://mcp-tools:8001/sse.

Usage:
    python -m tools_mcp.server          # Docker CMD / local dev

Health endpoint:
    GET /health  →  {"status": "ok", ...}  (used by docker-compose healthcheck)
"""

from __future__ import annotations

import sys
from pathlib import Path
from contextlib import asynccontextmanager
from typing import AsyncIterator

# Ensure project root is on sys.path when run via `fastmcp inspect` (which
# imports the file directly without the project root in the path).
_project_root = str(Path(__file__).parent.parent)
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

import structlog
import uvicorn
from fastmcp import FastMCP
from sqlalchemy import text
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Mount, Route

from app.cache.redis_client import close_redis_pool, ping_redis, set_redis_available
from app.config import get_settings
from app.db.session import engine


from tools_mcp.tools import (
    account_info,
    order_cancel,
    order_items,
    order_lookup,
    product_detail,
    product_search,
    refund_initiate,
    refund_status,
    review_lookup,
    shipment_tracking,
)

settings = get_settings()
logger = structlog.get_logger(__name__)



mcp = FastMCP(
    name="ecommerce-tools",
    instructions=(
        "Tools for querying ecommerce data on behalf of authenticated customers. "
        "user_id is always sourced from the X-User-Id request header — never trust "
        "user_id values supplied in tool arguments."
    ),
)



def _register_tools() -> None:
    """Mount all tool modules onto the shared FastMCP instance.

    Called once at module import so tools are available before the server
    starts accepting connections.
    """
    order_lookup.register(mcp)
    order_items.register(mcp)
    product_search.register(mcp)
    product_detail.register(mcp)
    shipment_tracking.register(mcp)
    refund_status.register(mcp)
    refund_initiate.register(mcp)
    order_cancel.register(mcp)
    review_lookup.register(mcp)
    account_info.register(mcp)

    logger.info("mcp.tools_registered", count=10)


_register_tools()

async def _health(request: Request) -> JSONResponse:
    """Liveness probe — always returns 200 if the process is alive.

    Docker-compose healthcheck: GET http://localhost:8001/health
    A 200 means the MCP server process is up; it does NOT verify DB/Redis.
    Use the /ready endpoint (if added) for deep readiness checks.
    """
    return JSONResponse(
        {
            "status": "ok",
            "service": "mcp-tools",
            "version": settings.app_version,
        }
    )


@asynccontextmanager
async def _lifespan(app: Starlette) -> AsyncIterator[None]:
    """Startup and shutdown for the combined Starlette + FastMCP app.

    Startup:
    - Verify PostgreSQL is reachable (fail hard — tools need DB to function).
    - Verify Redis is reachable (warn only — tools fall back to DB on miss).

    Shutdown:
    - Dispose SQLAlchemy connection pool.
    - Close Redis connection pool.
    """
    # ----- Startup -----
    logger.info(
        "mcp_server.startup",
        service="mcp-tools",
        version=settings.app_version,
        environment=settings.environment,
    )

    # PostgreSQL — hard failure: tools cannot function without DB
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        logger.info("mcp_server.db_connected")
    except Exception as exc:
        logger.error("mcp_server.db_connection_failed", error=str(exc))
        raise RuntimeError(
            f"MCP tools server cannot connect to PostgreSQL on startup: {exc}"
        ) from exc

    # Redis — soft failure: cache misses degrade gracefully to DB queries
    redis_ok = await ping_redis()
    set_redis_available(redis_ok)
    if redis_ok:
        logger.info("mcp_server.redis_connected")
    else:
        logger.warning(
            "mcp_server.redis_unavailable",
            detail="Tool responses will not be cached — all reads hit PostgreSQL.",
        )

    logger.info("mcp_server.ready", transport="sse", port=8001)

    yield

    # ----- Shutdown -----
    logger.info("mcp_server.shutdown")
    await engine.dispose()
    logger.info("mcp_server.db_pool_disposed")
    await close_redis_pool()
    logger.info("mcp_server.redis_pool_closed")
    logger.info("mcp_server.shutdown_complete")



def _build_app() -> Starlette:
    """Construct the combined Starlette + FastMCP ASGI application."""
    mcp_asgi = mcp.http_app(transport="sse")

    return Starlette(
        lifespan=_lifespan,
        routes=[
            Route("/health", _health, methods=["GET"]),
            Mount("/", app=mcp_asgi),
        ],
    )


app = _build_app()



def main() -> None:  # pragma: no cover
    """Start the MCP tools server with uvicorn.

    Invoked via: python -m tools_mcp.server
    Or Docker CMD: python -m tools_mcp.server
    """
    uvicorn.run(
        "tools_mcp.server:app",
        host="0.0.0.0",
        port=8001,
        reload=settings.is_development,
        log_level=settings.log_level.lower(),
        access_log=settings.is_development,
    )


if __name__ == "__main__":
    main()
