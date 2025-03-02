import streamlit as st

def init_cart():
    if 'cart' not in st.session_state:
        st.session_state.cart = []

def add_to_cart(product_id, name, price):
    st.session_state.cart.append({"id": product_id, "name": name, "price": price})
    st.success(f"Added {name} to cart")

def view_cart():
    st.sidebar.title("Shopping Cart")
    if 'cart' in st.session_state and st.session_state.cart:
        total = 0
        for item in st.session_state.cart:
            st.sidebar.write(f"{item['name']} - {item['price']} ₮")
            total += item['price']
        st.sidebar.write(f"**Total: {total} ₮**")
        if st.sidebar.button("Checkout"):
            st.sidebar.success("Checkout successful!")
            st.session_state.cart = []
    else:
        st.sidebar.write("Your cart is empty.")
