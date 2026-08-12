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
        session.execute(text("TRUNCATE customers, accounts, transactions"))
        session.execute(text("ALTER SEQUENCE customer_id_seq RESTART WITH 1"))
        session.execute(text("ALTER SEQUENCE account_id_seq RESTART WITH 1"))
        session.commit()


@pytest.fixture
def client():
    from fastapi.testclient import TestClient

    from app.main import app

    return TestClient(app)
