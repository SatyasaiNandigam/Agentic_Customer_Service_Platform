"""Short-term memory — Redis hot storage for active chat sessions.

Every active session keeps two Redis keys:

``conv:{session_id}:messages``  (Redis List)
    Stores the last ``session_max_messages`` (default 50) messages as
    JSON-encoded dicts.  Serialised with LangChain's ``messages_to_dict``
    so the list can be round-tripped back to ``BaseMessage`` objects.

``conv:{session_id}:meta``  (Redis Hash)
    Lightweight metadata about the session:
      - ``user_id``   — authenticated user ID
      - ``intent``    — last classified intent
      - ``summary``   — latest rolling summary text (if any)
      - ``updated_at`` — ISO timestamp of last write

Both keys use a sliding TTL (``session_ttl_seconds``, default 7200 s / 2 h)
that is refreshed on every write so idle-session cleanup happens automatically.

Public API
----------
``get_session_messages(session_id, limit)``
    Read the last *limit* messages from Redis.  Returns ``[]`` on cache miss
    or Redis error (fail-open).

``append_message(session_id, message)``
    Append one message to the list, trim to ``session_max_messages``, and
    refresh the TTL.

``load_session_context(session_id)``
    Read ``conv:{session_id}:meta`` and return a dict.

``save_session_context(session_id, **fields)``
    Write (HSET) arbitrary fields to the meta hash and refresh the TTL.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone

import structlog
from langchain_core.messages import BaseMessage
from langchain_core.messages import messages_from_dict, messages_to_dict
from redis.exceptions import RedisError

from app.cache.redis_client import get_redis_context
from app.config import get_settings

logger = structlog.get_logger(__name__)


# ---------------------------------------------------------------------------
# Key helpers
# ---------------------------------------------------------------------------


def _messages_key(session_id: str) -> str:
    return f"conv:{session_id}:messages"


def _meta_key(session_id: str) -> str:
    return f"conv:{session_id}:meta"


# ---------------------------------------------------------------------------
# Message list helpers
# ---------------------------------------------------------------------------


async def get_session_messages(
    session_id: str,
    limit: int | None = None,
) -> list[BaseMessage]:
    """Load messages from the Redis session list.

    Args:
        session_id: The session identifier (``state["session_id"]``).
        limit:      Maximum number of recent messages to return.  Defaults to
                    ``settings.session_max_messages`` (50).  Pass a smaller
                    value (e.g. 20) to trim the context passed to the LLM.

    Returns:
        List of :class:`BaseMessage` objects in chronological order (oldest
        first).  Returns ``[]`` on cache miss or Redis error.
    """
    settings = get_settings()
    effective_limit = limit if limit is not None else settings.session_max_messages
    key = _messages_key(session_id)

    try:
        async with get_redis_context() as redis:
            # LRANGE 0 -1 returns the full list; we take the last N items
            raw_items: list[bytes] = await redis.lrange(key, -effective_limit, -1)

        messages: list[BaseMessage] = []
        for raw in raw_items:
            try:
                msg_dict = json.loads(raw)
                parsed = messages_from_dict([msg_dict])
                messages.extend(parsed)
            except (json.JSONDecodeError, KeyError, ValueError) as exc:
                logger.warning(
                    "short_term.deserialize_error",
                    session_id=session_id,
                    error=str(exc),
                )
        return messages

    except RedisError as exc:
        logger.warning(
            "short_term.get_messages_redis_error",
            session_id=session_id,
            error=str(exc),
        )
        return []


async def append_message(session_id: str, message: BaseMessage) -> None:
    """Append a single message to the session list and refresh the TTL.

    Serialises the message with LangChain's ``messages_to_dict`` so any
    message type (HumanMessage, AIMessage, ToolMessage, etc.) round-trips
    correctly.

    After appending, the list is trimmed to ``session_max_messages`` items
    from the right (most recent) so the key never grows unbounded.

    Args:
        session_id: The session identifier.
        message:    Any :class:`BaseMessage` subclass.
    """
    settings = get_settings()
    key = _messages_key(session_id)
    ttl = settings.session_ttl_seconds
    max_messages = settings.session_max_messages

    try:
        serialised = json.dumps(messages_to_dict([message])[0])
    except (TypeError, ValueError) as exc:
        logger.error(
            "short_term.serialize_error",
            session_id=session_id,
            message_type=type(message).__name__,
            error=str(exc),
        )
        return

    try:
        async with get_redis_context() as redis:
            pipe = redis.pipeline()
            pipe.rpush(key, serialised)
            # Keep only the last max_messages entries (trim from the left)
            pipe.ltrim(key, -max_messages, -1)
            pipe.expire(key, ttl)
            await pipe.execute()

        logger.debug(
            "short_term.message_appended",
            session_id=session_id,
            role=message.type,
        )

    except RedisError as exc:
        logger.warning(
            "short_term.append_redis_error",
            session_id=session_id,
            error=str(exc),
        )


async def append_messages(session_id: str, messages: list[BaseMessage]) -> None:
    """Append multiple messages in a single pipeline call.

    Convenience wrapper around :func:`append_message` that batches all
    serialisation and Redis operations into one round-trip.

    Args:
        session_id: The session identifier.
        messages:   List of messages to append (in order, oldest first).
    """
    if not messages:
        return

    settings = get_settings()
    key = _messages_key(session_id)
    ttl = settings.session_ttl_seconds
    max_messages = settings.session_max_messages

    serialised_items: list[str] = []
    for msg in messages:
        try:
            serialised_items.append(json.dumps(messages_to_dict([msg])[0]))
        except (TypeError, ValueError) as exc:
            logger.warning(
                "short_term.serialize_error",
                session_id=session_id,
                message_type=type(msg).__name__,
                error=str(exc),
            )

    if not serialised_items:
        return

    try:
        async with get_redis_context() as redis:
            pipe = redis.pipeline()
            pipe.rpush(key, *serialised_items)
            pipe.ltrim(key, -max_messages, -1)
            pipe.expire(key, ttl)
            await pipe.execute()

    except RedisError as exc:
        logger.warning(
            "short_term.append_batch_redis_error",
            session_id=session_id,
            error=str(exc),
        )


# ---------------------------------------------------------------------------
# Session metadata helpers
# ---------------------------------------------------------------------------


async def load_session_context(session_id: str) -> dict[str, str]:
    """Read all fields from the session meta hash.

    Args:
        session_id: The session identifier.

    Returns:
        Dict of field→value strings, or ``{}`` if the key does not exist or
        Redis is unavailable.
    """
    key = _meta_key(session_id)
    try:
        async with get_redis_context() as redis:
            data: dict[bytes, bytes] = await redis.hgetall(key)
        return {k.decode(): v.decode() for k, v in data.items()}

    except RedisError as exc:
        logger.warning(
            "short_term.load_context_redis_error",
            session_id=session_id,
            error=str(exc),
        )
        return {}


async def save_session_context(session_id: str, **fields: str | int | None) -> None:
    """Write fields to the session meta hash and refresh the TTL.

    Any field whose value is ``None`` is skipped — this prevents accidentally
    overwriting a stored value with a null.

    Args:
        session_id: The session identifier.
        **fields:   Keyword arguments become hash field→value pairs.
                    Values are coerced to strings before storage.

    Example::

        await save_session_context(
            session_id,
            user_id=42,
            intent="order_status",
            summary="Customer asked about order #1234.",
        )
    """
    settings = get_settings()
    key = _meta_key(session_id)
    ttl = settings.session_ttl_seconds

    # Filter out None values and stringify
    payload: dict[str, str] = {
        k: str(v)
        for k, v in fields.items()
        if v is not None
    }
    payload["updated_at"] = datetime.now(tz=timezone.utc).isoformat()

    if not payload:
        return

    try:
        async with get_redis_context() as redis:
            pipe = redis.pipeline()
            pipe.hset(key, mapping=payload)
            pipe.expire(key, ttl)
            await pipe.execute()

        logger.debug(
            "short_term.context_saved",
            session_id=session_id,
            fields=list(payload.keys()),
        )

    except RedisError as exc:
        logger.warning(
            "short_term.save_context_redis_error",
            session_id=session_id,
            error=str(exc),
        )


async def delete_session(session_id: str) -> None:
    """Remove all Redis keys for a session.

    Called after a successful flush to PostgreSQL so that stale data does not
    persist in Redis beyond the regular TTL.

    Args:
        session_id: The session identifier.
    """
    messages_key = _messages_key(session_id)
    meta_key = _meta_key(session_id)

    try:
        async with get_redis_context() as redis:
            await redis.delete(messages_key, meta_key)
        logger.info("short_term.session_deleted", session_id=session_id)

    except RedisError as exc:
        logger.warning(
            "short_term.delete_redis_error",
            session_id=session_id,
            error=str(exc),
        )
