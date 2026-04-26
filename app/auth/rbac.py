"""Role-Based Access Control (RBAC) for tool permissions.

Defines which tools each role may call. The SecureTool base class
(app/tools/base.py) will check these permissions before executing any tool.

Role hierarchy (least → most privileged):
    customer < support_agent < admin
"""

from typing import Literal

# ---------------------------------------------------------------------------
# Type alias
# ---------------------------------------------------------------------------

Role = Literal["customer", "support_agent", "admin"]

# ---------------------------------------------------------------------------
# Tool permission matrix
# ---------------------------------------------------------------------------
# Each role entry lists the tool names it is ALLOWED to call.
# support_agent inherits all customer tools plus its own.
# admin inherits everything.

_CUSTOMER_TOOLS: frozenset[str] = frozenset(
    {
        # Read — own data only (user-scoped queries enforce WHERE user_id = ...)
        "get_orders",
        "get_order_items",
        "track_shipment",
        "get_refund_status",
        "get_account_info",
        # Read — public data (no user scoping required)
        "search_products",
        "get_product_detail",
        "get_reviews",
        # Write — own data only (confirmation flow enforced in tool layer)
        "initiate_refund",
        "cancel_order",
    }
)

_SUPPORT_AGENT_TOOLS: frozenset[str] = _CUSTOMER_TOOLS | frozenset(
    {
        # Support agents can look up any customer's orders/refunds without
        # being the resource owner — user-scoping is relaxed at the query level
        # when role == "support_agent".
        "get_orders_any_user",
        "get_refund_status_any_user",
        "track_shipment_any_user",
    }
)

_ADMIN_TOOLS: frozenset[str] = _SUPPORT_AGENT_TOOLS | frozenset(
    {
        # Admins can take destructive actions and access aggregated data.
        "force_cancel_order",
        "force_initiate_refund",
        "get_all_reviews",
    }
)

ROLE_PERMISSIONS: dict[Role, frozenset[str]] = {
    "customer": _CUSTOMER_TOOLS,
    "support_agent": _SUPPORT_AGENT_TOOLS,
    "admin": _ADMIN_TOOLS,
}

# ---------------------------------------------------------------------------
# Permission checks
# ---------------------------------------------------------------------------


class PermissionDeniedError(Exception):
    """Raised when a role attempts to call a tool it is not permitted to use."""


def is_tool_allowed(role: Role, tool_name: str) -> bool:
    """Return True if *role* may call *tool_name*.

    Args:
        role:      The authenticated user's role from the JWT.
        tool_name: The name of the tool being invoked.

    Returns:
        True if the role has permission, False otherwise.
    """
    allowed = ROLE_PERMISSIONS.get(role, frozenset())
    return tool_name in allowed


def assert_tool_allowed(role: Role, tool_name: str) -> None:
    """Raise PermissionDeniedError if *role* may not call *tool_name*.

    Args:
        role:      The authenticated user's role from the JWT.
        tool_name: The name of the tool being invoked.

    Raises:
        PermissionDeniedError: If the role lacks permission.
    """
    if not is_tool_allowed(role, tool_name):
        raise PermissionDeniedError(
            f"Role '{role}' is not permitted to call tool '{tool_name}'."
        )


def get_allowed_tools(role: Role) -> frozenset[str]:
    """Return the full set of tool names permitted for *role*.

    Args:
        role: The authenticated user's role.

    Returns:
        Frozenset of allowed tool names.
    """
    return ROLE_PERMISSIONS.get(role, frozenset())
