from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends

from app.models.schemas import AuthenticatedUser, DepositRequest, TransactionOut, TransferRequest, WithdrawRequest
from app.services import transactionsServices as transactions_service
from app.services.authDeps import get_current_user

router = APIRouter(prefix="/api/v1/transactions", tags=["transactions"])


@router.get("", response_model=list[TransactionOut])
def list_transactions(
    start_date: date | None = None,
    type: str | None = None,
    from_account_id: str | None = None,
    to_account_id: str | None = None,
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    return transactions_service.list_transactions(
        current_user,
        start_date=start_date,
        type=type,
        from_account_id=from_account_id,
        to_account_id=to_account_id,
    )


@router.post("/transfer", response_model=TransactionOut, status_code=201)
def transfer(payload: TransferRequest, current_user: AuthenticatedUser = Depends(get_current_user)):
    return transactions_service.transfer(payload, current_user)


@router.post("/deposit", response_model=TransactionOut, status_code=201)
def deposit(payload: DepositRequest, current_user: AuthenticatedUser = Depends(get_current_user)):
    return transactions_service.deposit(payload, current_user)


@router.post("/withdraw", response_model=TransactionOut, status_code=201)
def withdraw(payload: WithdrawRequest, current_user: AuthenticatedUser = Depends(get_current_user)):
    return transactions_service.withdraw(payload, current_user)
