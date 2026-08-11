import pytest

from app.services.bank import Bank
from app.models.customer import Customer
from app.models.account import Account


@pytest.fixture
def bank():
    return Bank("Test Bank")


def test_bank_name(bank):
    assert bank.name == "Test Bank"


def test_add_and_get_customer(bank):
    c = Customer("c1", "Alice")
    bank.add_customer(c)
    assert bank.get_customer("c1") is c


def test_add_duplicate_customer_raises(bank):
    c1 = Customer("c1", "Alice")
    c2 = Customer("c1", "Bob")
    bank.add_customer(c1)
    with pytest.raises(ValueError):
        bank.add_customer(c2)


def test_get_missing_customer_returns_none(bank):
    assert bank.get_customer("nope") is None


def test_get_customers_returns_all(bank):
    c1 = Customer("c1", "Alice")
    c2 = Customer("c2", "Bob")
    bank.add_customer(c1)
    bank.add_customer(c2)
    assert set(bank.get_customers()) == {c1, c2}


def test_add_account_with_customer_object_owner(bank):
    c = Customer("c1", "Alice")
    bank.add_customer(c)
    a = Account("a1", c, 100.0)
    bank.add_account(a)
    assert bank.get_account("a1") is a
    assert a in c.get_accounts()


def test_add_account_auto_registers_unknown_customer(bank):
    c = Customer("c1", "Alice")
    a = Account("a1", c, 100.0)
    bank.add_account(a)
    assert bank.get_customer("c1") is c


def test_add_account_with_string_owner_resolves_customer(bank):
    c = Customer("c1", "Alice")
    bank.add_customer(c)
    a = Account("a1", "c1", 100.0)
    bank.add_account(a)
    assert a.owner is c
    assert bank.get_account("a1") is a


def test_add_account_with_unknown_string_owner_raises(bank):
    a = Account("a1", "does-not-exist", 100.0)
    with pytest.raises(ValueError):
        bank.add_account(a)


def test_add_account_with_invalid_owner_type_raises(bank):
    a = Account("a1", 12345, 100.0)
    with pytest.raises(ValueError):
        bank.add_account(a)


def test_add_duplicate_account_raises(bank):
    c = Customer("c1", "Alice")
    bank.add_customer(c)
    a1 = Account("a1", c, 100.0)
    a2 = Account("a1", c, 50.0)
    bank.add_account(a1)
    with pytest.raises(ValueError):
        bank.add_account(a2)


def test_get_missing_account_returns_none(bank):
    assert bank.get_account("nope") is None


def test_find_accounts_by_customer(bank):
    c = Customer("c1", "Alice")
    bank.add_customer(c)
    a1 = Account("a1", c, 100.0)
    a2 = Account("a2", c, 50.0)
    bank.add_account(a1)
    bank.add_account(a2)
    assert set(bank.find_accounts_by_customer("c1")) == {a1, a2}


def test_find_accounts_by_missing_customer_returns_empty(bank):
    assert bank.find_accounts_by_customer("nope") == []


def test_remove_account(bank):
    c = Customer("c1", "Alice")
    bank.add_customer(c)
    a = Account("a1", c, 100.0)
    bank.add_account(a)
    bank.remove_account("a1")
    assert bank.get_account("a1") is None
    assert a not in c.get_accounts()


def test_remove_missing_account_is_noop(bank):
    bank.remove_account("nope")


def test_remove_customer_also_removes_their_accounts(bank):
    c = Customer("c1", "Alice")
    bank.add_customer(c)
    a1 = Account("a1", c, 100.0)
    a2 = Account("a2", c, 50.0)
    bank.add_account(a1)
    bank.add_account(a2)
    bank.remove_customer("c1")
    assert bank.get_customer("c1") is None
    assert bank.get_account("a1") is None
    assert bank.get_account("a2") is None


def test_remove_missing_customer_is_noop(bank):
    bank.remove_customer("nope")


def test_str(bank):
    c = Customer("c1", "Alice")
    bank.add_customer(c)
    bank.add_account(Account("a1", c, 100.0))
    assert str(bank) == "Bank(name=Test Bank, customers=1, accounts=1)"
