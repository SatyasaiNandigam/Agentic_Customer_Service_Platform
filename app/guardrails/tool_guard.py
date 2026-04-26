from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field

import structlog
from langchain_core.messages import HumanMessage
from redis.exceptions import RedisError

from app.agent.state import AgentState
from app.auth.rbac import PermissionDeniedError, assert_tool_allowed
from app.cache.redis_client import get_redis_context
from app.config import get_settings
from app.guardrails.rate_limiter import check_write_rate_limit

logger = structlog.get_logger(__name__)

# ---------------------------------------------------------------------------
# Tool classification
# ---------------------------------------------------------------------------
# Kept in sync with tool_executor.py — any new write tool must appear here.

_WRITE_TOOLS: frozenset[str] = frozenset(
    {"initiate_refund", "cancel_order", "force_initiate_refund", "force_cancel_order"}
)

_DESTRUCTIVE_TOOLS: frozenset[str] = frozenset(
    {"cancel_order", "force_cancel_order"}
)


def _classify_tool(tool_name: str) -> str:
    """Return ``'destructive'``, ``'write'``, or ``'read'`` for a tool name."""
    if tool_name in _DESTRUCTIVE_TOOLS:
        return "destructive"
    if tool_name in _WRITE_TOOLS:
        return "write"
    return "read"


def _is_write_tool(tool_name: str) -> bool:
    """Return True when the tool modifies data and requires a confirmation check."""
    return tool_name in _WRITE_TOOLS


# ---------------------------------------------------------------------------
# Confirmation keyword detection
# ---------------------------------------------------------------------------
# Keywords that unambiguously signal user consent for a pending write action.
# The check is case-insensitive; single-word matches anywhere in the message
# are enough — a customer saying "yes" or "okay" is sufficient.

_CONFIRMATION_KEYWORDS: frozenset[str] = frozenset(
    {
        "yes", "yeah", "yep", "yup", "sure", "ok", "okay",
        "confirm", "confirmed", "proceed", "go ahead", "go_ahead",
        "do it", "do_it", "cancel it", "cancel_it", "approve", "agreed",
        "please proceed", "yes please", "go for it",
    }
)

# Keywords that explicitly CANCEL a pending confirmation request
_DENIAL_KEYWORDS: frozenset[str] = frozenset(
    {
        "no", "nope", "nah", "cancel", "abort", "stop", "nevermind",
        "never mind", "don't", "dont", "not now", "skip", "decline",
    }
)


def _user_confirmed(last_human_text: str) -> bool:
    """Return True when the user's message matches a confirmation keyword."""
    normalised = last_human_text.lower().strip()
    # Check exact token match (handles multi-word phrases too)
    for keyword in _CONFIRMATION_KEYWORDS:
        if keyword in normalised:
            return True
    return False


def _user_denied(last_human_text: str) -> bool:
    """Return True when the user explicitly declines the pending action."""
    normalised = last_human_text.lower().strip()
    for keyword in _DENIAL_KEYWORDS:
        if keyword in normalised:
            return True
    return False


def _get_last_human_text(state: AgentState) -> str | None:
    """Extract the text content of the most recent HumanMessage, or None."""
    for msg in reversed(state["messages"]):
        if isinstance(msg, HumanMessage):
            content = msg.content
            if isinstance(content, str):
                return content.strip() or None
            if isinstance(content, list):
                parts = [
                    block["text"]
                    for block in content
                    if isinstance(block, dict) and block.get("type") == "text"
                ]
                combined = " ".join(parts).strip()
                return combined or None
    return None


# ---------------------------------------------------------------------------
# Redis key helpers
# ---------------------------------------------------------------------------


def _write_rate_key(user_id: int) -> str:
    """Sorted-set key for per-user write-op rate limiting."""
    return f"rate:write_ops:{user_id}"


def _pending_confirm_key(session_id: str, tool_name: str) -> str:
    """String key for a pending write confirmation record.

    Scoped to session + tool so a cancel_order confirmation does not
    accidentally unblock an initiate_refund call in the same session.
    """
    return f"conv:{session_id}:pending_confirm:{tool_name}"


def _hash_tool_input(tool_input: dict) -> str:
    """Return a short deterministic fingerprint of the tool input arguments.

    Used to detect when the pending confirmation matches the current call's
    arguments (guard against a replay where the LLM re-plans different args).
    """
    serialised = json.dumps(tool_input, sort_keys=True, default=str)
    return hashlib.md5(serialised.encode(), usedforsecurity=False).hexdigest()[:12]


# ---------------------------------------------------------------------------
# Confirmation messages shown to the user
# ---------------------------------------------------------------------------

_CONFIRMATION_PROMPTS: dict[str, str] = {
    "cancel_order": (
        "I can cancel your order for you.  Before I proceed, please confirm: "
        "reply **YES** to cancel this order, or **NO** to keep it."
    ),
    "force_cancel_order": (
        "You are about to force-cancel this order.  This action cannot be undone.  "
        "Reply **YES** to proceed or **NO** to abort."
    ),
    "initiate_refund": (
        "I can initiate a refund for you.  Please confirm: "
        "reply **YES** to start the refund process, or **NO** to cancel."
    ),
    "force_initiate_refund": (
        "You are about to force-initiate a refund.  "
        "Reply **YES** to proceed or **NO** to abort."
    ),
}

_DEFAULT_CONFIRMATION_PROMPT: str = (
    "I need your confirmation before proceeding with this action.  "
    "Reply **YES** to confirm or **NO** to cancel."
)

# ---------------------------------------------------------------------------
# Result type
# ---------------------------------------------------------------------------


@dataclass
class ToolGuardResult:
    """Result returned by :func:`apply_tool_guard`.

    Attributes:
        allowed:              True when the tool call may proceed.
        requires_confirmation: True when the call is pending user confirmation.
                               ``tool_executor_node`` should exhaust the retry
                               budget so the graph routes to response_generator.
        violation_type:       Machine-readable label for the block reason.
                              None when ``allowed=True``.
        user_message:         Human-readable message to surface to the user
                              (confirmation prompt or rejection reason).
                              None when ``allowed=True``.
    """

    allowed: bool
    requires_confirmation: bool = False
    violation_type: str | None = None
    user_message: str | None = None


# ---------------------------------------------------------------------------
# Layer 1 — RBAC check (synchronous)
# ---------------------------------------------------------------------------


def check_tool_rbac(role: str, tool_name: str) -> str | None:
    """Return a violation string if *role* is not permitted to call *tool_name*.

    Delegates to :func:`app.auth.rbac.assert_tool_allowed`.

    Args:
        role:      User's role from the JWT (``customer``, ``support_agent``,
                   ``admin``).
        tool_name: Name of the tool about to be called.

    Returns:
        ``None`` when access is granted, or a short human-readable denial
        string when it is not.
    """
    try:
        assert_tool_allowed(role, tool_name)  # type: ignore[arg-type]
        return None
    except PermissionDeniedError as exc:
        return str(exc)


# ---------------------------------------------------------------------------
# Layer 3 — Write confirmation flow (Redis)
# ---------------------------------------------------------------------------


async def _get_pending_confirmation(session_id: str, tool_name: str) -> str | None:
    """Return the stored input hash for a pending confirmation, or None.

    Args:
        session_id: Current session identifier.
        tool_name:  Name of the write tool requiring confirmation.

    Returns:
        The input hash stored when the confirmation was requested, or ``None``
        if no pending confirmation exists (expired or never set).
        Returns ``None`` also on Redis errors (fails open).
    """
    key = _pending_confirm_key(session_id, tool_name)
    try:
        async with get_redis_context() as redis:
            value: str | None = await redis.get(key)
        return value
    except RedisError as exc:
        logger.warning(
            "tool_guard.get_confirmation_redis_error",
            session_id=session_id,
            tool_name=tool_name,
            error=str(exc),
        )
        return None


async def _set_pending_confirmation(
    session_id: str,
    tool_name: str,
    input_hash: str,
    ttl: int = 300,
) -> None:
    """Store a pending confirmation record in Redis.

    Args:
        session_id:  Current session identifier.
        tool_name:   Name of the write tool awaiting confirmation.
        input_hash:  Fingerprint of the tool input arguments.
        ttl:         Seconds until the confirmation request expires (default: 5 min).

    Silently ignores Redis errors — a failed set means the confirmation flow
    will re-request on the next call (one extra round-trip; not a security risk).
    """
    key = _pending_confirm_key(session_id, tool_name)
    try:
        async with get_redis_context() as redis:
            await redis.set(key, input_hash, ex=ttl)
    except RedisError as exc:
        logger.warning(
            "tool_guard.set_confirmation_redis_error",
            session_id=session_id,
            tool_name=tool_name,
            error=str(exc),
        )


async def _clear_pending_confirmation(session_id: str, tool_name: str) -> None:
    """Delete the pending confirmation record after it has been consumed.

    Args:
        session_id: Current session identifier.
        tool_name:  Name of the write tool whose confirmation is being cleared.
    """
    key = _pending_confirm_key(session_id, tool_name)
    try:
        async with get_redis_context() as redis:
            await redis.delete(key)
    except RedisError as exc:
        logger.warning(
            "tool_guard.clear_confirmation_redis_error",
            session_id=session_id,
            tool_name=tool_name,
            error=str(exc),
        )


# ---------------------------------------------------------------------------
# Composite guard function
# ---------------------------------------------------------------------------


async def apply_tool_guard(state: AgentState) -> ToolGuardResult:
    """Run all three pre-execution guard layers for the currently selected tool.

    Applies RBAC → write rate limit → confirmation flow, in that order.
    Returns on the first failure so the cheapest checks run first.

    This function is idempotent — calling it multiple times with the same
    state is safe (confirmation state lives in Redis, not in the AgentState).

    Args:
        state: Full AgentState.  Must have ``selected_tool``, ``tool_input``,
               ``user_id``, ``user_role``, and ``session_id`` set.

    Returns:
        :class:`ToolGuardResult`.  When ``allowed=True``, the tool may proceed.
        When ``allowed=False``, ``violation_type`` and ``user_message`` describe
        why execution was blocked.
    """
    selected_tool: str | None = state.get("selected_tool")
    tool_input: dict = state.get("tool_input") or {}
    user_id: int = state.get("user_id", 0)
    user_role: str = state.get("user_role", "customer")
    session_id: str = state.get("session_id", "")

    log = logger.bind(
        user_id=user_id,
        session_id=session_id,
        selected_tool=selected_tool,
        tool_type=_classify_tool(selected_tool) if selected_tool else "unknown",
        user_role=user_role,
    )

    # Guard: must have a tool selected
    if not selected_tool:
        log.error("tool_guard.no_tool_selected")
        return ToolGuardResult(
            allowed=False,
            violation_type="no_tool_selected",
            user_message="No tool was selected for execution.",
        )

    # ------------------------------------------------------------------
    # Layer 1: RBAC check
    # ------------------------------------------------------------------
    rbac_error = check_tool_rbac(user_role, selected_tool)
    if rbac_error:
        log.warning(
            "tool_guard.rbac_denied",
            tool_name=selected_tool,
            user_role=user_role,
            error=rbac_error,
        )
        return ToolGuardResult(
            allowed=False,
            violation_type="rbac_denied",
            user_message=(
                f"You don't have permission to perform that action. "
                f"If you believe this is an error, please contact support."
            ),
        )

    # ------------------------------------------------------------------
    # Layer 2: Write rate limit (only for write/destructive tools)
    # ------------------------------------------------------------------
    if _is_write_tool(selected_tool):
        is_allowed, write_count = await check_write_rate_limit(user_id)
        if not is_allowed:
            settings = get_settings()
            log.warning(
                "tool_guard.write_rate_limit_exceeded",
                tool_name=selected_tool,
                write_count=write_count,
                limit=settings.rate_limit_write_ops,
                window_seconds=settings.rate_limit_write_window_seconds,
            )
            return ToolGuardResult(
                allowed=False,
                violation_type="write_rate_limit_exceeded",
                user_message=(
                    "You've made too many changes recently. "
                    f"Please wait a few minutes before trying again."
                ),
            )

    # ------------------------------------------------------------------
    # Layer 3: Write confirmation flow (only for write/destructive tools)
    # ------------------------------------------------------------------
    if _is_write_tool(selected_tool):
        input_hash = _hash_tool_input(tool_input)
        stored_hash = await _get_pending_confirmation(session_id, selected_tool)

        if stored_hash is None:
            # No pending confirmation — request one
            await _set_pending_confirmation(session_id, selected_tool, input_hash)
            prompt = _CONFIRMATION_PROMPTS.get(selected_tool, _DEFAULT_CONFIRMATION_PROMPT)
            log.info(
                "tool_guard.confirmation_requested",
                tool_name=selected_tool,
                input_hash=input_hash,
            )
            return ToolGuardResult(
                allowed=False,
                requires_confirmation=True,
                violation_type="awaiting_confirmation",
                user_message=prompt,
            )

        # Pending confirmation exists — check the user's latest reply
        last_human_text = _get_last_human_text(state) or ""

        if _user_denied(last_human_text):
            # User explicitly declined — clear confirmation and block
            await _clear_pending_confirmation(session_id, selected_tool)
            log.info(
                "tool_guard.confirmation_declined",
                tool_name=selected_tool,
            )
            return ToolGuardResult(
                allowed=False,
                violation_type="confirmation_declined",
                user_message=(
                    "No problem — I won't proceed with that action. "
                    "Is there anything else I can help you with?"
                ),
            )

        if _user_confirmed(last_human_text):
            # User confirmed — consume the pending record and allow execution
            await _clear_pending_confirmation(session_id, selected_tool)
            log.info(
                "tool_guard.confirmation_granted",
                tool_name=selected_tool,
                input_hash_match=(stored_hash == input_hash),
            )
            # Allow execution — fall through to the allowed=True return below

        else:
            # User's reply is ambiguous — re-request confirmation
            prompt = _CONFIRMATION_PROMPTS.get(selected_tool, _DEFAULT_CONFIRMATION_PROMPT)
            log.info(
                "tool_guard.confirmation_ambiguous",
                tool_name=selected_tool,
                last_human_preview=last_human_text[:60],
            )
            return ToolGuardResult(
                allowed=False,
                requires_confirmation=True,
                violation_type="awaiting_confirmation",
                user_message=(
                    "I didn't quite catch that. " + prompt
                ),
            )

    # ------------------------------------------------------------------
    # All layers passed — execution allowed
    # ------------------------------------------------------------------
    log.info(
        "tool_guard.allowed",
        tool_name=selected_tool,
        tool_type=_classify_tool(selected_tool),
    )
    return ToolGuardResult(allowed=True)
