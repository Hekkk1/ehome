import sqlite3

def initialize_db():
    try:
        conn = sqlite3.connect('products.db')
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                price REAL NOT NULL,
                available BOOLEAN NOT NULL,
                image TEXT,
                description TEXT,
                color TEXT,
                size TEXT
            )
        ''')
        conn.commit()
        return conn
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return None

if __name__ == "__main__":
    conn = initialize_db()
    if conn:
        print("Database initialized successfully")
    else:
        print("Failed to initialize database")
