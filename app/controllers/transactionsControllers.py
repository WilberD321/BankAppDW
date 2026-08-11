from __future__ import annotations

from datetime import date

from fastapi import APIRouter

from app.models.schemas import TransactionOut, TransferRequest
from app.services import transactionsServices as transactions_service

router = APIRouter(prefix="/api/v1/transactions", tags=["transactions"])


@router.get("", response_model=list[TransactionOut])
def list_transactions(start_date: date | None = None, type: str | None = None):
    return transactions_service.list_transactions(start_date=start_date, type=type)


@router.post("/transfer", response_model=TransactionOut, status_code=201)
def transfer(payload: TransferRequest):
    return transactions_service.transfer(payload)
