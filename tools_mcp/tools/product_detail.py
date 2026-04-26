from __future__ import annotations

from fastmcp import Context, FastMCP

from app.cache.keys import product_key
from app.cache.strategies import cache_aside
from app.config import get_settings
from app.db.session import AsyncSessionLocal
from tools_mcp.auth import MCPAuthError, get_user_context
from tools_mcp.db.queries.products import get_product_detail, get_product_id_by_name

settings = get_settings()


def register(mcp: FastMCP) -> None:
    """Mount product detail tool onto *mcp*."""

    @mcp.tool(
        name="get_product_detail",
        description=(
            "Fetch full detail for a specific product: description, all variants "
            "(sizes, colours, SKUs, prices, stock), all images, brand and category. "
            "Provide product_id (numeric) when available — e.g. from get_order_items results. "
            "If only a product name is known, provide product_name instead and the tool "
            "will resolve it automatically."
        ),
    )
    async def get_product_detail_tool(
        ctx: Context,
        product_id: int | None = None,
        product_name: str | None = None,
    ) -> dict:
        """
        Args:
            product_id:   Numeric product ID. Takes priority over product_name when both given.
            product_name: Product name string. Used as fallback when product_id is not available.
        """
        try:
            get_user_context(ctx)
        except MCPAuthError as exc:
            return {"error": exc.message, "error_type": "auth_error"}

        if product_id is None and product_name is None:
            return {
                "error": "Provide either product_id or product_name.",
                "error_type": "invalid_args",
            }

        async with AsyncSessionLocal() as db:
            try:
                # Resolve name → id when only a name was supplied
                if product_id is None:
                    product_id = await get_product_id_by_name(db, product_name)
                    if product_id is None:
                        return {
                            "error": f"No active product found with name '{product_name}'.",
                            "error_type": "not_found",
                        }

                cache_key = product_key(product_id)
                detail = await cache_aside(
                    key=cache_key,
                    ttl=settings.cache_ttl_product,
                    fetch=lambda: get_product_detail(db, product_id),
                )
            except Exception as exc:
                return {"error": f"Failed to fetch product: {exc}", "error_type": "db_error"}

        if detail is None:
            return {
                "error": f"Product {product_id} not found or no longer active.",
                "error_type": "not_found",
            }

        return detail
