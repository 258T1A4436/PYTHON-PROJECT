"""
=============================================================================
Module: add_book.py
Description: Handles logic for displaying the 'Add Book' form and inserting
             new book records into the MySQL database.
=============================================================================
"""

import os
from db import get_db_connection

TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), 'templates')

def render_add_page(alert_message="", user_nav=""):
    """
    Reads the add_book.html template and prepares it for rendering.
    Args:
        alert_message (str): Optional alert banner to display in the page.
        user_nav (str): HTML for user profile and logout button in navbar.
    Returns:
        str: Populated HTML string.
    """
    file_path = os.path.join(TEMPLATES_DIR, 'add_book.html')
    with open(file_path, 'r', encoding='utf-8') as f:
        html = f.read()

    html = html.replace("{{alert_message}}", alert_message)
    html = html.replace("{{user_nav}}", user_nav)
    return html

def insert_book(title, author, category, quantity):
    """
    Inserts a new book into the 'books' table using a parameterized SQL query.
    Args:
        title (str): The title of the book.
        author (str): The author of the book.
        category (str): The subject or genre category.
        quantity (int/str): Number of copies in stock.
    Returns:
        tuple: (success: bool, message: str)
    """
    # 1. Validation
    title = title.strip()
    author = author.strip()
    category = category.strip()

    if not title or not author or not category:
        return False, "All fields are required!"

    try:
        qty = int(quantity)
        if qty < 0:
            return False, "Quantity cannot be negative!"
    except ValueError:
        return False, "Quantity must be a valid whole number!"

    # 2. Database Connection
    conn = get_db_connection()
    if not conn:
        return False, "Database connection failed. Please check MySQL server."

    try:
        cursor = conn.cursor()

        # Parameterized query to safely insert data and prevent SQL injection
        query = "INSERT INTO books (title, author, category, quantity) VALUES (%s, %s, %s, %s);"
        cursor.execute(query, (title, author, category, qty))

        # Commit changes to database
        conn.commit()

        cursor.close()
        conn.close()
        return True, f"Book '{title}' added successfully!"

    except Exception as e:
        return False, f"Error inserting book: {str(e)}"
