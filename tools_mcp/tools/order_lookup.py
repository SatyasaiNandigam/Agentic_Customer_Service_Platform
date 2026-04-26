from __future__ import annotations

from fastmcp import Context, FastMCP

from app.cache.keys import order_detail_key, order_list_key
from app.cache.strategies import cache_aside
from app.config import get_settings
from app.db.session import AsyncSessionLocal
from tools_mcp.auth import MCPAuthError, get_user_context
from tools_mcp.db.queries.orders import get_order_detail, get_orders_for_user

settings = get_settings()


def register(mcp: FastMCP) -> None:
    """Mount order lookup tools onto *mcp*."""

    @mcp.tool(
        name="get_orders",
        description=(
            "List recent orders for the authenticated customer. "
            "Returns order IDs, statuses, totals, and the latest status note. "
            "Use get_order_detail for full history of a specific order."
        ),
    )
    async def get_orders(
        ctx: Context,
        limit: int = 10,
        status_filter: str | None = None,
    ) -> dict:
        """
        Args:
            limit:         Max number of orders to return (1-50).
            status_filter: Optional status to filter by (e.g. "pending", "delivered",
                           "cancelled"). Omit to return all statuses.
        """
        try:
            user = get_user_context(ctx)
        except MCPAuthError as exc:
            return {"error": exc.message, "error_type": "auth_error"}

        limit = max(1, min(limit, 50))
        cache_key = order_list_key(user.user_id)

        async with AsyncSessionLocal() as db:
            try:
                orders = await cache_aside(
                    key=cache_key,
                    ttl=settings.cache_ttl_order_status,
                    fetch=lambda: get_orders_for_user(
                        db, user.user_id, limit=limit, status=status_filter
                    ),
                )
            except Exception as exc:
                return {"error": f"Failed to fetch orders: {exc}", "error_type": "db_error"}

        return {"orders": orders, "count": len(orders)}

    # ------------------------------------------------------------------

    @mcp.tool(
        name="get_order_detail",
        description=(
            "Fetch complete detail for a specific order owned by the authenticated customer: "
            "full status history, line-item summary, and shipping address. "
            "Use this when the customer asks about a specific order number."
        ),
    )
    async def get_order_detail_tool(
        ctx: Context,
        order_id: int,
    ) -> dict:
        """
        Args:
            order_id: Numeric order ID (visible on the customer's order list).
        """
        try:
            user = get_user_context(ctx)
        except MCPAuthError as exc:
            return {"error": exc.message, "error_type": "auth_error"}

        cache_key = order_detail_key(order_id)

        async with AsyncSessionLocal() as db:
            try:
                detail = await cache_aside(
                    key=cache_key,
                    ttl=settings.cache_ttl_order_status,
                    fetch=lambda: get_order_detail(db, order_id, user.user_id),
                )
            except PermissionError as exc:
                return {"error": str(exc), "error_type": "permission_denied"}
            except Exception as exc:
                return {"error": f"Failed to fetch order detail: {exc}", "error_type": "db_error"}

        if detail is None:
            return {
                "error": f"Order {order_id} not found.",
                "error_type": "not_found",
            }

        return detail
