import pandas as pd
import pytest
from whatsapp_service import (
    clean_phone_number,
    generate_whatsapp_web_link,
    format_monthly_report_message,
    send_whatsapp_message,
    dispatch_user_monthly_report,
)
from monthly_scheduler import run_monthly_whatsapp_dispatch


def test_clean_phone_number():
    assert clean_phone_number("9876543210") == "919876543210"
    assert clean_phone_number("+91 9876543210") == "919876543210"
    assert clean_phone_number("") == ""


def test_generate_whatsapp_web_link():
    link = generate_whatsapp_web_link("9876543210", "Hello Test")
    assert "api.whatsapp.com/send" in link
    assert "phone=919876543210" in link
    assert "Hello%20Test" in link


def test_format_monthly_report_message_filled():
    inc_df = pd.DataFrame([{"amount": 5000.0, "category": "Salary"}])
    exp_df = pd.DataFrame([{"amount": 2000.0, "category": "Food"}])
    bdg_df = pd.DataFrame([{"month": "2026-09", "budget": 3000.0}])

    msg, is_empty = format_monthly_report_message("johndoe", "2026-09", inc_df, exp_df, bdg_df)
    assert is_empty is False
    assert "Personal Finance Report for 2026-09" in msg
    assert "Total Income:* Rs. 5,000.00" in msg
    assert "Total Expenses:* Rs. 2,000.00" in msg
    assert "Monthly Savings:* Rs. 3,000.00" in msg
    assert "Under budget by Rs. 1,000.00" in msg


def test_format_monthly_report_message_empty():
    inc_df = pd.DataFrame(columns=["amount"])
    exp_df = pd.DataFrame(columns=["amount"])
    bdg_df = pd.DataFrame(columns=["budget"])

    msg, is_empty = format_monthly_report_message("johndoe", "2026-09", inc_df, exp_df, bdg_df)
    assert is_empty is True
    assert "Personal Finance Reminder for 2026-09" in msg
    assert "You did not record any income or expenses" in msg


def test_send_whatsapp_message_offline_mode():
    ok, status = send_whatsapp_message("9876543210", "Test Message")
    assert ok is True
    assert "Dev / Offline mode" in status


def test_dispatch_user_monthly_report_no_phone():
    user_info = {"username": "nophoneuser", "phone": ""}
    ok, status, _ = dispatch_user_monthly_report(user_info, "2026-09")
    assert ok is False
    assert "no registered phone number" in status


def test_monthly_scheduler_run():
    res = run_monthly_whatsapp_dispatch(target_month="2026-09", force_send=True)
    assert "total_users" in res
    assert "sent" in res
