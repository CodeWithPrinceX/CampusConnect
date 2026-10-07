"""
CampusConnect - Database Setup
This file creates the SQLite database and tables.
Your FastAPI backend teammate can import from this file.
"""

import sqlite3

def get_connection():
    """
    Opens a connection to the SQLite database file.
    If the file doesn't exist yet, SQLite will create it automatically.
    """
    connection = sqlite3.connect("campusconnect.db")
    return connection

def create_tables():
    """
    Creates the 'users' table if it doesn't already exist.
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

    connection.commit()
    connection.close()
    print("[OK] users table created successfully!")

if __name__ == "__main__":
    create_tables()
