from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from dotenv import load_dotenv

from app.models.orm import UserRow

load_dotenv()

ALGORITHM = "HS256"


def _get_secret_key() -> str:
    key = os.environ.get("JWT_SECRET_KEY")
    if not key:
        raise RuntimeError(
            "JWT_SECRET_KEY is not set. Copy .env.example to .env and fill in a secret key."
        )
    return key


def _get_expire_minutes() -> int:
    return int(os.environ.get("JWT_EXPIRE_MINUTES", "120"))


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(password.encode(), password_hash.encode())


def create_access_token(user: UserRow) -> str:
    claims = {
        "sub": user.id,
        "role": user.role,
        "customer_id": user.customer_id,
        "iat": datetime.now(timezone.utc),
        "exp": datetime.now(timezone.utc) + timedelta(minutes=_get_expire_minutes()),
    }
    return jwt.encode(claims, _get_secret_key(), algorithm=ALGORITHM)


def decode_access_token(token: str) -> dict:
    return jwt.decode(token, _get_secret_key(), algorithms=[ALGORITHM])
