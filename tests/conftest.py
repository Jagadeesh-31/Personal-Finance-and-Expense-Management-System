import os
import pytest
import shutil
from pathlib import Path
from finance import FinanceManager, Income, Expense


@pytest.fixture
def temp_data_dir(tmp_path, monkeypatch):
    """Fixture to redirect working directory to a temporary folder for isolated tests."""
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    
    # Change current working directory to tmp_path so 'data/' files are created isolated
    monkeypatch.chdir(tmp_path)
    return tmp_path


@pytest.fixture
def clean_manager(temp_data_dir):
    """Fixture providing a fresh FinanceManager instance with no pre-existing records."""
    manager = FinanceManager()
    return manager


@pytest.fixture
def populated_manager(temp_data_dir):
    """Fixture providing a FinanceManager instance populated with test income and expenses."""
    manager = FinanceManager()

    # Set budget
    manager.set_monthly_budget("2026-09", 5000.0)

    # Add test income entries
    inc1 = Income(3000.0, "Salary", "Monthly Salary", "Employer")
    inc1.date = "2026-09-01"
    inc2 = Income(1500.0, "Freelance", "Project X", "Client")
    inc2.date = "2026-09-05"
    manager.income.extend([inc1, inc2])

    # Add test expense entries
    exp1 = Expense(500.0, "Food", "Groceries", "UPI")
    exp1.date = "2026-09-02"
    exp2 = Expense(1200.0, "Shopping", "Clothes", "Card")
    exp2.date = "2026-09-10"
    exp3 = Expense(300.0, "Food", "Dinner out", "Cash")
    exp3.date = "2026-09-15"
    manager.expenses.extend([exp1, exp2, exp3])

    return manager
