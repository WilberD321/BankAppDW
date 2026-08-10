from __future__ import annotations
from typing import Dict, List, TYPE_CHECKING

if TYPE_CHECKING:
    from account import Account


class Customer:
    """Customer with encapsulated fields and owns accounts."""

    def __init__(self, customer_id: str, name: str, email: str | None = None):
        self._id = str(customer_id)
        self._name = str(name)
        self._email = email
        self._accounts: Dict[str, 'Account'] = {}

    @classmethod
    def from_dict(cls, data: dict) -> 'Customer':
        return cls(data.get('id') or data.get('customer_id'), data.get('name'), data.get('email'))

    @property
    def id(self) -> str:
        return self._id

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        self._name = str(value)

    @property
    def email(self) -> str | None:
        return self._email

    @email.setter
    def email(self, value: str | None) -> None:
        self._email = value

    def add_account(self, account: 'Account') -> None:
        if account.id in self._accounts:
            raise ValueError("Account already added to customer")
        # set the account owner to this customer
        account.owner = self
        self._accounts[account.id] = account

    def remove_account(self, account_id: str) -> None:
        self._accounts.pop(account_id, None)

    def get_accounts(self) -> List['Account']:
        return list(self._accounts.values())

    def __str__(self) -> str:
        return f"Customer(id={self._id}, name={self._name}, email={self._email})"

    def __repr__(self) -> str:
        return f"Customer({self._id!r}, {self._name!r}, {self._email!r})"

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Customer) and self._id == other._id

