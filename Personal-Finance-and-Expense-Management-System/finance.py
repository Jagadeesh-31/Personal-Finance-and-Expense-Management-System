import csv
import os
from datetime import datetime


class Transaction:
    """Transaction details"""

    def __init__(self, amount, category, description):
        self.amount = amount
        self.category = category
        self.description = description
        self.date = datetime.now().strftime("%Y-%m-%d")

    def display(self):
        print(f"Date: {self.date}")
        print(f"Amount: {self.amount}")
        print(f"Category: {self.category}")
        print(f"Description: {self.description}")


class Income(Transaction):
    """Income details"""

    def __init__(self, amount, category, description, source):
        super().__init__(amount, category, description)
        self.source = source

    def display(self):
        print(f"Date: {self.date}")
        print(f"Income: Rs.{self.amount}")
        print(f"Category: {self.category}")
        print(f"Source: {self.source}")
        print(f"Description: {self.description}")


class Expense(Transaction):
    """Expense details"""

    def __init__(self, amount, category, description, payment):
        super().__init__(amount, category, description)
        self.payment = payment

    def display(self):
        print(f"Date: {self.date}")
        print(f"Expense: Rs.{self.amount}")
        print(f"Category: {self.category}")
        print(f"Payment: {self.payment}")
        print(f"Description: {self.description}")


class FinanceManager:
    """Personal Finance Management"""

    def __init__(self):
        self.income = []
        self.expenses = []
        self.budget = 0
        self.budgets = {}

        self.create_files()
        self.load_data()

    def create_files(self):

        if not os.path.exists("data"):
            os.mkdir("data")

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

        if not os.path.exists("data/budgets.csv"):
            with open("data/budgets.csv", "w", newline="") as file:
                writer = csv.writer(file)
                writer.writerow(["month", "amount"])

    def load_data(self):

        try:

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

            with open("data/budgets.csv", "r") as file:
                reader = csv.DictReader(file)
                for row in reader:
                    self.budgets[row["month"]] = float(row["amount"])

            current_month = datetime.now().strftime("%Y-%m")
            self.budget = self.budgets.get(current_month, 0)

        except FileNotFoundError:
            print("Data files are not available.")

        except Exception as error:
            print("Error while loading data:", error)

    def monthly_income(self, month):
        """Return income recorded in YYYY-MM month."""
        return sum(item.amount for item in self.income if item.date.startswith(month))

    def monthly_expense(self, month):
        """Return expenses recorded in YYYY-MM month."""
        return sum(item.amount for item in self.expenses if item.date.startswith(month))

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

    def monthly_savings_value(self, month):
        return self.monthly_income(month) - self.monthly_expense(month)

    def add_income(self):

        print("\n----- Add Income -----")

        try:

            amount = float(input("Enter income amount: "))
            if amount <= 0:
                raise ValueError("Amount must be greater than zero")

            if amount <= 0:
                print("Amount must be greater than 0")
                return

            source = input("Enter income source: ")
            category = input("Enter income category: ")
            description = input("Enter description: ")

            income = Income(
                amount,
                category,
                description,
                source
            )

            self.income.append(income)

            with open("data/income.csv", "a", newline="") as file:
                writer = csv.writer(file)

                writer.writerow([
                    income.date,
                    income.amount,
                    income.category,
                    income.source,
                    income.description
                ])

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

    def add_expense(self):

        print("\n----- Add Expense -----")

        try:

            amount = float(input("Enter expense amount: "))

            if amount <= 0:
                print("Amount must be greater than 0")
                return

            print("\nExpense Categories")
            print("1. Food")
            print("2. Transport")
            print("3. Shopping")
            print("4. Education")
            print("5. Medical")
            print("6. Bills")
            print("7. Entertainment")
            print("8. Other")

            category_choice = int(
                input("Select category: ")
            )

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

            description = input("Enter description: ")
            payment = input(
                "Enter payment method (Cash/UPI/Card): "
            )

            expense = Expense(
                amount,
                category,
                description,
                payment
            )

            self.expenses.append(expense)

            with open("data/expenses.csv", "a", newline="") as file:
                writer = csv.writer(file)

                writer.writerow([
                    expense.date,
                    expense.amount,
                    expense.category,
                    expense.payment,
                    expense.description
                ])

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

    def show_income(self):

        print("\n----- Income Records -----")

        if len(self.income) == 0:
            print("No income records found.")
            return

        for income in self.income:
            income.display()
            print("-" * 30)

    def show_expenses(self):

        print("\n----- Expense Records -----")

        if len(self.expenses) == 0:
            print("No expense records found.")
            return

        for expense in self.expenses:
            expense.display()
            print("-" * 30)

    def set_budget(self):

        try:

            budget = float(
                input("Enter monthly budget: ")
            )

            if budget <= 0:
                print("Budget must be greater than 0.")
                return

            self.set_monthly_budget(datetime.now().strftime("%Y-%m"), budget)

            print("Monthly budget set successfully.")

        except ValueError:
            print("Please enter a valid budget.")

    def show_budget(self):

        print("\n----- Monthly Budget -----")

        if self.budget == 0:
            print("Budget is not set.")
        else:
            print(f"Monthly Budget: Rs.{self.budget}")

    def total_income(self):

        total = 0

        for income in self.income:
            total = total + income.amount

        return total

    def total_expense(self):

        total = 0

        for expense in self.expenses:
            total = total + expense.amount

        return total

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
            print(
                f"{category}: Rs.{category_data[category]}"
            )

    def monthly_savings(self):

        print("\n----- Monthly Savings -----")

        income = self.total_income()
        expense = self.total_expense()

        savings = income - expense

        print(f"Total Income: Rs.{income}")
        print(f"Total Expense: Rs.{expense}")
        print(f"Savings: Rs.{savings}")

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

    def transaction_history(self):

        print("\n----- Transaction History -----")

        try:

            with open(
                "data/transactions.csv",
                "r"
            ) as file:

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
