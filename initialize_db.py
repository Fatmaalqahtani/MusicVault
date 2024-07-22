import mysql.connector
from mysql.connector import Error
import config

def create_connection():
    """Establish a connection to the MySQL server."""
    try:
        conn = mysql.connector.connect(
            host=config.DB_HOST,
            user=config.DB_USER,
            password=config.DB_PASSWORD
        )
        if conn.is_connected():
            print("Connection established")
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
    """Create tables in the database if they do not exist."""
    try:
        conn.database = config.DB_NAME
        cursor = conn.cursor()

        # Create Users table
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

        # Create Files table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS Files (
            id INT AUTO_INCREMENT PRIMARY KEY,
            file_name VARCHAR(255) NOT NULL,
            file_type VARCHAR(50) NOT NULL,
            checksum VARCHAR(64) NOT NULL,
            encrypted_content LONGBLOB NOT NULL,
            owner_id INT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            file_path VARCHAR(255) NOT NULL,
            FOREIGN KEY (owner_id) REFERENCES Users(id)
        )
        """)

        # Create Logs table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS Logs (
            id INT AUTO_INCREMENT PRIMARY KEY,
            action TEXT NOT NULL,
            user_id INT NOT NULL,
            file_id INT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES Users(id),
            FOREIGN KEY (file_id) REFERENCES Files(id)
        )
        """)

        # Create IntegrityChecks table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS IntegrityChecks (
            id INT AUTO_INCREMENT PRIMARY KEY,
            file_id INT NOT NULL,
            checksum VARCHAR(255) NOT NULL,
            checked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (file_id) REFERENCES Files(id)
        )
        """)

        print("Tables created successfully.")
    except Error as e:
        print(f"Error: '{e}'")
    finally:
        conn.close()

def main():
    """Main function to set up the database and tables."""
    conn = create_connection()
    if conn:
        create_database(conn)
        create_tables(conn)
        conn.close()

if __name__ == "__main__":
    main()
