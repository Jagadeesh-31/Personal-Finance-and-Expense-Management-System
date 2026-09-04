# Personal Finance Management System

A Python application for recording income and expenses, managing monthly budgets, and generating financial reports.

## Features

- User Authentication (Sign Up & Log In with PBKDF2 HMAC SHA-256 password hashing)
- Multi-user data isolation and personalized tracking per account
- Add and view income records
- Add and view expense records
- Expense categories and payment methods
- Monthly budgets with CSV persistence
- Budget validation and remaining-budget calculation
- Transaction history
- Category-wise expense totals
- Monthly savings calculation
- Highest-expense identification
- Monthly financial reports
- Financial summary
- Streamlit dashboard with authentication portal, search, delete, savings goal, and Excel export
- WhatsApp Integration: Interactive WhatsApp Web pre-filled sharing (`wa.me`) & automated direct delivery via Meta WhatsApp Cloud API
- Smart WhatsApp Content: Dispatches full financial reports for active months and automated reminder alerts (*"You did not record any income/expenses this month"*) for empty months
- Dual Triggers: Automatic monthly completion dispatch & instant trigger on "Export Report" button click
- Centralized logging & Pytest automated test suite
- Transaction tables with row numbers starting at 1


## WhatsApp Configuration & Automated Scheduler

### 1. Interactive WhatsApp Sharing (100% Free)
Click the **"📲 Share Report via WhatsApp Web Link"** button in the Streamlit app to open WhatsApp Web or Mobile with your pre-filled report or reminder alert.

### 2. Meta WhatsApp Cloud API (Automated Direct Messaging)
To enable background direct messaging:
1. Copy `.env.example` to `.env`.
2. Add your Meta WhatsApp API Token and Sender Phone Number ID:
   ```env
   META_WHATSAPP_TOKEN=your_meta_token_here
   META_PHONE_NUMBER_ID=your_meta_phone_number_id_here
   ```

### 3. Automated Monthly Background Dispatcher
To run the automated monthly WhatsApp dispatch for all registered accounts:
```bash
python monthly_scheduler.py
```

- Python 3.11 or later
- pandas
- streamlit
- openpyxl for Excel report export

## Installation

Open a terminal in the project folder and run:

```bash
pip install -r requirements.txt
```

## Run the Console Application

```bash
python main.py
```

The console menu provides options for income, expenses, budgets, history, savings, category analysis, highest expense, reports, and summary.

## Run the Streamlit Application

```bash
streamlit run streamlit_app.py
```

Open the URL shown in the terminal. The Streamlit application provides the complete visual dashboard and report features.

## Run the Desktop GUI Application

```bash
python gui/gui_app.py
```

The desktop GUI provides an offline dashboard for tracking transactions and summary cards.

## Data Storage

Application data is stored in the `data` folder:

- `income.csv` stores income records.
- `expenses.csv` stores expense records.
- `transactions.csv` stores transaction history for the console application.
- `budgets.csv` stores monthly console budgets.
- `budget.csv` stores Streamlit monthly budgets.

Generated financial reports are saved in the project folder.

## Monthly Calculations

Monthly reports use the `YYYY-MM` format, for example `2026-08`.

```text
Monthly Savings = Monthly Income - Monthly Expenses
Remaining Budget = Monthly Budget - Monthly Expenses
```

## Project Files

- `finance.py`: Transaction classes, CSV storage, calculations, and validation.
- `report.py`: Console financial report generation.
- `main.py`: Console menu and application entry point.
- `streamlit_app.py`: Streamlit dashboard.
- `gui/gui_app.py`: Tkinter desktop transaction dashboard.
- `requirements.txt`: Python dependencies.

## Troubleshooting

If Excel export reports that `openpyxl` is missing, run:

```bash
python -m pip install openpyxl
```

Then restart Streamlit.
