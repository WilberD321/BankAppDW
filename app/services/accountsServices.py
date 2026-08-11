from __future__ import annotations

from fastapi import HTTPException
from sqlalchemy import select

from app.models.orm import AccountRow, CustomerRow
from app.models.schemas import AccountCreate, AccountOut
from app.services.db import get_session
from app.services.ids import insert_with_id


def to_account_out(row: AccountRow) -> AccountOut:
    return AccountOut(id=row.id, owner_id=row.owner_id, branch_id=row.branch_id, balance=float(row.balance))


def list_accounts(
    owner_id: str | None = None, branch_id: str | None = None, min_balance: float | None = None
) -> list[AccountOut]:
    with get_session() as session:
        query = select(AccountRow)
        if owner_id is not None:
            query = query.where(AccountRow.owner_id == owner_id)
        if branch_id is not None:
            query = query.where(AccountRow.branch_id == branch_id)
        if min_balance is not None:
            query = query.where(AccountRow.balance >= min_balance)
        rows = session.execute(query).scalars().all()
        return [to_account_out(row) for row in rows]


def create_account(payload: AccountCreate) -> AccountOut:
    with get_session() as session:
        if session.get(CustomerRow, payload.owner_id) is None:
            raise HTTPException(status_code=400, detail="Owner customer id not found: %s" % payload.owner_id)
        row = insert_with_id(
            session,
            AccountRow,
            "a",
            payload.id,
            {"owner_id": payload.owner_id, "branch_id": payload.branch_id, "balance": payload.balance},
            "Account already exists",
        )
        session.commit()
        return to_account_out(row)


def delete_account(account_id: str) -> None:
    with get_session() as session:
        row = session.get(AccountRow, account_id)
        if row is None:
            raise HTTPException(status_code=404, detail="Account not found")
        session.delete(row)
        session.commit()
