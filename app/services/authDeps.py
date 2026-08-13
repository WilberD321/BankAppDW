from __future__ import annotations

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.models.orm import UserRow
from app.models.schemas import AuthenticatedUser
from app.services.auth import decode_access_token
from app.services.db import get_session

_bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
) -> AuthenticatedUser:
    if credentials is None:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        claims = decode_access_token(credentials.credentials)
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    with get_session() as session:
        row = session.get(UserRow, claims["sub"])
        if row is None:
            raise HTTPException(status_code=401, detail="Invalid or expired token")
        return AuthenticatedUser(id=row.id, username=row.username, role=row.role, customer_id=row.customer_id)


def require_role(*roles: str):
    def _check(current_user: AuthenticatedUser = Depends(get_current_user)) -> AuthenticatedUser:
        if current_user.role not in roles:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return current_user

    return _check
