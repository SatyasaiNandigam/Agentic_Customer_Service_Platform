"""User / account query functions (read-only)."""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from tools_mcp.db.models import Address, User
from tools_mcp.db.queries import serialize


async def resolve_user_pk(db: AsyncSession, user_uuid: str) -> int:
    """Resolve the UUID string from X-User-Id header to the integer user_id PK."""
    result = await db.execute(
        select(User.user_id).where(User.user_uuid == uuid.UUID(user_uuid))
    )
    user_pk = result.scalar_one_or_none()
    if user_pk is None:
        raise PermissionError("User not found.")
    return user_pk


async def get_account_info(
    db: AsyncSession,
    user_id: str,
) -> dict | None:
    """Return public account info for user_id.  Never returns password_hash."""
    user_pk = await resolve_user_pk(db, user_id)
    result = await db.execute(
        select(User).where(User.user_id == user_pk)
    )
    user = result.scalar_one_or_none()
    if user is None:
        return None

    return serialize({
        "user_id": user.user_id,
        "user_uuid": user.user_uuid,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "full_name": user.full_name,
        "email": user.email,
        "phone": user.phone,
        "city": user.city,
        "is_email_verified": user.is_email_verified,
        "status": user.status,
        "created_at": user.created_at,
    })


async def get_addresses(
    db: AsyncSession,
    user_id: str,
) -> list[dict]:
    """Return all saved addresses for user_id, default address first."""
    user_pk = await resolve_user_pk(db, user_id)
    result = await db.execute(
        select(Address)
        .where(Address.user_id == user_pk)
        .order_by(Address.is_default.desc(), Address.address_id.asc())
    )
    addresses = result.scalars().all()

    return [
        serialize({
            "address_id": a.address_id,
            "type": a.type,
            "street_line1": a.street_line1,
            "landmark": a.landmark,
            "city": a.city,
            "state": a.state,
            "country": a.country,
            "pincode": a.pincode,
            "is_default": a.is_default,
        })
        for a in addresses
    ]
