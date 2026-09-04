"""
=============================================================================
Utility: set_password.py
Description: Simple interactive helper to test and configure your MySQL
             password in db.py without manually editing code.
Usage:
    py set_password.py
=============================================================================
"""

import sys
import mysql.connector
from mysql.connector import Error

def configure_password():
    print("=" * 60)
    print("  MySQL Password Configuration Helper")
    print("  College Library Management System")
    print("=" * 60)
    print("\nThis helper will test your MySQL password and automatically update db.py.\n")

    entered_password = input("Enter your MySQL 'root' password: ").strip()

    print(f"\n[1/3] Testing connection to MySQL Server on localhost:3306...")
    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password=entered_password,
            port=3306
        )
        print("-> [SUCCESS] Connection established with MySQL Server!")
        conn.close()
    except Error as err:
        print(f"-> [FAILED] Could not connect: {err}")
        print("\nPlease check your password and verify MySQL service is running.")
        return

    # Update db.py
    print("[2/3] Updating password in db.py...")
    try:
        with open('db.py', 'r', encoding='utf-8') as f:
            content = f.read()

        # Replace password setting in DB_CONFIG
        import re
        new_content = re.sub(
            r"('password'\s*:\s*)'[^']*'",
            r"\g<1>" + repr(entered_password),
            content
        )

        with open('db.py', 'w', encoding='utf-8') as f:
            f.write(new_content)

        print("-> [SUCCESS] db.py updated successfully!")
    except Exception as e:
        print(f"-> [ERROR] Could not update db.py: {e}")
        return

    # Initialize database
    print("[3/3] Initializing 'library_management' database and tables...")
    try:
        from db import init_db
        init_db()
        print("\n============================================================")
        print(" SETUP COMPLETE! You can now start the application with:")
        print(" py index.py")
        print("============================================================")
    except Exception as e:
        print(f"-> Warning during initialization: {e}")

if __name__ == '__main__':
    configure_password()
