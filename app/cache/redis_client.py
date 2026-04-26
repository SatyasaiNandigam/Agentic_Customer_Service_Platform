from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager


import redis.asyncio as aioredis
from redis.asyncio import Redis
from redis.asyncio.connection import ConnectionPool
from redis.exceptions import RedisError

from app.config import get_settings

settings = get_settings()

_redis_available: bool = True


def set_redis_available(ok: bool) -> None:
    global _redis_available
    _redis_available = ok


def is_redis_available() -> bool:
    return _redis_available


_pool: ConnectionPool = aioredis.ConnectionPool.from_url(
    settings.redis_url_str,
    max_connections=settings.redis_max_connections,
    socket_timeout=settings.redis_socket_timeout,
    socket_connect_timeout=settings.redis_socket_connect_timeout,
    decode_responses=True,  # all keys/values are str, not bytes
)


def get_pool() -> ConnectionPool:
    """Return the shared connection pool (useful for testing overrides)."""
    return _pool


async def get_redis() -> AsyncGenerator[Redis, None]:
    """Yield a Redis client scoped to a single request.

    The client borrows a connection from the shared pool and releases it when
    the generator exits — no explicit close() needed per request.

    Usage::

        @router.get("/ping")
        async def ping(redis: Redis = Depends(get_redis)):
            return await redis.ping()
    """
    client: Redis = aioredis.Redis(connection_pool=_pool)
    try:
        yield client
    finally:
        await client.aclose()


@asynccontextmanager
async def get_redis_context() -> AsyncGenerator[Redis, None]:
    """Async context manager that mirrors get_redis for non-Depends usage.

    Usage::

        async with get_redis_context() as redis:
            await redis.set("key", "value", ex=60)
    """
    client: Redis = aioredis.Redis(connection_pool=_pool)
    try:
        yield client
    finally:
        await client.aclose()


async def ping_redis() -> bool:
    """Return True if Redis is reachable, False otherwise.

    Used by the /ready health endpoint to gate traffic until the cache is up.
    """
    try:
        async with get_redis_context() as redis:
            return await redis.ping()
    except RedisError:
        return False


async def close_redis_pool() -> None:
    """Drain and close the connection pool gracefully.

    Call this from the FastAPI lifespan shutdown handler so all in-flight
    commands finish before the process exits.
    """
    await _pool.aclose()
