import streamlit as st
from utils import init_db, load_css, send_contact_email, add_donation_record, get_gallery_images

init_db()
load_css("static/styles.css")

st.set_page_config(page_title="Marathon Of Hope Foundation", layout="wide")

def is_admin():
    return st.session_state.get("is_admin", False)
  
with st.sidebar:
    st.title("Marathon Of Hope")
    page = st.radio("Go to", ["Home", "About", "Donate", "Contact", "Gallery", "Admin"])

if page == "Home":
    st.header("Welcome to Marathon Of Hope Foundation — Canada")
    st.write(
        """
        This starter Streamlit app is a migration skeleton. Replace these sections
        with content from your existing site: events, mission, volunteer sign-ups, etc.
        """
    )
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Latest News")
        st.info("Migrate dynamic news list here from your CMS or database.")
    with col2:
        st.subheader("Upcoming Events")
        st.write("- Event A — Date\n- Event B — Date")

elif page == "About":
    st.header("About Us")
    st.write(
        """
        Add your organization's history, mission, team profiles, and impact metrics here.
        Use images from the static/images folder and format with st.columns and st.markdown.
        """
    )

elif page == "Donate":
    st.header("Make a Donation")
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

elif page == "Contact":
    st.header("Contact Us")
    with st.form("contact_form"):
        name = st.text_input("Name")
        email = st.text_input("Email")
        subject = st.text_input("Subject")
        body = st.text_area("Message")
        sent = st.form_submit_button("Send")
        if sent:
            # Sends email via SMTP; configure credentials in utils.send_contact_email
            ok, error = send_contact_email(name, email, subject, body)
            if ok:
                st.success("Message sent. We'll get back to you soon.")
            else:
                st.error(f"Failed to send message: {error}")

elif page == "Gallery":
    st.header("Gallery")
    images = get_gallery_images("static/images")
    if images:
        cols = st.columns(3)
        for i, img_path in enumerate(images):
            with cols[i % 3]:
                st.image(img_path, use_column_width=True)
    else:
        st.info("No images found in static/images. Add photos and re-run.")

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
