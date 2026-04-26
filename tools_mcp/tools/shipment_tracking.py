from __future__ import annotations

from fastmcp import Context, FastMCP

from app.cache.keys import shipment_key
from app.cache.strategies import cache_aside
from app.config import get_settings
from app.db.session import AsyncSessionLocal
from tools_mcp.auth import MCPAuthError, get_user_context
from tools_mcp.db.queries.shipments import get_shipment_for_order

settings = get_settings()


def register(mcp: FastMCP) -> None:
    """Mount shipment tracking tool onto *mcp*."""

    @mcp.tool(
        name="track_shipment",
        description=(
            "Return the shipment status and full tracking event timeline for an order "
            "owned by the authenticated customer. "
            "Includes carrier name, tracking number, and each scan event with location and time."
        ),
    )
    async def track_shipment_tool(
        ctx: Context,
        order_id: int,
    ) -> dict:
        """
        Args:
            order_id: Numeric order ID to look up the shipment for.
        """
        try:
            user = get_user_context(ctx)
        except MCPAuthError as exc:
            return {"error": exc.message, "error_type": "auth_error"}

        cache_key = shipment_key(order_id)

        async with AsyncSessionLocal() as db:
            try:
                shipment = await cache_aside(
                    key=cache_key,
                    ttl=settings.cache_ttl_order_status,
                    fetch=lambda: get_shipment_for_order(db, order_id, user.user_id),
                )
            except PermissionError as exc:
                return {"error": str(exc), "error_type": "permission_denied"}
            except Exception as exc:
                return {"error": f"Failed to fetch shipment: {exc}", "error_type": "db_error"}

        if shipment is None:
            return {
                "order_id": order_id,
                "message": "No shipment found for this order yet. "
                           "It may still be processing or not yet dispatched.",
                "shipment": None,
            }

        return shipment
