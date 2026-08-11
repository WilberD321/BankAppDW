from __future__ import annotations
import sys
from typing import Optional

from app.services.bank import Bank
from app.models.customer import Customer
from app.models.account import Account


def prompt(text: str) -> str:
    return input(text).strip()


def prompt_nonempty(text: str) -> str:
    while True:
        v = prompt(text)
        if v:
            return v
        print("Please enter a value.")


def prompt_float(text: str) -> float:
    while True:
        v = prompt(text)
        try:
            return float(v)
        except ValueError:
            print("Enter a valid number.")


def list_customers(bank: Bank) -> None:
    print("Customers:")
    customers = bank.get_customers()
    if not customers:
        print("  (none)")
        return
    for cust in customers:
        print(f"  {cust.id}: {cust.name} <{cust.email}>")


def list_accounts(cust: Customer) -> None:
    accts = cust.get_accounts()
    print(f"Accounts for {cust.name}:")
    if not accts:
        print("  (none)")
        return
    for a in accts:
        print(f"  {a.id}: balance={a.balance:.2f}")


def account_menu(bank: Bank, cust: Customer) -> None:
    while True:
        list_accounts(cust)
        print("\nAccount options:\n  1) Create account\n  2) Select account\n  3) Delete account\n  4) Back to customers")
        choice = prompt("Choose: ")
        if choice == '1':
            aid = prompt_nonempty("Account id: ")
            bal = prompt_float("Initial balance: ")
            a = Account(aid, cust, bal)
            try:
                bank.add_account(a)
                print("Account added.")
            except ValueError as e:
                print("Error:", e)
        elif choice == '2':
            aid = prompt_nonempty("Account id to select: ")
            a = bank.get_account(aid)
            if not a or (hasattr(a.owner, 'id') and a.owner.id != cust.id):
                print("Account not found for this customer.")
            else:
                account_actions(a)
        elif choice == '3':
            aid = prompt_nonempty("Account id to delete: ")
            a = bank.get_account(aid)
            if not a or (hasattr(a.owner, 'id') and a.owner.id != cust.id):
                print("Account not found for this customer.")
            else:
                bank.remove_account(aid)
                print("Account removed.")
        elif choice == '4':
            return
        else:
            print("Invalid choice")


def account_actions(a: Account) -> None:
    while True:
        print(f"\nSelected {a}")
        print("  1) Deposit\n  2) Withdraw\n  3) Back")
        choice = prompt("Choose: ")
        if choice == '1':
            amt = prompt_float("Amount to deposit: ")
            try:
                a.deposit(amt)
                print("Deposited.")
            except ValueError as e:
                print("Error:", e)
        elif choice == '2':
            amt = prompt_float("Amount to withdraw: ")
            try:
                a.withdraw(amt)
                print("Withdrawn.")
            except ValueError as e:
                print("Error:", e)
        elif choice == '3':
            return
        else:
            print("Invalid choice")


def main_menu(bank: Bank) -> None:
    while True:
        print("\nMain menu:\n  1) Create customer\n  2) Select customer\n  3) Delete customer\n  4) List customers\n  5) Exit")
        choice = prompt("Choose: ")
        if choice == '1':
            cid = prompt_nonempty("Customer id: ")
            name = prompt_nonempty("Name: ")
            email = prompt("Email (optional): ") or None
            try:
                c = Customer(cid, name, email)
                bank.add_customer(c)
                print("Customer created.")
            except ValueError as e:
                print("Error:", e)
        elif choice == '2':
            cid = prompt_nonempty("Customer id to select: ")
            c = bank.get_customer(cid)
            if not c:
                print("Customer not found.")
            else:
                account_menu(bank, c)
        elif choice == '3':
            cid = prompt_nonempty("Customer id to delete: ")
            if bank.get_customer(cid) is None:
                print("Customer not found.")
            else:
                bank.remove_customer(cid)
                print("Customer removed.")
        elif choice == '4':
            list_customers(bank)
        elif choice == '5':
            print("Goodbye.")
            return
        else:
            print("Invalid choice")


def demo() -> None:
    bank = Bank("Demo Bank CLI")
    print("Running demo...")
    c = Customer("demo1", "Demo User", "demo@example.com")
    bank.add_customer(c)
    a = Account("demoA", c, 100.0)
    bank.add_account(a)
    a.deposit(25.0)
    try:
        a.withdraw(50.0)
    except ValueError:
        pass
    print(bank)
    print(c.get_accounts())


def main(argv: Optional[list[str]] = None) -> None:
    argv = argv if argv is not None else sys.argv[1:]
    bank = Bank("My Bank")
    if '--demo' in argv:
        demo()
        return
    print("Welcome to the Bank CLI")
    main_menu(bank)


if __name__ == '__main__':
    main()
