# Step 1: Import core data processing and dashboard libraries.
import io
import pandas as pd
import streamlit as st
from pathlib import Path

# Step 2: Define file paths and constants for persistent data storage.
ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
INCOME_FILE = DATA_DIR / "income.csv"
EXPENSE_FILE = DATA_DIR / "expenses.csv"
BUDGET_FILE = DATA_DIR / "budget.csv"
REPORT_FILE = ROOT / "financial_report.csv"
CURRENCY = "Rs."


# Step 3: Define utility function to auto-create directory and CSV files with proper headers.
def ensure_data_files():
    """Ensure the data folder and required CSV files exist with proper headers."""
    DATA_DIR.mkdir(exist_ok=True)

    # Create income CSV if non-existent or empty
    if not INCOME_FILE.exists() or INCOME_FILE.stat().st_size == 0:
        pd.DataFrame(columns=["date", "timestamp", "amount", "category", "source", "description"]).to_csv(
            INCOME_FILE, index=False
        )

    # Create expense CSV if non-existent or empty
    if not EXPENSE_FILE.exists() or EXPENSE_FILE.stat().st_size == 0:
        pd.DataFrame(columns=["date", "timestamp", "amount", "category", "payment", "description"]).to_csv(
            EXPENSE_FILE, index=False
        )

    # Create budget CSV if non-existent or empty
    if not BUDGET_FILE.exists() or BUDGET_FILE.stat().st_size == 0:
        pd.DataFrame(columns=["month", "budget"]).to_csv(BUDGET_FILE, index=False)


# Step 4: Define data loader functions using pandas DataFrames.
def load_income():
    """Load income data from income.csv as a pandas DataFrame."""
    ensure_data_files()
    try:
        df = pd.read_csv(INCOME_FILE)
    except pd.errors.EmptyDataError:
        df = pd.DataFrame(columns=["date", "timestamp", "amount", "category", "source", "description"])
    return df if not df.empty else pd.DataFrame(columns=["date", "timestamp", "amount", "category", "source", "description"])


def load_expenses():
    """Load expense data from expenses.csv as a pandas DataFrame."""
    ensure_data_files()
    try:
        df = pd.read_csv(EXPENSE_FILE)
    except pd.errors.EmptyDataError:
        df = pd.DataFrame(columns=["date", "timestamp", "amount", "category", "payment", "description"])
    return df if not df.empty else pd.DataFrame(columns=["date", "timestamp", "amount", "category", "payment", "description"])


def load_budget():
    """Load monthly budget settings from budget.csv as a pandas DataFrame."""
    ensure_data_files()
    try:
        df = pd.read_csv(BUDGET_FILE)
    except pd.errors.EmptyDataError:
        df = pd.DataFrame(columns=["month", "budget"])
    return df if not df.empty else pd.DataFrame(columns=["month", "budget"])


# Step 5: Define data saver functions to persist DataFrame changes to disk.
def save_income(df):
    """Save updated income DataFrame to income.csv."""
    df.to_csv(INCOME_FILE, index=False)


def save_expenses(df):
    """Save updated expenses DataFrame to expenses.csv."""
    df.to_csv(EXPENSE_FILE, index=False)


def save_budget(df):
    """Save updated budget DataFrame to budget.csv."""
    df.to_csv(BUDGET_FILE, index=False)


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


# Step 7: Configure Streamlit page layout and main header.
st.set_page_config(page_title="Personal Finance Manager", page_icon="💼", layout="wide")
st.title("Personal Finance Management System")

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
    with st.form("add_income_form"):
        income_amount = st.number_input("Amount", min_value=0.0, step=100.0)
        income_category = st.text_input("Category")
        income_source = st.text_input("Source")
        income_description = st.text_input("Description")
        submitted = st.form_submit_button("Add Income")

    if submitted:
        df = load_income()
        new_row = {
            "date": pd.Timestamp.today().strftime("%Y-%m-%d"),
            "timestamp": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),
            "amount": income_amount,
            "category": income_category,
            "source": income_source,
            "description": income_description,
        }
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        save_income(df)
        st.success(f"Income of {CURRENCY} {income_amount:,.2f} added successfully.")

# Step 10.2: Add Expense Form Handler
elif choice == "2. Add Expense":
    with st.form("add_expense_form"):
        expense_amount = st.number_input("Amount", min_value=0.0, step=50.0)
        expense_category = st.text_input("Category")
        expense_payment = st.text_input("Payment Method")
        expense_description = st.text_input("Description")
        submitted = st.form_submit_button("Add Expense")

    if submitted:
        df = load_expenses()
        new_row = {
            "date": pd.Timestamp.today().strftime("%Y-%m-%d"),
            "timestamp": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),
            "amount": expense_amount,
            "category": expense_category,
            "payment": expense_payment,
            "description": expense_description,
        }
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        save_expenses(df)
        st.success(f"Expense of {CURRENCY} {expense_amount:,.2f} added successfully.")

# Step 10.3: View Income Table Handler
elif choice == "3. View Income":
    df = load_income()
    if df.empty:
        st.info("No income records found.")
    else:
        display_table(df)

# Step 10.4: View Expenses Table Handler
elif choice == "4. View Expenses":
    df = load_expenses()
    if df.empty:
        st.info("No expense records found.")
    else:
        display_table(df)

# Step 10.5: Set Monthly Budget Handler
elif choice == "5. Set Monthly Budget":
    budget_value = st.number_input("Monthly budget", min_value=0.0, step=500.0)
    month = st.text_input("Month", value=get_month_label())
    if st.button("Save Budget"):
        budget_df = load_budget()
        budget_df = budget_df[budget_df["month"] != month]
        budget_df = pd.concat([budget_df, pd.DataFrame([{"month": month, "budget": budget_value}])], ignore_index=True)
        save_budget(budget_df)
        st.success(f"Budget saved for {month}: {CURRENCY} {budget_value:,.2f}")

# Step 10.6: View Monthly Budget Handler
elif choice == "6. View Monthly Budget":
    budget_df = load_budget()
    if budget_df.empty:
        st.info("No monthly budget set yet.")
    else:
        display_table(budget_df)

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
    goal = st.number_input("Set savings goal", min_value=0.0, step=500.0)
    current_savings = monthly_savings_value()
    if st.button("Check Goal"):
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

    summary = pd.DataFrame(
        {
            "Metric": ["Total Income", "Total Expense", "Monthly Savings", "Budget"],
            "Value": [total_income(), total_expense(), monthly_savings_value(), float(budget_df["budget"].sum()) if not budget_df.empty else 0.0],
        }
    )

    try:
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
            income_df.to_excel(writer, sheet_name="Income", index=False)
            expense_df.to_excel(writer, sheet_name="Expenses", index=False)
            budget_df.to_excel(writer, sheet_name="Budget", index=False)
            summary.to_excel(writer, sheet_name="Summary", index=False)

        # Also save local file on server as backup
        with open(REPORT_FILE.with_suffix(".xlsx"), "wb") as f:
            f.write(buffer.getvalue())

        st.success("Report generated successfully!")
        st.download_button(
            label="📥 Click Here to Download Financial Report (.xlsx)",
            data=buffer.getvalue(),
            file_name="financial_report.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
    except ModuleNotFoundError:
        st.error("Excel export needs openpyxl. Install it with: pip install -r requirements.txt")

# Default Fallback Prompt
else:
    st.info("Choose an option from the menu to continue.")

