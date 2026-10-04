"""
Run once to create data/farmers.db with the correct table structure.
Real farmer data is inserted automatically by the frontend signup form.

Usage: python -m scripts.init_db
"""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "farmers.db")


def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS farmers (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            name          TEXT NOT NULL,
            password      TEXT NOT NULL,
            crop          TEXT NOT NULL,
            soil_type     TEXT,
            planting_date TEXT,
            place_name    TEXT,
            pincode       INTEGER,
            lat           REAL,
            lon           REAL
        )
    """)

    conn.commit()
    conn.close()
    print(f"[OK] Database ready at: {os.path.abspath(DB_PATH)}")


if __name__ == "__main__":
    init_db()
