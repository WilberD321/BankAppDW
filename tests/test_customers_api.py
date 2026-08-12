from __future__ import annotations


def test_list_customers_empty(client):
    response = client.get("/api/v1/customers")
    assert response.status_code == 200
    assert response.json() == []


def test_list_customers_returns_all(client):
    client.post("/api/v1/customers", json={"name": "Alice"})
    client.post("/api/v1/customers", json={"name": "Bob"})

    response = client.get("/api/v1/customers")

    assert response.status_code == 200
    assert {c["id"] for c in response.json()} == {"c001", "c002"}


def test_list_customers_filtered_by_name(client):
    client.post("/api/v1/customers", json={"name": "Alexandra"})
    client.post("/api/v1/customers", json={"name": "Bob"})

    response = client.get("/api/v1/customers", params={"name": "alex"})

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["name"] == "Alexandra"


def test_create_customer_auto_id(client):
    response = client.post("/api/v1/customers", json={"name": "Alice", "email": "alice@example.com"})

    assert response.status_code == 201
    body = response.json()
    assert body["id"] == "c001"
    assert body["name"] == "Alice"
    assert body["email"] == "alice@example.com"


def test_create_customer_explicit_id(client):
    response = client.post("/api/v1/customers", json={"id": "c050", "name": "Bob"})

    assert response.status_code == 201
    assert response.json()["id"] == "c050"


def test_create_customer_duplicate_id_returns_409(client):
    client.post("/api/v1/customers", json={"id": "c001", "name": "First"})

    response = client.post("/api/v1/customers", json={"id": "c001", "name": "Second"})

    assert response.status_code == 409


def test_create_customer_auto_id_fast_forwards_past_explicit_id(client):
    client.post("/api/v1/customers", json={"id": "c050", "name": "Explicit"})

    response = client.post("/api/v1/customers", json={"name": "AfterExplicit"})

    assert response.status_code == 201
    assert response.json()["id"] == "c051"


def test_get_customer(client):
    client.post("/api/v1/customers", json={"id": "c001", "name": "Alice"})

    response = client.get("/api/v1/customers/c001")

    assert response.status_code == 200
    assert response.json()["name"] == "Alice"


def test_get_customer_not_found(client):
    response = client.get("/api/v1/customers/does-not-exist")

    assert response.status_code == 404


def test_update_customer(client):
    client.post("/api/v1/customers", json={"id": "c001", "name": "Alice"})

    response = client.put("/api/v1/customers/c001", json={"name": "Alice Updated", "email": "new@example.com"})

    assert response.status_code == 200
    body = response.json()
    assert body["name"] == "Alice Updated"
    assert body["email"] == "new@example.com"


def test_update_customer_not_found(client):
    response = client.put("/api/v1/customers/does-not-exist", json={"name": "Nobody"})

    assert response.status_code == 404


def test_delete_customer(client):
    client.post("/api/v1/customers", json={"id": "c001", "name": "Alice"})

    response = client.delete("/api/v1/customers/c001")

    assert response.status_code == 204
    assert client.get("/api/v1/customers/c001").status_code == 404


def test_delete_customer_not_found(client):
    response = client.delete("/api/v1/customers/does-not-exist")

    assert response.status_code == 404


def test_delete_customer_cascades_to_accounts(client):
    client.post("/api/v1/customers", json={"id": "c001", "name": "Alice"})
    client.post("/api/v1/accounts", json={"id": "a001", "owner_id": "c001", "branch_id": "123", "balance": 50.0})

    response = client.delete("/api/v1/customers/c001")

    assert response.status_code == 204
    assert client.get("/api/v1/accounts", params={"owner_id": "c001"}).json() == []
