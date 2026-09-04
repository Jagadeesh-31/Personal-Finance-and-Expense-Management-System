import argparse
import json
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
from auth import UserManager
from logger_config import get_logger
from whatsapp_service import dispatch_user_monthly_report

# Step 1: Initialize logger for automated monthly scheduler
logger = get_logger("monthly_scheduler")


def get_previous_month_label() -> str:
    """Calculate year-month string for previous month (YYYY-MM)."""
    today = datetime.today()
    first_of_this_month = today.replace(day=1)
    last_day_prev_month = first_of_this_month - timedelta(days=1)
    return last_day_prev_month.strftime("%Y-%m")


def load_user_dataframe(user_dir: Path, filename: str, columns: list) -> pd.DataFrame:
    """Helper to safely load user CSV file as pandas DataFrame."""
    filepath = user_dir / filename
    if not filepath.exists():
        return pd.DataFrame(columns=columns)
    try:
        df = pd.read_csv(filepath)
        return df if not df.empty else pd.DataFrame(columns=columns)
    except Exception as err:
        logger.error(f"Error loading {filename} for path {user_dir}: {err}")
        return pd.DataFrame(columns=columns)


def run_monthly_whatsapp_dispatch(target_month: str = None, force_send: bool = False):
    """
    Run automated monthly WhatsApp report/reminder dispatch for all registered users.
    """
    if not target_month:
        target_month = get_previous_month_label()

    logger.info(f"Starting automated monthly WhatsApp dispatch for month: {target_month}")

    auth_manager = UserManager()
    data_dir = auth_manager.data_dir
    tracker_file = data_dir / "sent_whatsapp_reports.json"

    # Load dispatched report history log
    dispatched_history = {}
    if tracker_file.exists():
        try:
            with open(tracker_file, "r", encoding="utf-8") as f:
                dispatched_history = json.load(f)
        except Exception:
            dispatched_history = {}

    summary_stats = {"total_users": len(auth_manager.users), "sent": 0, "skipped": 0, "errors": 0}

    for username, user_info in auth_manager.users.items():
        phone = user_info.get("phone", "").strip()
        auto_send = user_info.get("whatsapp_auto_send", True)

        if not auto_send or not phone:
            logger.info(f"Skipping user '{username}': Auto-send disabled or no phone number.")
            summary_stats["skipped"] += 1
            continue

        # Prevent duplicate monthly dispatches unless force_send is True
        user_key = f"{username}:{target_month}"
        if user_key in dispatched_history and not force_send:
            logger.info(f"Skipping user '{username}': Already dispatched for month {target_month}.")
            summary_stats["skipped"] += 1
            continue

        # Resolve user isolated data directory
        user_dir = auth_manager.get_user_data_dir(username)
        inc_df = load_user_dataframe(user_dir, "income.csv", ["date", "timestamp", "amount", "category", "source", "description"])
        exp_df = load_user_dataframe(user_dir, "expenses.csv", ["date", "timestamp", "amount", "category", "payment", "description"])
        bdg_df = load_user_dataframe(user_dir, "budget.csv", ["month", "budget"])

        # Execute WhatsApp dispatch (handles filled report vs empty reminder)
        ok, status_msg, msg_text = dispatch_user_monthly_report(
            user_info, target_month, inc_df, exp_df, bdg_df, trigger_source="monthly_cron"
        )

        if ok:
            summary_stats["sent"] += 1
            dispatched_history[user_key] = {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "status": status_msg,
                "phone": phone
            }
        else:
            summary_stats["errors"] += 1

    # Save updated tracking log
    try:
        with open(tracker_file, "w", encoding="utf-8") as f:
            json.dump(dispatched_history, f, indent=4)
    except Exception as err:
        logger.error(f"Error saving tracking log: {err}")

    logger.info(f"Monthly WhatsApp Dispatch completed: {summary_stats}")
    return summary_stats


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Automated Monthly WhatsApp Financial Report & Reminder Dispatcher")
    parser.add_argument("--month", type=str, help="Target month in YYYY-MM format (defaults to previous month)")
    parser.add_argument("--force", action="store_true", help="Force resending reports even if already sent")
    args = parser.parse_args()

    results = run_monthly_whatsapp_dispatch(target_month=args.month, force_send=args.force)
    print(f"[OK] Automated Monthly WhatsApp Dispatch Completed: {results}")
