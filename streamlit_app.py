import base64
import io
import os
import pandas as pd
import streamlit as st
from pathlib import Path
from logger_config import get_logger
from auth import UserManager
from email_service import send_monthly_report_email
from whatsapp_service import (
    generate_whatsapp_web_link,
    format_monthly_report_message,
    send_whatsapp_message,
    dispatch_user_monthly_report,
    _load_env,
)

_load_env()
logger = get_logger("streamlit_app")
if "auth_manager" not in st.session_state:
    st.session_state.auth_manager = UserManager()
auth_manager = st.session_state.auth_manager

# Step 2: Define base paths and constants
ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
REPORT_FILE = ROOT / "financial_report.csv"
CURRENCY = "Rs."


def get_current_user_data_dir() -> Path:
    """Resolve data directory for logged-in user or fallback."""
    username = st.session_state.get("username", "default")
    if not username or username == "default":
        DATA_DIR.mkdir(exist_ok=True)
        return DATA_DIR
    return auth_manager.get_user_data_dir(username)


def get_income_file() -> Path:
    return get_current_user_data_dir() / "income.csv"


def get_expense_file() -> Path:
    return get_current_user_data_dir() / "expenses.csv"


def get_budget_file() -> Path:
    return get_current_user_data_dir() / "budget.csv"


# Step 3: Define utility function to auto-create directory and CSV files with proper headers.
def ensure_data_files():
    """Ensure the user's data folder and required CSV files exist with proper headers."""
    user_dir = get_current_user_data_dir()
    user_dir.mkdir(parents=True, exist_ok=True)

    income_path = get_income_file()
    expense_path = get_expense_file()
    budget_path = get_budget_file()

    # Create income CSV if non-existent or empty
    if not income_path.exists() or income_path.stat().st_size == 0:
        pd.DataFrame(columns=["date", "timestamp", "amount", "category", "source", "description"]).to_csv(
            income_path, index=False
        )

    # Create expense CSV if non-existent or empty
    if not expense_path.exists() or expense_path.stat().st_size == 0:
        pd.DataFrame(columns=["date", "timestamp", "amount", "category", "payment", "description"]).to_csv(
            expense_path, index=False
        )

    # Create budget CSV if non-existent or empty
    if not budget_path.exists() or budget_path.stat().st_size == 0:
        pd.DataFrame(columns=["month", "budget"]).to_csv(budget_path, index=False)


# Step 4: Define data loader functions using pandas DataFrames.
def load_income():
    """Load income data for current user as a pandas DataFrame."""
    ensure_data_files()
    income_path = get_income_file()
    try:
        df = pd.read_csv(income_path)
    except (pd.errors.EmptyDataError, FileNotFoundError):
        df = pd.DataFrame(columns=["date", "timestamp", "amount", "category", "source", "description"])
    return df if not df.empty else pd.DataFrame(columns=["date", "timestamp", "amount", "category", "source", "description"])


def load_expenses():
    """Load expense data for current user as a pandas DataFrame."""
    ensure_data_files()
    expense_path = get_expense_file()
    try:
        df = pd.read_csv(expense_path)
    except (pd.errors.EmptyDataError, FileNotFoundError):
        df = pd.DataFrame(columns=["date", "timestamp", "amount", "category", "payment", "description"])
    return df if not df.empty else pd.DataFrame(columns=["date", "timestamp", "amount", "category", "payment", "description"])


def load_budget():
    """Load monthly budget settings for current user as a pandas DataFrame."""
    ensure_data_files()
    budget_path = get_budget_file()
    try:
        df = pd.read_csv(budget_path)
    except (pd.errors.EmptyDataError, FileNotFoundError):
        df = pd.DataFrame(columns=["month", "budget"])
    return df if not df.empty else pd.DataFrame(columns=["month", "budget"])


# Step 5: Define data saver functions to persist DataFrame changes to disk.
def save_excel_report():
    """Write current user data to financial_report.xlsx with all sheets."""
    ensure_data_files()
    income_path = get_income_file()
    expense_path = get_expense_file()
    budget_path = get_budget_file()

    try:
        inc_df = pd.read_csv(income_path)
    except Exception:
        inc_df = pd.DataFrame(columns=["date", "timestamp", "amount", "category", "source", "description"])

    try:
        exp_df = pd.read_csv(expense_path)
    except Exception:
        exp_df = pd.DataFrame(columns=["date", "timestamp", "amount", "category", "payment", "description"])

    try:
        bdg_df = pd.read_csv(budget_path)
    except Exception:
        bdg_df = pd.DataFrame(columns=["month", "budget"])


    # Normalize dates to YYYY-MM-DD format
    if not inc_df.empty and "date" in inc_df.columns:
        inc_df["date"] = pd.to_datetime(inc_df["date"], errors="coerce").dt.strftime("%Y-%m-%d").fillna(inc_df["date"].astype(str))
    if not exp_df.empty and "date" in exp_df.columns:
        exp_df["date"] = pd.to_datetime(exp_df["date"], errors="coerce").dt.strftime("%Y-%m-%d").fillna(exp_df["date"].astype(str))

    clean_income = (
        inc_df[["date", "amount", "category", "source", "description"]]
        if not inc_df.empty and "source" in inc_df.columns
        else inc_df
    )
    clean_expenses = (
        exp_df[["date", "amount", "category", "payment", "description"]]
        if not exp_df.empty and "payment" in exp_df.columns
        else exp_df
    )

    all_transactions = []
    if not inc_df.empty:
        for _, row in inc_df.iterrows():
            all_transactions.append({
                "type": "Income",
                "date": str(row.get("date", "")),
                "amount": row.get("amount", 0.0),
                "category": str(row.get("category", "")),
                "detail": str(row.get("source", "")),
                "description": str(row.get("description", "")),
            })
    if not exp_df.empty:
        for _, row in exp_df.iterrows():
            all_transactions.append({
                "type": "Expense",
                "date": str(row.get("date", "")),
                "amount": row.get("amount", 0.0),
                "category": str(row.get("category", "")),
                "detail": str(row.get("payment", "")),
                "description": str(row.get("description", "")),
            })
    history_df = pd.DataFrame(all_transactions)
    if not history_df.empty:
        history_df = history_df.sort_values(by="date", ascending=False)

    cat_summary = pd.DataFrame(columns=["category", "total_amount"])
    if not exp_df.empty and "category" in exp_df.columns:
        cat_grp = exp_df.groupby("category")["amount"].sum().reset_index()
        cat_summary = cat_grp.rename(columns={"amount": "total_amount"}).sort_values(by="total_amount", ascending=False)

    tot_inc = float(inc_df["amount"].sum()) if not inc_df.empty and "amount" in inc_df.columns else 0.0
    tot_exp = float(exp_df["amount"].sum()) if not exp_df.empty and "amount" in exp_df.columns else 0.0
    tot_savings = tot_inc - tot_exp
    curr_budget = float(bdg_df["budget"].sum()) if not bdg_df.empty and "budget" in bdg_df.columns else 0.0

    summary = pd.DataFrame(
        {
            "Metric": ["Total Income", "Total Expense", "Monthly Savings", "Current Budget"],
            "Value": [tot_inc, tot_exp, tot_savings, curr_budget],
        }
    )

    excel_path = ROOT / "financial_report.xlsx"
    try:
        with pd.ExcelWriter(excel_path, engine="openpyxl") as writer:
            clean_income.to_excel(writer, sheet_name="Income", index=False)
            clean_expenses.to_excel(writer, sheet_name="Expenses", index=False)
            bdg_df.to_excel(writer, sheet_name="Budget", index=False)
            history_df.to_excel(writer, sheet_name="Transactions", index=False)
            cat_summary.to_excel(writer, sheet_name="Category Expenses", index=False)
            summary.to_excel(writer, sheet_name="Summary", index=False)
    except PermissionError:
        st.warning("'financial_report.xlsx' is currently open in Excel. Please save and close the file in Excel so Streamlit can update it.")
    except Exception:
        pass


def save_income(df):
    """Save updated income DataFrame for current user."""
    df.to_csv(get_income_file(), index=False)
    save_excel_report()


def save_expenses(df):
    """Save updated expenses DataFrame for current user."""
    df.to_csv(get_expense_file(), index=False)
    save_excel_report()


def save_budget(df):
    """Save updated budget DataFrame for current user."""
    df.to_csv(get_budget_file(), index=False)
    save_excel_report()


# Step 6: Define financial aggregate helper functions.
def total_income():
    """Calculate the total sum of all recorded income entries."""
    return float(load_income()["amount"].sum()) if "amount" in load_income().columns and not load_income().empty else 0.0


def total_expense():
    """Calculate the total sum of all recorded expense entries."""
    return float(load_expenses()["amount"].sum()) if "amount" in load_expenses().columns and not load_expenses().empty else 0.0


def monthly_savings_value():
    """Compute overall net savings (Total Income - Total Expenses)."""
    return total_income() - total_expense()


def get_month_label():
    """Return the current year-month string formatted as YYYY-MM."""
    return pd.Timestamp.today().strftime("%Y-%m")


def display_table(dataframe):
    """Display a 1-indexed formatted DataFrame table in Streamlit."""
    displayed = dataframe.reset_index(drop=True)
    displayed.index = displayed.index + 1
    st.dataframe(displayed, use_container_width=True)


# Step 7: Configure Streamlit page layout and authentication session state.
st.set_page_config(page_title="Personal Finance Manager", page_icon="💼", layout="wide")

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "username" not in st.session_state:
    st.session_state.username = None
if "user_info" not in st.session_state:
    st.session_state.user_info = {}

# Authentication Portal Gate
if not st.session_state.authenticated:
    st.title("🔐 Personal Finance Portal")
    st.write("Please sign up, log in, or reset your password to manage your personal finance data.")

    tab_login, tab_signup, tab_forgot = st.tabs(["🔑 Log In", "📝 Sign Up", "❓ Forgot Password"])

    with tab_login:
        st.subheader("Account Login")
        with st.form("login_form"):
            login_user = st.text_input("Username")
            login_pass = st.text_input("Password", type="password")
            login_btn = st.form_submit_button("Log In", use_container_width=True)

            if login_btn:
                success, msg, user_info = auth_manager.login(login_user, login_pass)
                if success:
                    st.session_state.authenticated = True
                    st.session_state.username = login_user
                    st.session_state.user_info = user_info
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)

    with tab_signup:
        st.subheader("Create New User Account")
        with st.form("signup_form"):
            signup_user = st.text_input("Desired Username")
            signup_name = st.text_input("Full Name")
            signup_email = st.text_input("Email Address")
            signup_phone = st.text_input("WhatsApp Phone Number (e.g. +919876543210)")
            whatsapp_auto = st.checkbox("Enable Automated Monthly WhatsApp Reports & Reminders", value=True)
            signup_pass = st.text_input("Password", type="password")
            signup_pass_confirm = st.text_input("Confirm Password", type="password")
            signup_btn = st.form_submit_button("Sign Up", use_container_width=True)

            if signup_btn:
                if signup_pass != signup_pass_confirm:
                    st.error("Passwords do not match. Please re-enter your password.")
                else:
                    success, msg = auth_manager.signup(
                        signup_user,
                        signup_pass,
                        signup_name,
                        signup_email,
                        signup_phone,
                        whatsapp_auto,
                    )
                    if success:
                        st.success(msg + " You can now log in using your credentials.")
                    else:
                        st.error(msg)

    with tab_forgot:
        st.subheader("Forgot Password / Reset with OTP")
        st.write("Enter your registered username or email to receive a 6-digit OTP code.")
        
        with st.form("request_otp_form"):
            reset_identifier = st.text_input("Username or Email Address")
            send_otp_btn = st.form_submit_button("Send OTP Code", use_container_width=True)

            if send_otp_btn:
                if not reset_identifier.strip():
                    st.error("Please enter your username or registered email address.")
                else:
                    success, msg, found_username = auth_manager.request_password_reset_otp(reset_identifier)
                    if success:
                        st.session_state["otp_target_user"] = found_username
                        st.success(msg + " Enter the OTP below to set a new password.")
                    else:
                        st.error(msg)

        st.markdown("---")
        st.subheader("Set New Password")
        with st.form("verify_otp_form"):
            reset_user = st.text_input("Username or Email Address", value=st.session_state.get("otp_target_user", ""))
            input_otp = st.text_input("6-Digit OTP Code")
            new_password = st.text_input("New Password", type="password")
            new_password_confirm = st.text_input("Confirm New Password", type="password")
            reset_btn = st.form_submit_button("Reset Password", use_container_width=True)

            if reset_btn:
                if new_password != new_password_confirm:
                    st.error("New passwords do not match. Please try again.")
                else:
                    success, msg = auth_manager.verify_otp_and_reset_password(reset_user, input_otp, new_password)
                    if success:
                        st.success(msg + " You can now log in with your new password.")
                        if "otp_target_user" in st.session_state:
                            del st.session_state["otp_target_user"]
                    else:
                        st.error(msg)

    st.stop()  # Stop execution here if user is not authenticated

# Helper function for base64 sidebar avatar encoding
def get_image_base64(image_path: str) -> str:
    """Convert local image file to base64 data URI string for HTML rendering."""
    try:
        with open(image_path, "rb") as img_file:
            encoded = base64.b64encode(img_file.read()).decode("utf-8")
            ext = Path(image_path).suffix.lstrip(".").lower()
            mime = "image/png" if ext == "png" else f"image/{ext}"
            return f"data:{mime};base64,{encoded}"
    except Exception:
        return ""

# Logged in UI User Header in Sidebar
username = st.session_state.username
user_info = auth_manager.users.get(username, st.session_state.get("user_info", {}))
st.session_state.user_info = user_info

full_name = user_info.get("full_name") or username
email = user_info.get("email") or "Not provided"
phone = user_info.get("phone") or "Not provided"
auto_wa = user_info.get("whatsapp_auto_send", True)
profile_pic = user_info.get("profile_pic", "")
wa_badge = "<span style='color:#16a34a; font-weight:bold;'>Active 🟢</span>" if auto_wa else "<span style='color:#dc2626; font-weight:bold;'>Disabled 🔴</span>"

# Display profile avatar image or default emoji inside card
avatar_html = '<div style="font-size: 32px; margin-right: 12px; line-height: 1;">👤</div>'
if profile_pic and os.path.exists(profile_pic):
    img_b64 = get_image_base64(profile_pic)
    if img_b64:
        avatar_html = f'<img src="{img_b64}" style="width: 48px; height: 48px; border-radius: 50%; object-fit: cover; margin-right: 12px; border: 2px solid #2563eb; flex-shrink: 0;" />'

st.sidebar.markdown(
    f"""
    <div style="background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%); border: 1px solid #cbd5e1; border-radius: 12px; padding: 16px; margin-bottom: 14px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);">
        <div style="display: flex; align-items: center; margin-bottom: 10px;">
            {avatar_html}
            <div style="overflow: hidden;">
                <div style="font-size: 16px; font-weight: 700; color: #0f172a; text-overflow: ellipsis; overflow: hidden; white-space: nowrap;">{full_name}</div>
                <div style="font-size: 13px; color: #2563eb; font-weight: 600;">@{username}</div>
            </div>
        </div>
        <hr style="margin: 10px 0; border: 0; border-top: 1px solid #e2e8f0;" />
        <div style="font-size: 12px; color: #334155; line-height: 1.8;">
            <div>📧 <b>Email:</b> {email}</div>
            <div>📱 <b>Phone:</b> {phone}</div>
            <div>📲 <b>WhatsApp Auto-Send:</b> {wa_badge}</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

if st.sidebar.button("🚪 Logout", use_container_width=True):
    st.session_state.authenticated = False
    st.session_state.username = None
    st.session_state.user_info = {}
    st.rerun()

st.sidebar.markdown("---")
st.title(f"Personal Finance Management System - Welcome, {full_name}!")


# Step 8: Define menu navigation items and render sidebar radio selector.
menu_items = [
    "Add Income",
    "Add Expense",
    "View Income",
    "View Expenses",
    "Set Monthly Budget",
    "View Monthly Budget",
    "Budget Validation",
    "Transaction History",
    "Category Wise Expenses",
    "Monthly Savings",
    "Highest Expense",
    "Monthly Financial Report",
    "Financial Summary",
    "Search Transactions",
    "Delete Income",
    "Delete Expense",
    "Savings Goal",
    "Export Financial Report",
    "WhatsApp Settings & Direct Share",
]

menu = []
for index, label in enumerate(menu_items, start=1):
    menu.append(f"{index}. {label}")

choice = st.sidebar.radio("Select an option", menu)

# Step 9: Initialize storage directory and files.
ensure_data_files()

# Step 10: Process selected menu option and render corresponding UI views.

# Step 10.1: Add Income Form Handler
if choice == "1. Add Income":
    st.subheader("➕ Add Income Entry")
    income_categories = [
        "Salary",
        "Freelance / Side Hustle",
        "Business Revenue",
        "Investment / Dividends",
        "Rental Income",
        "Bonus / Reward",
        "Gift",
        "Other (Type custom category below)",
    ]

    with st.form("add_income_form"):
        income_amount = st.number_input("Amount", value=None, min_value=0.0, step=100.0, placeholder="Enter income amount")
        income_category_select = st.selectbox("Select Income Category", income_categories)
        income_category_custom = st.text_input("Custom Category (Optional if 'Other' selected)", placeholder="e.g. Consulting, Royalties")
        income_source = st.text_input("Source / Payer", placeholder="e.g. Company Name, Client Name, Bank")
        income_description = st.text_input("Description", placeholder="e.g. Monthly salary payout")
        submitted = st.form_submit_button("Add Income", use_container_width=True)

    if submitted:
        if income_amount is None or income_amount <= 0:
            st.error("Please enter a valid amount greater than 0.")
        else:
            final_category = (
                income_category_custom.strip()
                if "Other" in income_category_select and income_category_custom.strip()
                else income_category_select
            )
            df = load_income()
            new_row = {
                "date": pd.Timestamp.today().strftime("%Y-%m-%d"),
                "timestamp": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),
                "amount": income_amount,
                "category": final_category,
                "source": income_source.strip(),
                "description": income_description.strip(),
            }
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            save_income(df)
            st.success(f"Income of {CURRENCY} {income_amount:,.2f} under '{final_category}' added successfully.")

# Step 10.2: Add Expense Form Handler
elif choice == "2. Add Expense":
    st.subheader("➖ Add Expense Entry")
    expense_categories = [
        "Food & Dining",
        "Groceries",
        "Rent & Housing",
        "Bills & Utilities",
        "Transport / Fuel",
        "Shopping & Clothing",
        "Entertainment & Leisure",
        "Health & Medical",
        "Education",
        "Travel & Vacation",
        "Subscriptions & Software",
        "EMI & Loan",
        "Savings & Investment",
        "Other (Type custom category below)",
    ]

    payment_methods = [
        "UPI (GPay / PhonePe / Paytm)",
        "Credit Card",
        "Debit Card",
        "Cash",
        "Net Banking",
        "Bank Transfer",
        "Other",
    ]

    with st.form("add_expense_form"):
        expense_amount = st.number_input("Amount", value=None, min_value=0.0, step=50.0, placeholder="Enter expense amount")
        expense_category_select = st.selectbox("Select Expense Category", expense_categories)
        expense_category_custom = st.text_input("Custom Category (Optional if 'Other' selected)", placeholder="e.g. Repairs, Pet Care")
        expense_payment = st.selectbox("Payment Method", payment_methods)
        expense_description = st.text_input("Description", placeholder="e.g. Dinner with friends, Monthly groceries")
        submitted = st.form_submit_button("Add Expense", use_container_width=True)

    if submitted:
        if expense_amount is None or expense_amount <= 0:
            st.error("Please enter a valid amount greater than 0.")
        else:
            final_category = (
                expense_category_custom.strip()
                if "Other" in expense_category_select and expense_category_custom.strip()
                else expense_category_select
            )
            df = load_expenses()
            new_row = {
                "date": pd.Timestamp.today().strftime("%Y-%m-%d"),
                "timestamp": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),
                "amount": expense_amount,
                "category": final_category,
                "payment": expense_payment,
                "description": expense_description.strip(),
            }
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            save_expenses(df)
            st.success(f"Expense of {CURRENCY} {expense_amount:,.2f} under '{final_category}' added successfully.")

# Step 10.3: View Income Table Handler & Interactive Editor
elif choice == "3. View Income":
    st.subheader("View & Modify Income Data")
    df = load_income()
    if df.empty:
        st.info("No income records found.")
    else:
        st.caption(" Tip: You can double-click cells to modify, add new rows, or select and delete rows.")
        edited_df = st.data_editor(df, num_rows="dynamic", use_container_width=True, key="income_editor")
        if st.button(" Save Income Modifications"):
            save_income(edited_df)
            st.success("Income modifications saved successfully!")

# Step 10.4: View Expenses Table Handler & Interactive Editor
elif choice == "4. View Expenses":
    st.subheader("View & Modify Expense Data")
    df = load_expenses()
    if df.empty:
        st.info("No expense records found.")
    else:
        st.caption(" Tip: You can double-click cells to modify, add new rows, or select and delete rows.")
        edited_df = st.data_editor(df, num_rows="dynamic", use_container_width=True, key="expense_editor")
        if st.button(" Save Expense Modifications"):
            save_expenses(edited_df)
            st.success("Expense modifications saved successfully!")

# Step 10.5: Set Monthly Budget Handler
elif choice == "5. Set Monthly Budget":
    budget_value = st.number_input("Monthly budget", value=None, min_value=0.0, step=500.0, placeholder="Enter monthly budget")
    month = st.text_input("Month", value=get_month_label())
    if st.button("Save Budget"):
        if budget_value is None or budget_value <= 0:
            st.error("Please enter a valid budget amount greater than 0.")
        else:
            budget_df = load_budget()
            budget_df = budget_df[budget_df["month"] != month]
            budget_df = pd.concat([budget_df, pd.DataFrame([{"month": month, "budget": budget_value}])], ignore_index=True)
            save_budget(budget_df)
            st.success(f"Budget saved for {month}: {CURRENCY} {budget_value:,.2f}")

# Step 10.6: View Monthly Budget Handler & Interactive Editor
elif choice == "6. View Monthly Budget":
    st.subheader("View & Modify Monthly Budget")
    budget_df = load_budget()
    if budget_df.empty:
        st.info("No monthly budget set yet.")
    else:
        st.caption(" Tip: Double-click cells to modify monthly budgets.")
        edited_budget = st.data_editor(budget_df, num_rows="dynamic", use_container_width=True, key="budget_editor")
        if st.button(" Save Budget Modifications"):
            save_budget(edited_budget)
            st.success("Monthly budget modifications saved successfully!")

# Step 10.7: Budget Validation Metric Display Handler
elif choice == "7. Budget Validation":
    budget_df = load_budget()
    if budget_df.empty:
        st.info("Set a monthly budget first.")
    else:
        current_month = get_month_label()
        month_budget = float(budget_df.loc[budget_df["month"] == current_month, "budget"].sum()) if not budget_df.empty else 0.0
        expense_total = total_expense()
        st.metric("Current Month Budget", f"{CURRENCY} {month_budget:,.2f}")
        st.metric("Current Spending", f"{CURRENCY} {expense_total:,.2f}")
        if expense_total > month_budget:
            diff = expense_total - month_budget
            st.error(f"Budget exceeded by {CURRENCY} {diff:,.2f}")
        else:
            remaining = month_budget - expense_total
            st.success(f"Within budget. Remaining: {CURRENCY} {remaining:,.2f}")

# Step 10.8: Transaction History Log View Handler
elif choice == "8. Transaction History":
    income_df = load_income()
    expense_df = load_expenses()
    if income_df.empty and expense_df.empty:
        st.info("No transaction history available.")
    else:
        all_transactions = []
        for _, row in income_df.iterrows():
            all_transactions.append({
                "type": "Income",
                "date": row["date"],
                "amount": row["amount"],
                "category": row["category"],
                "detail": row["source"],
                "description": row["description"],
            })
        for _, row in expense_df.iterrows():
            all_transactions.append({
                "type": "Expense",
                "date": row["date"],
                "amount": row["amount"],
                "category": row["category"],
                "detail": row["payment"],
                "description": row["description"],
            })

        history = pd.DataFrame(all_transactions)
        if history.empty:
            st.info("No transaction history available.")
        else:
            history = history.sort_values(by="date", ascending=False)
        display_table(history)

# Step 10.9: Category-wise Expense Chart and Summary Handler
elif choice == "9. Category Wise Expenses":
    df = load_expenses()
    if df.empty:
        st.info("No expense data available.")
    else:
        category_summary = df.groupby("category")["amount"].sum().sort_values(ascending=False)
        st.bar_chart(category_summary)
        display_table(category_summary.reset_index().rename(columns={"amount": "total_amount"}))

# Step 10.10: Monthly Savings Metric Handler
elif choice == "10. Monthly Savings":
    income_total = total_income()
    expense_total = total_expense()
    savings = income_total - expense_total
    st.metric("Monthly Savings", f"{CURRENCY} {savings:,.2f}")
    if savings >= 0:
        st.success("You are saving positive money this month.")
    else:
        st.warning("Your expenses are above your income.")

# Step 10.11: Highest Expense Detail View Handler
elif choice == "11. Highest Expense":
    df = load_expenses()
    if df.empty:
        st.info("No expenses recorded.")
    else:
        top_expense = df.loc[df["amount"].idxmax()]
        st.metric("Highest Expense", f"{CURRENCY} {top_expense['amount']:,.2f}")
        st.markdown(f"**Category:** {top_expense['category']}")
        st.markdown(f"**Payment:** {top_expense['payment']}")
        st.markdown(f"**Description:** {top_expense['description']}")
        transaction_time = pd.to_datetime(top_expense.get("timestamp", top_expense["date"]))
        st.markdown(f"**Transaction Date:** {transaction_time.strftime('%A, %Y-%m-%d')}")
        st.markdown(f"**Transaction Time:** {transaction_time.strftime('%I:%M:%S %p')}")

# Step 10.12: Monthly Financial Breakdown Report Handler
elif choice == "12. Monthly Financial Report":
    income_total = total_income()
    expense_total = total_expense()
    savings = income_total - expense_total
    st.subheader("Monthly Financial Report")
    report = pd.DataFrame(
        {
            "Metric": ["Total Income", "Total Expense", "Savings"],
            "Value": [income_total, expense_total, savings],
        }
    )
    display_table(report)

# Step 10.13: Dashboard Key Metrics Summary Handler
elif choice == "13. Financial Summary":
    income_total = total_income()
    expense_total = total_expense()
    savings = monthly_savings_value()
    budget_df = load_budget()
    current_budget = float(budget_df["budget"].sum()) if not budget_df.empty else 0.0

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Income", f"{CURRENCY} {income_total:,.2f}")
    col2.metric("Expense", f"{CURRENCY} {expense_total:,.2f}")
    col3.metric("Savings", f"{CURRENCY} {savings:,.2f}")
    col4.metric("Budget", f"{CURRENCY} {current_budget:,.2f}")

# Step 10.14: Keyword Search Handler across Income and Expense records
elif choice == "14. Search Transactions":
    keyword = st.text_input("Search by category, source, payment, or description")
    if keyword:
        income_df = load_income()
        expense_df = load_expenses()
        matched_income = income_df[
            income_df.astype(str).apply(lambda row: keyword.lower() in " ".join(row).lower(), axis=1)
        ]
        matched_expense = expense_df[
            expense_df.astype(str).apply(lambda row: keyword.lower() in " ".join(row).lower(), axis=1)
        ]

        if matched_income.empty and matched_expense.empty:
            st.info("No matching transactions found.")
        else:
            st.subheader("Income Matches")
            display_table(matched_income)
            st.subheader("Expense Matches")
            display_table(matched_expense)
    else:
        st.info("Enter a keyword to search transactions.")

# Step 10.15: Income Record Deletion Handler
elif choice == "15. Delete Income":
    df = load_income()
    if df.empty:
        st.info("No income records available to delete.")
    else:
        display_ids = list(range(1, len(df) + 1))
        delete_id = st.selectbox("Select income row to delete", display_ids)
        if st.button("Delete Selected Income"):
            df = df.drop(index=delete_id - 1)
            save_income(df)
            st.success("Income record deleted successfully.")

# Step 10.16: Expense Record Deletion Handler
elif choice == "16. Delete Expense":
    df = load_expenses()
    if df.empty:
        st.info("No expense records available to delete.")
    else:
        display_ids = list(range(1, len(df) + 1))
        delete_id = st.selectbox("Select expense row to delete", display_ids)
        if st.button("Delete Selected Expense"):
            df = df.drop(index=delete_id - 1)
            save_expenses(df)
            st.success("Expense record deleted successfully.")

# Step 10.17: Savings Goal Checker Handler
elif choice == "17. Savings Goal":
    goal = st.number_input("Set savings goal", value=None, min_value=0.0, step=500.0, placeholder="Enter target savings goal")
    current_savings = monthly_savings_value()
    if st.button("Check Goal"):
        if goal is None or goal <= 0:
            st.error("Please enter a valid savings goal amount greater than 0.")
        else:
            if current_savings >= goal:
                st.success(f"Goal reached. Current savings: {CURRENCY} {current_savings:,.2f}")
            else:
                remaining = goal - current_savings
                st.warning(f"Goal not reached. Remaining amount: {CURRENCY} {remaining:,.2f}")

# Step 10.18: Export Multi-Sheet Excel Financial Report Handler
elif choice == "18. Export Financial Report":
    income_df = load_income()
    expense_df = load_expenses()
    budget_df = load_budget()

    # Clean Income & Expense DataFrames for export
    clean_income = (
        income_df[["date", "amount", "category", "source", "description"]]
        if not income_df.empty and "source" in income_df.columns
        else income_df
    )
    clean_expenses = (
        expense_df[["date", "amount", "category", "payment", "description"]]
        if not expense_df.empty and "payment" in expense_df.columns
        else expense_df
    )

    # Combined Transaction History
    all_transactions = []
    if not income_df.empty:
        for _, row in income_df.iterrows():
            all_transactions.append({
                "type": "Income",
                "date": row.get("date", ""),
                "amount": row.get("amount", 0.0),
                "category": row.get("category", ""),
                "detail": row.get("source", ""),
                "description": row.get("description", ""),
            })
    if not expense_df.empty:
        for _, row in expense_df.iterrows():
            all_transactions.append({
                "type": "Expense",
                "date": row.get("date", ""),
                "amount": row.get("amount", 0.0),
                "category": row.get("category", ""),
                "detail": row.get("payment", ""),
                "description": row.get("description", ""),
            })
    history_df = pd.DataFrame(all_transactions)
    if not history_df.empty:
        history_df = history_df.sort_values(by="date", ascending=False)

    # Category Wise Expense Breakdown
    cat_summary = pd.DataFrame(columns=["category", "total_amount"])
    if not expense_df.empty and "category" in expense_df.columns:
        cat_grp = expense_df.groupby("category")["amount"].sum().reset_index()
        cat_summary = cat_grp.rename(columns={"amount": "total_amount"}).sort_values(by="total_amount", ascending=False)

    # Financial Summary Metrics
    summary = pd.DataFrame(
        {
            "Metric": ["Total Income", "Total Expense", "Monthly Savings", "Current Budget"],
            "Value": [
                total_income(),
                total_expense(),
                monthly_savings_value(),
                float(budget_df["budget"].sum()) if not budget_df.empty else 0.0,
            ],
        }
    )

    try:
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
            clean_income.to_excel(writer, sheet_name="Income", index=False)
            clean_expenses.to_excel(writer, sheet_name="Expenses", index=False)
            budget_df.to_excel(writer, sheet_name="Budget", index=False)
            history_df.to_excel(writer, sheet_name="Transactions", index=False)
            cat_summary.to_excel(writer, sheet_name="Category Expenses", index=False)
            summary.to_excel(writer, sheet_name="Summary", index=False)

        # Also save local file on server as backup
        with open(REPORT_FILE.with_suffix(".xlsx"), "wb") as f:
            f.write(buffer.getvalue())

        st.success("Complete Financial Report (.xlsx) generated successfully!")
        st.download_button(
            label=" Click Here to Download Complete Financial Report (.xlsx)",
            data=buffer.getvalue(),
            file_name="financial_report.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

        st.markdown("---")
        st.subheader("📲 WhatsApp Report Delivery")

        user_info = st.session_state.get("user_info", {})
        current_month = get_month_label()
        user_phone = user_info.get("phone", "")

        # Format message & check if empty or filled
        msg_text, is_empty = format_monthly_report_message(
            st.session_state.username, current_month, income_df, expense_df, budget_df
        )

        if is_empty:
            st.warning("⚠️ Report is empty for this month (0 Income & 0 Expenses). The WhatsApp message generated is a reminder alert.")
        else:
            st.info("📊 Report contains financial data. Full summary will be shared via WhatsApp.")

        # Interactive WhatsApp Web Link Button (100% Free)
        wa_link = generate_whatsapp_web_link(user_phone, msg_text)
        st.link_button("🟢 Share Report via WhatsApp Web Link (Free)", wa_link, use_container_width=True)

        # Trigger Automated Direct WhatsApp Message via Meta Cloud API
        if st.button("🤖 Send Direct WhatsApp Message via Meta API", use_container_width=True):
            if not user_phone:
                st.error("Please add a WhatsApp phone number in '19. WhatsApp Settings & Direct Share'.")
            else:
                ok, res_msg, _ = dispatch_user_monthly_report(
                    user_info, current_month, income_df, expense_df, budget_df, trigger_source="export_button"
                )
                if ok:
                    st.success(f"Direct WhatsApp notification sent! ({res_msg})")
                else:
                    st.warning(f"Notice: {res_msg}")

        # Email Report Delivery Section
        st.markdown("---")
        st.subheader("📧 Email Report Delivery")
        user_email = user_info.get("email", "")

        if st.button("📧 Dispatch Financial Report to Registered Email", use_container_width=True):
            if not user_email:
                st.error("No registered email address found for your account.")
            else:
                inc_tot = total_income()
                exp_tot = total_expense()
                sav_tot = monthly_savings_value()
                bdg_tot = float(budget_df["budget"].sum()) if not budget_df.empty else 0.0
                ok_email, email_status = send_monthly_report_email(
                    user_email, st.session_state.username, current_month, inc_tot, exp_tot, sav_tot, bdg_tot
                )
                if ok_email:
                    st.success(f"Email report successfully sent to '{user_email}'!")
                else:
                    st.warning(f"Email delivery status: {email_status}")

        # Auto-trigger WhatsApp & Email on export if enabled
        if user_info.get("whatsapp_auto_send") and not st.session_state.get("wa_exported_already"):
            st.session_state["wa_exported_already"] = True
            if user_phone:
                ok, auto_msg, _ = dispatch_user_monthly_report(
                    user_info, current_month, income_df, expense_df, budget_df, trigger_source="auto_export"
                )
                st.caption(f"🤖 Automated WhatsApp Export Trigger: {auto_msg}")
            if user_email:
                inc_tot = total_income()
                exp_tot = total_expense()
                sav_tot = monthly_savings_value()
                bdg_tot = float(budget_df["budget"].sum()) if not budget_df.empty else 0.0
                ok_email, email_status = send_monthly_report_email(
                    user_email, st.session_state.username, current_month, inc_tot, exp_tot, sav_tot, bdg_tot
                )
                st.caption(f"📧 Automated Email Export Trigger: {email_status}")

    except ModuleNotFoundError:
        st.error("Excel export needs openpyxl. Install it with: pip install -r requirements.txt")

# Step 10.19: User Profile & WhatsApp Security Handler
elif choice == "19. WhatsApp Settings & Direct Share":
    st.subheader("👤 User Profile & WhatsApp Security Settings")

    username = st.session_state.username
    user_info = auth_manager.users.get(username, {})
    current_name = user_info.get("full_name", "")
    current_email = user_info.get("email", "")
    current_phone = user_info.get("phone", "")
    current_auto = user_info.get("whatsapp_auto_send", True)

    # -------------------------------------------------------------
    # SECTION 1: General Preferences (Full Name & Auto-Send)
    # -------------------------------------------------------------
    st.markdown("### 1. General Account Preferences")
    with st.form("general_profile_form"):
        new_name = st.text_input("Full Name", value=current_name)
        new_auto = st.checkbox("Enable Automated Monthly WhatsApp Reports & Reminders", value=current_auto)
        save_gen_btn = st.form_submit_button("Save General Preferences")

        if save_gen_btn:
            ok, msg = auth_manager.update_user_profile(username, full_name=new_name, whatsapp_auto_send=new_auto)
            if ok:
                st.session_state.user_info["full_name"] = new_name
                st.session_state.user_info["whatsapp_auto_send"] = new_auto
                st.success("General preferences updated successfully!")
                st.rerun()

    st.markdown("---")

    # -------------------------------------------------------------
    # SECTION 1B: 📸 Profile Picture Upload & Management
    # -------------------------------------------------------------
    st.markdown("### 📸 Profile Picture Upload")
    pic_col1, pic_col2 = st.columns([1, 2])
    with pic_col1:
        current_pic = user_info.get("profile_pic", "")
        if current_pic and os.path.exists(current_pic):
            st.image(current_pic, caption="Current Profile Picture", width=140)
        else:
            st.info("No custom profile picture uploaded yet.")

    with pic_col2:
        uploaded_pic = st.file_uploader("Upload new profile picture (PNG, JPG, WEBP)", type=["png", "jpg", "jpeg", "webp"])
        if uploaded_pic is not None:
            if st.button("🖼️ Save Profile Picture", use_container_width=True):
                ext = os.path.splitext(uploaded_pic.name)[1]
                ok, pic_msg, rel_path = auth_manager.save_profile_picture(
                    username, uploaded_pic.getvalue(), file_extension=ext
                )
                if ok:
                    st.session_state.user_info["profile_pic"] = rel_path
                    st.success(pic_msg)
                    st.rerun()
                else:
                    st.error(pic_msg)

        if current_pic and os.path.exists(current_pic):
            if st.button("🗑️ Remove Profile Picture"):
                auth_manager.update_user_profile(username, profile_pic="")
                st.session_state.user_info["profile_pic"] = ""
                st.success("Profile picture removed!")
                st.rerun()

    st.markdown("---")

    # -------------------------------------------------------------
    # SECTION 2: 2FA OTP Email Update
    # -------------------------------------------------------------
    st.markdown("### 2. 📧 Email Address Update (2FA OTP Secured)")
    st.caption(f"Current Email: **{current_email or 'Not set'}**")

    col_e1, col_e2 = st.columns(2)
    with col_e1:
        new_email_input = st.text_input("Enter New Email Address", placeholder="e.g. user@example.com", key="new_email_input")
        if st.button("📩 Request Email Update OTP", use_container_width=True):
            ok, email_msg = auth_manager.request_email_change_otp(username, new_email_input)
            if ok:
                st.success(email_msg)
            else:
                st.error(email_msg)

    with col_e2:
        email_otp_input = st.text_input("Enter 6-Digit Email OTP Code", key="email_otp_input")
        if st.button("✅ Verify & Save New Email", use_container_width=True):
            ok, verify_msg = auth_manager.verify_profile_otp_and_update(username, email_otp_input)
            if ok:
                st.success(verify_msg)
                st.rerun()
            else:
                st.error(verify_msg)

    st.markdown("---")

    # -------------------------------------------------------------
    # SECTION 3: 2FA OTP WhatsApp Phone Update
    # -------------------------------------------------------------
    st.markdown("### 3. 📱 WhatsApp Phone Number Update (2FA OTP Secured)")
    st.caption(f"Current Phone: **{current_phone or 'Not set'}**")

    col_p1, col_p2 = st.columns(2)
    with col_p1:
        new_phone_input = st.text_input("Enter New Mobile Phone Number", placeholder="e.g. +919876543210", key="new_phone_input")
        if st.button("📲 Request WhatsApp Phone OTP", use_container_width=True):
            ok, phone_msg, otp_code, wa_link = auth_manager.request_phone_change_otp(username, new_phone_input)
            if ok:
                st.session_state["pending_phone_wa_link"] = wa_link
                st.success("🔒 OTP created! Click the green button below to send/view it via WhatsApp:")
            else:
                st.error(phone_msg)

        if "pending_phone_wa_link" in st.session_state and st.session_state["pending_phone_wa_link"]:
            st.info("ℹ️ **Pop-up Notice:** Clicking the button below will open WhatsApp in a new tab with your verification OTP pre-filled.")
            st.toast("📲 WhatsApp OTP link ready! Opening in a new tab.", icon="💬")
            st.link_button("🟢 Click Here to Send OTP via WhatsApp", st.session_state["pending_phone_wa_link"], use_container_width=True)

    with col_p2:
        phone_otp_input = st.text_input("Enter 6-Digit Phone OTP Code", key="phone_otp_input")
        if st.button("✅ Verify & Save New Phone Number", use_container_width=True):
            ok, verify_msg = auth_manager.verify_profile_otp_and_update(username, phone_otp_input)
            if ok:
                if "pending_phone_wa_link" in st.session_state:
                    del st.session_state["pending_phone_wa_link"]
                if "pending_phone_otp" in st.session_state:
                    del st.session_state["pending_phone_otp"]
                st.success(verify_msg)
                st.rerun()
            else:
                st.error(verify_msg)

    st.markdown("---")
    st.subheader("📲 Instant Interactive WhatsApp Report Test")

    income_df = load_income()
    expense_df = load_expenses()
    budget_df = load_budget()
    current_month = get_month_label()

    msg_text, is_empty = format_monthly_report_message(username, current_month, income_df, expense_df, budget_df)

    st.markdown("### Message Preview:")
    st.code(msg_text, language="text")

    wa_link = generate_whatsapp_web_link(current_phone, msg_text)
    st.info("ℹ️ **Pop-up Notice:** Clicking the button below will open WhatsApp in a new tab with your monthly financial report pre-filled.")
    st.toast("💬 WhatsApp report link ready! Click below to send.", icon="🚀")
    st.link_button("📲 Click to Open in WhatsApp Web / App", wa_link, use_container_width=True)

# Default Fallback Prompt
else:
    st.info("Choose an option from the menu to continue.")

