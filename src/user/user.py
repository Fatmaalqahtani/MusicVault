import os
from getpass import getpass
from src.common.db_manager import (
    insert_file_metadata,
    get_files_by_user,
    update_file_metadata,
    get_file_by_id,
    get_all_files,
    get_user_credentials,
    register_user
)
from src.common.encryption import encrypt_file,generate_key
from src.common.integrity_check import generate_checksum

def print_menu():
    """Print the user portal menu."""
    print("\nUser Portal")
    print("1. Add Entry")
    print("2. View Own Entries")
    print("3. Modify Own Entry")
    print("4. View Others' Entries")
    print("5. Logout")

def add_entry(user_id):
    """Allow the user to add a new file entry."""
    file_path = input("Enter the path of the file to upload: ").strip()
    if not os.path.isfile(file_path):
        print(f"File '{file_path}' does not exist.")
        return

    file_name = os.path.basename(file_path)
    file_type = input("Enter file type (e.g., MP3, FLAC): ").strip().upper()

    # Generate or retrieve your encryption key
    key = generate_key()  # Generate a new key

    encrypted_file_path = encrypt_file(file_path, key)  # Encrypt the file and get the encrypted file path
    checksum = generate_checksum(file_path)  # Calculate checksum of the original file

    # Store the key securely if needed or handle encryption/decryption process properly
    # For demo purposes, we’re assuming the key is securely managed.

    file_id = insert_file_metadata(
        filename=file_name,
        file_type=file_type,
        checksum=checksum,
        encrypted_content=encrypted_file_path,  # Store path to the encrypted file
        owner_id=user_id,
        file_path=file_path
    )

    if file_id:
        print(f"File '{file_name}' added successfully with ID {file_id}.")
    else:
        print("Failed to add file.")

    
def view_own_entries(user_id):
    """Display all files uploaded by the user."""
    files = get_files_by_user(user_id)
    if files:
        print("Your Entries:")
        for file in files:
            print(f"ID: {file['id']}, Name: {file['file_name']}, Type: {file['file_type']}, Created At: {file['created_at']}")
    else:
        print("No entries found.")

def modify_own_entry(user_id):
    """Allow the user to modify details of their own file entry."""
    view_own_entries(user_id)
    file_id = int(input("Enter the ID of the file to modify: ").strip())

    file = get_file_by_id(file_id)
    if file and file['owner_id'] == user_id:
        new_file_name = input("Enter new file name (leave blank to keep current): ").strip()
        new_file_type = input("Enter new file type (leave blank to keep current): ").strip().upper()

        if new_file_name:
            file['file_name'] = new_file_name
        if new_file_type:
            file['file_type'] = new_file_type

        if update_file_metadata(file_id, file['file_name'], file['file_type']):
            print("File updated successfully.")
        else:
            print("Failed to update file.")
    else:
        print("File not found or you do not have permission to modify this file.")

def view_others_entries(user_id):
    """Display all files uploaded by other users."""
    files = get_all_files()
    if files:
        print("Entries by Others:")
        for file in files:
            if file['owner_id'] != user_id:  # Exclude the user's own files
                print(f"ID: {file['id']}, Name: {file['file_name']}, Type: {file['file_type']}, Owner ID: {file['owner_id']}, Created At: {file['created_at']}")
    else:
        print("No entries found.")


def login():
    """Handle user login."""
    username = input("Enter username: ").strip()
    password = getpass("Enter password: ").strip()
    user = get_user_credentials(username, password)
    if user:
        return user['id']
    else:
        print("Invalid credentials.")
        return None

def register():
    """Handle user registration."""
    username = input("Enter username: ").strip()
    password = getpass("Enter password: ").strip()
    role = 'User'  # Default role for new users

    existing_user = get_user_credentials(username, password)
    if existing_user:
        print("User already exists. Please log in.")
        return

    user_id = register_user(username, password, role)
    if user_id:
        print(f"User registered successfully with ID {user_id}.")
        return user_id
    else:
        print("Failed to register user.")
        return None

def user_portal():
    """Main function to run the user portal."""
    user_id = None
    while True:
        choice = input("Do you want to (L)ogin or (R)egister? (Enter 'L' or 'R'): ").strip().upper()
        if choice == 'L':
            user_id = login()
            if user_id:
                break
        elif choice == 'R':
            user_id = register()
            if user_id:
                break
        else:
            print("Invalid choice. Please enter 'L' for Login or 'R' for Register.")

    while True:
        print_menu()
        choice = input("Enter choice: ").strip()
        if choice == '1':
            add_entry(user_id)
        elif choice == '2':
            view_own_entries(user_id)
        elif choice == '3':
            modify_own_entry(user_id)
        elif choice == '4':
            view_others_entries(user_id)  # Pass user_id here
        elif choice == '5':
            print("Logging out...")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    user_portal()