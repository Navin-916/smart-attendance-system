import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), "attendance.db")

conn = sqlite3.connect(db_path)

cursor = conn.cursor()

cursor.execute("SELECT roll_no, name FROM students")

students = cursor.fetchall()

print(f"Total Students: {len(students)}\n")

for student in students:
    print(student)

conn.close()