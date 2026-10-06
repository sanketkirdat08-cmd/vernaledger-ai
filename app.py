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
import math
from datetime import date, datetime
from html import escape
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
    layout="wide",
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

# --- INITIALIZE STATE FROM QUERY PARAMS EARLY ---
if "lang" in st.query_params and "ui_language" not in st.session_state:
    st.session_state["ui_language"] = st.query_params["lang"]
    st.session_state["ui_language_english"] = st.query_params["lang"] == "en"

if "page" in st.query_params and "selected_page" not in st.session_state:
    st.session_state["selected_page"] = st.query_params["page"]

if "subpage" in st.query_params and "business_dropdown" not in st.session_state:
    st.session_state["business_dropdown"] = st.query_params["subpage"]

# Sync localStorage using a small JS injection just to satisfy localStorage persistence fallback
import streamlit.components.v1 as components
def sync_local_storage():
    lang = st.session_state.get("ui_language", "mr")
    page = st.session_state.get("selected_page", "OCR Scanner")
    # Only inject JS if state changed, preventing iframe from recreating and stealing focus every rerun!
    if st.session_state.get("last_synced_lang") != lang or st.session_state.get("last_synced_page") != page:
        st.session_state["last_synced_lang"] = lang
        st.session_state["last_synced_page"] = page
        components.html(
            f'''
            <script>
                try {{
                    window.parent.localStorage.setItem('vernaledger_lang', '{lang}');
                    window.parent.localStorage.setItem('vernaledger_page', '{page}');
                }} catch (e) {{}}
            </script>
            ''',
            height=0, width=0
        )
sync_local_storage()



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


def get_tts_voice(text: str) -> str:
    """Choose an Edge TTS voice based on the language of the generated answer."""
    devanagari_count = len(re.findall(r"[\u0900-\u097f]", text))
    latin_count = len(re.findall(r"[A-Za-z]", text))
    if latin_count > devanagari_count:
        return "en-IN-NeerjaNeural"

    marathi_markers = (
        "ळ", "ऱ", "आहे", "आहेत", "आणि", "तुमच्या", "तुम्ही", "तुम्हाला",
        "साठी", "मध्ये", "म्हणून", "उधारी", "किती", "नमस्कार", "ठरू शकते",
        "विचारू शकता",
    )
    hindi_markers = (
        "है", "हैं", "और", "आपके", "आपकी", "के लिए", "क्योंकि", "सकते हैं",
        "करता है", "होता है",
    )
    marathi_score = sum(text.count(marker) for marker in marathi_markers)
    hindi_score = sum(text.count(marker) for marker in hindi_markers)
    return "mr-IN-AarohiNeural" if marathi_score > hindi_score else "hi-IN-SwaraNeural"


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


KHATA_CREDIT = "उधारी बाकी (Given Credit)"
KHATA_PAYMENT = "पैसे जमा / हप्ता (Received Payment / Partial)"
KHATA_TRANSACTION_TYPES = (KHATA_CREDIT, KHATA_PAYMENT)
KHATA_COLUMNS = [
    "id", "customer_name", "phone", "amount", "transaction_type",
    "date", "due_date", "notes",
]


def _khata_text(value):
    if value is None:
        return ""
    try:
        if pd.isna(value):
            return ""
    except (TypeError, ValueError):
        pass
    return str(value)


def load_business_upi_id():
    try:
        secret_value = st.secrets.get("BUSINESS_UPI_ID", "")
    except Exception as exc:
        ai_logger.warning(
            "Could not read BUSINESS_UPI_ID from Streamlit secrets (%s).",
            type(exc).__name__,
        )
        secret_value = ""
    environment_value = os.getenv("BUSINESS_UPI_ID", "")
    return str(
        secret_value or environment_value or "sanketkirdat08@okaxis"
    ).strip()


def build_upi_payment_link(upi_id, payee_name, customer_name, amount):
    normalized_upi_id = str(upi_id or "").strip()
    if not re.fullmatch(r"[A-Za-z0-9._-]{2,256}@[A-Za-z0-9.-]{2,64}", normalized_upi_id):
        raise ValueError("व्यवसायाचा UPI ID वैध स्वरूपात कॉन्फिगर केलेला नाही.")
    try:
        normalized_amount = float(amount)
    except (TypeError, ValueError) as exc:
        raise ValueError("पेमेंट रक्कम वैध नाही.") from exc
    if not math.isfinite(normalized_amount) or normalized_amount <= 0:
        raise ValueError("बाकी रक्कम शून्यापेक्षा जास्त असणे आवश्यक आहे.")

    parameters = urllib.parse.urlencode(
        {
            "pa": normalized_upi_id,
            "pn": str(payee_name or "VernaLedger").strip(),
            "am": f"{normalized_amount:.2f}",
            "cu": "INR",
            "tn": f"Khata payment - {str(customer_name or '').strip()}"[:80],
        },
        quote_via=urllib.parse.quote,
    )
    return f"upi://pay?{parameters}"


def _normalize_khata_date(value, field_name):
    if isinstance(value, datetime):
        value = value.date()
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, str):
        try:
            return datetime.strptime(value.strip(), "%Y-%m-%d").date().isoformat()
        except ValueError as exc:
            raise ValueError(f"{field_name} YYYY-MM-DD स्वरूपात असणे आवश्यक आहे.") from exc
    raise ValueError(f"{field_name} वैध तारीख असणे आवश्यक आहे.")


def validate_khata_entry(customer_name, phone, amount, transaction_type, entry_date, due_date, notes):
    name = _khata_text(customer_name).strip()
    if not name:
        raise ValueError("कृपया ग्राहकाचे नाव भरा.")
    if len(name) > 100:
        raise ValueError("ग्राहकाचे नाव 100 अक्षरांपेक्षा मोठे असू शकत नाही.")

    phone_text = _khata_text(phone).strip()
    if phone_text and (
        not re.fullmatch(r"[0-9\s()+-]+", phone_text)
        or not re.fullmatch(r"[6-9]\d{9}", re.sub(r"[\s()+-]", "", phone_text))
    ):
        raise ValueError("फोन नंबर रिकामा ठेवा किंवा वैध 10 अंकी मोबाईल नंबर भरा.")
    normalized_phone = re.sub(r"[\s()+-]", "", phone_text)

    try:
        normalized_amount = float(amount)
    except (TypeError, ValueError) as exc:
        raise ValueError("रक्कम वैध संख्या असणे आवश्यक आहे.") from exc
    if not math.isfinite(normalized_amount) or normalized_amount <= 0:
        raise ValueError("रक्कम शून्यापेक्षा मोठी असणे आवश्यक आहे.")

    if transaction_type not in KHATA_TRANSACTION_TYPES:
        raise ValueError("व्यवहार प्रकार उपलब्ध पर्यायांपैकी निवडा.")

    normalized_notes = _khata_text(notes).strip()
    if len(normalized_notes) > 1000:
        raise ValueError("टीप 1000 अक्षरांपेक्षा मोठी असू शकत नाही.")

    return {
        "customer_name": name,
        "phone": normalized_phone,
        "amount": normalized_amount,
        "transaction_type": transaction_type,
        "date": _normalize_khata_date(entry_date, "व्यवहार तारीख"),
        "due_date": _normalize_khata_date(due_date, "परतफेड तारीख"),
        "notes": normalized_notes,
    }


def save_khata_transaction(customer_name, phone, amount, transaction_type, entry_date, due_date, notes):
    entry = validate_khata_entry(
        customer_name, phone, amount, transaction_type, entry_date, due_date, notes
    )
    with sqlite3.connect("ledger.db", timeout=10) as conn:
        cursor = conn.execute(
            """
            INSERT INTO customer_khata
                (customer_name, phone, amount, transaction_type, date, due_date, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                entry["customer_name"], entry["phone"], entry["amount"],
                entry["transaction_type"], entry["date"], entry["due_date"],
                entry["notes"],
            ),
        )
        return cursor.lastrowid


def load_khata_transactions():
    with sqlite3.connect("ledger.db", timeout=10) as conn:
        return pd.read_sql_query(
            "SELECT id, customer_name, phone, amount, transaction_type, date, due_date, notes "
            "FROM customer_khata ORDER BY id DESC",
            conn,
        )


def update_khata_transactions(original_df, edited_df):
    original_ids = {int(record_id) for record_id in original_df["id"].tolist()}
    updates = []
    for _, row in edited_df.iterrows():
        try:
            record_id = int(row["id"])
        except (TypeError, ValueError) as exc:
            raise ValueError("रेकॉर्ड आयडी बदलता येत नाही.") from exc
        if record_id not in original_ids:
            raise ValueError("नवीन किंवा अपरिचित रेकॉर्ड बदलता येत नाही.")
        original_row = original_df.loc[original_df["id"] == record_id].iloc[0]
        fields = ("customer_name", "phone", "amount", "transaction_type", "date", "due_date", "notes")
        if all(str(original_row[field] or "") == str(row[field] or "") for field in fields):
            continue
        entry = validate_khata_entry(
            row["customer_name"], row["phone"], row["amount"],
            row["transaction_type"], row["date"], row["due_date"], row["notes"],
        )
        updates.append((entry, record_id))

    if updates:
        with sqlite3.connect("ledger.db", timeout=10) as conn:
            conn.executemany(
                """
                UPDATE customer_khata
                SET customer_name = ?, phone = ?, amount = ?, transaction_type = ?,
                    date = ?, due_date = ?, notes = ?
                WHERE id = ?
                """,
                [
                    (
                        entry["customer_name"], entry["phone"], entry["amount"],
                        entry["transaction_type"], entry["date"], entry["due_date"],
                        entry["notes"], record_id,
                    )
                    for entry, record_id in updates
                ],
            )
    return len(updates)


def delete_khata_transaction(record_id):
    with sqlite3.connect("ledger.db", timeout=10) as conn:
        cursor = conn.execute("DELETE FROM customer_khata WHERE id = ?", (int(record_id),))
        return cursor.rowcount > 0


def build_khata_risk_report(khata_df):
    customers = {}
    today = date.today()
    for record in khata_df.to_dict("records"):
        name = _khata_text(record.get("customer_name")).strip()
        phone = _khata_text(record.get("phone")).strip()
        key = name.casefold()
        customer = customers.setdefault(
            key,
            {
                "customer_name": name,
                "phone": phone,
                "credit": 0.0,
                "payments": 0.0,
                "overdue_credit": 0.0,
            },
        )
        if not customer["phone"] and phone:
            customer["phone"] = phone
        try:
            amount = float(record.get("amount") or 0)
        except (TypeError, ValueError):
            continue
        if not math.isfinite(amount):
            continue
        if record.get("transaction_type") == KHATA_CREDIT:
            customer["credit"] += amount
            try:
                due_date = datetime.strptime(str(record.get("due_date")), "%Y-%m-%d").date()
            except (TypeError, ValueError):
                due_date = None
            if due_date and due_date < today:
                customer["overdue_credit"] += amount
        elif record.get("transaction_type") == KHATA_PAYMENT:
            customer["payments"] += amount

    report = []
    for customer in customers.values():
        balance = customer["credit"] - customer["payments"]
        overdue_balance = min(max(balance, 0.0), customer["overdue_credit"])
        risk_score = 0
        if balance > 0:
            risk_score = min(
                100,
                20 + min(int(balance / 100), 40) + (40 if overdue_balance > 0 else 0),
            )
        if risk_score >= 70:
            risk_level = "High Risk (बिकट उधारी)"
        elif risk_score >= 40:
            risk_level = "Moderate Risk"
        else:
            risk_level = "Safe Customer"
        report.append(
            {
                **customer,
                "balance": balance,
                "overdue_balance": overdue_balance,
                "risk_score": risk_score,
                "risk_level": risk_level,
            }
        )
    return pd.DataFrame(report)


def parse_voice_khata_details(transcript):
    if not API_KEY:
        raise ValueError("AI voice parsing साठी Gemini API key कॉन्फिगर केलेली नाही.")
    genai.configure(api_key=API_KEY)
    prompt = (
        "Extract a customer khata transaction from this Marathi, Hindi, or English transcript. "
        "Return only JSON with customer_name, phone (empty if absent), amount (number or null), "
        f"transaction_type (exactly {json.dumps(KHATA_CREDIT)} or {json.dumps(KHATA_PAYMENT)}), "
        f"and notes. Transcript: {json.dumps(transcript, ensure_ascii=False)}"
    )
    response = None
    last_error = None
    for model_name in get_active_gemini_models():
        try:
            model = genai.GenerativeModel(model_name)
            candidate_response = model.generate_content(prompt)
            if candidate_response and candidate_response.text:
                response = candidate_response
                break
            last_error = ValueError(f"{model_name} कडून रिकामा प्रतिसाद मिळाला.")
        except Exception as exc:
            last_error = exc
            ai_logger.warning(
                "Voice khata parsing failed with Gemini model %s (%s).",
                model_name,
                type(exc).__name__,
            )
    if not response:
        if last_error:
            raise RuntimeError(
                f"उपलब्ध Gemini मॉडेल्स वापरून व्हॉईस तपशील वाचता आले नाहीत: {last_error}"
            ) from last_error
        raise ValueError("Gemini API कडून कोणतेही उपलब्ध मॉडेल मिळाले नाही.")

    clean_response = re.sub(
        r"^```(?:json)?\s*|\s*```$", "", response.text.strip(), flags=re.IGNORECASE
    )
    parsed = json.loads(clean_response)
    if not isinstance(parsed, dict):
        raise ValueError("AI कडून मिळालेला व्यवहार तपशील योग्य स्वरूपात नाही.")
    amount = parsed.get("amount")
    try:
        amount = float(amount) if amount is not None else 0.0
    except (TypeError, ValueError):
        amount = 0.0
    if not math.isfinite(amount) or amount < 0:
        amount = 0.0
    transaction_type = parsed.get("transaction_type")
    if transaction_type not in KHATA_TRANSACTION_TYPES:
        transaction_type = KHATA_CREDIT
    phone = parsed.get("phone")
    return {
        "customer_name": str(parsed.get("customer_name") or "").strip(),
        "phone": str(phone or "").strip(),
        "amount": amount,
        "transaction_type": transaction_type,
        "notes": str(parsed.get("notes") or transcript).strip(),
    }


def render_business_module_styles():
    st.markdown("""
    <style>

    /* --- SAFE FONT APPLICATION --- */
    .stApp {{
        font-family: 'Plus Jakarta Sans', 'Mukta', 'Hind', 'Baloo 2', sans-serif;
    }}
    h1, h2, h3, h4, h5, h6, p, li, label, .stMarkdown {{
        font-family: 'Plus Jakarta Sans', 'Mukta', 'Hind', 'Baloo 2', sans-serif;
    }}
    /* Protect all Streamlit default icons and SVG from font overrides */
    svg, svg * {{
        font-family: inherit; 
    }}
    .material-symbols-rounded, .material-symbols-outlined, .material-icons, [class*="icon"] {{
        font-family: 'Material Symbols Rounded', 'Material Symbols Outlined', 'Material Icons' !important;
    }}
    /* --- END SAFE FONT --- */
    

    [data-testid="stMain"]:has(.business-suite-page) .studio-header {
        position: relative;
        overflow: hidden;
        min-height: 126px;
        align-items: center;
        padding: 22px 26px;
        margin-bottom: 15px;
        border: 1px solid rgba(125, 211, 252, 0.24) !important;
        border-radius: 26px !important;
        background:
            radial-gradient(circle at 88% 16%, rgba(34, 211, 238, 0.2), transparent 28%),
            radial-gradient(circle at 73% 110%, rgba(99, 102, 241, 0.2), transparent 35%),
            linear-gradient(120deg, rgba(8, 18, 37, 0.98), rgba(14, 31, 55, 0.94) 58%, rgba(12, 27, 49, 0.96)) !important;
        box-shadow: 0 20px 54px rgba(0, 0, 0, 0.28), inset 0 1px 0 rgba(255, 255, 255, 0.08) !important;
    }
    [data-testid="stMain"]:has(.business-suite-page) .studio-header::after {
        content: "";
        position: absolute;
        width: 180px;
        height: 180px;
        right: 5%;
        top: -82px;
        border: 1px solid rgba(125, 211, 252, 0.13);
        border-radius: 50%;
        box-shadow: 0 0 0 20px rgba(125, 211, 252, 0.025), 0 0 0 42px rgba(125, 211, 252, 0.02);
        pointer-events: none;
    }
    [data-testid="stMain"]:has(.business-suite-page) .studio-header:hover {
        transform: none !important;
        border-color: rgba(103, 232, 249, 0.42) !important;
        box-shadow: 0 22px 58px rgba(0, 0, 0, 0.34), 0 0 34px rgba(34, 211, 238, 0.08) !important;
    }
    .business-hero-content {
        position: relative;
        z-index: 1;
        max-width: 760px;
    }
    .business-eyebrow {
        display: inline-flex;
        align-items: center;
        gap: 7px;
        margin-bottom: 10px;
        padding: 5px 10px;
        color: #a5f3fc;
        background: rgba(34, 211, 238, 0.09);
        border: 1px solid rgba(103, 232, 249, 0.2);
        border-radius: 999px;
        font-size: 10px;
        font-weight: 800;
        letter-spacing: 1.25px;
        text-transform: uppercase;
    }
    .business-hero-title {
        margin: 0 !important;
        color: #f8fafc !important;
        font-size: clamp(25px, 3.2vw, 36px) !important;
        font-weight: 800 !important;
        letter-spacing: -1.1px;
        line-height: 1.16 !important;
    }
    .business-hero-title span {
        color: #67e8f9;
    }
    .business-hero-subtitle {
        margin: 9px 0 0 !important;
        color: #a8b8ce !important;
        font-size: 13px !important;
        line-height: 1.65 !important;
    }
    .business-hero-mark {
        position: relative;
        z-index: 1;
        display: grid;
        flex: 0 0 72px;
        width: 72px;
        height: 72px;
        place-items: center;
        margin-left: 20px;
        color: #a5f3fc;
        background: linear-gradient(145deg, rgba(34, 211, 238, 0.19), rgba(99, 102, 241, 0.14));
        border: 1px solid rgba(103, 232, 249, 0.25);
        border-radius: 23px;
        box-shadow: inset 0 1px 0 rgba(255,255,255,0.1), 0 14px 30px rgba(2, 6, 23, 0.28);
        font-size: 32px;
    }
    [data-testid="stMain"]:has(.business-suite-page) [role="tablist"] {
        margin-top: 4px;
        gap: 8px;
        padding: 7px;
        background: rgba(7, 15, 30, 0.7);
        border: 1px solid rgba(148, 163, 184, 0.13);
        border-radius: 17px;
    }
    [data-testid="stMain"]:has(.business-suite-page) [role="tab"] {
        min-height: 43px;
        padding: 9px 15px;
        color: #9aabc2;
        border: 1px solid transparent;
        border-radius: 12px;
        font-size: 12px;
        font-weight: 700;
        transition: color 0.18s ease, background 0.18s ease, border-color 0.18s ease;
    }
    [data-testid="stMain"]:has(.business-suite-page) [role="tab"]:hover {
        color: #e2faff;
        background: rgba(34, 211, 238, 0.07);
    }
    [data-testid="stMain"]:has(.business-suite-page) [role="tab"][aria-selected="true"] {
        color: #d9fbff;
        background: linear-gradient(135deg, rgba(8, 145, 178, 0.22), rgba(59, 130, 246, 0.16));
        border-color: rgba(103, 232, 249, 0.25);
        box-shadow: inset 0 1px 0 rgba(255,255,255,0.06);
    }
    [data-testid="stMain"]:has(.business-suite-page) .panel-card {
        box-sizing: border-box;
        padding: clamp(13px, 1.4vw, 18px) !important;
        margin-bottom: 13px !important;
        background: linear-gradient(145deg, rgba(11, 20, 37, 0.94), rgba(12, 23, 41, 0.88)) !important;
        border: 1px solid rgba(148, 163, 184, 0.15) !important;
        border-radius: 20px !important;
        box-shadow: 0 14px 34px rgba(0, 0, 0, 0.2), inset 0 1px 0 rgba(255,255,255,0.035) !important;
    }
    [data-testid="stMain"]:has(.business-suite-page) .panel-card:hover {
        transform: none !important;
        border-color: rgba(103, 232, 249, 0.26) !important;
        box-shadow: 0 18px 38px rgba(0, 0, 0, 0.24) !important;
    }
    .business-section-heading {
        display: flex;
        align-items: center;
        gap: 11px;
        margin: 8px 0 16px;
    }
    .business-section-icon {
        display: grid;
        flex: 0 0 38px;
        width: 38px;
        height: 38px;
        place-items: center;
        color: #a5f3fc;
        background: rgba(34, 211, 238, 0.1);
        border: 1px solid rgba(103, 232, 249, 0.17);
        border-radius: 12px;
        font-size: 18px;
    }
    .business-section-title {
        margin: 0;
        color: #edf6ff;
        font-size: 16px;
        font-weight: 800;
        letter-spacing: -0.2px;
    }
    .business-section-caption {
        margin: 3px 0 0;
        color: #8294ad;
        font-size: 11px;
    }
    .business-metric-card {
        min-height: 104px;
        padding: 16px 17px;
        background: linear-gradient(145deg, rgba(16, 30, 51, 0.92), rgba(10, 20, 37, 0.9));
        border: 1px solid rgba(148, 163, 184, 0.14);
        border-radius: 17px;
        box-shadow: inset 0 1px 0 rgba(255,255,255,0.035);
    }
    .business-metric-label {
        color: #90a2ba;
        font-size: 10px;
        font-weight: 800;
        letter-spacing: 0.75px;
        text-transform: uppercase;
    }
    .business-metric-value {
        margin-top: 9px;
        color: #f3f8ff;
        font-size: 23px;
        font-weight: 800;
        line-height: 1.1;
        letter-spacing: -0.6px;
    }
    .business-metric-note {
        margin-top: 5px;
        color: #73869f;
        font-size: 10px;
    }
    [data-testid="stMain"]:has(.business-suite-page) [data-testid="stForm"] {
        padding: 13px;
        background: rgba(5, 13, 27, 0.42);
        border: 1px solid rgba(148, 163, 184, 0.11);
        border-radius: 16px;
    }
    [data-testid="stMain"]:has(.business-suite-page) [data-testid="stDataFrame"],
    [data-testid="stMain"]:has(.business-suite-page) [data-testid="stDataEditor"] {
        overflow: hidden;
        border: 1px solid rgba(148, 163, 184, 0.14);
        border-radius: 14px;
    }
    [data-testid="stMain"]:has(.business-suite-page) [data-testid="stAlert"] {
        border-radius: 14px;
    }
    @media (max-width: 720px) {
        [data-testid="stMain"]:has(.business-suite-page) .studio-header {
            min-height: 0;
            padding: 18px 16px;
            border-radius: 21px !important;
        }
        .business-hero-mark {
            flex-basis: 52px;
            width: 52px;
            height: 52px;
            margin-left: 10px;
            border-radius: 16px;
            font-size: 24px;
        }
        .business-hero-subtitle {
            max-width: 92%;
            font-size: 12px !important;
        }
        [data-testid="stMain"]:has(.business-suite-page) [role="tablist"] {
            gap: 4px;
            padding: 5px;
        }
        [data-testid="stMain"]:has(.business-suite-page) [role="tab"] {
            padding: 8px 10px;
            font-size: 11px;
        }
        [data-testid="stMain"]:has(.business-suite-page) [data-testid="stForm"] {
            padding: 13px;
        }
    }
    </style>
    <div class="business-suite-page" aria-hidden="true"></div>
    """, unsafe_allow_html=True)


def render_rag_sidebar_design_styles():
    _streamlit_ui.markdown("""
    <style>

    /* --- SAFE FONT APPLICATION --- */
    .stApp {{
        font-family: 'Plus Jakarta Sans', 'Mukta', 'Hind', 'Baloo 2', sans-serif;
    }}
    h1, h2, h3, h4, h5, h6, p, li, label, .stMarkdown {{
        font-family: 'Plus Jakarta Sans', 'Mukta', 'Hind', 'Baloo 2', sans-serif;
    }}
    /* Protect all Streamlit default icons and SVG from font overrides */
    svg, svg * {{
        font-family: inherit; 
    }}
    .material-symbols-rounded, .material-symbols-outlined, .material-icons, [class*="icon"] {{
        font-family: 'Material Symbols Rounded', 'Material Symbols Outlined', 'Material Icons' !important;
    }}
    /* --- END SAFE FONT --- */
    

    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0c1728 0%, #09111f 100%) !important;
        border-right: 1px solid rgba(148, 163, 184, 0.13) !important;
        box-shadow: 12px 0 36px rgba(0, 0, 0, 0.22) !important;
        box-sizing: border-box !important;
        width: 18.75rem !important;
        min-width: 18.75rem !important;
        max-width: 18.75rem !important;
        flex: 0 0 18.75rem !important;
        resize: none !important;
    }
    [data-testid="stSidebarResizer"] {
        display: none !important;
        pointer-events: none !important;
    }
    [data-testid="stSidebar"] > div:first-child {
        height: 100dvh !important;
        overflow: hidden !important;
        padding: 6px 10px !important;
    }
    section[data-testid="stSidebar"][aria-expanded="false"] {
        width: 0 !important;
        min-width: 0 !important;
        max-width: 0 !important;
        flex: 0 0 0 !important;
        overflow: hidden !important;
    }
    [data-testid="stSidebarContent"] {
        height: 100% !important;
        padding: 0.2rem 0.4rem 0.5rem !important;
        overflow-x: hidden !important;
        overflow-y: auto !important;
        overscroll-behavior: contain;
        scrollbar-width: thin;
        scrollbar-color: rgba(56, 189, 248, 0.38) transparent;
    }
    [data-testid="stSidebarUserContent"] {
        box-sizing: border-box !important;
        min-height: 0 !important;
        max-height: calc(100dvh - 5.25rem) !important;
        padding: 0.3rem 0.15rem 0.5rem !important;
        overflow-x: hidden !important;
        overflow-y: auto !important;
        overscroll-behavior: contain;
        scrollbar-width: thin;
        scrollbar-color: rgba(56, 189, 248, 0.38) transparent;
    }
    [data-testid="stSidebarUserContent"] [data-testid="stVerticalBlock"] {
        gap: 0.45rem !important;
    }
    [data-testid="stSidebarUserContent"] [data-testid="stMarkdownContainer"]:has(.sidebar-role-badge),
    [data-testid="stSidebarUserContent"] [data-testid="stMarkdownContainer"]:has(.sidebar-title),
    [data-testid="stSidebarUserContent"] [data-testid="stMarkdownContainer"]:has(.dev-credit-box) {
        margin-bottom: 0 !important;
    }
    section[data-testid="stSidebar"] .sidebar-role-badge {
        box-sizing: border-box !important;
        display: flex !important;
        min-height: 25px !important;
        width: 100% !important;
        align-items: center !important;
        justify-content: center !important;
        margin: 15px 0 0 !important;
        padding: 4px 8px !important;
        border-radius: 8px !important;
        line-height: 1.25 !important;
    }
    section[data-testid="stSidebar"] .sidebar-role-badge span {
        font-size: 9px !important;
    }
    section[data-testid="stSidebar"] .sidebar-brand {
        margin-bottom: 1px !important;
        padding: 0 !important;
        gap: 8px !important;
    }
    section[data-testid="stSidebar"] .sidebar-title {
        box-sizing: border-box !important;
        margin: 4px 0 7px 3px !important;
        font-size: 9px !important;
        letter-spacing: 1px !important;
        line-height: 1.4 !important;
        overflow-wrap: anywhere;
    }
    section[data-testid="stSidebar"] div[role="radiogroup"] {
        display: flex !important;
        flex-direction: column !important;
        gap: 7px !important;
    }
    section[data-testid="stSidebar"] div[role="radiogroup"] > label {
        box-sizing: border-box !important;
        display: flex !important;
        min-height: 40px !important;
        align-items: center !important;
        gap: 10px !important;
        padding: 8px 11px !important;
        margin: 0 !important;
        background: linear-gradient(115deg, rgba(14, 165, 233, 0.09), rgba(37, 99, 235, 0.07)) !important;
        border: 1px solid rgba(56, 189, 248, 0.2) !important;
        border-radius: 12px !important;
        box-shadow: 0 4px 14px rgba(2, 8, 23, 0.16), inset 0 1px rgba(255, 255, 255, 0.025) !important;
        transition: background 180ms ease, border-color 180ms ease, box-shadow 180ms ease, color 180ms ease !important;
        transform: none !important;
    }
    section[data-testid="stSidebar"] div[role="radiogroup"] label input[type="radio"] {
        accent-color: #22d3ee !important;
        flex: 0 0 auto !important;
        width: 15px !important;
        height: 15px !important;
        margin: 0 !important;
    }
    section[data-testid="stSidebar"] div[role="radiogroup"] label p {
        color: #dceafa !important;
        font-size: 11.5px !important;
        font-weight: 650 !important;
        letter-spacing: 0.01em !important;
        line-height: 1.35 !important;
        margin: 0 !important;
        overflow-wrap: anywhere;
    }
    section[data-testid="stSidebar"] div[role="radiogroup"] > label:hover {
        background: linear-gradient(115deg, rgba(14, 165, 233, 0.2), rgba(99, 102, 241, 0.16)) !important;
        border-color: rgba(103, 232, 249, 0.75) !important;
        box-shadow: 0 0 0 1px rgba(34, 211, 238, 0.14), 0 0 20px rgba(34, 211, 238, 0.2), inset 0 1px rgba(255, 255, 255, 0.07) !important;
        color: #f0fdff !important;
        transform: translateY(-1px) !important;
    }
    section[data-testid="stSidebar"] div[role="radiogroup"] > label:has(input:checked) {
        background: linear-gradient(115deg, rgba(14, 165, 233, 0.24), rgba(79, 70, 229, 0.2)) !important;
        border-color: rgba(103, 232, 249, 0.82) !important;
        box-shadow: inset 3px 0 #22d3ee, 0 0 0 1px rgba(34, 211, 238, 0.1), 0 0 18px rgba(34, 211, 238, 0.17) !important;
    }
    section[data-testid="stSidebar"] div[role="radiogroup"] > label:focus-within {
        outline: 2px solid rgba(103, 232, 249, 0.72) !important;
        outline-offset: 2px !important;
    }
    section[data-testid="stSidebar"] [data-testid="stToggle"],
    section[data-testid="stSidebar"] [data-testid="stCheckbox"] {
        margin: 0 !important;
        box-sizing: border-box !important;
        min-width: 0 !important;
    }
    section[data-testid="stSidebar"] [data-testid="stToggle"] label,
    section[data-testid="stSidebar"] [data-testid="stCheckbox"] label {
        box-sizing: border-box !important;
        display: flex !important;
        width: 100% !important;
        min-height: 30px !important;
        align-items: center !important;
        gap: 8px !important;
        margin: 0 !important;
        padding: 2px 0 !important;
    }
    section[data-testid="stSidebar"] [data-testid="stToggle"] label p,
    section[data-testid="stSidebar"] [data-testid="stCheckbox"] label p {
        font-size: 11px !important;
        font-weight: 700 !important;
        line-height: 1.3 !important;
        margin: 0 !important;
        overflow-wrap: anywhere;
    }
    section[data-testid="stSidebar"] [data-testid="stSelectbox"] [data-baseweb="select"] > div {
        min-height: 34px !important;
        border-color: rgba(56, 189, 248, 0.24) !important;
        border-radius: 10px !important;
    }
    section[data-testid="stSidebar"] .dev-credit-box {
        box-sizing: border-box !important;
        width: 100% !important;
        padding: 7px 9px !important;
        margin: 4px 0 2px !important;
        border-radius: 10px !important;
        line-height: 1.35 !important;
    }
    section[data-testid="stSidebar"] .stButton > button {
        min-height: 34px !important;
        padding: 6px 9px !important;
    }
    @media (max-width: 900px) {
        section[data-testid="stSidebar"][aria-expanded="true"] {
            width: min(18rem, 82vw) !important;
            max-width: min(18rem, 82vw) !important;
            min-width: min(18rem, 82vw) !important;
            flex-basis: min(18rem, 82vw) !important;
        }
    }
    </style>
    """, unsafe_allow_html=True)


def render_application_design_styles():
    lang = st.session_state.get("ui_language", "mr")
    font_css = ""
    if lang == "mr":
        font_css = """
        @import url('https://fonts.googleapis.com/css2?family=Baloo+2:wght@400;500;600;700;800&family=Hind:wght@400;500;600;700&display=swap');
        
        
        
        
        """

    st.markdown("""
    <style>

    /* --- SAFE FONT APPLICATION --- */
    .stApp {{
        font-family: 'Plus Jakarta Sans', 'Mukta', 'Hind', 'Baloo 2', sans-serif;
    }}
    h1, h2, h3, h4, h5, h6, p, li, label, .stMarkdown {{
        font-family: 'Plus Jakarta Sans', 'Mukta', 'Hind', 'Baloo 2', sans-serif;
    }}
    /* Protect all Streamlit default icons and SVG from font overrides */
    svg, svg * {{
        font-family: inherit; 
    }}
    .material-symbols-rounded, .material-symbols-outlined, .material-icons, [class*="icon"] {{
        font-family: 'Material Symbols Rounded', 'Material Symbols Outlined', 'Material Icons' !important;
    }}
    /* --- END SAFE FONT --- */
    

    """ + font_css + """
    body:has(.app-ui-polish-scope) .stApp, .block-container {
        background-color: #08111f !important;
        background-image:
            radial-gradient(ellipse at 8% 0%, rgba(14, 165, 233, 0.12), transparent 38%),
            radial-gradient(ellipse at 100% 18%, rgba(99, 102, 241, 0.11), transparent 34%),
            linear-gradient(145deg, #08111f 0%, #0b1424 54%, #0a1020 100%) !important;
        color: #e7eef8 !important;
    }
    body:has(.app-ui-polish-scope) [data-testid="stHeader"] {
        background: rgba(8, 17, 31, 0.84) !important;
        border-bottom-color: rgba(148, 163, 184, 0.12) !important;
    }
    body:has(.app-ui-polish-scope) [data-testid="stMainBlockContainer"] {
        box-sizing: border-box !important;
        width: 100% !important;
        max-width: 1680px !important;
        margin: 0 auto !important;
        padding: clamp(0.45rem, 0.9vw, 0.8rem) clamp(0.75rem, 2vw, 1.75rem) 1.1rem !important;
    }
    body:has(section[data-testid="stSidebar"][aria-expanded="false"]) [data-testid="stMainBlockContainer"] {
        max-width: none !important;
        width: 100% !important;
    }
    body:has(.app-ui-polish-scope) section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0c1728 0%, #09111f 100%) !important;
        border-right: 1px solid rgba(148, 163, 184, 0.13) !important;
        box-shadow: 12px 0 36px rgba(0, 0, 0, 0.22) !important;
        box-sizing: border-box !important;
        width: 18.75rem !important;
        min-width: 18.75rem !important;
        max-width: 18.75rem !important;
        flex: 0 0 18.75rem !important;
        resize: none !important;
    }
    body:has(.app-ui-polish-scope) [data-testid="stSidebarResizer"] {
        display: none !important;
        pointer-events: none !important;
    }
    body:has(.app-ui-polish-scope) [data-testid="stSidebar"] > div:first-child {
        padding: 6px 10px !important;
        height: 100dvh !important;
        overflow: hidden !important;
    }
    body:has(.app-ui-polish-scope) section[data-testid="stSidebar"][aria-expanded="false"] {
        width: 0 !important;
        min-width: 0 !important;
        max-width: 0 !important;
        flex: 0 0 0 !important;
        overflow: hidden !important;
    }
    body:has(.app-ui-polish-scope) [data-testid="stSidebarContent"] {
        height: 100% !important;
        padding: 0.2rem 0.4rem 0.5rem !important;
        overflow-x: hidden !important;
        overflow-y: auto !important;
        overscroll-behavior: contain;
        scrollbar-width: thin;
        scrollbar-color: rgba(56, 189, 248, 0.38) transparent;
    }
    body:has(.app-ui-polish-scope) [data-testid="stSidebarUserContent"] {
        box-sizing: border-box !important;
        min-height: 0 !important;
        max-height: calc(100dvh - 5.25rem) !important;
        padding: 0.3rem 0.15rem 0.5rem !important;
        overflow-x: hidden !important;
        overflow-y: auto !important;
        overscroll-behavior: contain;
        scrollbar-width: thin;
        scrollbar-color: rgba(56, 189, 248, 0.38) transparent;
    }
    body:has(.app-ui-polish-scope) [data-testid="stSidebarUserContent"] [data-testid="stVerticalBlock"] {
        gap: 0.45rem !important;
    }
    body:has(.app-ui-polish-scope) [data-testid="stSidebarUserContent"] [data-testid="stMarkdownContainer"]:has(.sidebar-role-badge),
    body:has(.app-ui-polish-scope) [data-testid="stSidebarUserContent"] [data-testid="stMarkdownContainer"]:has(.sidebar-title),
    body:has(.app-ui-polish-scope) [data-testid="stSidebarUserContent"] [data-testid="stMarkdownContainer"]:has(.dev-credit-box) {
        margin-bottom: 0 !important;
    }
    body:has(.app-ui-polish-scope) section[data-testid="stSidebar"] .sidebar-role-badge {
        box-sizing: border-box !important;
        display: flex !important;
        min-height: 25px !important;
        width: 100% !important;
        align-items: center !important;
        justify-content: center !important;
        margin: 15px 0 0 !important;
        padding: 4px 8px !important;
        border-radius: 8px !important;
        line-height: 1.25 !important;
    }
    body:has(.app-ui-polish-scope) section[data-testid="stSidebar"] .sidebar-role-badge span {
        font-size: 9px !important;
    }
    body:has(.app-ui-polish-scope) section[data-testid="stSidebar"] .sidebar-brand {
        margin-bottom: 1px !important;
        padding: 0 !important;
        gap: 8px !important;
    }
    body:has(.app-ui-polish-scope) .sidebar-title {
        color: #91a9c7 !important;
        box-sizing: border-box !important;
        margin: 4px 0 7px 3px !important;
        font-size: 9px !important;
        letter-spacing: 1px !important;
        line-height: 1.4 !important;
        overflow-wrap: anywhere;
    }
    body:has(.app-ui-polish-scope) section[data-testid="stSidebar"] div[role="radiogroup"] {
        display: flex !important;
        flex-direction: column !important;
        gap: 7px !important;
    }
    body:has(.app-ui-polish-scope) section[data-testid="stSidebar"] div[role="radiogroup"] > label {
        box-sizing: border-box !important;
        display: flex !important;
        min-height: 40px !important;
        align-items: center !important;
        gap: 10px !important;
        padding: 8px 11px !important;
        margin: 0 !important;
        background: linear-gradient(115deg, rgba(14, 165, 233, 0.09), rgba(37, 99, 235, 0.07)) !important;
        border: 1px solid rgba(56, 189, 248, 0.2) !important;
        border-radius: 12px !important;
        box-shadow: 0 4px 14px rgba(2, 8, 23, 0.16), inset 0 1px rgba(255, 255, 255, 0.025) !important;
        transition: background 180ms ease, border-color 180ms ease, box-shadow 180ms ease, color 180ms ease !important;
        transform: none !important;
    }
    body:has(.app-ui-polish-scope) section[data-testid="stSidebar"] div[role="radiogroup"] > label:hover {
        background: linear-gradient(115deg, rgba(14, 165, 233, 0.2), rgba(99, 102, 241, 0.16)) !important;
        border-color: rgba(103, 232, 249, 0.75) !important;
        box-shadow: 0 0 0 1px rgba(34, 211, 238, 0.14), 0 0 20px rgba(34, 211, 238, 0.2), inset 0 1px rgba(255, 255, 255, 0.07) !important;
        color: #f0fdff !important;
        transform: translateY(-1px) !important;
    }
    body:has(.app-ui-polish-scope) section[data-testid="stSidebar"] div[role="radiogroup"] > label:has(input:checked) {
        background: linear-gradient(115deg, rgba(14, 165, 233, 0.24), rgba(79, 70, 229, 0.2)) !important;
        border-color: rgba(103, 232, 249, 0.82) !important;
        box-shadow: inset 3px 0 #22d3ee, 0 0 0 1px rgba(34, 211, 238, 0.1), 0 0 18px rgba(34, 211, 238, 0.17) !important;
    }
    body:has(.app-ui-polish-scope) section[data-testid="stSidebar"] div[role="radiogroup"] > label:focus-within {
        outline: 2px solid rgba(103, 232, 249, 0.72) !important;
        outline-offset: 2px !important;
    }
    body:has(.app-ui-polish-scope) section[data-testid="stSidebar"] div[role="radiogroup"] label input[type="radio"] {
        accent-color: #22d3ee !important;
        flex: 0 0 auto !important;
        width: 15px !important;
        height: 15px !important;
        margin: 0 !important;
    }
    body:has(.app-ui-polish-scope) section[data-testid="stSidebar"] div[role="radiogroup"] label p {
        color: #dceafa !important;
        font-size: 11.5px !important;
        font-weight: 650 !important;
        letter-spacing: 0.01em !important;
        line-height: 1.35 !important;
        margin: 0 !important;
        overflow-wrap: anywhere;
    }
    body:has(.app-ui-polish-scope) section[data-testid="stSidebar"] [data-testid="stToggle"],
    body:has(.app-ui-polish-scope) section[data-testid="stSidebar"] [data-testid="stCheckbox"] {
        margin: 0 !important;
        box-sizing: border-box !important;
        min-width: 0 !important;
    }
    body:has(.app-ui-polish-scope) section[data-testid="stSidebar"] [data-testid="stToggle"] label,
    body:has(.app-ui-polish-scope) section[data-testid="stSidebar"] [data-testid="stCheckbox"] label {
        box-sizing: border-box !important;
        display: flex !important;
        width: 100% !important;
        min-height: 30px !important;
        align-items: center !important;
        gap: 8px !important;
        margin: 0 !important;
        padding: 2px 0 !important;
    }
    body:has(.app-ui-polish-scope) section[data-testid="stSidebar"] [data-testid="stToggle"] label p,
    body:has(.app-ui-polish-scope) section[data-testid="stSidebar"] [data-testid="stCheckbox"] label p {
        font-size: 11px !important;
        font-weight: 700 !important;
        line-height: 1.3 !important;
        margin: 0 !important;
        overflow-wrap: anywhere;
    }
    body:has(.app-ui-polish-scope) section[data-testid="stSidebar"] [data-testid="stSelectbox"] [data-baseweb="select"] > div {
        min-height: 34px !important;
        border-color: rgba(56, 189, 248, 0.24) !important;
        border-radius: 10px !important;
    }
    body:has(.app-ui-polish-scope) .dev-credit-box {
        background: rgba(15, 29, 48, 0.78) !important;
        border-color: rgba(148, 163, 184, 0.14) !important;
        border-radius: 10px !important;
        box-sizing: border-box !important;
        width: 100% !important;
        padding: 7px 9px !important;
        margin: 4px 0 2px !important;
        line-height: 1.35 !important;
    }
    body:has(.app-ui-polish-scope) section[data-testid="stSidebar"] .stButton > button {
        min-height: 34px !important;
        padding: 6px 9px !important;
    }
    body:has(.app-ui-polish-scope) .studio-header {
        position: relative;
        overflow: hidden;
        min-height: 118px;
        padding: clamp(16px, 2vw, 25px) !important;
        margin-bottom: 15px !important;
        background:
            radial-gradient(circle at 88% 10%, rgba(56, 189, 248, 0.15), transparent 32%),
            linear-gradient(125deg, rgba(16, 31, 51, 0.96), rgba(12, 23, 40, 0.92)) !important;
        border: 1px solid rgba(148, 163, 184, 0.17) !important;
        border-radius: 22px !important;
        box-shadow: 0 18px 44px rgba(0, 0, 0, 0.2), inset 0 1px rgba(255, 255, 255, 0.045) !important;
        transform: none !important;
    }
    body:has(.app-ui-polish-scope) .studio-header:hover {
        border-color: rgba(56, 189, 248, 0.3) !important;
        box-shadow: 0 18px 44px rgba(0, 0, 0, 0.22), inset 0 1px rgba(255, 255, 255, 0.05) !important;
    }
    body:has(.app-ui-polish-scope) .studio-header h2 {
        color: #e9f4ff !important;
        font-size: clamp(20px, 2.2vw, 28px) !important;
        line-height: 1.25 !important;
        letter-spacing: -0.035em !important;
    }
    body:has(.app-ui-polish-scope) .studio-header p {
        color: #9bb0c9 !important;
        font-size: clamp(12px, 1.15vw, 14px) !important;
        line-height: 1.6 !important;
    }
    body:has(.app-ui-polish-scope) .panel-card {
        box-sizing: border-box !important;
        padding: clamp(13px, 1.4vw, 18px) !important;
        margin-bottom: 13px !important;
        background: linear-gradient(145deg, rgba(15, 28, 46, 0.94), rgba(12, 23, 39, 0.94)) !important;
        border: 1px solid rgba(148, 163, 184, 0.15) !important;
        border-radius: 18px !important;
        box-shadow: 0 14px 34px rgba(0, 0, 0, 0.19), inset 0 1px rgba(255, 255, 255, 0.035) !important;
        transform: none !important;
    }
    body:has(.app-ui-polish-scope) .panel-card:hover {
        border-color: rgba(56, 189, 248, 0.24) !important;
        box-shadow: 0 16px 38px rgba(0, 0, 0, 0.23) !important;
        transform: none !important;
    }
    body:has(.app-ui-polish-scope) h1,
    body:has(.app-ui-polish-scope) h2,
    body:has(.app-ui-polish-scope) h3,
    body:has(.app-ui-polish-scope) h4 {
        letter-spacing: -0.025em;
    }
    body:has(.app-ui-polish-scope) [data-testid="stMarkdownContainer"] h4 {
        color: #dceaf9 !important;
        font-size: 16px !important;
        margin-bottom: 14px !important;
    }
    body:has(.app-ui-polish-scope) [data-testid="stTabs"] [role="tablist"] {
        gap: 6px !important;
        padding: 6px !important;
        background: rgba(10, 20, 35, 0.74) !important;
        border: 1px solid rgba(148, 163, 184, 0.14) !important;
        border-radius: 15px !important;
    }
    body:has(.app-ui-polish-scope) [data-testid="stTabs"] [role="tab"] {
        min-height: 42px !important;
        padding: 9px 14px !important;
        color: #9fb2c9 !important;
        border: 1px solid transparent !important;
        border-radius: 10px !important;
        font-size: 12px !important;
        font-weight: 700 !important;
    }
    body:has(.app-ui-polish-scope) [data-testid="stTabs"] [role="tab"][aria-selected="true"] {
        color: #e5f6ff !important;
        background: linear-gradient(120deg, rgba(14, 165, 233, 0.2), rgba(59, 130, 246, 0.13)) !important;
        border-color: rgba(56, 189, 248, 0.25) !important;
        box-shadow: inset 0 1px rgba(255, 255, 255, 0.06) !important;
    }
    body:has(.app-ui-polish-scope) [data-testid="stTextInput"] input,
    body:has(.app-ui-polish-scope) [data-testid="stNumberInput"] input,
    body:has(.app-ui-polish-scope) [data-testid="stDateInput"] input,
    body:has(.app-ui-polish-scope) [data-testid="stTextArea"] textarea,
    body:has(.app-ui-polish-scope) [data-baseweb="select"] > div {
        min-height: 42px;
        color: #e7eef8 !important;
        background: rgba(7, 16, 29, 0.78) !important;
        border-color: rgba(148, 163, 184, 0.2) !important;
        border-radius: 11px !important;
    }
    body:has(.app-ui-polish-scope) [data-testid="stTextInput"] input:focus,
    body:has(.app-ui-polish-scope) [data-testid="stNumberInput"] input:focus,
    body:has(.app-ui-polish-scope) [data-testid="stDateInput"] input:focus,
    body:has(.app-ui-polish-scope) [data-testid="stTextArea"] textarea:focus {
        border-color: rgba(56, 189, 248, 0.72) !important;
        box-shadow: 0 0 0 3px rgba(14, 165, 233, 0.13) !important;
    }
    body:has(.app-ui-polish-scope) [data-testid="stWidgetLabel"] p,
    body:has(.app-ui-polish-scope) [data-testid="stMarkdownContainer"] p {
        line-height: 1.55;
    }
    body:has(.app-ui-polish-scope) .stButton > button,
    body:has(.app-ui-polish-scope) .stDownloadButton > button,
    body:has(.app-ui-polish-scope) [data-testid="stFormSubmitButton"] > button {
        min-height: 43px !important;
        padding: 10px 16px !important;
        border-radius: 11px !important;
        box-shadow: 0 6px 16px rgba(2, 8, 23, 0.23) !important;
        transition: background 0.18s ease, border-color 0.18s ease, box-shadow 0.18s ease !important;
        transform: none !important;
    }
    body:has(.app-ui-polish-scope) .stButton > button[kind="primary"],
    body:has(.app-ui-polish-scope) [data-testid="stFormSubmitButton"] > button {
        background: linear-gradient(115deg, #0284c7, #2563eb) !important;
        border: 1px solid rgba(125, 211, 252, 0.28) !important;
        color: #f8fbff !important;
    }
    body:has(.app-ui-polish-scope) .stButton > button:hover,
    body:has(.app-ui-polish-scope) .stDownloadButton > button:hover,
    body:has(.app-ui-polish-scope) [data-testid="stFormSubmitButton"] > button:hover {
        border-color: rgba(125, 211, 252, 0.58) !important;
        box-shadow: 0 8px 20px rgba(2, 8, 23, 0.29) !important;
        transform: translateY(-1px) !important;
    }
    body:has(.app-ui-polish-scope) [data-testid="stMetric"] {
        padding: 15px 16px;
        background: rgba(10, 21, 37, 0.74);
        border: 1px solid rgba(148, 163, 184, 0.14);
        border-radius: 14px;
    }
    body:has(.app-ui-polish-scope) [data-testid="stDataFrame"],
    body:has(.app-ui-polish-scope) [data-testid="stDataEditor"] {
        overflow: hidden;
        border: 1px solid rgba(148, 163, 184, 0.16);
        border-radius: 14px;
        background: rgba(10, 19, 33, 0.65);
    }
    body:has(.app-ui-polish-scope) [data-testid="stFileUploader"],
    body:has(.app-ui-polish-scope) [data-testid="stCameraInput"] {
        background: rgba(9, 19, 33, 0.65) !important;
        border: 1px dashed rgba(56, 189, 248, 0.42) !important;
        border-radius: 15px !important;
        box-shadow: none !important;
        transform: none !important;
    }
    body:has(.app-ui-polish-scope) [data-testid="stAlert"] {
        border-radius: 13px !important;
    }
    body:has(.app-ui-polish-scope) [data-testid="stMainBlockContainer"],
    body:has(.app-ui-polish-scope) [data-testid="stHorizontalBlock"],
    body:has(.app-ui-polish-scope) [data-testid="stColumn"] {
        box-sizing: border-box !important;
        min-width: 0 !important;
    }
    body:has(.app-ui-polish-scope) [data-testid="stMainBlockContainer"] {
        overflow-x: clip;
    }
    body:has(.app-ui-polish-scope) .khata-ai-entry {
        padding: 12px 15px;
        margin: 4px 0 12px;
        background: linear-gradient(115deg, rgba(8, 145, 178, 0.12), rgba(59, 130, 246, 0.08));
        border: 1px solid rgba(103, 232, 249, 0.2);
        border-radius: 13px;
    }
    body:has(.app-ui-polish-scope) .khata-ai-entry-title {
        color: #d9fbff;
        font-size: 13px;
        font-weight: 800;
    }
    body:has(.app-ui-polish-scope) .khata-ai-entry-caption {
        margin-top: 3px;
        color: #9fb2c9;
        font-size: 11px;
        line-height: 1.45;
    }
    body:has(.app-ui-polish-scope) .khata-ai-parse-spacer {
        height: 27px;
    }
    body:has(.app-ui-polish-scope) [data-testid="stForm"] {
        padding: 13px;
        background: rgba(5, 13, 27, 0.36);
        border: 1px solid rgba(148, 163, 184, 0.1);
        border-radius: 15px;
    }
    @media (max-width: 900px) {
        body:has(.app-ui-polish-scope) [data-testid="stMainBlockContainer"] {
            padding: 0.55rem 0.7rem 1rem !important;
        }
        body:has(.app-ui-polish-scope) [data-testid="stHorizontalBlock"] {
            flex-wrap: wrap !important;
            gap: 0.75rem !important;
        }
        body:has(.app-ui-polish-scope) [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] {
            min-width: calc(50% - 0.4rem) !important;
            flex: 1 1 calc(50% - 0.4rem) !important;
        }
        body:has(.app-ui-polish-scope) section[data-testid="stSidebar"][aria-expanded="true"] {
            width: min(18rem, 82vw) !important;
            max-width: min(18rem, 82vw) !important;
            min-width: min(18rem, 82vw) !important;
            flex-basis: min(18rem, 82vw) !important;
        }
    }
    @media (max-width: 640px) {
        body:has(.app-ui-polish-scope) [data-testid="stMainBlockContainer"] {
            width: 100% !important;
            max-width: 100% !important;
            padding: 0.45rem 0.55rem 0.85rem !important;
        }
        body:has(.app-ui-polish-scope) .studio-header {
            min-height: 0;
            flex-wrap: wrap;
            gap: 12px;
            align-items: flex-start;
            padding: 14px 13px !important;
            margin-bottom: 12px !important;
            border-radius: 18px !important;
        }
        body:has(.app-ui-polish-scope) .studio-header h2 {
            font-size: 20px !important;
        }
        body:has(.app-ui-polish-scope) .panel-card {
            box-sizing: border-box;
            padding: 13px !important;
            margin-bottom: 10px !important;
            border-radius: 16px !important;
        }
        body:has(.app-ui-polish-scope) [data-testid="stDataFrame"],
        body:has(.app-ui-polish-scope) [data-testid="stDataEditor"],
        body:has(.app-ui-polish-scope) [data-testid="stPlotlyChart"] {
            box-sizing: border-box !important;
            max-width: 100% !important;
        }
        body:has(.app-ui-polish-scope) [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] {
            min-width: 100% !important;
            flex: 1 1 100% !important;
        }
        body:has(.app-ui-polish-scope) [data-testid="stTabs"] [role="tablist"] {
            gap: 4px !important;
            overflow-x: auto !important;
            flex-wrap: nowrap !important;
            scrollbar-width: none;
        }
        body:has(.app-ui-polish-scope) [data-testid="stTabs"] [role="tablist"]::-webkit-scrollbar {
            display: none;
        }
        body:has(.app-ui-polish-scope) [data-testid="stTabs"] [role="tab"] {
            flex: 0 0 auto !important;
            min-height: 40px !important;
            padding: 8px 11px !important;
            font-size: 11px !important;
        }
        body:has(.app-ui-polish-scope) [data-testid="stFileUploader"] {
            padding: 12px !important;
        }
        body:has(.app-ui-polish-scope) .khata-ai-parse-spacer {
            display: none;
        }
    }
    </style>
    <div class="app-ui-polish-scope" aria-hidden="true"></div>
    """, unsafe_allow_html=True)


def render_customer_khata():
    if st.session_state.get("user_role") == "Staff":
        st.error("प्रतिबंधीत क्षेत्रः कामागार/स्टाफला उधारी मॅनेजमेंट पेजवर प्रवेश करण्याची परवानगी नाही!")
        st.stop()

    st.markdown("""
    <div class="studio-header business-module-hero">
        <div class="business-hero-content">
            <div class="business-eyebrow">✦ Business Modules &gt; Customer Khata</div>
            <h2 class="business-hero-title">Customer Khata - Credit Ledger</h2>
        </div>
        <div class="business-hero-mark" aria-hidden="true">◈</div>
    </div>
    """, unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["New Credit / Installment Entry", "Credit Ledger & AI Risk Report"])

    with tab1:
        if st.session_state.pop("khata_form_reset", False):
            for field in (
                "khata_form_customer_name",
                "khata_form_phone",
                "khata_form_amount",
                "khata_form_type",
                "khata_form_entry_date",
                "khata_form_due_date",
                "khata_form_notes",
                "khata_ai_transcript",
                "khata_voice_draft",
            ):
                st.session_state.pop(field, None)
        st.markdown("<div class='panel-card'>", unsafe_allow_html=True)
        st.markdown("""
        <div class="business-section-heading">
            <div class="business-section-icon">＋</div>
            <div><h3 class="business-section-title">Add a new transaction</h3>
            <p class="business-section-caption">Safely record customer credit or a received installment.</p></div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("""
        <div class="khata-ai-entry">
            <div class="khata-ai-entry-title">⌁ AI व्हॉइस किंवा मजकूर नोंद</div>
            <div class="khata-ai-entry-caption">बोला किंवा व्यवहाराचे वाक्य लिहा; AI तपशील फॉर्ममध्ये भरेल. सेव्ह करण्यापूर्वी तपासा.</div>
        </div>
        """, unsafe_allow_html=True)
        try:
            transcript = speech_to_text(
                start_prompt="Speak transaction details",
                stop_prompt="बोलणे थांबवा",
                just_once=True,
                language="mr-IN",
                key="khata_unified_voice_input",
            )
        except Exception as exc:
            logging.exception("Voice transcription failed for customer khata")
            st.error(f"व्हॉईस रेकॉर्डिंग उपलब्ध नाही: {exc}")
            transcript = None
        if isinstance(transcript, str) and transcript.strip():
            st.session_state["khata_ai_transcript"] = transcript.strip()

        transcript_col, parse_col = st.columns([4, 1])
        with transcript_col:
            st.text_area(
                "बोलून किंवा टाइप करून व्यवहाराचा तपशील द्या",
                key="khata_ai_transcript",
                height=72,
                max_chars=1000,
                placeholder="उदा. सौरभकडे २०० रुपये उधारी",
            )
        with parse_col:
            st.markdown("<div class='khata-ai-parse-spacer'></div>", unsafe_allow_html=True)
            parse_voice = st.button(
                "AI तपशील भरा",
                key="parse_unified_khata_voice",
                type="secondary",
                
            )
        if parse_voice:
            transcript_text = st.session_state.get("khata_ai_transcript", "").strip()
            if not transcript_text:
                st.warning("आधी व्हॉईस नोंद करा किंवा व्यवहाराचे वाक्य लिहा.")
            else:
                try:
                    draft = parse_voice_khata_details(transcript_text)
                    st.session_state["khata_voice_draft"] = draft
                    st.session_state["khata_form_customer_name"] = draft["customer_name"]
                    st.session_state["khata_form_phone"] = draft["phone"]
                    st.session_state["khata_form_amount"] = draft["amount"]
                    st.session_state["khata_form_type"] = draft["transaction_type"]
                    st.session_state["khata_form_notes"] = draft["notes"]
                    st.toast("AI तपशील फॉर्ममध्ये भरले. सेव्ह करण्यापूर्वी तपासा.", icon="✨")
                    st.rerun()
                except (ValueError, json.JSONDecodeError) as exc:
                    st.error(f"AI तपशील ओळखता आले नाहीत: {exc}")
                except Exception as exc:
                    logging.exception("AI voice khata parsing failed")
                    st.error(f"AI तपशील वाचताना Error: {exc}")

        with st.form("khata_form"):
            fc1, fc2 = st.columns(2)
            with fc1:
                customer_name = st.text_input(
                    "ग्राहक नाव (Customer Name)",
                    max_chars=100,
                    key="khata_form_customer_name",
                )
                phone = st.text_input(
                    "Phone Number (10 digits)",
                    max_chars=16,
                    key="khata_form_phone",
                )
                amount = st.number_input(
                    "Amount",
                    min_value=0.0,
                    step=10.0,
                    key="khata_form_amount",
                )
            with fc2:
                transaction_type = st.selectbox(
                    "व्यवहार प्रकार (Transaction Type)",
                    KHATA_TRANSACTION_TYPES,
                    key="khata_form_type",
                )
                entry_date = st.date_input(
                    "व्यवहार तारीख (Date)",
                    value=date.today(),
                    key="khata_form_entry_date",
                )
                due_date = st.date_input(
                    "परतफेची मुदत तारीख (Due Date)",
                    value=date.today(),
                    key="khata_form_due_date",
                )
            notes = st.text_area(
                "टीप / वस्तु तपशील (Itemized Notes e.g. 2 kg sugar)",
                max_chars=1000,
                key="khata_form_notes",
            )
            submitted = st.form_submit_button("खात्यात नोंद सेव्ह करा")
        if submitted:
            try:
                record_id = save_khata_transaction(
                    customer_name, phone, amount, transaction_type, entry_date, due_date, notes
                )
                log_activity(
                    st.session_state.get("current_username", "admin"),
                    f"Added Khata ID {record_id}",
                )
                st.session_state["khata_form_reset"] = True
                st.toast("खाते नोंद अपडेट झाली!", icon="📝")
                st.rerun()
            except ValueError as exc:
                st.error(str(exc))
            except sqlite3.Error as exc:
                logging.exception("Could not save customer khata transaction")
                st.error(f"डेटाबेसमध्ये नोंद सेव्ह करता आली नाही: {exc}")
        st.markdown("</div>", unsafe_allow_html=True)

    with tab2:
        st.markdown("<div class='panel-card'>", unsafe_allow_html=True)
        header_col, refresh_col = st.columns([3, 1])
        with header_col:
            st.markdown("""
            <div class="business-section-heading">
                <div class="business-section-icon">◉</div>
                <div><h3 class="business-section-title">उधारी लेजर आणि जोखीम</h3>
                <p class="business-section-caption">बाकी रक्कम, मुदत आणि ग्राहक व्यवहारांचा आढावा.</p></div>
            </div>
            """, unsafe_allow_html=True)
        with refresh_col:
            if st.button("डेटा रिफ्रेश करा", type="primary", key="refresh_khata"):
                st.rerun()
        try:
            khata_df = load_khata_transactions()
        except sqlite3.Error as exc:
            logging.exception("Could not load customer khata transactions")
            st.error(f"लेजर डेटा वाचता आला नाही: {exc}")
            khata_df = pd.DataFrame(columns=KHATA_COLUMNS)

        risk_report = build_khata_risk_report(khata_df)
        amounts = pd.to_numeric(khata_df["amount"], errors="coerce").fillna(0)
        total_balance = float(
            amounts.where(khata_df["transaction_type"] == KHATA_CREDIT, 0).sum()
            - amounts.where(khata_df["transaction_type"] == KHATA_PAYMENT, 0).sum()
        )
        st.markdown(
            f"""
            <div class="business-metric-card" style="margin-bottom: 16px;">
                <div class="business-metric-label">एकूण येणे बाकी · Net Udhari</div>
                <div class="business-metric-value" style="color:#67e8f9;">₹ {total_balance:,.2f}</div>
                <div class="business-metric-note">जमा हप्ते वजा करून मोजलेली एकूण बाकी</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("हिशोब ऑडिओत ऐका", key="khata_audio_summary") and not khata_df.empty:
            audio_summary_text = f"सध्या एकूण रक्कम रुपये {total_balance:.0f} उधारी येणे बाकी आहे."
            try:
                audio_file = generate_marathi_tts(audio_summary_text)
                if audio_file and os.path.exists(audio_file):
                    st.audio(audio_file, autoplay=True)
                else:
                    st.error("ऑडिओ तयार करता आला नाही.")
            except Exception as exc:
                logging.exception("Could not generate khata audio summary")
                st.error(f"ऑडिओ तयार करताना Error: {exc}")

        search = st.text_input(
            "ग्राहक नाव किंवा नंबर द्वारे शोधा (Search Customer):",
            placeholder="नाव टाईप करा...",
            key="khata_search",
        ).strip()
        visible_df = khata_df.copy()
        if search:
            matches = (
                visible_df["customer_name"].fillna("").astype(str).str.contains(search, case=False, regex=False)
                | visible_df["phone"].fillna("").astype(str).str.contains(search, case=False, regex=False)
            )
            visible_df = visible_df[matches]
        visible_risk = risk_report
        if search and not risk_report.empty:
            visible_risk = risk_report[
                risk_report["customer_name"].fillna("").astype(str).str.contains(search, case=False, regex=False)
                | risk_report["phone"].fillna("").astype(str).str.contains(search, case=False, regex=False)
            ]

        st.markdown("##### ग्राहकनिहाय उधारी, AI रिस्क, WhatsApp & Direct Call")
        st.caption("रिस्क स्कोअर उर्वरित शिल्लक आणि मुदत ओलांडलेल्या उधारीवरून स्थानिक पातळीवर मोजला जातो.")
        business_upi_id = load_business_upi_id()
        upi_configured = bool(
            re.fullmatch(
                r"[A-Za-z0-9._-]{2,256}@[A-Za-z0-9.-]{2,64}",
                business_upi_id,
            )
        )
        if not upi_configured and not visible_risk.empty:
            st.info(
                "WhatsApp पेमेंट लिंक चालू करण्यासाठी Streamlit secrets मध्ये "
                "BUSINESS_UPI_ID कॉन्फिगर करा."
            )
        for _, customer in visible_risk.iterrows():
            name = _khata_text(customer["customer_name"])
            customer_phone = _khata_text(customer["phone"])
            risk_level = customer["risk_level"]
            risk_color = "#f87171" if risk_level.startswith("High") else (
                "#f59e0b" if risk_level.startswith("Moderate") else "#00ff87"
            )
            st.markdown(
                f"""
                <div style="background: rgba(15,23,42,0.9); border: 1px solid rgba(0,242,254,0.25); padding: 14px; border-radius: 14px; margin-bottom: 12px;">
                    <div style="display: flex; justify-content:space-between; font-weight:700; font-size:15px;">
                        <span>{escape(name)} ({escape(customer_phone or "फोन उपलब्ध नाही")})</span>
                        <span style="color:{risk_color};">{escape(risk_level)} · {int(customer["risk_score"])}/100</span>
                    </div>
                    <div style="font-size:13px; color:#94a3b8; margin-top:6px;">
                        बाकी रक्कम: <b style="color:#00f2fe; font-size:15px;">{customer["balance"]:,.2f}</b>
                        &nbsp; मुदतबाह्य: <b>{customer["overdue_balance"]:,.2f}</b>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            clean_phone = re.sub(r"\D", "", customer_phone)
            if len(clean_phone) >= 10:
                if len(clean_phone) == 10:
                    clean_phone = "91" + clean_phone
                elif len(clean_phone) == 11 and clean_phone.startswith("0"):
                    clean_phone = "91" + clean_phone[1:]
                    
                if upi_configured and customer["balance"] > 0:
                    action_col1, action_col2, action_col3 = st.columns(3)
                else:
                    action_col1, action_col2 = st.columns(2)
                    action_col3 = None
                    
                if customer["balance"] > 0:
                    message = (
                        f"नमस्कार {name} जी, तुमच्याकडे VernaLedger दुकान उधारीचे "
                        f"₹{customer['balance']:,.2f} रुपये बाकी आहेत. धन्यवाद!"
                    )
                else:
                    message = (
                        f"नमस्कार {name} जी, तुमच्या VernaLedger खात्यात सध्या "
                        "काही बाकी रक्कम नाही. धन्यवाद!"
                    )
                if upi_configured and customer["balance"] > 0:
                    payment_link = build_upi_payment_link(
                        business_upi_id,
                        "VernaLedger",
                        name,
                        customer["balance"],
                    )
                    message += (
                        f"\n\nGoogle Pay किंवा इतर UPI अॅपमधून पेमेंट करण्यासाठी लिंक:\n"
                        f"{payment_link}"
                    )
                    whatsapp_label = "WhatsApp + पेमेंट"
                else:
                    whatsapp_label = "WhatsApp संदेश"
                    
                with action_col1:
                    st.link_button(whatsapp_label, f"https://wa.me/{clean_phone}?text={urllib.parse.quote(message)}", use_container_width=True)
                with action_col2:
                    st.link_button("थेट कॉल करा", f"tel:{customer_phone}", use_container_width=True)
                if action_col3 and upi_configured and customer["balance"] > 0:
                    with action_col3:
                        st.link_button("Direct UPI Pay", payment_link, use_container_width=True)

        st.markdown("---")
        st.markdown("##### संपूर्ण उधारी व्यवहारांची यादी व Edit / Settle")
        if visible_df.empty:
            st.info("कोणतीही उधारी नोंद उपलब्ध नाही.")
        else:
            visible_record_ids = [int(record_id) for record_id in visible_df["id"].tolist()]
            record_signature = hashlib.sha256(
                visible_df[KHATA_COLUMNS].to_json(
                    orient="split", force_ascii=False
                ).encode("utf-8")
            ).hexdigest()
            edited_df = st.data_editor(
                visible_df[KHATA_COLUMNS],
                
                key=f"khata_editable_table_{record_signature}",
                disabled=["id"],
                num_rows="fixed",
            )
            edit_col, delete_col = st.columns(2)
            with edit_col:
                if st.button("उधारी records अपडेट (Save Edit)", key="save_khata_edits"):
                    try:
                        updated_count = update_khata_transactions(visible_df, edited_df)
                        log_activity(
                            st.session_state.get("current_username", "admin"),
                            f"Updated {updated_count} Khata Records",
                        )
                        st.toast(f"{updated_count} उधारी रेकॉर्ड अपडेट केले.", icon="✅")
                        st.rerun()
                    except ValueError as exc:
                        st.error(str(exc))
                    except sqlite3.Error as exc:
                        logging.exception("Could not update customer khata transactions")
                        st.error(f"रेकॉर्ड अपडेट करता आले नाहीत: {exc}")
            with delete_col:
                delete_id = st.selectbox(
                    "डिलिट करण्यासाठी रेकॉर्ड आयडी (Delete ID)",
                    visible_record_ids,
                    key=f"delete_khata_id_{record_signature}",
                )
                if st.button("उधारी नोंद डिलीट करा", key="delete_khata_record"):
                    try:
                        if delete_khata_transaction(delete_id):
                            log_activity(
                                st.session_state.get("current_username", "admin"),
                                f"Deleted Khata ID {delete_id}",
                            )
                            st.toast(f"रेकॉर्ड ID {delete_id} डिलीट केला!", icon="🗑️")
                            st.rerun()
                        else:
                            st.error("रेकॉर्ड सापडला नाही; लेजर रिफ्रेश करा.")
                    except sqlite3.Error as exc:
                        logging.exception("Could not delete customer khata transaction")
                        st.error(f"रेकॉर्ड डिलीट करता आला नाही: {exc}")
        st.markdown("</div>", unsafe_allow_html=True)

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
if 'user_role' not in st.session_state:
    st.session_state['user_role'] = 'Admin'
if 'current_username' not in st.session_state:
    st.session_state['current_username'] = 'admin'
if 'forgot_pass_mode' not in st.session_state:
    st.session_state['forgot_pass_mode'] = False
if 'input_method' not in st.session_state:
    st.session_state['input_method'] = 'Upload File'
if "ui_language" not in st.session_state:
    st.session_state["ui_language"] = "mr"


_UI_TRANSLATION_PAIRS = {
    "Language / भाषा": "भाषा",
    "Use English": "English वापरा",
    "चालू: English · बंद: मराठी": "On: English · Off: Marathi",
    "Login": "लॉगिन",
    "Admin Sign Up": "प्रशासक नोंदणी",
    "Auth Mode": "प्रवेश प्रकार",
    "Navigation": "नेव्हिगेशन",
    "Username": "वापरकर्ता नाव",
    "Password": "पासवर्ड",
    "Confirm Password": "पासवर्डची पुष्टी",
    "Mobile Number": "मोबाईल नंबर",
    "Admin Username": "प्रशासक वापरकर्ता नाव",
    "Admin Password": "प्रशासक पासवर्ड",
    "Auto-Login Persistent Session": "मला लॉग इन ठेवा",
    "Access VernaLedger Studio": "VernaLedger सुरू करा",
    "Create Master Admin": "मास्टर प्रशासक तयार करा",
    "10-digit mobile number": "१० अंकी मोबाईल नंबर",
    "Choose admin username": "प्रशासकाचे वापरकर्ता नाव निवडा",
    "Confirm password": "पासवर्ड पुन्हा लिहा",
    "Enter password": "पासवर्ड लिहा",
    "Enter username (e.g. admin)": "वापरकर्ता नाव लिहा (उदा. admin)",
    "Min 6 chars": "किमान ६ अक्षरे",
    "Min 6 chars password": "किमान ६ अक्षरांचा पासवर्ड",
    "Re-enter password": "पासवर्ड पुन्हा भरा",
    "OCR Scanner": "OCR स्कॅनर",
    "Sales & Analytics": "विक्री आणि विश्लेषण",
    "Business Modules": "व्यवसाय विभाग",
    "Ledger Database": "लेजर डेटाबेस",
    "RAG AI Chat": "RAG AI चॅट",
    "Staff Management": "स्टाफ व्यवस्थापन",
    "Customer Khata": "ग्राहक खाते",
    "Stock & Inventory": "स्टॉक आणि इन्व्हेंटरी",
    "Business Expenses": "व्यवसाय खर्च",
    "New Credit / Installment Entry": "New Credit / Installment Entry",
    "Old Records & AI Smart Search": "Old Records & AI Smart Search",
    "Speak transaction details": "Speak transaction details",
    "New Credit / Installment Entry": "New Credit / Installment Entry",
    "Credit Ledger & AI Risk Report": "उधारी लेजर & AI रिस्क रिपोर्ट",
    "Speak the order (Voice Billing)": "बोलून ऑर्डर द्या (वॉइस बिलिंग)",
    "Press here when done speaking": "बोलणे पूर्ण झाल्यावर इथे दाबा",

    "Stop recording": "Stop recording",
    "Old Transactions & AI Search": "जुने व्यवहार आणि AI शोधक",
    "Log of past transactions and smart AI search.": "मागील सर्व व्यवहारांची नोंद आणि AI द्वारे स्मार्ट सर्च.",
    "No past transactions found in the system.": "सिस्टीममध्ये कोणताही जुना व्यवहार सापडला नाही.",
    "New khata entry safely saved!": "नवीन खता नोंद सुरक्षितपणे सेव्ह केली!",
    "Transaction ID to delete": "व्यवहार नोंद डिलीट करण्यासाठी ID",
    "No goods found in inventory.": "इन्व्हेंटरी मध्ये कोणताही माल सापडला नाही.",
    "Save Stock Update": "स्टॉक अपडेट सेव्ह करा",
    "New stock item successfully added to inventory!": "नवीन माल इन्व्हेंटरीमध्ये Successfully जोडला गेला!",
    "Expense successfully recorded!": "Expense successfully recorded!",

    "Item Name": "वस्तूचे नाव (Item Name)",
    "Stock Quantity": "उपलब्ध नग/साठा (Stock Quantity)",
    "Unit (e.g. kg, pcs, ltr)": "मोजमाप एकक (Unit e.g. kg, pcs, ltr)",
    "Low Stock Alert Limit": "किमान वार्निंग लिमिट (Low Stock Alert Limit)",
    "Save Stock": "स्टॉक सेव्ह करा",
    "Please enter item name!": "Please enter item name!",
    "Item ID to delete": "डिलिट करण्यासाठी आयटम ID",
    "No stock available.": "No stock available.",
    "Total Business Expenses": "एकूण व्यवसाय खर्च",
    "Expense Records": "खर्च नोंदी",
    "Expense ID to delete": "डिलिट करण्यासाठी खर्च ID",
    "Delete Expense Record": "खर्च नोंद डिलीट करा",
    "No expenses recorded.": "No expenses recorded.",
    "Restricted Area: Staff not allowed on Staff Management page!": "प्रतिबंधीत क्षेत्रः कामागार/स्टाफला स्टाफ मॅनेजमेंट पेजवर प्रवेश करण्याची परवानगी नाही!",
    "Add New Staff or Admin": "नवीन स्टाफ किंवा अॅडमिन जोडा",
    "Password (Min 6 digits)": "पासवर्ड (Password - किमान ६ अंक)",
    "Role": "भूमिका",
    "Staff (Cashier - Limited Access)": "Staff (कामगार/कॅशियर - Limited Access)",
    "Admin (Owner - Full Access)": "Admin (मालक - Full Access)",
    "Create Account": "अकाऊंट तयार करा",
    "Please fill all fields and password must be at least 6 characters!": "कृपया सर्व फील्ड भरा आणि पासवर्ड किमान ६ अंकांचा असावा!",
    "Username to delete account": "Username to delete account",
    "Delete Account": "Delete Account",
    "System Audit Logs": "System Audit Logs",
    "Total Revenue Today": "Total Revenue Today",
    "Total Bills Today": "Total Bills Today",
    "Average Ticket Size": "Average Ticket Size",
    "Top Performing Shop": "Top Performing Shop",

    "Stock & <span>Inventory</span>": "स्टॉक आणि <span>इन्व्हेंटरी</span>",
    "Manage your goods, prices, and availability here.": "तुमचा माल, त्याचे दर आणि उपलब्धतेची माहिती येथे ठेवा.",
    "Add New Stock": "नवीन माल जोडा",
    "Add new items to inventory and set low-stock alerts.": "इन्व्हेंटरी मध्ये नवीन आयटम आणि लो-स्टॉक अलर्ट सेट करा.",
    "Current Stock": "सध्याचा स्टॉक",
    "List of available goods and low stock items.": "उपलब्ध माल आणि संपत असलेल्या साठ्याची यादी.",
    "Business Expenses <span>— Tracker</span>": "व्यवसाय खर्च <span>— ट्रॅकर</span>",
    "Keep track of rent, salary, electricity bills, and other expenses.": "भाडे, पगार, लाईट बिल आणि इतर सर्व खर्चांची नोंद ठेवा.",
    "Record New Expense": "नवीन खर्च नोंदवा",
    "Keep track of daily shop expenses.": "दुकानातील दैनंदिन खर्चाची नोंद ठेवा.",
    "Expense Report": "खर्चाचा अहवाल",
    "Analysis and list of past expenses.": "मागील खर्चाचे विश्लेषण आणि यादी.",
    "Expense Title (e.g. Light Bill)": "खर्चाचा टायटल (Expense Title e.g. Light Bill)",
    "Expense Amount": "खर्च रक्कम (Amount)",
    "Expense Category": "खर्चाचा वर्ग (Category)",
    "Shop Rent": "दुकान भाडे (Shop Rent)",
    "Electricity Bill": "लाईट बिल (Electricity)",
    "Staff Salary": "स्टाफचा पगार (Staff Salary)",
    "Transport": "वाहतूक / ट्रान्सपोर्ट (Transport)",
    "Miscellaneous": "इतर खर्च (Miscellaneous)",
    "Date": "तारीख (Date)",
    "Notes": "नोट्स / टिपणी (Notes)",
    "Submit Expense": "खर्च सबमिट करा",
    "No goods selected.": "तुम्ही कोणताही माल निवडला नाही.",
    "Delete Expense": "खर्च डिलीट करा",
    "Item Name (e.g. Milk 1L)": "आयटमचे नाव (Item Name e.g. Milk 1L)",
    "Purchase Price": "खरेदी किंमत (Purchase Price)",
    "Selling Price": "विक्री किंमत (Selling Price)",
    "Quantity": "स्टॉक प्रमाण (Quantity)",
    "Unit (e.g. Kg, L, Pcs)": "युनिट (Unit e.g. Kg, L, Pcs)",
    "Low Stock Limit": "लो-स्टॉक अलर्ट लिमिट (Low Stock Limit)",
    "Add to Inventory": "माल इन्व्हेंटरीत जोडा",
    "Delete from Inventory": "इन्व्हेंटरी मधून हटवा",
    "Delete Stock Item": "Delete Stock Item",
    "Customer Name": "कस्टमर नाव (Customer Name)",
    "Phone Number (10 digits)": "मोबाईल नंबर (Phone Number - 10 digits)",
    "Phone Number": "मोबाईल नंबर (Phone Number)",
    "Amount": "रक्कम (Amount)",
    "Transaction Type": "व्यवहाराचा प्रकार (Transaction Type)",
    "Credit Given": "उधारी दिली (Credit Given)",
    "Payment Received": "पैसे मिळाले (Payment Received)",
    "Optional Notes": "नोट्स (Optional Notes)",
    "Save Transaction": "व्यवहार सेव्ह करा",
    "Delete Transaction": "खाता व्यवहार डिलीट करा",

    "Navigation Suite": "नेव्हिगेशन",
    "NAVIGATION SUITE": "नेव्हिगेशन",
    "✦ BUSINESS MODULES · EXPENSES": "✦ व्यवसाय विभाग · खर्च",
    "✦ BUSINESS MODULES · INVENTORY": "✦ व्यवसाय विभाग · इन्व्हेंटरी",
    "MERCHANT SUITE PRO": "व्यवसाय व्यवस्थापन",
    "Next-Gen Merchant & AI Financial Suite": "नव्या पिढीचे व्यापारी आणि AI आर्थिक व्यासपीठ",
    "Verna Pro Multi-Language Studio (Auto-Detect Language)": "Verna Pro बहुभाषिक स्टुडिओ (भाषा आपोआप ओळखा)",
    "Marathi Audio Summary": "मराठी ऑडिओ सारांश",
    "📥 Backups & Report Downloads": "📥 बॅकअप आणि अहवाल डाउनलोड",
    "Initial Admin Registration": "प्रारंभिक प्रशासक नोंदणी",
    "Project Developers": "प्रकल्प विकासक",
    "Logout System": "लॉगआउट",
    "ROLE: ADMIN": "भूमिका: प्रशासक",
    "ROLE: STAFF": "भूमिका: कर्मचारी",
    "Customer Khata": "ग्राहक खाते",
        "उधारी लेजर & AI रिस्क रिपोर्ट": "लेजर आणि AI जोखीम अहवाल",
    "स्मार्ट AI व्हॉईस नोंद (Multi-Language Voice-to-Khata)": "AI व्हॉइस नोंद",
    "Customer Khata - Credit Ledger": "ग्राहक खाते - उधारी वही",
    "नवीन व्यवहार नोंदवा": "Add a new transaction",
    "ग्राहकाची उधारी किंवा जमा झालेला हप्ता सुरक्षितपणे नोंदवा.": "Safely record customer credit or a received installment.",
    "ग्राहक नाव (Customer Name)": "ग्राहकाचे नाव",
    "Phone Number (10 digits)": "मोबाईल नंबर (१० अंक)",
    "Phone Number": "मोबाईल नंबर",
    "मोबाईल नंबर (Phone)": "मोबाईल नंबर",
    "Amount": "रक्कम",
    "व्यवहार प्रकार (Transaction Type)": "व्यवहाराचा प्रकार",
    "व्यवहार तारीख (Date)": "व्यवहाराची तारीख",
    "परतफेची मुदत तारीख (Due Date)": "देय तारीख",
    "टीप / वस्तु तपशील (Itemized Notes e.g. 2 kg sugar)": "टीप / वस्तूंचा तपशील",
    "खात्यात नोंद सेव्ह करा": "Save transaction",
    "⌁ AI व्हॉइस किंवा मजकूर नोंद": "⌁ AI voice or text entry",
    "बोला किंवा व्यवहाराचे वाक्य लिहा; AI तपशील फॉर्ममध्ये भरेल. सेव्ह करण्यापूर्वी तपासा.": "Speak or type a transaction; AI will fill the form. Review it before saving.",
    "डेटा रिफ्रेश करा": "Refresh data",
    "हिशोब ऑडिओत ऐका": "Play audio summary",
    "ग्राहक नाव किंवा नंबर द्वारे शोधा (Search Customer):": "Search by customer name or phone:",
    "नाव टाईप करा...": "Enter a name...",
    "ग्राहकनिहाय उधारी, AI रिस्क, WhatsApp & Direct Call": "Customer credit, AI risk, WhatsApp and calls",
    "रिस्क स्कोअर उर्वरित शिल्लक आणि मुदत ओलांडलेल्या उधारीवरून स्थानिक पातळीवर मोजला जातो.": "Risk scores are calculated locally from outstanding balances and overdue credit.",
    "एकूण येणे बाकी · Net Udhari": "Total outstanding balance",
    "जमा हप्ते वजा करून मोजलेली एकूण बाकी": "Outstanding amount after received payments",
    "WhatsApp पेमेंट लिंक": "WhatsApp payment link",
    "WhatsApp संदेश": "WhatsApp message",
    "थेट कॉल करा": "Call customer",
    "संपूर्ण उधारी व्यवहारांची यादी व Edit / Settle": "All credit transactions · edit or settle",
    "उधारी records अपडेट (Save Edit)": "Save record edits",
    "डिलिट करण्यासाठी रेकॉर्ड आयडी (Delete ID)": "Record ID to delete",
    "उधारी नोंद डिलीट करा": "Delete credit record",
    "रेकॉर्ड सापडला नाही; लेजर रिफ्रेश करा.": "Record not found. Refresh the ledger.",
    "कृपया ग्राहकाचे नाव भरा.": "Enter the customer name.",
    "ग्राहकाचे नाव 100 अक्षरांपेक्षा मोठे असू शकत नाही.": "Customer name cannot exceed 100 characters.",
    "रक्कम शून्यापेक्षा मोठी असणे आवश्यक आहे.": "Amount must be greater than zero.",
    "रक्कम वैध संख्या असणे आवश्यक आहे.": "Enter a valid amount.",
    "व्यवहार प्रकार उपलब्ध पर्यायांपैकी निवडा.": "Select a valid transaction type.",
    "टीप 1000 अक्षरांपेक्षा मोठी असू शकत नाही.": "Notes cannot exceed 1,000 characters.",
    "ग्राहकाचे नाव 100 अक्षरांपेक्षा मोठे असू शकत नाही.": "Customer name cannot exceed 100 characters.",
    "फोन नंबर रिकामा ठेवा किंवा वैध 10 अंकी मोबाईल नंबर भरा.": "Leave the phone number blank or enter a valid 10-digit mobile number.",
    "डेटाबेसमध्ये नोंद सेव्ह करता आली नाही:": "Could not save the database record:",
    "नोंद सेव्ह करता आली नाही:": "Could not save the record:",
    "रेकॉर्ड अपडेट करता आले नाहीत:": "Could not update records:",
    "रेकॉर्ड डिलीट करता आला नाही:": "Could not delete the record:",
    "खाते नोंद अपडेट झाली!": "Ledger entry saved!",
    "व्हॉईस खात्यातील नोंद सेव्ह झाली!": "Voice transaction saved!",
    "प्रतिबंधीत क्षेत्रः": "Restricted area:",
    "कामागार/स्टाफला": "staff members are not allowed to access",
    "उधारी मॅनेजमेंट पेजवर प्रवेश करण्याची परवानगी नाही!": "the customer credit page.",
    "इन्व्हेंटरी पेजवर प्रवेश करण्याची परवानगी नाही!": "the inventory page.",
    "व्यवसाय खर्च पेजवर प्रवेश करण्याची परवानगी नाही!": "the business expenses page.",
    "OCR Scanner & Multi-Language Voice Billing": "OCR स्कॅनर आणि बहुभाषिक व्हॉईस बिलिंग",
    "Instant Digital POS Receipt Parsing & Audio Confirmation": "पावत्या स्कॅन करा आणि आवाजाद्वारे बिल नोंदवा",
    "POS ONLINE": "POS सुरू आहे",
    "Input Mode": "इनपुट प्रकार",
    "ड्युप्लिकेट पावती असल्यास जबरदस्तीने सेव्ह करा (Force Save)": "Save duplicate receipts anyway",
    "Upload File": "फाइल अपलोड करा",
    "Live Camera": "थेट कॅमेरा",
    "Voice Bill": "व्हॉइस बिल",
    "Take photo": "फोटो घ्या",
    "Choose Receipts": "पावत्या निवडा",
    "प्रोग्रेस सुरू आहे... व्हॉईसवरून बिल तयार होत आहे.": "Processing voice input and preparing the bill...",
    "व्हॉईस बिल Successfully तयार होऊन डेटाबेसमध्ये सेव्ह झाले !": "Voice bill processed and saved successfully!",
    "व्हॉईस बिल सेव्ह झाले!": "Voice bill saved!",
    "Process Receipt(s)": "पावती प्रक्रिया करा",
    "Successfully processed": "यशस्वी प्रक्रिया:",
    "पावती Successfully स्कॅन झाली!": "Receipt scanned successfully!",
    "कृपया किमान एक पावती निवडा किंवा कॅमेऱ्याने फोटो घ्या.": "Select at least one receipt or take a photo.",
    "Extracted Items & Summary": "काढलेल्या वस्तू आणि सारांश",
    "Scan receipt(s) or use Multi-Language Voice Bill to display extracted items & summary.": "Scan a receipt or use voice billing to see extracted items and the summary.",
    "Daily Sales & Merchant Analytics": "दैनिक विक्री आणि व्यवसाय विश्लेषण",
    "Daily Revenue, Ticket Size, Category & Custom Period Reports": "दैनिक उत्पन्न, सरासरी बिल आणि कालावधी अहवाल",
    "कस्टम अहवाल आणि कालावधी फिल्टर (Custom Period Filters)": "अहवाल कालावधी फिल्टर",
    "अहवाल कालावधी निवडा (Select Report Period):": "अहवालाचा कालावधी निवडा:",
    "All Time (संपूर्ण वेळ)": "सर्व कालावधी",
    "Daily (आजचा दिवस)": "आज",
    "Weekly (चालू आठवडा)": "या आठवड्यात",
    "Monthly (चालू महिना)": "या महिन्यात",
    "TOTAL REVENUE / SALES": "एकूण विक्री",
    "TOTAL BILLS/ORDERS": "एकूण बिले / ऑर्डर",
    "AVG TICKET SIZE": "सरासरी बिल रक्कम",
    "TOP PERFORMING SHOP": "आघाडीचे दुकान",
    "Category Breakdown": "वर्गनिहाय विक्री",
    "Shop Revenue Overview": "दुकाननिहाय उत्पन्न",
    "स्टॉक आणि इन्व्हेंटरी": "Stock & Inventory",
    "उपलब्ध माल, कमी साठा आणि वस्तूंची स्थिती एका नजरेत.": "View available stock, low inventory and item status at a glance.",
    "Save Stock": "Save stock",
    "Item Name": "वस्तूचे नाव",
    "Stock Quantity": "उपलब्ध साठा",
    "Unit (e.g. kg, pcs, ltr)": "मोजमापाचे एकक (उदा. kg, नग, ltr)",
    "Low Stock Alert Limit": "कमी साठ्याची सूचना मर्यादा",
    "स्टॉक आयटम डिलिट करा": "Delete stock item",
    "डिलिट करण्यासाठी स्टॉक ID": "Stock ID to delete",
    "कोणताही स्टॉक जोडलेला नाही.": "No stock items have been added.",
    "नवीन माल जोडा": "Add inventory item",
    "वस्तूचे नाव, प्रमाण आणि कमी-साठा मर्यादा भरा.": "Enter the item name, quantity and low-stock limit.",
    "साठ्याचा आढावा": "Inventory overview",
    "वस्तूंची यादी आणि पुन्हा मागवायच्या वस्तू.": "Items in stock and items to reorder.",
    "व्यवसाय खर्च · नोंदवही": "Business Expenses",
    "भाडे, वीज, पगार आणि रोजच्या खर्चांचा स्पष्ट हिशोब.": "Track rent, utilities, payroll and everyday business costs.",
    "Record New Expense": "Add an expense",
    "खर्चाचा प्रकार, रक्कम आणि तारीख नोंदवा.": "Enter the expense type, amount and date.",
    "खर्चाचे शीर्षक (Expense Title e.g. Light Bill)": "खर्चाचे शीर्षक (उदा. वीज बिल)",
    "Expense Amount": "खर्चाची रक्कम",
    "खर्चाचा प्रकार (Category)": "खर्चाचा प्रकार",
    "Date": "तारीख",
    "तपशील / टीप (Notes)": "तपशील / टीप",
    "खर्च सेव्ह करा": "Save expense",
    "Total Business Expenses": "Total business expenses",
    "Expense ID to delete": "Expense ID to delete",
    "Delete Expense Record": "Delete expense record",
    "No expenses recorded.": "No expenses have been recorded.",
    "Admin Staff Management & Audit Logs": "स्टाफ व्यवस्थापन आणि ऑडिट लॉग",
    "Create Staff Accounts & View Complete System Activity Audit Trail": "स्टाफ खाती तयार करा आणि प्रणालीतील हालचाली पहा",
    "Staff Management": "स्टाफ व्यवस्थापन",
    "System Audit Logs": "सिस्टीम ऑडिट लॉग",
    "Add New Staff or Admin": "नवीन स्टाफ किंवा प्रशासक जोडा",
    "Username": "वापरकर्ता नाव",
    "Phone Number": "मोबाईल नंबर",
    "Password (Min 6 digits)": "पासवर्ड (किमान ६ अक्षरे)",
    "Role": "भूमिका",
    "Create Account": "Create account",
    "नोंदणीकृत युझर्सची यादी": "नोंदणीकृत वापरकर्ते",
    "डिलिट करण्यासाठी युजरनेम टाईप करा (Username to delete)": "हटवण्यासाठी वापरकर्ता नाव लिहा",
    "युजर डिलीट करा": "वापरकर्ता हटवा",
    "मुख्य मास्टर अॅडमिन युजर डिलीट करता येणार नाही!": "The master administrator account cannot be deleted.",
    "कोणतेही ऑडिट लॉग्ज उपलब्ध नाहीत.": "No audit logs are available.",
    "ऑडिट लॉग्ज लोड करण्यात त्रुटी.": "Could not load audit logs.",
    "Ledger Database & Multi-Language Export": "लेजर डेटाबेस आणि अहवाल डाउनलोड",
    "Enterprise Storage, Advanced Filters, Clean Layout & Report Downloads": "डेटा, प्रगत फिल्टर आणि अहवाल डाउनलोड",
    "Select Shop / Vendor": "दुकान / विक्रेता निवडा",
    "Select Category": "वर्ग निवडा",
    "Quick Search": "जलद शोध",
    "Search anything...": "काहीही शोधा...",
    "➕": "➕",
    "नवीन रो Successfully जोडली गेली!": "New entry जोडली!",
    "दुकान निवडून डाउनलोड करा (Select Shop)": "डाउनलोडसाठी दुकान निवडा",
    "पावतीची भाषा निवडा:": "पावतीची भाषा निवडा:",
    "पावतीची भाषा निवडा": "पावतीची भाषा निवडा",
    "पासून (Start Date)": "सुरुवातीची तारीख",
    "पर्यंत (End Date)": "शेवटची तारीख",
    "Export Clean CSV": "CSV डाउनलोड करा",
    "Ledger database is empty.": "लेजर डेटाबेस रिकामा आहे.",
    "Welcome to Verna AI": "Verna AI मध्ये स्वागत आहे",
    "Verna AI Studio": "Verna AI Studio",
    "Your Smart Ledger &amp; Business Assistant": "तुमचा स्मार्ट लेजर आणि व्यवसाय सहाय्यक",
    "Voice Output": "आवाजात उत्तर",
    "ऑडिओ उत्तर चालू किंवा बंद करा": "आवाजातील उत्तरे सुरू किंवा बंद करा",
    "Gemini is not configured. Add GEMINI_API_KEY to Streamlit secrets or the environment to enable AI chat. Never share the key publicly.": "Gemini कॉन्फिगर केलेले नाही. AI चॅट सुरू करण्यासाठी Streamlit secrets किंवा environment मध्ये GEMINI_API_KEY जोडा. ही key सार्वजनिक करू नका.",
    "Hello! Ask me anything about your shop ledger, stock, or expenses.": "नमस्कार! दुकानाचा लेजर, साठा किंवा खर्च याबद्दल प्रश्न विचारा.",
    "Chat message": "चॅट संदेश",
    "Speak your message": "बोलून संदेश द्या",
    "Send message": "संदेश पाठवा",
    "Ask in English, Marathi, or Hindi": "मराठी, इंग्रजी किंवा हिंदीत विचारा",
    "Ask in English, मराठी, or हिंदी...": "मराठी, इंग्रजी किंवा हिंदीत विचारा...",
    "Speech recognition is not supported in this browser.": "या ब्राउझरमध्ये आवाज ओळखण्याची सुविधा उपलब्ध नाही.",
    "Listening": "ऐकत आहे",
    "Microphone access was denied.": "मायक्रोफोन वापरण्याची परवानगी नाकारली.",
    "Unable to start speech recognition.": "आवाज ओळख सुरू करता आली नाही.",
    "English": "English",
    "Select an option": "पर्याय निवडा",
    "All Shops/Vendors": "सर्व दुकाने / विक्रेते",
    "All Categories": "सर्व वर्ग",
    "Staff (Cashier - Limited Access)": "कर्मचारी (मर्यादित प्रवेश)",
    "Admin (Owner - Full Access)": "प्रशासक (पूर्ण प्रवेश)",
    "Shop Rent": "दुकान भाडे",
    "वीज बिल (Electricity Bill)": "वीज बिल",
    "स्टाफ पगार (Staff Salary)": "स्टाफ पगार",
    "वाहतूक (Transport)": "वाहतूक",
    "इतर (Other)": "इतर",
}


def _translate_ui_text(value):
    if not isinstance(value, str):
        return value
    language = st.session_state.get("ui_language", "mr")
    devanagari_pattern = re.compile(r"[\u0900-\u097f]")
    if language == "en":
        replacements = []
        for source, target in _UI_TRANSLATION_PAIRS.items():
            source_has_devanagari = bool(devanagari_pattern.search(source))
            target_has_devanagari = bool(devanagari_pattern.search(target))
            if source_has_devanagari and not target_has_devanagari:
                replacements.append((source, target))
            elif not source_has_devanagari and target_has_devanagari:
                replacements.append((target, source))
            elif source_has_devanagari and target_has_devanagari:
                english_label = re.search(r"\(([^()]*)\)", source)
                if english_label and not devanagari_pattern.search(english_label.group(1)):
                    replacements.append((source, english_label.group(1).strip()))
        
        # FINAL FALLBACK for English: if there's still Devanagari in the value, aggressively strip it if it has an English parenthetical!
        if devanagari_pattern.search(value):
            # Extract parentheticals (e.g. "मराठी (English text)" -> "English text")
            clean_val = re.sub(r'[ऀ-ॿ]+[^ऀ-ॿ(]*\(([^()]+)\)', r'\1', value)
            if clean_val != value: return clean_val
            
    else:
        replacements = []
        for source, target in _UI_TRANSLATION_PAIRS.items():
            source_has_devanagari = bool(devanagari_pattern.search(source))
            target_has_devanagari = bool(devanagari_pattern.search(target))
            if target_has_devanagari:
                replacements.append((source, target))
            elif source_has_devanagari:
                replacements.append((target, source))
    translated = value
    for source, target in sorted(replacements, key=lambda pair: len(pair[0]), reverse=True):
        translated = translated.replace(source, target)
    return translated


class _LocalizedStreamlitProxy:
    _TEXT_METHODS = {
        "title", "header", "subheader", "caption", "write", "info", "success",
        "warning", "error", "toast", "button", "text_input", "text_area",
        "selectbox", "radio", "checkbox", "form_submit_button",
        "download_button", "metric", "date_input", "number_input",
        "file_uploader", "camera_input", "toggle", "spinner", "expander",
    }
    _OPTION_METHODS = {"selectbox", "radio", "multiselect", "select_slider"}

    def __init__(self, streamlit_module):
        self._streamlit_module = streamlit_module

    def __getattr__(self, name):
        original = getattr(self._streamlit_module, name)
        if name not in self._TEXT_METHODS | self._OPTION_METHODS | {"markdown", "tabs", "dataframe", "data_editor"}:
            return original

        def localized_call(*args, **kwargs):
            if name == "markdown" and args:
                args = (_translate_ui_text(args[0]), *args[1:])
            elif name == "tabs" and args:
                args = ([_translate_ui_text(label) for label in args[0]], *args[1:])
            elif name in self._TEXT_METHODS and args:
                args = (_translate_ui_text(args[0]), *args[1:])

            for keyword in ("help", "placeholder"):
                if isinstance(kwargs.get(keyword), str):
                    kwargs[keyword] = _translate_ui_text(kwargs[keyword])

            if name in self._OPTION_METHODS:
                formatter = kwargs.get("format_func", str)
                kwargs["format_func"] = lambda option: _translate_ui_text(formatter(option))

            if name in {"dataframe", "data_editor"} and args and isinstance(args[0], pd.DataFrame):
                column_config = dict(kwargs.get("column_config") or {})
                for column in args[0].columns:
                    label = _translate_ui_text(str(column))
                    if label != str(column) and column not in column_config:
                        column_config[column] = self._streamlit_module.column_config.Column(label=label)
                if column_config:
                    kwargs["column_config"] = column_config

            return original(*args, **kwargs)

        return localized_call


def _sync_language_from_toggle():
    st.session_state["ui_language"] = (
        "en" if st.session_state.get("ui_language_english", False) else "mr"
    )
    st.query_params["lang"] = st.session_state["ui_language"]


def _render_language_toggle():
    _streamlit_ui.toggle(
        _translate_ui_text("Use English"),
        value=st.session_state.get("ui_language", "mr") == "en",
        key="ui_language_english",
        
        on_change=_sync_language_from_toggle,
    )


_streamlit_ui = st
st = _LocalizedStreamlitProxy(_streamlit_ui)


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
        <div class="sidebar-brand" style="display: flex; align-items: center; gap: 10px; margin-bottom: 10px; padding: 4px 0;">
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

    /* --- SAFE FONT APPLICATION --- */
    .stApp {{
        font-family: 'Plus Jakarta Sans', 'Mukta', 'Hind', 'Baloo 2', sans-serif;
    }}
    h1, h2, h3, h4, h5, h6, p, li, label, .stMarkdown {{
        font-family: 'Plus Jakarta Sans', 'Mukta', 'Hind', 'Baloo 2', sans-serif;
    }}
    /* Protect all Streamlit default icons and SVG from font overrides */
    svg, svg * {{
        font-family: inherit; 
    }}
    .material-symbols-rounded, .material-symbols-outlined, .material-icons, [class*="icon"] {{
        font-family: 'Material Symbols Rounded', 'Material Symbols Outlined', 'Material Icons' !important;
    }}
    /* --- END SAFE FONT --- */
    

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

.stApp, .block-container {
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
    gap: 7px !important;
}
section[data-testid="stSidebar"] div[role="radiogroup"] > label {
    box-sizing: border-box !important;
    display: flex !important;
    align-items: center !important;
    gap: 10px !important;
    min-height: 40px !important;
    padding: 8px 11px !important;
    margin: 0 !important;
    background: linear-gradient(115deg, rgba(14, 165, 233, 0.09), rgba(37, 99, 235, 0.07)) !important;
    border: 1px solid rgba(56, 189, 248, 0.2) !important;
    border-radius: 12px !important;
    box-shadow: 0 4px 14px rgba(2, 8, 23, 0.16), inset 0 1px rgba(255, 255, 255, 0.025) !important;
    transition: background 180ms ease, border-color 180ms ease, box-shadow 180ms ease, color 180ms ease !important;
    cursor: pointer !important;
    width: 100% !important;
}
section[data-testid="stSidebar"] div[role="radiogroup"] > label:hover {
    background: linear-gradient(115deg, rgba(14, 165, 233, 0.2), rgba(99, 102, 241, 0.16)) !important;
    border-color: rgba(103, 232, 249, 0.75) !important;
    box-shadow: 0 0 0 1px rgba(34, 211, 238, 0.14), 0 0 20px rgba(34, 211, 238, 0.2), inset 0 1px rgba(255, 255, 255, 0.07) !important;
    color: #f0fdff !important;
    transform: translateY(-1px) !important;
}
section[data-testid="stSidebar"] div[role="radiogroup"] > label:has(input:checked) {
    background: linear-gradient(115deg, rgba(14, 165, 233, 0.24), rgba(79, 70, 229, 0.2)) !important;
    border-color: rgba(103, 232, 249, 0.82) !important;
    box-shadow: inset 3px 0 #22d3ee, 0 0 0 1px rgba(34, 211, 238, 0.1), 0 0 18px rgba(34, 211, 238, 0.17) !important;
}
section[data-testid="stSidebar"] div[role="radiogroup"] > label:focus-within {
    outline: 2px solid rgba(103, 232, 249, 0.72) !important;
    outline-offset: 2px !important;
}
section[data-testid="stSidebar"] div[role="radiogroup"] label input[type="radio"] {
    accent-color: #22d3ee !important;
    flex: 0 0 auto !important;
    width: 15px !important;
    height: 15px !important;
    margin: 0 !important;
}
section[data-testid="stSidebar"] div[role="radiogroup"] label p {
    color: #dceafa !important;
    font-size: 11.5px !important;
    font-weight: 650 !important;
    letter-spacing: 0.01em !important;
    line-height: 1.35 !important;
    margin: 0 !important;
    overflow-wrap: anywhere;
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
        border-radius: 12px !important;
        min-height: 40px !important;
        padding: 8px 11px !important;
        gap: 10px !important;
        box-shadow: 0 4px 14px rgba(2, 8, 23, 0.16), inset 0 1px rgba(255, 255, 255, 0.025) !important;
    }
    section[data-testid="stSidebar"] div[data-testid="stRadio"] div[role="radiogroup"] label:has(input[type="radio"]:checked),
    section[data-testid="stSidebar"] div.row-widget.stRadio div[role="radiogroup"] label:has(input[type="radio"]:checked),
    section[data-testid="stSidebar"] div[role="radiogroup"] > label:has(input[type="radio"]:checked) {
        background: linear-gradient(115deg, rgba(14, 165, 233, 0.24), rgba(79, 70, 229, 0.2)) !important;
        border-color: rgba(103, 232, 249, 0.82) !important;
        box-shadow: inset 3px 0 #22d3ee, 0 0 0 1px rgba(34, 211, 238, 0.1), 0 0 18px rgba(34, 211, 238, 0.17) !important;
    }
    section[data-testid="stSidebar"] div[data-testid="stRadio"] div[role="radiogroup"] label input[type="radio"],
    section[data-testid="stSidebar"] div.row-widget.stRadio div[role="radiogroup"] label input[type="radio"] {
        accent-color: #22d3ee !important;
        width: 15px !important;
        height: 15px !important;
        margin: 0 !important;
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

    /* --- SAFE FONT APPLICATION --- */
    .stApp {{
        font-family: 'Plus Jakarta Sans', 'Mukta', 'Hind', 'Baloo 2', sans-serif;
    }}
    h1, h2, h3, h4, h5, h6, p, li, label, .stMarkdown {{
        font-family: 'Plus Jakarta Sans', 'Mukta', 'Hind', 'Baloo 2', sans-serif;
    }}
    /* Protect all Streamlit default icons and SVG from font overrides */
    svg, svg * {{
        font-family: inherit; 
    }}
    .material-symbols-rounded, .material-symbols-outlined, .material-icons, [class*="icon"] {{
        font-family: 'Material Symbols Rounded', 'Material Symbols Outlined', 'Material Icons' !important;
    }}
    /* --- END SAFE FONT --- */
    

    header, [data-testid="stHeader"] {{ display: none !important; }}
    html, body {{
        overflow: {overflow_css} !important;
        height: 100vh !important;
    }}
    [data-testid="stAppViewContainer"], .stApp, section.main, [data-testid="stMain"] {{
        overflow: {overflow_css} !important;
        background:
            radial-gradient(ellipse at 18% 18%, rgba(14, 165, 233, 0.20), transparent 36%),
            radial-gradient(ellipse at 82% 82%, rgba(99, 102, 241, 0.17), transparent 34%),
            linear-gradient(145deg, #07111f 0%, #0a1628 52%, #080e1c 100%) !important;
    }}
    section.main {{
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        min-height: 100vh !important;
        padding: 10px 0 !important;
    }}
    [data-testid="stMainBlockContainer"] {{
        box-sizing: border-box !important;
        width: 90% !important;
        max-width: 460px !important;
        padding: 1.35rem clamp(1.1rem, 5vw, 2rem) !important;
        margin: auto !important;
        background: linear-gradient(145deg, rgba(16, 31, 51, 0.96), rgba(10, 21, 37, 0.95)) !important;
        backdrop-filter: blur(24px) !important;
        border: 1px solid rgba(148, 163, 184, 0.2) !important;
        border-radius: 24px !important;
        box-shadow: 0 30px 80px rgba(0, 0, 0, 0.38), inset 0 1px rgba(255,255,255,0.06) !important;
    }}
    [data-testid="stTextInput"] input {{
        min-height: 44px !important;
        background: rgba(5, 13, 25, 0.72) !important;
        border: 1px solid rgba(148, 163, 184, 0.2) !important;
        border-radius: 11px !important;
    }}
    [data-testid="stTextInput"] input:focus {{
        border-color: rgba(56, 189, 248, 0.75) !important;
        box-shadow: 0 0 0 3px rgba(14, 165, 233, 0.14) !important;
    }}
    .stButton > button, [data-testid="stFormSubmitButton"] > button {{
        min-height: 44px !important;
        border-radius: 11px !important;
        background: linear-gradient(115deg, #0284c7, #2563eb) !important;
        box-shadow: 0 8px 22px rgba(2, 8, 23, 0.3) !important;
    }}
    @media (max-width: 520px) {{
        section.main {{ padding: 12px 0 !important; }}
        [data-testid="stMainBlockContainer"] {{
            width: calc(100% - 24px) !important;
            padding: 1.1rem 1rem !important;
            border-radius: 19px !important;
        }}
    }}
    </style>
    """, unsafe_allow_html=True)
    
    _render_language_toggle()
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
            f_user = st.text_input("Username", placeholder="तुमचा युजरनेम")
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
                            st.error(f"Error: {ex}")
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
                                st.error("Invalid username or password!")
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
                                st.success("मास्टर अॅडमिन Successfully तयार झाला! आता लॉगीन करा.")
                                time.sleep(0.8)
                                st.rerun()
                            except Exception as ex:
                                conn.rollback()
                                st.error(f"Error: {ex}")

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
    st.markdown('''
    <style>
    /* Sleek Sidebar CSS */
    [data-testid="stSidebar"] {
        background: rgba(10, 15, 30, 0.95) !important;
        border-right: 1px solid rgba(0, 242, 254, 0.2);
        overflow: hidden !important;
    }
    [data-testid="stSidebarUserContent"] {
        overflow-y: hidden !important;
        padding-bottom: 0 !important;
    }
    [data-testid="stSidebar"] ::-webkit-scrollbar {
        width: 0px;
        background: transparent;
    }
    .stRadio > div {
        gap: 15px;
    }
    .stRadio label {
        font-size: 16px !important;
        font-weight: 600 !important;
        padding: 10px 15px;
        border-radius: 8px;
        transition: 0.3s;
    }
    /* Red Logout Button */
    /* Red Logout Button by targeting Sidebar Button directly */
    [data-testid="stSidebar"] [data-testid="stButton"] button {
        background: linear-gradient(135deg, #ff4b4b, #dc2626) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: bold !important;
        box-shadow: 0 4px 15px rgba(255, 75, 75, 0.4) !important;
        transition: 0.3s;
        width: 100% !important;
    }
    [data-testid="stSidebar"] [data-testid="stButton"] button:hover {
        transform: scale(1.02) !important;
        box-shadow: 0 6px 20px rgba(255, 75, 75, 0.6) !important;
    }
    
    /* Completely hide scrollbars */
    [data-testid="stSidebar"] {
        overflow: hidden !important;
    }
    [data-testid="stSidebarUserContent"] {
        overflow: hidden !important;
        padding-bottom: 0px !important;
    }
    [data-testid="stSidebar"] > div {
        overflow: hidden !important;
    }
    .os-viewport {
        overflow: hidden !important;
    }
    ::-webkit-scrollbar {
        display: none !important;
        width: 0px !important;
        background: transparent !important;
    }
    
    </style>
    ''', unsafe_allow_html=True)

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

    # KPI Widgets
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        tot_exp = f"{df['grand_total'].sum():,.2f}" if not df.empty else "0.00"
        st.markdown(f"<div class='panel-card' style='margin-bottom:15px;'><div style='font-size:11px; color:#94a3b8; font-weight:700;'>TOTAL REVENUE / SALES</div><div style='font-size: 18px; font-weight:800; color:#00f2fe; margin-top:4px;'>₹{tot_exp}</div></div>", unsafe_allow_html=True)
    with k2:
        tot_rec = len(df) if not df.empty else 0
        st.markdown(f"<div class='panel-card' style='margin-bottom:15px;'><div style='font-size:11px; color:#94a3b8; font-weight:700;'>TOTAL BILLS/ORDERS</div><div style='font-size:18px; font-weight:800; color:#4facfe; margin-top:4px;'>{tot_rec}</div></div>", unsafe_allow_html=True)
    with k3:
        avg_exp = f"{df['grand_total'].mean():,.2f}" if not df.empty else "0.00"
        st.markdown(f"<div class='panel-card' style='margin-bottom:15px;'><div style='font-size:11px; color:#94a3b8; font-weight:700;'>AVG TICKET SIZE</div><div style='font-size:18px; font-weight:800; color:#00ff87; margin-top:4px;'>₹{avg_exp}</div></div>", unsafe_allow_html=True)
    with k4:
        top_v = df.groupby('vendor_name')['grand_total'].sum().idxmax() if not df.empty and 'vendor_name' in df.columns else "N/A"
        st.markdown(f"<div class='panel-card' style='margin-bottom:15px;'><div style='font-size:11px; color:#94a3b8; font-weight:700;'>TOP PERFORMING SHOP</div><div style='font-size:15px; font-weight:800; color:#c084fc; margin-top:4px;'>{top_v[:14]}</div></div>", unsafe_allow_html=True)

    # Quick Cashflow / Udhar Summary (Khatabook Style)
    try:
        dash_khata_df = load_khata_transactions()
        dash_risk_report = build_khata_risk_report(dash_khata_df)
        total_unpaid = dash_risk_report["balance"].sum() if not dash_risk_report.empty else 0.0
        total_collected = dash_khata_df[dash_khata_df["transaction_type"] == KHATA_PAYMENT]["amount"].sum() if not dash_khata_df.empty else 0.0
        total_overdue = dash_risk_report["overdue_balance"].sum() if not dash_risk_report.empty else 0.0
    except Exception:
        total_unpaid = total_collected = total_overdue = 0.0

    st.markdown("##### ⚡ Quick Cashflow / Udhar Summary")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"<div class='panel-card' style='margin-bottom:15px; border-left:4px solid #00ff87;'><div style='font-size:11px; color:#94a3b8; font-weight:700;'>✅ CASH RECOVERED</div><div style='font-size: 18px; font-weight:800; color:#00ff87; margin-top:4px;'>₹{total_collected:,.2f}</div></div>", unsafe_allow_html=True)
    with c2:
        st.markdown(f"<div class='panel-card' style='margin-bottom:15px; border-left:4px solid #f59e0b;'><div style='font-size:11px; color:#94a3b8; font-weight:700;'>⏳ PENDING UDHAR</div><div style='font-size: 18px; font-weight:800; color:#f59e0b; margin-top:4px;'>₹{total_unpaid:,.2f}</div></div>", unsafe_allow_html=True)
    with c3:
        st.markdown(f"<div class='panel-card' style='margin-bottom:15px; border-left:4px solid #ef4444;'><div style='font-size:11px; color:#94a3b8; font-weight:700;'>🚨 OVERDUE (AT RISK)</div><div style='font-size: 18px; font-weight:800; color:#ef4444; margin-top:4px;'>₹{total_overdue:,.2f}</div></div>", unsafe_allow_html=True)


    
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
            if up_files:
                st.markdown("<div style='font-size: 13px; font-weight: 700; color: #00f2fe; margin-bottom: 10px; margin-top: 10px;'>📸 Uploaded Previews:</div>", unsafe_allow_html=True)
                cols = st.columns(min(len(up_files), 5))
                for idx, uf in enumerate(up_files[:5]):
                    cols[idx].image(uf,  caption=f"({idx+1})")
                if len(up_files) > 5:
                    st.markdown(f"<div style='font-size: 12px; color: #94a3b8; font-weight: 600;'>+ {len(up_files)-5} more receipts ready...</div>", unsafe_allow_html=True)
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
                        st.success("व्हॉईस बिल Successfully तयार होऊन डेटाबेसमध्ये सेव्ह झाले !")
                        st.toast("व्हॉईस बिल सेव्ह झाले!", icon="🎤")
                        st.rerun()
                    except Exception as ve:
                        logging.error(f"Voice billing error: {ve}")
                        st.error(f"व्हॉईस बिल Error: {ve}")
                        
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
                import concurrent.futures
                
                def process_single_file(idx, single_file):
                    temp_f = f"temp_{os.urandom(4).hex()}.png"
                    try:
                        with open(temp_f, "wb") as f:
                            f.write(single_file.getbuffer())
                        data = process_receipt_advanced(temp_f, API_KEY, force_save=force_save_option)
                        if os.path.exists(temp_f):
                            os.remove(temp_f)
                        return (idx, data, None)
                    except Exception as e:
                        if os.path.exists(temp_f):
                            os.remove(temp_f)
                        err_str = str(e)
                        return (idx, None, (single_file.name, err_str))

                with st.spinner(f"🚀 AI is processing {total_f} receipts simultaneously... Please wait!"):
                    with concurrent.futures.ThreadPoolExecutor(max_workers=min(total_f, 10)) as executor:
                        futures = {executor.submit(process_single_file, i, f): i for i, f in enumerate(target_files)}
                        
                        results = []
                        completed_count = 0
                        for future in concurrent.futures.as_completed(futures):
                            results.append(future.result())
                            completed_count += 1
                            progress_bar.progress(completed_count / total_f)
                            status_text.text(f"⚡ पावती स्कॅन होत आहे ({completed_count}/{total_f})...")
                            
                        # Sort by original index to maintain order
                        results.sort(key=lambda x: x[0])
                        
                        for idx, data, err in results:
                            if data:
                                processed_batch.append(data)
                            if err:
                                fname, err_str = err
                                if "Duplicate Warning:" in err_str:
                                    clean_err = err_str.split("Duplicate Warning:")[-1].strip()
                                    warning_messages.append(f"⚠️ {fname}: {clean_err}")
                                else:
                                    warning_messages.append(f"❌ {fname}: {err_str}")
                
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
                    st.toast("पावती Successfully स्कॅन झाली!", icon="✅")
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
            if len(batch_data) == 1:
                p_item = batch_data[0]
                v_disp = decode_unicode(p_item.get('vendor_name'))
                tot = p_item.get('grand_total', 0)
                items_raw = p_item.get('items', [])
                
                st.markdown(f"**Shop Name:** {v_disp}")
                st.markdown(f"**Grand Total:** <h2 style='color:#00ff87; margin:0;'>₹{tot:,.2f}</h2>", unsafe_allow_html=True)
                
                import pandas as pd
                items_df = pd.DataFrame(items_raw)
                if not items_df.empty:
                    st.dataframe(items_df, use_container_width=True)
                    
                    if st.button('📦 Auto-Update to Smart Inventory', key='inv_sync_single'):
                        try:
                            import sqlite3
                            with sqlite3.connect('ledger.db') as conn:
                                cursor = conn.cursor()
                                for item in items_raw:
                                    q = str(item.get('qty', '1')).split()[0]
                                    if not q.isdigit(): q = 1
                                    cursor.execute('INSERT INTO shop_inventory (item_name, quantity, unit) VALUES (?, ?, ?)', (item.get('item_name'), float(q), 'units'))
                                conn.commit()
                            st.toast('📦 Stock automatically updated!')
                            st.success('Inventory synced successfully!')
                        except Exception as e: st.error(str(e))
                        
                audio_text = f"{v_disp} कडून खरेदी केलेली पावती. एकूण रक्कम {tot} रुपये."
                aud_path = generate_marathi_tts(audio_text)
                if aud_path and os.path.exists(aud_path):
                    st.audio(aud_path)
            else:
                st.markdown(f"**Processed {len(batch_data)} Receipts Successfully**")
                for idx, p_item in enumerate(batch_data):
                    v_disp = decode_unicode(p_item.get('vendor_name'))
                    tot = p_item.get('grand_total', 0)
                    with st.expander(f"🧾 Receipt #{idx+1} - {v_disp} (₹{tot:,.2f})"):
                        import pandas as pd
                        items_df = pd.DataFrame(p_item.get('items', []))
                        if not items_df.empty:
                            st.dataframe(items_df, use_container_width=True)
                            
                        if st.button('📦 Auto-Update to Smart Inventory', key=f'inv_sync_{idx}'):
                            try:
                                import sqlite3
                                with sqlite3.connect('ledger.db') as conn:
                                    cursor = conn.cursor()
                                    for item in p_item.get('items', []):
                                        q = str(item.get('qty', '1')).split()[0]
                                        if not q.isdigit(): q = 1
                                        cursor.execute('INSERT INTO shop_inventory (item_name, quantity, unit) VALUES (?, ?, ?)', (item.get('item_name'), float(q), 'units'))
                                    conn.commit()
                                st.toast('📦 Stock automatically updated!')
                                st.success('Inventory synced successfully!')
                            except Exception as e: st.error(str(e))
                            
                st.markdown("---")
                st.markdown("#### Marathi Audio Summary")
                vendor_names_list = [decode_unicode(item.get('vendor_name', 'अनामित')) for item in batch_data]
                audio_text = "तुमच्या स्कॅन केलेल्या पावत्यांची दुकाने: " + ", ".join(vendor_names_list)
                aud_path = generate_marathi_tts(audio_text)
                if aud_path and os.path.exists(aud_path):
                    st.audio(aud_path)
                    
            # Instant Invoice Download
            inv_html = f"""
            <html><body style='font-family:sans-serif; padding:20px; color:#333;'>
            <h2 style='color:#0ea5e9;'>INVOICE - {v_disp}</h2>
            <hr>
            <table width='100%' cellpadding='8' style='border-collapse:collapse; text-align:left;'>
                <tr style='background:#f1f5f9;'><th>Item Name</th><th>Quantity</th><th>Price</th><th>Total</th></tr>
            """
            for itm in items_raw:
                inv_html += f"<tr><td style='border-bottom:1px solid #e2e8f0;'>{itm.get('item_name')}</td><td style='border-bottom:1px solid #e2e8f0;'>{itm.get('qty')}</td><td style='border-bottom:1px solid #e2e8f0;'>₹{itm.get('price')}</td><td style='border-bottom:1px solid #e2e8f0;'>₹{itm.get('total_price')}</td></tr>"
            inv_html += f"</table><h3 style='text-align:right; margin-top:20px;'>Grand Total: ₹{tot:,.2f}</h3></body></html>"
            
            st.download_button(
                label="📄 Download Invoice (PDF/HTML)",
                data=inv_html,
                file_name=f"Invoice_{v_disp.replace(' ', '_')}.html",
                mime="text/html",
                
                type="primary"
            )

            st.markdown("---")
            st.markdown("#### Marathi Audio Summary")
            aud_path = generate_marathi_tts(f"{v_disp} कडील पावतीची एकूण रक्कम रुपये {tot} आहे.")
            if aud_path and os.path.exists(aud_path):
                st.audio(aud_path)
        else:
            st.caption("Scan receipt(s) or use Multi-Language Voice Bill to display extracted items & summary.")
        st.markdown("</div>", unsafe_allow_html=True)

# FEATURE 3: ADVANCED CUSTOMER KHATA ---
elif selected_page == "Customer Khata":
    render_customer_khata()

# FEATURE 4: STOCK & INVENTORY ---
elif selected_page == "Stock & Inventory":
    if st.session_state.get('user_role') == 'Staff':
        st.error("प्रतिबंधीत क्षेत्रः कामागार/स्टाफला इन्व्हेंटरी पेजवर प्रवेश करण्याची परवानगी नाही!")
        st.stop()
    render_business_module_styles()
    st.markdown("""
    <div class="studio-header business-module-hero">
        <div class="business-hero-content">
            <div class="business-eyebrow">✦ BUSINESS MODULES · INVENTORY</div>
            <h2 class="business-hero-title">Stock & <span>Inventory</span></h2>
            <p class="business-hero-subtitle">उपलब्ध माल, कमी साठा आणि वस्तूंची स्थिती एका नजरेत.</p>
        </div>
        <div class="business-hero-mark" aria-hidden="true">▦</div>
    </div>
    """, unsafe_allow_html=True)
    ic1, ic2 = st.columns([1, 1])
    with ic1:
        st.markdown("<div class='panel-card'>", unsafe_allow_html=True)
        st.markdown("""
        <div class="business-section-heading">
            <div class="business-section-icon">＋</div>
            <div><h3 class="business-section-title">Add New Stock</h3>
            <p class="business-section-caption">वस्तूचे नाव, प्रमाण आणि कमी-साठा मर्यादा भरा.</p></div>
        </div>
        """, unsafe_allow_html=True)
        with st.form("stock_form"):
            s_name = st.text_input("Item Name")
            s_qty = st.number_input("Stock Quantity", min_value=0.0, step=1.0)
            s_unit = st.text_input("Unit (e.g. kg, pcs, ltr)", value="kg")
            s_limit = st.number_input("Low Stock Alert Limit", min_value=0.0, step=1.0, value=5.0)
            submit_stock = st.form_submit_button("Save Stock")
            if submit_stock:
                if not s_name.strip():
                    st.error("Please enter item name!")
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
                        st.success(f"Stock '{s_name}' successfully added!")
                        st.rerun()
                    except Exception as ex:
                        st.error(f"Error: {ex}")
        st.markdown("</div>", unsafe_allow_html=True)
    with ic2:
        st.markdown("<div class='panel-card'>", unsafe_allow_html=True)
        st.markdown("""
        <div class="business-section-heading">
            <div class="business-section-icon">▤</div>
            <div><h3 class="business-section-title">साठ्याचा आढावा</h3>
            <p class="business-section-caption">वस्तूंची यादी आणि पुन्हा मागवायच्या वस्तू.</p></div>
        </div>
        """, unsafe_allow_html=True)
        try:
            with sqlite3.connect("ledger.db") as conn:
                stock_df = pd.read_sql_query("SELECT * FROM shop_inventory", conn)
        except Exception:
            stock_df = pd.DataFrame()
            
        if not stock_df.empty:
            low_stock_items = stock_df[stock_df['stock_qty'] <= stock_df['alert_limit']]
            stock_metric1, stock_metric2 = st.columns(2)
            with stock_metric1:
                st.markdown(
                    f"""
                    <div class="business-metric-card" style="margin-bottom:14px;">
                        <div class="business-metric-label">एकूण वस्तू</div>
                        <div class="business-metric-value">{len(stock_df)}</div>
                        <div class="business-metric-note">नोंदवलेल्या इन्व्हेंटरी आयटम्स</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            with stock_metric2:
                low_color = "#fca5a5" if not low_stock_items.empty else "#86efac"
                st.markdown(
                    f"""
                    <div class="business-metric-card" style="margin-bottom:14px;">
                        <div class="business-metric-label">कमी साठा</div>
                        <div class="business-metric-value" style="color:{low_color};">{len(low_stock_items)}</div>
                        <div class="business-metric-note">मर्यादेपेक्षा कमी किंवा समान</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            display_df = stock_df.copy()
            display_df.insert(0, 'Status', display_df.apply(lambda row: "🚨 Low Stock" if row['stock_qty'] <= row['alert_limit'] else "✅ In Stock", axis=1))
            st.dataframe(display_df,  hide_index=True)
            if not low_stock_items.empty:
                low_names = ", ".join(low_stock_items['item_name'].tolist())
                st.markdown(f"""
                <div style="background: rgba(239, 68, 68, 0.15); border: 1px solid rgba(239, 68, 68, 0.4); padding: 12px; border-radius: 12px; margin-top: 14px; color: #f87171;">
                    <b>लो स्टॉक वार्निंग (Low Stock Alert):</b> खालील वस्तू संपत आल्या आहेत: <b>{low_names}</b>
                </div>
                """, unsafe_allow_html=True)
            del_s_id = st.number_input("डिलिट करण्यासाठी स्टॉक ID", min_value=1, step=1, key="del_stock_id")
            if st.button("Delete Stock Item"):
                try:
                    with sqlite3.connect("ledger.db") as conn:
                        conn.execute("BEGIN TRANSACTION;")
                        cursor = conn.cursor()
                        cursor.execute("DELETE FROM shop_inventory WHERE id=?", (del_s_id,))
                        conn.commit()
                    log_activity(st.session_state.get('current_username', 'admin'), f"Deleted Stock ID {del_s_id}")
                    st.success(f"Stock ID {del_s_id} deleted!")
                    st.rerun()
                except Exception as ex:
                    st.error(f"Error: {ex}")
        else:
            st.info("कोणताही स्टॉक जोडलेला नाही.")
        st.markdown("</div>", unsafe_allow_html=True)

# FEATURE 5: BUSINESS EXPENSES TRACKER ---
elif selected_page == "Business Expenses":
    if st.session_state.get('user_role') == 'Staff':
        st.error("प्रतिबंधीत क्षेत्रः कामागार/स्टाफला व्यवसाय खर्च पेजवर प्रवेश करण्याची परवानगी नाही!")
        st.stop()
    render_business_module_styles()
    st.markdown("""
    <div class="studio-header business-module-hero">
        <div class="business-hero-content">
            <div class="business-eyebrow">✦ BUSINESS MODULES · EXPENSES</div>
            <h2 class="business-hero-title">व्यवसाय खर्च <span>· नोंदवही</span></h2>
            <p class="business-hero-subtitle">भाडे, वीज, पगार आणि रोजच्या खर्चांचा स्पष्ट हिशोब.</p>
        </div>
        <div class="business-hero-mark" aria-hidden="true">₹</div>
    </div>
    """, unsafe_allow_html=True)
    ec1, ec2 = st.columns([1, 1])
    with ec1:
        st.markdown("<div class='panel-card'>", unsafe_allow_html=True)
        st.markdown("""
        <div class="business-section-heading">
            <div class="business-section-icon">＋</div>
            <div><h3 class="business-section-title">Record New Expense</h3>
            <p class="business-section-caption">खर्चाचा प्रकार, रक्कम आणि तारीख नोंदवा.</p></div>
        </div>
        """, unsafe_allow_html=True)
        with st.form("expense_form"):
            e_title = st.text_input("खर्चाचे शीर्षक (Expense Title e.g. Light Bill)")
            e_amount = st.number_input("Expense Amount", min_value=0.0, step=50.0)
            e_cat = st.selectbox("खर्चाचा प्रकार (Category)", ["Shop Rent", "वीज बिल (Electricity)", "कर्मचारी पगार (Staff Salary)", "Transport", "Miscellaneous"])
            e_date = st.text_input("Date", value=time.strftime("%Y-%m-%d"))
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
                        st.success(f"Expense '{e_title}' successfully recorded!")
                        st.rerun()
                    except Exception as ex:
                        st.error(f"Error: {ex}")
        st.markdown("</div>", unsafe_allow_html=True)
    with ec2:
        st.markdown("<div class='panel-card'>", unsafe_allow_html=True)
        st.markdown("""
        <div class="business-section-heading">
            <div class="business-section-icon">▤</div>
            <div><h3 class="business-section-title">खर्चाचा आढावा</h3>
            <p class="business-section-caption">नोंदवलेले व्यवहार आणि एकूण खर्च.</p></div>
        </div>
        """, unsafe_allow_html=True)
        try:
            with sqlite3.connect("ledger.db") as conn:
                exp_df = pd.read_sql_query("SELECT * FROM business_expenses ORDER BY id DESC", conn)
        except Exception:
            exp_df = pd.DataFrame()
        if not exp_df.empty:
            total_expenses = exp_df['amount'].sum()
            st.markdown(f"""
            <div class="business-metric-card" style="margin-bottom:14px;">
                <div class="business-metric-label">एकूण व्यवसाय खर्च</div>
                <div class="business-metric-value" style="color:#fca5a5;">₹ {total_expenses:,.2f}</div>
                <div class="business-metric-note">{len(exp_df)} खर्च नोंदी</div>
            </div>
            """, unsafe_allow_html=True)
            st.dataframe(exp_df, use_container_width=True)
            del_exp_id = st.number_input("Expense ID to delete", min_value=1, step=1, key="del_exp_id")
            if st.button("Delete Expense Record"):
                try:
                    with sqlite3.connect("ledger.db") as conn:
                        conn.execute("BEGIN TRANSACTION;")
                        cursor = conn.cursor()
                        cursor.execute("DELETE FROM business_expenses WHERE id=?", (del_exp_id,))
                        conn.commit()
                    log_activity(st.session_state.get('current_username', 'admin'), f"Deleted Expense ID {del_exp_id}")
                    st.success(f"Expense ID {del_exp_id} deleted!")
                    st.rerun()
                except Exception as ex:
                    st.error(f"Error: {ex}")
        else:
            st.info("No expenses recorded.")
        st.markdown("</div>", unsafe_allow_html=True)

# FEATURE 6: ADMIN STAFF MANAGEMENT ---
elif selected_page == "Staff Management":
    if st.session_state.get('user_role') == 'Staff':
        st.error("Restricted Area: Staff not allowed on Staff Management page!")
        st.stop()
    st.markdown("""
    <div class="studio-header">
        <div>
            <h2 style="margin:0; font-size: 22px; font-weight: 800; color: #00f2fe;">Admin Staff Management & Audit Logs</h2>
            <p style="margin:4px 0 0 0; font-size: 12px; color: #94a3b8; font-weight: 600;">Create Staff Accounts & View Complete System Activity Audit Trail</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    tab_st1, tab_st2 = st.tabs(["Staff Management", "System Audit Logs"])
    with tab_st1:
        sc1, sc2 = st.columns([1, 1])
        with sc1:
            st.markdown("<div class='panel-card'>", unsafe_allow_html=True)
            st.markdown("<h4 style='color:#00f2fe; margin-top:0;'>नवीन स्टाफ किंवा अॅडमिन जोडा</h4>", unsafe_allow_html=True)
            with st.form("new_staff_form"):
                s_user = st.text_input("Username")
                s_phone = st.text_input("Phone Number")
                s_pass = st.text_input("Password (Min 6 digits)", type="password")
                s_role = st.selectbox("Role", ["Staff (Cashier - Limited Access)", "Admin (Owner - Full Access)"])
                submit_new_user = st.form_submit_button("Create Account")
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
                            st.success(f"नवीन '{role_val}' अकाऊंट ({s_user}) Successfully तयार झाले!")
                            st.rerun()
                        except Exception as ex:
                            st.error(f"Error: हा युजरनेम आधीपासून अस्तित्वात आहे किंवा डेटाबेस त्रुटी.")
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
                            st.success(f"User '{del_uname}' successfully deleted!")
                            st.rerun()
                        except Exception as ex:
                            st.error(f"Error: {ex}")
            except Exception as e:
                st.error(f"Error loading data: {e}")
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
                        st.success("नवीन रो Successfully जोडली गेली!")
                        st.rerun()
                    except Exception as ex:
                        st.error(f"Error: {ex}")
            
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
            
            edited_sheet_df = st.data_editor(sheet_preview_df,  key="ledger_checkbox_table")
            
            selected_ids = edited_sheet_df[edited_sheet_df['Select'] == True]['id'].tolist()
            if selected_ids:
                if st.button(f"🗑️ निवडलेले records डिलीट करा ({len(selected_ids)})", type="primary", use_container_width=True):
                    try:
                        with sqlite3.connect("ledger.db") as conn:
                            conn.execute("BEGIN TRANSACTION;")
                            cursor = conn.cursor()
                            for s_id in selected_ids:
                                cursor.execute("DELETE FROM receipts WHERE id = ?", (s_id,))
                            conn.commit()
                        log_activity(st.session_state.get('current_username', 'admin'), f"Deleted Receipt IDs via checkbox: {selected_ids}")
                        st.success(f"Successfully {len(selected_ids)} रेकॉर्ड deleted!")
                        st.rerun()
                    except Exception as ex:
                        st.error(f"Error: {ex}")
                
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
        st.markdown("<div class='panel-card'>", unsafe_allow_html=True)
        st.info("Ledger database is empty.")
        st.markdown("</div>", unsafe_allow_html=True)

# FEATURE 8: RAG AI CHATBOT ---
elif selected_page == "RAG AI Chat":
    st.markdown("""
<style>

    /* --- SAFE FONT APPLICATION --- */
    .stApp {{
        font-family: 'Plus Jakarta Sans', 'Mukta', 'Hind', 'Baloo 2', sans-serif;
    }}
    h1, h2, h3, h4, h5, h6, p, li, label, .stMarkdown {{
        font-family: 'Plus Jakarta Sans', 'Mukta', 'Hind', 'Baloo 2', sans-serif;
    }}
    /* Protect all Streamlit default icons and SVG from font overrides */
    svg, svg * {{
        font-family: inherit; 
    }}
    .material-symbols-rounded, .material-symbols-outlined, .material-icons, [class*="icon"] {{
        font-family: 'Material Symbols Rounded', 'Material Symbols Outlined', 'Material Icons' !important;
    }}
    /* --- END SAFE FONT --- */
    

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
[data-testid="stMainBlockContainer"] {
    box-sizing: border-box !important;
    width: min(100%, 960px) !important;
    max-width: 960px !important;
    min-width: 0 !important;
    margin-inline: auto !important;
    padding: clamp(1rem, 3vw, 2rem) clamp(1rem, 3vw, 1.5rem) 9rem !important;
    overflow-x: clip !important;
}
[data-testid="stHorizontalBlock"],
[data-testid="stColumn"] {
    box-sizing: border-box !important;
    min-width: 0 !important;
}
body:has(.verna-ai-heading) [data-testid="stAppViewContainer"] {
    max-width: 100vw !important;
    overflow-x: clip !important;
}
body:has(.verna-ai-heading) [data-testid="stHorizontalBlock"] [data-testid="stCheckbox"] {
    display: flex !important;
    width: 100% !important;
    justify-content: center !important;
}
body:has(.verna-ai-heading) [data-testid="stHorizontalBlock"] [data-testid="stElementContainer"]:has([data-testid="stCheckbox"]) {
    width: 100% !important;
}
.verna-ai-title {
    margin: 0;
    padding: 0 !important;
    color: #d9fbff;
    font-size: clamp(2rem, 5vw, 3.25rem);
    font-weight: 800;
    letter-spacing: -0.045em;
    line-height: 1.12;
    text-align: center;
    text-shadow:
        0 0 10px rgba(34, 211, 238, 0.82),
        0 0 26px rgba(34, 211, 238, 0.5),
        0 0 48px rgba(139, 92, 246, 0.42);
}
.verna-ai-heading {
    display: flex;
    width: 100%;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 0.35rem;
    margin: 0.2rem 0 1.25rem;
    text-align: center;
}
.verna-ai-subtitle {
    margin: 0;
    color: #aab8ca;
    font-size: 0.9rem;
    font-weight: 500;
    letter-spacing: 0.015em;
    text-align: center;
}
.verna-ai-greeting {
    box-sizing: border-box;
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
.st-key-rag_chat_history {
    box-sizing: border-box;
    display: flex;
    width: min(100%, 760px) !important;
    max-width: 100% !important;
    flex-direction: column;
    align-items: center;
    margin: 0 auto !important;
}
.st-key-rag_chat_history [data-testid="stChatMessage"] {
    box-sizing: border-box;
    width: 100%;
    align-self: center;
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
    width: min(760px, calc(100vw - 2rem)) !important;
    max-width: 100% !important;
    margin: 0 !important;
    padding: 0 !important;
    z-index: 20 !important;
}
body:has(section[data-testid="stSidebar"][aria-expanded="true"]) [data-testid="stCustomComponentV1"] {
    left: calc(50% + 9.375rem) !important;
    width: min(760px, calc(100vw - 18.75rem - 2rem)) !important;
}
main.block-container {
    padding-bottom: 9rem !important;
}
@media (max-width: 900px) and (min-width: 641px) {
    body:has(section[data-testid="stSidebar"][aria-expanded="true"]) [data-testid="stCustomComponentV1"] {
        left: calc(50% + 9rem) !important;
        width: min(760px, calc(100vw - 18rem - 3rem)) !important;
    }
}
@media (max-width: 640px) {
    [data-testid="stMainBlockContainer"] {
        width: 100% !important;
        max-width: 100% !important;
        padding: 1rem 0.8rem 8rem !important;
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
        left: 50% !important;
        bottom: max(0.55rem, env(safe-area-inset-bottom)) !important;
        width: calc(100vw - 1.25rem) !important;
    }
    body:has(section[data-testid="stSidebar"][aria-expanded="true"]) [data-testid="stCustomComponentV1"] {
        left: 50% !important;
        width: calc(100vw - 1.25rem) !important;
    }
    main.block-container {
        padding-bottom: 8rem !important;
    }
}
</style>
""", unsafe_allow_html=True)

    st.markdown("""
<div class="verna-ai-heading">
  <h1 class="verna-ai-title">Verna AI Studio</h1>
  <p class="verna-ai-subtitle">Your Smart Ledger &amp; Business Assistant</p>
</div>
""", unsafe_allow_html=True)
    _, toggle_col, _ = st.columns([1, 2, 1])
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
    <h1 style="font-size:40px; margin-bottom:5px;">✨ Verna AI</h1><p style="color:#00f2fe; font-size:16px;">Hello! Ask me anything about your shop ledger, stock, or expenses.</p>
  </div>
</section>
""", unsafe_allow_html=True)

        for idx, chat in enumerate(st.session_state["chat_history"]):
            message_role = "user" if chat["role"] == "user" else "assistant"
            with st.chat_message(message_role, avatar='\U0001f916' if message_role == 'assistant' else '\U0001f464'):
                _streamlit_ui.markdown(chat["text"])
                if enable_voice_output and chat.get("audio_file") and os.path.exists(chat["audio_file"]):
                    st.audio(chat["audio_file"], autoplay=(idx == len(st.session_state["chat_history"])-1))

    chat_input_event = CHAT_INPUT_COMPONENT(
        key="verna_chat_input_component",
        default=None,
        language=st.session_state.get("ui_language", "mr"),
    )
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
        target_prompt = voice_captured
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
            try:
                phone_match = re.search(r"(?<!\d)[6-9]\d{9}(?!\d)", last_user_msg)
                phone = phone_match.group(0) if phone_match else ""
                amount_text = last_user_msg.replace(phone, "") if phone else last_user_msg
                amount_matches = re.findall(r"\d+(?:[.,]\d+)?", amount_text)
                amount = float(amount_matches[0].replace(",", "")) if amount_matches else 0
                ignored_terms = {
                    "उधारी", "जोड", "जोडा", "लिही", "लिहा", "खात्यात", "नोंदव",
                    "नोंदवा", "नोंद", "सेव्ह", "करा", "कडे", "साठी", "रुपये", "रुपया",
                    "रु", "₹", "credit", "add", "record", "please", "payment", "जमा",
                    "हप्ता", "पैसे",
                }
                customer_parts = [
                    re.sub(r"^[.,!?;:]+|[.,!?;:]+$", "", word)
                    for word in amount_text.split()
                    if not re.search(r"\d", word) and word.casefold() not in ignored_terms
                ]
                customer_name = " ".join(part for part in customer_parts if part)
                transaction_type = (
                    KHATA_PAYMENT
                    if any(term in last_user_msg.casefold() for term in ("हप्ता", "जमा", "payment"))
                    else KHATA_CREDIT
                )
                if not customer_name or not amount_matches:
                    action_status_msg = (
                        "उधारी नोंद सेव्ह झाली नाही. कृपया ग्राहकाचे नाव आणि वैध रक्कम "
                        "स्पष्टपणे द्या; किंवा Customer Khata फॉर्म वापरा."
                    )
                else:
                    record_id = save_khata_transaction(
                        customer_name, phone, amount, transaction_type,
                        date.today(), date.today(), last_user_msg,
                    )
                    action_status_msg = (
                        f"Customer Khata मध्ये {customer_name} साठी रुपये {amount:,.2f} "
                        f"ची नोंद सेव्ह झाली (रेकॉर्ड {record_id})."
                    )
            except ValueError as exc:
                action_status_msg = f"उधारी नोंद सेव्ह झाली नाही: {exc}"
            except sqlite3.Error as exc:
                logging.exception("Could not save khata transaction from AI chat")
                action_status_msg = f"डेटाबेसमध्ये उधारी नोंद सेव्ह करता आली नाही: {exc}"

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
            "You are an intelligent AI assistant for VernaLedger AI. Detect the language of "
            "the latest user query automatically and respond strictly in that same language: "
            "English queries, including Romanized English, require professional, clear English; "
            "Marathi queries require natural, grammatically correct Marathi; Hindi queries "
            "require fluent Hindi. Do not translate the query or answer into another language "
            "and do not use a default language."
        )
        assistant_instruction = (
            "Choose how to answer based on the user's intent. For questions about VernaLedger AI, "
            "project details, people and ownership, or ledger records such as receipts, credit, "
            "expenses, and stock, use the supplied reference context as the source of truth. "
            "Do not invent internal project facts or database values. If a requested internal "
            "fact is absent from the supplied context, say that it is not present in the "
            "available context instead of guessing. The database context contains at most the "
            "five most recent rows for each listed ledger table, so do not imply it is a complete "
            "database search. For unrelated general-knowledge questions (including science, "
            "history, coding, and general facts), answer helpfully using your general knowledge; "
            "do not require the answer to appear in the project database. If a question combines "
            "both, use the supplied context for project-specific facts and general knowledge "
            "for the rest. Always follow the response-language instruction."
        )
        generation_config = {
            "temperature": 0.3,
            "max_output_tokens": 1024,
        }
        rag_context = f"""
        The following are reference facts only. They do not set the response language.

        [Reference context]:
        - Lead Developer: संकेत किर्दत
        - Project Guide: कैसर अतार सर
        - Developers: साक्षी भगत, वैष्णवी ढवळे, ऋषिकेश मुळीक.
        - College: Arvind Gavali College of Engineering, Satara.
        - Database Context:
        {db_context}
        - Database Action Result:
        {action_status_msg or "No database action was performed."}
        
        [Recent conversation context]:
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
                        system_instruction=f"{language_instruction}\n\n{assistant_instruction}",
                        generation_config=generation_config,
                    )
                    response_stream = model.generate_content(
                        [rag_context, f"[Latest user query — answer this query]\n{last_user_msg}"],
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
            devanagari_count = len(re.findall(r"[\u0900-\u097f]", audio_text))
            if devanagari_count:
                audio_text = re.sub(r"\s*[\(\[][A-Za-z][^\)\]]*[\)\]]", "", audio_text)

            tts_voice = get_tts_voice(audio_text)
            if tts_voice.startswith("mr-"):
                audio_text = re.sub(r"\bAI\b", "ए आय", audio_text, flags=re.IGNORECASE)
                pronunciation_hints = {
                    "वैष्णवी ढवळे": "वैष्णवी ढव्-ळे",
                    "ढवाळे": "ढव्-ळे",
                    "ढवळे": "ढव्-ळे",
                    "गवाली": "गव्-ळी",
                    "गवळी": "गव्-ळी",
                    "कैसर": "कै-सर",
                    "कौसर": "कै-सर",
                }
                for name, pronunciation in pronunciation_hints.items():
                    audio_text = audio_text.replace(name, pronunciation)
                audio_text = re.sub(r"\bGavali\b", "गव्-ळी", audio_text, flags=re.IGNORECASE)

            audio_text = re.sub(r"[ \t]+", " ", audio_text)
            audio_text = re.sub(r" *([,;:]) *", r"\1 ", audio_text)
            audio_text = re.sub(r" *([.!?।]) *", r"\1 ", audio_text)
            audio_text = re.sub(r"\s*\n\s*", ". ", audio_text).strip()
            audio_file_path = generate_marathi_tts(audio_text, voice=tts_voice)

        st.session_state["chat_history"].append({
            "role": "ai",
            "text": clean_ans,
            "audio_file": audio_file_path
        })
        st.rerun()