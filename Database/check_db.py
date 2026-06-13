import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), "attendance.db")

print("Database Path:")
print(db_path)

conn = sqlite3.connect(db_path)

cursor = conn.cursor()

cursor.execute("""
SELECT name
FROM sqlite_master
WHERE type='table'
""")

tables = cursor.fetchall()

print("\nTables Found:")
print(tables)

conn.close()