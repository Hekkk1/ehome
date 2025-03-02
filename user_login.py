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

def login():
    if 'user_logged_in' not in st.session_state:
        st.session_state.user_logged_in = False
        st.session_state.is_admin = False

    if st.session_state.user_logged_in:
        st.sidebar.success(f"Logged in as {st.session_state.username}")
        if st.session_state.is_admin:
            st.sidebar.info("Admin Console")
    else:
        st.sidebar.title("Login")
        username = st.sidebar.text_input("Username")
        password = st.sidebar.text_input("Password", type="password")
        if st.sidebar.button("Login"):
            cursor = conn.cursor()
            cursor.execute("SELECT id, username, password, is_admin FROM users WHERE username = ? AND password = ?", (username, password))
            user = cursor.fetchone()
            if user:
                st.session_state.user_logged_in = True
                st.session_state.username = username
                st.session_state.is_admin = user[3]  # Set to True for admin, False for regular user
                st.sidebar.success(f"Logged in as {username}")
                if st.session_state.is_admin:
                    st.sidebar.info("Admin Console")
            else:
                st.sidebar.error("Incorrect username or password. Please try again.")
        st.sidebar.markdown("[Sign Up](#sign-up)")

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

def logout():
    if st.sidebar.button("Logout"):
        st.session_state.user_logged_in = False
        st.session_state.is_admin = False
        st.sidebar.success("Logged out successfully!")
