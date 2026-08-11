from __future__ import annotations

from fastapi import HTTPException

from app.models.schemas import AccountCreate, AccountOut
from app.services.db import accounts_collection, customers_collection
from app.services.ids import insert_with_id


def to_account_out(doc: dict) -> AccountOut:
    return AccountOut(id=doc["_id"], owner_id=doc["owner_id"], branch_id=doc["branch_id"], balance=doc["balance"])


def list_accounts(
    owner_id: str | None = None, branch_id: str | None = None, min_balance: float | None = None
) -> list[AccountOut]:
    query: dict = {}
    if owner_id is not None:
        query["owner_id"] = owner_id
    if branch_id is not None:
        query["branch_id"] = branch_id
    if min_balance is not None:
        query["balance"] = {"$gte": min_balance}
    return [to_account_out(doc) for doc in accounts_collection().find(query)]


def create_account(payload: AccountCreate) -> AccountOut:
    if customers_collection().find_one({"_id": payload.owner_id}) is None:
        raise HTTPException(status_code=400, detail="Owner customer id not found: %s" % payload.owner_id)
    doc = insert_with_id(
        accounts_collection(),
        "a",
        payload.id,
        {"owner_id": payload.owner_id, "branch_id": payload.branch_id, "balance": payload.balance},
        "Account already exists",
    )
    return to_account_out(doc)


def delete_account(account_id: str) -> None:
    result = accounts_collection().delete_one({"_id": account_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Account not found")
