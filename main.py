from finance import FinanceManager
from report import FinancialReport


def menu():

    print("\n")
    print("=" * 45)
    print(" PERSONAL FINANCE MANAGEMENT SYSTEM")
    print("=" * 45)

    print("1. Add Income")
    print("2. Add Expense")
    print("3. View Income")
    print("4. View Expenses")
    print("5. Set Monthly Budget")
    print("6. View Monthly Budget")
    print("7. Budget Validation")
    print("8. Transaction History")
    print("9. Category Wise Expenses")
    print("10. Monthly Savings")
    print("11. Highest Expense")
    print("12. Monthly Financial Report")
    print("13. Financial Summary")
    print("14. Exit")

    print("=" * 45)


manager = FinanceManager()
report = FinancialReport(manager)


while True:

    menu()

    try:

        choice = int(input("Enter your choice: "))

        if choice == 1:
            manager.add_income()

        elif choice == 2:
            manager.add_expense()

        elif choice == 3:
            manager.show_income()

        elif choice == 4:
            manager.show_expenses()

        elif choice == 5:
            manager.set_budget()

        elif choice == 6:
            manager.show_budget()

        elif choice == 7:
            manager.budget_validation()

        elif choice == 8:
            manager.transaction_history()

        elif choice == 9:
            manager.category_wise_expense()

        elif choice == 10:
            manager.monthly_savings()

        elif choice == 11:
            manager.highest_expense()

        elif choice == 12:
            report.monthly_report()

        elif choice == 13:
            report.summary()

        elif choice == 14:
            print("Thank you for using the system.")
            break

        else:
            print("Please select a number from 1 to 14.")

    except ValueError:
        print("Please enter a valid number.")

    except Exception as error:
        print("Something went wrong:", error)