from __future__ import annotations

from fastapi import HTTPException

from app.models.schemas import CustomerCreate, CustomerOut, CustomerUpdate
from app.services.db import accounts_collection, customers_collection
from app.services.ids import insert_with_id


def to_customer_out(doc: dict) -> CustomerOut:
    return CustomerOut(id=doc["_id"], name=doc["name"], email=doc.get("email"))


def list_customers() -> list[CustomerOut]:
    return [to_customer_out(doc) for doc in customers_collection().find()]


def create_customer(payload: CustomerCreate) -> CustomerOut:
    doc = insert_with_id(
        customers_collection(),
        "c",
        payload.id,
        {"name": payload.name, "email": payload.email},
        "Customer already exists",
    )
    return to_customer_out(doc)


def get_customer(customer_id: str) -> CustomerOut:
    doc = customers_collection().find_one({"_id": customer_id})
    if doc is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    return to_customer_out(doc)


def update_customer(customer_id: str, payload: CustomerUpdate) -> CustomerOut:
    updates = {k: v for k, v in payload.model_dump(exclude_unset=True).items() if v is not None}
    if updates:
        customers_collection().update_one({"_id": customer_id}, {"$set": updates})
    doc = customers_collection().find_one({"_id": customer_id})
    if doc is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    return to_customer_out(doc)


def deactivate_customer(customer_id: str) -> None:
    result = customers_collection().delete_one({"_id": customer_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Customer not found")
    accounts_collection().delete_many({"owner_id": customer_id})
