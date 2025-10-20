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
        The Marathon Of Hope began in 1980 when Terry Fox set out on a 
        """
    )

elif page == "Shop":
    st.header("Shop Merchendise")
    st.write("You can implement donations via Credit/Debit card. Below is a demo.")
    with st.form("donation_form"):
        donor_name = st.text_input("Full name")
        donor_email = st.text_input("Email")
        amount = st.number_input("Amount (CAD)", min_value=1.0, step=1.0, value=10.0)
        message = st.text_area("Message (optional)")
        submit = st.form_submit_button("Donate (demo)")
        if submit:
            # TODO: Replace with real payment flow (Stripe Checkout/Payment Intent server-side)
            add_donation_record(donor_name, donor_email, amount, message)
            st.success(f"Thank you {donor_name}! Donation of ${amount:.2f} recorded locally (demo).")
            st.info("Hook this form up to a payment processor and server-side verification.")

elif page == "Admin":
    st.header("Admin (demo)")
    if not is_admin():
        if st.button("Log in as admin (demo)"):
            st.session_state["is_admin"] = True
            st.experimental_rerun()
    else:
        st.success("Logged in as admin (demo).")
        st.write("Admin tools: view donations, export CSV, manage content (implement as needed).")
        # TODO: add admin functions e.g., list donations, delete, export
        st.button("Log out", on_click=lambda: st.session_state.update({"is_admin": False}))

# Footer
st.markdown("---")
st.caption("This is a starter Streamlit migration. Replace placeholders with your repo content.")
