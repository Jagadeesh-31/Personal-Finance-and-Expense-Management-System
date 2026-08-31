# Step 1: Import modules for CSV operations, file path checks, and date management.
import csv
import os
from datetime import datetime


# Step 2: Define base Transaction class (Parent class for financial transactions).
class Transaction:
    """Base class for representing general financial transactions."""

    # Step 2.1: Initialize transaction attributes (amount, category, description, date).
    def __init__(self, amount, category, description):
        self.amount = amount
        self.category = category
        self.description = description
        # Automatically capture today's date in YYYY-MM-DD format
        self.date = datetime.now().strftime("%Y-%m-%d")

    # Step 2.2: Print details of the transaction to console.
    def display(self):
        print(f"Date: {self.date}")
        print(f"Amount: {self.amount}")
        print(f"Category: {self.category}")
        print(f"Description: {self.description}")


# Step 3: Inherit from Transaction to create Income subclass.
class Income(Transaction):
    """Represents an income entry with income-specific attributes."""

    # Step 3.1: Call parent constructor and set the source attribute (e.g., Salary, Freelance).
    def __init__(self, amount, category, description, source):
        super().__init__(amount, category, description)
        self.source = source

    # Step 3.2: Override display method to include income source.
    def display(self):
        print(f"Date: {self.date}")
        print(f"Income: Rs.{self.amount}")
        print(f"Category: {self.category}")
        print(f"Source: {self.source}")
        print(f"Description: {self.description}")


# Step 4: Inherit from Transaction to create Expense subclass.
class Expense(Transaction):
    """Represents an expense entry with payment method details."""

    # Step 4.1: Call parent constructor and set the payment method attribute (e.g., Cash, UPI, Card).
    def __init__(self, amount, category, description, payment):
        super().__init__(amount, category, description)
        self.payment = payment

    # Step 4.2: Override display method to include payment method.
    def display(self):
        print(f"Date: {self.date}")
        print(f"Expense: Rs.{self.amount}")
        print(f"Category: {self.category}")
        print(f"Payment: {self.payment}")
        print(f"Description: {self.description}")


# Step 5: Define the core FinanceManager class for data persistence and business logic.
class FinanceManager:
    """Core manager handling transaction lists, budget tracking, and persistent CSV storage."""

    # Step 5.1: Initialize storage structures and auto-initialize data files/load state.
    def __init__(self):
        self.income = []        # Stores list of Income objects
        self.expenses = []      # Stores list of Expense objects
        self.budget = 0         # Active monthly budget
        self.budgets = {}       # Dictionary mapping YYYY-MM -> budget amount

        # Step 5.1a: Ensure data folder and CSV headers exist
        self.create_files()
        # Step 5.1b: Load existing data from CSV files into memory
        self.load_data()

    # Step 5.2: Create required directories and CSV files with headers if absent.
    def create_files(self):

        # Step 5.2a: Create 'data' folder if it doesn't exist
        if not os.path.exists("data"):
            os.mkdir("data")

        # Step 5.2b: Create income.csv with column headers
        if not os.path.exists("data/income.csv"):
            with open("data/income.csv", "w", newline="") as file:
                writer = csv.writer(file)
                writer.writerow([
                    "date",
                    "amount",
                    "category",
                    "source",
                    "description"
                ])

        # Step 5.2c: Create expenses.csv with column headers
        if not os.path.exists("data/expenses.csv"):
            with open("data/expenses.csv", "w", newline="") as file:
                writer = csv.writer(file)
                writer.writerow([
                    "date",
                    "amount",
                    "category",
                    "payment",
                    "description"
                ])

        # Step 5.2d: Create transactions.csv with general log headers
        if not os.path.exists("data/transactions.csv"):
            with open("data/transactions.csv", "w", newline="") as file:
                writer = csv.writer(file)
                writer.writerow([
                    "date",
                    "type",
                    "amount",
                    "category",
                    "description"
                ])

        # Step 5.2e: Create budgets.csv with month-to-budget mapping headers
        if not os.path.exists("data/budgets.csv"):
            with open("data/budgets.csv", "w", newline="") as file:
                writer = csv.writer(file)
                writer.writerow(["month", "amount"])

    # Step 5.3: Read persistent CSV data and populate in-memory lists/dictionaries.
    def load_data(self):

        try:

            # Step 5.3a: Read income entries from data/income.csv
            with open("data/income.csv", "r") as file:
                reader = csv.DictReader(file)

                for row in reader:
                    income = Income(
                        float(row["amount"]),
                        row["category"],
                        row["description"],
                        row["source"]
                    )
                    income.date = row["date"]
                    self.income.append(income)

            # Step 5.3b: Read expense entries from data/expenses.csv
            with open("data/expenses.csv", "r") as file:
                reader = csv.DictReader(file)

                for row in reader:
                    expense = Expense(
                        float(row["amount"]),
                        row["category"],
                        row["description"],
                        row["payment"]
                    )
                    expense.date = row["date"]
                    self.expenses.append(expense)

            # Step 5.3c: Read budget mappings from data/budgets.csv
            with open("data/budgets.csv", "r") as file:
                reader = csv.DictReader(file)
                for row in reader:
                    self.budgets[row["month"]] = float(row["amount"])

            # Step 5.3d: Set current active budget for current YYYY-MM
            current_month = datetime.now().strftime("%Y-%m")
            self.budget = self.budgets.get(current_month, 0)

        except FileNotFoundError:
            print("Data files are not available.")

        except Exception as error:
            print("Error while loading data:", error)

    # Step 5.4: Calculate total income for a target month (YYYY-MM).
    def monthly_income(self, month):
        """Return total income recorded in specified YYYY-MM month."""
        return sum(item.amount for item in self.income if item.date.startswith(month))

    # Step 5.5: Calculate total expenses for a target month (YYYY-MM).
    def monthly_expense(self, month):
        """Return total expenses recorded in specified YYYY-MM month."""
        return sum(item.amount for item in self.expenses if item.date.startswith(month))

    # Step 5.6: Update monthly budget record in memory and write back to budgets.csv.
    def set_monthly_budget(self, month, amount):
        """Store a positive budget for a YYYY-MM month."""
        if amount <= 0:
            raise ValueError("Budget must be greater than zero")
        self.budgets[month] = amount
        self.budget = amount
        with open("data/budgets.csv", "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["month", "amount"])
            for budget_month, budget_amount in sorted(self.budgets.items()):
                writer.writerow([budget_month, budget_amount])

    # Step 5.7: Compute net monthly savings value (Monthly Income - Monthly Expense).
    def monthly_savings_value(self, month):
        return self.monthly_income(month) - self.monthly_expense(month)

    # Step 5.8: Interactively collect income inputs from console and append to CSV logs.
    def add_income(self):

        print("\n----- Add Income -----")

        try:

            # Step 5.8a: Validate positive amount input
            amount = float(input("Enter income amount: "))
            if amount <= 0:
                print("Amount must be greater than 0")
                return

            # Step 5.8b: Read source, category, and description text
            source = input("Enter income source: ")
            category = input("Enter income category: ")
            description = input("Enter description: ")

            # Step 5.8c: Construct Income instance and append to in-memory list
            income = Income(
                amount,
                category,
                description,
                source
            )
            self.income.append(income)

            # Step 5.8d: Append entry to income.csv
            with open("data/income.csv", "a", newline="") as file:
                writer = csv.writer(file)
                writer.writerow([
                    income.date,
                    income.amount,
                    income.category,
                    income.source,
                    income.description
                ])

            # Step 5.8e: Append entry to unified transactions.csv log
            with open("data/transactions.csv", "a", newline="") as file:
                writer = csv.writer(file)
                writer.writerow([
                    income.date,
                    "Income",
                    income.amount,
                    income.category,
                    income.description
                ])

            print("Income added successfully.")

        except ValueError:
            print("Please enter a valid amount.")

    # Step 5.9: Interactively collect expense inputs, category selection, and write to CSV logs.
    def add_expense(self):

        print("\n----- Add Expense -----")

        try:

            # Step 5.9a: Validate positive amount input
            amount = float(input("Enter expense amount: "))
            if amount <= 0:
                print("Amount must be greater than 0")
                return

            # Step 5.9b: Prompt category choice selection menu
            print("\nExpense Categories")
            print("1. Food")
            print("2. Transport")
            print("3. Shopping")
            print("4. Education")
            print("5. Medical")
            print("6. Bills")
            print("7. Entertainment")
            print("8. Other")

            category_choice = int(input("Select category: "))

            categories = {
                1: "Food",
                2: "Transport",
                3: "Shopping",
                4: "Education",
                5: "Medical",
                6: "Bills",
                7: "Entertainment",
                8: "Other"
            }

            if category_choice not in categories:
                print("Invalid category.")
                return

            category = categories[category_choice]

            # Step 5.9c: Read description and payment method
            description = input("Enter description: ")
            payment = input("Enter payment method (Cash/UPI/Card): ")

            # Step 5.9d: Construct Expense instance and append to in-memory list
            expense = Expense(
                amount,
                category,
                description,
                payment
            )
            self.expenses.append(expense)

            # Step 5.9e: Append entry to expenses.csv
            with open("data/expenses.csv", "a", newline="") as file:
                writer = csv.writer(file)
                writer.writerow([
                    expense.date,
                    expense.amount,
                    expense.category,
                    expense.payment,
                    expense.description
                ])

            # Step 5.9f: Append entry to unified transactions.csv log
            with open("data/transactions.csv", "a", newline="") as file:
                writer = csv.writer(file)
                writer.writerow([
                    expense.date,
                    "Expense",
                    expense.amount,
                    expense.category,
                    expense.description
                ])

            print("Expense added successfully.")

        except ValueError:
            print("Please enter valid input.")

    # Step 5.10: Print all loaded income records.
    def show_income(self):

        print("\n----- Income Records -----")

        if len(self.income) == 0:
            print("No income records found.")
            return

        for income in self.income:
            income.display()
            print("-" * 30)

    # Step 5.11: Print all loaded expense records.
    def show_expenses(self):

        print("\n----- Expense Records -----")

        if len(self.expenses) == 0:
            print("No expense records found.")
            return

        for expense in self.expenses:
            expense.display()
            print("-" * 30)

    # Step 5.12: Console prompt to set current month budget.
    def set_budget(self):

        try:

            budget = float(input("Enter monthly budget: "))

            if budget <= 0:
                print("Budget must be greater than 0.")
                return

            self.set_monthly_budget(datetime.now().strftime("%Y-%m"), budget)
            print("Monthly budget set successfully.")

        except ValueError:
            print("Please enter a valid budget.")

    # Step 5.13: Output currently loaded active budget amount.
    def show_budget(self):

        print("\n----- Monthly Budget -----")

        if self.budget == 0:
            print("Budget is not set.")
        else:
            print(f"Monthly Budget: Rs.{self.budget}")

    # Step 5.14: Calculate total sum of all income records in memory.
    def total_income(self):

        total = 0
        for income in self.income:
            total = total + income.amount
        return total

    # Step 5.15: Calculate total sum of all expense records in memory.
    def total_expense(self):

        total = 0
        for expense in self.expenses:
            total = total + expense.amount
        return total

    # Step 5.16: Group and sum expenses by category, optionally filtering by month.
    def category_wise_expense(self, month=None):

        print("\n----- Category Wise Expenses -----")

        if len(self.expenses) == 0:
            print("No expenses found.")
            return

        category_data = {}

        for expense in self.expenses:

            if month and not expense.date.startswith(month):
                continue

            category = expense.category
            if category in category_data:
                category_data[category] += expense.amount
            else:
                category_data[category] = expense.amount

        for category in category_data:
            print(f"{category}: Rs.{category_data[category]}")

    # Step 5.17: Print overall financial savings summary to console.
    def monthly_savings(self):

        print("\n----- Monthly Savings -----")

        income = self.total_income()
        expense = self.total_expense()
        savings = income - expense

        print(f"Total Income: Rs.{income}")
        print(f"Total Expense: Rs.{expense}")
        print(f"Savings: Rs.{savings}")

    # Step 5.18: Find and display the maximum expense record, filtered optionally by month.
    def highest_expense(self, month=None):

        print("\n----- Highest Expense -----")

        expenses = [expense for expense in self.expenses if not month or expense.date.startswith(month)]

        if len(expenses) == 0:
            print("No expenses found.")
            return

        highest = expenses[0]

        for expense in expenses:
            if expense.amount > highest.amount:
                highest = expense

        highest.display()

    # Step 5.19: Compare total expenses against the current active budget and report status.
    def budget_validation(self):

        print("\n----- Budget Validation -----")

        if self.budget == 0:
            print("Please set the budget first.")
            return

        expense = self.total_expense()

        print(f"Budget: Rs.{self.budget}")
        print(f"Total Expense: Rs.{expense}")

        if expense > self.budget:
            print("Warning: Budget exceeded.")
        else:
            remaining = self.budget - expense
            print("You are within the budget.")
            print(f"Remaining Budget: Rs.{remaining}")

    # Step 5.20: Read and display full transaction history log from data/transactions.csv.
    def transaction_history(self):

        print("\n----- Transaction History -----")

        try:

            with open("data/transactions.csv", "r") as file:

                reader = csv.DictReader(file)
                count = 0

                for row in reader:
                    count = count + 1
                    print(
                        f"{row['date']} | "
                        f"{row['type']} | "
                        f"Rs.{row['amount']} | "
                        f"{row['category']} | "
                        f"{row['description']}"
                    )

                if count == 0:
                    print("No transactions found.")

        except FileNotFoundError:
            print("Transaction file not found.")

