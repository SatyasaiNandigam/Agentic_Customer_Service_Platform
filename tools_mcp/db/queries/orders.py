"""Order query functions — read and write (cancel)."""

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from tools_mcp.db.models import Order, OrderItem, OrderStatusHistory, ProductVariant, Product
from tools_mcp.db.queries import serialize
from tools_mcp.db.queries.users import resolve_user_pk


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _order_to_dict(order: Order) -> dict:
    return serialize({
        "order_id": order.order_id,
        "order_uuid": order.order_uuid,
        "status": order.status,
        "subtotal": order.subtotal,
        "discount": order.discount,
        "tax": order.tax,
        "shipping_fee": order.shipping_fee,
        "grand_total": order.grand_total,
        "created_at": order.created_at,
        "updated_at": order.updated_at,
    })


async def verify_order_belongs_to_user(
    db: AsyncSession, order_id: int, user_id: str
) -> Order:
    """Return the Order if it belongs to user_id, raise PermissionError otherwise.

    Raises:
        PermissionError: order not found or not owned by this user.
    """
    user_pk = await resolve_user_pk(db, user_id)
    result = await db.execute(
        select(Order).where(Order.order_id == order_id, Order.user_id == user_pk)
    )
    order = result.scalar_one_or_none()
    if order is None:
        raise PermissionError(
            f"Order {order_id} not found or does not belong to this user."
        )
    return order


# ---------------------------------------------------------------------------
# Read queries
# ---------------------------------------------------------------------------

async def get_orders_for_user(
    db: AsyncSession,
    user_id: str,
    limit: int = 10,
    status: str | None = None,
) -> list[dict]:
    """Return a list of orders for *user_id*, newest first.

    Each dict includes the latest status history entry for quick display.
    """
    user_pk = await resolve_user_pk(db, user_id)
    stmt = (
        select(Order)
        .where(Order.user_id == user_pk)
        .options(
            selectinload(Order.status_history)
        )
        .order_by(Order.created_at.desc())
        .limit(limit)
    )
    if status:
        stmt = stmt.where(Order.status == status)

    result = await db.execute(stmt)
    orders = result.scalars().all()

    rows = []
    for o in orders:
        d = _order_to_dict(o)
        # Attach most recent status history note
        if o.status_history:
            latest = o.status_history[-1]
            d["latest_status_note"] = latest.note
            d["latest_status_at"] = serialize(latest.changed_at)
        else:
            d["latest_status_note"] = None
            d["latest_status_at"] = None
        rows.append(d)

    return rows


async def get_order_detail(
    db: AsyncSession,
    order_id: int,
    user_id: str,
) -> dict | None:
    """Return full order detail including status history, or None if not found/not owned."""
    user_pk = await resolve_user_pk(db, user_id)
    result = await db.execute(
        select(Order)
        .where(Order.order_id == order_id, Order.user_id == user_pk)
        .options(
            selectinload(Order.status_history),
            selectinload(Order.address),
        )
    )
    order = result.scalar_one_or_none()
    if order is None:
        return None

    d = _order_to_dict(order)
    d["status_history"] = [
        {
            "status": h.status,
            "note": h.note,
            "changed_at": serialize(h.changed_at),
        }
        for h in order.status_history
    ]
    if order.address:
        a = order.address
        d["shipping_address"] = {
            "street_line1": a.street_line1,
            "landmark": a.landmark,
            "city": a.city,
            "state": a.state,
            "country": a.country,
            "pincode": a.pincode,
        }
    else:
        d["shipping_address"] = None

    return d


async def get_order_items(
    db: AsyncSession,
    order_id: int,
    user_id: str,
) -> list[dict]:
    """Return line items for an order, with product name and SKU.

    Raises PermissionError if the order is not owned by user_id.
    """
    await verify_order_belongs_to_user(db, order_id, user_id)

    result = await db.execute(
        select(OrderItem)
        .where(OrderItem.order_id == order_id)
        .options(
            selectinload(OrderItem.variant).selectinload(ProductVariant.product)
        )
    )
    items = result.scalars().all()

    return [
        serialize({
            "item_id": item.item_id,
            "product_id": item.variant.product.product_id,
            "variant_id": item.variant_id,
            "sku": item.variant.sku,
            "product_name": item.variant.product.name,
            "quantity": item.quantity,
            "unit_price": item.unit_price,
            "total_price": item.total_price,
        })
        for item in items
    ]


# ---------------------------------------------------------------------------
# Write query
# ---------------------------------------------------------------------------

# Statuses that allow cancellation
_CANCELLABLE_STATUSES = {"pending", "confirmed", "processing"}


async def cancel_order(
    db: AsyncSession,
    order_id: int,
    user_id: str,
) -> dict:
    """Cancel an order owned by user_id.

    Raises:
        PermissionError: order not found or not owned by this user.
        ValueError: order status does not allow cancellation.

    Returns:
        dict with updated order summary.
    """
    order = await verify_order_belongs_to_user(db, order_id, user_id)

    if order.status not in _CANCELLABLE_STATUSES:
        raise ValueError(
            f"Order {order_id} cannot be cancelled (current status: {order.status!r}). "
            f"Only {sorted(_CANCELLABLE_STATUSES)} orders can be cancelled."
        )

    now = datetime.now(timezone.utc).replace(tzinfo=None)
    order.status = "cancelled"
    order.updated_at = now

    history = OrderStatusHistory(
        order_id=order_id,
        status="cancelled",
        note="Cancelled by customer via support agent.",
        changed_at=now,
    )
    db.add(history)
    await db.flush()  # write to DB within current transaction; caller commits

    return serialize({
        "order_id": order.order_id,
        "order_uuid": order.order_uuid,
        "status": order.status,
        "updated_at": order.updated_at,
        "message": "Order successfully cancelled.",
    })
