from __future__ import annotations

import pytest


@pytest.fixture
def two_accounts(admin_client):
    admin_client.post("/api/v1/customers", json={"id": "c001", "name": "Alice"})
    admin_client.post("/api/v1/customers", json={"id": "c002", "name": "Bob"})
    admin_client.post("/api/v1/accounts", json={"id": "a001", "owner_id": "c001", "branch_id": "123", "balance": 500.0})
    admin_client.post("/api/v1/accounts", json={"id": "a002", "owner_id": "c002", "branch_id": "456", "balance": 200.0})
    return "a001", "a002"


def _balances(client):
    return {a["id"]: a["balance"] for a in client.get("/api/v1/accounts").json()}


def test_list_transactions_unfiltered_returns_all(admin_client, two_accounts):
    from_id, to_id = two_accounts
    admin_client.post(
        "/api/v1/transactions/transfer",
        json={"from_account_id": from_id, "to_account_id": to_id, "amount": 100.0},
    )
    admin_client.post("/api/v1/transactions/deposit", json={"account_id": to_id, "amount": 20.0})

    response = admin_client.get("/api/v1/transactions")

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 2
    for tx in body:
        assert {"id", "from_account_id", "to_account_id", "amount", "type", "timestamp"} <= tx.keys()


def test_transfer_success(admin_client, two_accounts):
    from_id, to_id = two_accounts

    response = admin_client.post(
        "/api/v1/transactions/transfer",
        json={"from_account_id": from_id, "to_account_id": to_id, "amount": 100.0},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["type"] == "TRANSFER"
    assert body["from_account_id"] == from_id
    assert body["to_account_id"] == to_id
    assert body["amount"] == 100.0

    balances = _balances(admin_client)
    assert balances[from_id] == 400.0
    assert balances[to_id] == 300.0


def test_transfer_insufficient_funds(admin_client, two_accounts):
    from_id, to_id = two_accounts

    response = admin_client.post(
        "/api/v1/transactions/transfer",
        json={"from_account_id": from_id, "to_account_id": to_id, "amount": 999999.0},
    )

    assert response.status_code == 400
    assert _balances(admin_client)[from_id] == 500.0


def test_transfer_account_not_found(admin_client):
    response = admin_client.post(
        "/api/v1/transactions/transfer",
        json={"from_account_id": "does-not-exist-1", "to_account_id": "does-not-exist-2", "amount": 1.0},
    )

    assert response.status_code == 404


def test_deposit_success(admin_client, two_accounts):
    from_id, _ = two_accounts

    response = admin_client.post("/api/v1/transactions/deposit", json={"account_id": from_id, "amount": 50.0})

    assert response.status_code == 201
    body = response.json()
    assert body["type"] == "DEPOSIT"
    assert body["from_account_id"] is None
    assert body["to_account_id"] == from_id
    assert _balances(admin_client)[from_id] == 550.0


def test_deposit_account_not_found(admin_client):
    response = admin_client.post("/api/v1/transactions/deposit", json={"account_id": "does-not-exist", "amount": 1.0})

    assert response.status_code == 404


def test_withdraw_success(admin_client, two_accounts):
    from_id, _ = two_accounts

    response = admin_client.post("/api/v1/transactions/withdraw", json={"account_id": from_id, "amount": 50.0})

    assert response.status_code == 201
    body = response.json()
    assert body["type"] == "WITHDRAWAL"
    assert body["to_account_id"] is None
    assert body["from_account_id"] == from_id
    assert _balances(admin_client)[from_id] == 450.0


def test_withdraw_insufficient_funds(admin_client, two_accounts):
    from_id, _ = two_accounts

    response = admin_client.post("/api/v1/transactions/withdraw", json={"account_id": from_id, "amount": 999999.0})

    assert response.status_code == 400
    assert _balances(admin_client)[from_id] == 500.0


def test_withdraw_account_not_found(admin_client):
    response = admin_client.post("/api/v1/transactions/withdraw", json={"account_id": "does-not-exist", "amount": 1.0})

    assert response.status_code == 404


def test_list_transactions_filters(admin_client, two_accounts):
    from_id, to_id = two_accounts
    admin_client.post(
        "/api/v1/transactions/transfer",
        json={"from_account_id": from_id, "to_account_id": to_id, "amount": 100.0},
    )
    admin_client.post("/api/v1/transactions/deposit", json={"account_id": to_id, "amount": 20.0})

    response = admin_client.get("/api/v1/transactions", params={"type": "TRANSFER"})
    assert len(response.json()) == 1
    assert response.json()[0]["type"] == "TRANSFER"

    response = admin_client.get("/api/v1/transactions", params={"from_account_id": from_id})
    assert len(response.json()) == 1
    assert response.json()[0]["type"] == "TRANSFER"

    response = admin_client.get("/api/v1/transactions", params={"to_account_id": to_id})
    assert len(response.json()) == 2

    response = admin_client.get("/api/v1/transactions", params={"from_account_id": from_id, "to_account_id": to_id})
    assert len(response.json()) == 1
    assert response.json()[0]["type"] == "TRANSFER"
