from datetime import datetime
from logger_config import get_logger

logger = get_logger("report")


# Step 2: Define the FinancialReport class to generate formatted financial statements.
class FinancialReport:
    """Monthly Financial Report helper class."""

    # Step 2.1: Initialize report generator with reference to a FinanceManager instance.
    def __init__(self, manager):
        self.manager = manager

    # Step 2.2: Generate and print a comprehensive report for a given month (YYYY-MM).
    def monthly_report(self, month=None):

        # Step 2.2a: Default to current month string (YYYY-MM) if no specific month is passed.
        month = month or datetime.now().strftime("%Y-%m")
        logger.info(f"Generating monthly financial report for: {month}")

        print("\n")
        print("=" * 45)
        print("       MONTHLY FINANCIAL REPORT")
        print("=" * 45)

        # Step 2.2b: Retrieve aggregated metrics for the specified month from the manager.
        total_income = self.manager.monthly_income(month)
        total_expense = self.manager.monthly_expense(month)
        savings = self.manager.monthly_savings_value(month)
        budget = self.manager.budgets.get(month, self.manager.budget)

        # Step 2.2c: Display basic financial totals.
        print(f"Month          : {month}")
        print(f"Total Income   : Rs.{total_income}")
        print(f"Total Expense  : Rs.{total_expense}")
        print(f"Total Savings  : Rs.{savings}")
        print(f"Monthly Budget : Rs.{budget}")

        # Step 2.2d: Evaluate budget status based on total expenses versus budget threshold.
        if budget == 0:
            print("Budget Status  : Budget not set")

        elif total_expense > budget:
            print("Budget Status  : Budget Exceeded")

        else:
            remaining = budget - total_expense

            print("Budget Status  : Within Budget")
            print(f"Remaining      : Rs.{remaining}")

        print("=" * 45)

    # Step 2.3: Display total transaction count summary across all stored records.
    def summary(self):

        print("\n----- Financial Summary -----")

        # Output overall count of loaded income entries
        print(
            f"Income Records  : "
            f"{len(self.manager.income)}"
        )

        # Output overall count of loaded expense entries
        print(
            f"Expense Records : "
            f"{len(self.manager.expenses)}"
        )

