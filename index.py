"""
=============================================================================
Main Application: index.py
Project: Simple Library Management System (HTML, CSS, Python, MySQL)
Target Audience: 2nd Year B.Tech CSE Students

Technology Notes:
- Built strictly using Python Standard Library (http.server, urllib.parse, http.cookies)
- Zero external web frameworks (No Flask, Django, FastAPI, etc.)
- Connects to MySQL using mysql-connector-python
- User Authentication (Login, Register, Logout) using SHA-256 and HTTP Cookies
- Pure modular architecture
=============================================================================
"""

import os
import sys
import html
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from http.cookies import SimpleCookie

# Import backend modules
from db import init_db, get_db_connection
from auth import login_user, register_user, render_login_page, render_register_page
from add_book import render_add_page, insert_book
from update_book import render_update_page, update_book_record
from delete_book import delete_book_record
from search_book import render_search_page

PORT = 8000
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(BASE_DIR, 'templates')
STATIC_DIR = os.path.join(BASE_DIR, 'static')


class LibraryRequestHandler(BaseHTTPRequestHandler):
    """
    HTTP Request Handler to route requests and handle GET/POST actions.
    Subclasses Python's built-in BaseHTTPRequestHandler.
    """

    def send_html(self, content, status=200, extra_headers=None):
        """Helper to send an HTML response with custom status and headers."""
        encoded = content.encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.send_header('Content-Length', str(len(encoded)))
        if extra_headers:
            for header_name, header_value in extra_headers:
                self.send_header(header_name, header_value)
        self.end_headers()
        self.wfile.write(encoded)

    def redirect(self, location, cookie_headers=None):
        """Helper to issue an HTTP 303 redirect with optional cookie headers."""
        self.send_response(303)
        self.send_header('Location', location)
        if cookie_headers:
            for h_name, h_val in cookie_headers:
                self.send_header(h_name, h_val)
        self.end_headers()

    def serve_static(self, file_path, content_type):
        """Serves CSS or static assets."""
        if os.path.exists(file_path):
            with open(file_path, 'rb') as f:
                data = f.read()
            self.send_response(200)
            self.send_header('Content-Type', content_type)
            self.send_header('Content-Length', str(len(data)))
            self.end_headers()
            self.wfile.write(data)
        else:
            self.send_error(404, "Static file not found")

    def get_current_user(self):
        """
        Reads the 'session_user' cookie from incoming HTTP request headers.
        Returns the username if authenticated, or None if not logged in.
        """
        raw_cookie = self.headers.get('Cookie')
        if raw_cookie:
            try:
                cookie = SimpleCookie()
                cookie.load(raw_cookie)
                if 'session_user' in cookie:
                    username = cookie['session_user'].value.strip()
                    if username:
                        return username
            except Exception:
                pass
        return None

    def get_user_nav(self, username):
        """Builds HTML snippet for the user banner and Logout button in navbar."""
        if username:
            return f"""
            <div class="user-profile-nav">
                <span class="user-name">👤 {html.escape(username)}</span>
                <a href="/logout" class="btn-logout">Logout</a>
            </div>
            """
        return ""

    # =========================================================================
    # HTTP GET Requests (Page Views & Search)
    # =========================================================================
    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        query_params = parse_qs(parsed.query)

        # 1. Public: Serve Static CSS
        if path == '/static/style.css':
            css_file = os.path.join(STATIC_DIR, 'style.css')
            self.serve_static(css_file, 'text/css')
            return

        # 2. Public: Login Page ('/login')
        if path == '/login':
            current_user = self.get_current_user()
            if current_user:
                self.redirect('/')
                return

            msg_param = query_params.get('msg', [''])[0]
            alert = ""
            if msg_param == 'registered':
                alert = '<div class="alert alert-success">Account created successfully! Please sign in.</div>'
            elif msg_param == 'logged_out':
                alert = '<div class="alert alert-success">You have been logged out safely.</div>'
            elif msg_param == 'login_required':
                alert = '<div class="alert alert-warning">Please sign in to access the library.</div>'

            self.send_html(render_login_page(alert_message=alert))
            return

        # 3. Public: Register Page ('/register')
        if path == '/register':
            current_user = self.get_current_user()
            if current_user:
                self.redirect('/')
                return
            self.send_html(render_register_page())
            return

        # 4. Action: Logout ('/logout')
        if path == '/logout':
            # Expire session cookie immediately
            expired_cookie = ('Set-Cookie', 'session_user=; Path=/; Expires=Thu, 01 Jan 1970 00:00:00 GMT; HttpOnly')
            self.redirect('/login?msg=logged_out', cookie_headers=[expired_cookie])
            return

        # ---------------------------------------------------------------------
        # Protected Routes (Require active login session)
        # ---------------------------------------------------------------------
        current_user = self.get_current_user()
        if not current_user:
            # User is not logged in: redirect to login page
            self.redirect('/login?msg=login_required')
            return

        user_nav_html = self.get_user_nav(current_user)

        # Home Page ('/' or '/index')
        if path in ('/', '/index'):
            self.handle_home_page(query_params, user_nav_html)
            return

        # Add Book Page ('/add')
        if path == '/add':
            html_content = render_add_page(user_nav=user_nav_html)
            self.send_html(html_content)
            return

        # Update Book Page ('/update?id=X')
        if path == '/update':
            book_id = query_params.get('id', [None])[0]
            if not book_id:
                self.redirect('/')
                return
            html_content = render_update_page(book_id, user_nav=user_nav_html)
            self.send_html(html_content)
            return

        # Delete Book Action ('/delete?id=X')
        if path == '/delete':
            book_id = query_params.get('id', [None])[0]
            if book_id:
                success, msg = delete_book_record(book_id)
                self.redirect('/?msg=deleted' if success else '/?msg=delete_failed')
            else:
                self.redirect('/')
            return

        # Search Book Page ('/search' or '/search?query=XYZ')
        if path == '/search':
            search_query = query_params.get('query', [''])[0]
            html_content = render_search_page(search_query, user_nav=user_nav_html)
            self.send_html(html_content)
            return

        # Fallback: 404 Not Found
        self.send_html("""
            <!DOCTYPE html>
            <html>
                <head><link rel="stylesheet" href="/static/style.css"><title>404 Not Found</title></head>
                <body class="container" style="text-align:center; padding-top: 5rem;">
                    <h1>404 - Page Not Found</h1>
                    <p style="color: var(--text-secondary); margin: 1rem 0 2rem 0;">The page you are looking for does not exist.</p>
                    <a href="/" class="btn btn-primary">Return to Home</a>
                </body>
            </html>
        """, status=404)

    # =========================================================================
    # HTTP POST Requests (Form Submissions)
    # =========================================================================
    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path

        # Read POST body
        content_length = int(self.headers.get('Content-Length', 0))
        post_body = self.rfile.read(content_length).decode('utf-8')
        form_data = parse_qs(post_body)

        def get_val(key):
            vals = form_data.get(key, [''])
            return vals[0].strip() if vals else ''

        # 1. Handle User Login ('/login')
        if path == '/login':
            username = get_val('username')
            password = get_val('password')

            success, result = login_user(username, password)
            if success:
                # Set HttpOnly session cookie and redirect to Home
                cookie_header = ('Set-Cookie', f'session_user={result}; Path=/; HttpOnly')
                self.redirect('/', cookie_headers=[cookie_header])
            else:
                alert = f'<div class="alert alert-danger">{html.escape(result)}</div>'
                self.send_html(render_login_page(alert_message=alert))
            return

        # 2. Handle User Registration ('/register')
        if path == '/register':
            username = get_val('username')
            password = get_val('password')
            confirm_pwd = get_val('confirm_password')

            success, msg = register_user(username, password, confirm_pwd)
            if success:
                self.redirect('/login?msg=registered')
            else:
                alert = f'<div class="alert alert-danger">{html.escape(msg)}</div>'
                self.send_html(render_register_page(alert_message=alert, username_val=username))
            return

        # ---------------------------------------------------------------------
        # Protected POST Routes (Require active login session)
        # ---------------------------------------------------------------------
        current_user = self.get_current_user()
        if not current_user:
            self.redirect('/login?msg=login_required')
            return

        user_nav_html = self.get_user_nav(current_user)

        # 3. Handle Add Book Submission ('/add')
        if path == '/add':
            title = get_val('title')
            author = get_val('author')
            category = get_val('category')
            quantity = get_val('quantity')

            success, msg = insert_book(title, author, category, quantity)
            if success:
                self.redirect('/?msg=added')
            else:
                alert = f'<div class="alert alert-warning">{html.escape(msg)}</div>'
                self.send_html(render_add_page(alert_message=alert, user_nav=user_nav_html))
            return

        # 4. Handle Update Book Submission ('/update')
        if path == '/update':
            book_id = get_val('id')
            title = get_val('title')
            author = get_val('author')
            category = get_val('category')
            quantity = get_val('quantity')

            success, msg = update_book_record(book_id, title, author, category, quantity)
            if success:
                self.redirect('/?msg=updated')
            else:
                alert = f'<div class="alert alert-warning">{html.escape(msg)}</div>'
                self.send_html(render_update_page(book_id, alert_message=alert, user_nav=user_nav_html))
            return

        # Default fallback
        self.redirect('/')

    # =========================================================================
    # Helper: Home Page Rendering
    # =========================================================================
    def handle_home_page(self, query_params, user_nav_html):
        """Fetches all books from MySQL and renders index.html."""
        conn = get_db_connection()
        books = []
        if conn:
            try:
                cursor = conn.cursor(dictionary=True)
                cursor.execute("SELECT id, title, author, category, quantity FROM books ORDER BY id ASC;")
                books = cursor.fetchall()
                cursor.close()
                conn.close()
            except Exception as e:
                print(f"[Error fetching all books]: {e}")

        # Build notification banner based on URL query parameter ?msg=...
        msg_type = query_params.get('msg', [''])[0]
        alert_message = ""
        if msg_type == 'added':
            alert_message = '<div class="alert alert-success">Book added to the library successfully!</div>'
        elif msg_type == 'updated':
            alert_message = '<div class="alert alert-success">Book details updated successfully!</div>'
        elif msg_type == 'deleted':
            alert_message = '<div class="alert alert-success">Book deleted successfully from library records.</div>'
        elif msg_type == 'delete_failed':
            alert_message = '<div class="alert alert-warning">Could not delete book. Please check ID.</div>'

        # Build table rows HTML
        if books:
            table_rows = []
            for b in books:
                qty_badge = "badge-qty-low" if b['quantity'] <= 2 else "badge-qty"
                row = f"""
                <tr>
                    <td><strong>#{b['id']}</strong></td>
                    <td><strong>{html.escape(str(b['title']))}</strong></td>
                    <td>{html.escape(str(b['author']))}</td>
                    <td><span class="badge badge-category">{html.escape(str(b['category']))}</span></td>
                    <td><span class="badge {qty_badge}">{b['quantity']} copies</span></td>
                    <td>
                        <a href="/update?id={b['id']}" class="btn btn-secondary btn-sm">Edit</a>
                        <a href="/delete?id={b['id']}" class="btn btn-danger btn-sm"
                           onclick="return confirm('Are you sure you want to delete book #{b['id']} ({html.escape(str(b['title']))})?');">Delete</a>
                    </td>
                </tr>
                """
                table_rows.append(row)
            table_html = "".join(table_rows)
        else:
            table_html = """
                <tr>
                    <td colspan="6" class="empty-state">
                        <h3>No Books Available</h3>
                        <p>Your library collection is currently empty. Click "Add New Book" to get started!</p>
                    </td>
                </tr>
            """

        # Read template and replace placeholders
        index_file = os.path.join(TEMPLATES_DIR, 'index.html')
        with open(index_file, 'r', encoding='utf-8') as f:
            content = f.read()

        content = content.replace("{{alert_message}}", alert_message)
        content = content.replace("{{total_books}}", str(len(books)))
        content = content.replace("{{books_table}}", table_html)
        content = content.replace("{{user_nav}}", user_nav_html)

        self.send_html(content)

    def log_message(self, format, *args):
        """Custom clean logging to console."""
        sys.stderr.write(f"[{self.log_date_time_string()}] {args[0]} - {args[1]}\n")


# =============================================================================
# Server Initialization
# =============================================================================
def start_server():
    print("=" * 65)
    print("  COLLEGE LIBRARY MANAGEMENT SYSTEM")
    print("  Pure Python (http.server) + MySQL + HTML/CSS")
    print("=" * 65)

    # 1. Initialize / check database connection
    print("\n[Step 1/2] Checking MySQL Database connection...")
    init_db()

    # 2. Launch HTTP server
    server_address = ('', PORT)
    httpd = HTTPServer(server_address, LibraryRequestHandler)

    print(f"\n[Step 2/2] Server running successfully!")
    print(f"-> Open your web browser and visit: http://localhost:{PORT}")
    print(f"-> Default login: Username 'admin', Password 'admin123'")
    print(f"-> Press Ctrl+C in this terminal to stop the server.\n")
    print("-" * 65)

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n[Shutting down] Server stopped gracefully.")
        httpd.server_close()


if __name__ == '__main__':
    start_server()
