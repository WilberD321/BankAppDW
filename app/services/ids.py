from __future__ import annotations

from typing import Type, TypeVar

from fastapi import HTTPException
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.orm import Base

ModelT = TypeVar("ModelT", bound=Base)

# One Postgres SEQUENCE per id prefix (see alembic/versions/4cedf3848236_id_sequences.py).
# nextval() is atomic at the DB level, so no scan-and-retry loop is needed here anymore.
_SEQUENCES = {
    "c": "customer_id_seq",
    "a": "account_id_seq",
    "u": "user_id_seq",
}


def next_id(session: Session, prefix: str) -> str:
    """Atomically claim the next '{prefix}NNN' id from that prefix's DB sequence, e.g. c001 -> c002."""
    seq = _SEQUENCES[prefix]
    n = session.execute(text(f"SELECT nextval('{seq}')")).scalar_one()
    return f"{prefix}{n:03d}"


def _bump_sequence_past(session: Session, prefix: str, explicit_id: str) -> None:
    """If a manually-supplied id is ahead of the sequence, fast-forward the sequence past it.

    Without this, an out-of-sequence manual id (e.g. c050 while the sequence is only at c010)
    would leave the sequence generating ids that collide with it on every auto-create until
    the sequence catches back up.
    """
    suffix = explicit_id[len(prefix):]
    if not suffix.isdigit():
        return
    seq = _SEQUENCES[prefix]
    session.execute(
        text(f"SELECT setval('{seq}', GREATEST(:n, (SELECT last_value FROM {seq})))"),
        {"n": int(suffix)},
    )


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
        _bump_sequence_past(session, prefix, explicit_id)
        return row

    row = model(id=next_id(session, prefix), **fields)
    session.add(row)
    try:
        session.flush()
    except IntegrityError as exc:
        session.rollback()
        raise HTTPException(status_code=500, detail="Failed to generate a unique id, please try again") from exc
    return row
