from __future__ import annotations

from fastmcp import Context, FastMCP

from app.cache.keys import reviews_key
from app.cache.strategies import cache_aside
from app.config import get_settings
from app.db.session import AsyncSessionLocal
from tools_mcp.auth import MCPAuthError, get_user_context
from tools_mcp.db.queries.reviews import get_reviews_for_product

settings = get_settings()

# Reviews cache TTL — same as product search (inventory-adjacent freshness)
_REVIEWS_TTL = settings.cache_ttl_product_search  # 15min


def register(mcp: FastMCP) -> None:
    """Mount review lookup tool onto *mcp*."""

    @mcp.tool(
        name="get_reviews",
        description=(
            "Fetch customer reviews for a product. "
            "Returns rating, title, review body, verified-purchase flag, and any attached images. "
            "Use when a customer asks about product quality or other shoppers' experiences."
        ),
    )
    async def get_reviews_tool(
        ctx: Context,
        product_id: int,
        limit: int = 20,
        offset: int = 0,
        min_rating: int | None = None,
    ) -> dict:
        """
        Args:
            product_id: Numeric product ID.
            limit:      Max reviews to return (1-50, default 20).
            offset:     Pagination offset (default 0).
            min_rating: Only return reviews with this rating or higher (1-5).
        """
        try:
            get_user_context(ctx)   # validate caller is authenticated
        except MCPAuthError as exc:
            return {"error": exc.message, "error_type": "auth_error"}

        limit = max(1, min(limit, 50))
        offset = max(0, offset)

        if min_rating is not None and not (1 <= min_rating <= 5):
            return {
                "error": "min_rating must be between 1 and 5.",
                "error_type": "invalid_request",
            }

        # Cache only first page with no rating filter (most common call)
        use_cache = (offset == 0 and min_rating is None)
        cache_key = reviews_key(product_id) if use_cache else None

        async with AsyncSessionLocal() as db:
            try:
                if cache_key:
                    reviews = await cache_aside(
                        key=cache_key,
                        ttl=_REVIEWS_TTL,
                        fetch=lambda: get_reviews_for_product(
                            db, product_id, limit=limit, offset=offset, min_rating=min_rating
                        ),
                    )
                else:
                    reviews = await get_reviews_for_product(
                        db, product_id, limit=limit, offset=offset, min_rating=min_rating
                    )
            except Exception as exc:
                return {"error": f"Failed to fetch reviews: {exc}", "error_type": "db_error"}

        return {
            "product_id": product_id,
            "reviews": reviews,
            "count": len(reviews),
            "limit": limit,
            "offset": offset,
        }
