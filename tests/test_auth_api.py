from __future__ import annotations


def test_login_success(client, admin_user):
    response = client.post("/api/v1/auth/login", json=admin_user)

    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "bearer"
    assert body["access_token"]


def test_login_wrong_password(client, admin_user):
    response = client.post("/api/v1/auth/login", json={"username": admin_user["username"], "password": "wrong"})

    assert response.status_code == 401


def test_login_unknown_username(client):
    response = client.post("/api/v1/auth/login", json={"username": "nobody", "password": "whatever"})

    assert response.status_code == 401


def test_login_failure_messages_do_not_leak_which_field_was_wrong(client, admin_user):
    wrong_password = client.post(
        "/api/v1/auth/login", json={"username": admin_user["username"], "password": "wrong"}
    )
    unknown_user = client.post("/api/v1/auth/login", json={"username": "nobody", "password": "whatever"})

    assert wrong_password.json()["detail"] == unknown_user.json()["detail"]


def test_protected_route_without_token(client):
    response = client.get("/api/v1/customers")

    assert response.status_code == 401


def test_protected_route_with_malformed_token(client):
    response = client.get("/api/v1/customers", headers={"Authorization": "Bearer not-a-real-token"})

    assert response.status_code == 401


def test_protected_route_with_expired_token(client, admin_user, monkeypatch):
    monkeypatch.setenv("JWT_EXPIRE_MINUTES", "-1")
    login_response = client.post("/api/v1/auth/login", json=admin_user)
    expired_token = login_response.json()["access_token"]

    response = client.get("/api/v1/customers", headers={"Authorization": f"Bearer {expired_token}"})

    assert response.status_code == 401


def test_create_login_for_customer(admin_client):
    admin_client.post("/api/v1/customers", json={"id": "c001", "name": "Alice"})

    response = admin_client.post(
        "/api/v1/auth/users", json={"customer_id": "c001", "username": "alice", "password": "alicepass123"}
    )

    assert response.status_code == 201
    body = response.json()
    assert body["username"] == "alice"
    assert body["role"] == "customer"
    assert body["customer_id"] == "c001"
    assert "password_hash" not in body


def test_create_login_duplicate_customer_returns_409(admin_client):
    admin_client.post("/api/v1/customers", json={"id": "c001", "name": "Alice"})
    admin_client.post(
        "/api/v1/auth/users", json={"customer_id": "c001", "username": "alice", "password": "alicepass123"}
    )

    response = admin_client.post(
        "/api/v1/auth/users", json={"customer_id": "c001", "username": "alice2", "password": "alicepass123"}
    )

    assert response.status_code == 409


def test_create_login_unknown_customer_returns_400(admin_client):
    response = admin_client.post(
        "/api/v1/auth/users", json={"customer_id": "does-not-exist", "username": "alice", "password": "alicepass123"}
    )

    assert response.status_code == 400


def test_create_login_requires_admin(admin_client, customer_client_for):
    admin_client.post("/api/v1/customers", json={"id": "c001", "name": "Alice"})
    admin_client.post("/api/v1/customers", json={"id": "c002", "name": "Bob"})
    alice_client = customer_client_for("c001")

    response = alice_client.post(
        "/api/v1/auth/users", json={"customer_id": "c002", "username": "bob", "password": "bobpass123"}
    )

    assert response.status_code == 403
