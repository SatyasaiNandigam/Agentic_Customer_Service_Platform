from __future__ import annotations

from fastmcp import Context, FastMCP

from app.cache.keys import order_list_key, refund_list_key
from app.cache.strategies import invalidate
from app.db.session import AsyncSessionLocal
from tools_mcp.auth import MCPAuthError, get_user_context
from tools_mcp.db.queries.refunds import initiate_refund


def register(mcp: FastMCP) -> None:
    """Mount refund initiation tool onto *mcp*."""

    @mcp.tool(
        name="initiate_refund",
        description=(
            "Submit a refund request for a delivered order owned by the authenticated customer. "
            "The order must be in 'delivered' status and have no active refund already. "
            "If amount is omitted, the full order total is refunded. "
            "Returns the new refund record with its ID and 'pending' status."
        ),
    )
    async def initiate_refund_tool(
        ctx: Context,
        order_id: int,
        reason: str,
        amount: float | None = None,
    ) -> dict:
        """
        Args:
            order_id: ID of the delivered order to refund.
            reason:   Customer-provided reason for the refund (e.g. "Item arrived damaged").
            amount:   Refund amount in the order currency. Defaults to the full order total
                      if omitted. Must not exceed the original payment amount.
        """
        try:
            user = get_user_context(ctx)
        except MCPAuthError as exc:
            return {"error": exc.message, "error_type": "auth_error"}

        # Only customers and support agents may initiate refunds
        if user.role == "admin":
            # Admins use a different workflow — this tool is for customer-facing flows
            pass  # Allow admin too — no restriction here

        if not reason or not reason.strip():
            return {
                "error": "A reason is required to initiate a refund.",
                "error_type": "invalid_request",
            }

        async with AsyncSessionLocal() as db:
            try:
                result = await initiate_refund(
                    db,
                    order_id=order_id,
                    user_id=user.user_id,
                    reason=reason.strip(),
                    amount=amount,
                )
                await db.commit()
            except PermissionError as exc:
                return {"error": str(exc), "error_type": "permission_denied"}
            except ValueError as exc:
                return {"error": str(exc), "error_type": "invalid_request"}
            except Exception as exc:
                return {"error": f"Refund initiation failed: {exc}", "error_type": "db_error"}

        # Invalidate stale cache entries so next read reflects the new refund
        await invalidate(
            refund_list_key(user.user_id),
            order_list_key(user.user_id),
        )

        return result
