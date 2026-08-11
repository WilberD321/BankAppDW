from __future__ import annotations

import uuid
from datetime import date, datetime, time, timezone

from fastapi import HTTPException

from app.models.schemas import TransactionOut, TransferRequest
from app.services.db import accounts_collection, get_client, transactions_collection


def to_transaction_out(doc: dict) -> TransactionOut:
    return TransactionOut(
        id=doc["_id"],
        from_account_id=doc["from_account_id"],
        to_account_id=doc["to_account_id"],
        amount=doc["amount"],
        type=doc["type"],
        timestamp=doc["timestamp"],
    )


def list_transactions(start_date: date | None = None, type: str | None = None) -> list[TransactionOut]:
    query: dict = {}
    if start_date is not None:
        query["timestamp"] = {"$gte": datetime.combine(start_date, time.min, tzinfo=timezone.utc)}
    if type is not None:
        query["type"] = type
    return [to_transaction_out(doc) for doc in transactions_collection().find(query)]


def transfer(payload: TransferRequest) -> TransactionOut:
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
