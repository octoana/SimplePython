import sqlite3

# Connect to an in-memory SQLite database for testing
conn = sqlite3.connect(":memory:")
cursor = conn.cursor()

# Create a sample users table
cursor.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, username TEXT, password TEXT)")
cursor.execute("INSERT INTO users (username, password) VALUES ('admin', 'securepass')")
conn.commit()

# UNSANITIZED User Input (Vulnerable to SQL Injection)
username = input("Enter your username: ")
query = f"SELECT * FROM users WHERE username = '{username}'"
print("\n[DEBUG] Executing Query:", query)  # Debugging purpose

cursor.execute(query)
result = cursor.fetchall()

if result:
    print("\n User found:", result)
else:
    print("\n No user found.")

conn.close()
