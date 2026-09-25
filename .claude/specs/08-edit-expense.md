# Spec: Edit Expense

## Overview
This feature allows users to modify existing expense records. Users can correct errors in amount, category, date, or description. This is a critical part of the Spendly roadmap to ensure data accuracy and user control over their financial tracking.

## Depends on
- 07-add-expense

## Routes
- `GET /expenses/{id}/edit` — Display a form with the current details of the expense. Only accessible if the expense belongs to the logged-in user. (logged-in)
- `POST /expenses/{id}/edit` — Process the update of the expense details. Only accessible if the expense belongs to the logged-in user. (logged-in)

## Database changes
No database changes. Existing `expenses` table supports updates.

## Templates
- **Create:** `templates/edit_expense.html` (A form similar to `add_expense.html` but pre-filled with existing data).
- **Modify:** No existing templates need modification.

## Files to change
- `main.py`: Implement the GET and POST routes for editing expenses.
- `database/db.py`: Add a function `get_expense_by_id` to fetch a single expense and `update_expense` to modify an existing record.

## Files to create
- `templates/edit_expense.html`

## New dependencies
No new dependencies.

## Rules for implementation
- No SQLAlchemy or ORMs
- Parameterised queries only
- Passwords hashed with werkzeug
- Use CSS variables — never hardcode hex values
- All templates extend `base.html`
- **Security:** Verify that the expense being edited actually belongs to the `user_id` from the session before fetching or updating.

## Definition of done
- [ ] Navigating to `/expenses/<id>/edit` for a valid expense belonging to the user loads the edit form with pre-filled data.
- [ ] Attempting to access `/expenses/<id>/edit` for an expense that does not belong to the user results in a 404 or 403 error.
- [ ] Submitting the edit form successfully updates the expense in the database.
- [ ] After a successful update, the user is redirected back to the profile page.
- [ ] Form validation ensures amount is greater than zero and required fields (category, date) are present.
