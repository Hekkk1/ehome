import sqlite3

def alter_users_table():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute("ALTER TABLE users ADD COLUMN is_admin BOOLEAN NOT NULL DEFAULT 0")
    conn.commit()
    conn.close()
    print("Added 'is_admin' column to 'users' table successfully!")

if __name__ == "__main__":
    alter_users_table()
