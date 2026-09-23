---

description: Create a single dummy Nepali user in the database
allowed-tools: Read, Bash(python3:*)
------------------------------------

Read `database/db.py` to understand the `users` table schema and the `get_db()` helper.

Then write and run a Python script using Bash that:

1. Generates a realistic random Nepali user using common Nepali names from different regions:

   * Name: a realistic Nepali first + last name
   * Email: derived from the name with a random 2–3 digit number suffix
     (e.g. `suman.shrestha91@gmail.com`)
   * Password: `"password123"` hashed using Werkzeug's `generate_password_hash`
   * `created_at`: current datetime

2. Checks if the generated email already exists in the `users` table.
   If it already exists, regenerate the email until a unique email is found.

3. Inserts the user into the database using the same `get_db()` pattern found in `database/db.py`.

4. Uses parameterised SQL queries only.

5. Commits the transaction after successful insertion.

6. Prints confirmation:

   * `id`
   * `name`
   * `email`
