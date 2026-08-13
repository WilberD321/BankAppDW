from __future__ import annotations

from fastapi import APIRouter, Depends

from app.models.schemas import LoginRequest, TokenResponse, UserCreate, UserOut
from app.services import authServices as auth_service
from app.services.authDeps import require_role

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest):
    return auth_service.login(payload)


@router.post("/users", response_model=UserOut, status_code=201, dependencies=[Depends(require_role("admin"))])
def create_login(payload: UserCreate):
    return auth_service.create_login(payload)
