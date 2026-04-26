from __future__ import annotations

from fastmcp import Context, FastMCP

from app.cache.keys import account_key
from app.cache.strategies import cache_aside
from app.config import get_settings
from app.db.session import AsyncSessionLocal
from tools_mcp.auth import MCPAuthError, get_user_context
from tools_mcp.db.queries.users import get_account_info, get_addresses

settings = get_settings()

# Account info is relatively stable — cache for 5 minutes
_ACCOUNT_TTL = 300


def register(mcp: FastMCP) -> None:
    """Mount account info tool onto *mcp*."""

    @mcp.tool(
        name="get_account_info",
        description=(
            "Return the authenticated customer's profile (name, email, phone, city) "
            "and all saved delivery addresses. "
            "Use when the customer asks about their account details or saved addresses."
        ),
    )
    async def get_account_info_tool(ctx: Context) -> dict:
        """No arguments required — identity comes from the auth header."""
        try:
            user = get_user_context(ctx)
        except MCPAuthError as exc:
            return {"error": exc.message, "error_type": "auth_error"}

        cache_key = account_key(user.user_id)

        async with AsyncSessionLocal() as db:
            try:
                profile = await cache_aside(
                    key=cache_key,
                    ttl=_ACCOUNT_TTL,
                    fetch=lambda: get_account_info(db, user.user_id),
                )
                # Addresses fetched separately (not cached — can change more often)
                addresses = await get_addresses(db, user.user_id)
            except Exception as exc:
                return {
                    "error": f"Failed to fetch account info: {exc}",
                    "error_type": "db_error",
                }

        if profile is None:
            return {
                "error": "Account not found.",
                "error_type": "not_found",
            }

        return {**profile, "addresses": addresses}
