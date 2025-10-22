import sqlite3
import os
from pathlib import Path
from typing import List, Optional

DB_PATH = "data.db"


# ==============================
# 🧱 DATABASE INITIALIZATION
# ==============================
def get_connection():
    return sqlite3.connect(DB_PATH)


def init_db():
    conn = get_connection()
    c = conn.cursor()

    # --- Donations Table ---
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS donations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT,
            amount REAL,
            message TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    # --- Store Items Table ---
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS store_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price REAL NOT NULL,
            image BLOB
        )
        """
    )

    # --- Orders Table ---
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name TEXT,
            email TEXT,
            message TEXT,
            total REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    conn.commit()
    conn.close()


# ==============================
# 💰 DONATIONS
# ==============================
def add_donation_record(name: str, email: str, amount: float, message: str):
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        "INSERT INTO donations (name, email, amount, message) VALUES (?, ?, ?, ?)",
        (name, email, amount, message),
    )
    conn.commit()
    conn.close()


# ==============================
# 🛍️ STORE ITEMS
# ==============================
def add_item(name: str, price: float, image_data: Optional[bytes]):
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        "INSERT INTO store_items (name, price, image) VALUES (?, ?, ?)",
        (name, price, image_data),
    )
    conn.commit()
    conn.close()


def remove_item(name: str):
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM store_items WHERE name = ?", (name,))
    conn.commit()
    conn.close()


def get_all_items():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT name, price, image FROM store_items")
    rows = c.fetchall()
    conn.close()

    items = []
    for row in rows:
        items.append({"name": row[0], "price": row[1], "image": row[2]})
    return items


# ==============================
# 🧾 ORDERS
# ==============================
def add_order(customer_name: str, email: str, message: str, total: float):
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        "INSERT INTO orders (customer_name, email, message, total) VALUES (?, ?, ?, ?)",
        (customer_name, email, message, total),
    )
    conn.commit()
    conn.close()


def get_all_orders():
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        "SELECT id, customer_name, email, message, total, created_at FROM orders ORDER BY created_at DESC"
    )
    rows = c.fetchall()
    conn.close()

    orders = []
    for row in rows:
        orders.append(
            {
                "id": row[0],
                "customer_name": row[1],
                "email": row[2],
                "message": row[3],
                "total": row[4],
                "created_at": row[5],
            }
        )
    return orders


# ==============================
# 💌 EMAIL + UI HELPERS
# ==============================
def send_contact_email(name: str, from_email: str, subject: str, body: str):
    """
    Demo email sender. Replace with real SMTP credentials.
    """
    import smtplib
    from email.message import EmailMessage

    try:
        msg = EmailMessage()
        msg["Subject"] = f"[Website Contact] {subject}"
        msg["From"] = from_email
        msg["To"] = os.environ.get("CONTACT_RECEIVER_EMAIL", "you@example.com")
        msg.set_content(f"From: {name} <{from_email}>\n\n{body}")

        smtp_host = os.environ.get("SMTP_HOST")
        smtp_port = int(os.environ.get("SMTP_PORT", "587"))
        smtp_user = os.environ.get("SMTP_USER")
        smtp_pass = os.environ.get("SMTP_PASS")

        if not smtp_host or not smtp_user:
            return False, "SMTP configuration missing (set SMTP_HOST, SMTP_USER, SMTP_PASS)."

        server = smtplib.SMTP(smtp_host, smtp_port, timeout=10)
        server.starttls()
        server.login(smtp_user, smtp_pass)
        server.send_message(msg)
        server.quit()

        return True, ""
    except Exception as e:
        return False, str(e)


def load_css(css_path: str):
    try:
        from streamlit import markdown

        if Path(css_path).exists():
            with open(css_path, "r", encoding="utf-8") as f:
                css = f.read()
            markdown(f"<style>{css}</style>", unsafe_allow_html=True)
    except Exception:
        pass


def get_gallery_images(folder: str) -> List[str]:
    p = Path(folder)
    if not p.exists():
        return []
    return [
        str(x)
        for x in sorted(p.glob("*"))
        if x.suffix.lower() in {".png", ".jpg", ".jpeg", ".gif"}
    ]
