"""One-time script to bootstrap the first admin login. Run locally: python scripts/create_admin.py"""
from __future__ import annotations

import getpass
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.models.orm import UserRow
from app.services.auth import hash_password
from app.services.db import get_session
from app.services.ids import insert_with_id


def main() -> None:
    username = input("Admin username: ").strip()
    password = getpass.getpass("Admin password: ")
    confirm = getpass.getpass("Confirm password: ")
    if password != confirm:
        print("Passwords do not match.")
        raise SystemExit(1)

    with get_session() as session:
        row = insert_with_id(
            session,
            UserRow,
            "u",
            None,
            {"username": username, "password_hash": hash_password(password), "role": "admin", "customer_id": None},
            "Username already taken",
        )
        session.commit()
        print(f"Created admin user '{row.username}' ({row.id}).")


if __name__ == "__main__":
    main()
