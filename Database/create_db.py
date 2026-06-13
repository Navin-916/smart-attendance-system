import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), "attendance.db")

conn = sqlite3.connect(db_path)

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    roll_no TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL
)
""")

conn.commit()
conn.close()

print("Database Created Successfully")