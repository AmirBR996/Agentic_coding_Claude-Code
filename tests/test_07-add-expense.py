import pytest
from fastapi.testclient import TestClient
from main import app
from database.db import init_db, create_user, get_db
import sqlite3
import os
from datetime import date

# Use a separate test database
TEST_DB = "test_spendly.db"

@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    # Monkeypatch DB_PATH in database.db before any imports if possible,
    # but since it's already imported in main, we might need to handle it.
    # For this project structure, we'll override the path in the module.
    import database.db
    original_db_path = database.db.DB_PATH
    database.db.DB_PATH = TEST_DB
    init_db()
    yield
    database.db.DB_PATH = original_db_path
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)

@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c

@pytest.fixture
def test_user():
    # Create a test user in the database, handling the case where the user might already exist
    email = "test@example.com"
    with get_db() as conn:
        existing_user = conn.execute("SELECT id FROM users WHERE email = ?", (email,)).fetchone()
        if existing_user:
            return {"id": existing_user["id"], "email": email}

    user_id = create_user("Test User", email, "password123")
    return {"id": user_id, "email": email}

@pytest.fixture
def authenticated_client(client, test_user):
    # Manually set the session cookie to simulate a logged-in user
    # The session middleware uses a signed cookie. We can simulate the session
    # by using the client to log in first.
    client.post("/login", data={"email": test_user["email"], "password": "password123"})
    return client

def test_add_expense_page_unauthenticated(client):
    # Accessing GET /expenses/add while logged out should redirect to /login
    response = client.get("/expenses/add", follow_redirects=False)
    assert response.status_code == 303
    assert response.headers["Location"] == "/login"

def test_add_expense_post_unauthenticated(client):
    # Accessing POST /expenses/add while logged out should redirect to /login
    response = client.post("/expenses/add", data={"amount": 10, "category": "Food", "date": "2023-01-01"}, follow_redirects=False)
    assert response.status_code == 303
    assert response.headers["Location"] == "/login"

def test_add_expense_page_renders(authenticated_client):
    # Verify GET /expenses/add renders the page and provides a default date
    response = authenticated_client.get("/expenses/add")
    assert response.status_code == 200
    assert "add_expense.html" in response.text or "amount" in response.text.lower()

    # Verify today's date is present in the form
    today = date.today().isoformat()
    assert today in response.text

def test_add_expense_happy_path(authenticated_client, test_user):
    # Submit a valid expense
    expense_data = {
        "amount": 50.0,
        "category": "Food",
        "date": "2023-10-27",
        "description": "Dinner at Restaurant"
    }
    response = authenticated_client.post("/expenses/add", data=expense_data, follow_redirects=False)

    # Verify 303 redirect to /profile
    assert response.status_code == 303
    assert response.headers["Location"] == "/profile"

    # Verify record is actually inserted into the database
    with get_db() as conn:
        expense = conn.execute(
            "SELECT * FROM expenses WHERE user_id = ? AND amount = ? AND category = ?",
            (test_user["id"], 50.0, "Food")
        ).fetchone()
        assert expense is not None
        assert expense["description"] == "Dinner at Restaurant"

def test_add_expense_invalid_amount(authenticated_client):
    # Submit an amount <= 0
    expense_data = {
        "amount": 0,
        "category": "Food",
        "date": "2023-10-27",
        "description": "Free Meal"
    }
    response = authenticated_client.post("/expenses/add", data=expense_data, follow_redirects=False)

    # Verify 303 redirect to /expenses/add?error=...
    assert response.status_code == 303
    assert "error=Amount+must+be+greater+than+zero" in response.headers["Location"]

def test_add_expense_empty_fields(authenticated_client):
    # Submit empty category or date
    # Test empty category
    expense_data_no_cat = {
        "amount": 10.0,
        "category": "",
        "date": "2023-10-27",
        "description": "Test"
    }
    response = authenticated_client.post("/expenses/add", data=expense_data_no_cat, follow_redirects=False)
    assert response.status_code == 303
    assert "error=Category+and+date+are+required" in response.headers["Location"]

    # Test empty date
    expense_data_no_date = {
        "amount": 10.0,
        "category": "Food",
        "date": "",
        "description": "Test"
    }
    response = authenticated_client.post("/expenses/add", data=expense_data_no_date, follow_redirects=False)
    assert response.status_code == 303
    assert "error=Category+and+date+are+required" in response.headers["Location"]
