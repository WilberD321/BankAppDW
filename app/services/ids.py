from __future__ import annotations

from typing import Type, TypeVar

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.orm import Base

ModelT = TypeVar("ModelT", bound=Base)


def next_id(session: Session, model: Type[ModelT], prefix: str) -> str:
    """Scan for the highest existing '{prefix}NNN' id and return the next one, e.g. c001 -> c002."""
    max_num = 0
    for (row_id,) in session.execute(select(model.id).where(model.id.like(f"{prefix}%"))):
        suffix = row_id[len(prefix):]
        if suffix.isdigit():
            max_num = max(max_num, int(suffix))
    return f"{prefix}{max_num + 1:03d}"


def insert_with_id(
    session: Session, model: Type[ModelT], prefix: str, explicit_id: str | None, fields: dict, conflict_detail: str
) -> ModelT:
    if explicit_id:
        row = model(id=explicit_id, **fields)
        session.add(row)
        try:
            session.flush()
        except IntegrityError as exc:
            session.rollback()
            raise HTTPException(status_code=409, detail=conflict_detail) from exc
        return row

    # No id given: generate the next one in sequence. Retry a few times in case
    # of a race with another request generating the same id concurrently.
    for _ in range(5):
        row = model(id=next_id(session, model, prefix), **fields)
        session.add(row)
        try:
            session.flush()
            return row
        except IntegrityError:
            session.rollback()
            continue
    raise HTTPException(status_code=500, detail="Failed to generate a unique id, please try again")
