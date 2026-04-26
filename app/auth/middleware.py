from typing import Annotated, Literal

from fastapi import Depends, HTTPException, Query, WebSocket, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.auth.rbac import Role
from app.auth.service import InvalidTokenError, TokenData, verify_access_token

_bearer_scheme = HTTPBearer(auto_error=False)


def _credentials_to_token(
    credentials: HTTPAuthorizationCredentials | None,
) -> str:
    """Extract raw token string from bearer credentials or raise 401."""
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid Authorization header. Expected: Bearer <token>",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return credentials.credentials


async def get_current_user(
    credentials: Annotated[
        HTTPAuthorizationCredentials | None,
        Depends(_bearer_scheme),
    ],
) -> TokenData:
    """FastAPI dependency — decode the JWT and return the authenticated user.

    Injects TokenData(user_id, role, session_id) into the route handler.

    Raises:
        HTTPException 401: If the token is missing, malformed, or expired.
    """
    token = _credentials_to_token(credentials)
    try:
        return verify_access_token(token)
    except InvalidTokenError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc
        
        
def require_role(*allowed_roles: Role):
    """Return a FastAPI dependency that enforces one of the allowed roles.

    Args:
        *allowed_roles: One or more roles that may access the endpoint.

    Returns:
        An async dependency function compatible with Depends().

    Example:
        Depends(require_role("support_agent", "admin"))
    """

    async def _check_role(
        user: Annotated[TokenData, Depends(get_current_user)],
    ) -> TokenData:
        if user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    f"Role '{user.role}' is not permitted. "
                    f"Required: {', '.join(allowed_roles)}"
                ),
            )
        return user

    return _check_role


async def get_current_user_ws(
    websocket: WebSocket,
    token: Annotated[str | None, Query(alias="token")] = None,
) -> TokenData:
    """WebSocket dependency — extract JWT from the 'token' query parameter.

    WebSocket connections cannot send Authorization headers, so the token is
    passed as ?token=<jwt> in the connection URL.

    Closes the WebSocket with code 1008 (policy violation) if auth fails.

    Args:
        websocket: The active WebSocket connection.
        token:     Raw JWT string from the query string.

    Returns:
        TokenData for the authenticated user.
    """
    if token is None:
        await websocket.close(code=1008, reason="Missing token query parameter.")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="WebSocket connection requires ?token=<jwt>",
        )

    try:
        return verify_access_token(token)
    except InvalidTokenError as exc:
        await websocket.close(code=1008, reason=str(exc))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        ) from exc


CurrentUser = Annotated[TokenData, Depends(get_current_user)]