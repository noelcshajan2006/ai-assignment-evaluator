import sqlite3

conn = sqlite3.connect("assignments.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS assignments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_name TEXT,
    content TEXT,
    score INTEGER,
    feedback TEXT
)
""")

conn.commit()