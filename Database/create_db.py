import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), "attendance.db")

conn = sqlite3.connect(db_path)

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    roll_no TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    section TEXT NOT NULL
);
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS attendance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER,
    attendance_date TEXT,
    status TEXT,
    FOREIGN KEY(student_id)
    REFERENCES students(id)
)
""")
conn.commit()
conn.close()

print("Database Created Successfully")