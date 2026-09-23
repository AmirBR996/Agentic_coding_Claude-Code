---

description: Seed realistic dummy expenses for a specific user

argument-hint: "<user_id> <count> <months>"

allowed-tools: Read, Bash(python3:*)

---

Read `database/db.py` to understand the expenses table schema, the database connection pattern, and the database file name.

User input: `$ARGUMENTS`

## Step 1 — Parse arguments

Extract from `$ARGUMENTS`:

* `user_id` — integer
* `count` — integer, number of expenses to create
* `months` — integer, how many past months to spread them across

If any argument is missing or not a valid integer, stop and say:

"Usage: /seed-expenses <user_id> <count> <months>

Example: /seed-expenses 1 50 6"

## Step 2 — Verify user exists

Before generating anything, confirm that the `user_id` exists in the `users` table.

If the user does not exist, stop and say:

"No user found with id <user_id>."

## Step 3 — Generate and insert expenses

Write and run a Python script that:

1. Spreads expenses randomly across the past `<months>` months.

2. Uses realistic Nepali categories, descriptions, and amounts in Nepalese Rupees (NPR):

   * Food: रु. 100–1,500
   * Transport: रु. 30–800
   * Bills: रु. 300–5,000
   * Health: रु. 200–3,000
   * Entertainment: रु. 200–2,500
   * Shopping: रु. 300–8,000
   * Other: रु. 100–2,000

3. Uses realistic Nepali expense descriptions, such as:

   * Food: momo, dal bhat, chowmein, tea, coffee, lunch, snacks, groceries
   * Transport: bus fare, Pathao ride, InDrive ride, taxi, fuel
   * Bills: electricity bill, internet bill, mobile recharge, water bill, rent
   * Health: medicine, pharmacy, doctor consultation, health checkup
   * Entertainment: movie ticket, restaurant, gaming, streaming subscription
   * Shopping: clothes, shoes, groceries, electronics, household items
   * Other: stationery, gifts, miscellaneous expenses

4. Distributes categories roughly proportionally:

   * Food should be the most common.
   * Transport and Bills should be moderately common.
   * Shopping and Other should have medium frequency.
   * Health and Entertainment should be the least common.

5. Uses the database connection pattern from `database/db.py`.
   Do not hardcode the database filename.

6. Uses parameterised queries only.
   Do not use string formatting or string interpolation in SQL queries.

7. Inserts all expenses in a single transaction.
   If any insert fails, roll back the entire transaction so that no partial data is stored.

8. Generates dates randomly within the specified number of past months.

9. Ensures all generated expenses belong to the specified `user_id`.

## Step 4 — Confirm

After successful insertion, print:

* Number of expenses inserted
* Date range of the generated expenses
* A sample of 5 inserted records

The output should clearly show the expense ID, date, category, description, and amount for the sample records.

