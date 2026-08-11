from __future__ import annotations

import uuid
from datetime import date, datetime, time, timezone

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from pymongo.errors import DuplicateKeyError

from db import accounts_collection, customers_collection, get_client, transactions_collection

app = FastAPI(title="BankAppDW API")


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
    branch_id: str
    balance: float


class AccountCreate(BaseModel):
    id: str
    owner_id: str
    branch_id: str
    balance: float = Field(default=0.0, ge=0)


class TransferRequest(BaseModel):
    from_account_id: str
    to_account_id: str
    amount: float = Field(gt=0)


class TransactionOut(BaseModel):
    id: str
    from_account_id: str
    to_account_id: str
    amount: float
    type: str
    timestamp: datetime


def to_customer_out(doc: dict) -> CustomerOut:
    return CustomerOut(id=doc["_id"], name=doc["name"], email=doc.get("email"))


def to_account_out(doc: dict) -> AccountOut:
    return AccountOut(id=doc["_id"], owner_id=doc["owner_id"], branch_id=doc["branch_id"], balance=doc["balance"])


def to_transaction_out(doc: dict) -> TransactionOut:
    return TransactionOut(
        id=doc["_id"],
        from_account_id=doc["from_account_id"],
        to_account_id=doc["to_account_id"],
        amount=doc["amount"],
        type=doc["type"],
        timestamp=doc["timestamp"],
    )


@app.get("/api/v1/customers", response_model=list[CustomerOut])
def list_customers():
    return [to_customer_out(doc) for doc in customers_collection().find()]


@app.post("/api/v1/customers", response_model=CustomerOut, status_code=201)
def create_customer(payload: CustomerCreate):
    doc = {"_id": payload.id, "name": payload.name, "email": payload.email}
    try:
        customers_collection().insert_one(doc)
    except DuplicateKeyError as exc:
        raise HTTPException(status_code=409, detail="Customer already exists") from exc
    return to_customer_out(doc)


@app.get("/api/v1/customers/{customer_id}", response_model=CustomerOut)
def get_customer(customer_id: str):
    doc = customers_collection().find_one({"_id": customer_id})
    if doc is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    return to_customer_out(doc)


@app.put("/api/v1/customers/{customer_id}", response_model=CustomerOut)
def update_customer(customer_id: str, payload: CustomerUpdate):
    updates = {k: v for k, v in payload.model_dump(exclude_unset=True).items() if v is not None}
    if updates:
        customers_collection().update_one({"_id": customer_id}, {"$set": updates})
    doc = customers_collection().find_one({"_id": customer_id})
    if doc is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    return to_customer_out(doc)


@app.delete("/api/v1/customers/{customer_id}", status_code=204)
def deactivate_customer(customer_id: str):
    result = customers_collection().delete_one({"_id": customer_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Customer not found")
    accounts_collection().delete_many({"owner_id": customer_id})


@app.get("/api/v1/accounts", response_model=list[AccountOut])
def list_accounts(owner_id: str | None = None, branch_id: str | None = None, min_balance: float | None = None):
    query: dict = {}
    if owner_id is not None:
        query["owner_id"] = owner_id
    if branch_id is not None:
        query["branch_id"] = branch_id
    if min_balance is not None:
        query["balance"] = {"$gte": min_balance}
    return [to_account_out(doc) for doc in accounts_collection().find(query)]


@app.post("/api/v1/accounts", response_model=AccountOut, status_code=201)
def create_account(payload: AccountCreate):
    if customers_collection().find_one({"_id": payload.owner_id}) is None:
        raise HTTPException(status_code=400, detail="Owner customer id not found: %s" % payload.owner_id)
    doc = {
        "_id": payload.id,
        "owner_id": payload.owner_id,
        "branch_id": payload.branch_id,
        "balance": payload.balance,
    }
    try:
        accounts_collection().insert_one(doc)
    except DuplicateKeyError as exc:
        raise HTTPException(status_code=409, detail="Account already exists") from exc
    return to_account_out(doc)


@app.delete("/api/v1/accounts/{account_id}", status_code=204)
def delete_account(account_id: str):
    result = accounts_collection().delete_one({"_id": account_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Account not found")


@app.get("/api/v1/transactions", response_model=list[TransactionOut])
def list_transactions(start_date: date | None = None, type: str | None = None):
    query: dict = {}
    if start_date is not None:
        query["timestamp"] = {"$gte": datetime.combine(start_date, time.min, tzinfo=timezone.utc)}
    if type is not None:
        query["type"] = type
    return [to_transaction_out(doc) for doc in transactions_collection().find(query)]


@app.post("/api/v1/transactions/transfer", response_model=TransactionOut, status_code=201)
def transfer(payload: TransferRequest):
    accounts = accounts_collection()
    with get_client().start_session() as session:
        with session.start_transaction():
            from_account = accounts.find_one({"_id": payload.from_account_id}, session=session)
            to_account = accounts.find_one({"_id": payload.to_account_id}, session=session)
            if from_account is None or to_account is None:
                raise HTTPException(status_code=404, detail="Account not found")
            if from_account["balance"] < payload.amount:
                raise HTTPException(status_code=400, detail="Insufficient funds")

            accounts.update_one(
                {"_id": payload.from_account_id}, {"$inc": {"balance": -payload.amount}}, session=session
            )
            accounts.update_one(
                {"_id": payload.to_account_id}, {"$inc": {"balance": payload.amount}}, session=session
            )

            transaction_doc = {
                "_id": str(uuid.uuid4()),
                "from_account_id": payload.from_account_id,
                "to_account_id": payload.to_account_id,
                "amount": payload.amount,
                "type": "TRANSFER",
                "timestamp": datetime.now(timezone.utc),
            }
            transactions_collection().insert_one(transaction_doc, session=session)

    return to_transaction_out(transaction_doc)
