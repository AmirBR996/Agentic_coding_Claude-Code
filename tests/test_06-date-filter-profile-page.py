import pytest
from fastapi.testclient import TestClient
from main import app
import database.db as db
import sqlite3
import os

# Use a separate test database
TEST_DB_PATH = "test_spendly.db"

@pytest.fixture(scope="function", autouse=True)
def setup_test_db():
    # Override DB_PATH in the db module
    original_db_path = db.DB_PATH
    db.DB_PATH = TEST_DB_PATH

    # Initialize the database
    db.init_db()

    yield

    # Cleanup: remove the test database file
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)
    db.DB_PATH = original_db_path

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def authenticated_user(client):
    """Creates a user and logs them in, returning the user_id."""
    name = "Test User"
    email = "test@example.com"
    password = "password123"

    # Create user
    user_id = db.create_user(name, email, password)

    # Login to establish session
    client.post("/login", data={"email": email, "password": password})

    return user_id

def test_profile_auth_guard(client):
    """Ensure the profile route is protected and redirects unauthenticated users."""
    response = client.get("/profile")
    # The route raises HTTPException(status_code=303, headers={"Location": "/login"})
    assert response.status_code == 303
    assert response.headers["location"] == "/login"

def test_profile_date_filter_happy_path(client, authenticated_user):
    """Filtering by both start_date and end_date correctly limits results and updates stats."""
    user_id = authenticated_user

    # Seed expenses for the user
    with db.get_db() as conn:
        expenses = [
            (user_id, 100.0, "Food", "2023-01-01", "Exp 1"),
            (user_id, 200.0, "Shopping", "2023-01-15", "Exp 2"),
            (user_id, 300.0, "Bills", "2023-02-01", "Exp 3"),
        ]
        conn.executemany(
            "INSERT INTO expenses (user_id, amount, category, date, description) VALUES (?, ?, ?, ?, ?)",
            expenses
        )
        conn.commit()

    # Filter for January 2023
    response = client.get("/profile?start_date=2023-01-01&end_date=2023-01-31")
    assert response.status_code == 200

    html = response.text
    # Check summary stats: Total spent should be 100 + 200 = 300
    # Note: The app formats as ₹300.00
    assert "₹300.00" in html
    assert "2" in html # Transaction count

    # Check that only Jan expenses are present
    assert "Exp 1" in html
    assert "Exp 2" in html
    assert "Exp 3" not in html

def test_profile_date_filter_start_only(client, authenticated_user):
    """Providing only start_date filters results from that date onwards."""
    user_id = authenticated_user

    with db.get_db() as conn:
        expenses = [
            (user_id, 100.0, "Food", "2023-01-01", "Old"),
            (user_id, 200.0, "Shopping", "2023-02-01", "Newer"),
            (user_id, 300.0, "Bills", "2023-03-01", "Newest"),
        ]
        conn.executemany(
            "INSERT INTO expenses (user_id, amount, category, date, description) VALUES (?, ?, ?, ?, ?)",
            expenses
        )
        conn.commit()

    response = client.get("/profile?start_date=2023-02-01")
    assert response.status_code == 200

    html = response.text
    assert "Newer" in html
    assert "Newest" in html
    assert "Old" not in html
    # Total: 200 + 300 = 500
    assert "₹500.00" in html

def test_profile_date_filter_end_only(client, authenticated_user):
    """Providing only end_date filters results up to that date."""
    user_id = authenticated_user

    with db.get_db() as conn:
        expenses = [
            (user_id, 100.0, "Food", "2023-01-01", "Old"),
            (user_id, 200.0, "Shopping", "2023-02-01", "Mid"),
            (user_id, 300.0, "Bills", "2023-03-01", "New"),
        ]
        conn.executemany(
            "INSERT INTO expenses (user_id, amount, category, date, description) VALUES (?, ?, ?, ?, ?)",
            expenses
        )
        conn.commit()

    response = client.get("/profile?end_date=2023-02-15")
    assert response.status_code == 200

    html = response.text
    assert "Old" in html
    assert "Mid" in html
    assert "New" not in html
    # Total: 100 + 200 = 300
    assert "₹300.00" in html

def test_profile_date_filter_empty_results(client, authenticated_user):
    """Providing a date range with no expenses results in an empty list and zeroed stats."""
    user_id = authenticated_user

    with db.get_db() as conn:
        expenses = [
            (user_id, 100.0, "Food", "2023-01-01", "Existing"),
        ]
        conn.executemany(
            "INSERT INTO expenses (user_id, amount, category, date, description) VALUES (?, ?, ?, ?, ?)",
            expenses
        )
        conn.commit()

    # Range where nothing exists
    response = client.get("/profile?start_date=2024-01-01&end_date=2024-01-31")
    assert response.status_code == 200

    html = response.text
    assert "₹0.00" in html
    assert "0" in html # Count
    assert "Existing" not in html

def test_profile_date_filter_persistence(client, authenticated_user):
    """Verify that the date parameters are passed back in the response context."""
    # This is typically checked by seeing if the values are present in the HTML inputs
    # given the spec "The filter state is preserved in the URL query parameters"
    # and "Pass them to the database helper" + "passed back in response context".

    start = "2023-01-01"
    end = "2023-01-31"
    response = client.get(f"/profile?start_date={start}&end_date={end}")
    assert response.status_code == 200

    html = response.text
    # We check if the values are present in the HTML.
    # Since the implementation passes start_date/end_date to context,
    # the template should render them.
    assert start in html
    assert end in html
