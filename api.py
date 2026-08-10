from __future__ import annotations

import uuid
from datetime import date, datetime, timezone

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from account import Account
from bank import Bank
from customer import Customer

app = FastAPI(title="BankAppDW API")

bank = Bank("My Bank")
bank.add_customer(Customer("c001", "Alice", "alice@example.com"))
bank.add_customer(Customer("c002", "Bob", "bob@example.com"))

_transactions: list["TransactionOut"] = []


class CustomerOut(BaseModel):
    id: str
    name: str
    email: str | None = None


class CustomerCreate(BaseModel):
    id: str
    name: str
    email: str | None = None


class CustomerUpdate(BaseModel):
    name: str | None = None
    email: str | None = None


class AccountOut(BaseModel):
    id: str
    owner_id: str
    balance: float


class AccountCreate(BaseModel):
    id: str
    owner_id: str
    balance: float = 0.0


class TransferRequest(BaseModel):
    from_account_id: str
    to_account_id: str
    amount: float


class TransactionOut(BaseModel):
    id: str
    from_account_id: str
    to_account_id: str
    amount: float
    type: str
    timestamp: datetime


def to_customer_out(customer: Customer) -> CustomerOut:
    return CustomerOut(id=customer.id, name=customer.name, email=customer.email)


def to_account_out(account: Account) -> AccountOut:
    owner_id = account.owner.id if isinstance(account.owner, Customer) else account.owner
    return AccountOut(id=account.id, owner_id=owner_id, balance=account.balance)


@app.get("/api/v1/customers", response_model=list[CustomerOut])
def list_customers():
    return [to_customer_out(c) for c in bank.get_customers()]


@app.post("/api/v1/customers", response_model=CustomerOut, status_code=201)
def create_customer(payload: CustomerCreate):
    customer = Customer(payload.id, payload.name, payload.email)
    try:
        bank.add_customer(customer)
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return to_customer_out(customer)


@app.get("/api/v1/customers/{customer_id}", response_model=CustomerOut)
def get_customer(customer_id: str):
    customer = bank.get_customer(customer_id)
    if customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    return to_customer_out(customer)


@app.put("/api/v1/customers/{customer_id}", response_model=CustomerOut)
def update_customer(customer_id: str, payload: CustomerUpdate):
    customer = bank.get_customer(customer_id)
    if customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    if payload.name is not None:
        customer.name = payload.name
    if payload.email is not None:
        customer.email = payload.email
    return to_customer_out(customer)


@app.delete("/api/v1/customers/{customer_id}", status_code=204)
def deactivate_customer(customer_id: str):
    if bank.get_customer(customer_id) is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    bank.remove_customer(customer_id)


@app.get("/api/v1/accounts", response_model=list[AccountOut])
def list_accounts(owner_id: str | None = None, min_balance: float | None = None):
    accounts = bank.find_accounts_by_customer(owner_id) if owner_id is not None else bank.get_accounts()
    if min_balance is not None:
        accounts = [a for a in accounts if a.balance >= min_balance]
    return [to_account_out(a) for a in accounts]


@app.post("/api/v1/accounts", response_model=AccountOut, status_code=201)
def create_account(payload: AccountCreate):
    if bank.get_account(payload.id) is not None:
        raise HTTPException(status_code=409, detail="Account already exists")
    try:
        account = Account(payload.id, payload.owner_id, payload.balance)
        bank.add_account(account)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return to_account_out(account)


@app.get("/api/v1/transactions", response_model=list[TransactionOut])
def list_transactions(start_date: date | None = None, type: str | None = None):
    results = _transactions
    if start_date is not None:
        results = [t for t in results if t.timestamp.date() >= start_date]
    if type is not None:
        results = [t for t in results if t.type == type]
    return results


@app.post("/api/v1/transactions/transfer", response_model=TransactionOut, status_code=201)
def transfer(payload: TransferRequest):
    from_account = bank.get_account(payload.from_account_id)
    to_account = bank.get_account(payload.to_account_id)
    if from_account is None or to_account is None:
        raise HTTPException(status_code=404, detail="Account not found")
    try:
        from_account.withdraw(payload.amount)
        to_account.deposit(payload.amount)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    transaction = TransactionOut(
        id=str(uuid.uuid4()),
        from_account_id=from_account.id,
        to_account_id=to_account.id,
        amount=payload.amount,
        type="TRANSFER",
        timestamp=datetime.now(timezone.utc),
    )
    _transactions.append(transaction)
    return transaction
