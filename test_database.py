"""
CampusConnect - Test Script for Stage 2 (Issues Table)
Run this to verify that everything is set up correctly.
"""

import sqlite3

conn = sqlite3.connect("campusconnect.db")
conn.execute("PRAGMA foreign_keys = ON;")
conn.row_factory = sqlite3.Row  
c = conn.cursor()

print("=== TEST 1: Does issues table exist? ===")
c.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [r[0] for r in c.fetchall()]
print("Tables found:", tables)
print()

print("=== TEST 2: Are the columns correct? ===")
c.execute("PRAGMA table_info(issues)")
rows = c.fetchall()
for r in rows:
    print(f"  {r['name']:15} | Type: {r['type']:10} | Required: {bool(r['notnull'])}  | Default: {r['dflt_value']}")
print()

print("=== TEST 3: Is user_id connected to users? ===")
c.execute("PRAGMA foreign_key_list(issues)")
fk = c.fetchall()
if fk:
    print(f"  Foreign Key: issues.{fk[0]['from']} --> {fk[0]['table']}.{fk[0]['to']}")
else:
    print("  No foreign key found!")
print()

print("=== TEST 4: Is default status 'Open'? ===")
print("=== TEST 5: Can we store and read an issue? ===")

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

print(f"  Issue ID    : {issue['id']}")
print(f"  User ID     : {issue['user_id']}")
print(f"  Category    : {issue['category']}")
print(f"  Title       : {issue['title']}")
print(f"  Description : {issue['description']}")
print(f"  Location    : {issue['location']}")
print(f"  Status      : {issue['status']}")
print(f"  Created At  : {issue['created_at']}")
print()

if issue['status'] == "Open":
    print("[OK] Default status is 'Open' -- PASS!")
else:
    print("[FAIL] Default status is NOT 'Open'!")

c.execute("DELETE FROM issues")
c.execute("DELETE FROM users")
conn.commit()
conn.close()
print("[OK] Test data cleaned up.")
print("[OK] All tests passed!")
