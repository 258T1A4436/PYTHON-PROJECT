"""
=============================================================================
Module: delete_book.py
Description: Handles deletion of a book record from the MySQL database by ID.
=============================================================================
"""

from db import get_db_connection

def delete_book_record(book_id):
    """
    Deletes a book from the 'books' table using its ID.
    Args:
        book_id (int/str): The ID of the book to remove.
    Returns:
        tuple: (success: bool, message: str)
    """
    conn = get_db_connection()
    if not conn:
        return False, "Database connection failed. Please check MySQL server."

    try:
        cursor = conn.cursor()

        # Parameterized query to safely delete book record
        query = "DELETE FROM books WHERE id = %s;"
        cursor.execute(query, (book_id,))
        conn.commit()

        # Check how many rows were affected
        deleted_count = cursor.rowcount
        cursor.close()
        conn.close()

        if deleted_count > 0:
            return True, f"Book #{book_id} was successfully deleted."
        else:
            return False, f"No book found with ID #{book_id}."

    except Exception as e:
        return False, f"Error deleting book: {str(e)}"
