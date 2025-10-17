import sqlite3
import os
from pathlib import Path
from typing import List

DB_PATH = "data.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
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
    conn.commit()
    conn.close()

def add_donation_record(name: str, email: str, amount: float, message: str):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "INSERT INTO donations (name, email, amount, message) VALUES (?, ?, ?, ?)",
        (name, email, amount, message),
    )
    conn.commit()
    conn.close()

def send_contact_email(name: str, from_email: str, subject: str, body: str):
    """
    Demo email sender. Replace with configured SMTP credentials or an email sending service.
    Returns (True, "") on success or (False, error_message).
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
    images = [str(x) for x in sorted(p.glob("*")) if x.suffix.lower() in {".png", ".jpg", ".jpeg", ".gif"}]
    return images
