"""
=============================================================================
Module: update_book.py
Description: Handles logic for retrieving a book by ID, rendering the edit form,
             and updating the record in the MySQL database.
=============================================================================
"""

import os
import html
from db import get_db_connection

TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), 'templates')

def get_book_by_id(book_id):
    """
    Fetches a single book record by its primary key (ID).
    Args:
        book_id (int/str): The ID of the book.
    Returns:
        dict: Book details or None if not found.
    """
    conn = get_db_connection()
    if not conn:
        return None

    try:
        cursor = conn.cursor(dictionary=True)
        query = "SELECT id, title, author, category, quantity FROM books WHERE id = %s;"
        cursor.execute(query, (book_id,))
        book = cursor.fetchone()
        cursor.close()
        conn.close()
        return book
    except Exception as e:
        print(f"Error fetching book ID {book_id}: {e}")
        return None

def render_update_page(book_id, alert_message="", user_nav=""):
    """
    Reads update_book.html, populates the input fields with current book data,
    and returns the ready HTML string.
    """
    book = get_book_by_id(book_id)
    if not book:
        return f"""
        <html>
            <head><link rel="stylesheet" href="/static/style.css"></head>
            <body class="container" style="text-align:center; padding-top: 5rem;">
                <h2>Book Not Found</h2>
                <p>The requested book (ID: {html.escape(str(book_id))}) does not exist in the database.</p>
                <br>
                <a href="/" class="btn btn-primary">Return to Home</a>
            </body>
        </html>
        """

    file_path = os.path.join(TEMPLATES_DIR, 'update_book.html')
    with open(file_path, 'r', encoding='utf-8') as f:
        template = f.read()

    # Replace placeholders with escaped safe values
    template = template.replace("{{book_id}}", str(book['id']))
    template = template.replace("{{title}}", html.escape(str(book['title'])))
    template = template.replace("{{author}}", html.escape(str(book['author'])))
    template = template.replace("{{category}}", html.escape(str(book['category'])))
    template = template.replace("{{quantity}}", str(book['quantity']))
    template = template.replace("{{alert_message}}", alert_message)
    template = template.replace("{{user_nav}}", user_nav)

    return template

def update_book_record(book_id, title, author, category, quantity):
    """
    Updates an existing book record in the 'books' table.
    Args:
        book_id (int/str): ID of the book to update.
        title (str): Updated title.
        author (str): Updated author.
        category (str): Updated category.
        quantity (int/str): Updated quantity.
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

    # 2. Database Execution
    conn = get_db_connection()
    if not conn:
        return False, "Database connection failed. Please check MySQL server."

    try:
        cursor = conn.cursor()
        query = """
            UPDATE books
            SET title = %s, author = %s, category = %s, quantity = %s
            WHERE id = %s;
        """
        cursor.execute(query, (title, author, category, qty, book_id))
        conn.commit()

        cursor.close()
        conn.close()
        return True, f"Book #{book_id} updated successfully!"

    except Exception as e:
        return False, f"Error updating book: {str(e)}"
