import sqlite3

conn = sqlite3.connect("messages.db")

cursor = conn.cursor()

cursor.execute("""
ALTER TABLE messages
ADD COLUMN status TEXT DEFAULT 'new'
""")

conn.commit()

conn.close()

print("Status column added successfully!")