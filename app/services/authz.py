from __future__ import annotations

from fastapi import HTTPException

from app.models.schemas import AuthenticatedUser


def require_self_or_admin(current_user: AuthenticatedUser, owning_customer_id: str) -> None:
    if current_user.role == "admin":
        return
    if current_user.role == "customer" and current_user.customer_id == owning_customer_id:
        return
    raise HTTPException(status_code=403, detail="Not authorized")
