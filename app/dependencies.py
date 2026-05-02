"""Shared FastAPI dependencies for the agent API.

Each symbol here is designed to be dropped into an endpoint signature via
``Depends()`` or the ``Annotated`` type-alias pattern.  Centralising them means
cross-cutting concerns (auth, rate-limiting, graph injection) are tested and
changed in one place rather than scattered across every route handler.
"""
from typing import Annotated, Any

from fastapi import Depends, HTTPException, Request, status

from app.auth.middleware import CurrentUser
from app.auth.service import TokenData
from app.config import get_settings
from app.guardrails.rate_limiter import peek_message_rate_limit


# ---------------------------------------------------------------------------
# Graph injection
# ---------------------------------------------------------------------------


async def get_agent_graph(request: Request) -> Any:
    """Provide the compiled LangGraph agent from app lifespan state."""
    return request.app.state.graph


AgentGraph = Annotated[Any, Depends(get_agent_graph)]


# ---------------------------------------------------------------------------
# Rate-limited user
# ---------------------------------------------------------------------------


async def _enforce_message_rate_limit(user: CurrentUser) -> TokenData:
    """Raise HTTP 429 before graph invocation when the user is over the message limit.

    Uses ``peek()`` (read-only) so this pre-check does not add an event entry —
    the authoritative recording still happens inside ``guardrails_in_node`` via
    ``check_message_rate_limit()``.  This avoids double-counting while still
    letting obviously over-limit requests be rejected cheaply at the API boundary
    before any graph resources are consumed.

    Returns the authenticated ``TokenData`` on success so it can replace
    ``CurrentUser`` in endpoint signatures transparently.
    """
    settings = get_settings()
    limit = settings.rate_limit_messages_per_minute
    count = await peek_message_rate_limit(user.user_id)

    if count >= limit:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=(
                f"Rate limit exceeded: {count}/{limit} messages in the last 60 seconds. "
                "Please wait before sending another message."
            ),
            headers={"Retry-After": "60"},
        )

    return user


RateLimitedUser = Annotated[TokenData, Depends(_enforce_message_rate_limit)]
