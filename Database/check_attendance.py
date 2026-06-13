import sqlite3
import os

db_path = os.path.join(
    os.path.dirname(__file__),
    "attendance.db"
)

conn = sqlite3.connect(db_path)

cursor = conn.cursor()

cursor.execute("""
SELECT *
FROM attendance
""")

rows = cursor.fetchall()

print(f"Records Found: {len(rows)}")

for row in rows[:10]:
    print(row)

conn.close()