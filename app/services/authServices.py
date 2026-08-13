from __future__ import annotations

from fastapi import HTTPException
from sqlalchemy import select

from app.models.orm import CustomerRow, UserRow
from app.models.schemas import LoginRequest, TokenResponse, UserCreate, UserOut
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
