# Personal Finance Management System

A Python application for recording income and expenses, managing monthly budgets, and generating financial reports.

## Features

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
- Streamlit dashboard with search, delete, savings goal, and Excel export
- Transaction tables with row numbers starting at 1

## Requirements

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
- `gui.py`: Tkinter transaction dashboard.
- `requirements.txt`: Python dependencies.

## Troubleshooting

If Excel export reports that `openpyxl` is missing, run:

```bash
python -m pip install openpyxl
```

Then restart Streamlit.
