import sqlite3
import os

db_path = os.path.join(
    os.path.dirname(__file__),
    "attendance.db"
)

conn = sqlite3.connect(db_path)

cursor = conn.cursor()

cursor.execute("""
SELECT section, COUNT(*)
FROM students
GROUP BY section
""")

for row in cursor.fetchall():
    print(row)

conn.close()