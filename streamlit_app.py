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
        We support what Terry Fox started: to support cancer research.
        """
    )

elif page == "About":
    st.header("Join The Leagacy")
    st.write(
        """
        The Marathon of Hope began in 1980 when Terry Fox set out on an 
        unforgettable journey across Canada to raise funds and awareness 
        for cancer research. Running a marathon on a prosthetic leg, Terry 
        inspired a nation with his determination, courage, and hope. Though
        his run ended after 143 days, his mission still lives on - and you can 
        be a part of it. Every purchase from our merchandise collection supports 
        cancer research and helps keep Terry's dream alive. Wear the cause,
        spread the message, and carry the Marathon of Hope forward.
        """
    )

elif page == "Shop":
  import streamlit as st
from io import BytesIO
from PIL import Image

# Toggle admin mode (you can replace this with real login later)
is_admin = st.sidebar.checkbox("Admin Mode", value=False)

# Initialize session state
if "store_items" not in st.session_state:
    st.session_state.store_items = [
        {"name": "Apple", "price": 1.00, "image": None},
        {"name": "Banana", "price": 0.75, "image": None},
    ]

if "cart" not in st.session_state:
    st.session_state.cart = []

st.title("🛍️ My Streamlit Shop")

# ==============================
# 🔧 ADMIN SECTION
# ==============================
if is_admin:
    st.subheader("🧰 Admin Panel - Manage Items")

    # --- Add Item ---
    with st.form("add_item_form", clear_on_submit=True):
        name = st.text_input("Item name")
        price = st.number_input("Item price ($)", min_value=0.0, step=0.01)
        image_file = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg"])
        submitted = st.form_submit_button("Add Item")

        if submitted:
            if name:
                image_data = image_file.getvalue() if image_file else None
                st.session_state.store_items.append({
                    "name": name,
                    "price": price,
                    "image": image_data
                })
                st.success(f"✅ Added {name} (${price:.2f}) to the store!")
            else:
                st.warning("Please enter an item name.")

    st.divider()

    # --- Remove Item ---
    st.subheader("🗑️ Remove Items")
    if st.session_state.store_items:
        item_names = [item["name"] for item in st.session_state.store_items]
        to_remove = st.selectbox("Select an item to remove", item_names)
        if st.button("Remove Selected Item"):
            st.session_state.store_items = [
                item for item in st.session_state.store_items if item["name"] != to_remove
            ]
            st.success(f"🗑️ Removed {to_remove} from the store.")
    else:
        st.info("No items in the store yet.")

st.divider()

# ==============================
# 🛒 SHOP SECTION
# ==============================
st.subheader("🛒 Available Items")

for item in st.session_state.store_items:
    with st.container():
        cols = st.columns([1, 2, 1])
        # Show image
        if item["image"]:
            image = Image.open(BytesIO(item["image"]))
            cols[0].image(image, width=100)
        else:
            cols[0].write("🖼️ No image")

        cols[1].markdown(f"**{item['name']}**\n\n${item['price']:.2f}")

        if cols[2].button("Add to Cart", key=f"add_{item['name']}"):
            st.session_state.cart.append(item)
            st.success(f"Added {item['name']} to cart!")

st.divider()
    
elif page == "Admin":
    st.header("Admin")
    if not is_admin():
        if st.button("Log in as admin (demo)"):
            st.text_input("Enter Password","Password")
            st.session_state["is_admin"] = True
            st.experimental_rerun()
    else:
        st.success("Logged in as admin (demo).")
        st.write("Admin tools: view payments, add merchandise.")

        st.button("Log out", on_click=lambda: st.session_state.update({"is_admin": False}))

# Footer
st.markdown("---")
st.caption("This is a starter Streamlit migration. Replace placeholders with your repo content.")
