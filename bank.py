from __future__ import annotations
from typing import Dict, List

from customer import Customer
from account import Account


class Bank:
    """Simple Bank class managing customers and accounts."""

    def __init__(self, name: str):
        self._name = str(name)
        self._customers: Dict[str, Customer] = {}
        self._accounts: Dict[str, Account] = {}

    @property
    def name(self) -> str:
        return self._name

    def add_customer(self, customer: Customer) -> None:
        if customer.id in self._customers:
            raise ValueError("Customer already exists")
        self._customers[customer.id] = customer

    def get_customer(self, customer_id: str) -> Customer | None:
        return self._customers.get(customer_id)

    def get_customers(self) -> List[Customer]:
        return list(self._customers.values())

    def add_account(self, account: Account) -> None:
        if account.id in self._accounts:
            raise ValueError("Account already exists")
        # Resolve owner: if it's a customer id string, find the customer
        owner = account.owner
        if isinstance(owner, str):
            cust = self.get_customer(owner)
            if cust is None:
                raise ValueError("Owner customer id not found: %s" % owner)
        elif isinstance(owner, Customer):
            cust = owner
            if cust.id not in self._customers:
                # register the customer automatically
                self.add_customer(cust)
        else:
            raise ValueError("Account owner must be Customer or customer id string")

        # attach to customer and to bank registry
        cust.add_account(account)
        self._accounts[account.id] = account

    def get_account(self, account_id: str) -> Account | None:
        return self._accounts.get(account_id)

    def find_accounts_by_customer(self, customer_id: str) -> List[Account]:
        cust = self.get_customer(customer_id)
        if cust is None:
            return []
        return cust.get_accounts()

    def remove_account(self, account_id: str) -> None:
        acc = self._accounts.pop(account_id, None)
        if acc and isinstance(acc.owner, Customer):
            acc.owner.remove_account(account_id)

    def remove_customer(self, customer_id: str) -> None:
        # remove customer and their accounts
        cust = self._customers.pop(customer_id, None)
        if not cust:
            return
        for acc in cust.get_accounts():
            self._accounts.pop(acc.id, None)

    def __str__(self) -> str:
        return f"Bank(name={self._name}, customers={len(self._customers)}, accounts={len(self._accounts)})"


if __name__ == "__main__":
    # Quick example usage
    c = Customer("c001", "Alice", "alice@example.com")
    a1 = Account("a100", c, 150.0)
    a2 = Account.from_owner_name("a101", "c001", 200.0)

    bank = Bank("Demo Bank")
    bank.add_customer(c)
    bank.add_account(a1)
    bank.add_account(a2)

    a1.deposit(50)
    try:
        a1.withdraw(300)
    except ValueError:
        pass

    print(bank)
    print(bank.find_accounts_by_customer("c001"))
