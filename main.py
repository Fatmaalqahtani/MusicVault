from src.cli.cli import main as cli_main
from dummy_admin import add_dummy_admin
from initialize_db import main as init_db_main
from src.admin.admin import admin_portal
from src.user.user import user_portal  # Import the correct function

def main():
    # Initialize the database and add dummy admin if needed
    init_db_main()
    add_dummy_admin()

    # Prompt for user role
    role = input("Do you want to run the application as User or Admin? (Enter 'user' or 'admin'): ").strip().lower()

    if role == 'admin':
        print("Starting Admin Portal...")
        admin_portal()
    elif role == 'user':
        print("Starting User Portal...")
        user_portal()  # Call the user portal function
    else:
        print("Invalid choice. Please enter 'user' or 'admin'.")

if __name__ == "__main__":
    main()
