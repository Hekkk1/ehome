import streamlit as st
import sqlite3

# Initialize the database connection
def init_user_db():
    conn = sqlite3.connect('users.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL,
        is_admin BOOLEAN NOT NULL DEFAULT 0
    )
    ''')
    conn.commit()
    return conn

conn = init_user_db()

def sign_up():
    st.title("Sign Up")
    username = st.text_input("Username", key="sign_up_username")
    password = st.text_input("Password", type="password", key="sign_up_password")
    confirm_password = st.text_input("Confirm Password", type="password", key="sign_up_confirm_password")
    if st.button("Sign Up", key="sign_up_button"):
        if username and password:
            cursor = conn.cursor()
            try:
                cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
                conn.commit()
                st.success("User registered successfully! Please log in.")
            except sqlite3.IntegrityError:
                st.error("Username already exists. Please choose a different username.")
        else:
            st.error("Please fill in both fields.")
    st.write("Sign-up form goes here")

if __name__ == "__main__":
    sign_up()