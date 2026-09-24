# Spec: Profile Page

## Overview
The Profile Page allows logged-in users to view and manage their account details. It provides a centralized place for users to see their registered name and email, and serves as a foundation for future account management features (like password changes or profile updates).

## Depends on
- Step 2: Registration
- Step 3: Login and Logout

## Routes
- `GET /profile` — Displays user profile information — logged-in

## Database changes
No database changes.

## Templates
- **Create:** `templates/profile.html`
- **Modify:** `templates/base.html` (to add a link to the profile page in the navigation bar when logged in)

## Files to change
- `main.py`: Implement the `/profile` route to fetch the current user's data from the database.

## Files to create
- `templates/profile.html`

## New dependencies
No new dependencies.

## Rules for implementation
- No SQLAlchemy or ORMs
- Parameterised queries only
- Passwords hashed with werkzeug
- Use CSS variables — never hardcode hex values
- All templates extend `base.html`

## Definition of done
- [ ] Logged-in user can navigate to `/profile` and see their correct name and email.
- [ ] Unauthenticated user attempting to access `/profile` is redirected to the login page.
- [ ] Profile page layout is consistent with the rest of the application and uses `base.html`.
- [ ] Profile link is visible in the navigation bar only when the user is authenticated.
