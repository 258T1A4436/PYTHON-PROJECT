"""
=============================================================================
Module: auth.py
Description: Authentication handler (Registration, Login, and SHA-256 Hashing)
             for the Library Management System.
=============================================================================
"""

import os
import html
import hashlib
from db import get_db_connection

TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), 'templates')


def hash_password(plain_password):
    """
    Hashes a plain-text password using the standard SHA-256 cryptographic algorithm.
    Returns:
        str: 64-character hexadecimal representation of the hash.
    """
    return hashlib.sha256(plain_password.encode('utf-8')).hexdigest()


def register_user(username, password, confirm_password):
    """
    Validates and registers a new user into the 'users' database table.
    Args:
        username (str): Desired username.
        password (str): Plain-text password.
        confirm_password (str): Confirmation password.
    Returns:
        tuple: (success: bool, message: str)
    """
    username = username.strip()

    # 1. Validation
    if not username or not password:
        return False, "Username and password cannot be empty."

    if len(username) < 3:
        return False, "Username must be at least 3 characters long."

    if len(password) < 4:
        return False, "Password must be at least 4 characters long."

    if password != confirm_password:
        return False, "Passwords do not match! Please re-type."

    # 2. Database Connection
    conn = get_db_connection()
    if not conn:
        return False, "Database connection failed. Please ensure MySQL server is running."

    try:
        cursor = conn.cursor(dictionary=True)

        # Check if username already exists
        cursor.execute("SELECT id FROM users WHERE username = %s;", (username,))
        existing_user = cursor.fetchone()

        if existing_user:
            cursor.close()
            conn.close()
            return False, f"Username '{html.escape(username)}' is already taken. Please choose another."

        # Hash password and insert
        hashed = hash_password(password)
        cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s);", (username, hashed))
        conn.commit()

        cursor.close()
        conn.close()
        return True, "Account registered successfully! You can now log in."

    except Exception as e:
        return False, f"Error registering user: {str(e)}"


def login_user(username, password):
    """
    Verifies user login credentials against hashed passwords stored in MySQL.
    Args:
        username (str): Username entered by user.
        password (str): Plain-text password entered by user.
    Returns:
        tuple: (success: bool, user_data_or_error: str)
    """
    username = username.strip()
    if not username or not password:
        return False, "Please enter both username and password."

    conn = get_db_connection()
    if not conn:
        return False, "Database connection failed. Please check MySQL server."

    try:
        cursor = conn.cursor(dictionary=True)
        hashed = hash_password(password)

        query = "SELECT id, username FROM users WHERE username = %s AND password = %s;"
        cursor.execute(query, (username, hashed))
        user = cursor.fetchone()

        cursor.close()
        conn.close()

        if user:
            return True, user['username']
        else:
            return False, "Invalid username or password. Please try again."

    except Exception as e:
        return False, f"Authentication error: {str(e)}"


def render_login_page(alert_message=""):
    """Renders the login.html template."""
    file_path = os.path.join(TEMPLATES_DIR, 'login.html')
    with open(file_path, 'r', encoding='utf-8') as f:
        template = f.read()
    return template.replace("{{alert_message}}", alert_message)


def render_register_page(alert_message="", username_val=""):
    """Renders the register.html template."""
    file_path = os.path.join(TEMPLATES_DIR, 'register.html')
    with open(file_path, 'r', encoding='utf-8') as f:
        template = f.read()
    template = template.replace("{{alert_message}}", alert_message)
    template = template.replace("{{username_val}}", html.escape(username_val))
    return template
