import sqlite3
from werkzeug.security import generate_password_hash

DB_PATH = "spendly.db"

def get_db():
    """
    Returns a SQLite connection with row_factory and foreign keys enabled.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def get_user_by_email(email: str):
    """
    Retrieves a user from the database by their email address.
    """
    with get_db() as conn:
        return conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()

def create_user(name: str, email: str, password: str):
    """
    Hashes the password and inserts a new user into the users table.
    Returns the new user's id.
    """
    password_hash = generate_password_hash(password)
    with get_db() as conn:
        cursor = conn.execute(
            "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
            (name, email, password_hash)
        )
        conn.commit()
        return cursor.lastrowid

def init_db():
    """
    Creates all tables using CREATE TABLE IF NOT EXISTS.
    """
    with get_db() as conn:
        # Users table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Expenses table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                amount REAL NOT NULL,
                category TEXT NOT NULL,
                date TEXT NOT NULL,
                description TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)
        conn.commit()

def seed_db():
    """
    Inserts sample data for development if the database is empty.
    """
    with get_db() as conn:
        # Check if users table already contains data
        user = conn.execute("SELECT 1 FROM users LIMIT 1").fetchone()
        if user:
            return

        # Insert demo user
        password_hash = generate_password_hash("demo123")
        cursor = conn.execute(
            "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
            ("Demo User", "demo@spendly.com", password_hash)
        )
        user_id = cursor.lastrowid

        # Sample expenses covering all categories
        # Categories: Food, Transport, Bills, Health, Entertainment, Shopping, Other
        expenses = [
            (user_id, 12.50, "Food", "2026-09-01", "Lunch at Cafe"),
            (user_id, 45.00, "Transport", "2026-09-02", "Weekly Fuel"),
            (user_id, 120.00, "Bills", "2026-09-03", "Electricity Bill"),
            (user_id, 30.00, "Health", "2026-09-05", "Pharmacy"),
            (user_id, 15.00, "Entertainment", "2026-09-07", "Movie Ticket"),
            (user_id, 60.00, "Shopping", "2026-09-10", "New Shirt"),
            (user_id, 10.00, "Other", "2026-09-12", "Postage"),
            (user_id, 25.00, "Food", "2026-09-15", "Grocery Store"),
        ]

        conn.executemany(
            "INSERT INTO expenses (user_id, amount, category, date, description) VALUES (?, ?, ?, ?, ?)",
            expenses
        )
        conn.commit()
