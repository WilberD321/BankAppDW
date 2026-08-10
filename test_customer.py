import pytest

from customer import Customer
from account import Account


def test_create_customer():
    c = Customer("c1", "Alice", "alice@example.com")
    assert c.id == "c1"
    assert c.name == "Alice"
    assert c.email == "alice@example.com"


def test_create_customer_without_email():
    c = Customer("c1", "Alice")
    assert c.email is None


def test_from_dict_with_id_key():
    c = Customer.from_dict({"id": "c1", "name": "Alice", "email": "a@example.com"})
    assert c.id == "c1"
    assert c.name == "Alice"
    assert c.email == "a@example.com"


def test_from_dict_with_customer_id_key():
    c = Customer.from_dict({"customer_id": "c1", "name": "Alice"})
    assert c.id == "c1"


def test_name_setter():
    c = Customer("c1", "Alice")
    c.name = "Alicia"
    assert c.name == "Alicia"


def test_email_setter():
    c = Customer("c1", "Alice")
    c.email = "new@example.com"
    assert c.email == "new@example.com"


def test_add_account_sets_owner_and_registers():
    c = Customer("c1", "Alice")
    a = Account("a1", "c1", 100.0)
    c.add_account(a)
    assert a.owner is c
    assert c.get_accounts() == [a]


def test_add_duplicate_account_raises():
    c = Customer("c1", "Alice")
    a1 = Account("a1", "c1", 100.0)
    a2 = Account("a1", "c1", 50.0)
    c.add_account(a1)
    with pytest.raises(ValueError):
        c.add_account(a2)


def test_remove_account():
    c = Customer("c1", "Alice")
    a = Account("a1", "c1", 100.0)
    c.add_account(a)
    c.remove_account("a1")
    assert c.get_accounts() == []


def test_remove_missing_account_is_noop():
    c = Customer("c1", "Alice")
    c.remove_account("does-not-exist")
    assert c.get_accounts() == []


def test_get_accounts_returns_copy():
    c = Customer("c1", "Alice")
    a = Account("a1", "c1", 100.0)
    c.add_account(a)
    accounts = c.get_accounts()
    accounts.clear()
    assert c.get_accounts() == [a]


def test_equality_based_on_id():
    c1 = Customer("c1", "Alice")
    c2 = Customer("c1", "Someone Else")
    c3 = Customer("c2", "Alice")
    assert c1 == c2
    assert c1 != c3
    assert c1 != "not a customer"


def test_hashable_and_usable_in_set():
    c1 = Customer("c1", "Alice")
    c2 = Customer("c1", "Someone Else")
    assert hash(c1) == hash(c2)
    assert {c1, c2} == {c1}


def test_str_and_repr():
    c = Customer("c1", "Alice", "a@example.com")
    assert str(c) == "Customer(id=c1, name=Alice, email=a@example.com)"
    assert repr(c) == "Customer('c1', 'Alice', 'a@example.com')"
