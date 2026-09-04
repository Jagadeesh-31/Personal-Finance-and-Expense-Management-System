import json
import os
import re
import urllib.parse
import urllib.request
from typing import Tuple
from pathlib import Path
from logger_config import get_logger

# Step 1: Initialize logger for WhatsApp dispatch operations
logger = get_logger("whatsapp_service")


# Step 1.1: Helper function to dynamically load .env variables
def _load_env():
    env_file = Path.cwd() / ".env"
    if env_file.exists():
        try:
            with open(env_file, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        k, v = line.split("=", 1)
                        os.environ[k.strip()] = v.strip()
        except Exception:
            pass


def get_meta_token() -> str:
    _load_env()
    return os.environ.get("META_WHATSAPP_TOKEN", "").strip()


def get_meta_phone_id() -> str:
    _load_env()
    return os.environ.get("META_PHONE_NUMBER_ID", "").strip()


def get_meta_api_version() -> str:
    _load_env()
    return os.environ.get("META_API_VERSION", "v18.0").strip()


# Step 2: Format phone number into international E.164 numeric format
def clean_phone_number(phone: str) -> str:
    """
    Clean and format phone number into digits-only string.
    Defaults to India country code 91 if a 10-digit number is provided.
    """
    if not phone:
        return ""
    digits = re.sub(r"\D", "", phone.strip())
    if len(digits) == 10:
        digits = "91" + digits
    return digits


# Step 3: Build interactive WhatsApp Web pre-filled click link (wa.me)
def generate_whatsapp_web_link(phone: str, message: str) -> str:
    """
    Generate a 100% free pre-filled WhatsApp Web click URL (wa.me).
    """
    clean_phone = clean_phone_number(phone)
    encoded_text = urllib.parse.quote(message)
    if clean_phone:
        return f"https://api.whatsapp.com/send?phone={clean_phone}&text={encoded_text}"
    return f"https://api.whatsapp.com/send?text={encoded_text}"


# Step 4: Format monthly report message text and perform Empty Report Check
def format_monthly_report_message(
    username: str,
    month: str,
    income_df=None,
    expense_df=None,
    budget_df=None
) -> Tuple[str, bool]:
    """
    Construct formatted WhatsApp report message.
    Returns (message_text, is_empty).
    - If total income and total expense are 0, generates a Reminder Alert message.
    - Otherwise, generates a complete Financial Summary Report.
    """
    tot_inc = 0.0
    tot_exp = 0.0
    top_cat = "None"
    top_cat_amt = 0.0

    if income_df is not None and not income_df.empty and "amount" in income_df.columns:
        tot_inc = float(income_df["amount"].sum())

    if expense_df is not None and not expense_df.empty:
        if "amount" in expense_df.columns:
            tot_exp = float(expense_df["amount"].sum())
        if "category" in expense_df.columns and "amount" in expense_df.columns:
            cat_totals = expense_df.groupby("category")["amount"].sum()
            if not cat_totals.empty:
                top_cat = str(cat_totals.idxmax())
                top_cat_amt = float(cat_totals.max())

    tot_savings = tot_inc - tot_exp

    curr_budget = 0.0
    if budget_df is not None and not budget_df.empty and "budget" in budget_df.columns:
        curr_budget = float(budget_df["budget"].sum())

    rem_budget = curr_budget - tot_exp

    is_empty = (tot_inc == 0.0 and tot_exp == 0.0)

    if is_empty:
        message = (
            f"⚠️ *Personal Finance Reminder for {month}*\n\n"
            f"Hi *{username}*,\n"
            f"You did not record any income or expenses for the month of *{month}*!\n\n"
            f"💡 *Tip:* Please log your daily income and expenses in the app to keep your financial budget on track."
        )
        return message, True

    budget_status = f"Under budget by Rs. {rem_budget:,.2f}" if rem_budget >= 0 else f"OVER budget by Rs. {abs(rem_budget):,.2f}"

    message = (
        f"📊 *Personal Finance Report for {month}*\n"
        f"👤 *User:* {username}\n\n"
        f"💵 *Total Income:* Rs. {tot_inc:,.2f}\n"
        f"💸 *Total Expenses:* Rs. {tot_exp:,.2f}\n"
        f"📈 *Monthly Savings:* Rs. {tot_savings:,.2f}\n"
        f"🏷️ *Top Category:* {top_cat} (Rs. {top_cat_amt:,.2f})\n"
        f"🎯 *Budget Summary:* {budget_status}\n\n"
        f"✅ *Report generated via Personal Finance App*"
    )
    return message, False


# Step 5: Dispatch automated direct message using Meta WhatsApp Cloud API
def send_whatsapp_message(to_phone: str, message_text: str) -> Tuple[bool, str]:
    """
    Send automated direct WhatsApp message via Meta Cloud API.
    Falls back to offline log mode if credentials are missing.
    """
    clean_phone = clean_phone_number(to_phone)
    if not clean_phone:
        logger.warning("No recipient phone number provided. Skipping WhatsApp dispatch.")
        return False, "Recipient phone number is empty."

    token = get_meta_token()
    phone_id = get_meta_phone_id()
    api_version = get_meta_api_version()

    # Fallback mode if Meta credentials are not configured
    if not token or not phone_id or "your_meta" in token:
        logger.info(
            f"[DEV / OFFLINE WHATSAPP MODE] To: +{clean_phone}\nMessage:\n{message_text}"
        )
        return True, "WhatsApp message logged (Dev / Offline mode - Set META_WHATSAPP_TOKEN in .env to send live)."

    # Construct Meta WhatsApp API endpoint & payload
    url = f"https://graph.facebook.com/{api_version}/{phone_id}/messages"
    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": clean_phone,
        "type": "text",
        "text": {
            "preview_url": False,
            "body": message_text
        }
    }

    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        method="POST"
    )

    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            res_body = response.read().decode("utf-8")
            logger.info(f"Meta WhatsApp API Response ({response.status}): {res_body}")
            return True, "WhatsApp message sent successfully via Meta Cloud API."
    except urllib.error.HTTPError as http_err:
        err_msg = http_err.read().decode("utf-8")
        logger.error(f"Meta WhatsApp API HTTP Error ({http_err.code}): {err_msg}")
        return False, f"Meta API Error ({http_err.code}): {err_msg}"
    except Exception as err:
        logger.error(f"Failed to dispatch Meta WhatsApp message: {err}", exc_info=True)
        return False, f"WhatsApp delivery failed: {err}"


# Step 6: Master function handling complete dispatch workflow
def dispatch_user_monthly_report(
    user_info: dict,
    month: str,
    income_df=None,
    expense_df=None,
    budget_df=None,
    trigger_source: str = "manual"
) -> Tuple[bool, str, str]:
    """
    Format report and send WhatsApp notification (Report or Reminder).
    Returns (success, status_message, generated_message_text).
    """
    username = user_info.get("username", "User")
    phone = user_info.get("phone", "").strip()

    if not phone:
        msg = f"User '{username}' has no registered phone number."
        logger.warning(msg)
        return False, msg, ""

    message_text, is_empty = format_monthly_report_message(
        username, month, income_df, expense_df, budget_df
    )

    logger.info(
        f"Dispatching WhatsApp notification for user '{username}' (Month: {month}, "
        f"Is Empty: {is_empty}, Trigger: {trigger_source})"
    )

    success, api_msg = send_whatsapp_message(phone, message_text)
    return success, api_msg, message_text


# Step 7: Dispatch Phone Update Verification OTP via Meta API
def send_phone_update_otp(to_phone: str, username: str, otp: str) -> Tuple[bool, str]:
    """Send 6-digit WhatsApp OTP to verify new phone number update."""
    message = (
        f"🔒 Personal Finance Phone Verification OTP for @{username}: {otp}\n"
        f"(Valid for 5 minutes. Enter this code in the app to confirm your new phone number)."
    )
    return send_whatsapp_message(to_phone, message)


# Step 8: Build WhatsApp Web click link for Phone Update OTP (wa.me)
def generate_phone_update_otp_link(to_phone: str, username: str, otp: str) -> str:
    """Generate pre-filled wa.me link containing the exact Phone Update OTP message."""
    message = (
        f"🔒 Personal Finance Phone Verification OTP for @{username}: {otp}\n"
        f"(Valid for 5 minutes. Enter this code in the app to confirm your new phone number)."
    )
    return generate_whatsapp_web_link(to_phone, message)
