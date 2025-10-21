import streamlit as st
from utils import init_db, load_css, send_contact_email, add_donation_record, get_gallery_images

init_db()
load_css("static/styles.css")

st.set_page_config(page_title="Marathon Of Hope Foundation", layout="wide")

def is_admin():
    return st.session_state.get("is_admin", False)
  
if 'page' not in st.session_state:
    st.session_state.page = "Home"

with st.sidebar:
    st.title("Marathon Of Hope")
    st.write("Go to")

    if st.button("Home"):
        page = "Home"
    if st.button("About"):
        page = "About"
    if st.button("Shop"):
        page = "Shop"
    if st.button("Admin"):
        page = "Admin"

if page == "Home":
    st.header("Welcome to Marathon Of Hope Foundation — Canada")
    st.write(
        """
        We support what Terry Fox started; to support cancer reasearch.
        """
    )

elif page == "About":
    st.header("Join The Leagacy")
    st.write(
        """
        The Marathon of Hope began in 1980 when Terry Fox set out on an 
        unforgettable journey across Canada to raise funds and awareness 
        for cancer reasearch. Running a marathon on a prosthetic leg, Terry 
        inspired a nation with his determination, courage, and hope. Though
        his run ended after 143 days, his mission still lives on - and you can 
        be a part of it. Every purchase from our merchandise collection supports 
        cancer reasearch and helps keep Terry's dream alive. Wear the cause,
        spread the message, and carry the Marathon of Hope forward.
        """
    )

elif page == "Shop":
    from io import BytesIO
    from PIL import Image
    
    # Admin flag (replace with login logic later if you want)
    is_admin = st.sidebar.checkbox("Admin Mode", value=False)
    
    # Initialize session state for store and cart
    if "store_items" not in st.session_state:
        st.session_state.store_items = [
            {"name": "Apple", "price": 1.00, "image": None},
            {"name": "Banana", "price": 0.75, "image": None},
        ]
    
    if "cart" not in st.session_state:
        st.session_state.cart = []
    
    st.title("🛍️ My Streamlit Shop")
    
    # --- ADMIN SECTION ---
    if is_admin:
        st.subheader("Admin Panel - Add Items")
        with st.form("add_item_form", clear_on_submit=True):
            name = st.text_input("Item name")
            price = st.number_input("Item price ($)", min_value=0.0, step=0.01)
            image_file = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg"])
            submitted = st.form_submit_button("Add Item")
    
            if submitted:
                if name:
                    image_data = None
                    if image_file:
                        
                        image_data = image_file.getvalue()
                    st.session_state.store_items.append({
                        "name": name,
                        "price": price,
                        "image": image_data
                    })
                    st.success(f"Added {name} (${price:.2f}) to the store!")
                else:
                    st.warning("Please enter an item name.")
    
    st.divider()
    
    st.subheader("🛒 Available Items")
    
    for item in st.session_state.store_items:
        with st.container():
            cols = st.columns([1, 2, 1])

            if item["image"]:
                image = Image.open(BytesIO(item["image"]))
                cols[0].image(image, width=100)
            else:
                cols[0].write("🖼️ No image")
    
            cols[1].markdown(f"**{item['name']}**\n\n${item['price']:.2f}")
    
            if cols[2].button("Add to Cart", key=item["name"]):
                st.session_state.cart.append(item)
                st.success(f"Added {item['name']} to cart!")
    
    st.divider()
    
    st.subheader("🧺 Your Cart")
    if st.session_state.cart:
        total = sum(item["price"] for item in st.session_state.cart)
        for item in st.session_state.cart:
            st.write(f"- {item['name']} (${item['price']:.2f})")
        st.write(f"**Total: ${total:.2f}**")
    else:
        st.write("Your cart is empty.")
    
elif page == "Admin":
    st.header("Admin")
    if not is_admin():
        if st.button("Log in as admin (demo)"):
            
            st.session_state["is_admin"] = True
            st.experimental_rerun()
    else:
        st.success("Logged in as admin (demo).")
        st.write("Admin tools: view donations, add merchandise.")
        # TODO: add admin functions e.g., list donations, delete, export
        st.button("Log out", on_click=lambda: st.session_state.update({"is_admin": False}))

# Footer
st.markdown("---")
st.caption("This is a starter Streamlit migration. Replace placeholders with your repo content.")
