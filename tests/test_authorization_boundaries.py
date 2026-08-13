from __future__ import annotations

import pytest


@pytest.fixture
def two_customers(admin_client):
    admin_client.post("/api/v1/customers", json={"id": "c001", "name": "Alice"})
    admin_client.post("/api/v1/customers", json={"id": "c002", "name": "Bob"})
    admin_client.post("/api/v1/accounts", json={"id": "a001", "owner_id": "c001", "branch_id": "123", "balance": 500.0})
    admin_client.post("/api/v1/accounts", json={"id": "a002", "owner_id": "c002", "branch_id": "456", "balance": 200.0})
    return "c001", "c002"


def test_customer_cannot_view_other_customers_record(admin_client, two_customers, customer_client_for):
    _, customer_b = two_customers
    alice_client = customer_client_for("c001")

    response = alice_client.get(f"/api/v1/customers/{customer_b}")

    assert response.status_code == 403


def test_customer_cannot_update_other_customers_record(admin_client, two_customers, customer_client_for):
    _, customer_b = two_customers
    alice_client = customer_client_for("c001")

    response = alice_client.put(f"/api/v1/customers/{customer_b}", json={"name": "Hacked"})

    assert response.status_code == 403


def test_customer_can_view_own_record(two_customers, customer_client_for):
    alice_client = customer_client_for("c001")

    response = alice_client.get("/api/v1/customers/c001")

    assert response.status_code == 200


@pytest.mark.parametrize(
    "method,path,json",
    [
        ("get", "/api/v1/customers", None),
        ("post", "/api/v1/customers", {"name": "New"}),
        ("delete", "/api/v1/customers/c001", None),
        ("post", "/api/v1/accounts", {"owner_id": "c001", "branch_id": "123"}),
        ("put", "/api/v1/accounts/a001", {"branch_id": "999"}),
        ("delete", "/api/v1/accounts/a001", None),
    ],
)
def test_customer_blocked_from_admin_only_routes(two_customers, customer_client_for, method, path, json):
    alice_client = customer_client_for("c001")

    response = getattr(alice_client, method)(path, json=json) if json is not None else getattr(alice_client, method)(path)

    assert response.status_code == 403


def test_customer_account_list_scoped_to_own_accounts_even_with_foreign_owner_id(two_customers, customer_client_for):
    alice_client = customer_client_for("c001")

    response = alice_client.get("/api/v1/accounts", params={"owner_id": "c002"})

    assert response.status_code == 200
    assert {a["id"] for a in response.json()} == {"a001"}


def test_customer_cannot_view_other_customers_account(two_customers, customer_client_for):
    alice_client = customer_client_for("c001")

    response = alice_client.get("/api/v1/accounts/a002")

    assert response.status_code == 403


def test_transfer_out_of_unowned_account_forbidden(two_customers, customer_client_for):
    alice_client = customer_client_for("c001")

    response = alice_client.post(
        "/api/v1/transactions/transfer", json={"from_account_id": "a002", "to_account_id": "a001", "amount": 10.0}
    )

    assert response.status_code == 403


def test_transfer_to_unowned_account_allowed(two_customers, customer_client_for):
    alice_client = customer_client_for("c001")

    response = alice_client.post(
        "/api/v1/transactions/transfer", json={"from_account_id": "a001", "to_account_id": "a002", "amount": 10.0}
    )

    assert response.status_code == 201


def test_deposit_to_unowned_account_forbidden(two_customers, customer_client_for):
    alice_client = customer_client_for("c001")

    response = alice_client.post("/api/v1/transactions/deposit", json={"account_id": "a002", "amount": 10.0})

    assert response.status_code == 403


def test_deposit_to_own_account_allowed(two_customers, customer_client_for):
    alice_client = customer_client_for("c001")

    response = alice_client.post("/api/v1/transactions/deposit", json={"account_id": "a001", "amount": 10.0})

    assert response.status_code == 201


def test_withdraw_from_unowned_account_forbidden(two_customers, customer_client_for):
    alice_client = customer_client_for("c001")

    response = alice_client.post("/api/v1/transactions/withdraw", json={"account_id": "a002", "amount": 10.0})

    assert response.status_code == 403


def test_customer_transaction_list_scoped_to_own_accounts(admin_client, two_customers, customer_client_for):
    admin_client.post(
        "/api/v1/transactions/transfer", json={"from_account_id": "a001", "to_account_id": "a002", "amount": 50.0}
    )
    admin_client.post("/api/v1/transactions/deposit", json={"account_id": "a002", "amount": 20.0})
    alice_client = customer_client_for("c001")

    response = alice_client.get("/api/v1/transactions")

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["from_account_id"] == "a001"
