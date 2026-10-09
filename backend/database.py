"""
CampusConnect - Database Setup

This file creates the SQLite database and tables (users + issues).
The FastAPI backend can import get_connection() from this file.
"""

import sqlite3
from pathlib import Path


# Always use the database file inside the backend folder
BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "campusconnect.db"


def get_connection():
    """
    Opens a connection to the SQLite database.
    """
    connection = sqlite3.connect(DB_PATH)
    connection.execute("PRAGMA foreign_keys = ON;")
    return connection


def create_tables():
    """
    Creates the users and issues tables if they don't already exist.
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
            location       TEXT,
            status         TEXT     NOT NULL DEFAULT 'Open',
            created_at     DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        );
    """)

    # Safe migration: add location column if it doesn't exist
    cursor.execute("PRAGMA table_info(issues);")
    columns = [row[1] for row in cursor.fetchall()]
    if "location" not in columns:
        cursor.execute("ALTER TABLE issues ADD COLUMN location TEXT;")
        print("[OK] Added 'location' column to existing database.")

    connection.commit()
    connection.close()

    print("[OK] users table created successfully!")
    print("[OK] issues table created successfully!")


if __name__ == "__main__":
    create_tables()
