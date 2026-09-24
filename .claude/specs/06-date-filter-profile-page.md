# Spec: Date Filter Profile Page

## Overview
This feature adds the ability for users to filter their expenses on the profile page by date range. Currently, the profile page displays all expenses for the user. Adding a date filter allows users to analyze their spending habits over specific periods (e.g., last 30 days, this month, or a custom range), improving the utility of the spending summary and transaction list.

## Depends on
- 04-profile-page-design (Profile page implementation)
- 03-authentication (Logged-in user sessions)

## Routes
No new routes. The existing `GET /profile` route will be modified to accept optional query parameters for date filtering.
- `GET /profile?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD` — filters expenses by date range — logged-in

## Database changes
No database changes. The existing `expenses` table already has a `date` column (TEXT) that can be used for filtering.

## Templates
- **Modify:** `templates/profile.html` — Add a date filter form (two date inputs and a submit button) at the top of the transaction list or summary section.

## Files to change
- `main.py`: Update the `profile` route to handle `start_date` and `end_date` query parameters and pass them to the database helper.
- `database/db.py`: Update `get_expenses_by_user` to optionally accept date filters.
- `templates/profile.html`: Add the filter UI.

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
- Handle empty date inputs gracefully (default to all time if both are missing).
- Ensure the date inputs use `type="date"` for native browser pickers.

## Definition of done
- [ ] Profile page renders a date filter form with "From" and "To" inputs.
- [ ] Submitting the form with valid dates filters the transaction list and updates summary stats (Total Spent, Transaction Count, Top Category) to reflect only the filtered range.
- [ ] Clearing the filters returns the view to show all expenses.
- [ ] The application does not crash when invalid or partial dates are provided.
- [ ] The filter state is preserved in the URL query parameters.
