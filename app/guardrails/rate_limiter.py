from __future__ import annotations

import time
import uuid

import structlog
from redis.exceptions import RedisError

from app.cache.redis_client import get_redis_context
from app.config import get_settings

logger = structlog.get_logger(__name__)

class SlidingWindowRateLimiter:
    """Per-user sliding-window rate limiter backed by a Redis sorted set.

    Args:
        key_prefix:     Redis key prefix.  Final key is ``<prefix>:<user_id>``.
        limit:          Maximum number of allowed events within the window.
        window_seconds: Window length in seconds.

    Example::

        limiter = SlidingWindowRateLimiter(
            key_prefix="rate:msgs",
            limit=20,
            window_seconds=60,
        )
        allowed, count = await limiter.check(user_id=42)
        if not allowed:
            raise ValueError(f"Rate limit exceeded: {count}/20 messages in 60 s")
    """

    def __init__(
        self,
        key_prefix: str,
        limit: int,
        window_seconds: int,
    ) -> None:
        self.key_prefix = key_prefix
        self.limit = limit
        self.window_seconds = window_seconds


    def _key(self, user_id: int) -> str:
        """Return the Redis key for *user_id*."""
        return f"{self.key_prefix}:{user_id}"



    async def check(self, user_id: int) -> tuple[bool, int]:
        """Record a new event for *user_id* and check whether the limit is exceeded.

        The event is always recorded — even when the limit is already exceeded.
        This prevents a misbehaving client from resetting the window by staying
        exactly at the boundary: every request counts.

        Args:
            user_id: The authenticated user's ID (from JWT, never from LLM args).

        Returns:
            ``(is_allowed, current_count)`` where *is_allowed* is ``False``
            when *current_count* > ``self.limit``.
            Returns ``(True, 0)`` when Redis is unavailable so a cache outage
            never blocks legitimate users (fail-open policy).
        """
        now = time.time()
        window_start = now - self.window_seconds
        key = self._key(user_id)

        try:
            async with get_redis_context() as redis:
                pipe = redis.pipeline()
                pipe.zremrangebyscore(key, "-inf", window_start)
                pipe.zadd(key, {str(uuid.uuid4()): now})
                pipe.zcard(key)
                pipe.expire(key, self.window_seconds + 5)  # small buffer past window
                results = await pipe.execute()
                count: int = results[2]  # zcard result

            is_allowed = count <= self.limit
            logger.debug(
                "rate_limiter.check",
                key_prefix=self.key_prefix,
                user_id=user_id,
                count=count,
                limit=self.limit,
                window_seconds=self.window_seconds,
                allowed=is_allowed,
            )
            return is_allowed, count

        except RedisError as exc:
            logger.warning(
                "rate_limiter.redis_error",
                key_prefix=self.key_prefix,
                user_id=user_id,
                error=str(exc),
                error_type=type(exc).__name__,
            )
            return True, 0  # fail open

    async def peek(self, user_id: int) -> int:
        """Return the current event count for *user_id* without recording a new event.

        Useful for monitoring, health checks, or pre-flight inspections where
        the request itself should not be counted.  Prunes expired members as
        a side effect so the count reflects the true active window.

        Args:
            user_id: The authenticated user's ID.

        Returns:
            Active event count within the window, or 0 on Redis errors.
        """
        now = time.time()
        window_start = now - self.window_seconds
        key = self._key(user_id)

        try:
            async with get_redis_context() as redis:
                pipe = redis.pipeline()
                pipe.zremrangebyscore(key, "-inf", window_start)
                pipe.zcard(key)
                results = await pipe.execute()
                count: int = results[1]  # zcard result
            return count

        except RedisError as exc:
            logger.warning(
                "rate_limiter.peek_redis_error",
                key_prefix=self.key_prefix,
                user_id=user_id,
                error=str(exc),
            )
            return 0

    async def reset(self, user_id: int) -> None:
        """Clear all rate-limit state for *user_id*.

        Intended for tests and admin tooling only — not called in normal
        request paths.

        Args:
            user_id: The user whose rate-limit counter to clear.
        """
        key = self._key(user_id)
        try:
            async with get_redis_context() as redis:
                await redis.delete(key)
            logger.info(
                "rate_limiter.reset",
                key_prefix=self.key_prefix,
                user_id=user_id,
            )
        except RedisError as exc:
            logger.warning(
                "rate_limiter.reset_redis_error",
                key_prefix=self.key_prefix,
                user_id=user_id,
                error=str(exc),
            )



_message_limiter: SlidingWindowRateLimiter | None = None
_write_limiter: SlidingWindowRateLimiter | None = None


def _get_message_limiter() -> SlidingWindowRateLimiter:
    global _message_limiter
    if _message_limiter is None:
        settings = get_settings()
        _message_limiter = SlidingWindowRateLimiter(
            key_prefix="rate:msgs",
            limit=settings.rate_limit_messages_per_minute,
            window_seconds=60,
        )
    return _message_limiter


def _get_write_limiter() -> SlidingWindowRateLimiter:
    global _write_limiter
    if _write_limiter is None:
        settings = get_settings()
        _write_limiter = SlidingWindowRateLimiter(
            key_prefix="rate:write_ops",
            limit=settings.rate_limit_write_ops,
            window_seconds=settings.rate_limit_write_window_seconds,
        )
    return _write_limiter


async def check_message_rate_limit(user_id: int) -> tuple[bool, int]:
    """Check the per-user **message** rate limit (20 msgs / 60 s by default).

    Delegates to the pre-configured message :class:`SlidingWindowRateLimiter`.
    Called by ``input_guard.guardrails_in_node`` before every user turn.

    Args:
        user_id: The authenticated user's ID (from JWT, never from LLM args).

    Returns:
        ``(is_allowed, current_count)``.  Fails open on Redis errors.
    """
    return await _get_message_limiter().check(user_id)


async def check_write_rate_limit(user_id: int) -> tuple[bool, int]:
    """Check the per-user **write-op** rate limit (3 ops / 300 s by default).

    Delegates to the pre-configured write :class:`SlidingWindowRateLimiter`.
    Called by ``tool_guard.apply_tool_guard`` before write tool execution.

    Args:
        user_id: The authenticated user's ID (from JWT, never from LLM args).

    Returns:
        ``(is_allowed, current_count)``.  Fails open on Redis errors.
    """
    return await _get_write_limiter().check(user_id)
