from __future__ import annotations

from fastmcp import Context, FastMCP

from app.cache.keys import order_items_key
from app.cache.strategies import cache_aside
from app.config import get_settings
from app.db.session import AsyncSessionLocal
from tools_mcp.auth import MCPAuthError, get_user_context
from tools_mcp.db.queries.orders import get_order_items

settings = get_settings()


def register(mcp: FastMCP) -> None:
    """Mount order items tool onto *mcp*."""

    @mcp.tool(
        name="get_order_items",
        description=(
            "Return the line items (products, quantities, prices) inside a specific order "
            "owned by the authenticated customer. "
            "Use this when the customer asks what was in their order."
        ),
    )
    async def get_order_items_tool(
        ctx: Context,
        order_id: int,
    ) -> dict:
        """
        Args:
            order_id: Numeric order ID.
        """
        try:
            user = get_user_context(ctx)
        except MCPAuthError as exc:
            return {"error": exc.message, "error_type": "auth_error"}

        cache_key = order_items_key(order_id)

        async with AsyncSessionLocal() as db:
            try:
                items = await cache_aside(
                    key=cache_key,
                    ttl=settings.cache_ttl_order_status,
                    fetch=lambda: get_order_items(db, order_id, user.user_id),
                )
            except PermissionError as exc:
                return {"error": str(exc), "error_type": "permission_denied"}
            except Exception as exc:
                return {"error": f"Failed to fetch order items: {exc}", "error_type": "db_error"}

        return {"order_id": order_id, "items": items, "count": len(items)}
