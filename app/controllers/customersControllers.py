from __future__ import annotations

from fastapi import APIRouter

from app.models.schemas import CustomerCreate, CustomerOut, CustomerUpdate
from app.services import customersServices as customers_service

router = APIRouter(prefix="/api/v1/customers", tags=["customers"])


@router.get("", response_model=list[CustomerOut])
def list_customers(name: str | None = None):
    return customers_service.list_customers(name=name)


@router.post("", response_model=CustomerOut, status_code=201)
def create_customer(payload: CustomerCreate):
    return customers_service.create_customer(payload)


@router.get("/{customer_id}", response_model=CustomerOut)
def get_customer(customer_id: str):
    return customers_service.get_customer(customer_id)


@router.put("/{customer_id}", response_model=CustomerOut)
def update_customer(customer_id: str, payload: CustomerUpdate):
    return customers_service.update_customer(customer_id, payload)


@router.delete("/{customer_id}", status_code=204)
def deactivate_customer(customer_id: str):
    customers_service.deactivate_customer(customer_id)
