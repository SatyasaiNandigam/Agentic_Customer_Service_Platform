from __future__ import annotations

from fastmcp import Context, FastMCP

from app.cache.keys import refund_list_key
from app.cache.strategies import cache_aside
from app.config import get_settings
from app.db.session import AsyncSessionLocal
from tools_mcp.auth import MCPAuthError, get_user_context
from tools_mcp.db.queries.refunds import get_refund_detail, get_refunds_for_user

settings = get_settings()


def register(mcp: FastMCP) -> None:
    """Mount refund status tool onto *mcp*."""

    @mcp.tool(
        name="get_refund_status",
        description=(
            "Check the status of refund requests for the authenticated customer. "
            "If refund_id is provided, returns detail for that specific refund. "
            "Otherwise returns all refunds, newest first. "
            "Includes amount, reason, current status (pending / approved / completed / rejected)."
        ),
    )
    async def get_refund_status_tool(
        ctx: Context,
        refund_id: int | None = None,
    ) -> dict:
        """
        Args:
            refund_id: Optional specific refund ID. If omitted, returns all refunds
                       for the authenticated customer.
        """
        try:
            user = get_user_context(ctx)
        except MCPAuthError as exc:
            return {"error": exc.message, "error_type": "auth_error"}

        async with AsyncSessionLocal() as db:
            if refund_id is not None:
                # Specific refund lookup — no caching (narrow query, always fresh)
                try:
                    detail = await get_refund_detail(db, refund_id, user.user_id)
                except Exception as exc:
                    return {
                        "error": f"Failed to fetch refund: {exc}",
                        "error_type": "db_error",
                    }
                if detail is None:
                    return {
                        "error": f"Refund {refund_id} not found.",
                        "error_type": "not_found",
                    }
                return detail

            # All refunds for user — cache the list
            cache_key = refund_list_key(user.user_id)
            try:
                refunds = await cache_aside(
                    key=cache_key,
                    ttl=settings.cache_ttl_order_status,  # 5min — refund status can change
                    fetch=lambda: get_refunds_for_user(db, user.user_id),
                )
            except Exception as exc:
                return {
                    "error": f"Failed to fetch refunds: {exc}",
                    "error_type": "db_error",
                }

        return {"refunds": refunds, "count": len(refunds)}
