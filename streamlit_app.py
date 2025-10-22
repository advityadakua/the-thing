import streamlit as st
import sqlite3
from io import BytesIO
from PIL import Image
from datetime import datetime
import base64
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from utils import init_db, load_css, send_contact_email

# =============================
# 🔧 Database Initialization
# =============================
init_db()

# Create tables for shop if not exist
conn = sqlite3.connect("data.db")
c = conn.cursor()
c.execute("""
CREATE TABLE IF NOT EXISTS shop_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    price REAL,
    image BLOB
)
""")
conn.commit()
conn.close()

load_css("static/styles.css")

st.set_page_config(page_title="Marathon Of Hope Foundation", layout="wide")


# =============================
# 🔐 Admin Check
# =============================
def is_admin():
    return st.session_state.get("is_admin", False)


# =============================
# 🧾 PDF Receipt Generator
# =============================
def generate_receipt(name, email, total, message, items):
    pdf_filename = f"receipt_{name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
    c = canvas.Canvas(pdf_filename, pagesize=letter)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(200, 750, "Marathon of Hope Foundation")
    c.setFont("Helvetica", 12)
    c.drawString(100, 720, "Purchase Receipt")
    c.drawString(100, 690, f"Name: {name}")
    c.drawString(100, 675, f"Email: {email}")
    c.drawString(100, 660, f"Total: ${total:.2f}")
    c.drawString(100, 645, f"Message: {message or '(none)'}")
    c.drawString(100, 630, f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    c.drawString(100, 600, "Items Purchased:")
    y = 580
    for item in items:
        c.drawString(120, y, f"- {item['name']} (${item['price']:.2f})")
        y -= 15

    c.drawString(100, y - 20, "Thank you for supporting cancer research!")
    c.save()
    return pdf_filename


def download_button(file_path, label):
    with open(file_path, "rb") as f:
        bytes_data = f.read()
    b64 = base64.b64encode(bytes_data).decode()
    href = f'<a href="data:application/octet-stream;base64,{b64}" download="{file_path}">{label}</a>'
    st.markdown(href, unsafe_allow_html=True)


# =============================
# 🧭 Navigation
# =============================
if 'page' not in st.session_state:
    st.session_state.page = "Home"
page = st.session_state.page

with st.sidebar:
    st.title("Marathon Of Hope")
    st.write("Navigate")

    if st.button("Home"): page = "Home"
    if st.button("About"): page = "About"
    if st.button("Shop"): page = "Shop"
    if st.button("Admin"): page = "Admin"

st.session_state.page = page


# =============================
# 🏠 HOME PAGE
# =============================
if page == "Home":
    st.header("Welcome to Marathon Of Hope Foundation — Canada")
    st.write("""
        We support what Terry Fox started: to support cancer research.
    """)

# =============================
# ℹ️ ABOUT PAGE
# =============================
elif page == "About":
    st.header("Join The Legacy")
    st.write("""
        The Marathon of Hope began in 1980 when Terry Fox set out on an unforgettable journey across Canada
        to raise funds and awareness for cancer research. Every purchase from our merchandise collection
        supports cancer research and helps keep Terry's dream alive.
    """)

# =============================
# 🛍️ SHOP PAGE
# =============================
elif page == "Shop":
    st.header("Shop")

    # Load items from database
    conn = sqlite3.connect("data.db")
    c = conn.cursor()
    c.execute("SELECT id, name, price, image FROM shop_items")
    items = [{"id": row[0], "name": row[1], "price": row[2], "image": row[3]} for row in c.fetchall()]
    conn.close()

    if "cart" not in st.session_state:
        st.session_state.cart = []

    # ============ ADMIN SECTION ============
    if is_admin():
        st.subheader("🧰 Admin Panel - Manage Items")

        with st.form("add_item_form", clear_on_submit=True):
            name = st.text_input("Item name")
            price = st.number_input("Item price ($)", min_value=0.0, step=0.01)
            image_file = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg"])
            submitted = st.form_submit_button("Add Item")

            if submitted:
                if name:
                    image_data = image_file.getvalue() if image_file else None
                    conn = sqlite3.connect("data.db")
                    c = conn.cursor()
                    c.execute("INSERT INTO shop_items (name, price, image) VALUES (?, ?, ?)", (name, price, image_data))
                    conn.commit()
                    conn.close()
                    st.success(f"✅ Added {name} (${price:.2f}) to the store!")
                    st.experimental_rerun()
                else:
                    st.warning("Please enter an item name.")

        st.divider()

        # Remove Item
        st.subheader("🗑️ Remove Items")
        if items:
            item_names = [item["name"] for item in items]
            to_remove = st.selectbox("Select an item to remove", item_names)
            if st.button("Remove Selected Item"):
                conn = sqlite3.connect("data.db")
                c = conn.cursor()
                c.execute("DELETE FROM shop_items WHERE name = ?", (to_remove,))
                conn.commit()
                conn.close()
                st.success(f"🗑️ Removed {to_remove} from the store.")
                st.experimental_rerun()
        else:
            st.info("No items in the store yet.")

    st.divider()

    # ============ SHOP SECTION ============
    st.subheader("🛒 Available Items")

    for item in items:
        with st.container():
            cols = st.columns([1, 2, 1])
            if item["image"]:
                image = Image.open(BytesIO(item["image"]))
                cols[0].image(image, width=100)
            else:
                cols[0].write("🖼️ No image")
            cols[1].markdown(f"**{item['name']}**\n\n${item['price']:.2f}")
            if cols[2].button("Add to Cart", key=f"add_{item['id']}"):
                st.session_state.cart.append(item)
                st.success(f"Added {item['name']} to cart!")

    # ============ CART SECTION ============
    st.divider()
    st.subheader("🛍️ Your Cart")

    if st.session_state.cart:
        total = sum(item['price'] for item in st.session_state.cart)
        for item in st.session_state.cart:
            st.write(f"- {item['name']} (${item['price']:.2f})")
        st.write(f"**Total: ${total:.2f}**")

        with st.form("checkout_form"):
            name = st.text_input("Your Name")
            email = st.text_input("Your Email")
            message = st.text_area("Message (optional)")
            submit_checkout = st.form_submit_button("Checkout")

            if submit_checkout:
                if not name or not email:
                    st.warning("Please enter name and email.")
                else:
                    # Generate and download PDF receipt
                    file_path = generate_receipt(name, email, total, message, st.session_state.cart)
                    st.success("✅ Order placed successfully!")
                    download_button(file_path, "📥 Download Receipt PDF")

                    # Optional: Email receipt
                    subject = "Your Marathon of Hope Purchase Receipt"
                    body = f"Thank you, {name}!\n\nYour total: ${total:.2f}\nMessage: {message or '(none)'}\n\nWe appreciate your support for cancer research!"
                    ok, err = send_contact_email("Marathon of Hope", email, subject, body)
                    if ok:
                        st.info("📧 Receipt sent to your email.")
                    else:
                        st.warning(f"Couldn't send email: {err}")

                    st.session_state.cart = []
    else:
        st.write("Your cart is empty.")

# =============================
# 🧑‍💼 ADMIN LOGIN PAGE
# =============================
elif page == "Admin":
    st.header("Admin Login")
    if not is_admin():
        password = st.text_input("Enter admin password", type="password")
        if st.button("Log in"):
            if password == "Auggie@2025":
                st.session_state["is_admin"] = True
                st.success("✅ Logged in as admin.")
                st.experimental_rerun()
            else:
                st.error("Incorrect password.")
    else:
        st.success("Logged in as admin.")
        if st.button("Log out"):
            st.session_state["is_admin"] = False
            st.experimental_rerun()

# =============================
# 🧩 Footer
# =============================
st.markdown("---")
st.caption("Marathon Of Hope Foundation © 2025 — Built with ❤️ using Streamlit")
