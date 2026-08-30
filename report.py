from datetime import datetime

class FinancialReport:
    """Monthly Financial Report"""

    def __init__(self, manager):
        self.manager = manager

    def monthly_report(self, month=None):

        print("\n")
        print("=" * 45)
        print("       MONTHLY FINANCIAL REPORT")
        print("=" * 45)

        month = month or datetime.now().strftime("%Y-%m")
        total_income = self.manager.monthly_income(month)
        total_expense = self.manager.monthly_expense(month)
        savings = self.manager.monthly_savings_value(month)
        budget = self.manager.budgets.get(month, self.manager.budget)

        print(f"Month          : {month}")
        print(f"Total Income   : Rs.{total_income}")
        print(f"Total Expense  : Rs.{total_expense}")
        print(f"Total Savings  : Rs.{savings}")
        print(f"Monthly Budget : Rs.{budget}")

        if budget == 0:
            print("Budget Status  : Budget not set")

        elif total_expense > budget:
            print("Budget Status  : Budget Exceeded")

        else:
            remaining = budget - total_expense

            print("Budget Status  : Within Budget")
            print(f"Remaining      : Rs.{remaining}")

        print("=" * 45)

    def summary(self):

        print("\n----- Financial Summary -----")

        print(
            f"Income Records  : "
            f"{len(self.manager.income)}"
        )

        print(
            f"Expense Records : "
            f"{len(self.manager.expenses)}"
        )
