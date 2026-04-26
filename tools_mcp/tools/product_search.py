from __future__ import annotations

from fastmcp import Context, FastMCP

from app.cache.keys import product_search_key
from app.cache.strategies import cache_aside
from app.config import get_settings
from app.db.session import AsyncSessionLocal
from tools_mcp.auth import MCPAuthError, get_user_context
from tools_mcp.db.queries.products import search_products

settings = get_settings()


def register(mcp: FastMCP) -> None:
    """Mount product search tool onto *mcp*."""

    @mcp.tool(
        name="search_products",
        description=(
            "Search the product catalogue by keyword and/or filters. "
            "Returns a summary list (name, price, brand, category, primary image). "
            "Use get_product_detail for full variants and images of a specific product."
        ),
    )
    async def search_products_tool(
        ctx: Context,
        keyword: str | None = None,
        category_id: int | None = None,
        brand_id: int | None = None,
        min_price: float | None = None,
        max_price: float | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> dict:
        """
        Args:
            keyword:     Text to search in product name and description (case-insensitive).
            category_id: Filter by category ID.
            brand_id:    Filter by brand ID.
            min_price:   Minimum base price (inclusive).
            max_price:   Maximum base price (inclusive).
            limit:       Results per page (1-50, default 20).
            offset:      Pagination offset (default 0).
        """
        try:
            get_user_context(ctx)   # validate caller is authenticated
        except MCPAuthError as exc:
            return {"error": exc.message, "error_type": "auth_error"}

        limit = max(1, min(limit, 50))
        offset = max(0, offset)

        cache_key = product_search_key(
            keyword=keyword,
            category_id=category_id,
            brand_id=brand_id,
            min_price=min_price,
            max_price=max_price,
            limit=limit,
            offset=offset,
        )

        async with AsyncSessionLocal() as db:
            try:
                products = await cache_aside(
                    key=cache_key,
                    ttl=settings.cache_ttl_product_search,
                    fetch=lambda: search_products(
                        db,
                        keyword=keyword,
                        category_id=category_id,
                        brand_id=brand_id,
                        min_price=min_price,
                        max_price=max_price,
                        limit=limit,
                        offset=offset,
                    ),
                )
            except Exception as exc:
                return {"error": f"Product search failed: {exc}", "error_type": "db_error"}

        return {
            "products": products,
            "count": len(products),
            "limit": limit,
            "offset": offset,
        }
