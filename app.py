import streamlit as st
import pandas as pd
import os
from PIL import Image
import io
import sqlite3
import base64
from datetime import datetime

# Set page configuration
st.set_page_config(
    page_title="Бэлэн бараанууд",
    page_icon="🛍️",
    layout="wide"
)

# Database setup
def init_db():
    conn = sqlite3.connect('products.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('''
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        price REAL NOT NULL,
        available BOOLEAN NOT NULL,
        image BLOB NOT NULL,
        description TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    conn.commit()
    return conn

# Initialize the database connection
conn = init_db()

# Function to convert image to base64 for storing in the database
def image_to_base64(img):
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

# Initialize session state for admin login
if 'admin_logged_in' not in st.session_state:
    st.session_state.admin_logged_in = False

# Get the query parameters from the URL
query_params = st.query_params

# Check if the user is trying to access the Admin Panel
if 'admin' in query_params:
    if not st.session_state.admin_logged_in:
        password = st.text_input("Enter Admin Password", type="password")
        if st.button("Login"):
            if password == "Admin":  # Replace with your actual password
                st.session_state.admin_logged_in = True
                st.success("Logged in successfully!")
            else:
                st.error("Incorrect password. Please try again.")
    else:
        st.markdown("<h1 class='main-title'>Admin Panel</h1>", unsafe_allow_html=True)
        
        # Add new product form
        st.subheader("Add New Product")
        with st.form("add_product_form"):
            name = st.text_input("Product Name")
            # Increased price range to reflect Mongolian Tugrik values
            price = st.number_input("Price (₮)", min_value=0.0, max_value=10000000.0, step=1000.0)
            available = st.checkbox("Available", value=True)
            description = st.text_area("Description")
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
                        "INSERT INTO products (name, price, available, image, description) VALUES (?, ?, ?, ?, ?)",
                        (name, price, available, image_base64, description)
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
                cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))
                conn.commit()
                st.success(f"Product {product_to_delete} deleted successfully!")
                st.experimental_rerun()
            
            # Edit product
            st.subheader("Edit Product")
            product_to_edit = st.selectbox("Select product to edit", 
                                          options=[f"{p[0]} - {p[1]}" for p in products],
                                          key="edit_select")
            
            if product_to_edit:
                product_id = product_to_edit.split(" - ")[0]
                cursor.execute("SELECT name, price, available, description FROM products WHERE id = ?", (product_id,))
                product_data = cursor.fetchone()
                
                if product_data:
                    with st.form("edit_product_form"):
                        name = st.text_input("Product Name", value=product_data[0])
                        price = st.number_input("Price (₮)", min_value=0.0, value=product_data[1], step=1000.0)
                        available = st.checkbox("Available", value=product_data[2])
                        description = st.text_area("Description", value=product_data[3] or "")
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
                                        "UPDATE products SET name=?, price=?, available=?, image=?, description=? WHERE id=?",
                                        (name, price, available, image_base64, description, product_id)
                                    )
                                else:
                                    # Update without changing the image
                                    cursor.execute(
                                        "UPDATE products SET name=?, price=?, available=?, description=? WHERE id=?",
                                        (name, price, available, description, product_id)
                                    )
                                
                                conn.commit()
                                st.success("Product updated successfully!")
                            else:
                                st.error("Please fill all required fields (Name, Price)")
else:
    # Browse Products page
    st.markdown("<h1 class='main-title'>Бэлэн Бараанууд</h1>", unsafe_allow_html=True)
    
    # Filter section
    with st.expander("Filter Products"):
        col1, col2 = st.columns(2)
        with col1:
            show_available_only = st.checkbox("Show available products only")
        with col2:
            price_range = st.slider("Price Range", 0, 1000000, (0, 1000000))

    # Get products from the database
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, price, available, image, description FROM products")
    products = cursor.fetchall()
    
    if not products:
        st.info("No products available. Add some from the Admin Panel.")
    else:
        # Apply filters
        filtered_products = []
        for product in products:
            product_id, name, price, available, image_base64, description = product
            if show_available_only and not available:
                continue
            if not (price_range[0] <= price <= price_range[1]):
                continue
            filtered_products.append(product)
        
        # Display products in a grid (3 columns)
        col1, col2, col3 = st.columns(3)
        cols = [col1, col2, col3]
        
        for i, product in enumerate(filtered_products):
            product_id, name, price, available, image_base64, description = product
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
                    
                    st.markdown("</div>", unsafe_allow_html=True)
                    st.markdown("<br>", unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("© 2025 Product Showcase. All rights reserved.")