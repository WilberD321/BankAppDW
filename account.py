from __future__ import annotations
from typing import Union, TYPE_CHECKING

if TYPE_CHECKING:
    from customer import Customer


class Account:
    """Simple Account class with encapsulation, properties and operator overloading.

    Attributes:
        _id: account identifier (str)
        _owner: Customer or str (customer id)
        _balance: float
    """

    def __init__(self, account_id: str, owner: 'Customer | str', balance: float = 0.0):
        self._id = str(account_id)
        self._owner: 'Customer | str' = owner
        self._balance = float(balance)

    @classmethod
    def from_owner_name(cls, account_id: str, owner_name: str, balance: float = 0.0):
        return cls(account_id, owner_name, balance)

    @property
    def id(self) -> str:
        return self._id

    @property
    def owner(self) -> 'Customer | str':
        return self._owner

    @owner.setter
    def owner(self, value: 'Customer | str') -> None:
        self._owner = value

    @property
    def balance(self) -> float:
        return self._balance

    def deposit(self, amount: float) -> None:
        if amount <= 0:
            raise ValueError("Deposit amount must be positive")
        self._balance += float(amount)

    def withdraw(self, amount: float) -> None:
        if amount <= 0:
            raise ValueError("Withdraw amount must be positive")
        if amount > self._balance:
            raise ValueError("Insufficient funds")
        self._balance -= float(amount)

    def __str__(self) -> str:
        owner_repr = self._owner.id if hasattr(self._owner, 'id') else self._owner
        return f"Account(id={self._id}, owner={owner_repr}, balance={self._balance:.2f})"

    def __repr__(self) -> str:
        return f"Account({self._id!r}, {self._owner!r}, {self._balance!r})"

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Account) and self._id == other._id

    def __add__(self, other: Union['Account', float, int]) -> float:
        """Support adding two accounts (sum balances) or adding a numeric amount to balance."""
        if isinstance(other, Account):
            return self._balance + other._balance
        if isinstance(other, (int, float)):
            return self._balance + float(other)
        return NotImplemented

