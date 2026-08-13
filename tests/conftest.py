from __future__ import annotations

import os
from pathlib import Path

import pytest
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url

load_dotenv()

TEST_DB_NAME = "bankapp_pytest"

_real_url = make_url(os.environ["DATABASE_URL"])
_test_url = _real_url.set(database=TEST_DB_NAME)
_maintenance_url = _real_url.set(database="postgres")

TEST_DATABASE_URL = _test_url.render_as_string(hide_password=False)
MAINTENANCE_DATABASE_URL = _maintenance_url.render_as_string(hide_password=False)

# Must happen before anything imports app.services.db, so its lazy
# get_engine() picks up the throwaway test database instead of the real one.
os.environ["DATABASE_URL"] = TEST_DATABASE_URL

REPO_ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture(scope="session", autouse=True)
def build_test_database():
    """Create bankapp_pytest fresh, migrate it to head, drop it when the session ends."""
    admin_engine = create_engine(MAINTENANCE_DATABASE_URL, isolation_level="AUTOCOMMIT")
    with admin_engine.connect() as conn:
        conn.execute(text(f'DROP DATABASE IF EXISTS "{TEST_DB_NAME}" WITH (FORCE)'))
        conn.execute(text(f'CREATE DATABASE "{TEST_DB_NAME}"'))
    admin_engine.dispose()

    from alembic import command
    from alembic.config import Config

    cfg = Config(str(REPO_ROOT / "alembic.ini"))
    cfg.set_main_option("sqlalchemy.url", TEST_DATABASE_URL)
    command.upgrade(cfg, "head")

    yield

    from app.services import db as db_module

    db_module.get_engine().dispose()

    admin_engine = create_engine(MAINTENANCE_DATABASE_URL, isolation_level="AUTOCOMMIT")
    with admin_engine.connect() as conn:
        conn.execute(text(f'DROP DATABASE IF EXISTS "{TEST_DB_NAME}" WITH (FORCE)'))
    admin_engine.dispose()


@pytest.fixture(autouse=True)
def reset_database(build_test_database):
    """Blank slate before every test: empty tables, sequences restarted at 1."""
    from app.services.db import get_session

    with get_session() as session:
        session.execute(text("TRUNCATE customers, accounts, transactions, users"))
        session.execute(text("ALTER SEQUENCE customer_id_seq RESTART WITH 1"))
        session.execute(text("ALTER SEQUENCE account_id_seq RESTART WITH 1"))
        session.execute(text("ALTER SEQUENCE user_id_seq RESTART WITH 1"))
        session.commit()


@pytest.fixture
def client():
    from fastapi.testclient import TestClient

    from app.main import app

    return TestClient(app)


def _create_user(username: str, password: str, role: str, customer_id: str | None) -> None:
    from app.models.orm import UserRow
    from app.services.auth import hash_password
    from app.services.db import get_session
    from app.services.ids import insert_with_id

    with get_session() as session:
        insert_with_id(
            session,
            UserRow,
            "u",
            None,
            {"username": username, "password_hash": hash_password(password), "role": role, "customer_id": customer_id},
            "Username already taken",
        )
        session.commit()


@pytest.fixture
def admin_user():
    """Insert an admin login directly (there's no HTTP way to create one)."""
    username, password = "admin", "adminpass123"
    _create_user(username, password, "admin", None)
    return {"username": username, "password": password}


@pytest.fixture
def admin_token(client, admin_user):
    response = client.post("/api/v1/auth/login", json=admin_user)
    return response.json()["access_token"]


@pytest.fixture
def admin_headers(admin_token):
    return {"Authorization": f"Bearer {admin_token}"}


@pytest.fixture
def admin_client(client, admin_headers):
    client.headers.update(admin_headers)
    return client


@pytest.fixture
def customer_client_for(client, admin_headers):
    """Factory: given an existing customer id, create a login for them and return a client authenticated as them."""

    def _make(customer_id: str, username: str | None = None, password: str = "customerpass123"):
        from fastapi.testclient import TestClient

        from app.main import app

        username = username or f"user_{customer_id}"
        create_response = client.post(
            "/api/v1/auth/users",
            json={"customer_id": customer_id, "username": username, "password": password},
            headers=admin_headers,
        )
        assert create_response.status_code == 201, create_response.text

        login_response = client.post("/api/v1/auth/login", json={"username": username, "password": password})
        token = login_response.json()["access_token"]

        customer_client = TestClient(app)
        customer_client.headers.update({"Authorization": f"Bearer {token}"})
        return customer_client

    return _make
