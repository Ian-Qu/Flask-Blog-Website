import sqlite3
import uuid

# Create Connection
connection = sqlite3.connect('database.db')

# Read SQL
with open('schema.sql') as f:
    connection.executescript(f.read())

cur = connection.cursor()

# Generate UUIDs
first_id = str(uuid.uuid4())
second_id = str(uuid.uuid4())

cur.execute("INSERT INTO posts (id, title, content) VALUES (?, ?, ?)",
            (first_id, 'First Post', 'Content for the first post')
            )

cur.execute("INSERT INTO posts (id, title, content) VALUES (?, ?, ?)",
            (second_id, 'Second Post', 'Content for the second post')
            )

cur.execute("INSERT INTO changes (id, title, content, change_made) VALUES (?, ?, ?, ?)",
            (first_id, 'First Post', 'Content for the first post', 'Database Initialized: ')
            )

cur.execute("INSERT INTO changes (id, title, content, change_made) VALUES (?, ?, ?, ?)",
            (second_id, 'Second Post', 'Content for the second post', 'Database Initialized: ')
            )

connection.commit()
connection.close()