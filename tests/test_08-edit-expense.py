import pytest
from fastapi.testclient import TestClient
from main import app
from database.db import init_db, create_user, get_db, create_expense
import sqlite3
import os
from datetime import date

# Use a separate test database
TEST_DB = "test_spendly_edit.db"

@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
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
    email = "edit_test@example.com"
    with get_db() as conn:
        existing_user = conn.execute("SELECT id FROM users WHERE email = ?", (email,)).fetchone()
        if existing_user:
            return {"id": existing_user["id"], "email": email}

    user_id = create_user("Edit User", email, "password123")
    return {"id": user_id, "email": email}

@pytest.fixture
def other_user():
    email = "other_test@example.com"
    with get_db() as conn:
        existing_user = conn.execute("SELECT id FROM users WHERE email = ?", (email,)).fetchone()
        if existing_user:
            return {"id": existing_user["id"], "email": email}

    user_id = create_user("Other User", email, "password123")
    return {"id": user_id, "email": email}

@pytest.fixture
def authenticated_client(client, test_user):
    client.post("/login", data={"email": test_user["email"], "password": "password123"})
    return client

@pytest.fixture
def test_expense(test_user):
    # Create an expense to edit
    expense_id = create_expense(
        user_id=test_user["id"],
        amount=100.0,
        category="Food",
        date="2023-01-01",
        description="Original Expense"
    )
    return {"id": expense_id, "user_id": test_user["id"]}

def test_edit_expense_page_unauthenticated(client):
    # Accessing GET /expenses/1/edit while logged out should redirect to /login
    response = client.get("/expenses/1/edit", follow_redirects=False)
    assert response.status_code == 303
    assert response.headers["Location"] == "/login"

def test_edit_expense_page_renders(authenticated_client, test_expense):
    # Verify GET /expenses/{id}/edit renders the page and is pre-filled
    response = authenticated_client.get(f"/expenses/{test_expense['id']}/edit")
    assert response.status_code == 200
    assert "edit_expense.html" in response.text or "amount" in response.text.lower()
    assert "Original Expense" in response.text
    assert "100" in response.text
    assert "Food" in response.text
    assert "2023-01-01" in response.text

def test_edit_expense_happy_path(authenticated_client, test_expense):
    # Submit updated expense data
    updated_data = {
        "amount": 150.0,
        "category": "Shopping",
        "date": "2023-01-02",
        "description": "Updated Expense"
    }
    response = authenticated_client.post(
        f"/expenses/{test_expense['id']}/edit",
        data=updated_data,
        follow_redirects=False
    )

    # Verify 303 redirect to /profile
    assert response.status_code == 303
    assert response.headers["Location"] == "/profile"

    # Verify record is actually updated in the database
    with get_db() as conn:
        expense = conn.execute(
            "SELECT * FROM expenses WHERE id = ?",
            (test_expense['id'],)
        ).fetchone()
        assert expense is not None
        assert expense["amount"] == 150.0
        assert expense["category"] == "Shopping"
        assert expense["date"] == "2023-01-02"
        assert expense["description"] == "Updated Expense"

def test_edit_expense_not_found(authenticated_client):
    # Attempt to edit an expense ID that doesn't exist
    response = authenticated_client.get("/expenses/999999/edit")
    assert response.status_code == 404

def test_edit_expense_unauthorized(client, test_expense, other_user):
    # Log in as a different user
    client.post("/login", data={"email": other_user["email"], "password": "password123"})

    # Attempt to access another user's expense edit page
    response = client.get(f"/expenses/{test_expense['id']}/edit")
    # Spec says 404 or 403
    assert response.status_code in [403, 404]

def test_edit_expense_post_unauthorized(client, test_expense, other_user):
    # Log in as a different user
    client.post("/login", data={"email": other_user["email"], "password": "password123"})

    # Attempt to update another user's expense
    updated_data = {
        "amount": 200.0,
        "category": "Food",
        "date": "2023-01-01",
        "description": "Hacker"
    }
    response = client.post(f"/expenses/{test_expense['id']}/edit", data=updated_data)
    assert response.status_code in [403, 404]

def test_edit_expense_invalid_amount(authenticated_client, test_expense):
    # Submit an amount <= 0
    updated_data = {
        "amount": 0,
        "category": "Food",
        "date": "2023-01-01",
        "description": "Free"
    }
    response = authenticated_client.post(
        f"/expenses/{test_expense['id']}/edit",
        data=updated_data,
        follow_redirects=False
    )

    # Verify 303 redirect to edit page with error
    assert response.status_code == 303
    assert f"/expenses/{test_expense['id']}/edit?error=Amount+must+be+greater+than+zero" in response.headers["Location"]

def test_edit_expense_empty_fields(authenticated_client, test_expense):
    # Test empty category
    updated_data_no_cat = {
        "amount": 10.0,
        "category": "",
        "date": "2023-01-01",
        "description": "Test"
    }
    response = authenticated_client.post(
        f"/expenses/{test_expense['id']}/edit",
        data=updated_data_no_cat,
        follow_redirects=False
    )
    assert response.status_code == 303
    assert "error=Category+and+date+are+required" in response.headers["Location"]

    # Test empty date
    updated_data_no_date = {
        "amount": 10.0,
        "category": "Food",
        "date": "",
        "description": "Test"
    }
    response = authenticated_client.post(
        f"/expenses/{test_expense['id']}/edit",
        data=updated_data_no_date,
        follow_redirects=False
    )
    assert response.status_code == 303
    assert "error=Category+and+date+are+required" in response.headers["Location"]
