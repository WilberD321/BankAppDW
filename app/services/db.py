from __future__ import annotations

import os

from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database

load_dotenv()

DATABASE_NAME = "bankApp"

_client: MongoClient | None = None


def get_client() -> MongoClient:
    global _client
    if _client is None:
        uri = os.environ.get("MONGODB_URI")
        if not uri:
            raise RuntimeError(
                "MONGODB_URI is not set. Copy .env.example to .env and fill in your "
                "MongoDB Atlas connection string."
            )
        _client = MongoClient(uri, tz_aware=True)
    return _client


def get_db() -> Database:
    return get_client()[DATABASE_NAME]


def customers_collection() -> Collection:
    return get_db()["customers"]


def accounts_collection() -> Collection:
    return get_db()["accounts"]


def transactions_collection() -> Collection:
    return get_db()["transactions"]
