from __future__ import annotations

from fastapi import APIRouter, Depends

from app.models.schemas import AuthenticatedUser, CustomerCreate, CustomerOut, CustomerUpdate
from app.services import customersServices as customers_service
from app.services.authDeps import get_current_user, require_role

router = APIRouter(prefix="/api/v1/customers", tags=["customers"])


@router.get("", response_model=list[CustomerOut], dependencies=[Depends(require_role("admin"))])
def list_customers(name: str | None = None):
    return customers_service.list_customers(name=name)


@router.post("", response_model=CustomerOut, status_code=201, dependencies=[Depends(require_role("admin"))])
def create_customer(payload: CustomerCreate):
    return customers_service.create_customer(payload)


@router.get("/{customer_id}", response_model=CustomerOut)
def get_customer(customer_id: str, current_user: AuthenticatedUser = Depends(get_current_user)):
    return customers_service.get_customer(customer_id, current_user)


@router.put("/{customer_id}", response_model=CustomerOut)
def update_customer(
    customer_id: str, payload: CustomerUpdate, current_user: AuthenticatedUser = Depends(get_current_user)
):
    return customers_service.update_customer(customer_id, payload, current_user)


@router.delete("/{customer_id}", status_code=204, dependencies=[Depends(require_role("admin"))])
def deactivate_customer(customer_id: str):
    customers_service.deactivate_customer(customer_id)
