from __future__ import annotations

import uuid as _uuid_lib
from dataclasses import dataclass
from typing import Literal

from fastmcp import Context

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

VALID_ROLES: frozenset[str] = frozenset({"customer", "support_agent", "admin"})

_HEADER_USER_ID = "x-user-id"    # HTTP headers are lower-cased by most frameworks
_HEADER_USER_ROLE = "x-user-role"


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

@dataclass(frozen=True, slots=True)
class UserContext:
    """Authenticated caller extracted from MCP request headers."""

    user_id: str
    role: Literal["customer", "support_agent", "admin"]

    def is_admin(self) -> bool:
        return self.role == "admin"

    def is_support_agent(self) -> bool:
        return self.role in ("support_agent", "admin")

    def is_customer(self) -> bool:
        return self.role == "customer"


# ---------------------------------------------------------------------------
# Error
# ---------------------------------------------------------------------------

class MCPAuthError(Exception):
    """Raised when a required auth header is missing or invalid.

    Callers (tool functions) should let this propagate — FastMCP will surface
    it as an MCP error response to the agent, which treats it as a tool failure.
    """

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = 401  # informational — not directly used by FastMCP transport


# ---------------------------------------------------------------------------
# Public helper
# ---------------------------------------------------------------------------

def get_user_context(ctx: Context) -> UserContext:
    """Extract and validate caller identity from MCP request headers.

    Args:
        ctx: FastMCP tool context, populated from the inbound HTTP request.

    Returns:
        Frozen :class:`UserContext` with ``user_id`` and ``role``.

    Raises:
        MCPAuthError: If either required header is absent, ``X-User-Id`` is not
            a valid integer, or ``X-User-Role`` is not a recognised role string.
    """
    headers: dict[str, str] = dict(ctx.request_context.request.headers)

    # --- user_id ---
    raw_user_id = headers.get(_HEADER_USER_ID) or headers.get("X-User-Id")
    if not raw_user_id:
        raise MCPAuthError(
            "Missing required header 'X-User-Id'. "
            "Ensure the agent is forwarding JWT-derived headers."
        )

    try:
        _uuid_lib.UUID(raw_user_id)
    except ValueError:
        raise MCPAuthError(
            f"Header 'X-User-Id' must be a valid UUID, got: {raw_user_id!r}"
        )
    user_id = raw_user_id

    # --- role ---
    role = headers.get(_HEADER_USER_ROLE) or headers.get("X-User-Role")
    if not role:
        raise MCPAuthError(
            "Missing required header 'X-User-Role'. "
            "Ensure the agent is forwarding JWT-derived headers."
        )

    role = role.strip().lower()
    if role not in VALID_ROLES:
        raise MCPAuthError(
            f"Header 'X-User-Role' contains unrecognised role {role!r}. "
            f"Must be one of: {sorted(VALID_ROLES)}"
        )

    return UserContext(user_id=user_id, role=role)  # type: ignore[arg-type]
