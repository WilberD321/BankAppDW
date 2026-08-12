from __future__ import annotations

import uuid
from datetime import date, datetime, time, timezone
from decimal import Decimal

from fastapi import HTTPException
from sqlalchemy import select

from app.models.orm import AccountRow, TransactionRow
from app.models.schemas import DepositRequest, TransactionOut, TransferRequest, WithdrawRequest
from app.services.db import get_session


def to_transaction_out(row: TransactionRow) -> TransactionOut:
    return TransactionOut(
        id=row.id,
        from_account_id=row.from_account_id,
        to_account_id=row.to_account_id,
        amount=float(row.amount),
        type=row.type,
        timestamp=row.timestamp,
    )


def list_transactions(start_date: date | None = None, type: str | None = None) -> list[TransactionOut]:
    with get_session() as session:
        query = select(TransactionRow)
        if start_date is not None:
            query = query.where(TransactionRow.timestamp >= datetime.combine(start_date, time.min, tzinfo=timezone.utc))
        if type is not None:
            query = query.where(TransactionRow.type == type)
        rows = session.execute(query).scalars().all()
        return [to_transaction_out(row) for row in rows]


def transfer(payload: TransferRequest) -> TransactionOut:
    with get_session() as session:
        from_account = session.get(AccountRow, payload.from_account_id, with_for_update=True)
        to_account = session.get(AccountRow, payload.to_account_id, with_for_update=True)
        if from_account is None or to_account is None:
            raise HTTPException(status_code=404, detail="Account not found")
        amount = Decimal(str(payload.amount))
        if from_account.balance < amount:
            raise HTTPException(status_code=400, detail="Insufficient funds")

        from_account.balance -= amount
        to_account.balance += amount

        transaction_row = TransactionRow(
            id=str(uuid.uuid4()),
            from_account_id=payload.from_account_id,
            to_account_id=payload.to_account_id,
            amount=payload.amount,
            type="TRANSFER",
            timestamp=datetime.now(timezone.utc),
        )
        session.add(transaction_row)
        session.commit()
        session.refresh(transaction_row)
        return to_transaction_out(transaction_row)


def deposit(payload: DepositRequest) -> TransactionOut:
    with get_session() as session:
        account = session.get(AccountRow, payload.account_id, with_for_update=True)
        if account is None:
            raise HTTPException(status_code=404, detail="Account not found")

        account.balance += Decimal(str(payload.amount))

        transaction_row = TransactionRow(
            id=str(uuid.uuid4()),
            from_account_id=None,
            to_account_id=payload.account_id,
            amount=payload.amount,
            type="DEPOSIT",
            timestamp=datetime.now(timezone.utc),
        )
        session.add(transaction_row)
        session.commit()
        session.refresh(transaction_row)
        return to_transaction_out(transaction_row)


def withdraw(payload: WithdrawRequest) -> TransactionOut:
    with get_session() as session:
        account = session.get(AccountRow, payload.account_id, with_for_update=True)
        if account is None:
            raise HTTPException(status_code=404, detail="Account not found")
        amount = Decimal(str(payload.amount))
        if account.balance < amount:
            raise HTTPException(status_code=400, detail="Insufficient funds")

        account.balance -= amount

        transaction_row = TransactionRow(
            id=str(uuid.uuid4()),
            from_account_id=payload.account_id,
            to_account_id=None,
            amount=payload.amount,
            type="WITHDRAWAL",
            timestamp=datetime.now(timezone.utc),
        )
        session.add(transaction_row)
        session.commit()
        session.refresh(transaction_row)
        return to_transaction_out(transaction_row)
