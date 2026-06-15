import sqlite3
import os

db_path = os.path.join(
    os.path.dirname(__file__),
    "attendance.db"
)

conn = sqlite3.connect(db_path)

cursor = conn.cursor()

# Students Table
cursor.execute("""
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    roll_no TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    section TEXT NOT NULL
)
""")

# Attendance Table
cursor.execute("""
CREATE TABLE IF NOT EXISTS attendance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    attendance_date TEXT NOT NULL,
    status TEXT NOT NULL,
    section TEXT NOT NULL,
    FOREIGN KEY(student_id)
    REFERENCES students(id)
)
""")

conn.commit()
conn.close()

print("Database Created Successfully")