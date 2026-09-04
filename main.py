from finance import FinanceManager
from report import FinancialReport
from logger_config import get_logger
from auth import UserManager

logger = get_logger("main")
logger.info("Initializing Personal Finance Management Console System...")

auth_manager = UserManager()


def authenticate_cli_user() -> str:
    """Prompt user for Login, Signup, Forgot Password, or Guest mode in CLI."""
    print("=" * 45)
    print(" WELCOME TO PERSONAL FINANCE MANAGEMENT SYSTEM")
    print("=" * 45)
    print("1. Log In")
    print("2. Sign Up")
    print("3. Forgot Password (OTP Reset)")
    print("4. Continue as Guest")
    print("=" * 45)

    while True:
        choice = input("Select Option (1-4): ").strip()
        if choice == "1":
            username = input("Username: ").strip()
            password = input("Password: ").strip()
            success, msg, user_info = auth_manager.login(username, password)
            if success:
                display_name = user_info.get("full_name") or username
                print(f"\nWelcome back, {display_name}!")
                return username
            else:
                print(f"\nLogin Failed: {msg}\n")
        elif choice == "2":
            username = input("Desired Username: ").strip()
            full_name = input("Full Name: ").strip()
            email = input("Email: ").strip()
            password = input("Password: ").strip()
            success, msg = auth_manager.signup(username, password, full_name, email)
            if success:
                print(f"\n{msg} You can now log in.")
            else:
                print(f"\nSignup Failed: {msg}\n")
        elif choice == "3":
            print("\n--- FORGOT PASSWORD / OTP RESET ---")
            identifier = input("Enter your Username or Email: ").strip()
            success, msg, target_user = auth_manager.request_password_reset_otp(identifier)
            if not success:
                print(f"\n{msg}\n")
            else:
                print(f"\n{msg}")
                otp_code = input("Enter 6-digit OTP received in email: ").strip()
                new_pass = input("Enter New Password: ").strip()
                res_ok, res_msg = auth_manager.verify_otp_and_reset_password(target_user, otp_code, new_pass)
                if res_ok:
                    print(f"\nSUCCESS: {res_msg}\n")
                else:
                    print(f"\nRESET FAILED: {res_msg}\n")
        elif choice == "4":
            print("\nContinuing in Guest mode...")
            return "default"
        else:
            print("Please select 1, 2, 3, or 4.")


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
    print(f" PERSONAL FINANCE MANAGEMENT SYSTEM ({current_username.upper()})")
    print("=" * 45)

    # Loop through the dictionary items to display menu options step-by-step
    for option_number, option_name in menu_options.items():
        print(f"{option_number}. {option_name}")

    print("=" * 45)


# Step 3: Authenticate user and instantiate core manager and report objects.
current_username = authenticate_cli_user()
manager = FinanceManager(username=current_username)
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
        logger.warning("Invalid non-integer menu choice entered.")
        print("Please enter a valid number.")

    except Exception as error:
        # Catch and report any unexpected errors during operation execution
        logger.error(f"Unexpected error in CLI loop: {error}", exc_info=True)
        print("Something went wrong:", error)

