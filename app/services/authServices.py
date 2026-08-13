from __future__ import annotations

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.models.orm import CustomerRow, UserRow
from app.models.schemas import (
    AdminUpdateUserRequest,
    AuthenticatedUser,
    LoginRequest,
    SelfPasswordChangeRequest,
    TokenResponse,
    UserCreate,
    UserOut,
)
from app.services.auth import create_access_token, hash_password, verify_password
from app.services.db import get_session
from app.services.ids import insert_with_id


def to_user_out(row: UserRow) -> UserOut:
    return UserOut(id=row.id, username=row.username, role=row.role, customer_id=row.customer_id)


def login(payload: LoginRequest) -> TokenResponse:
    with get_session() as session:
        row = session.execute(select(UserRow).where(UserRow.username == payload.username)).scalar_one_or_none()
        if row is None or not verify_password(payload.password, row.password_hash):
            raise HTTPException(status_code=401, detail="Invalid username or password")
        token = create_access_token(row)
        return TokenResponse(access_token=token)


def create_login(payload: UserCreate) -> UserOut:
    with get_session() as session:
        if session.get(CustomerRow, payload.customer_id) is None:
            raise HTTPException(status_code=400, detail="Customer not found: %s" % payload.customer_id)

        existing = session.execute(
            select(UserRow).where(UserRow.customer_id == payload.customer_id)
        ).scalar_one_or_none()
        if existing is not None:
            raise HTTPException(status_code=409, detail="Customer already has login credentials")

        row = insert_with_id(
            session,
            UserRow,
            "u",
            None,
            {
                "username": payload.username,
                "password_hash": hash_password(payload.password),
                "role": "customer",
                "customer_id": payload.customer_id,
            },
            "Username already taken",
        )
        session.commit()
        return to_user_out(row)


def admin_update_customer_login(
    customer_id: str, payload: AdminUpdateUserRequest, current_user: AuthenticatedUser
) -> UserOut:
    with get_session() as session:
        admin_row = session.get(UserRow, current_user.id)
        if admin_row is None or not verify_password(payload.admin_password, admin_row.password_hash):
            raise HTTPException(status_code=401, detail="Invalid password")

        if payload.username is None and payload.new_password is None:
            raise HTTPException(status_code=400, detail="Must provide username and/or new_password")

        row = session.execute(select(UserRow).where(UserRow.customer_id == customer_id)).scalar_one_or_none()
        if row is None:
            raise HTTPException(status_code=404, detail="No login found for customer: %s" % customer_id)

        if payload.username is not None:
            row.username = payload.username
        if payload.new_password is not None:
            row.password_hash = hash_password(payload.new_password)

        try:
            session.flush()
        except IntegrityError as exc:
            session.rollback()
            raise HTTPException(status_code=409, detail="Username already taken") from exc

        session.commit()
        return to_user_out(row)


def change_own_password(payload: SelfPasswordChangeRequest, current_user: AuthenticatedUser) -> UserOut:
    with get_session() as session:
        row = session.get(UserRow, current_user.id)
        if row is None or not verify_password(payload.current_password, row.password_hash):
            raise HTTPException(status_code=401, detail="Current password is incorrect")

        row.password_hash = hash_password(payload.new_password)
        session.commit()
        return to_user_out(row)
