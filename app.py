import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import sqlite3
import os
import json
import hashlib
import shutil
import plotly.express as px
from io import BytesIO
import time
import re
import urllib.parse
import logging
import google.generativeai as genai
from ocr_engine import (
    generate_marathi_tts,
    get_active_gemini_models,
    process_receipt_advanced,
    process_voice_billing_advanced,
)
from streamlit_mic_recorder import speech_to_text

st.set_page_config(
    page_title="VernaLedger AI",
    page_icon="🤖",
    layout="centered",
)

CHAT_INPUT_COMPONENT = components.declare_component(
    "verna_chat_input",
    path=os.path.join(os.path.dirname(os.path.abspath(__file__)), "chat_input_component"),
)

# ERROR LOGGING SETUP
logging.basicConfig(filename='app.log', level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')
ai_logger = logging.getLogger("vernaledger.ai")
ai_logger.setLevel(logging.ERROR)
if not ai_logger.handlers:
    ai_file_handler = logging.FileHandler("app.log")
    ai_file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    ai_logger.addHandler(ai_file_handler)
    ai_logger.propagate = False


def load_gemini_api_key() -> str:
    secret_key = ""
    secret_error_type = None
    try:
        secret_value = st.secrets.get("GEMINI_API_KEY", "")
        if isinstance(secret_value, str):
            secret_key = secret_value.strip()
    except Exception as exc:
        secret_error_type = type(exc).__name__

    environment_key = os.getenv("GEMINI_API_KEY", "").strip()
    if secret_key:
        return secret_key
    if environment_key:
        return environment_key
    if secret_error_type:
        ai_logger.error(
            "Could not read Streamlit secrets (%s), and GEMINI_API_KEY is not set in the environment.",
            secret_error_type,
        )
    return ""


API_KEY = load_gemini_api_key()


def is_gemini_auth_error(exception: Exception) -> bool:
    """Return whether a Gemini exception indicates authentication or access failure."""
    error_text = f"{type(exception).__name__} {exception}".casefold()
    status_code = getattr(exception, "status_code", None)
    if status_code is None:
        response = getattr(exception, "response", None)
        status_code = getattr(response, "status_code", None)

    return (
        any(
            marker in error_text
            for marker in (
                "unauthenticated",
                "unauthorized",
                "api key",
                "api_key",
                "permission denied",
                "permission_denied",
                "forbidden",
            )
        )
        or status_code in (401, 403)
    )


# --- AI AUTOMATIC RETRY LOGIC ---
def generate_ai_content_with_retry(model, prompt, retries=3, delay=1):
    for attempt in range(retries):
        try:
            response = model.generate_content(prompt)
            if response and response.text:
                return response
        except Exception as e:
            logging.warning(f"AI API retry attempt {attempt+1}/{retries} failed: {e}")
            if attempt < retries - 1:
                time.sleep(delay * (2 ** attempt))
            else:
                raise e

# --- SECURE HASHING & DATABASE STRUCTURE ---
def get_db_connection():
    db_url = os.getenv("DATABASE_URL")
    if db_url:
        import psycopg2
        return psycopg2.connect(db_url)
    return sqlite3.connect("ledger.db")

def hash_password_secure(password):
    return hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), b'salt_verna_bcrypt_layer', 100000).hex()

# -- ADVANCED DATABASE SETUP WITH ACID TRANSACTIONS ---
def init_databases():
    if not os.path.exists("backups"):
        os.makedirs("backups")
    if os.path.exists("ledger.db"):
        backup_filename = f"backups/ledger_backup_{time.strftime('%Y%m%d_%H%M%S')}.db"
        existing_backups = sorted([os.path.join("backups", f) for f in os.listdir("backups") if f.endswith(".db")])
        if len(existing_backups) >= 5:
            try:
                os.remove(existing_backups[0])
            except Exception:
                pass
        try:
            shutil.copy("ledger.db", backup_filename)
        except Exception:
            pass
            
    with sqlite3.connect("ledger.db") as conn:
        try:
            conn.execute("BEGIN TRANSACTION;")
            cursor = conn.cursor()
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                password_hash TEXT NOT NULL,
                role TEXT DEFAULT 'Admin',
                phone TEXT
            )
            """)
            cursor.execute("PRAGMA table_info(users)")
            columns = [col[1] for col in cursor.fetchall()]
            if "role" not in columns:
                cursor.execute("ALTER TABLE users ADD COLUMN role TEXT DEFAULT 'Admin'")
            if "phone" not in columns:
                cursor.execute("ALTER TABLE users ADD COLUMN phone TEXT")

            cursor.execute("""
            CREATE TABLE IF NOT EXISTS audit_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT,
                action TEXT,
                timestamp TEXT
            )
            """)
            
            cursor.execute("SELECT username FROM users WHERE username = 'admin'")
            if not cursor.fetchone():
                default_pass_hash = hash_password_secure("verna123")
                cursor.execute("INSERT INTO users (username, password_hash, role, phone) VALUES (?, ?, ?, ?)", ("admin", default_pass_hash, "Admin", "9999999999"))
                
            cursor.execute("SELECT username FROM users WHERE username = 'sanket'")
            if not cursor.fetchone():
                sanket_pass_hash = hash_password_secure("pass123")
                cursor.execute("INSERT INTO users (username, password_hash, role, phone) VALUES (?, ?, ?, ?)", ("sanket", sanket_pass_hash, "Admin", "9999999999"))

            cursor.execute("""
            CREATE TABLE IF NOT EXISTS customer_khata (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_name TEXT,
                phone TEXT,
                amount REAL,
                transaction_type TEXT,
                date TEXT,
                due_date TEXT,
                notes TEXT
            )
            """)
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_khata_name ON customer_khata(customer_name)")

            cursor.execute("""
            CREATE TABLE IF NOT EXISTS shop_inventory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_name TEXT,
                stock_qty REAL,
                unit TEXT,
                alert_limit REAL
            )
            """)
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_stock_name ON shop_inventory(item_name)")

            cursor.execute("""
            CREATE TABLE IF NOT EXISTS business_expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                expense_title TEXT,
                amount REAL,
                category TEXT,
                date TEXT,
                notes TEXT
            )
            """)
            conn.commit()
        except Exception as e:
            conn.rollback()
            logging.error(f"Database initialization transaction failed: {e}")

init_databases()

def log_activity(username, action):
    with sqlite3.connect("ledger.db") as conn:
        try:
            conn.execute("BEGIN TRANSACTION;")
            cursor = conn.cursor()
            cursor.execute("INSERT INTO audit_logs (username, action, timestamp) VALUES (?, ?, ?)", (username, action, time.strftime("%Y-%m-%d %H:%M:%S")))
            conn.commit()
        except Exception as e:
            conn.rollback()
            logging.error(f"Audit log failed: {e}")

@st.cache_data(ttl=10)
def load_receipts_data():
    try:
        with sqlite3.connect("ledger.db") as conn:
            df = pd.read_sql_query("SELECT * FROM receipts", conn)
            if not df.empty:
                df['vendor_name'] = df['vendor_name'].apply(lambda v: decode_unicode(v))
                df['category'] = df['category'].apply(lambda c: decode_unicode(c))
            return df
    except Exception as e:
        logging.error(f"Error loading receipts: {e}")
        return pd.DataFrame()

def cleanup_temp_files():
    try:
        for f in os.listdir("."):
            if f.startswith("temp_") and f.endswith(".png"):
                if time.time() - os.path.getmtime(f) > 300:
                    os.remove(f)
    except Exception:
        pass

cleanup_temp_files()

if "remember_me" in st.session_state and st.session_state["remember_me"]:
    st.session_state['logged_in'] = True
if "logged_in" in st.query_params and st.query_params["logged_in"] == "true":
    st.session_state['logged_in'] = True
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'offline_queue' not in st.session_state:
    st.session_state['offline_queue'] = []
if 'user_role' not in st.session_state:
    st.session_state['user_role'] = 'Admin'
if 'current_username' not in st.session_state:
    st.session_state['current_username'] = 'admin'
if 'forgot_pass_mode' not in st.session_state:
    st.session_state['forgot_pass_mode'] = False
if 'input_method' not in st.session_state:
    st.session_state['input_method'] = 'Upload File'

def render_custom_logo(size="large"):
    if size == "large":
        st.markdown("""
        <div style="display: flex; justify-content: center; align-items: center; margin-bottom: 8px;">
            <div style="background: linear-gradient(135deg, #00f2fe 0%, #4facfe 50%, #7f00ff 100%); padding: 12px; border-radius: 16px; box-shadow: 0 0 20px rgba(0, 242, 254, 0.6); animation: pulseGlow 3s infinite alternate;">
                <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"></path>
                </svg>
            </div>
        </div>
        """, unsafe_allow_html=True)
    elif size == "compact":
        st.markdown("""
        <div style="display: flex; justify-content: center; align-items: center; margin-bottom: 4px;">
            <div style="background: linear-gradient(135deg, #00f2fe 0%, #4facfe 50%, #7f00ff 100%); padding: 6px; border-radius: 10px; box-shadow: 0 0 12px rgba(0, 242, 254, 0.5);">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"></path>
                </svg>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 10px; padding: 4px 0;">
            <div style="background: linear-gradient(135deg, #00f2fe 0%, #7f00ff 100%); padding: 7px; border-radius: 10px; box-shadow: 0 0 12px rgba(0, 242, 254, 0.5); flex-shrink: 0;">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"></path>
                </svg>
            </div>
            <div style="line-height: 1.2;">
                <span style="font-size: 16px; font-weight: 800; background: linear-gradient(135deg, #00f2fe 0%, #00ff87 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; display: block; text-shadow: 0 0 8px rgba(0,242,254,0.4);">VernaLedger.AI</span>
                <span style="font-size: 8px; color: #00f2fe; display: block; font-weight: 700; letter-spacing: 1.1px; margin-top: 2px;">MERCHANT SUITE PRO</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

# --- PERFECT DYNAMIC & FULL-WIDTH RESPONSIVE CSS ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css?family=Mukta:wght@400;600;700;800&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
@keyframes pulseGlow {
    0% { box-shadow: 0 0 10px rgba(0, 242, 254, 0.3); }
    100% { box-shadow: 0 0 22px rgba(0, 242, 254, 0.7); }
}
@keyframes liveDotPulse {
    0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(0, 255, 135, 0.7); }
    70% { transform: scale(1.1); box-shadow: 0 0 0 8px rgba(0, 255, 135, 0); }
    100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(0, 255, 135, 0); }
}
html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', 'Mukta', -apple-system, sans-serif !important;
}
.stApp {
    background-color: #020617 !important;
    background-image: 
        radial-gradient(circle at 15% 15%, rgba(0, 242, 254, 0.15) 0%, transparent 45%),
        radial-gradient(circle at 85% 85%, rgba(127, 0, 255, 0.15) 0%, transparent 45%),
        linear-gradient(135deg, #020617 0%, #0b1120 50%, #030712 100%) !important;
    background-attachment: fixed !important;
    color: #f8fafc !important;
}
[data-testid="stHeader"] {
    background: rgba(2, 6, 23, 0.8) !important;
    backdrop-filter: blur(20px) !important;
    border-bottom: 1px solid rgba(0, 242, 254, 0.25) !important;
}
[data-testid="stAppViewBlockContainer"] {
    max-width: 100% !important;
    width: 100% !important;
    padding-left: 1.5rem !important;
    padding-right: 1.5rem !important;
}
main.block-container {
    max-width: 100% !important;
    width: 100% !important;
    padding-top: 1.2rem !important;
    padding-bottom: 2.2rem !important;
    padding-left: 1rem !important;
    padding-right: 1rem !important;
}
[data-testid="stSidebarResizer"] {
    display: none !important;
    pointer-events: none !important;
}
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, rgba(6, 11, 25, 0.98) 0%, rgba(2, 6, 23, 0.99) 100%) !important;
    border-right: 1.5px solid rgba(0, 242, 254, 0.25) !important;
    box-shadow: 8px 0 28px rgba(0, 0, 0, 0.8) !important;
    resize: none !important;
}
.studio-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 22px 30px;
    background: linear-gradient(135deg, rgba(13, 19, 33, 0.9) 0%, rgba(15, 23, 42, 0.8) 100%) !important;
    backdrop-filter: blur(30px) !important;
    border: 1.5px solid rgba(0, 242, 254, 0.3) !important;
    border-radius: 22px !important;
    margin-bottom: 24px;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.6), inset 0 1px 1px rgba(255, 255, 255, 0.15) !important;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    width: 100% !important;
}
.studio-header:hover {
    border-color: rgba(0, 242, 254, 0.6) !important;
    box-shadow: 0 12px 40px rgba(0, 242, 254, 0.2) !important;
}
.panel-card {
    background: linear-gradient(135deg, rgba(13, 19, 33, 0.85) 0%, rgba(15, 23, 42, 0.75) 100%) !important;
    backdrop-filter: blur(28px) !important;
    border: 1.5px solid rgba(0, 242, 254, 0.22) !important;
    border-radius: 22px !important;
    padding: 24px !important;
    margin-bottom: 24px !important;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5) !important;
    transition: transform 0.25s ease, border-color 0.25s ease, box-shadow 0.25s ease !important;
    width: 100% !important;
}
.panel-card:hover {
    transform: translateY(-3px) !important;
    border-color: rgba(0, 242, 254, 0.45) !important;
    box-shadow: 0 14px 38px rgba(0, 242, 254, 0.15) !important;
}
div[data-testid="stDataFrame"] {
    font-size: 14px !important;
}
div[data-testid="stDataFrame"] table {
    font-size: 14px !important;
}
[data-testid="stSidebar"] > div:first-child {
    padding: 16px 14px !important;
    box-sizing: border-box !important;
}
.sidebar-title {
    font-size: 10.5px !important;
    font-weight: 800 !important;
    color: #00f2fe !important;
    letter-spacing: 1.2px !important;
    margin: 8px 0 6px 2px !important;
    text-transform: uppercase !important;
    display: block !important;
}
section[data-testid="stSidebar"] div[role="radiogroup"] {
    display: flex !important;
    flex-direction: column !important;
    gap: 6px !important;
}
section[data-testid="stSidebar"] div[role="radiogroup"] > label {
    background: linear-gradient(135deg, rgba(14, 165, 233, 0.12) 0%, rgba(37, 99, 235, 0.14) 48%, rgba(124, 58, 237, 0.16) 100%) !important;
    border: 1px solid rgba(0, 242, 254, 0.55) !important;
    padding: 7px 12px !important;
    border-radius: 12px !important;
    margin-bottom: 0 !important;
    min-height: 36px !important;
    display: flex !important;
    align-items: center !important;
    box-shadow: 0 0 0 1px rgba(255, 255, 255, 0.05), 0 5px 14px rgba(14, 165, 233, 0.16), 0 0 14px rgba(0, 242, 254, 0.18) !important;
    transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease, background 0.2s ease !important;
    cursor: pointer !important;
    width: 100% !important;
}
section[data-testid="stSidebar"] div[role="radiogroup"] > label:hover {
    border-color: #00f2fe !important;
    box-shadow: 0 0 0 1px rgba(255, 255, 255, 0.08), 0 8px 18px rgba(14, 165, 233, 0.25), 0 0 22px rgba(0, 242, 254, 0.42) !important;
    transform: translateY(-1px) !important;
}
section[data-testid="stSidebar"] div[role="radiogroup"] > label:has(input:checked) {
    background: linear-gradient(135deg, rgba(14, 165, 233, 0.28) 0%, rgba(37, 99, 235, 0.3) 48%, rgba(124, 58, 237, 0.32) 100%) !important;
    border: 1px solid #00f2fe !important;
    box-shadow: 0 0 0 1px rgba(255, 255, 255, 0.1), 0 8px 18px rgba(14, 165, 233, 0.24), 0 0 20px rgba(0, 242, 254, 0.38) !important;
}
section[data-testid="stSidebar"] div[role="radiogroup"] > label:focus-within {
    outline: none !important;
    border-color: #00f2fe !important;
    box-shadow: 0 0 0 2px rgba(0, 242, 254, 0.35), 0 0 18px rgba(0, 242, 254, 0.35) !important;
}
section[data-testid="stSidebar"] div[role="radiogroup"] label p {
    color: #f1f5f9 !important;
    font-size: 11.5px !important;
    font-weight: 700 !important;
    margin: 0 !important;
}
div[data-testid="stFileUploader"] {
    background: linear-gradient(135deg, rgba(11, 17, 32, 0.95) 0%, rgba(15, 23, 42, 0.90) 100%) !important;
    border: 2.2px dashed #00f2fe !important;
    border-radius: 20px !important;
    padding: 22px !important;
    box-shadow: 0 0 25px rgba(0, 242, 254, 0.35), inset 0 0 15px rgba(0, 242, 254, 0.15) !important;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
}
div[data-testid="stFileUploader"]:hover {
    border-color: #00ff87 !important;
    box-shadow: 0 0 35px rgba(0, 255, 135, 0.55), inset 0 0 20px rgba(0, 255, 135, 0.25) !important;
    transform: translateY(-2px) !important;
}
div[data-testid="stFileUploader"] section {
    background: transparent !important;
}
.dev-credit-box {
    background: rgba(0, 242, 254, 0.06);
    border: 1px solid rgba(0, 242, 254, 0.25);
    border-radius: 12px;
    padding: 8px 10px;
    margin-top: 8px;
    margin-bottom: 6px;
    flex-shrink: 0;
    transition: border-color 0.2s ease !important;
}
.dev-credit-box:hover {
    border-color: #00f2fe !important;
}
.stButton>button, .stDownloadButton>button, div[data-testid="stFormSubmitButton"]>button {
    background: linear-gradient(135deg, #0ea5e9 0%, #2563eb 48%, #7c3aed 100%) !important;
    color: #ffffff !important;
    font-weight: 800 !important;
    font-size: 13px !important;
    letter-spacing: 0.02em !important;
    border-radius: 12px !important;
    border: 1px solid rgba(0, 242, 254, 0.7) !important;
    padding: 0.72rem 1.2rem !important;
    min-height: 42px !important;
    box-shadow: 0 0 0 1px rgba(255, 255, 255, 0.08), 0 8px 18px rgba(14, 165, 233, 0.24), 0 0 18px rgba(0, 242, 254, 0.25) !important;
    text-shadow: 0 0 10px rgba(255, 255, 255, 0.35) !important;
    transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease, filter 0.2s ease !important;
}
.stButton>button:hover, .stDownloadButton>button:hover, div[data-testid="stFormSubmitButton"]>button:hover {
    box-shadow: 0 0 0 1px rgba(255, 255, 255, 0.1), 0 10px 22px rgba(14, 165, 233, 0.32), 0 0 24px rgba(0, 242, 254, 0.5) !important;
    border-color: #00f2fe !important;
    transform: translateY(-2px) scale(1.01) !important;
    filter: brightness(1.04) !important;
}
.stButton>button:focus-visible, .stDownloadButton>button:focus-visible, div[data-testid="stFormSubmitButton"]>button:focus-visible {
    outline: none !important;
    box-shadow: 0 0 0 2px rgba(0, 242, 254, 0.45), 0 0 0 5px rgba(14, 165, 233, 0.2), 0 0 20px rgba(0, 242, 254, 0.45) !important;
}
@media (max-width: 768px) {
    section[data-testid="stSidebar"] div[data-testid="stRadio"] div[role="radiogroup"] label,
    section[data-testid="stSidebar"] div.row-widget.stRadio div[role="radiogroup"] label,
    section[data-testid="stSidebar"] div[role="radiogroup"] > label {
        box-sizing: border-box !important;
        display: flex !important;
        align-items: center !important;
        width: 100% !important;
        color: #f1f5f9 !important;
        background: linear-gradient(135deg, rgba(14, 165, 233, 0.16) 0%, rgba(37, 99, 235, 0.18) 48%, rgba(124, 58, 237, 0.2) 100%) !important;
        border: 1px solid rgba(0, 242, 254, 0.7) !important;
        border-radius: 10px !important;
        min-height: 42px !important;
        padding: 9px 12px !important;
        box-shadow: 0 0 0 1px rgba(255, 255, 255, 0.07), 0 6px 14px rgba(14, 165, 233, 0.2), 0 0 16px rgba(0, 242, 254, 0.28) !important;
    }
    section[data-testid="stSidebar"] div[data-testid="stRadio"] div[role="radiogroup"] label:has(input[type="radio"]:checked),
    section[data-testid="stSidebar"] div.row-widget.stRadio div[role="radiogroup"] label:has(input[type="radio"]:checked),
    section[data-testid="stSidebar"] div[role="radiogroup"] > label:has(input[type="radio"]:checked) {
        background: linear-gradient(135deg, rgba(14, 165, 233, 0.34) 0%, rgba(37, 99, 235, 0.36) 48%, rgba(124, 58, 237, 0.38) 100%) !important;
        border: 1px solid #00f2fe !important;
        box-shadow: 0 0 0 1px rgba(255, 255, 255, 0.1), 0 7px 16px rgba(14, 165, 233, 0.28), 0 0 20px rgba(0, 242, 254, 0.44) !important;
    }
    section[data-testid="stSidebar"] div[data-testid="stRadio"] div[role="radiogroup"] label input[type="radio"],
    section[data-testid="stSidebar"] div.row-widget.stRadio div[role="radiogroup"] label input[type="radio"] {
        accent-color: #00f2fe !important;
    }
    section[data-testid="stSidebar"] div[role="radiogroup"] > label:hover {
        transform: none !important;
    }
    .stButton>button, .stDownloadButton>button, div[data-testid="stFormSubmitButton"]>button {
        font-size: 12px !important;
        border-radius: 10px !important;
        padding: 10px 16px !important;
        min-height: 40px !important;
        width: 100% !important;
        box-shadow: 0 0 0 1px rgba(255, 255, 255, 0.08), 0 6px 14px rgba(14, 165, 233, 0.22), 0 0 14px rgba(0, 242, 254, 0.2) !important;
    }
    .stButton>button:hover, .stDownloadButton>button:hover, div[data-testid="stFormSubmitButton"]>button:hover {
        transform: translateY(-1px) scale(1.005) !important;
    }
}
.live-pulse-badge {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: rgba(0, 255, 135, 0.15);
    border: 1px solid rgba(0, 255, 135, 0.4);
    padding: 6px 14px;
    border-radius: 20px;
    color: #00ff87;
    font-size: 11px;
    font-weight: 800;
}
.pulse-dot {
    width: 8px;
    height: 8px;
    background-color: #00ff87;
    border-radius: 50%;
    animation: liveDotPulse 1.8s infinite ease-in-out;
}
</style>
""", unsafe_allow_html=True)

# LOGIN PORTAL ---
def render_login_portal():
    is_reset_page = st.session_state.get('forgot_pass_mode', False)
    overflow_css = "auto" if is_reset_page else "hidden"
    st.markdown(f"""
    <style>
    header, [data-testid="stHeader"] {{ display: none !important; }}
    html, body {{
        overflow: {overflow_css} !important;
        height: 100vh !important;
    }}
    [data-testid="stAppViewContainer"], .stApp, section.main, [data-testid="stMain"] {{
        overflow: {overflow_css} !important;
        background: linear-gradient(rgba(2, 6, 23, 0.85), rgba(3, 7, 18, 0.90)),
        url('https://images.unsplash.com/photo-1639762681485-074b7f938ba0?q=80&w=1920&auto=format&fit=crop') !important;
        background-size: cover !important;
        background-position: center !important;
        background-attachment: fixed !important;
    }}
    section.main {{
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        min-height: 100vh !important;
        padding: 10px 0 !important;
    }}
    main.block-container {{
        width: 90% !important;
        max-width: 340px !important;
        padding: 0.8rem 1.2rem !important;
        margin: auto !important;
        background: linear-gradient(135deg, rgba(11, 17, 32, 0.95) 0%, rgba(15, 23, 42, 0.90) 100%) !important;
        backdrop-filter: blur(25px) !important;
        border: 1.5px solid rgba(0, 242, 254, 0.4) !important;
        border-radius: 18px !important;
        box-shadow: 0 0 25px rgba(0, 242, 254, 0.2) !important;
    }}
    </style>
    """, unsafe_allow_html=True)
    
    render_custom_logo("compact")
    st.markdown("""
    <div style="text-align: center; margin-bottom: 6px;">
        <h2 style="font-size: 18px; font-weight: 800; margin: 0; background: linear-gradient(135deg, #00f2fe 0%, #4facfe 50%, #00ff87 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
            VernaLedger.AI
        </h2>
        <p style="font-size: 9.5px; color: #94a3b8; font-weight: 600; margin-top: 1px;">Next-Gen Merchant & AI Financial Suite</p>
    </div>
    """, unsafe_allow_html=True)
    
    if is_reset_page:
        st.markdown("<h4 style='color:#00f2fe; text-align:center; font-size:13px; margin-bottom: 6px;'>पासवर्ड रिसेट करा (Reset Password)</h4>", unsafe_allow_html=True)
        with st.form("forgot_pass_form_standalone"):
            f_user = st.text_input("युजरनेम (Username)", placeholder="तुमचा युजरनेम")
            f_phone = st.text_input("मोबाईल नंबर (Phone)", placeholder="10-digit mobile number")
            new_p1 = st.text_input("नवीन पासवर्ड (New Password)", type="password", placeholder="Min 6 chars")
            new_p2 = st.text_input("कन्फर्म पासवर्ड (Confirm Password)", type="password", placeholder="Re-enter password")
            reset_btn = st.form_submit_button("पासवर्ड रिसेट करा")
            if reset_btn:
                if not f_user.strip() or not f_phone.strip() or len(new_p1) < 6:
                    st.error("सर्व माहिती भरणे आणि पासवर्ड किमान ६ अंकी असणे आवश्यक आहे!")
                elif new_p1 != new_p2:
                    st.error("पासवर्ड जुळत नाहीत!")
                else:
                    with sqlite3.connect("ledger.db") as conn:
                        try:
                            conn.execute("BEGIN TRANSACTION;")
                            cursor = conn.cursor()
                            cursor.execute("SELECT username FROM users WHERE username = ? AND phone = ?", (f_user.strip(), f_phone.strip()))
                            if cursor.fetchone():
                                new_hashed = hash_password_secure(new_p1)
                                cursor.execute("UPDATE users SET password_hash = ? WHERE username = ?", (new_hashed, f_user.strip()))
                                conn.commit()
                                log_activity(f_user.strip(), "Password Reset via Forgot Password")
                                st.success("पासवर्ड रिसेट झाला! नवीन पासवर्डने लॉगिन करा.")
                                time.sleep(1.2)
                                st.session_state['forgot_pass_mode'] = False
                                st.rerun()
                            else:
                                conn.rollback()
                                st.error("युजरनेम किंवा नंबर चुकीचा आहे!")
                        except Exception as ex:
                            conn.rollback()
                            st.error(f"त्रुटी: {ex}")
        if st.button("मूळ लॉगिन स्क्रीनवर जा", key="back_to_login"):
            st.session_state['forgot_pass_mode'] = False
            st.rerun()
    else:
        with sqlite3.connect("ledger.db") as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT count(*) FROM users WHERE role = 'Admin'")
            admin_count = cursor.fetchone()[0]
            
        auth_tab = "Login" if admin_count > 0 else st.radio("Auth Mode", ["Login", "Admin Sign Up"], horizontal=True, label_visibility="collapsed")
        
        if auth_tab == "Login":
            with st.form("login_form"):
                uname_input = st.text_input("Username", placeholder="Enter username (e.g. admin)")
                pass_input = st.text_input("Password", type="password", placeholder="Enter password")
                remember_me = st.checkbox("Auto-Login Persistent Session", value=True)
                submit_login = st.form_submit_button("Access VernaLedger Studio")
                if submit_login:
                    if not uname_input.strip() or not pass_input.strip():
                        st.error("कृपया युजरनेम आणि पासवर्ड दोन्ही भरा!")
                    else:
                        hashed_pass = hash_password_secure(pass_input)
                        with sqlite3.connect("ledger.db") as conn:
                            cursor = conn.cursor()
                            cursor.execute("SELECT password_hash, role FROM users WHERE username = ?", (uname_input.strip(),))
                            row = cursor.fetchone()
                            if row and row[0] == hashed_pass:
                                st.session_state['logged_in'] = True
                                st.session_state['user_role'] = row[1] if row[1] else 'Admin'
                                st.session_state['current_username'] = uname_input.strip()
                                log_activity(uname_input.strip(), "User Logged In")
                                if remember_me:
                                    st.session_state['remember_me'] = True
                                    st.query_params["logged_in"] = "true"
                                st.toast(f"स्वागत आहे! ({st.session_state['user_role']} Role)", icon="⚡")
                                time.sleep(0.4)
                                st.rerun()
                            else:
                                st.error("चुकीचा युजरनेम किंवा पासवर्ड!")
            if st.button("पासवर्ड विसरलात? (Reset Password)", key="btn_forgot_redirect"):
                st.session_state['forgot_pass_mode'] = True
                st.rerun()
        else:
            with st.form("signup_form"):
                st.markdown("##### Initial Admin Registration")
                new_user = st.text_input("Admin Username", placeholder="Choose admin username")
                new_phone = st.text_input("Mobile Number", placeholder="10-digit mobile number")
                new_pass = st.text_input("Admin Password", type="password", placeholder="Min 6 chars password")
                confirm_pass = st.text_input("Confirm Password", type="password", placeholder="Confirm password")
                submit_signup = st.form_submit_button("Create Master Admin")
                if submit_signup:
                    if not new_user.strip() or not new_phone.strip() or len(new_pass) < 6:
                        st.error("सर्व माहिती आणि पासवर्ड किमान ६ अंकी भरणे आवश्यक आहे!")
                    elif new_pass != confirm_pass:
                        st.error("पासवर्ड जुळत नाहीत!")
                    else:
                        with sqlite3.connect("ledger.db") as conn:
                            try:
                                conn.execute("BEGIN TRANSACTION;")
                                cursor = conn.cursor()
                                new_hashed_pass = hash_password_secure(new_pass)
                                cursor.execute("INSERT OR REPLACE INTO users (username, password_hash, role, phone) VALUES (?, ?, ?, ?)", (new_user.strip(), new_hashed_pass, "Admin", new_phone.strip()))
                                conn.commit()
                                log_activity(new_user.strip(), "Master Admin Created")
                                st.success("मास्टर अॅडमिन यशस्वीरीत्या तयार झाला! आता लॉगीन करा.")
                                time.sleep(0.8)
                                st.rerun()
                            except Exception as ex:
                                conn.rollback()
                                st.error(f"त्रुटी: {ex}")

if not st.session_state.get('logged_in', False):
    render_login_portal()
    st.stop()

def decode_unicode(val):
    if isinstance(val, str) and '\\u' in val:
        try:
            return val.encode('utf-8').decode('unicode-escape')
        except Exception:
            return val
    return str(val) if val else ""

def generate_pdf_report(dataframe, shop_name="All Receipts", lang="मराठी"):
    labels = {
        "मराठी": {"title": "व्हर्ना लेजर एआय आर्थिक अहवाल", "item": "वस्तूचे नाव", "qty": "नग", "rate": "दर", "total": "एकूण", "g_total": "एकूण रक्कम", "id": "रेकॉर्ड आयडी", "date": "तारीख"},
        "हिंदी": {"title": "वर्ना लेजर एआय वित्तीय रिपोर्ट", "item": "वस्तु का नाम", "qty": "मात्रा", "rate": "दर", "total": "कुल", "g_total": "कुल राशि", "id": "रिकॉर्ड आईडी", "date": "दिनांक"},
        "English": {"title": "VernaLedger.AI - Financial Report", "item": "Item Name", "qty": "Quantity", "rate": "Rate", "total": "Total", "g_total": "Grand Total", "id": "Record ID", "date": "Date"}
    }
    l = labels.get(lang, labels["मराठी"])
    cards_html = ""
    for idx, row in dataframe.iterrows():
        vendor = decode_unicode(row.get('vendor_name', ''))
        cat = decode_unicode(row.get('category', ''))
        g_total = row.get('grand_total', 0)
        date_str = row.get('date', 'N/A')
        raw_j_str = row.get('raw_json', '{}')
        items_rows = ""
        try:
            parsed_j = json.loads(raw_j_str) if isinstance(raw_j_str, str) else raw_j_str
            items_list = parsed_j.get('items', [])
            for it in items_list:
                i_name = decode_unicode(it.get('item_name', 'Item'))
                qty = it.get('quantity', '1')
                rate = it.get('rate', 0.0)
                tot = it.get('total_price', 0.0)
                items_rows += f"""
                <tr>
                    <td style="padding:8px 12px; border-bottom:1px solid #334155; font-weight:600; color:#f8fafc;">{i_name}</td>
                    <td style="padding:8px 12px; border-bottom:1px solid #334155; text-align:center; color:#94a3b8;">{qty}</td>
                    <td style="padding:8px 12px; border-bottom:1px solid #334155; text-align:right; color:#94a3b8;">{rate:,.2f}</td>
                    <td style="padding:8px 12px; border-bottom:1px solid #334155; text-align:right; font-weight:700; color:#00f2fe;">{tot:,.2f}</td>
                </tr>"""
        except Exception:
            items_rows = f"<tr><td colspan='4' style='padding:8px; color:#94a3b8; text-align:center;'>No itemized details</td></tr>"
            
        cards_html += f"""
        <div style="background:#0d1321; border:1px solid rgba(0,242,254,0.3); border-radius:14px; padding:20px; margin-bottom:20px;">
            <div style="display: flex; justify-content:space-between; align-items:center; border-bottom:2px solid #00f2fe; padding-bottom:10px; margin-bottom:14px;">
                <div>
                    <span style="font-size:20px; font-weight:800; color:#00f2fe;">{vendor}</span>
                    <span style="font-size:12px; background:rgba(0,242,254,0.15); color:#00f2fe; padding:4px 10px; border-radius:12px; margin-left:10px; font-weight:700;">{cat}</span>
                </div>
                <div style="text-align:right;">
                    <span style="font-size:12px; color:#94a3b8; font-weight:600;">{l['id']}: #{row.get('id', '')} | {l['date']}: {date_str}</span>
                </div>
            </div>
            <table style="width:100%; border-collapse:collapse; font-size:13px; margin-bottom:12px;">
                <thead>
                    <tr style="background:#050814; color:#00f2fe;">
                        <th style="padding:8px 12px; text-align:left;">{l['item']}</th>
                        <th style="padding:8px 12px; text-align:center;">{l['qty']}</th>
                        <th style="padding:8px 12px; text-align:right;">{l['rate']}</th>
                        <th style="padding:8px 12px; text-align:right;">{l['total']}</th>
                    </tr>
                </thead>
                <tbody>{items_rows}</tbody>
            </table>
            <div style="text-align:right; font-size:16px; font-weight:800; color:#f8fafc; padding-top:6px; border-top:1px dashed #334155;">
                {l['g_total']}: <span style="color:#00ff87; font-size:18px;">{g_total:,.2f}</span>
            </div>
        </div>"""
        
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head><meta charset='utf-8'><title>{l['title']}</title></head>
    <body style="font-family: 'Segoe UI', sans-serif; padding:30px; color:#f8fafc; background:#050814; max-width:950px; margin:0 auto;">
        <div style="display: flex; justify-content:space-between; align-items:center; border-bottom: 3px solid #00f2fe; padding-bottom: 15px; margin-bottom:25px;">
            <div style="font-size:26px; color:#00f2fe; font-weight:bold;">{l['title']}</div>
        </div>
        {cards_html}
    </body>
    </html>"""
    buffer = BytesIO(html_content.encode('utf-8'))
    buffer.seek(0)
    return buffer

df = load_receipts_data()

# SIDEBAR NAVIGATION ---
with st.sidebar:
    render_custom_logo("small")
    current_role = st.session_state.get('user_role', 'Admin')
    role_badge_color = "#00ff87" if current_role == 'Admin' else "#f59e0b"
    st.markdown(f"""
    <div style="background: rgba(15, 23, 42, 0.9); border: 1px solid {role_badge_color}; padding: 6px 10px; border-radius: 10px; margin-bottom: 8px; text-align: center; box-shadow: 0 0 12px {role_badge_color}33;">
        <span style="font-size: 10px; font-weight: 800; color: {role_badge_color};">ROLE: {current_role.upper()}</span>
    </div>
    """, unsafe_allow_html=True)
    
    queue_len = len(st.session_state['offline_queue'])
    if queue_len > 0:
        st.markdown(f"""
        <div style="background: rgba(245, 158, 11, 0.15); border: 1px solid #f59e0b; padding: 6px; border-radius: 10px; margin-bottom: 8px; text-align: center;">
            <span style="font-size: 9.5px; font-weight: 800; color: #f59e0b;">OFFLINE QUEUE: {queue_len} pending</span>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown("<div class='sidebar-title'>NAVIGATION SUITE</div>", unsafe_allow_html=True)
    if current_role == 'Staff':
        nav_options = ["OCR Scanner", "Ledger Database", "RAG AI Chat"]
        selected_page = st.radio("Navigation", nav_options, index=0, label_visibility="collapsed")
    else:
        nav_options = ["OCR Scanner", "Sales & Analytics", "Business Modules", "Ledger Database", "RAG AI Chat", "Staff Management"]
        selected_main_page = st.radio("Navigation", nav_options, index=0, label_visibility="collapsed")
        if selected_main_page == "Business Modules":
            dropdown_choice = st.selectbox("व्यवसाय विभाग निवडा:", ["Customer Khata (उधारी)", "Stock & Inventory", "Business Expenses"])
            selected_page = dropdown_choice
        else:
            selected_page = selected_main_page
            
    st.markdown("""
    <div class="dev-credit-box">
        <div style="font-size: 9px; text-transform: uppercase; color: #00f2fe; font-weight: 800; margin-bottom: 3px;">Project Developers</div>
        <div style="font-size: 10px; font-weight: 700; color: #ffffff; line-height: 1.3;">
            Sanket Kirdat | Sakshi Bhagat<br>Vaishnavi Dhavale | Rushikesh Mulik
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("Logout System"):
        log_activity(st.session_state.get('current_username', 'admin'), "User Logged Out")
        st.session_state['logged_in'] = False
        st.session_state['remember_me'] = False
        st.query_params.clear()
        st.toast("लॉगआऊट यशस्वी!", icon="🔒")
        time.sleep(0.4)
        st.rerun()

# FEATURE 1: OCR SCANNER + MULTI-LANGUAGE VOICE BILLING ---
if selected_page == "OCR Scanner":
    st.markdown("""
    <div class="studio-header">
        <div>
            <h2 style="margin:0; font-size: 22px; font-weight: 800; color: #00f2fe;">OCR Scanner & Multi-Language Voice Billing</h2>
            <p style="margin:4px 0 0 0; font-size: 12px; color: #94a3b8; font-weight: 600;">Instant Digital POS Receipt Parsing & Audio Confirmation</p>
        </div>
        <div class="live-pulse-badge">
            <div class="pulse-dot"></div>
            POS ONLINE
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    col_u, col_p = st.columns([1.1, 0.9])
    with col_u:
        st.markdown("<div class='panel-card'>", unsafe_allow_html=True)
        st.markdown("<h4 style='color:#00f2fe; margin-top:0; font-size: 16px;'>Input Mode</h4>", unsafe_allow_html=True)
        force_save_option = st.checkbox("ड्युप्लिकेट पावती असल्यास जबरदस्तीने सेव्ह करा (Force Save)", value=False)
        
        m_col1, m_col2, m_col3 = st.columns(3)
        with m_col1:
            if st.button("Upload File", type="primary" if st.session_state['input_method'] == "Upload File" else "secondary", use_container_width=True):
                st.session_state['input_method'] = "Upload File"
                st.rerun()
        with m_col2:
            if st.button("Live Camera", type="primary" if st.session_state['input_method'] == "Live Camera" else "secondary", use_container_width=True):
                st.session_state['input_method'] = "Live Camera"
                st.rerun()
        with m_col3:
            if st.button("Voice Bill", type="primary" if st.session_state['input_method'] == "Multi-Language Voice Bill" else "secondary", use_container_width=True):
                st.session_state['input_method'] = "Multi-Language Voice Bill"
                st.rerun()
                
        input_method = st.session_state['input_method']
        up_files = []
        up_cam = None
        if input_method == "Live Camera":
            up_cam = st.camera_input("Take photo")
        elif input_method == "Upload File":
            up_files = st.file_uploader("Choose Receipts", type=["jpg", "jpeg", "png"], accept_multiple_files=True, label_visibility="collapsed")
        elif input_method == "Multi-Language Voice Bill":
            st.markdown("""
            <div style="background: rgba(0,242,254,0.08); border: 1px solid #00f2fe; padding: 14px; border-radius: 14px; text-align: center; margin-bottom: 15px;">
                <div style="font-size: 15px; font-weight: 800; color: #00f2fe; margin-bottom: 4px;">Verna Pro Multi-Language Studio (Auto-Detect Language)</div>
                <div style="font-size: 12px; color: #f8fafc;">Speak in Marathi, Hindi, or English (उदा: Store name, items & price)</div>
            </div>
            """, unsafe_allow_html=True)
            spoken_bill = speech_to_text(start_prompt="बोलणे सुरू करा (माइक दाबा)", stop_prompt="थांबवा आणि बिल सेव्ह करा", just_once=True, language='mr-IN', key='voice_billing_mic_auto')
            if spoken_bill:
                with st.spinner("प्रोग्रेस सुरू आहे... व्हॉईसवरून बिल तयार होत आहे."):
                    try:
                        v_data = process_voice_billing_advanced(spoken_bill, API_KEY)
                        st.session_state['processed_data'] = v_data
                        log_activity(st.session_state.get('current_username', 'admin'), "Processed Voice Bill")
                        st.success("व्हॉईस बिल यशस्वीरीत्या तयार होऊन डेटाबेसमध्ये सेव्ह झाले !")
                        st.toast("व्हॉईस बिल सेव्ह झाले!", icon="🎤")
                        st.rerun()
                    except Exception as ve:
                        logging.error(f"Voice billing error: {ve}")
                        st.error(f"व्हॉईस बिल त्रुटी: {ve}")
                        
        st.write("")
        process_clicked = st.button("Process Receipt(s)", type="primary")
        if process_clicked and input_method != "Multi-Language Voice Bill":
            target_files = []
            if input_method == "Live Camera" and up_cam:
                target_files = [up_cam]
            elif input_method == "Upload File" and up_files:
                target_files = up_files
            if target_files:
                progress_bar = st.progress(0)
                status_text = st.empty()
                processed_batch = []
                warning_messages = []
                total_f = len(target_files)
                for idx, single_file in enumerate(target_files):
                    status_text.text(f"पावती विश्लेषित करत आहे ({idx+1}/{total_f})...")
                    progress_bar.progress((idx+1)/total_f)
                    temp_f = f"temp_{os.urandom(4).hex()}.png"
                    try:
                        with open(temp_f, "wb") as f:
                            f.write(single_file.getbuffer())
                        data = process_receipt_advanced(temp_f, API_KEY, force_save=force_save_option)
                        processed_batch.append(data)
                        if os.path.exists(temp_f):
                            os.remove(temp_f)
                    except Exception as e:
                        if os.path.exists(temp_f):
                            os.remove(temp_f)
                        err_str = str(e)
                        if "Duplicate Warning:" in err_str:
                            clean_err = err_str.split("Duplicate Warning:")[-1].strip()
                            warning_messages.append(f"पावती क्र. {idx+1} ({single_file.name}): {clean_err}")
                        else:
                            warning_messages.append(f"पावती क्र. {idx+1} ({single_file.name}): {err_str}")
                progress_bar.empty()
                status_text.empty()
                if processed_batch:
                    st.session_state['processed_batch'] = processed_batch
                    st.session_state['processed_data'] = processed_batch[0]
                    log_activity(st.session_state.get('current_username', 'admin'), f"Scanned {len(processed_batch)} Receipts")
                    if warning_messages:
                        st.session_state['warning_msg'] = " | ".join(warning_messages)
                        st.session_state['warning_time'] = time.time()
                    else:
                        st.session_state['warning_msg'] = None
                    st.success(f"Successfully processed {len(processed_batch)} receipt(s)!")
                    st.toast("पावती यशस्वीरीत्या स्कॅन झाली!", icon="✅")
                    st.rerun()
            else:
                st.warning("कृपया किमान एक पावती निवडा किंवा कॅमेऱ्याने फोटो घ्या.")
        if st.session_state.get('warning_msg'):
            elapsed = time.time() - st.session_state.get('warning_time', 0)
            if elapsed < 15:
                st.warning(f"ड्युप्लिकेट पावती अलर्ट: {st.session_state['warning_msg']}")
        st.markdown("</div>", unsafe_allow_html=True)
        
    with col_p:
        st.markdown("<div class='panel-card'>", unsafe_allow_html=True)
        st.markdown("<h4 style='color:#00f2fe; margin-top:0; font-size: 16px;'>Extracted Items & Summary</h4>", unsafe_allow_html=True)
        batch_data = st.session_state.get('processed_batch', [])
        if batch_data:
            for idx, p_item in enumerate(batch_data):
                v_disp = decode_unicode(p_item.get('vendor_name'))
                tot = p_item.get('grand_total', 0)
                st.markdown(f"**पावती #{idx+1} - Shop:** {v_disp} | **Total:** *{tot:,.2f}*")
            st.markdown("---")
            st.markdown("#### Marathi Audio Summary")
            if len(batch_data) > 1:
                vendor_names_list = [decode_unicode(item.get('vendor_name', 'दुकान')) for item in batch_data]
                audio_text = "स्कॅन केलेल्या पावत्यांची दुकाने: " + ", ".join(vendor_names_list)
            else:
                single_v = decode_unicode(batch_data[0].get('vendor_name'))
                single_tot = batch_data[0].get('grand_total', 0)
                audio_text = f"{single_v} कडील पावतीची एकूण रक्कम रुपये {single_tot} आहे."
            aud_path = generate_marathi_tts(audio_text)
            if aud_path and os.path.exists(aud_path):
                st.audio(aud_path)
        elif 'processed_data' in st.session_state:
            items_raw = st.session_state['processed_data'].get('items', [])
            items_df = pd.DataFrame(items_raw)
            if not items_df.empty:
                st.dataframe(items_df, use_container_width=True)
            v_disp = decode_unicode(st.session_state['processed_data'].get('vendor_name'))
            tot = st.session_state['processed_data'].get('grand_total', 0)
            st.markdown(f"**Shop Name:** {v_disp}")
            st.markdown(f"**Grand Total:** <h2 style='color:#00ff87; margin:0;'>{tot:,.2f}</h2>", unsafe_allow_html=True)
            st.markdown("---")
            st.markdown("#### Marathi Audio Summary")
            aud_path = generate_marathi_tts(f"{v_disp} कडील पावतीची एकूण रक्कम रुपये {tot} आहे.")
            if aud_path and os.path.exists(aud_path):
                st.audio(aud_path)
        else:
            st.caption("Scan receipt(s) or use Multi-Language Voice Bill to display extracted items & summary.")
        st.markdown("</div>", unsafe_allow_html=True)

# FEATURE 2: SALES & ANALYTICS ---
elif selected_page == "Sales & Analytics":
    if st.session_state.get('user_role') == 'Staff':
        st.error("प्रतिबंधीत क्षेत्रः कामागार/स्टाफला या पेजवर प्रवेश करण्याची परवानगी नाही!")
        st.stop()
    st.markdown("""
    <div class="studio-header">
        <div>
            <h2 style="margin:0; font-size: 22px; font-weight: 800; color: #00f2fe;">Daily Sales & Merchant Analytics</h2>
            <p style="margin:4px 0 0 0; font-size: 12px; color: #94a3b8; font-weight: 600;">Daily Revenue, Ticket Size, Category & Custom Period Reports</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("<div class='panel-card'>", unsafe_allow_html=True)
    st.markdown("<h4 style='color:#00f2fe; margin-top:0;'>कस्टम अहवाल आणि कालावधी फिल्टर (Custom Period Filters)</h4>", unsafe_allow_html=True)
    time_frame = st.selectbox("अहवाल कालावधी निवडा (Select Report Period):", ["All Time (संपूर्ण वेळ)", "Daily (आजचा दिवस)", "Weekly (चालू आठवडा)", "Monthly (चालू महिना)"])
    filtered_df_analytics = df.copy()
    if not filtered_df_analytics.empty and 'date' in filtered_df_analytics.columns:
        try:
            filtered_df_analytics['date_dt'] = pd.to_datetime(filtered_df_analytics['date'], errors='coerce')
            now_dt = pd.Timestamp.now()
            if time_frame == "Daily (आजचा दिवस)":
                filtered_df_analytics = filtered_df_analytics[filtered_df_analytics['date_dt'].dt.date == now_dt.date()]
            elif time_frame == "Weekly (चालू आठवडा)":
                filtered_df_analytics = filtered_df_analytics[filtered_df_analytics['date_dt'] >= (now_dt - pd.Timedelta(days=7))]
            elif time_frame == "Monthly (चालू महिना)":
                filtered_df_analytics = filtered_df_analytics[filtered_df_analytics['date_dt'].dt.month == now_dt.month]
        except Exception:
            pass
    st.markdown("</div>", unsafe_allow_html=True)
    
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        tot_exp = f"{filtered_df_analytics['grand_total'].sum():,.2f}" if not filtered_df_analytics.empty else "0.00"
        st.markdown(f"<div class='panel-card'><div style='font-size:11px; color:#94a3b8; font-weight:700;'>TOTAL REVENUE / SALES</div><div style='font-size: 18px; font-weight:800; color:#00f2fe; margin-top:4px;'>{tot_exp}</div></div>", unsafe_allow_html=True)
    with k2:
        tot_rec = len(filtered_df_analytics) if not filtered_df_analytics.empty else 0
        st.markdown(f"<div class='panel-card'><div style='font-size:11px; color:#94a3b8; font-weight:700;'>TOTAL BILLS/ORDERS</div><div style='font-size:18px; font-weight:800; color:#4facfe; margin-top:4px;'>{tot_rec}</div></div>", unsafe_allow_html=True)
    with k3:
        avg_exp = f"{filtered_df_analytics['grand_total'].mean():,.2f}" if not filtered_df_analytics.empty else "0.00"
        st.markdown(f"<div class='panel-card'><div style='font-size:11px; color:#94a3b8; font-weight:700;'>AVG TICKET SIZE</div><div style='font-size:18px; font-weight:800; color:#00ff87; margin-top:4px;'>{avg_exp}</div></div>", unsafe_allow_html=True)
    with k4:
        top_v = filtered_df_analytics.groupby('vendor_name')['grand_total'].sum().idxmax() if not filtered_df_analytics.empty else "N/A"
        st.markdown(f"<div class='panel-card'><div style='font-size:11px; color:#94a3b8; font-weight:700;'>TOP PERFORMING SHOP</div><div style='font-size:15px; font-weight:800; color:#c084fc; margin-top:4px;'>{top_v[:14]}...</div></div>", unsafe_allow_html=True)
        
    if not filtered_df_analytics.empty:
        ca1, ca2 = st.columns(2)
        with ca1:
            st.markdown("<div class='panel-card'>", unsafe_allow_html=True)
            st.markdown("#### Category Breakdown")
            c_sum = filtered_df_analytics.groupby('category')['grand_total'].sum().reset_index()
            fig_p = px.pie(c_sum, names='category', values='grand_total', hole=0.55, color_discrete_sequence=['#00f2fe', '#00ff87', '#4facfe', '#7f00ff'])
            fig_p.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='#f8fafc', size=11), height=240, margin=dict(l=5, r=5, t=5, b=5))
            st.plotly_chart(fig_p, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
        with ca2:
            st.markdown("<div class='panel-card'>", unsafe_allow_html=True)
            st.markdown("#### Shop Revenue Overview")
            fig_b = px.bar(filtered_df_analytics, x='vendor_name', y='grand_total', color='category', color_discrete_sequence=['#00f2fe', '#00ff87', '#4facfe'])
            fig_b.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='#f8fafc', size=11), showlegend=False, height=240, margin=dict(l=5, r=5, t=10, b=20))
            st.plotly_chart(fig_b, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

# FEATURE 3: ADVANCED CUSTOMER KHATA ---
elif selected_page == "Customer Khata (उधारी)":
    if st.session_state.get('user_role') == 'Staff':
        st.error("प्रतिबंधीत क्षेत्रः कामागार/स्टाफला उधारी मॅनेजमेंट पेजवर प्रवेश करण्याची परवानगी नाही!")
        st.stop()
    st.markdown("""
    <div class="studio-header">
        <div>
            <h2 style="margin:0; font-size: 22px; font-weight: 800; color: #00f2fe;">Customer Khata (उधारी वही)</h2>
            <p style="margin:4px 0 0 0; font-size: 12px; color: #94a3b8; font-weight: 600;">Advanced AI Offline Support, AI Risk Scoring, Multi-Language Voice Parsing & Direct Settle</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["नवीन उधारी / हप्ता नोंद", "उधारी लेजर & AI रिस्क रिपोर्ट", "स्मार्ट AI व्हॉईस नोंद (Multi-Language Voice-to-Khata)"])
    with tab1:
        st.markdown("<div class='panel-card'>", unsafe_allow_html=True)
        st.markdown("<h4 style='color:#00f2fe; margin-top:0;'>+ नवीन उधारी किंवा हप्ता नोंद करा</h4>", unsafe_allow_html=True)
        with st.form("khata_form"):
            fc1, fc2 = st.columns(2)
            with fc1:
                c_name = st.text_input("ग्राहक नाव (Customer Name)")
                c_phone = st.text_input("मोबाईल नंबर (Phone Number - 10 digits)")
                c_amount = st.number_input("रक्कम (Amount)", min_value=0.0, step=10.0)
            with fc2:
                c_type = st.selectbox("व्यवहार प्रकार (Transaction Type)", ["उधारी बाकी (Given Credit)", "पैसे जमा / हप्ता (Received Payment / Partial)"])
                c_date = st.text_input("व्यवहार तारीख (Date)", value=time.strftime("%Y-%m-%d"))
                c_due = st.text_input("परतफेची मुदत तारीख (Due Date)", value=time.strftime("%Y-%m-%d"))
            c_notes = st.text_area("टीप / वस्तु तपशील (Itemized Notes e.g. 2 kg sugar)")
            submit_khata = st.form_submit_button("खात्यात नोंद सेव्ह करा")
            if submit_khata:
                if not c_name.strip() or c_amount <= 0:
                    st.error("कृपया ग्राहकाचे नाव आणि योग्य रक्कम भरा!")
                else:
                    try:
                        with sqlite3.connect("ledger.db") as conn:
                            conn.execute("BEGIN TRANSACTION;")
                            cursor = conn.cursor()
                            cursor.execute("""
                            INSERT INTO customer_khata (customer_name, phone, amount, transaction_type, date, due_date, notes)
                            VALUES (?, ?, ?, ?, ?, ?, ?)
                            """, (c_name.strip(), c_phone.strip(), c_amount, c_type, c_date, c_due, c_notes))
                            conn.commit()
                        log_activity(st.session_state.get('current_username', 'admin'), f"Added Khata for {c_name.strip()} - {c_amount}")
                        st.success(f"'{c_name}' ची उधारी नोंद यशस्वीरीत्या सेव्ह झाली!")
                        st.toast("खाते नोंद अपडेट झाली!", icon="📝")
                        time.sleep(0.4)
                        st.rerun()
                    except Exception as ex:
                        st.session_state['offline_queue'].append({
                            "name": c_name.strip(), "phone": c_phone.strip(), "amount": c_amount, "type": c_type, "date": c_date, "due": c_due, "notes": c_notes
                        })
                        st.warning("डेटाबेस त्रुटीमुळे डेटा ऑफलाइन क्यु (Offline Queue) मध्ये साठवला आहे!")
        st.markdown("</div>", unsafe_allow_html=True)
        
    with tab2:
        st.markdown("<div class='panel-card'>", unsafe_allow_html=True)
        rh_col1, rh_col2 = st.columns([3, 1])
        with rh_col1:
            st.markdown("<h4 style='color:#00f2fe; margin-top:0;'>उधारी लेजर, AI रिस्क, Edit & Quick Settle</h4>", unsafe_allow_html=True)
        with rh_col2:
            if st.button("डेटा रिफ्रेश करा", type="primary"):
                st.toast("लेजर डेटा अपडेट झाला!", icon="🔄")
                st.rerun()
        try:
            with sqlite3.connect("ledger.db") as conn:
                khata_df = pd.read_sql_query("SELECT * FROM customer_khata ORDER BY id DESC", conn)
        except Exception:
            khata_df = pd.DataFrame()
            
        if not khata_df.empty:
            total_udhari = khata_df[khata_df['transaction_type'] == "उधारी बाकी (Given Credit)"]['amount'].sum()
            total_jama = khata_df[khata_df['transaction_type'].str.contains("पैसे जमा | Received")]['amount'].sum() if 'transaction_type' in khata_df.columns else 0
            net_balance = total_udhari - total_jama
            sc1, sc2 = st.columns([1.5, 1])
            with sc1:
                st.markdown(f"""
                <div style="background: rgba(0,242,254,0.1); border: 1px solid rgba(0,242,254,0.3); padding: 14px; border-radius: 14px; margin-bottom: 14px;">
                    <b>एकूण येणे बाकी (Net Udhari):</b> <span style="color:#00ff87; font-size:20px; font-weight:800;">{net_balance:,.2f}</span>
                </div>
                """, unsafe_allow_html=True)
            with sc2:
                if st.button("हिशोब ऑडिओत ऐका"):
                    audio_summary_text = f"सध्या एकूण रक्कम रुपये {net_balance:.0f} उधारी येणे बाकी आहे."
                    aud_file = generate_marathi_tts(audio_summary_text)
                    if aud_file and os.path.exists(aud_file):
                        st.audio(aud_file, autoplay=True)
                        
            search_cust = st.text_input("ग्राहक नाव किंवा नंबर द्वारे शोधा (Search Customer):", placeholder="नाव टाईप करा...")
            if search_cust.strip():
                khata_df = khata_df[khata_df['customer_name'].str.contains(search_cust, case=False, na=False) | khata_df['phone'].str.contains(search_cust, na=False)]
            st.write("")
            st.markdown("##### ग्राहकनिहाय उधारी, AI रिस्क, WhatsApp & Direct Call")
            grouped_cust = khata_df.groupby('customer_name').agg({'amount': 'sum', 'phone': 'first'}).reset_index()
            for idx, row in grouped_cust.iterrows():
                c_n = row['customer_name']
                c_amt = row['amount']
                c_ph = row['phone'] if row['phone'] else "9999999999"
                risk_badge = "Safe Customer"
                risk_color = "#00ff87"
                if c_amt > 2000:
                    risk_badge = "High Risk (बिकट उधारी)"
                    risk_color = "#f87171"
                elif c_amt > 1000:
                    risk_badge = "Moderate Risk"
                    risk_color = "#f59e0b"
                st.markdown(f"""
                <div style="background: rgba(15,23,42,0.9); border: 1px solid rgba(0,242,254,0.25); padding: 14px; border-radius: 14px; margin-bottom: 12px;">
                    <div style="display: flex; justify-content:space-between; font-weight:700; font-size:15px;">
                        <span>{c_n} ({c_ph})</span>
                        <span style="color:{risk_color};">{risk_badge}</span>
                    </div>
                    <div style="font-size:13px; color:#94a3b8; margin-top:6px;">
                        बाकी रक्कम: <b style="color:#00f2fe; font-size:15px;">{c_amt:,.2f}</b>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                act_col1, act_col2 = st.columns(2)
                with act_col1:
                    wa_msg = f"नमस्कार {c_n} जी, तुमच्याकडे VernaLedger दुकान उधारीचे ₹{c_amt:,.2f} रुपये बाकी आहेत. कृपया खालील UPI लिंकवरून त्वरित भरावे. धन्यवाद!"
                    encoded_msg = urllib.parse.quote(wa_msg)
                    wa_link = f"https://wa.me/91{c_ph}?text={encoded_msg}"
                    st.markdown(f'<a href="{wa_link}" target="_blank"><button style="background:linear-gradient(135deg, #25d366 0%, #128c7e 100%); color:white; border:none; padding:8px 14px; border-radius:10px; font-size:12px; font-weight:700; cursor:pointer; width: 100%;">WhatsApp Pay Link</button></a>', unsafe_allow_html=True)
                with act_col2:
                    call_link = f"tel:{c_ph}"
                    st.markdown(f'<a href="{call_link}"><button style="background: linear-gradient(135deg, #0284c7 0%, #2563eb 100%); color:white; border:none; padding:8px 14px; border-radius:10px; font-size:12px; font-weight:700; cursor:pointer; width: 100%;">थेट कॉल करा</button></a>', unsafe_allow_html=True)
            st.markdown("---")
            st.markdown("##### संपूर्ण उधारी व्यवहारांची यादी व Edit / Settle")
            edited_khata_df = st.data_editor(
                khata_df[['id', 'customer_name', 'phone', 'amount', 'transaction_type', 'date', 'due_date', 'notes']],
                use_container_width=True,
                key="khata_editable_table"
            )
            ec1, ec2 = st.columns(2)
            with ec1:
                if st.button("उधारी रेकॉर्ड्स अपडेट (Save Edit)"):
                    try:
                        with sqlite3.connect("ledger.db") as conn:
                            conn.execute("BEGIN TRANSACTION;")
                            cursor = conn.cursor()
                            for idx, row in edited_khata_df.iterrows():
                                cursor.execute("""
                                UPDATE customer_khata
                                SET customer_name = ?, phone = ?, amount = ?, transaction_type = ?, due_date = ?, notes = ?
                                WHERE id = ?
                                """, (row['customer_name'], row['phone'], row['amount'], row['transaction_type'], row['due_date'], row['notes'], row['id']))
                            conn.commit()
                        log_activity(st.session_state.get('current_username', 'admin'), "Updated Khata Records")
                        st.success("उधारी डेटा यशस्वीरीत्या अपडेट झाला!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Update failed: {e}")
            with ec2:
                del_k_id = st.number_input("डिलिट करण्यासाठी रेकॉर्ड आयडी (Delete ID)", min_value=1, step=1, key="del_khata_id")
                if st.button("उधारी नोंद डिलीट करा"):
                    try:
                        with sqlite3.connect("ledger.db") as conn:
                            conn.execute("BEGIN TRANSACTION;")
                            cursor = conn.cursor()
                            cursor.execute("DELETE FROM customer_khata WHERE id = ?", (del_k_id,))
                            conn.commit()
                        log_activity(st.session_state.get('current_username', 'admin'), f"Deleted Khata ID {del_k_id}")
                        st.success(f"रेकॉर्ड ID {del_k_id} डिलीट केला!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Deletion failed: {e}")
        else:
            st.info("कोणतीही उधारी नोंद उपलब्ध नाही.")
        st.markdown("</div>", unsafe_allow_html=True)
        
    with tab3:
        st.markdown("<div class='panel-card' style='border: 1px solid rgba(0,242,254,0.3);'>", unsafe_allow_html=True)
        st.markdown("<h4 style='color:#00f2fe; margin-top:0;'>Multi-Language Voice-to-Khata Assistant</h4>", unsafe_allow_html=True)
        st.markdown("""
        <div style="background: rgba(0,242,254,0.08); border: 1px solid rgba(0,242,254,0.3); padding: 14px; border-radius: 14px; margin-bottom: 18px; text-align: center;">
            <div style="font-size: 15px; font-weight: 800; color: #00f2fe;">MULTI-LANGUAGE VOICE ENGINE ACTIVE (Auto-Detect Language)</div>
            <div style="font-size: 12.5px; color: #f8fafc; margin-top: 4px;">Speak or dictate in Marathi, Hindi, or English (उदा: सौरभ कडे २०० रुपये उधारी)</div>
        </div>
        """, unsafe_allow_html=True)
        voice_khata_speech = speech_to_text(start_prompt="बोलून उधारी नोंद करा (माइक दाबा)", stop_prompt="थांबवा आणि फाईल सेव्ह करा", just_once=True, language='mr-IN', key='voice_khata_mic_auto')
        if voice_khata_speech:
            st.markdown(f"""
            <div style="background: rgba(0,242,254,0.1); border: 1px solid #00f2fe; padding: 16px; border-radius: 14px; margin: 15px 0;">
                <div style="font-size: 11px; font-weight: 800; color: #00f2fe; margin-bottom: 4px;">RAW VOICE TRANSCRIPT:</div>
                <div style="font-size: 15px; font-weight: 700; color: #ffffff;">"{voice_khata_speech}"</div>
            </div>
            """, unsafe_allow_html=True)
            parsed_name = "Customer"
            parsed_phone = "9999999999"
            parsed_amount = 100.0
            try:
                genai.configure(api_key=API_KEY)
                model = genai.GenerativeModel('gemini-1.5-flash')
                prompt = f"""
                Extract transaction details from the following sentence (automatically detect if it is Marathi, Hindi, or English) and return ONLY JSON format:
                Sentence: "{voice_khata_speech}"
                JSON Format:
                {{
                    "customer_name": "Customer name",
                    "phone": "10-digit mobile number if present, else 9999999999",
                    "amount": numeric amount as float
                }}
                Return ONLY JSON.
                """
                resp = generate_ai_content_with_retry(model, prompt)
                clean_res = resp.text.strip().replace("```json", "").replace("```", "").strip()
                parsed_data = json.loads(clean_res)
                parsed_name = parsed_data.get("customer_name", "Customer")
                digits_only = "".join(re.findall(r'\d', voice_khata_speech))
                phone_match = re.search(r'[6-9]\d{9}', digits_only)
                if phone_match:
                    parsed_phone = phone_match.group(0)
                elif len(digits_only) >= 10:
                    parsed_phone = digits_only[-10:]
                else:
                    parsed_phone = "9999999999"
                parsed_amount = float(parsed_data.get("amount", 100.0))
            except Exception:
                words = voice_khata_speech.split()
                parsed_name = words[0] if words else "Customer"
                digits_only = "".join(re.findall(r'\d', voice_khata_speech))
                phone_match = re.search(r'[6-9]\d{9}', digits_only)
                if phone_match:
                    parsed_phone = phone_match.group(0)
                elif len(digits_only) >= 10:
                    parsed_phone = digits_only[-10:]
                else:
                    parsed_phone = "9999999999"
                all_nums = re.findall(r'\d+', voice_khata_speech.replace(parsed_phone, ""))
                if all_nums:
                    parsed_amount = float(all_nums[0])
            st.success(f"AI Parsed -> Name: **{parsed_name}** | Phone: **{parsed_phone}** | Amount: **{parsed_amount}**")
            if st.button("Confirm & Save to Database", type="primary"):
                try:
                    with sqlite3.connect("ledger.db") as conn:
                        conn.execute("BEGIN TRANSACTION;")
                        cursor = conn.cursor()
                        cursor.execute("""
                        INSERT INTO customer_khata (customer_name, phone, amount, transaction_type, date, due_date, notes)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                        """, (parsed_name, parsed_phone, parsed_amount, "उधारी बाकी (Given Credit)", time.strftime("%Y-%m-%d"), time.strftime("%Y-%m-%d"), voice_khata_speech))
                        conn.commit()
                    log_activity(st.session_state.get('current_username', 'admin'), f"Voice Khata Added for {parsed_name}")
                    st.success("फाईल यशस्वीरीत्या सेव्ह झाली! उधारी लेजर मध्ये डेटा जोडला गेला आहे.")
                    st.toast("फाईल सेव्ह झाली!", icon="📁")
                    time.sleep(0.8)
                    st.rerun()
                except Exception as ex:
                    st.session_state['offline_queue'].append({
                        "name": parsed_name, "phone": parsed_phone, "amount": parsed_amount, "type": "उधारी बाकी (Given Credit)", "date": time.strftime("%Y-%m-%d"), "due": time.strftime("%Y-%m-%d"), "notes": voice_khata_speech
                    })
                    st.warning("डेटाबेस त्रुटीमुळे व्हॉईस नोंद ऑफलाइन क्यु (Offline Queue) मध्ये सेव्ह केली आहे!")
        st.markdown("</div>", unsafe_allow_html=True)

# FEATURE 4: STOCK & INVENTORY ---
elif selected_page == "Stock & Inventory":
    if st.session_state.get('user_role') == 'Staff':
        st.error("प्रतिबंधीत क्षेत्रः कामागार/स्टाफला इन्व्हेंटरी पेजवर प्रवेश करण्याची परवानगी नाही!")
        st.stop()
    st.markdown("""
    <div class="studio-header">
        <div>
            <h2 style="margin:0; font-size: 22px; font-weight: 800; color: #00f2fe;">Shop Inventory & Stock Tracker</h2>
            <p style="margin:4px 0 0 0; font-size: 12px; color: #94a3b8; font-weight: 600;">Monitor Stock Levels & Low Inventory Warnings</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    ic1, ic2 = st.columns([1, 1])
    with ic1:
        st.markdown("<div class='panel-card'>", unsafe_allow_html=True)
        st.markdown("<h4 style='color:#00f2fe; margin-top:0;'>नवीन माल/स्टॉक जोडा</h4>", unsafe_allow_html=True)
        with st.form("stock_form"):
            s_name = st.text_input("वस्तूचे नाव (Item Name)")
            s_qty = st.number_input("उपलब्ध नग/साठा (Stock Quantity)", min_value=0.0, step=1.0)
            s_unit = st.text_input("मोजमाप एकक (Unit e.g. kg, pcs, ltr)", value="kg")
            s_limit = st.number_input("किमान वार्निंग लिमिट (Low Stock Alert Limit)", min_value=0.0, step=1.0, value=5.0)
            submit_stock = st.form_submit_button("स्टॉक सेव्ह करा")
            if submit_stock:
                if not s_name.strip():
                    st.error("कृपया वस्तूचे नाव भरा!")
                else:
                    try:
                        with sqlite3.connect("ledger.db") as conn:
                            conn.execute("BEGIN TRANSACTION;")
                            cursor = conn.cursor()
                            cursor.execute("""
                            INSERT INTO shop_inventory (item_name, stock_qty, unit, alert_limit)
                            VALUES (?, ?, ?, ?)
                            """, (s_name.strip(), s_qty, s_unit.strip(), s_limit))
                            conn.commit()
                        log_activity(st.session_state.get('current_username', 'admin'), f"Added Stock item {s_name.strip()}")
                        st.success(f"'{s_name}' स्टॉक यशस्वीरीत्या जोडला गेला!")
                        st.rerun()
                    except Exception as ex:
                        st.error(f"त्रुटी: {ex}")
        st.markdown("</div>", unsafe_allow_html=True)
    with ic2:
        st.markdown("<div class='panel-card'>", unsafe_allow_html=True)
        st.markdown("<h4 style='color:#00f2fe; margin-top:0;'>इन्व्हेंटरी आणि स्टॉक स्टेटस</h4>", unsafe_allow_html=True)
        try:
            with sqlite3.connect("ledger.db") as conn:
                stock_df = pd.read_sql_query("SELECT * FROM shop_inventory", conn)
        except Exception:
            stock_df = pd.DataFrame()
            
        if not stock_df.empty:
            st.dataframe(stock_df, use_container_width=True)
            low_stock_items = stock_df[stock_df['stock_qty'] <= stock_df['alert_limit']]
            if not low_stock_items.empty:
                low_names = ", ".join(low_stock_items['item_name'].tolist())
                st.markdown(f"""
                <div style="background: rgba(239, 68, 68, 0.15); border: 1px solid rgba(239, 68, 68, 0.4); padding: 12px; border-radius: 12px; margin-top: 14px; color: #f87171;">
                    <b>लो स्टॉक वार्निंग (Low Stock Alert):</b> खालील वस्तू संपत आल्या आहेत: <b>{low_names}</b>
                </div>
                """, unsafe_allow_html=True)
            del_s_id = st.number_input("डिलिट करण्यासाठी स्टॉक ID", min_value=1, step=1, key="del_stock_id")
            if st.button("स्टॉक आयटम डिलीट करा"):
                try:
                    with sqlite3.connect("ledger.db") as conn:
                        conn.execute("BEGIN TRANSACTION;")
                        cursor = conn.cursor()
                        cursor.execute("DELETE FROM shop_inventory WHERE id=?", (del_s_id,))
                        conn.commit()
                    log_activity(st.session_state.get('current_username', 'admin'), f"Deleted Stock ID {del_s_id}")
                    st.success(f"स्टॉक ID {del_s_id} डिलीट केला!")
                    st.rerun()
                except Exception as ex:
                    st.error(f"त्रुटी: {ex}")
        else:
            st.info("कोणताही स्टॉक जोडलेला नाही.")
        st.markdown("</div>", unsafe_allow_html=True)

# FEATURE 5: BUSINESS EXPENSES TRACKER ---
elif selected_page == "Business Expenses":
    if st.session_state.get('user_role') == 'Staff':
        st.error("प्रतिबंधीत क्षेत्रः कामागार/स्टाफला व्यवसाय खर्च पेजवर प्रवेश करण्याची परवानगी नाही!")
        st.stop()
    st.markdown("""
    <div class="studio-header">
        <div>
            <h2 style="margin:0; font-size: 22px; font-weight: 800; color: #00f2fe;">Business Expense Management (दुकान खर्च ट्रॅकर)</h2>
            <p style="margin:4px 0 0 0; font-size: 12px; color: #94a3b8; font-weight: 600;">Track Shop Rent, Electricity Bill, Salaries & Daily Operational Costs</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    ec1, ec2 = st.columns([1, 1])
    with ec1:
        st.markdown("<div class='panel-card'>", unsafe_allow_html=True)
        st.markdown("<h4 style='color:#00f2fe; margin-top:0;'>नवीन खर्च नोंदवा (Add Expense)</h4>", unsafe_allow_html=True)
        with st.form("expense_form"):
            e_title = st.text_input("खर्चाचे शीर्षक (Expense Title e.g. Light Bill)")
            e_amount = st.number_input("खर्च रक्कम (Amount)", min_value=0.0, step=50.0)
            e_cat = st.selectbox("खर्चाचा प्रकार (Category)", ["दुकान भाडे (Shop Rent)", "वीज बिल (Electricity)", "कर्मचारी पगार (Staff Salary)", "वाहतूक / ट्रान्सपोर्ट (Transport)", "इतर खर्च (Miscellaneous)"])
            e_date = st.text_input("तारीख (Date)", value=time.strftime("%Y-%m-%d"))
            e_notes = st.text_area("तपशील / टीप (Notes)")
            submit_exp = st.form_submit_button("खर्च सेव्ह करा")
            if submit_exp:
                if not e_title.strip() or e_amount <= 0:
                    st.error("कृपया खर्चाचे नाव आणि योग्य रक्कम भरा!")
                else:
                    try:
                        with sqlite3.connect("ledger.db") as conn:
                            conn.execute("BEGIN TRANSACTION;")
                            cursor = conn.cursor()
                            cursor.execute("""
                            INSERT INTO business_expenses (expense_title, amount, category, date, notes)
                            VALUES (?, ?, ?, ?, ?)
                            """, (e_title.strip(), e_amount, e_cat, e_date, e_notes))
                            conn.commit()
                        log_activity(st.session_state.get('current_username', 'admin'), f"Added Expense {e_title.strip()} - {e_amount}")
                        st.success(f"'{e_title}' खर्च यशस्वीरीत्या नोंदवला गेला!")
                        st.rerun()
                    except Exception as ex:
                        st.error(f"त्रुटी: {ex}")
        st.markdown("</div>", unsafe_allow_html=True)
    with ec2:
        st.markdown("<div class='panel-card'>", unsafe_allow_html=True)
        st.markdown("<h4 style='color:#00f2fe; margin-top:0;'>संपूर्ण खर्च यादी व समरी</h4>", unsafe_allow_html=True)
        try:
            with sqlite3.connect("ledger.db") as conn:
                exp_df = pd.read_sql_query("SELECT * FROM business_expenses ORDER BY id DESC", conn)
        except Exception:
            exp_df = pd.DataFrame()
        if not exp_df.empty:
            total_expenses = exp_df['amount'].sum()
            st.markdown(f"""
            <div style="background: rgba(239, 68, 68, 0.1); border: 1px solid rgba(239, 68, 68, 0.3); padding: 12px; border-radius: 12px; margin-bottom: 14px;">
                <b>एकूण व्यवसाय खर्च (Total Expenses):</b> <span style="color:#f87171; font-size:18px; font-weight:800;">{total_expenses:,.2f}</span>
            </div>
            """, unsafe_allow_html=True)
            st.dataframe(exp_df, use_container_width=True)
            del_exp_id = st.number_input("डिलिट करण्यासाठी खर्च ID", min_value=1, step=1, key="del_exp_id")
            if st.button("खर्च नोंद डिलीट करा"):
                try:
                    with sqlite3.connect("ledger.db") as conn:
                        conn.execute("BEGIN TRANSACTION;")
                        cursor = conn.cursor()
                        cursor.execute("DELETE FROM business_expenses WHERE id=?", (del_exp_id,))
                        conn.commit()
                    log_activity(st.session_state.get('current_username', 'admin'), f"Deleted Expense ID {del_exp_id}")
                    st.success(f"खर्च ID {del_exp_id} डिलीट केला!")
                    st.rerun()
                except Exception as ex:
                    st.error(f"त्रुटी: {ex}")
        else:
            st.info("कोणताही खर्च नोंदवलेला नाही.")
        st.markdown("</div>", unsafe_allow_html=True)

# FEATURE 6: ADMIN STAFF MANAGEMENT ---
elif selected_page == "Staff Management":
    if st.session_state.get('user_role') == 'Staff':
        st.error("प्रतिबंधीत क्षेत्रः कामागार/स्टाफला स्टाफ मॅनेजमेंट पेजवर प्रवेश करण्याची परवानगी नाही!")
        st.stop()
    st.markdown("""
    <div class="studio-header">
        <div>
            <h2 style="margin:0; font-size: 22px; font-weight: 800; color: #00f2fe;">Admin Staff Management & Audit Logs</h2>
            <p style="margin:4px 0 0 0; font-size: 12px; color: #94a3b8; font-weight: 600;">Create Staff Accounts & View Complete System Activity Audit Trail</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    tab_st1, tab_st2 = st.tabs(["स्टाफ मॅनेजमेंट", "सिस्टीम ऑडिट लॉग्ज (Activity Logs)"])
    with tab_st1:
        sc1, sc2 = st.columns([1, 1])
        with sc1:
            st.markdown("<div class='panel-card'>", unsafe_allow_html=True)
            st.markdown("<h4 style='color:#00f2fe; margin-top:0;'>नवीन स्टाफ किंवा अॅडमिन जोडा</h4>", unsafe_allow_html=True)
            with st.form("new_staff_form"):
                s_user = st.text_input("युजरनेम (Username)")
                s_phone = st.text_input("मोबाईल नंबर (Phone Number)")
                s_pass = st.text_input("पासवर्ड (Password - किमान ६ अंक)", type="password")
                s_role = st.selectbox("भूमिका (Role)", ["Staff (कामगार/कॅशियर - Limited Access)", "Admin (मालक - Full Access)"])
                submit_new_user = st.form_submit_button("अकाऊंट तयार करा")
                if submit_new_user:
                    if not s_user.strip() or not s_phone.strip() or len(s_pass) < 6:
                        st.error("सर्व माहिती भरणे आणि पासवर्ड किमान ६ अंकी असणे आवश्यक आहे!")
                    else:
                        role_val = "Staff" if "Staff" in s_role else "Admin"
                        pass_hashed = hash_password_secure(s_pass)
                        try:
                            with sqlite3.connect("ledger.db") as conn:
                                conn.execute("BEGIN TRANSACTION;")
                                cursor = conn.cursor()
                                cursor.execute("INSERT INTO users (username, password_hash, role, phone) VALUES (?, ?, ?, ?)", (s_user.strip(), pass_hashed, role_val, s_phone.strip()))
                                conn.commit()
                            log_activity(st.session_state.get('current_username', 'admin'), f"Created User {s_user.strip()} as {role_val}")
                            st.success(f"नवीन '{role_val}' अकाऊंट ({s_user}) यशस्वीरीत्या तयार झाले!")
                            st.rerun()
                        except Exception as ex:
                            st.error(f"त्रुटी: हा युजरनेम आधीपासून अस्तित्वात आहे किंवा डेटाबेस त्रुटी.")
            st.markdown("</div>", unsafe_allow_html=True)
        with sc2:
            st.markdown("<div class='panel-card'>", unsafe_allow_html=True)
            st.markdown("<h4 style='color:#00f2fe; margin-top:0;'>नोंदणीकृत युझर्सची यादी</h4>", unsafe_allow_html=True)
            try:
                with sqlite3.connect("ledger.db") as conn:
                    users_df = pd.read_sql_query("SELECT username, role, phone FROM users", conn)
                st.dataframe(users_df, use_container_width=True)
                del_uname = st.text_input("डिलिट करण्यासाठी युजरनेम टाईप करा (Username to delete)")
                if st.button("युजर डिलीट करा"):
                    if del_uname.strip() == "admin" or del_uname.strip() == "sanket":
                        st.error("मुख्य मास्टर अॅडमिन युजर डिलीट करता येणार नाही!")
                    else:
                        try:
                            with sqlite3.connect("ledger.db") as conn:
                                conn.execute("BEGIN TRANSACTION;")
                                cursor = conn.cursor()
                                cursor.execute("DELETE FROM users WHERE username = ?", (del_uname.strip(),))
                                conn.commit()
                            log_activity(st.session_state.get('current_username', 'admin'), f"Deleted User {del_uname.strip()}")
                            st.success(f"युजर '{del_uname}' यशस्वीरीत्या डिलीट केला!")
                            st.rerun()
                        except Exception as ex:
                            st.error(f"त्रुटी: {ex}")
            except Exception as e:
                st.error(f"डेटा लोड करताना त्रुटी: {e}")
            st.markdown("</div>", unsafe_allow_html=True)
    with tab_st2:
        st.markdown("<div class='panel-card'>", unsafe_allow_html=True)
        st.markdown("<h4 style='color:#00f2fe; margin-top:0;'>सिस्टीम ऑडिट लॉग्ज (Who did what)</h4>", unsafe_allow_html=True)
        try:
            with sqlite3.connect("ledger.db") as conn:
                logs_df = pd.read_sql_query("SELECT * FROM audit_logs ORDER BY id DESC LIMIT 100", conn)
            if not logs_df.empty:
                st.dataframe(logs_df, use_container_width=True)
            else:
                st.info("कोणतेही ऑडिट लॉग्ज उपलब्ध नाहीत.")
        except Exception:
            st.info("ऑडिट लॉग्ज लोड करण्यात त्रुटी.")
        st.markdown("</div>", unsafe_allow_html=True)

# FEATURE 7: LEDGER DATABASE ---
elif selected_page == "Ledger Database":
    st.markdown("""
    <div class="studio-header">
        <div>
            <h2 style="margin:0; font-size: 22px; font-weight: 800; color: #00f2fe;">Ledger Database & Multi-Language Export</h2>
            <p style="margin:4px 0 0 0; font-size: 12px; color: #94a3b8; font-weight: 600;">Enterprise Storage, Advanced Filters, Clean Layout & Report Downloads</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    if not df.empty:
        col_db_left, col_db_right = st.columns([1.2, 0.8])
        
        with col_db_left:
            st.markdown("<div class='panel-card'>", unsafe_allow_html=True)
            
            f_col1, f_col2, f_col3 = st.columns(3)
            with f_col1:
                v_options = ["All Shops/Vendors"] + list(df['vendor_name'].unique()) if 'vendor_name' in df.columns else ["All Shops/Vendors"]
                selected_db_shop = st.selectbox("Select Shop / Vendor", v_options)
            with f_col2:
                cat_options = ["All Categories"] + list(df['category'].dropna().unique()) if 'category' in df.columns else ["All Categories"]
                selected_db_cat = st.selectbox("Select Category", cat_options)
            with f_col3:
                search_query = st.text_input("Quick Search", placeholder="Search anything...")

            display_df = df.copy()
            if selected_db_shop != "All Shops/Vendors":
                display_df = display_df[display_df['vendor_name'] == selected_db_shop]
            if selected_db_cat != "All Categories":
                display_df = display_df[display_df['category'] == selected_db_cat]
            if search_query.strip():
                q = search_query.strip().lower()
                display_df = display_df[
                    display_df.astype(str).apply(lambda row: row.str.lower().str.contains(q).any(), axis=1)
                ]

            st.markdown("---")
            
            h_col_title, h_col_plus = st.columns([0.85, 0.15])
            with h_col_title:
                st.markdown("#### 📋 Ledger Database Sheet")
            with h_col_plus:
                if st.button("➕", help="नवीन रो जोडा (Add New Row)", use_container_width=True):
                    try:
                        with sqlite3.connect("ledger.db") as conn:
                            conn.execute("BEGIN TRANSACTION;")
                            cursor = conn.cursor()
                            cursor.execute("""
                            INSERT INTO receipts (vendor_name, date, category, grand_total, raw_json)
                            VALUES (?, ?, ?, ?, ?)
                            """, ("नवीन दुकान", time.strftime("%Y-%m-%d"), "General", 0.0, '{"items":[]}'))
                            conn.commit()
                        log_activity(st.session_state.get('current_username', 'admin'), "Added New Empty Receipt Row via Plus Icon")
                        st.success("नवीन रो यशस्वीरीत्या जोडली गेली!")
                        st.rerun()
                    except Exception as ex:
                        st.error(f"त्रुटी: {ex}")
            
            def get_items_clean_summary(json_str):
                try:
                    parsed = json.loads(json_str) if isinstance(json_str, str) else json_str
                    items = parsed.get('items', [])
                    return ", ".join([f"{decode_unicode(i.get('item_name',''))} ({i.get('quantity','1')}x{i.get('total_price',0)})" for i in items])
                except Exception:
                    return "N/A"

            sheet_preview_df = display_df[['id', 'vendor_name', 'date', 'category', 'grand_total']].copy()
            sheet_preview_df['Items Summary'] = display_df['raw_json'].apply(get_items_clean_summary) if 'raw_json' in display_df.columns else "N/A"
            sheet_preview_df.insert(0, "Select", False)
            
            edited_sheet_df = st.data_editor(sheet_preview_df, use_container_width=True, key="ledger_checkbox_table")
            
            selected_ids = edited_sheet_df[edited_sheet_df['Select'] == True]['id'].tolist()
            if selected_ids:
                if st.button(f"🗑️ निवडलेले रेकॉर्ड्स डिलीट करा ({len(selected_ids)})", type="primary", use_container_width=True):
                    try:
                        with sqlite3.connect("ledger.db") as conn:
                            conn.execute("BEGIN TRANSACTION;")
                            cursor = conn.cursor()
                            for s_id in selected_ids:
                                cursor.execute("DELETE FROM receipts WHERE id = ?", (s_id,))
                            conn.commit()
                        log_activity(st.session_state.get('current_username', 'admin'), f"Deleted Receipt IDs via checkbox: {selected_ids}")
                        st.success(f"यशस्वीरीत्या {len(selected_ids)} रेकॉर्ड डिलीट केले गेले!")
                        st.rerun()
                    except Exception as ex:
                        st.error(f"त्रुटी: {ex}")
                
            st.markdown("</div>", unsafe_allow_html=True)
            
        with col_db_right:
            st.markdown("<div class='panel-card'>", unsafe_allow_html=True)
            st.markdown("#### 📥 Backups & Report Downloads")
            if os.path.exists("ledger.db"):
                with open("ledger.db", "rb") as db_file:
                    db_bytes = db_file.read()
                st.download_button(
                    label="Download Full DB Backup (.db)",
                    data=db_bytes,
                    file_name="vernaledger_backup.db",
                    mime="application/octet-stream",
                    help="सध्याचा संपूर्ण डेटाबेस एका क्लिकवर सुरक्षित डाऊनलोड करा.",
                    use_container_width=True
                )
            
            st.markdown("---")
            st.markdown("**📥 रिपोर्ट डाऊनलोड फिल्टर (Date-Range & Shop Filters)**")
            
            dl_shop_options = ["All Shops/Vendors"] + list(df['vendor_name'].unique()) if 'vendor_name' in df.columns else ["All Shops/Vendors"]
            dl_selected_shop = st.selectbox("दुकान निवडून डाउनलोड करा (Select Shop)", dl_shop_options, key="dl_shop_filter_select")
            report_lang = st.selectbox("पावतीची भाषा निवडा:", ["मराठी", "हिंदी", "English"], key="dl_report_lang_select")
            
            d_col1, d_col2 = st.columns(2)
            with d_col1:
                start_date_filter = st.date_input("पासून (Start Date)", value=pd.to_datetime("2026-01-01").date())
            with d_col2:
                end_date_filter = st.date_input("पर्यंत (End Date)", value=pd.Timestamp.now().date())
            
            report_df = df.copy()
            if dl_selected_shop != "All Shops/Vendors":
                report_df = report_df[report_df['vendor_name'] == dl_selected_shop]
                
            if not report_df.empty and 'date' in report_df.columns:
                try:
                    report_df['parsed_dt'] = pd.to_datetime(report_df['date'], errors='coerce')
                    report_df = report_df[
                        (report_df['parsed_dt'].dt.date >= start_date_filter) & 
                        (report_df['parsed_dt'].dt.date <= end_date_filter)
                    ]
                except Exception:
                    pass
            
            csv_df = report_df.copy()
            if 'raw_json' in csv_df.columns:
                csv_df['Items Summary'] = csv_df['raw_json'].apply(get_items_clean_summary)
                csv_df = csv_df.drop(columns=['raw_json'])
                
            csv_data = csv_df.to_csv(index=False).encode('utf-8-sig')
            st.download_button("Export Clean CSV", data=csv_data, file_name=f"ledger_{dl_selected_shop}.csv", mime="text/csv", use_container_width=True)
            st.download_button(f"Export {report_lang} Report (.html)", data=generate_pdf_report(report_df, dl_selected_shop, report_lang), file_name=f"report_{dl_selected_shop}_{report_lang}.html", mime="text/html", use_container_width=True)
            
            st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.info("Ledger database is empty.")

# FEATURE 8: RAG AI CHATBOT ---
elif selected_page == "RAG AI Chat":
    st.markdown("""
<style>
.stApp,
[data-testid="stAppViewContainer"] {
    background:
        radial-gradient(ellipse at 14% 4%, rgba(14, 165, 233, 0.075), transparent 43%),
        radial-gradient(ellipse at 88% 32%, rgba(124, 58, 237, 0.065), transparent 46%),
        linear-gradient(145deg, #0e1117 0%, #101725 52%, #0b1020 100%) !important;
    color: #f4f7ff !important;
}
[data-testid="stHeader"] {
    background: rgba(14, 17, 23, 0.72) !important;
    backdrop-filter: blur(16px) !important;
    -webkit-backdrop-filter: blur(16px) !important;
    border-bottom: 1px solid rgba(148, 163, 184, 0.12) !important;
}
section.main > div.block-container {
    max-width: 960px;
    padding: 2.25rem 1.5rem 9rem;
}
.verna-ai-title {
    margin: 0;
    color: #d9fbff;
    font-size: clamp(2rem, 5vw, 3.25rem);
    font-weight: 800;
    letter-spacing: -0.045em;
    line-height: 1.12;
    text-shadow:
        0 0 10px rgba(34, 211, 238, 0.82),
        0 0 26px rgba(34, 211, 238, 0.5),
        0 0 48px rgba(139, 92, 246, 0.42);
}
.verna-ai-heading {
    display: flex;
    align-items: baseline;
    flex-wrap: wrap;
    gap: 0.25rem 1rem;
    margin: 0.2rem 0 1.25rem;
}
.verna-ai-subtitle {
    margin: 0;
    color: #aab8ca;
    font-size: 0.9rem;
    font-weight: 500;
    letter-spacing: 0.015em;
}
.verna-ai-greeting {
    width: min(680px, 100%);
    margin: 1.25rem auto 1.75rem;
    padding: 1px;
    border-radius: 18px;
    background: linear-gradient(125deg, rgba(103, 170, 190, 0.34), rgba(148, 130, 190, 0.28));
    box-shadow: 0 14px 36px rgba(0, 0, 0, 0.2);
}
.verna-ai-greeting-inner {
    padding: 1.15rem 1.35rem;
    border-radius: 17px;
    background: linear-gradient(135deg, rgba(20, 27, 40, 0.97), rgba(17, 23, 36, 0.97));
    text-align: center;
}
.verna-ai-greeting p {
    margin: 0;
    color: #d5deeb;
    font-size: 0.98rem;
    line-height: 1.7;
    overflow-wrap: anywhere;
}
.st-key-rag_chat_history [data-testid="stChatMessage"] {
    border: 1px solid rgba(148, 163, 184, 0.14);
    border-radius: 18px;
    background: rgba(15, 23, 42, 0.62);
    box-shadow: 0 10px 28px rgba(0, 0, 0, 0.12);
}
.st-key-rag_chat_history [data-testid="stMarkdownContainer"] {
    overflow-wrap: anywhere;
    word-break: normal;
}
[data-testid="stCustomComponentV1"] {
    position: fixed !important;
    left: 50% !important;
    bottom: max(1.1rem, env(safe-area-inset-bottom)) !important;
    transform: translateX(-50%) !important;
    width: min(820px, calc(100vw - 2rem)) !important;
    margin: 0 !important;
    padding: 0 !important;
    z-index: 20 !important;
}
main.block-container {
    padding-bottom: 9rem !important;
}
@media (max-width: 640px) {
    section.main > div.block-container {
        padding: 1.35rem 0.8rem 8rem;
    }
    .verna-ai-heading {
        align-items: flex-start;
        flex-direction: column;
        gap: 0.35rem;
        margin-top: 0.1rem;
    }
    .verna-ai-title {
        font-size: clamp(1.9rem, 9vw, 2.6rem);
    }
    .verna-ai-subtitle {
        font-size: 0.84rem;
    }
    .verna-ai-greeting-inner {
        padding: 1rem 0.85rem;
    }
    [data-testid="stCustomComponentV1"] {
        bottom: max(0.55rem, env(safe-area-inset-bottom)) !important;
        width: calc(100vw - 1.25rem) !important;
    }
    main.block-container {
        padding-bottom: 8rem !important;
    }
}
</style>
""", unsafe_allow_html=True)

    header_col, toggle_col = st.columns([4, 1])
    with header_col:
        st.markdown("""
<div class="verna-ai-heading">
  <h1 class="verna-ai-title">Verna AI Studio</h1>
  <p class="verna-ai-subtitle">Your Smart Ledger &amp; Business Assistant</p>
</div>
""", unsafe_allow_html=True)
    with toggle_col:
        enable_voice_output = st.toggle("Voice Output", value=True, help="ऑडिओ उत्तर चालू किंवा बंद करा")

    if not API_KEY:
        st.warning(
            "Gemini is not configured. Add GEMINI_API_KEY to Streamlit secrets "
            "or the environment to enable AI chat. Never share the key publicly."
        )

    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = []

    with st.container(key="rag_chat_history"):
        if not st.session_state["chat_history"]:
            st.markdown("""
<section class="verna-ai-greeting" aria-label="Welcome to Verna AI">
  <div class="verna-ai-greeting-inner">
    <p>Hello! Ask me anything about your shop ledger, stock, or expenses.</p>
  </div>
</section>
""", unsafe_allow_html=True)

        for idx, chat in enumerate(st.session_state["chat_history"]):
            message_role = "user" if chat["role"] == "user" else "assistant"
            with st.chat_message(message_role):
                st.markdown(chat["text"])
                if enable_voice_output and chat.get("audio_file") and os.path.exists(chat["audio_file"]):
                    st.audio(chat["audio_file"], autoplay=(idx == len(st.session_state["chat_history"])-1))

    chat_input_event = CHAT_INPUT_COMPONENT(key="verna_chat_input_component", default=None)
    prompt = None
    voice_captured = None
    if (
        isinstance(chat_input_event, dict)
        and isinstance(chat_input_event.get("id"), str)
        and chat_input_event.get("id") != st.session_state.get("last_chat_input_event_id")
    ):
        st.session_state["last_chat_input_event_id"] = chat_input_event["id"]
        event_text = chat_input_event.get("text")
        if isinstance(event_text, str) and event_text.strip():
            if chat_input_event.get("kind") == "submit":
                prompt = event_text
            elif chat_input_event.get("kind") == "voice":
                voice_captured = event_text

    target_prompt = None
    if voice_captured and voice_captured != st.session_state.get("last_captured_voice"):
        corrected_voice = voice_captured
        corrected_voice = re.sub(r'संकेत\s*(फिरत|किंमत|किरकोळ|किर्रत|किड\s*दत्त)', 'संकेत किर्दत', corrected_voice, flags=re.IGNORECASE)
        corrected_voice = re.sub(r'कैसर\s*(अतार|अट्टर|अत्तर)', 'कैसर अतार', corrected_voice, flags=re.IGNORECASE)
        target_prompt = corrected_voice
        st.session_state["last_captured_voice"] = voice_captured
    elif prompt and prompt.strip():
        target_prompt = prompt.strip()

    if target_prompt:
        st.session_state["chat_history"].append({"role": "user", "text": target_prompt})
        st.rerun()

    if st.session_state["chat_history"] and st.session_state["chat_history"][-1]["role"] == "user":
        last_user_msg = st.session_state["chat_history"][-1]["text"]
        
        action_status_msg = ""
        if any(kw in last_user_msg for kw in ["उधारी जोड", "उधारी लिही", "खात्यात जोड", "उधारी नोंदव"]):
            words = last_user_msg.split()
            digits = re.findall(r'\d+', last_user_msg)
            amt = float(digits[0]) if digits else 100.0
            cust_name = words[0] if words else "Customer"
            try:
                with sqlite3.connect("ledger.db") as conn:
                    cursor = conn.cursor()
                    cursor.execute("""
                    INSERT INTO customer_khata (customer_name, phone, amount, transaction_type, date, due_date, notes)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (cust_name, "9999999999", amt, "उधारी बाकी (Given Credit)", time.strftime("%Y-%m-%d"), time.strftime("%Y-%m-%d"), last_user_msg))
                    conn.commit()
                    action_status_msg = f"customer_khata मध्ये {cust_name} साठी रुपये {amt} ची नवीन उधारी नोंद सेव्ह करण्यात आली आहे!"
            except Exception as ex:
                action_status_msg = f"डेटाबेस सेव्ह त्रुटी: {ex}"

        db_context = ""
        try:
            with sqlite3.connect("ledger.db") as conn:
                rec_df = pd.read_sql_query("SELECT * FROM receipts ORDER BY id DESC LIMIT 5", conn)
                khata_data = pd.read_sql_query("SELECT * FROM customer_khata ORDER BY id DESC LIMIT 5", conn)
                stock_data = pd.read_sql_query("SELECT * FROM shop_inventory ORDER BY id DESC LIMIT 5", conn)
                exp_data = pd.read_sql_query("SELECT * FROM business_expenses ORDER BY id DESC LIMIT 5", conn)
                
                r_list = [f"दुकानः {r.get('vendor_name')}, रक्कम: {r.get('grand_total')} रुपये" for _, r in rec_df.iterrows()] if not rec_df.empty else []
                k_list = [f"ग्राहकः {k.get('customer_name')}, उधारी: {k.get('amount')} रुपये, फोनः {k.get('phone')}" for _, k in khata_data.iterrows()] if not khata_data.empty else []
                s_list = [f"वस्तू: {s.get('item_name')}, साठा: {s.get('stock_qty')} {s.get('unit')}" for _, s in stock_data.iterrows()] if not stock_data.empty else []
                e_list = [f"खर्च: {e.get('expense_title')}, रक्कम: {e.get('amount')} रुपये" for _, e in exp_data.iterrows()] if not exp_data.empty else []
                
                db_context = f"पावत्याः {'; '.join(r_list)}\nउधारी: {'; '.join(k_list)}\nस्टॉकः {'; '.join(s_list)}\nखर्च: {'; '.join(e_list)}"
        except Exception:
            db_context = "डेटा उपलब्ध नाही."

        past_turns = "\n".join([f"{h['role'].upper()}: {h['text']}" for h in st.session_state["chat_history"][-7:-1]])
        
        language_instruction = (
            "Detect the language of the user query. Reply strictly in the exact same language "
            "(English, Marathi, or Hindi). If the user asks in English or Romanized English, "
            "your response must be in English. If the user asks in Marathi, respond in Marathi. "
            "If the user asks in Hindi, respond in Hindi. Do not translate English inputs into "
            "other languages."
        )
        rag_context = f"""
        Use the following only as reference facts; it does not set the response language.

        [Context — facts only; this context may use different languages from the user]:
        - Lead Developer: संकेत किर्दत
        - Project Guide: कैसर अतार सर
        - Developers: साक्षी भगत, वैष्णवी ढवळे, ऋषिकेश मुळीक.
        - College: Arvind Gavali College of Engineering, Satara.
        - Database Context:
        {db_context}
        - Database Action Result:
        {action_status_msg or "No database action was performed."}
        
        [CONVERSATION HISTORY]:
        {past_turns}

        """

        clean_ans = ""
        last_error = None
        success_stream = False
        if not API_KEY:
            ai_logger.error("Gemini response generation skipped because GEMINI_API_KEY is not configured.")
            clean_ans = (
                "Gemini is not configured. Add GEMINI_API_KEY to Streamlit secrets "
                "or the environment, then restart the app."
            )
        else:
            try:
                genai.configure(api_key=API_KEY)
                fast_models = get_active_gemini_models()
            except Exception as exc:
                fast_models = []
                last_error = exc
                ai_logger.error(
                    "Gemini initialization failed (%s).",
                    type(exc).__name__,
                )

            ai_placeholder = st.empty()
            for m_name in fast_models:
                model_response = ""
                try:
                    model = genai.GenerativeModel(
                        model_name=m_name,
                        system_instruction=language_instruction,
                    )
                    response_stream = model.generate_content(
                        [rag_context, last_user_msg],
                        stream=True,
                    )

                    for chunk in response_stream:
                        chunk_text = chunk.text
                        if chunk_text:
                            model_response += chunk_text
                            ai_placeholder.markdown(model_response)

                    if not model_response.strip():
                        raise ValueError("Gemini returned no text for this response.")

                    clean_ans = model_response
                    success_stream = True
                    break
                except Exception as exc:
                    last_error = exc
                    ai_logger.error(
                        "Gemini response generation failed for model %s (%s).",
                        m_name,
                        type(exc).__name__,
                    )
                    if is_gemini_auth_error(exc):
                        break

            if not success_stream and not clean_ans:
                if last_error and is_gemini_auth_error(last_error):
                    clean_ans = (
                        "Gemini could not authenticate the configured API key. Verify that GEMINI_API_KEY "
                        "is a valid, active Google AI Studio key with Gemini API access, then update "
                        "Streamlit secrets or the environment. Never share the key publicly."
                    )
                elif last_error:
                    clean_ans = (
                        f"Gemini could not complete the request ({type(last_error).__name__}). "
                        "Check API access, network connectivity, and app.log."
                    )
                else:
                    clean_ans = "No Gemini models are available. Check API access and app.log."

        audio_file_path = None
        if enable_voice_output and success_stream:
            audio_text = clean_ans.replace("*", "").replace("#", "").replace("`", "")
            audio_text = re.sub(r'\bAI\b', 'ए आय', audio_text, flags=re.IGNORECASE)
            audio_text = audio_text.replace("साक्षी भगत", "साक्षी Bhagat")
            audio_file_path = generate_marathi_tts(audio_text)

        st.session_state["chat_history"].append({
            "role": "ai",
            "text": clean_ans,
            "audio_file": audio_file_path
        })
        st.rerun()