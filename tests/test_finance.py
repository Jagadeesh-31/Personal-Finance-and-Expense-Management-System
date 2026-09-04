import pytest
import os
from finance import Transaction, Income, Expense, FinanceManager


def test_transaction_init():
    t = Transaction(100.0, "General", "Test Transaction")
    assert t.amount == 100.0
    assert t.category == "General"
    assert t.description == "Test Transaction"
    assert len(t.date) == 10  # YYYY-MM-DD format check


def test_income_init():
    inc = Income(2500.0, "Salary", "Paycheck", "Employer")
    assert inc.amount == 2500.0
    assert inc.category == "Salary"
    assert inc.description == "Paycheck"
    assert inc.source == "Employer"


def test_expense_init():
    exp = Expense(150.0, "Food", "Lunch", "UPI")
    assert exp.amount == 150.0
    assert exp.category == "Food"
    assert exp.description == "Lunch"
    assert exp.payment == "UPI"


def test_finance_manager_create_files(temp_data_dir):
    manager = FinanceManager()
    assert os.path.exists("data/income.csv")
    assert os.path.exists("data/expenses.csv")
    assert os.path.exists("data/transactions.csv")
    assert os.path.exists("data/budgets.csv")


def test_set_monthly_budget_valid(clean_manager):
    clean_manager.set_monthly_budget("2026-09", 10000.0)
    assert clean_manager.budget == 10000.0
    assert clean_manager.budgets.get("2026-09") == 10000.0


def test_set_monthly_budget_invalid(clean_manager):
    with pytest.raises(ValueError, match="Budget must be greater than zero"):
        clean_manager.set_monthly_budget("2026-09", 0.0)

    with pytest.raises(ValueError, match="Budget must be greater than zero"):
        clean_manager.set_monthly_budget("2026-09", -500.0)


def test_monthly_income_and_expense(populated_manager):
    assert populated_manager.monthly_income("2026-09") == 4500.0
    assert populated_manager.monthly_expense("2026-09") == 2000.0
    assert populated_manager.monthly_savings_value("2026-09") == 2500.0


def test_total_income_and_expense(populated_manager):
    assert populated_manager.total_income() == 4500.0
    assert populated_manager.total_expense() == 2000.0


def test_category_wise_expense(populated_manager, capsys):
    populated_manager.category_wise_expense("2026-09")
    captured = capsys.readouterr().out
    assert "Food: Rs.800.0" in captured
    assert "Shopping: Rs.1200.0" in captured


def test_highest_expense(populated_manager, capsys):
    populated_manager.highest_expense("2026-09")
    captured = capsys.readouterr().out
    assert "Expense: Rs.1200.0" in captured
    assert "Category: Shopping" in captured


def test_budget_validation_within(populated_manager, capsys):
    populated_manager.budget_validation()
    captured = capsys.readouterr().out
    assert "You are within the budget." in captured
    assert "Remaining Budget: Rs.3000.0" in captured


def test_budget_validation_exceeded(populated_manager, capsys):
    populated_manager.set_monthly_budget("2026-09", 1500.0)
    populated_manager.budget_validation()
    captured = capsys.readouterr().out
    assert "Warning: Budget exceeded." in captured


def test_multi_user_data_isolation(temp_data_dir):
    # Instantiate manager for user A
    mgr_user_a = FinanceManager(username="user_a")
    mgr_user_a.set_monthly_budget("2026-09", 5000.0)
    inc_a = Income(4000.0, "Salary", "User A Salary", "Company A")
    mgr_user_a.income.append(inc_a)

    # Instantiate manager for user B
    mgr_user_b = FinanceManager(username="user_b")

    # Verify user B starts with empty records and 0 budget
    assert mgr_user_b.total_income() == 0.0
    assert mgr_user_b.budget == 0.0
    assert len(mgr_user_b.income) == 0

    # User A records
    assert mgr_user_a.total_income() == 4000.0
    assert mgr_user_a.budget == 5000.0

