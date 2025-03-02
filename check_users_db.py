import sqlite3

def check_users_db():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    # Check the structure of the users table
    cursor.execute("PRAGMA table_info(users)")
    columns = cursor.fetchall()
    print("Users table structure:")
    for column in columns:
        print(column)
    
    # Print the contents of the users table
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    print("\nUsers table contents:")
    for user in users:
        print(user)
    
    conn.close()

if __name__ == "__main__":
    check_users_db()
```
### Step 5: Verify the Changes

Run the `check_users_db.py` script to verify that the `is_admin` column has been added and that the table contains the correct data.
