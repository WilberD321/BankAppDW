from __future__ import annotations

from fastapi import APIRouter, Depends

from app.models.schemas import AccountCreate, AccountOut, AccountUpdate, AuthenticatedUser
from app.services import accountsServices as accounts_service
from app.services.authDeps import get_current_user, require_role

router = APIRouter(prefix="/api/v1/accounts", tags=["accounts"])


@router.get("", response_model=list[AccountOut])
def list_accounts(
    owner_id: str | None = None,
    branch_id: str | None = None,
    min_balance: float | None = None,
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    return accounts_service.list_accounts(
        current_user, owner_id=owner_id, branch_id=branch_id, min_balance=min_balance
    )


@router.post("", response_model=AccountOut, status_code=201, dependencies=[Depends(require_role("admin"))])
def create_account(payload: AccountCreate):
    return accounts_service.create_account(payload)


@router.get("/{account_id}", response_model=AccountOut)
def get_account(account_id: str, current_user: AuthenticatedUser = Depends(get_current_user)):
    return accounts_service.get_account(account_id, current_user)


@router.put("/{account_id}", response_model=AccountOut, dependencies=[Depends(require_role("admin"))])
def update_account(account_id: str, payload: AccountUpdate):
    return accounts_service.update_account(account_id, payload)


@router.delete("/{account_id}", status_code=204, dependencies=[Depends(require_role("admin"))])
def delete_account(account_id: str):
    accounts_service.delete_account(account_id)
