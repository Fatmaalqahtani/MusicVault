from hashlib import sha256
import mysql.connector
from mysql.connector import Error
import config

def create_connection():
    """Create and return a connection to the database."""
    try:
        conn = mysql.connector.connect(
            host=config.DB_HOST,
            user=config.DB_USER,
            password=config.DB_PASSWORD,
            database=config.DB_NAME
        )
        if conn.is_connected():
            return conn
    except Error as e:
        print(f"Error: '{e}'")
        return None

def insert_file_metadata(filename, file_type, checksum, encrypted_content, owner_id, file_path):
    """Insert file metadata into the database and return the file ID."""
    try:
        conn = create_connection()
        if conn:
            cursor = conn.cursor()
            query = """
            INSERT INTO Files (file_name, file_type, checksum, encrypted_content, owner_id, file_path)
            VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query, (filename, file_type, checksum, encrypted_content, owner_id, file_path))
            conn.commit()
            file_id = cursor.lastrowid
            conn.close()
            return file_id
    except Error as e:
        print(f"Error: '{e}'")
        return None


def get_all_files():
    """Retrieve all files from the database."""
    try:
        conn = create_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT id, file_name, file_path, file_type, owner_id, created_at FROM Files")
            files = cursor.fetchall()
            conn.close()
            return files
    except Error as e:
        print(f"Error: '{e}'")
        return []

def get_admin_credentials(username):
    """Retrieve admin credentials based on username."""
    try:
        conn = create_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM Users WHERE username = %s AND role = 'Admin'", (username,))
            admin = cursor.fetchone()
            conn.close()
            return admin
    except Error as e:
        print(f"Error: '{e}'")
        return None

def register_user(username, password, role):
    """Register a new user in the database."""
    try:
        conn = create_connection()
        if conn:
            cursor = conn.cursor()
            password_hash = sha256(password.encode()).hexdigest()
            query = """
            INSERT INTO Users (username, password_hash, role)
            VALUES (%s, %s, %s)
            """
            cursor.execute(query, (username, password_hash, role))
            conn.commit()
            user_id = cursor.lastrowid
            conn.close()
            return user_id
    except Error as e:
        print(f"Error: '{e}'")
        return None

def get_user_credentials(username, password):
    """Retrieve user credentials based on username and password."""
    try:
        conn = create_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            password_hash = sha256(password.encode()).hexdigest()
            query = "SELECT id FROM Users WHERE username = %s AND password_hash = %s"
            cursor.execute(query, (username, password_hash))
            user = cursor.fetchone()
            conn.close()
            return user
    except Error as e:
        print(f"Error: '{e}'")
        return None
    
def insert_log(action, user_id, file_id):
    """Insert a log entry into the database."""
    try:
        conn = create_connection()
        if conn:
            cursor = conn.cursor()
            query = """
            INSERT INTO Logs (action, user_id, file_id)
            VALUES (%s, %s, %s)
            """
            cursor.execute(query, (action, user_id, file_id))
            conn.commit()
            conn.close()
    except Error as e:
        print(f"Error: '{e}'")

def delete_file_metadata(file_id):
    """Delete file metadata from the database."""
    try:
        conn = create_connection()
        if conn:
            cursor = conn.cursor()
            query = "DELETE FROM Files WHERE id = %s"
            cursor.execute(query, (file_id,))
            conn.commit()
            conn.close()
    except Error as e:
        print(f"Error: '{e}'")

def get_all_logs():
    """Retrieve all logs from the database."""
    try:
        conn = create_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            query = "SELECT * FROM Logs"
            cursor.execute(query)
            logs = cursor.fetchall()
            conn.close()
            return logs
    except Error as e:
        print(f"Error: '{e}'")
        return []

def insert_integrity_check(file_id, checksum):
    """Insert or update an integrity check record in the database."""
    try:
        conn = create_connection()
        if conn:
            cursor = conn.cursor()
            query = """
            INSERT INTO IntegrityChecks (file_id, checksum)
            VALUES (%s, %s)
            ON DUPLICATE KEY UPDATE checksum = VALUES(checksum), checked_at = CURRENT_TIMESTAMP
            """
            cursor.execute(query, (file_id, checksum))
            conn.commit()
            print(f"Integrity check for file ID {file_id} inserted/updated successfully.")
    except Error as e:
        print(f"Error: '{e}'")
    finally:
        conn.close()

def update_file_metadata(file_id, new_file_name, new_file_type):
    """Update the file metadata in the database."""
    try:
        conn = create_connection()
        if conn:
            cursor = conn.cursor()
            query = """
            UPDATE Files
            SET file_name = %s, file_type = %s
            WHERE id = %s
            """
            cursor.execute(query, (new_file_name, new_file_type, file_id))
            conn.commit()
            affected_rows = cursor.rowcount
            conn.close()
            return affected_rows > 0
    except Error as e:
        print(f"Error: '{e}'")
        return False
 
def get_files_by_user(user_id):
    """Retrieve all files associated with a specific user."""
    try:
        conn = create_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            query = """
            SELECT id, file_name, file_type, checksum, created_at, file_path
            FROM Files
            WHERE owner_id = %s
            """
            cursor.execute(query, (user_id,))
            files = cursor.fetchall()
            conn.close()
            return files
    except Error as e:
        print(f"Error: '{e}'")
        return []

def get_file_by_id(file_id):
    """Retrieve file metadata by file ID."""
    try:
        conn = create_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            query = """
            SELECT id, file_name, file_type, checksum, encrypted_content, owner_id, created_at, file_path
            FROM Files
            WHERE id = %s
            """
            cursor.execute(query, (file_id,))
            file = cursor.fetchone()
            conn.close()
            return file
    except Error as e:
        print(f"Error: '{e}'")
        return None
    