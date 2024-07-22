from configparser import Error
import os
import getpass
from src.common.db_manager import (
    insert_file_metadata, 
    delete_file_metadata, 
    insert_log, 
    get_admin_credentials, 
    get_all_files, 
    get_all_logs,
    insert_integrity_check,
    create_connection
)
from src.common.encryption import encrypt_file, generate_key
from src.common.integrity_check import generate_checksum
from src.common.auth import verify_password
import config

def admin_login():
    """Handle admin login."""
    username = input("Enter admin username: ")
    password = getpass.getpass("Enter admin password: ")
    
    admin = get_admin_credentials(username)
    if admin and verify_password(admin['password_hash'], password):
        print("Login successful")
        return admin['id']  # Return admin ID
    else:
        print("Login failed")
        return None

def create_entry(admin_id):
    print("Creating a new entry...")

    file_path = input("Enter the path of the file to upload: ")
    if not os.path.isfile(file_path):
        print("File does not exist. Please try again.")
        return

    file_type = input("Enter file type (MP3, FLAC): ")
    
    checksum = generate_checksum(file_path)
    key = generate_key()
    encrypted_file_path = encrypt_file(file_path, key)

    with open(encrypted_file_path, 'rb') as file:
        encrypted_content = file.read()

    owner_id = admin_id  # Admin is the owner of the file
    file_id = insert_file_metadata(
        filename=os.path.basename(file_path),
        file_type=file_type,
        checksum=checksum,
        encrypted_content=encrypted_content,
        owner_id=owner_id,
        file_path=os.path.basename(file_path)  # Save the file name or path relative to the files directory
    )
    
    if file_id:
        insert_log("Created file", admin_id, file_id)
        print("Entry created and logged successfully.")
    else:
        print("Failed to create entry.")


def delete_file(admin_id):
    """Delete a file entry and log the action."""
    print("Deleting a data file...")
    
    files = get_all_files()
    if not files:
        print("No files available for deletion.")
        return
    
    print("\nAvailable files:")
    for file in files:
        print(f"ID: {file['id']}, Name: {file['file_name']}, Type: {file['file_type']}, Owner ID: {file['owner_id']}, Created At: {file['created_at']}")

    file_id = input("Enter the ID of the file to delete: ")
    
    if not any(file['id'] == int(file_id) for file in files):
        print("Invalid file ID. Please try again.")
        return

    delete_file_metadata(file_id)
    insert_log("Deleted file", admin_id, file_id)
    print("File deleted and action logged successfully.")

def generate_audit_log():
    """Generate and display the audit log."""
    print("Generating audit log...")
    
    logs = get_all_logs()
    if not logs:
        print("No audit logs available.")
        return
    
    print("\nAudit Logs:")
    for log in logs:
        print(f"ID: {log['id']}, Action: {log['action']}, User ID: {log['user_id']}, File ID: {log['file_id']}, Timestamp: {log['timestamp']}")

def generate_integrity_check():
    """Generate and update integrity checks for a selected file."""
    print("Generating integrity check...")
    
    conn = create_connection()
    if not conn:
        print("Failed to connect to the database.")
        return
    
    try:
        conn.database = config.DB_NAME
        cursor = conn.cursor()
        
        # Step 1: Retrieve existing checksums from the database
        cursor.execute("SELECT file_id, checksum FROM IntegrityChecks")
        existing_checksums = dict(cursor.fetchall())  # {file_id: checksum}
        
        # Step 2: Get all files from the Files table
        cursor.execute("SELECT id, file_name, file_path FROM Files")
        files = cursor.fetchall()
        
        if not files:
            print("No files available for integrity check.")
            return
        
        # Step 3: Display files and prompt user for selection
        print("\nAvailable files:")
        for file in files:
            print(f"ID: {file[0]}, Name: {file[1]}")
        
        file_id = input("Enter the ID of the file to check its integrity: ")
        
        # Find the selected file
        selected_file = next((file for file in files if file[0] == int(file_id)), None)
        
        if not selected_file:
            print("Invalid file ID. Please try again.")
            return
        
        # Extract file details
        file_id, file_name, file_path = selected_file
        
        # Construct the full file path using the file path from the database
        file_full_path = file_path  # Assuming file_path from database is the correct full path
        
        # Print the full path for debugging
        print(f"Checking file at path: {file_full_path}")
        
        if not os.path.isfile(file_full_path):
            print(f"File '{file_name}' does not exist at path '{file_full_path}'.")
            return
        
        # Generate checksum
        current_checksum = generate_checksum(file_full_path)
        
        # Retrieve the old checksum from the hashmap
        old_checksum = existing_checksums.get(file_id)
        
        # Check if the checksum has changed
        if old_checksum != current_checksum:
            print(f"Integrity check for file ID {file_id} and file '{file_name}' updated.")
            # Update the checksum in the database
            insert_integrity_check(file_id, current_checksum)
        else:
            print(f"File ID {file_id} and file '{file_name}' checksum is unchanged.")
    
    except Error as e:
        print(f"Error: '{e}'")
    
    finally:
        conn.close()


        
def admin_portal():
    """Main admin portal function."""
    admin_id = admin_login()
    if not admin_id:
        return

    while True:
        print("\nAdmin Portal")
        print("1. Create Entry")
        print("2. Delete File")
        print("3. Generate Audit Log")
        print("4. Generate Integrity Check")
        print("5. Logout")

        choice = input("Enter choice: ")

        if choice == '1':
            create_entry(admin_id)
        elif choice == '2':
            delete_file(admin_id)
        elif choice == '3':
            generate_audit_log()
        elif choice == '4':
            generate_integrity_check()
        elif choice == '5':
            print("Logging out...")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    admin_portal()
