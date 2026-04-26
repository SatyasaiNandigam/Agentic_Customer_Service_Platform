from __future__ import annotations

import hashlib
import json



def product_key(product_id: int) -> str:
    """Full product detail — variants, images, attributes.  TTL: 1h."""
    return f"cache:product:{product_id}"


def product_search_key(
    keyword: str | None,
    category_id: int | None,
    brand_id: int | None,
    min_price: float | None,
    max_price: float | None,
    limit: int,
    offset: int,
) -> str:
    """Search result list for a given filter combination.  TTL: 15min.

    Hashes all parameters into a short fingerprint so any filter change
    produces a different key without making the key unreadably long.
    """
    params = {
        "keyword": keyword,
        "category_id": category_id,
        "brand_id": brand_id,
        "min_price": min_price,
        "max_price": max_price,
        "limit": limit,
        "offset": offset,
    }
    fingerprint = hashlib.md5(
        json.dumps(params, sort_keys=True).encode(), usedforsecurity=False
    ).hexdigest()[:12]
    return f"cache:product_search:{fingerprint}"


def categories_key() -> str:
    """Full category tree.  TTL: 6h."""
    return "cache:categories"


def brands_key() -> str:
    """Full brand list.  TTL: 6h."""
    return "cache:brands"


def reviews_key(product_id: int) -> str:
    """Reviews for a product.  TTL: 15min."""
    return f"cache:reviews:{product_id}"



def order_list_key(user_id: str) -> str:
    """Order list for a user.  TTL: 5min."""
    return f"cache:order_status:{user_id}"


def order_detail_key(order_id: int) -> str:
    """Single order detail.  TTL: 5min."""
    return f"cache:order_detail:{order_id}"


def order_items_key(order_id: int) -> str:
    """Line items for an order.  TTL: 5min."""
    return f"cache:order_items:{order_id}"



def shipment_key(order_id: int) -> str:
    """Shipment + tracking events for an order.  TTL: 5min."""
    return f"cache:shipment:{order_id}"




def refund_list_key(user_id: str) -> str:
    """All refunds for a user.  TTL: 5min."""
    return f"cache:refunds:{user_id}"


def account_key(user_id: str) -> str:
    """User profile info.  TTL: 5min."""
    return f"cache:account:{user_id}"
