# Spec: Login

## Overview
This feature implements the authentication mechanism for Spendly, allowing users to securely access their accounts. It enables users to verify their identity using their email and password, establishing a session that allows them to manage their personal expenses.

## Depends on
Step 01 (Database Setup) and Step 02 (User Registration) must be complete to ensure the users table exists and contains hashed passwords.

## Routes
- `GET /login` — Displays the login form — public
- `POST /login` — Processes credentials and creates a session — public
- `GET /logout` — Terminates the user session — logged-in

## Database changes
No database changes.

## Templates
- **Create:** No new templates (uses existing `login.html`).
- **Modify:** `login.html` to ensure the form points to the correct POST endpoint.

## Files to change
- `main.py`: Implement POST `/login` and `/logout` routes, and session management.

## Files to create
No new files.

## New dependencies
No new dependencies.

## Rules for implementation
- No SQLAlchemy or ORMs
- Parameterised queries only
- Passwords hashed with werkzeug
- Use CSS variables — never hardcode hex values
- All templates extend `base.html`

## Definition of done
- [ ] Navigating to `/login` displays the login page.
- [ ] Submitting valid credentials redirects the user to a protected page (e.g., `/profile`).
- [ ] Submitting invalid credentials displays an error message.
- [ ] Navigating to `/logout` clears the session and redirects to the landing page.
- [ ] Accessing `/profile` without logging in redirects the user to `/login`.
