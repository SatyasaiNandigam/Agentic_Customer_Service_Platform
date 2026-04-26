from __future__ import annotations

from fastmcp import Context, FastMCP

from app.cache.keys import order_detail_key, order_items_key, order_list_key, shipment_key
from app.cache.strategies import invalidate
from app.db.session import AsyncSessionLocal
from tools_mcp.auth import MCPAuthError, get_user_context
from tools_mcp.db.queries.orders import cancel_order


def register(mcp: FastMCP) -> None:
    """Mount order cancellation tool onto *mcp*."""

    @mcp.tool(
        name="cancel_order",
        description=(
            "Cancel an order owned by the authenticated customer. "
            "Only orders with status 'pending', 'confirmed', or 'processing' can be cancelled. "
            "Once an order has shipped it cannot be cancelled — suggest a refund instead. "
            "Returns the updated order with status 'cancelled'."
        ),
    )
    async def cancel_order_tool(
        ctx: Context,
        order_id: int,
    ) -> dict:
        """
        Args:
            order_id: Numeric ID of the order to cancel.
        """
        try:
            user = get_user_context(ctx)
        except MCPAuthError as exc:
            return {"error": exc.message, "error_type": "auth_error"}

        async with AsyncSessionLocal() as db:
            try:
                result = await cancel_order(db, order_id=order_id, user_id=user.user_id)
                await db.commit()
            except PermissionError as exc:
                return {"error": str(exc), "error_type": "permission_denied"}
            except ValueError as exc:
                return {"error": str(exc), "error_type": "invalid_request"}
            except Exception as exc:
                return {"error": f"Order cancellation failed: {exc}", "error_type": "db_error"}

        # Invalidate all cache keys related to this order so next read is fresh
        await invalidate(
            order_list_key(user.user_id),
            order_detail_key(order_id),
            order_items_key(order_id),
            shipment_key(order_id),
        )

        return result
