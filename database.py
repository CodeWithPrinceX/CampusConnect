"""
CampusConnect - Database Setup
This file creates the SQLite database and tables (users + issues).
Your FastAPI backend teammate can import from this file.
"""

import sqlite3

def get_connection():
    """
    Opens a connection to the SQLite database file.
    If the file doesn't exist yet, SQLite will create it automatically.
    """
    connection = sqlite3.connect("campusconnect.db")
    connection.execute("PRAGMA foreign_keys = ON;")
    return connection

def create_tables():
    """
    Creates the 'users' and 'issues' tables if they don't already exist.
    This is safe to call multiple times — it won't erase existing data.
    """
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id             INTEGER PRIMARY KEY AUTOINCREMENT,
            name           TEXT    NOT NULL,
            email          TEXT    NOT NULL UNIQUE,
            password_hash  TEXT    NOT NULL
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS issues (
            id             INTEGER  PRIMARY KEY AUTOINCREMENT,
            user_id        INTEGER  NOT NULL,
            category       TEXT     NOT NULL,
            title          TEXT     NOT NULL,
            description    TEXT     NOT NULL,
            location       TEXT,                            <--- (NEW COLUMN ADDED HERE)
            status         TEXT     NOT NULL DEFAULT 'Open',
            created_at     DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        );
    """)
    
    cursor.execute("PRAGMA table_info(issues);")
    columns = [row[1] for row in cursor.fetchall()]

    if "location" not in columns:
        cursor.execute("ALTER TABLE issues ADD COLUMN location TEXT;")
        print("[OK] Added missing 'location' column to issues table.")

    connection.commit()
    connection.close()
    print("[OK] users table ready!")
    print("[OK] issues table ready!")

if __name__ == "__main__":
    create_tables()