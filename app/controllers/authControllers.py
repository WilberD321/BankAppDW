from __future__ import annotations

from fastapi import APIRouter, Depends

from app.models.schemas import (
    AdminUpdateUserRequest,
    AuthenticatedUser,
    LoginRequest,
    SelfPasswordChangeRequest,
    TokenResponse,
    UserCreate,
    UserOut,
)
from app.services import authServices as auth_service
from app.services.authDeps import get_current_user, require_role

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest):
    return auth_service.login(payload)


@router.post("/users", response_model=UserOut, status_code=201, dependencies=[Depends(require_role("admin"))])
def create_login(payload: UserCreate):
    return auth_service.create_login(payload)


@router.put("/users/by-customer/{customer_id}", response_model=UserOut, dependencies=[Depends(require_role("admin"))])
def admin_update_customer_login(
    customer_id: str, payload: AdminUpdateUserRequest, current_user: AuthenticatedUser = Depends(get_current_user)
):
    return auth_service.admin_update_customer_login(customer_id, payload, current_user)


@router.put("/me/password", response_model=UserOut)
def change_own_password(
    payload: SelfPasswordChangeRequest, current_user: AuthenticatedUser = Depends(get_current_user)
):
    return auth_service.change_own_password(payload, current_user)
