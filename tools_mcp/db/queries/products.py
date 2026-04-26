"""Product query functions — search and detail (read-only)."""

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from tools_mcp.db.models import (
    Attribute,
    AttributeValue,
    Brand,
    Category,
    Product,
    ProductImage,
    ProductVariant,
    VariantAttribute,
)
from tools_mcp.db.queries import serialize


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _variant_to_dict(variant: ProductVariant) -> dict:
    d: dict = {
        "variant_id": variant.variant_id,
        "sku": variant.sku,
        "price": variant.price,
        "stock_qty": variant.stock_qty,
        "weight_kg": variant.weight_kg,
        "status": variant.status,
    }
    # Include attributes if already loaded
    if "variant_attributes" in variant.__dict__:
        d["attributes"] = [
            {
                "attribute": va.attribute.name,
                "value": va.attribute_value.value,
            }
            for va in variant.variant_attributes
        ]
    return serialize(d)


# ---------------------------------------------------------------------------
# Read queries
# ---------------------------------------------------------------------------

async def search_products(
    db: AsyncSession,
    keyword: str | None = None,
    category_id: int | None = None,
    brand_id: int | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
    limit: int = 20,
    offset: int = 0,
) -> list[dict]:
    """Full-text keyword search + optional filters.

    Searches product name and description via ILIKE.  Returns summary rows
    (no variants or images — use get_product_detail for those).
    """
    stmt = (
        select(Product)
        .where(Product.status == "active")
        .options(
            selectinload(Product.brand),
            selectinload(Product.category),
            selectinload(Product.images),
        )
        .order_by(Product.created_at.desc())
        .limit(limit)
        .offset(offset)
    )

    if keyword:
        pattern = f"%{keyword}%"
        stmt = stmt.where(
            or_(
                Product.name.ilike(pattern),
                Product.description.ilike(pattern),
            )
        )
    if category_id is not None:
        stmt = stmt.where(Product.category_id == category_id)
    if brand_id is not None:
        stmt = stmt.where(Product.brand_id == brand_id)
    if min_price is not None:
        stmt = stmt.where(Product.base_price >= min_price)
    if max_price is not None:
        stmt = stmt.where(Product.base_price <= max_price)

    result = await db.execute(stmt)
    products = result.scalars().all()

    rows = []
    for p in products:
        primary_image = next(
            (img.url for img in p.images if img.is_primary), None
        ) or next((img.url for img in p.images), None)

        rows.append(serialize({
            "product_id": p.product_id,
            "product_uuid": p.product_uuid,
            "name": p.name,
            "base_price": p.base_price,
            "slug": p.slug,
            "brand": p.brand.name if p.brand else None,
            "category": p.category.name if p.category else None,
            "primary_image_url": primary_image,
            "status": p.status,
        }))

    return rows


async def get_product_id_by_name(
    db: AsyncSession,
    name: str,
) -> int | None:
    """Return the product_id of the first active product whose name matches *name*.

    Tries an exact case-insensitive match first; falls back to a leading
    prefix (ILIKE 'name%') so slight truncations still resolve correctly.
    Returns None if no active product is found.
    """
    result = await db.execute(
        select(Product.product_id)
        .where(Product.name.ilike(name), Product.status == "active")
        .limit(1)
    )
    product_id = result.scalar_one_or_none()
    if product_id is not None:
        return product_id

    result = await db.execute(
        select(Product.product_id)
        .where(Product.name.ilike(f"{name}%"), Product.status == "active")
        .limit(1)
    )
    return result.scalar_one_or_none()


async def get_product_detail(
    db: AsyncSession,
    product_id: int,
) -> dict | None:
    """Return full product detail: variants with attributes, all images.

    Returns None if the product does not exist or is not active.
    """
    result = await db.execute(
        select(Product)
        .where(Product.product_id == product_id, Product.status == "active")
        .options(
            selectinload(Product.brand),
            selectinload(Product.category),
            selectinload(Product.images),
            selectinload(Product.variants).selectinload(
                ProductVariant.variant_attributes
            ).selectinload(VariantAttribute.attribute),
            selectinload(Product.variants).selectinload(
                ProductVariant.variant_attributes
            ).selectinload(VariantAttribute.attribute_value),
        )
    )
    product = result.scalar_one_or_none()
    if product is None:
        return None

    return serialize({
        "product_id": product.product_id,
        "product_uuid": product.product_uuid,
        "name": product.name,
        "description": product.description,
        "base_price": product.base_price,
        "slug": product.slug,
        "status": product.status,
        "brand": {
            "brand_id": product.brand.brand_id,
            "name": product.brand.name,
            "country": product.brand.country,
        } if product.brand else None,
        "category": {
            "category_id": product.category.category_id,
            "name": product.category.name,
        } if product.category else None,
        "images": [
            {"url": img.url, "is_primary": img.is_primary, "variant_id": img.variant_id}
            for img in product.images
        ],
        "variants": [_variant_to_dict(v) for v in product.variants],
    })
