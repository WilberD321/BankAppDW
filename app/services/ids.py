from __future__ import annotations

from fastapi import HTTPException
from pymongo.collection import Collection
from pymongo.errors import DuplicateKeyError


def next_id(collection: Collection, prefix: str) -> str:
    """Scan for the highest existing '{prefix}NNN' id and return the next one, e.g. c001 -> c002."""
    max_num = 0
    for doc in collection.find({"_id": {"$regex": f"^{prefix}\\d+$"}}, {"_id": 1}):
        max_num = max(max_num, int(doc["_id"][len(prefix):]))
    return f"{prefix}{max_num + 1:03d}"


def insert_with_id(
    collection: Collection, prefix: str, explicit_id: str | None, fields: dict, conflict_detail: str
) -> dict:
    if explicit_id:
        doc = {"_id": explicit_id, **fields}
        try:
            collection.insert_one(doc)
        except DuplicateKeyError as exc:
            raise HTTPException(status_code=409, detail=conflict_detail) from exc
        return doc

    # No id given: generate the next one in sequence. Retry a few times in case
    # of a race with another request generating the same id concurrently.
    for _ in range(5):
        doc = {"_id": next_id(collection, prefix), **fields}
        try:
            collection.insert_one(doc)
            return doc
        except DuplicateKeyError:
            continue
    raise HTTPException(status_code=500, detail="Failed to generate a unique id, please try again")
