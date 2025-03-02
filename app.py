import streamlit as st
import pandas as pd
import os
from PIL import Image
import io
import sqlite3
import base64
from datetime import datetime
from user_login import login, logout

# Set page configuration
st.set_page_config(
    page_title="Product Showcase",
    page_icon="🛍️",
    layout="wide"
)

# Initialize the database connection
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

conn = initialize_db()
if conn:
    print("Database initialized successfully")
else:
    st.error("Failed to initialize database")
    st.stop()

# Function to convert image to base64 for storing in the database
def image_to_base64(img):
    if img.mode in ("RGBA", "LA"):
        background = Image.new(img.mode[:-1], img.size, (255, 255, 255))
        background.paste(img, img.split()[-1])
        img = background
    buffered = io.BytesIO()
    img.save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue()).decode()

# Function to convert base64 to image for displaying
def base64_to_image(base64_string):
    return Image.open(io.BytesIO(base64.b64decode(base64_string)))

# Function to load CSS from a file
def load_css(file_path):
    with open(file_path) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Load CSS
load_css("styles.css")

# Display the logo using Streamlit's st.image with a very small width and move it up more
logo_path = os.path.join(os.path.dirname(__file__), 'logo.png')
if os.path.exists(logo_path):
    st.markdown("<div style='margin-top: -40px;'></div>", unsafe_allow_html=True)
    st.image(logo_path, use_container_width=False, width=50)
else:
    st.warning("Logo image not found. Please check the path.")

# Initialize session state variables
if 'user_logged_in' not in st.session_state:
    st.session_state.user_logged_in = False
if 'is_admin' not in st.session_state:
    st.session_state.is_admin = False
if 'cart' not in st.session_state:
    st.session_state.cart = []

# Function to initialize the shopping cart
def init_cart():
    if 'cart' not in st.session_state:
        st.session_state.cart = []

# Function to add items to the cart
def add_to_cart(product_id, name, price, image):
    st.session_state.cart.append({
        'id': product_id,
        'name': name,
        'price': price,
        'image': image
    })

# Function to display the shopping cart
def display_cart():
    if not st.session_state.cart:
        st.info("Your cart is empty.")
    else:
        for item in st.session_state.cart:
            col1, col2 = st.columns([1, 4])
            with col1:
                st.image(base64_to_image(item['image']), width=50, output_format="JPEG")
            with col2:
                st.markdown(f"**{item['name']}**")
                st.markdown(f"**Price:** {item['price']:.2f} ₮")
            st.markdown("---")

# Navigation
page = st.sidebar.selectbox("Navigation", ["Main Page", "Sign Up", "Shopping Cart"])

if page == "Main Page":
    # Initialize user login and shopping cart
    login()
    init_cart()
    display_cart()

    # Function to remove a product from the database
    def remove_product(product_id):
        cursor = conn.cursor()
        cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))
        conn.commit()
        st.success(f"Product {product_id} deleted successfully!")
        st.experimental_rerun()

    # Display products for all users
    st.markdown("<h3 class='main-title'>Hot selling products 🔥🔥🔥</h3>", unsafe_allow_html=True)

    # Get products from the database
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, price, available, image, description, color, size FROM products")
    products = cursor.fetchall()

    if not products:
        st.info("No products available. Add some from the Admin Panel.")
    else:
        # Display products in a grid (3 columns)
        col1, col2, col3 = st.columns(3)
        cols = [col1, col2, col3]
        
        for i, product in enumerate(products):
            product_id, name, price, available, image_base64, description, color, size = product
            col = cols[i % 3]
            
            with col:
                with st.container():
                    st.markdown("<div class='product-card'>", unsafe_allow_html=True)
                    
                    # Display the image - using use_container_width instead of deprecated use_column_width
                    image = base64_to_image(image_base64)
                    st.image(image, caption="", use_container_width=True, output_format="JPEG")
                    
                    # Display product information
                    st.markdown(f"### {name}")
                    st.markdown(f"<div class='product-price'>{price:.2f} ₮</div>", unsafe_allow_html=True)
                    
                    availability_class = "available" if available else "unavailable"
                    availability_text = "In Stock" if available else "Out of Stock"
                    st.markdown(f"<div class='product-availability {availability_class}'>{availability_text}</div>", unsafe_allow_html=True)
                    
                    if description:
                        with st.expander("Details"):
                            st.write(description)
                    
                    if color:
                        st.markdown(f"**Color:** {color}")
                    
                    if size:
                        st.markdown(f"**Size:** {size}")
                    
                    st.markdown("</div>", unsafe_allow_html=True)
                    st.markdown("<br>", unsafe_allow_html=True)
                    
                    if available:
                        if st.button(f"Add to Cart", key=f"add_to_cart_{product_id}"):
                            add_to_cart(product_id, name, price, image_base64)
                            st.success(f"Added {name} to cart!")

    # Check if the user is logged in
    if st.session_state.user_logged_in:
        if st.session_state.is_admin:
            st.markdown("<h1 class='main-title'>Admin Panel</h1>", unsafe_allow_html=True)
            
            # Add new product form
            st.subheader("Add New Product")
            with st.form("add_product_form"):
                name = st.text_input("Product Name")
                price = st.number_input("Price (₮)", min_value=0.0, max_value=10000000.0, step=1000.0)
                available = st.checkbox("Available", value=True)
                description = st.text_area("Description")
                color = st.text_input("Color")
                size = st.text_input("Size")
                uploaded_file = st.file_uploader("Upload Product Image", type=["jpg", "jpeg", "png"])
                
                submitted = st.form_submit_button("Add Product")
                
                if submitted:
                    if name and price >= 0 and uploaded_file:
                        # Process the image
                        image = Image.open(uploaded_file)
                        # Resize image to standardize
                        image = image.resize((600, 600), Image.LANCZOS)
                        image_base64 = image_to_base64(image)
                        
                        # Insert into database
                        cursor = conn.cursor()
                        cursor.execute(
                            "INSERT INTO products (name, price, available, image, description, color, size) VALUES (?, ?, ?, ?, ?, ?, ?)",
                            (name, price, available, image_base64, description, color, size)
                        )
                        conn.commit()
                        
                        st.success("Product added successfully!")
                    else:
                        st.error("Please fill all required fields (Name, Price, Image)")
            
            # Manage existing products
            st.subheader("Manage Products")
            
            # Get products from the database
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, price, available FROM products")
            products = cursor.fetchall()
            
            if not products:
                st.info("No products available.")
            else:
                # Convert to DataFrame for easier display
                df = pd.DataFrame(products, columns=["ID", "Name", "Price", "Available"])
                st.dataframe(df)
                
                # Delete product
                product_to_delete = st.selectbox("Select product to delete", 
                                                 options=[f"{p[0]} - {p[1]}" for p in products])
                if st.button("Delete Product"):
                    product_id = product_to_delete.split(" - ")[0]
                    remove_product(product_id)
                
                # Edit product
                st.subheader("Edit Product")
                product_to_edit = st.selectbox("Select product to edit", 
                                              options=[f"{p[0]} - {p[1]}" for p in products],
                                              key="edit_select")
                
                if product_to_edit:
                    product_id = product_to_edit.split(" - ")[0]
                    cursor.execute("SELECT name, price, available, description, color, size FROM products WHERE id = ?", (product_id,))
                    product_data = cursor.fetchone()
                    
                    if product_data:
                        with st.form("edit_product_form"):
                            name = st.text_input("Product Name", value=product_data[0])
                            price = st.number_input("Price (₮)", min_value=0.0, value=product_data[1], step=1000.0)
                            available = st.checkbox("Available", value=product_data[2])
                            description = st.text_area("Description", value=product_data[3] or "")
                            color = st.text_input("Color", value=product_data[4] or "")
                            size = st.text_input("Size", value=product_data[5] or "")
                            uploaded_file = st.file_uploader("Upload New Product Image (leave empty to keep current)", 
                                                           type=["jpg", "jpeg", "png"])
                            
                            submitted = st.form_submit_button("Update Product")

                            if submitted:
                                if name and price >= 0:
                                    if uploaded_file:
                                        # Process the new image
                                        image = Image.open(uploaded_file)
                                        image = image.resize((600, 600), Image.LANCZOS)
                                        image_base64 = image_to_base64(image)
                                        
                                        cursor.execute(
                                            "UPDATE products SET name=?, price=?, available=?, image=?, description=?, color=?, size=? WHERE id=?",
                                            (name, price, available, image_base64, description, color, size, product_id)
                                        )
                                    else:
                                        # Update without changing the image
                                        cursor.execute(
                                            "UPDATE products SET name=?, price=?, available=?, description=?, color=?, size=? WHERE id=?",
                                            (name, price, available, description, color, size, product_id)
                                        )
                                    
                                    conn.commit()
                                    st.success("Product updated successfully!")
                                else:
                                    st.error("Please fill all required fields (Name, Price)")

elif page == "Sign Up":
    # Import the sign-up page
    import sign_up
    sign_up.sign_up()

elif page == "Shopping Cart":
    st.markdown("<h3 class='main-title' style='text-align: left;'>Shopping Cart</h3>", unsafe_allow_html=True)
    display_cart()
    if st.button("Proceed to Checkout"):
        if not st.session_state.user_logged_in:
            st.warning("Please log in to proceed to checkout.")
        else:
            st.success("Proceeding to checkout...")

# Footer
st.markdown("---")
st.markdown("© 2025 Product Showcase. All rights reserved.")