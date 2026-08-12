from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class CustomerOut(BaseModel):
    id: str
    name: str
    email: str | None = None


class CustomerCreate(BaseModel):
    id: str | None = None
    name: str
    email: str | None = None


class CustomerUpdate(BaseModel):
    name: str | None = None
    email: str | None = None


class AccountOut(BaseModel):
    id: str
    owner_id: str
    branch_id: str
    balance: float


class AccountCreate(BaseModel):
    id: str | None = None
    owner_id: str
    branch_id: str
    balance: float = Field(default=0.0, ge=0)


class AccountUpdate(BaseModel):
    branch_id: str | None = None


class TransferRequest(BaseModel):
    from_account_id: str
    to_account_id: str
    amount: float = Field(gt=0)


class DepositRequest(BaseModel):
    account_id: str
    amount: float = Field(gt=0)


class WithdrawRequest(BaseModel):
    account_id: str
    amount: float = Field(gt=0)


class TransactionOut(BaseModel):
    id: str
    from_account_id: str | None
    to_account_id: str | None
    amount: float
    type: str
    timestamp: datetime
