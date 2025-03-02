import sqlite3

def create_admin_user(username='AdminUser'):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (username, password, is_admin) VALUES (?, ?, ?)", (username, 'adminpassword', True))
    conn.commit()
    conn.close()
    print(f"Admin user '{username}' created successfully!")

if __name__ == "__main__":
    create_admin_user()
