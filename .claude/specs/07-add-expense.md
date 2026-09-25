# Spec: Add Expense

## Overview
This feature allows authenticated users to record new expenses. It provides a user-friendly form to input the amount, category, date, and a brief description, ensuring that users can maintain an up-to-date record of their spending.

## Depends on
- `04-profile-page-design` (for user context and existing expense structure)
- `database-setup` (for the expenses table)

## Routes
- `GET /expenses/add` — Renders the add expense form — logged-in
- `POST /expenses/add` — Processes the form submission and saves the expense to the database — logged-in

## Database changes
No database changes. The `expenses` table already contains the necessary columns: `user_id`, `amount`, `category`, `date`, and `description`.

## Templates
- **Create:** `templates/add_expense.html` — The form for adding a new expense.
- **Modify:** `templates/base.html` — Add a link to the "Add Expense" page in the navigation/profile area.

## Files to change
- `main.py` — Implement the GET and POST handlers for `/expenses/add`.
- `database/db.py` — Add a helper function `add_expense(user_id, amount, category, date, description)`.

## Files to create
- `templates/add_expense.html`

## New dependencies
No new dependencies.

## Rules for implementation
- No SQLAlchemy or ORMs
- Parameterised queries only
- Passwords hashed with werkzeug
- Use CSS variables — never hardcode hex values
- All templates extend `base.html`
- Validate that `amount` is a positive number.
- Ensure the `date` field defaults to today's date.

## Definition of done
- [ ] Navigating to `/expenses/add` while logged in renders a form.
- [ ] Submitting a valid expense redirects the user to the profile page.
- [ ] The newly added expense appears in the transaction list on the profile page.
- [ ] Attempting to access `/expenses/add` while logged out redirects to `/login`.
- [ ] Form validation prevents submission of negative amounts or empty required fields.
