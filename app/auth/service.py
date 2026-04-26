from datetime import datetime, timedelta, timezone
from typing import Literal

from jose import JWTError, jwt
from pydantic import BaseModel

from app.config import get_settings

settings = get_settings()


class TokenData(BaseModel):
    user_id: str
    role: Literal["customer", "support_agent", "admin"]
    session_id: str | None = None


class RefreshTokenData(BaseModel):
    user_id: str
    is_refresh: bool = True


def create_access_token(
    user_id: str,
    role: Literal["customer", "support_agent", "admin"],
    session_id: str | None = None,
) -> str:
    """Create a signed JWT access token.

    Args:
        user_id:    Database PK for the authenticated user.
        role:       RBAC role — determines which tools the user may call.
        session_id: Optional conversation session to embed in the token.

    Returns:
        Signed JWT string.
    """
    now = datetime.now(tz=timezone.utc)
    expire = now + timedelta(minutes=settings.jwt_access_token_expire_minutes)

    payload: dict = {
        "sub": str(user_id),
        "role": role,
        "iat": now,
        "exp": expire,
        "type": "access",
    }
    if session_id:
        payload["session_id"] = session_id

    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def create_refresh_token(user_id: str) -> str:
    now = datetime.now(tz=timezone.utc)
    expire = now + timedelta(days=settings.jwt_refresh_token_expire_days)
    payload: dict = {
        "sub": str(user_id),
        "iat": now,
        "exp": expire,
        "type": "refresh",
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


class InvalidTokenError(Exception):
    """Raised when a JWT cannot be decoded or fails validation."""
    
    
    
def verify_access_token(token: str) -> TokenData:
    """Decode and validate an access token.

    Args:
        token: Raw JWT string from the Authorization header.

    Returns:
        TokenData with user_id, role, and optional session_id.

    Raises:
        InvalidTokenError: If the token is expired, malformed, or wrong type.
    """
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )
    except JWTError as exc:
        raise InvalidTokenError(f"Token decode failed: {exc}") from exc

    if payload.get("type") != "access":
        raise InvalidTokenError("Expected access token, got refresh token.")

    user_id_raw = payload.get("sub")
    role = payload.get("role")

    if user_id_raw is None or role is None:
        raise InvalidTokenError("Token missing required claims (sub, role).")

    user_id = user_id_raw

    return TokenData(
        user_id=user_id,
        role=role,
        session_id=payload.get("session_id"),
    )


def verify_refresh_token(token: str) -> RefreshTokenData:
    """Decode and validate a refresh token.

    Args:
        token: Raw JWT string.

    Returns:
        RefreshTokenData with user_id.

    Raises:
        InvalidTokenError: If the token is expired, malformed, or wrong type.
    """
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )
    except JWTError as exc:
        raise InvalidTokenError(f"Token decode failed: {exc}") from exc

    if payload.get("type") != "refresh":
        raise InvalidTokenError("Expected refresh token, got access token.")

    user_id_raw = payload.get("sub")
    if user_id_raw is None:
        raise InvalidTokenError("Refresh token missing 'sub' claim.")

    user_id = user_id_raw

    return RefreshTokenData(user_id=user_id)
