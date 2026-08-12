from __future__ import annotations

import pytest


@pytest.fixture
def customer(client):
    client.post("/api/v1/customers", json={"id": "c001", "name": "Alice"})
    return "c001"


def test_list_accounts_unfiltered_returns_all(client, customer):
    client.post("/api/v1/accounts", json={"id": "a001", "owner_id": customer, "branch_id": "123", "balance": 50.0})
    client.post("/api/v1/accounts", json={"id": "a002", "owner_id": customer, "branch_id": "456", "balance": 75.0})

    response = client.get("/api/v1/accounts")

    assert response.status_code == 200
    body = response.json()
    assert {a["id"] for a in body} == {"a001", "a002"}
    for account in body:
        assert {"id", "owner_id", "branch_id", "balance"} <= account.keys()


def test_create_account_auto_id(client, customer):
    response = client.post("/api/v1/accounts", json={"owner_id": customer, "branch_id": "123", "balance": 100.0})

    assert response.status_code == 201
    body = response.json()
    assert body["id"] == "a001"
    assert body["owner_id"] == "c001"
    assert body["balance"] == 100.0


def test_create_account_explicit_id(client, customer):
    response = client.post("/api/v1/accounts", json={"id": "a050", "owner_id": customer, "branch_id": "123"})

    assert response.status_code == 201
    assert response.json()["id"] == "a050"


def test_create_account_duplicate_id_returns_409(client, customer):
    client.post("/api/v1/accounts", json={"id": "a001", "owner_id": customer, "branch_id": "123"})

    response = client.post("/api/v1/accounts", json={"id": "a001", "owner_id": customer, "branch_id": "123"})

    assert response.status_code == 409


def test_create_account_unknown_owner_returns_400(client):
    response = client.post("/api/v1/accounts", json={"owner_id": "does-not-exist", "branch_id": "123"})

    assert response.status_code == 400


def test_create_account_auto_id_fast_forwards_past_explicit_id(client, customer):
    client.post("/api/v1/accounts", json={"id": "a050", "owner_id": customer, "branch_id": "123"})

    response = client.post("/api/v1/accounts", json={"owner_id": customer, "branch_id": "123"})

    assert response.status_code == 201
    assert response.json()["id"] == "a051"


def test_list_accounts_filters(client, customer):
    client.post("/api/v1/accounts", json={"id": "a001", "owner_id": customer, "branch_id": "AAA", "balance": 50.0})
    client.post("/api/v1/accounts", json={"id": "a002", "owner_id": customer, "branch_id": "BBB", "balance": 500.0})

    response = client.get("/api/v1/accounts", params={"owner_id": customer})
    assert {a["id"] for a in response.json()} == {"a001", "a002"}

    response = client.get("/api/v1/accounts", params={"branch_id": "AAA"})
    assert {a["id"] for a in response.json()} == {"a001"}

    response = client.get("/api/v1/accounts", params={"min_balance": 100})
    assert {a["id"] for a in response.json()} == {"a002"}


def test_get_account(client, customer):
    client.post("/api/v1/accounts", json={"id": "a001", "owner_id": customer, "branch_id": "123", "balance": 10.0})

    response = client.get("/api/v1/accounts/a001")

    assert response.status_code == 200
    assert response.json()["branch_id"] == "123"


def test_get_account_not_found(client):
    response = client.get("/api/v1/accounts/does-not-exist")

    assert response.status_code == 404


def test_update_account_branch_id(client, customer):
    client.post("/api/v1/accounts", json={"id": "a001", "owner_id": customer, "branch_id": "123", "balance": 500.0})

    response = client.put("/api/v1/accounts/a001", json={"branch_id": "999"})

    assert response.status_code == 200
    body = response.json()
    assert body["branch_id"] == "999"
    assert body["balance"] == 500.0
    assert body["owner_id"] == "c001"


def test_update_account_not_found(client):
    response = client.put("/api/v1/accounts/does-not-exist", json={"branch_id": "999"})

    assert response.status_code == 404


def test_delete_account(client, customer):
    client.post("/api/v1/accounts", json={"id": "a001", "owner_id": customer, "branch_id": "123"})

    response = client.delete("/api/v1/accounts/a001")

    assert response.status_code == 204
    assert client.get("/api/v1/accounts/a001").status_code == 404


def test_delete_account_not_found(client):
    response = client.delete("/api/v1/accounts/does-not-exist")

    assert response.status_code == 404
