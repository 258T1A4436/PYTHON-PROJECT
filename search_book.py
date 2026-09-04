"""
=============================================================================
Module: search_book.py
Description: Handles searching books by title or author name and rendering
             the search results table.
=============================================================================
"""

import os
import html
from db import get_db_connection

TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), 'templates')

def search_books(query_str):
    """
    Searches books in the database matching title or author using the SQL LIKE operator.
    Args:
        query_str (str): The search term entered by the user.
    Returns:
        list of dict: Matching book records.
    """
    conn = get_db_connection()
    if not conn:
        return []

    try:
        cursor = conn.cursor(dictionary=True)
        # Using % wildcard for substring match in both title and author
        search_pattern = f"%{query_str.strip()}%"
        sql = """
            SELECT id, title, author, category, quantity
            FROM books
            WHERE title LIKE %s OR author LIKE %s
            ORDER BY id ASC;
        """
        cursor.execute(sql, (search_pattern, search_pattern))
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        return results
    except Exception as e:
        print(f"Error searching books: {e}")
        return []

def render_search_page(query=None, alert_message="", user_nav=""):
    """
    Renders the search.html page, dynamically inserting the search query,
    summary status banner, user navigation, and table of matched books.
    """
    file_path = os.path.join(TEMPLATES_DIR, 'search.html')
    with open(file_path, 'r', encoding='utf-8') as f:
        template = f.read()

    clean_query = query.strip() if query else ""

    if not clean_query:
        summary_html = '<p style="color: var(--text-secondary); margin-bottom: 1.25rem;">Enter a keyword above to find books in the library catalogue.</p>'
        table_html = """
            <tr>
                <td colspan="6" class="empty-state">
                    <h3>Ready to Search</h3>
                    <p>Enter a book title or author name in the search box above.</p>
                </td>
            </tr>
        """
    else:
        results = search_books(clean_query)
        if results:
            summary_html = f'<div class="alert alert-success">Found {len(results)} book(s) matching "<strong>{html.escape(clean_query)}</strong>"</div>'
            rows = []
            for b in results:
                qty_class = "badge-qty-low" if b['quantity'] <= 2 else "badge-qty"
                row = f"""
                <tr>
                    <td><strong>#{b['id']}</strong></td>
                    <td><strong>{html.escape(str(b['title']))}</strong></td>
                    <td>{html.escape(str(b['author']))}</td>
                    <td><span class="badge badge-category">{html.escape(str(b['category']))}</span></td>
                    <td><span class="badge {qty_class}">{b['quantity']} copies</span></td>
                    <td>
                        <a href="/update?id={b['id']}" class="btn btn-secondary btn-sm">Edit</a>
                        <a href="/delete?id={b['id']}" class="btn btn-danger btn-sm"
                           onclick="return confirm('Are you sure you want to delete book #{b['id']} ({html.escape(str(b['title']))})?');">Delete</a>
                    </td>
                </tr>
                """
                rows.append(row)
            table_html = "".join(rows)
        else:
            summary_html = f'<div class="alert alert-warning">No books found matching "<strong>{html.escape(clean_query)}</strong>"</div>'
            table_html = """
                <tr>
                    <td colspan="6" class="empty-state">
                        <h3>No Books Found</h3>
                        <p>Try searching with another keyword, author name, or check your spelling.</p>
                    </td>
                </tr>
            """

    template = template.replace("{{search_query}}", html.escape(clean_query))
    template = template.replace("{{search_summary}}", summary_html)
    template = template.replace("{{results_table}}", table_html)
    template = template.replace("{{user_nav}}", user_nav)
    return template
