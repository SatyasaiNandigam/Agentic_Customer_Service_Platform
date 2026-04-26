"""Refund query functions — read and write (initiate)."""

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from tools_mcp.db.models import Order, Payment, Refund
from tools_mcp.db.queries import serialize
from tools_mcp.db.queries.orders import verify_order_belongs_to_user
from tools_mcp.db.queries.users import resolve_user_pk


# Statuses on which a refund may be initiated
_REFUNDABLE_STATUSES = {"delivered"}
# Refund statuses that count as "already requested"
_ACTIVE_REFUND_STATUSES = {"pending", "approved", "processing", "completed"}


# ---------------------------------------------------------------------------
# Read queries
# ---------------------------------------------------------------------------

async def get_refunds_for_user(
    db: AsyncSession,
    user_id: str,
) -> list[dict]:
    """Return all refunds for orders belonging to user_id, newest first."""
    user_pk = await resolve_user_pk(db, user_id)
    result = await db.execute(
        select(Refund)
        .join(Order, Refund.order_id == Order.order_id)
        .where(Order.user_id == user_pk)
        .options(
            selectinload(Refund.payment),
            selectinload(Refund.order),
        )
        .order_by(Refund.created_at.desc())
    )
    refunds = result.scalars().all()

    return [
        serialize({
            "refund_id": r.refund_id,
            "order_id": r.order_id,
            "order_uuid": r.order.order_uuid,
            "payment_method": r.payment.method,
            "amount": r.amount,
            "reason": r.reason,
            "status": r.status,
            "created_at": r.created_at,
            "updated_at": r.updated_at,
        })
        for r in refunds
    ]


async def get_refund_detail(
    db: AsyncSession,
    refund_id: int,
    user_id: str,
) -> dict | None:
    """Return a single refund, verifying it belongs to this user's order."""
    user_pk = await resolve_user_pk(db, user_id)
    result = await db.execute(
        select(Refund)
        .join(Order, Refund.order_id == Order.order_id)
        .where(Refund.refund_id == refund_id, Order.user_id == user_pk)
        .options(
            selectinload(Refund.payment),
            selectinload(Refund.order),
        )
    )
    refund = result.scalar_one_or_none()
    if refund is None:
        return None

    return serialize({
        "refund_id": refund.refund_id,
        "order_id": refund.order_id,
        "order_uuid": refund.order.order_uuid,
        "payment_id": refund.payment_id,
        "payment_method": refund.payment.method,
        "amount": refund.amount,
        "reason": refund.reason,
        "status": refund.status,
        "created_at": refund.created_at,
        "updated_at": refund.updated_at,
    })


# ---------------------------------------------------------------------------
# Write query
# ---------------------------------------------------------------------------

async def initiate_refund(
    db: AsyncSession,
    order_id: int,
    user_id: str,
    reason: str,
    amount: float | None = None,
) -> dict:
    """Create a refund request for an order owned by user_id.

    Business rules enforced:
    - Order must belong to user_id.
    - Order status must be 'delivered'.
    - No active refund may already exist for this order.
    - If *amount* is None, defaults to the order's grand_total.
    - Refund amount may not exceed the original payment amount.

    Raises:
        PermissionError: order not found or not owned by this user.
        ValueError: business rule violation (see messages).

    Returns:
        dict with the newly created refund record.
    """
    order = await verify_order_belongs_to_user(db, order_id, user_id)

    if order.status not in _REFUNDABLE_STATUSES:
        raise ValueError(
            f"Refund cannot be initiated for order {order_id} "
            f"(current status: {order.status!r}). "
            f"Only delivered orders are eligible."
        )

    # Check for an existing active refund on this order
    existing = await db.execute(
        select(Refund).where(
            Refund.order_id == order_id,
            Refund.status.in_(_ACTIVE_REFUND_STATUSES),
        )
    )
    if existing.scalar_one_or_none() is not None:
        raise ValueError(
            f"A refund request for order {order_id} is already in progress."
        )

    # Fetch the payment record
    payment_result = await db.execute(
        select(Payment)
        .where(Payment.order_id == order_id, Payment.status == "paid")
        .order_by(Payment.paid_at.desc())
        .limit(1)
    )
    payment = payment_result.scalar_one_or_none()
    if payment is None:
        raise ValueError(
            f"No completed payment found for order {order_id}. "
            "Cannot initiate a refund."
        )

    refund_amount = float(amount) if amount is not None else float(order.grand_total or 0)

    if payment.amount and refund_amount > float(payment.amount):
        raise ValueError(
            f"Refund amount ({refund_amount}) exceeds the original payment "
            f"amount ({float(payment.amount)})."
        )

    now = datetime.now(timezone.utc).replace(tzinfo=None)
    refund = Refund(
        payment_id=payment.payment_id,
        order_id=order_id,
        amount=refund_amount,
        reason=reason,
        status="pending",
        created_at=now,
        updated_at=now,
    )
    db.add(refund)
    await db.flush()  # populate refund_id; caller commits

    return serialize({
        "refund_id": refund.refund_id,
        "order_id": order_id,
        "payment_id": payment.payment_id,
        "amount": refund.amount,
        "reason": refund.reason,
        "status": refund.status,
        "created_at": refund.created_at,
        "message": "Refund request submitted successfully. "
                   "You will receive a confirmation once it is approved.",
    })
