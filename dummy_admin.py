import mysql.connector
import bcrypt
from mysql.connector import Error
import config

def create_connection():
    """Create and return a database connection."""
    try:
        conn = mysql.connector.connect(
            host=config.DB_HOST,
            user=config.DB_USER,
            password=config.DB_PASSWORD
        )
        if conn.is_connected():
            print("Database connection established.")
            return conn
    except Error as e:
        print(f"Error: '{e}'")
        return None

def create_database(conn):
    """Create the database if it does not exist."""
    try:
        cursor = conn.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {config.DB_NAME}")
        print(f"Database '{config.DB_NAME}' created or already exists.")
    except Error as e:
        print(f"Error: '{e}'")

def create_tables(conn):
    """Create tables in the database."""
    try:
        conn.database = config.DB_NAME
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS Users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(255) NOT NULL UNIQUE,
            password_hash VARCHAR(255) NOT NULL,
            role ENUM('Admin', 'User') NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        )
        """)
        print("Users table created or already exists.")
    except Error as e:
        print(f"Error: '{e}'")

def admin_exists(conn):
    """Check if the admin already exists in the Users table."""
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT COUNT(*) as count FROM Users WHERE username = %s AND role = 'Admin'", ('root',))
        result = cursor.fetchone()
        return result['count'] > 0
    except Error as e:
        print(f"Error: '{e}'")
        return False
    finally:
        cursor.close()

def add_dummy_admin():
    """Add a dummy admin to the Users table if it does not already exist."""
    conn = create_connection()
    if conn:
        create_database(conn)
        create_tables(conn)
        
        if admin_exists(conn):
            print("Dummy admin already exists. No changes made.")
            conn.close()
            return
        
        # Define admin credentials
        username = 'root'
        password = '1234'
        
        # Hash the password
        hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode('utf-8')
        
        try:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT INTO Users (username, password_hash, role)
            VALUES (%s, %s, 'Admin')
            """, (username, hashed_password))
            
            conn.commit()
            print(f"Dummy admin '{username}' added to the database.")
        except Error as e:
            print(f"Error: '{e}'")
        finally:
            cursor.close()
            conn.close()

if __name__ == "__main__":
    add_dummy_admin()
