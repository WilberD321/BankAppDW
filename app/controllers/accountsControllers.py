from __future__ import annotations

from fastapi import APIRouter

from app.models.schemas import AccountCreate, AccountOut, AccountUpdate
from app.services import accountsServices as accounts_service

router = APIRouter(prefix="/api/v1/accounts", tags=["accounts"])


@router.get("", response_model=list[AccountOut])
def list_accounts(owner_id: str | None = None, branch_id: str | None = None, min_balance: float | None = None):
    return accounts_service.list_accounts(owner_id=owner_id, branch_id=branch_id, min_balance=min_balance)


@router.post("", response_model=AccountOut, status_code=201)
def create_account(payload: AccountCreate):
    return accounts_service.create_account(payload)


@router.get("/{account_id}", response_model=AccountOut)
def get_account(account_id: str):
    return accounts_service.get_account(account_id)


@router.put("/{account_id}", response_model=AccountOut)
def update_account(account_id: str, payload: AccountUpdate):
    return accounts_service.update_account(account_id, payload)


@router.delete("/{account_id}", status_code=204)
def delete_account(account_id: str):
    accounts_service.delete_account(account_id)
