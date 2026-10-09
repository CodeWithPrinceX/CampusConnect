import sqlite3
import os
import database

TEST_DB = "test_campusconnect.db"

def get_test_connection():
    conn = sqlite3.connect(TEST_DB)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

database.get_connection = get_test_connection
database.create_tables()

conn = database.get_connection()
conn.row_factory = sqlite3.Row
c = conn.cursor()

try:
    print("Running database checks...\n")

    c.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [r[0] for r in c.fetchall()]
    assert "issues" in tables, "Issues table was not created."
    assert "users" in tables, "Users table was not created."
    print("  [PASS] Tables exist.")

    c.execute("PRAGMA table_info(issues)")
    columns = [r["name"] for r in c.fetchall()]
    required_columns = ["id", "user_id", "category", "title", "description", "location", "status", "created_at"]
    for col in required_columns:
        assert col in columns, f"Column '{col}' is missing from the issues table."
    print("  [PASS] All columns (including location) are present.")

    c.execute("PRAGMA foreign_key_list(issues)")
    fk = c.fetchall()
    assert len(fk) > 0, "No foreign keys found in the issues table."
    assert fk[0]["from"] == "user_id", "Foreign key is not on the 'user_id' column."
    assert fk[0]["table"] == "users", "Foreign key does not link to the 'users' table."
    print("  [PASS] Foreign key is set up correctly.")

    c.execute(
        "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
        ("Test User", "test@college.edu", "hashed_pw_123")
    )
    user_id = c.lastrowid

    c.execute(
        "INSERT INTO issues (user_id, category, title, description, location) VALUES (?, ?, ?, ?, ?)",
        (user_id, "Classroom", "Projector not working", "Room 301 projector is broken", "Room 301")
    )
    conn.commit()

    c.execute("SELECT * FROM issues WHERE id = ?", (c.lastrowid,))
    issue = c.fetchone()

    assert issue is not None, "Failed to read the issue back from the database."
    assert issue["status"] == "Open", f"Expected default status 'Open', but got '{issue['status']}'."
    assert issue["location"] == "Room 301", "Location was not saved correctly."
    print("  [PASS] Data insertion and default status ('Open') work correctly.\n")

    print("[SUCCESS] All database tests passed!")

except AssertionError as e:
    print(f"\n[FAIL] Test failed: {e}")

finally:
    conn.close()
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)
        print(f"[CLEANUP] Deleted temporary test database: {TEST_DB}")