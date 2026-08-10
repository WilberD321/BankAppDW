from __future__ import annotations

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from bank import Bank
from customer import Customer

app = FastAPI(title="BankAppDW API")

bank = Bank("My Bank")
bank.add_customer(Customer("c001", "Alice", "alice@example.com"))
bank.add_customer(Customer("c002", "Bob", "bob@example.com"))


class CustomerOut(BaseModel):
    id: str
    name: str
    email: str | None = None


def to_customer_out(customer: Customer) -> CustomerOut:
    return CustomerOut(id=customer.id, name=customer.name, email=customer.email)


@app.get("/api/v1/customers", response_model=list[CustomerOut])
def list_customers():
    return [to_customer_out(c) for c in bank.get_customers()]


@app.get("/api/v1/customers/{customer_id}", response_model=CustomerOut)
def get_customer(customer_id: str):
    customer = bank.get_customer(customer_id)
    if customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    return to_customer_out(customer)
