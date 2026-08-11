from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Numeric
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class CustomerRow(Base):
    __tablename__ = "customers"

    id: Mapped[str] = mapped_column(primary_key=True)
    name: Mapped[str]
    email: Mapped[str | None]


class AccountRow(Base):
    __tablename__ = "accounts"

    id: Mapped[str] = mapped_column(primary_key=True)
    owner_id: Mapped[str] = mapped_column(ForeignKey("customers.id"))
    branch_id: Mapped[str]
    balance: Mapped[float] = mapped_column(Numeric)


class TransactionRow(Base):
    __tablename__ = "transactions"

    id: Mapped[str] = mapped_column(primary_key=True)
    from_account_id: Mapped[str]
    to_account_id: Mapped[str]
    amount: Mapped[float] = mapped_column(Numeric)
    type: Mapped[str]
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True))
