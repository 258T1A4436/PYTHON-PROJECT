"""
=============================================================================
Module: db.py
Description: Database connection and initialization helper for MySQL.
Features automatic table creation, initial data seeding, and smart password
fallback detection for beginner ease-of-use.
=============================================================================
"""
import os
import mysql.connector
from mysql.connector import Error

# Database connection configuration settings
# Adjust 'user' and 'password' according to your local MySQL installation
DB_CONFIG = {
    'host': os.environ.get('DB_HOST', 'localhost'),
    'user': os.environ.get('DB_USER', 'root'),
    'password': os.environ.get('DB_PASSWORD', ''),
    'database': os.environ.get('DB_NAME', 'library_management'),
    'port': int(os.environ.get('DB_PORT', '3306'))
}

# Common default passwords used in student/developer environments for auto-detection fallback
COMMON_PASSWORDS = ['', 'root', 'admin', 'password', '1234', '123456', 'root123', 'admin123', 'mysql']


def _find_working_password(target_db=None):
    """
    Attempts to connect using the configured password. If access is denied (1045),
    tries common passwords to automatically establish a connection.
    """
    # First, try user-specified password
    passwords_to_try = [DB_CONFIG['password']] + [p for p in COMMON_PASSWORDS if p != DB_CONFIG['password']]

    for pwd in passwords_to_try:
        try:
            kwargs = {
                'host': DB_CONFIG['host'],
                'user': DB_CONFIG['user'],
                'password': pwd,
                'port': DB_CONFIG['port']
            }
            if target_db:
                kwargs['database'] = target_db

            conn = mysql.connector.connect(**kwargs)
            if pwd != DB_CONFIG['password']:
                DB_CONFIG['password'] = pwd
                print(f"[Database] Auto-detected working MySQL password: '{pwd}'")
            return conn
        except Error as err:
            # Error 1045 is 'Access denied for user'
            if err.errno == 1045:
                continue
            # If database doesn't exist yet (1049) when connecting with target_db, break to handle later
            if err.errno == 1049:
                return None
            print(f"[Database Warning] {err}")
            return None

    return None


def get_db_connection():
    """
    Establishes and returns a connection to the 'library_management' MySQL database.
    """
    conn = _find_working_password(target_db=DB_CONFIG['database'])
    if conn:
        return conn

    # If connection failed, show helpful tips
    print(f"\n[Database Error] Could not connect to MySQL database '{DB_CONFIG['database']}'.")
    print("1. Ensure MySQL Server is running (e.g., XAMPP Control Panel -> Start MySQL).")
    print("2. If your MySQL server has a password, open db.py and set 'password' in DB_CONFIG.\n")
    return None


def init_db():
    """
    Automatically creates the 'library_management' database, 'books' table,
    and 'users' table if they do not already exist.
    """
    try:
        # Step 1: Connect to server without database to create library_management
        server_conn = _find_working_password(target_db=None)
        if not server_conn:
            print("[Database Warning] Unable to connect to MySQL server to check/create database.")
            return False

        cursor = server_conn.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_CONFIG['database']};")
        cursor.close()
        server_conn.close()

        # Step 2: Connect to database to verify/create tables
        conn = get_db_connection()
        if conn and conn.is_connected():
            cursor = conn.cursor()

            # 1. Create books table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS books (
                id INT AUTO_INCREMENT PRIMARY KEY,
                title VARCHAR(200) NOT NULL,
                author VARCHAR(100) NOT NULL,
                category VARCHAR(100) NOT NULL,
                quantity INT NOT NULL DEFAULT 1
            );
            """)

            # 2. Create users table for Authentication
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) NOT NULL UNIQUE,
                password VARCHAR(64) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """)

            # 3. Seed starter demo books if empty
            cursor.execute("SELECT COUNT(*) FROM books;")
            if cursor.fetchone()[0] == 0:
                sample_books = [
                    ('Introduction to Algorithms', 'Thomas H. Cormen', 'Computer Science', 5),
                    ('Clean Code', 'Robert C. Martin', 'Software Engineering', 3),
                    ('Operating System Concepts', 'Abraham Silberschatz', 'Computer Science', 4),
                    ('Database System Concepts', 'Abraham Silberschatz', 'Database Systems', 6),
                    ('Computer Networks', 'Andrew S. Tanenbaum', 'Networking', 2)
                ]
                cursor.executemany("INSERT INTO books (title, author, category, quantity) VALUES (%s, %s, %s, %s);", sample_books)
                conn.commit()
                print("[Database] Initial sample books seeded successfully.")

            # 4. Seed default admin user if users table is empty
            # Default username: admin, password: admin123
            cursor.execute("SELECT COUNT(*) FROM users;")
            if cursor.fetchone()[0] == 0:
                admin_hash = "240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9"
                cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s);", ('admin', admin_hash))
                conn.commit()
                print("[Database] Default user created: Username 'admin', Password 'admin123'.")

            cursor.close()
            conn.close()
            print("[Database] Database, tables, and seed verification completed.")
            return True

    except Error as err:
        print(f"[Database Setup Warning] Could not automatically initialize database: {err}")
        return False


if __name__ == '__main__':
    print("Testing MySQL Connection & Database Initialization...")
    init_db()
