import builtins

import pytest

from app import cli
from app.services.bank import Bank
from app.models.customer import Customer
from app.models.account import Account


def _feed_inputs(monkeypatch, values):
    it = iter(values)
    monkeypatch.setattr(builtins, "input", lambda *_args: next(it))


def test_prompt_strips_whitespace(monkeypatch):
    _feed_inputs(monkeypatch, ["  hello  "])
    assert cli.prompt("prompt: ") == "hello"


def test_prompt_nonempty_reprompts_until_value_given(monkeypatch, capsys):
    _feed_inputs(monkeypatch, ["", "   ", "value"])
    assert cli.prompt_nonempty("prompt: ") == "value"
    out = capsys.readouterr().out
    assert out.count("Please enter a value.") == 2


def test_prompt_float_reprompts_on_invalid_input(monkeypatch, capsys):
    _feed_inputs(monkeypatch, ["abc", "12.5"])
    assert cli.prompt_float("prompt: ") == 12.5
    out = capsys.readouterr().out
    assert "Enter a valid number." in out


def test_list_customers_empty(capsys):
    bank = Bank("Test Bank")
    cli.list_customers(bank)
    out = capsys.readouterr().out
    assert "(none)" in out


def test_list_customers_with_entries(capsys):
    bank = Bank("Test Bank")
    bank.add_customer(Customer("c1", "Alice", "alice@example.com"))
    cli.list_customers(bank)
    out = capsys.readouterr().out
    assert "c1: Alice <alice@example.com>" in out


def test_list_accounts_empty(capsys):
    c = Customer("c1", "Alice")
    cli.list_accounts(c)
    out = capsys.readouterr().out
    assert "(none)" in out


def test_list_accounts_with_entries(capsys):
    c = Customer("c1", "Alice")
    c.add_account(Account("a1", c, 100.0))
    cli.list_accounts(c)
    out = capsys.readouterr().out
    assert "a1: balance=100.00" in out


def test_demo_runs_without_error(capsys):
    cli.demo()
    out = capsys.readouterr().out
    assert "Running demo..." in out
    assert "Bank(name=Demo Bank CLI, customers=1, accounts=1)" in out


def test_main_with_demo_flag_runs_demo(capsys):
    cli.main(["--demo"])
    out = capsys.readouterr().out
    assert "Running demo..." in out


def test_main_menu_create_and_list_customer_then_exit(monkeypatch, capsys):
    bank = Bank("Test Bank")
    _feed_inputs(
        monkeypatch,
        [
            "1", "c1", "Alice", "alice@example.com",  # create customer
            "4",  # list customers
            "5",  # exit
        ],
    )
    cli.main_menu(bank)
    out = capsys.readouterr().out
    assert "Customer created." in out
    assert "c1: Alice <alice@example.com>" in out
    assert "Goodbye." in out


def test_account_menu_deposit_and_withdraw(monkeypatch, capsys):
    bank = Bank("Test Bank")
    c = Customer("c1", "Alice")
    bank.add_customer(c)
    _feed_inputs(
        monkeypatch,
        [
            "1", "a1", "100",       # create account with balance 100
            "2", "a1",              # select account a1
            "1", "50",              # deposit 50
            "2", "1000",            # withdraw too much -> error
            "3",                    # back from account_actions
            "4",                    # back to customers
        ],
    )
    cli.account_menu(bank, c)
    out = capsys.readouterr().out
    assert "Account added." in out
    assert "Deposited." in out
    assert "Error:" in out
    assert bank.get_account("a1").balance == 150.0
