import pytest
from report import FinancialReport


def test_monthly_report_generation(populated_manager, capsys):
    report = FinancialReport(populated_manager)
    report.monthly_report("2026-09")
    captured = capsys.readouterr().out
    assert "MONTHLY FINANCIAL REPORT" in captured
    assert "Month          : 2026-09" in captured
    assert "Total Income   : Rs.4500.0" in captured
    assert "Total Expense  : Rs.2000.0" in captured
    assert "Total Savings  : Rs.2500.0" in captured
    assert "Within Budget" in captured


def test_financial_summary(populated_manager, capsys):
    report = FinancialReport(populated_manager)
    report.summary()
    captured = capsys.readouterr().out
    assert "Income Records  : 2" in captured
    assert "Expense Records : 3" in captured
