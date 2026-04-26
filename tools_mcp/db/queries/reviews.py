"""Review query functions (read-only)."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from tools_mcp.db.models import Review, ReviewImage
from tools_mcp.db.queries import serialize


async def get_reviews_for_product(
    db: AsyncSession,
    product_id: int,
    limit: int = 20,
    offset: int = 0,
    min_rating: int | None = None,
) -> list[dict]:
    """Return paginated reviews for a product, newest first.

    Args:
        db:         Active async session.
        product_id: Product to fetch reviews for.
        limit:      Max reviews to return (default 20, max enforced by caller).
        offset:     Pagination offset.
        min_rating: If set, only include reviews with rating >= min_rating.

    Returns:
        List of review dicts with images included.
    """
    stmt = (
        select(Review)
        .where(Review.product_id == product_id)
        .options(selectinload(Review.images))
        .order_by(Review.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    if min_rating is not None:
        stmt = stmt.where(Review.rating >= min_rating)

    result = await db.execute(stmt)
    reviews = result.scalars().all()

    return [
        serialize({
            "review_id": r.review_id,
            "product_id": r.product_id,
            "rating": r.rating,
            "title": r.title,
            "body": r.body,
            "is_verified_purchase": r.is_verified_purchase,
            "helpful_count": r.helpful_count,
            "created_at": r.created_at,
            "images": [img.url for img in r.images],
        })
        for r in reviews
    ]
