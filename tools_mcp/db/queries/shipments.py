"""Shipment query functions (read-only)."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from tools_mcp.db.models import Shipment, ShipmentTracking
from tools_mcp.db.queries import serialize
from tools_mcp.db.queries.orders import verify_order_belongs_to_user


async def get_shipment_for_order(
    db: AsyncSession,
    order_id: int,
    user_id: str,
) -> dict | None:
    """Return shipment info for an order owned by user_id.

    Raises PermissionError if the order is not owned by this user.
    Returns None if no shipment exists yet.
    """
    await verify_order_belongs_to_user(db, order_id, user_id)

    result = await db.execute(
        select(Shipment)
        .where(Shipment.order_id == order_id)
        .options(selectinload(Shipment.tracking_events))
        .order_by(Shipment.shipment_id.desc())
        .limit(1)
    )
    shipment = result.scalar_one_or_none()
    if shipment is None:
        return None

    return serialize({
        "shipment_id": shipment.shipment_id,
        "order_id": shipment.order_id,
        "carrier": shipment.carrier,
        "tracking_number": shipment.tracking_number,
        "status": shipment.status,
        "weight_kg": shipment.weight_kg,
        "shipping_charge": shipment.shipping_charge,
        "shipped_at": shipment.shipped_at,
        "delivered_at": shipment.delivered_at,
        "tracking_events": [
            {
                "event_description": e.event_description,
                "location": e.location,
                "event_time": e.event_time,
            }
            for e in shipment.tracking_events
        ],
    })


async def get_tracking_events(
    db: AsyncSession,
    shipment_id: int,
    user_id: str,
) -> list[dict]:
    """Return tracking events for a specific shipment, verifying ownership via its order.

    Raises PermissionError if the shipment's order is not owned by this user.
    """
    # Fetch the shipment to find its order_id for ownership verification
    result = await db.execute(
        select(Shipment)
        .where(Shipment.shipment_id == shipment_id)
        .options(selectinload(Shipment.tracking_events))
    )
    shipment = result.scalar_one_or_none()
    if shipment is None:
        raise PermissionError(f"Shipment {shipment_id} not found.")

    await verify_order_belongs_to_user(db, shipment.order_id, user_id)

    return [
        serialize({
            "tracking_id": e.tracking_id,
            "event_description": e.event_description,
            "location": e.location,
            "event_time": e.event_time,
        })
        for e in shipment.tracking_events
    ]
