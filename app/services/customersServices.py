from __future__ import annotations

from fastapi import HTTPException
from sqlalchemy import select

from app.models.orm import AccountRow, CustomerRow
from app.models.schemas import CustomerCreate, CustomerOut, CustomerUpdate
from app.services.db import get_session
from app.services.ids import insert_with_id


def to_customer_out(row: CustomerRow) -> CustomerOut:
    return CustomerOut(id=row.id, name=row.name, email=row.email)


def list_customers() -> list[CustomerOut]:
    with get_session() as session:
        rows = session.execute(select(CustomerRow)).scalars().all()
        return [to_customer_out(row) for row in rows]


def create_customer(payload: CustomerCreate) -> CustomerOut:
    with get_session() as session:
        row = insert_with_id(
            session,
            CustomerRow,
            "c",
            payload.id,
            {"name": payload.name, "email": payload.email},
            "Customer already exists",
        )
        session.commit()
        return to_customer_out(row)


def get_customer(customer_id: str) -> CustomerOut:
    with get_session() as session:
        row = session.get(CustomerRow, customer_id)
        if row is None:
            raise HTTPException(status_code=404, detail="Customer not found")
        return to_customer_out(row)


def update_customer(customer_id: str, payload: CustomerUpdate) -> CustomerOut:
    updates = {k: v for k, v in payload.model_dump(exclude_unset=True).items() if v is not None}
    with get_session() as session:
        row = session.get(CustomerRow, customer_id)
        if row is None:
            raise HTTPException(status_code=404, detail="Customer not found")
        for key, value in updates.items():
            setattr(row, key, value)
        session.commit()
        session.refresh(row)
        return to_customer_out(row)


def deactivate_customer(customer_id: str) -> None:
    with get_session() as session:
        row = session.get(CustomerRow, customer_id)
        if row is None:
            raise HTTPException(status_code=404, detail="Customer not found")
        session.query(AccountRow).filter(AccountRow.owner_id == customer_id).delete()
        session.delete(row)
        session.commit()
