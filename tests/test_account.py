import pytest

from account import Account
from customer import Customer


def test_create_account_with_customer_owner():
    c = Customer("c1", "Alice")
    a = Account("a1", c, 100.0)
    assert a.id == "a1"
    assert a.owner is c
    assert a.balance == 100.0


def test_create_account_defaults_to_zero_balance():
    a = Account("a1", "c1")
    assert a.balance == 0.0


def test_negative_initial_balance_raises():
    with pytest.raises(ValueError):
        Account("a1", "c1", -50.0)


def test_from_owner_name_stores_string_owner():
    a = Account.from_owner_name("a1", "c1", 10.0)
    assert a.owner == "c1"


def test_deposit_increases_balance():
    a = Account("a1", "c1", 100.0)
    a.deposit(50)
    assert a.balance == 150.0


@pytest.mark.parametrize("amount", [0, -10])
def test_deposit_nonpositive_amount_raises(amount):
    a = Account("a1", "c1", 100.0)
    with pytest.raises(ValueError):
        a.deposit(amount)


def test_withdraw_decreases_balance():
    a = Account("a1", "c1", 100.0)
    a.withdraw(40)
    assert a.balance == 60.0


@pytest.mark.parametrize("amount", [0, -10])
def test_withdraw_nonpositive_amount_raises(amount):
    a = Account("a1", "c1", 100.0)
    with pytest.raises(ValueError):
        a.withdraw(amount)


def test_withdraw_more_than_balance_raises():
    a = Account("a1", "c1", 100.0)
    with pytest.raises(ValueError):
        a.withdraw(150.0)


def test_owner_setter():
    a = Account("a1", "c1", 100.0)
    c = Customer("c1", "Alice")
    a.owner = c
    assert a.owner is c


def test_equality_based_on_id():
    a1 = Account("a1", "c1", 100.0)
    a2 = Account("a1", "c2", 999.0)
    a3 = Account("a2", "c1", 100.0)
    assert a1 == a2
    assert a1 != a3
    assert a1 != "not an account"


def test_hashable_and_usable_in_set():
    a1 = Account("a1", "c1", 100.0)
    a2 = Account("a1", "c2", 999.0)
    assert hash(a1) == hash(a2)
    assert {a1, a2} == {a1}


def test_add_two_accounts_sums_balances():
    a1 = Account("a1", "c1", 100.0)
    a2 = Account("a2", "c2", 50.0)
    assert a1 + a2 == 150.0


def test_add_numeric_amount():
    a1 = Account("a1", "c1", 100.0)
    assert a1 + 25 == 125.0
    assert a1 + 25.5 == 125.5


def test_add_unsupported_type_returns_not_implemented():
    a1 = Account("a1", "c1", 100.0)
    assert a1.__add__("nope") is NotImplemented


def test_str_with_customer_owner_shows_customer_id():
    c = Customer("c1", "Alice")
    a = Account("a1", c, 100.0)
    assert str(a) == "Account(id=a1, owner=c1, balance=100.00)"


def test_str_with_string_owner_shows_string():
    a = Account("a1", "c1", 100.0)
    assert str(a) == "Account(id=a1, owner=c1, balance=100.00)"


def test_repr():
    a = Account("a1", "c1", 100.0)
    assert repr(a) == "Account('a1', 'c1', 100.0)"
