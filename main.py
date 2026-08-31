# Step 1: Import required manager and reporting modules.
from finance import FinanceManager
from report import FinancialReport

# Step 2: Define a dictionary containing the menu option numbers and titles.
menu_options = {
    1: "Add Income",
    2: "Add Expense",
    3: "View Income",
    4: "View Expenses",
    5: "Set Monthly Budget",
    6: "View Monthly Budget",
    7: "Budget Validation",
    8: "Transaction History",
    9: "Category Wise Expenses",
    10: "Monthly Savings",
    11: "Highest Expense",
    12: "Monthly Financial Report",
    13: "Financial Summary",
    14: "Exit",
}


# Step 2.1: Define a function to render the CLI options menu dynamically from the dictionary.
def menu():
    """Display the interactive personal finance console menu using the dictionary."""
    print("\n")
    print("=" * 45)
    print(" PERSONAL FINANCE MANAGEMENT SYSTEM")
    print("=" * 45)

    # Loop through the dictionary items to display menu options step-by-step
    for option_number, option_name in menu_options.items():
        print(f"{option_number}. {option_name}")

    print("=" * 45)



# Step 3: Instantiate core manager and report objects.
# - FinanceManager initializes CSV storage files and loads existing transactions.
# - FinancialReport uses the FinanceManager instance to generate summaries.
manager = FinanceManager()
report = FinancialReport(manager)


# Step 4: Start the main interactive application loop.
while True:

    # Step 4.1: Display the numbered menu options to the user.
    menu()

    try:

        # Step 4.2: Prompt the user for numerical menu choice input.
        choice = int(input("Enter your choice: "))

        # Step 4.3: Route the selected menu choice to the appropriate handler method.
        if choice == 1:
            # Prompt user to record a new income transaction
            manager.add_income()

        elif choice == 2:
            # Prompt user to record a new expense transaction
            manager.add_expense()

        elif choice == 3:
            # Display all recorded income entries
            manager.show_income()

        elif choice == 4:
            # Display all recorded expense entries
            manager.show_expenses()

        elif choice == 5:
            # Prompt user to set a monthly budget threshold
            manager.set_budget()

        elif choice == 6:
            # Display the currently configured monthly budget
            manager.show_budget()

        elif choice == 7:
            # Compare spending against the configured budget to check limit status
            manager.budget_validation()

        elif choice == 8:
            # Output complete history log of all recorded transactions
            manager.transaction_history()

        elif choice == 9:
            # Aggregate and display total expenses categorized by type
            manager.category_wise_expense()

        elif choice == 10:
            # Calculate and display net savings (Total Income - Total Expenses)
            manager.monthly_savings()

        elif choice == 11:
            # Locate and display the transaction with the highest expense amount
            manager.highest_expense()

        elif choice == 12:
            # Render detailed monthly breakdown report of income, expense, and budget status
            report.monthly_report()

        elif choice == 13:
            # Render overview summary count of income and expense records
            report.summary()

        elif choice == 14:
            # Gracefully exit the CLI program loop
            print("Thank you for using the system.")
            break

        else:
            # Handle out-of-range option choices
            print("Please select a number from 1 to 14.")

    except ValueError:
        # Handle non-integer input errors safely without crashing
        print("Please enter a valid number.")

    except Exception as error:
        # Catch and report any unexpected errors during operation execution
        print("Something went wrong:", error)
