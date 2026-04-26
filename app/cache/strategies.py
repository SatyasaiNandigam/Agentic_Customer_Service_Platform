from __future__ import annotations

import json
import logging
from collections.abc import Awaitable, Callable
from typing import TypeVar

from redis.exceptions import RedisError

from app.cache.redis_client import get_redis_context, is_redis_available

logger = logging.getLogger(__name__)

T = TypeVar("T")


async def cache_aside(
    key: str,
    ttl: int,
    fetch: Callable[[], Awaitable[T]],
) -> T:
    """Read-through / write-through cache pattern.

    1. Try to read *key* from Redis.
       - Hit  → deserialise JSON and return immediately (no DB call).
       - Miss → fall through.
    2. Call *fetch()* to load data from PostgreSQL.
    3. If the result is not None/empty, store it in Redis with *ttl* seconds.
    4. Return the result.

    Redis failures are caught and logged at WARNING level so a Redis outage
    never takes down the MCP tools service.

    Args:
        key:   Redis key string (use helpers from app.cache.keys).
        ttl:   Expiry in seconds.  Use the cache_ttl_* settings from config.
        fetch: Zero-argument async callable that queries the DB and returns
               a JSON-serialisable value (dict, list, or None).

    Returns:
        The cached or freshly-fetched value.

    Example::

        result = await cache_aside(
            key=order_list_key(user_id),
            ttl=settings.cache_ttl_order_status,
            fetch=lambda: get_orders_for_user(db, user_id, limit=limit),
        )
    """
    # --- Cache read ---
    if is_redis_available():
        try:
            async with get_redis_context() as redis:
                raw = await redis.get(key)
                if raw is not None:
                    return json.loads(raw)  # type: ignore[return-value]
        except RedisError as exc:
            logger.warning("cache.read_failed", extra={"key": key, "error": str(exc)})

    # --- DB fetch ---
    result = await fetch()

    # --- Cache write ---
    if result is not None and is_redis_available():
        try:
            async with get_redis_context() as redis:
                await redis.set(key, json.dumps(result, default=str), ex=ttl)
        except RedisError as exc:
            logger.warning("cache.write_failed", extra={"key": key, "error": str(exc)})

    return result  # type: ignore[return-value]



async def invalidate(*keys: str) -> None:
    """Delete one or more keys from Redis.

    Called by write tools after a successful mutation so subsequent reads
    get fresh data instead of stale cached values.

    Silently skips if Redis is unavailable — the TTL will eventually expire.

    Args:
        *keys: One or more cache key strings to delete.

    Example::

        await invalidate(
            order_list_key(user_id),
            order_detail_key(order_id),
        )
    """
    if not keys:
        return
    try:
        async with get_redis_context() as redis:
            await redis.delete(*keys)
    except RedisError as exc:
        logger.warning(
            "cache.invalidate_failed",
            extra={"keys": list(keys), "error": str(exc)},
        )
