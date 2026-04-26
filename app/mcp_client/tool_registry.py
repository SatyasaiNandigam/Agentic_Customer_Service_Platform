"""Tool registry — agent side.

Caches LangChain tool objects returned by the MCP server so that
``tool_planner`` nodes don't reconnect and re-fetch schemas on every graph
invocation.

Why in-memory and not Redis?
    Tool schemas are Python ``BaseTool`` objects — they carry live callable
    references and cannot be JSON-serialised into Redis.  They are also
    stable for the lifetime of the MCP server process (registered at import
    time in ``tools_mcp/server.py``), so an in-process dict is the right
    storage tier.

Cache key: ``user_role``
    Tool *schemas* (names, descriptions, input definitions) are the same for
    every user in the same role.  Only tool *execution* is user-scoped
    (enforced by the ``X-User-Id`` header at call time).  Keying by role
    means we only fetch each unique schema once per process lifetime.

Lifecycle (plug into ``app/main.py`` lifespan)::

    # startup
    await warmup_tool_registry()   # pre-warm "customer", "support_agent", "admin"

    # per-turn (inside tool_planner node)
    tools = await get_registry_tools(user_id=state["user_id"],
                                     user_role=state["user_role"])

    # shutdown (optional — GC handles it, but explicit is cleaner)
    clear_tool_registry()
"""

from __future__ import annotations

import asyncio
from typing import Final

import structlog
from langchain_core.tools import BaseTool

from app.mcp_client.client import get_tools_for_user

logger = structlog.get_logger(__name__)



# All roles that should be pre-warmed at startup.
ALL_ROLES: Final[tuple[str, ...]] = ("customer", "support_agent", "admin")

# Sentinel user_id used *only* for schema warmup — we just need the tool list,
# not user-scoped data.  The MCP server's tool schemas don't change per user.
_WARMUP_USER_ID: Final[int] = 0


# Maps role → list of LangChain BaseTool objects.
_REGISTRY: dict[str, list[BaseTool]] = {}

# Per-role locks prevent concurrent coroutines from issuing duplicate fetches
# for the same role (e.g. many simultaneous first requests under the same role).
_LOCKS: dict[str, asyncio.Lock] = {role: asyncio.Lock() for role in ALL_ROLES}
_DEFAULT_LOCK: asyncio.Lock = asyncio.Lock()  # for unexpected roles


def _get_lock(role: str) -> asyncio.Lock:
    """Return the per-role lock, creating one on first access for unknown roles."""
    if role not in _LOCKS:
        _LOCKS[role] = asyncio.Lock()
    return _LOCKS[role]



async def _fetch_and_cache(user_id: int, user_role: str) -> list[BaseTool]:
    """Fetch schemas from the MCP server and store in ``_REGISTRY``.

    Must be called while holding the per-role lock to avoid duplicate fetches.
    """
    tools = await get_tools_for_user(user_id=user_id, user_role=user_role)
    _REGISTRY[user_role] = tools
    logger.info(
        "tool_registry.cached",
        user_role=user_role,
        tool_count=len(tools),
        tool_names=[t.name for t in tools],
    )
    return tools



async def warmup_tool_registry(
    roles: tuple[str, ...] | list[str] | None = None,
) -> None:
    """Pre-warm the registry for the given roles (default: all three roles).

    Call this once in the FastAPI lifespan startup handler so the first real
    user request never pays the MCP connection overhead.

    The warmup uses ``_WARMUP_USER_ID = 0`` because we only need the tool
    *schemas* — execution-time data access is still scoped per user via the
    ``X-User-Id`` header on each tool call.

    Args:
        roles: Roles to pre-warm.  Defaults to ``ALL_ROLES``
               (``"customer"``, ``"support_agent"``, ``"admin"``).
    """
    target_roles = list(roles) if roles is not None else list(ALL_ROLES)
    logger.info("tool_registry.warmup_start", roles=target_roles)

    results: list[str] = []
    errors: list[str] = []

    for role in target_roles:
        lock = _get_lock(role)
        async with lock:
            if role in _REGISTRY:
                # Already populated by a concurrent warmup call — skip.
                logger.debug("tool_registry.warmup_skip", role=role, reason="already_cached")
                results.append(role)
                continue
            try:
                await _fetch_and_cache(user_id=_WARMUP_USER_ID, user_role=role)
                results.append(role)
            except Exception as exc:
                logger.warning(
                    "tool_registry.warmup_failed",
                    role=role,
                    error=str(exc),
                )
                errors.append(role)

    logger.info(
        "tool_registry.warmup_complete",
        warmed=results,
        failed=errors,
    )
    if errors:
        # Non-fatal: the registry falls back to live fetch on first real request.
        logger.warning(
            "tool_registry.warmup_partial",
            detail="Failed roles will be fetched live on first request.",
            failed=errors,
        )


async def get_registry_tools(user_id: int, user_role: str) -> list[BaseTool]:
    """Return the cached tool list for *user_role*, fetching live if not cached.

    This is the primary call site for ``tool_planner``.  It avoids SSE
    connection overhead on every graph invocation by serving from the
    in-process cache for all but the very first request per role.

    Args:
        user_id:   Authenticated user PK — only used if a live fetch is needed
                   (cache miss).  Not used for cache lookup; roles are the key.
        user_role: ``"customer"`` | ``"support_agent"`` | ``"admin"``.

    Returns:
        List of LangChain-compatible ``BaseTool`` objects ready for
        ``llm.bind_tools(tools)``.
    """
    # Fast path — already cached (no lock needed for a pure read)
    if user_role in _REGISTRY:
        logger.debug(
            "tool_registry.cache_hit",
            user_role=user_role,
            tool_count=len(_REGISTRY[user_role]),
        )
        return _REGISTRY[user_role]

    # Slow path — first request for this role; acquire lock to prevent stampede
    lock = _get_lock(user_role)
    async with lock:
        # Re-check inside the lock — another coroutine may have populated it
        # while we were waiting.
        if user_role in _REGISTRY:
            return _REGISTRY[user_role]

        logger.info(
            "tool_registry.cache_miss",
            user_role=user_role,
            user_id=user_id,
            detail="Fetching live from MCP server.",
        )
        return await _fetch_and_cache(user_id=user_id, user_role=user_role)


def clear_tool_registry() -> None:
    """Clear the in-memory registry.

    Call from the FastAPI lifespan shutdown handler (or in tests between runs)
    to release references to ``BaseTool`` objects.  The registry will
    repopulate on the next ``get_registry_tools`` call.
    """
    count = len(_REGISTRY)
    _REGISTRY.clear()
    logger.info("tool_registry.cleared", previous_role_count=count)


def registry_status() -> dict[str, int]:
    """Return a snapshot of cached roles and their tool counts.

    Useful for the ``/ready`` health endpoint to confirm the registry is warm.

    Returns:
        Dict mapping role name → number of cached tools.
        Empty dict means nothing has been warmed yet.

    Example::

        {"customer": 10, "support_agent": 10, "admin": 10}
    """
    return {role: len(tools) for role, tools in _REGISTRY.items()}
