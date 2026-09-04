# Library Management System

A beginner-friendly, clean, and modular **Library Management System** created for **2nd Year B.Tech Computer Science & Engineering (CSE)** students. 

This project demonstrates core computer science competencies:
- **User Authentication**: Login, Registration, and Logout with SHA-256 password hashing.
- **Pure Standard Python**: Direct HTTP request/response handling and cookie sessions using Python's standard library (`http.server`, `http.cookies`) **without** Flask, Django, or FastAPI.
- **Relational Database**: Relational data storage using **MySQL** with parameterized SQL queries preventing SQL injection.
- **Modern Responsive UI**: Clean front-end web design using semantic **HTML5** and responsive **CSS3**.
- **Complete CRUD Operations**: Create, Read, Update, Delete, and live search across library inventory.

---

## 📁 Project Structure

```text
LibraryManagementSystem/
│
├── index.py                 # Main entry point: HTTP web server, routing & cookie sessions
├── db.py                    # MySQL database connection & auto-table initializer
├── auth.py                  # User authentication (Registration, Login, SHA-256 hashing)
├── add_book.py              # Logic to insert new books into MySQL
├── update_book.py           # Logic to fetch by ID and update book records
├── delete_book.py           # Logic to remove books by ID from the database
├── search_book.py           # Logic to search books by title or author name
├── set_password.py          # Utility script to test & save your MySQL password easily
│
├── templates/               # HTML5 user interface templates
│   ├── login.html           # Login screen with validation & demo credentials
│   ├── register.html        # Registration screen with password confirmation
│   ├── index.html           # Home page: list all books in a table with user navbar
│   ├── add_book.html        # Form to add a new book
│   ├── update_book.html     # Pre-filled form to update an existing book
│   └── search.html          # Search interface and results table
│
├── static/                  # Static assets
│   └── style.css            # Responsive CSS stylesheet (cards, tables, badges, auth)
│
├── library_management.sql   # SQL database script with starter sample records & demo user
├── requirements.txt         # Python dependencies (mysql-connector-python)
└── README.md                # Project documentation and Viva preparation guide
```

---

## 🛠️ Technology Stack

| Component | Technology | Description |
| :--- | :--- | :--- |
| **Frontend** | HTML5, CSS3 | Clean UI, responsive table, badges, forms, auth screens |
| **Backend** | Python 3.x | Standard Library (`http.server`, `http.cookies`, `hashlib`) |
| **Database** | MySQL | Relational database (`library_management`) |
| **Connector**| `mysql-connector-python` | Official Python-MySQL driver |
| **Frameworks** | **None** | Pure Python—no Flask, Django, or React required! |

---

## 🗄️ Database Schema

### Database Name: `library_management`

#### Table 1: `books`
| Field | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | `INT` | `AUTO_INCREMENT PRIMARY KEY` | Unique ID for each book |
| `title` | `VARCHAR(200)` | `NOT NULL` | Book title |
| `author` | `VARCHAR(100)` | `NOT NULL` | Author's full name |
| `category` | `VARCHAR(100)` | `NOT NULL` | Subject / genre category |
| `quantity` | `INT` | `NOT NULL DEFAULT 1` | Available copies in the library |

#### Table 2: `users`
| Field | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | `INT` | `AUTO_INCREMENT PRIMARY KEY` | Unique user ID |
| `username` | `VARCHAR(50)` | `NOT NULL UNIQUE` | Unique username for login |
| `password` | `VARCHAR(64)` | `NOT NULL` | SHA-256 hashed password (64 characters) |
| `created_at` | `TIMESTAMP` | `DEFAULT CURRENT_TIMESTAMP` | Account creation timestamp |

---

## 🔑 Default Credentials

The project comes with a pre-configured demo account:
- **Username**: `admin`
- **Password**: `admin123`

*(You can also register any number of new student/admin accounts on the `/register` page!)*

---

## 🚀 Setup & Installation Guide

### Step 1: Install Dependencies
Open PowerShell or Command Prompt in the `LibraryManagementSystem` folder and run:
```bash
pip install -r requirements.txt
```

---

### Step 2: Configure Your MySQL Password (Easy Helper)
If you are unsure how to edit Python files or what password your MySQL server uses:
Run the helper tool:
```bash
py set_password.py
```
Type your MySQL root password when prompted. The helper will:
1. Test connecting to your MySQL server.
2. Update `db.py` automatically.
3. Initialize the database, `books` table, and `users` table!

*(Alternatively, you can manually open `db.py` and set `'password'` in `DB_CONFIG`)*

---

### Step 3: Run the Application
In your terminal, execute:
```bash
py index.py
```

Console output:
```text
=================================================================
  COLLEGE LIBRARY MANAGEMENT SYSTEM
  Pure Python (http.server) + MySQL + HTML/CSS
=================================================================

[Step 1/2] Checking MySQL Database connection...
[Database] Database, tables, and seed verification completed.

[Step 2/2] Server running successfully!
-> Open your web browser and visit: http://localhost:8000
-> Default login: Username 'admin', Password 'admin123'
-> Press Ctrl+C in this terminal to stop the server.
-----------------------------------------------------------------
```

Open your browser and navigate to:
👉 **[http://localhost:8000](http://localhost:8000)**

---

## 🌟 Application Flow

1. **Login Page (`/login`)**:
   - Displays clean sign-in card.
   - Verifies username and compares SHA-256 hash of password with MySQL.
   - Sets a secure HTTP cookie (`session_user=username`) on successful login.

2. **Register Page (`/register`)**:
   - Form with Username, Password, and Confirm Password fields.
   - Validates input (minimum lengths, password match, duplicate username prevention).
   - Stores user securely in MySQL.

3. **Protected Navigation (`/`, `/add`, `/update`, `/delete`, `/search`)**:
   - Automatically redirects unauthenticated visitors to `/login`.
   - Displays active username in navbar: `👤 admin | Logout`.

4. **Logout (`/logout`)**:
   - Expires the session cookie and safely redirects the user back to the login screen.

5. **CRUD & Search**:
   - Full ability to Add, View, Search, Edit, and Delete library books.

---

## 🎓 Viva Questions & Answers (For B.Tech CSE Students)

### Q1: Why did you not use Flask or Django for this web application?
> **Answer**: By using Python's standard library `http.server` (`BaseHTTPRequestHandler`), this project demonstrates fundamental computer networking and HTTP protocols (handling `GET` and `POST` methods, parsing headers, managing cookies, reading raw request bodies) without relying on high-level framework abstractions.

---

### Q2: How is user authentication implemented without external session libraries?
> **Answer**:
> 1. **Password Security**: Passwords are never stored in plain text. When a user registers or logs in, we use Python's built-in `hashlib.sha256()` to compute a 64-character cryptographic hash.
> 2. **Session Cookie**: When credentials match, the server responds with the HTTP header:
>    `Set-Cookie: session_user=<username>; Path=/; HttpOnly`
> 3. **Request Verification**: On each incoming request, the server inspects the `Cookie` header. If the valid cookie is present, access is granted; otherwise, the user is redirected to `/login`.
> 4. **Logout**: The server sends a cookie expiration date in the past (`Expires=Thu, 01 Jan 1970 00:00:00 GMT`), which prompts the browser to discard the cookie.

---

### Q3: What is SHA-256 and why is it used?
> **Answer**: SHA-256 (Secure Hash Algorithm 256-bit) is a one-way cryptographic hash function. "One-way" means it is computationally infeasible to decrypt or reverse the hash back to the original password. Even if an attacker were to read the database, they cannot see the users' actual passwords.

---

### Q4: What is SQL Injection and how does your project prevent it?
> **Answer**: SQL Injection occurs when untrusted input is directly concatenated into SQL query strings. In this project, **all** database operations (including login, registration, and book CRUD) use **parameterized queries (`%s`)**:
> ```python
> cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s;", (username, hashed))
> ```
> The database driver treats the parameters strictly as data values, neutralizing any malicious SQL syntax.

---

### Q5: What is the purpose of `conn.commit()`?
> **Answer**: In relational database management systems (RDBMS), modifying operations (`INSERT`, `UPDATE`, `DELETE`) take place within transactions adhering to ACID properties. Calling `conn.commit()` commits the transaction permanently to disk.

---

### Q6: How does the search function work?
> **Answer**: In `search_book.py`, we execute a query using SQL's `LIKE` operator with `%` wildcards:
> ```sql
> SELECT * FROM books WHERE title LIKE %s OR author LIKE %s;
> ```
> The `%` wildcards allow pattern matching on substrings within the book title or author name.
