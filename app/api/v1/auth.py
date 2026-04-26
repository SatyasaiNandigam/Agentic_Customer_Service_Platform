"""Auth endpoints — login, token refresh, logout."""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, status
import bcrypt as _bcrypt
from pydantic import BaseModel
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.middleware import CurrentUser
from app.auth.service import (
    InvalidTokenError,
    create_access_token,
    create_refresh_token,
    verify_refresh_token,
)
from app.config import get_settings
from app.db.session import get_db
from tools_mcp.db.models import User, UserRole, UserRoleMapping, UserSession

router = APIRouter(prefix="/auth")

_settings = get_settings()


def _verify_password(plain: str, hashed: str) -> bool:
    return _bcrypt.checkpw(plain.encode(), hashed.encode())


class LoginRequest(BaseModel):
    email: str
    password: str


class RefreshRequest(BaseModel):
    refresh_token: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class LogoutResponse(BaseModel):
    message: str


@router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest, db: AsyncSession = Depends(get_db)) -> TokenResponse:
    result = await db.execute(select(User).where(User.email == body.email))
    user = result.scalar_one_or_none()
    if user is None or not user.password_hash:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not _verify_password(body.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    role_result = await db.execute(
        select(UserRole.role_name)
        .join(UserRoleMapping, UserRoleMapping.role_id == UserRole.role_id)
        .where(UserRoleMapping.user_id == user.user_id)
        .limit(1)
    )
    role = role_result.scalar_one_or_none()
    if role is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User has no assigned role.",
        )

    session_uuid = uuid.uuid4()
    user_uuid_str = str(user.user_uuid)
    access_token = create_access_token(
        user_id=user_uuid_str,
        role=role,
        session_id=str(session_uuid),
    )
    refresh_token = create_refresh_token(user_id=user_uuid_str)

    now = datetime.now(tz=timezone.utc)
    db.add(
        UserSession(
            session_uuid=session_uuid,
            user_id=user.user_id,
            token=refresh_token,
            created_at=now,
            expires_at=now + timedelta(days=_settings.jwt_refresh_token_expire_days),
            is_active=True,
        )
    )

    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


@router.post("/refresh", response_model=RefreshResponse)
async def refresh(body: RefreshRequest, db: AsyncSession = Depends(get_db)) -> RefreshResponse:
    try:
        token_data = verify_refresh_token(body.refresh_token)
    except InvalidTokenError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    session_result = await db.execute(
        select(UserSession).where(
            UserSession.token == body.refresh_token,
            UserSession.is_active == True,  # noqa: E712
        )
    )
    session = session_result.scalar_one_or_none()
    if session is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session is expired or revoked.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_result = await db.execute(
        select(User).where(User.user_uuid == uuid.UUID(token_data.user_id))
    )
    user = user_result.scalar_one_or_none()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    role_result = await db.execute(
        select(UserRole.role_name)
        .join(UserRoleMapping, UserRoleMapping.role_id == UserRole.role_id)
        .where(UserRoleMapping.user_id == user.user_id)
        .limit(1)
    )
    role = role_result.scalar_one_or_none()
    if role is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User has no assigned role.",
        )

    access_token = create_access_token(
        user_id=token_data.user_id,
        role=role,
        session_id=str(session.session_uuid),
    )
    return RefreshResponse(access_token=access_token)


@router.post("/logout", response_model=LogoutResponse)
async def logout(current_user: CurrentUser, db: AsyncSession = Depends(get_db)) -> LogoutResponse:
    if current_user.session_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token carries no session — nothing to revoke.",
        )

    await db.execute(
        update(UserSession)
        .where(UserSession.session_uuid == uuid.UUID(current_user.session_id))
        .values(is_active=False)
    )
    return LogoutResponse(message="Logged out successfully.")
