"""Intent-based tool scope filtering for the tool_planner node.

The tool registry returns the full tool list from the MCP server regardless of
role — RBAC is enforced at execution time via JWT headers. This module narrows
that list further based on the classified intent so the LLM only sees tools that
are relevant to the current goal, which:

  - eliminates wrong-category selections (e.g. get_order_detail for order_cancel)
  - makes admin-language fallback automatic for customer role (only the customer
    tier tool exists in scope, so the model must use it)
  - reduces prompt token count and inference latency per call
"""

from __future__ import annotations

from langchain_core.tools import BaseTool

# ---------------------------------------------------------------------------
# Direct-response intents — no tool call should ever be made
# ---------------------------------------------------------------------------

# These intents are answered from static knowledge or LLM reasoning alone.
# In the live graph the router sends them straight to the response generator,
# bypassing the tool_planner entirely. The node uses this set for an early
# return so the LLM is never invoked for these cases.
NO_TOOL_INTENTS: frozenset[str] = frozenset({
    "chitchat",
    "faq_policy",
    "unknown",
    "complaint",
})

# ---------------------------------------------------------------------------
# Scope maps
# ---------------------------------------------------------------------------

# Customer-accessible tools per intent.
INTENT_TOOL_SCOPE: dict[str, list[str]] = {
    "order_status":      ["get_orders", "get_order_items"],
    "order_cancel":      ["cancel_order"],
    "shipment_tracking": ["track_shipment"],
    "refund_request":    ["initiate_refund"],
    "refund_status":     ["get_refund_status"],
    "product_inquiry":   ["get_product_detail"],
    "product_search":    ["search_products"],
    "account_info":      ["get_account_info"],
    "review_lookup":     ["get_reviews"],
}

# Extra tools added for support_agent (and admin) on top of customer scope.
_SUPPORT_ADDITIONS: dict[str, list[str]] = {
    "order_status":      ["get_orders_any_user"],
    "refund_status":     ["get_refund_status_any_user"],
    "shipment_tracking": ["track_shipment_any_user"],
}

# Extra tools added for admin only, on top of support additions.
_ADMIN_ADDITIONS: dict[str, list[str]] = {
    "order_cancel":   ["force_cancel_order"],
    "refund_request": ["force_initiate_refund"],
    "review_lookup":  ["get_all_reviews"],
}


# ---------------------------------------------------------------------------
# Public helper
# ---------------------------------------------------------------------------

def scope_tools_for_intent(
    tools: list[BaseTool],
    intent: str,
    user_role: str,
) -> list[BaseTool]:
    """Return the subset of *tools* allowed for the given intent and role.

    If the intent is not in the scope map (e.g. chitchat, faq_policy — the
    tool_planner should not be called for these, but this handles it safely)
    the full list is returned unchanged.

    Args:
        tools:     Full tool list from the registry.
        intent:    Classified intent from AgentState.
        user_role: "customer" | "support_agent" | "admin"

    Returns:
        Filtered list, preserving original order.
    """
    allowed: set[str] = set(INTENT_TOOL_SCOPE.get(intent, []))

    if not allowed:
        return tools

    if user_role in ("support_agent", "admin"):
        allowed |= set(_SUPPORT_ADDITIONS.get(intent, []))
    if user_role == "admin":
        allowed |= set(_ADMIN_ADDITIONS.get(intent, []))

    scoped = [t for t in tools if t.name in allowed]
    # Safety: if scoping removed everything (tool not yet in registry), fall back.
    return scoped if scoped else tools
