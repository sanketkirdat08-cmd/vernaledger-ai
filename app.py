import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import sqlite3
import os
import base64
import json
import hashlib
import shutil
import concurrent.futures
from io import BytesIO
import time
import re
import urllib.parse
import logging
import math
from datetime import date, datetime, timedelta
from html import escape
import google.generativeai as genai
from ocr_engine import (
    generate_marathi_tts,
    get_active_gemini_models,
    process_receipt_advanced,
    process_voice_billing_advanced,
)
from streamlit_mic_recorder import speech_to_text
try:
    import qrcode
except ImportError:
    qrcode = None

try:
    import cv2
except ImportError:
    cv2 = None

try:
    import numpy as np
except ImportError:
    np = None

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
def sync_local_storage():
    lang = st.session_state.get("ui_language", "en")
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



# --- SECURE HASHING & DATABASE STRUCTURE ---
def hash_password_secure(password):
    return hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), b'salt_verna_bcrypt_layer', 100000).hex()

# -- ADVANCED DATABASE SETUP WITH ACID TRANSACTIONS ---
@st.cache_resource(show_spinner=False)
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
            conn.execute("PRAGMA journal_mode = WAL;")
            conn.execute("PRAGMA synchronous = NORMAL;")
            conn.execute("PRAGMA cache_size = -64000;")
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
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)")
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
                alert_limit REAL,
                barcode TEXT DEFAULT '',
                selling_price REAL DEFAULT 0.0
            )
            """)
            try:
                cursor.execute("ALTER TABLE shop_inventory ADD COLUMN barcode TEXT DEFAULT ''")
            except Exception:
                pass
            try:
                cursor.execute("ALTER TABLE shop_inventory ADD COLUMN selling_price REAL DEFAULT 0.0")
            except Exception:
                pass
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_stock_name ON shop_inventory(item_name)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_stock_barcode ON shop_inventory(barcode)")

            cursor.execute("""
            CREATE TABLE IF NOT EXISTS shop_settings (
                key TEXT PRIMARY KEY,
                value TEXT
            )
            """)

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
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_expenses_date ON business_expenses(date)")

            cursor.execute("""
            CREATE TABLE IF NOT EXISTS stock_inward_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_id INTEGER,
                item_name TEXT,
                barcode TEXT,
                quantity_added REAL,
                new_stock REAL,
                timestamp TEXT,
                added_by TEXT
            )
            """)
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_inward_time ON stock_inward_logs(timestamp)")
            conn.commit()
        except Exception as e:
            conn.rollback()
            logging.error(f"Database initialization transaction failed: {e}")

init_databases()

def get_shop_setting(key: str, default: str = "") -> str:
    try:
        with sqlite3.connect("ledger.db") as conn:
            cur = conn.cursor()
            cur.execute("SELECT value FROM shop_settings WHERE key = ?", (key,))
            row = cur.fetchone()
            if row and row[0] is not None and str(row[0]).strip():
                return str(row[0]).strip()
    except Exception:
        pass
    return default

def set_shop_setting(key: str, value: str) -> None:
    try:
        with sqlite3.connect("ledger.db") as conn:
            cur = conn.cursor()
            cur.execute("CREATE TABLE IF NOT EXISTS shop_settings (key TEXT PRIMARY KEY, value TEXT)")
            cur.execute("INSERT OR REPLACE INTO shop_settings (key, value) VALUES (?, ?)", (key, str(value).strip()))
            conn.commit()
    except Exception as e:
        ai_logger.error(f"Failed to set shop setting {key}: {e}")


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
    custom_upi = get_shop_setting("shop_upi_id", "")
    if custom_upi:
        return custom_upi
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
        secret_value or environment_value or "vernaledger@upi"
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
                "overdue_days_max": 0,
                "last_tx_date": None,
                "tx_count": 0,
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

        customer["tx_count"] += 1
        tx_date_str = str(record.get("date") or "")
        if tx_date_str:
            try:
                tx_d = datetime.strptime(tx_date_str, "%Y-%m-%d").date()
                if not customer["last_tx_date"] or tx_d > customer["last_tx_date"]:
                    customer["last_tx_date"] = tx_d
            except Exception:
                pass

        if record.get("transaction_type") == KHATA_CREDIT:
            customer["credit"] += amount
            try:
                due_date = datetime.strptime(str(record.get("due_date")), "%Y-%m-%d").date()
            except (TypeError, ValueError):
                due_date = None
            if due_date and due_date < today:
                customer["overdue_credit"] += amount
                days_diff = (today - due_date).days
                if days_diff > customer["overdue_days_max"]:
                    customer["overdue_days_max"] = days_diff
        elif record.get("transaction_type") == KHATA_PAYMENT:
            customer["payments"] += amount

    report = []
    for customer in customers.values():
        balance = customer["credit"] - customer["payments"]
        overdue_balance = min(max(balance, 0.0), customer["overdue_credit"])
        overdue_days = customer["overdue_days_max"] if overdue_balance > 0 else 0
        repayment_ratio = (customer["payments"] / customer["credit"]) if customer["credit"] > 0 else (1.0 if balance <= 0 else 0.0)

        risk_score = 0
        if balance > 0:
            exposure_pts = min(int(balance / 150), 35)
            overdue_pts = 0
            if overdue_balance > 0:
                if overdue_days > 60:
                    overdue_pts = 45
                elif overdue_days > 30:
                    overdue_pts = 35
                elif overdue_days > 14:
                    overdue_pts = 25
                else:
                    overdue_pts = 15

            if repayment_ratio == 0:
                repay_pts = 20
            elif repayment_ratio < 0.25:
                repay_pts = 12
            elif repayment_ratio < 0.50:
                repay_pts = 5
            else:
                repay_pts = -10

            risk_score = max(5, min(100, 15 + exposure_pts + overdue_pts + repay_pts))
        else:
            risk_score = 0

        if risk_score >= 70:
            risk_level = "High Risk (बिकट उधारी)"
            risk_tier = "High"
            ai_recommendation_mr = (
                f"🚨 तातडीने प्रत्यक्ष भेट द्या किंवा कडक नोटीस पाठवा. {overdue_days} दिवस थकीत आहेत. "
                "जोपर्यंत ही बाकी जमा होत नाही तोपर्यंत पुढील कोणतीही उधारी देणे त्वरित थांबवा!"
            )
            ai_recommendation_en = (
                f"🚨 Immediate action required. Payment overdue by {overdue_days} days. "
                "Halt all further credit sales immediately until this past-due balance is settled."
            )
        elif risk_score >= 40:
            risk_level = "Moderate Risk (मध्यम जोखीम)"
            risk_tier = "Moderate"
            ai_recommendation_mr = (
                "⚠️ पेमेंट आठवण व थेट UPI लिंक पाठवा. नवीन माल देण्यापूर्वी किमान ५०% रक्कम तातडीने वसूल करा."
            )
            ai_recommendation_en = (
                "⚠️ Send payment reminder with UPI link. Request at least 50% partial repayment before issuing new credit."
            )
        else:
            risk_level = "Safe Customer (सुरक्षित ग्राहक)"
            risk_tier = "Safe"
            ai_recommendation_mr = (
                "✅ चांगला आणि विश्वासू ग्राहक. नियमित व्यवहार चालू ठेवा. सौम्य आठवण किंवा धन्यवाद संदेश पाठवू शकता."
            )
            ai_recommendation_en = (
                "✅ Trusted customer with safe repayment history. Safe to maintain standard credit terms."
            )

        report.append(
            {
                **customer,
                "balance": balance,
                "overdue_balance": overdue_balance,
                "overdue_days": overdue_days,
                "repayment_ratio": repayment_ratio,
                "risk_score": risk_score,
                "risk_level": risk_level,
                "risk_tier": risk_tier,
                "ai_rec_mr": ai_recommendation_mr,
                "ai_rec_en": ai_recommendation_en,
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
        background: linear-gradient(150deg, rgba(15, 23, 42, 0.85), rgba(9, 9, 11, 0.75)) !important;
        backdrop-filter: blur(16px) !important;
        border: 1px solid rgba(56, 189, 248, 0.18) !important;
        border-radius: 20px !important;
        box-shadow: 0 15px 35px rgba(0, 0, 0, 0.4), inset 0 1px 0 rgba(255,255,255,0.05), inset 0 -1px 2px rgba(14,165,233,0.05) !important;
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


def render_page_header(title, subtitle, icon="✨"):
    st.markdown(f"""
    <div style="
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 14px 20px;
        background: linear-gradient(135deg, rgba(15, 23, 42, 0.9) 0%, rgba(13, 19, 33, 0.8) 100%);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(0, 242, 254, 0.25);
        border-radius: 14px;
        margin-bottom: 20px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3), inset 0 1px 1px rgba(255, 255, 255, 0.05);
    ">
        <div>
            <h2 style="margin: 0; font-size: 18px; font-weight: 800; color: #00f2fe; letter-spacing: normal;">{title}</h2>
            <p style="margin: 4px 0 0 0; font-size: 12px; color: #94a3b8; font-weight: 600; line-height: 1.4;">{subtitle}</p>
        </div>
        <div style="font-size: 26px; filter: drop-shadow(0 2px 4px rgba(0,242,254,0.3));">{icon}</div>
    </div>
    """, unsafe_allow_html=True)

def render_customer_khata():
    # Staff can now access this

    render_page_header("Customer Khata - Credit Ledger", "ग्राहकांची उधारी, जमा हप्ते आणि AI जोखीम व्यवस्थापन.", "📖")
    tab1, tab2 = st.tabs(["➕ नवीन उधारी / हप्ता नोंद (New Entry)", "📊 क्रेडिट लेजर & AI रिस्क रिपोर्ट (Ledger & Risk)"])

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

        with st.expander("🎙️ बोलून किंवा AI मजकुराद्वारे नोंद भरा (पर्यायी - Optional)", expanded=False):
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
                st.caption(f"व्हॉईस रेकॉर्डिंग उपलब्ध नाही: {exc}")
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
        try:
            khata_df = load_khata_transactions()
        except sqlite3.Error as exc:
            logging.exception("Could not load customer khata transactions")
            st.error(f"लेजर डेटा वाचता आला नाही: {exc}")
            khata_df = pd.DataFrame(columns=KHATA_COLUMNS)

        risk_report = build_khata_risk_report(khata_df)
        amounts = pd.to_numeric(khata_df["amount"], errors="coerce").fillna(0)
        total_credit = float(amounts.where(khata_df["transaction_type"] == KHATA_CREDIT, 0).sum())
        total_payment = float(amounts.where(khata_df["transaction_type"] == KHATA_PAYMENT, 0).sum())
        total_balance = total_credit - total_payment
        recovery_pct = (total_payment / total_credit * 100) if total_credit > 0 else 100.0

        if not risk_report.empty:
            total_overdue = float(risk_report["overdue_balance"].sum())
            overdue_count = len(risk_report[risk_report["overdue_balance"] > 0])
            high_risk_count = len(risk_report[risk_report["risk_score"] >= 70])
            moderate_risk_count = len(risk_report[(risk_report["risk_score"] >= 40) & (risk_report["risk_score"] < 70)])
            safe_count = len(risk_report[risk_report["risk_score"] < 40])
        else:
            total_overdue = 0.0
            overdue_count = 0
            high_risk_count = 0
            moderate_risk_count = 0
            safe_count = 0

        # --- 1. Portfolio KPI Dashboard ---
        st.markdown(
            f'''
            <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-bottom: 14px;">
                <div style="background: linear-gradient(135deg, rgba(30, 41, 59, 0.7), rgba(15, 23, 42, 0.8)); border: 1px solid rgba(148, 163, 184, 0.2); border-radius: 12px; padding: 12px; text-align: center;">
                    <div style="font-size: 11px; color: #94a3b8; font-weight: 700; text-transform: uppercase;">एकूण दिलेली उधारी</div>
                    <div style="font-size: 20px; font-weight: 800; color: #f1f5f9; margin-top: 4px;">₹{total_credit:,.2f}</div>
                    <div style="font-size: 10px; color: #64748b; margin-top: 2px;">{len(risk_report)} ग्राहक खाती</div>
                </div>
                <div style="background: linear-gradient(135deg, rgba(16, 185, 129, 0.1), rgba(6, 78, 59, 0.2)); border: 1px solid rgba(16, 185, 129, 0.3); border-radius: 12px; padding: 12px; text-align: center;">
                    <div style="font-size: 11px; color: #a7f3d0; font-weight: 700; text-transform: uppercase;">वसूल झालेली रक्कम</div>
                    <div style="font-size: 20px; font-weight: 800; color: #10b981; margin-top: 4px;">₹{total_payment:,.2f}</div>
                    <div style="font-size: 10px; color: #34d399; margin-top: 2px;">{recovery_pct:.1f}% परतफेड प्रमाण</div>
                </div>
                <div style="background: linear-gradient(135deg, rgba(14, 165, 233, 0.12), rgba(3, 105, 161, 0.2)); border: 1px solid rgba(14, 165, 233, 0.4); border-radius: 12px; padding: 12px; text-align: center; box-shadow: 0 4px 15px rgba(14, 165, 233, 0.1);">
                    <div style="font-size: 11px; color: #bae6fd; font-weight: 700; text-transform: uppercase;">शिल्लक येणे बाकी</div>
                    <div style="font-size: 20px; font-weight: 800; color: #38bdf8; margin-top: 4px;">₹{total_balance:,.2f}</div>
                    <div style="font-size: 10px; color: #7dd3fc; margin-top: 2px;">एकूण येणे शिल्लक</div>
                </div>
                <div style="background: linear-gradient(135deg, rgba(239, 68, 68, 0.12), rgba(153, 27, 27, 0.2)); border: 1px solid rgba(239, 68, 68, 0.4); border-radius: 12px; padding: 12px; text-align: center;">
                    <div style="font-size: 11px; color: #fecaca; font-weight: 700; text-transform: uppercase;">मुदतबाह्य उधारी (Overdue)</div>
                    <div style="font-size: 20px; font-weight: 800; color: #ef4444; margin-top: 4px;">₹{total_overdue:,.2f}</div>
                    <div style="font-size: 10px; color: #f87171; margin-top: 2px;">{overdue_count} खाती थकीत</div>
                </div>
            </div>
            ''',
            unsafe_allow_html=True,
        )

        # --- 2. Live Search, Risk Filter & Actions Toolbar ---
        sf_col1, sf_col2, sf_col3, sf_col4 = st.columns([1.6, 1.2, 1.2, 0.6])
        with sf_col1:
            search = st.text_input(
                "ग्राहक शोधा",
                placeholder="🔍 नाव किंवा फोन नंबर शोधा...",
                key="khata_search",
                label_visibility="collapsed",
            ).strip()

        with sf_col2:
            filter_opts = [
                f"सर्व ग्राहक ({len(risk_report)})",
                f"🔴 हाय रिस्क ({high_risk_count})",
                f"🟡 मध्यम जोखीम ({moderate_risk_count})",
                f"⚠️ फक्त मुदतबाह्य ({overdue_count})",
                f"🟢 सुरक्षित ग्राहक ({safe_count})",
            ]
            sel_filter = st.selectbox(
                "जोखीम फिल्टर:",
                filter_opts,
                key="khata_filter_cat",
                label_visibility="collapsed",
            )

        with sf_col3:
            sort_opts = [
                "सर्वात जास्त बाकी रक्कम आधी",
                "सर्वात जास्त रिस्क स्कोअर आधी",
                "सर्वाधिक दिवस थकीत आधी",
                "ग्राहक नाव (A-Z)",
            ]
            sel_sort = st.selectbox(
                "क्रमवारी:",
                sort_opts,
                key="khata_sort_cat",
                label_visibility="collapsed",
            )

        with sf_col4:
            if st.button("🔄 रिफ्रेश", key="refresh_khata", use_container_width=True):
                st.rerun()

        visible_risk = risk_report.copy()
        if search and not visible_risk.empty:
            search_match = (
                visible_risk["customer_name"].fillna("").astype(str).str.contains(search, case=False, regex=False)
                | visible_risk["phone"].fillna("").astype(str).str.contains(search, case=False, regex=False)
            )
            visible_risk = visible_risk[search_match]

        f_df = visible_risk.copy()
        if "हाय रिस्क" in sel_filter:
            f_df = f_df[f_df["risk_score"] >= 70]
        elif "मध्यम" in sel_filter:
            f_df = f_df[(f_df["risk_score"] >= 40) & (f_df["risk_score"] < 70)]
        elif "मुदतबाह्य" in sel_filter:
            f_df = f_df[f_df["overdue_balance"] > 0]
        elif "सुरक्षित" in sel_filter:
            f_df = f_df[f_df["risk_score"] < 40]

        if not f_df.empty:
            if "बाकी रक्कम" in sel_sort:
                f_df = f_df.sort_values(by="balance", ascending=False)
            elif "रिस्क स्कोअर" in sel_sort:
                f_df = f_df.sort_values(by="risk_score", ascending=False)
            elif "दिवस थकीत" in sel_sort:
                f_df = f_df.sort_values(by="overdue_days", ascending=False)
            elif "नाव" in sel_sort:
                f_df = f_df.sort_values(by="customer_name", ascending=True)

        if f_df.empty:
            if risk_report.empty:
                st.info("सध्या कोणतीही उधारी नोंद उपलब्ध नाही. नवीन नोंद जोडण्यासाठी वरील 'नवीन उधारी / हप्ता नोंद' टॅब वापरा.")
            else:
                st.warning("शोधलेल्या निकषांनुसार कोणतेही ग्राहक आढळले नाहीत.")
        else:
            PAGE_SIZE = 10
            total_custs = len(f_df)
            if total_custs > PAGE_SIZE:
                num_pages = math.ceil(total_custs / PAGE_SIZE)
                p_c1, p_c2 = st.columns([1, 2])
                with p_c1:
                    page_num = st.selectbox(
                        f"📄 पान निवडा (1-{num_pages}):",
                        range(1, num_pages + 1),
                        key="khata_page_num",
                    )
                f_df_page = f_df.iloc[(page_num - 1) * PAGE_SIZE : page_num * PAGE_SIZE]
            else:
                f_df_page = f_df

            shop_name = get_shop_setting("shop_name", "VernaLedger")
            business_upi_id = load_business_upi_id()

            # --- 3. Compact & Modern Customer Cards with 100% Working Actions ---
            for c_idx, customer in f_df_page.reset_index(drop=True).iterrows():
                name = _khata_text(customer["customer_name"])
                customer_phone = _khata_text(customer["phone"])
                risk_score = int(customer.get("risk_score", 0))
                balance = float(customer.get("balance", 0.0))
                overdue_balance = float(customer.get("overdue_balance", 0.0))
                overdue_days = int(customer.get("overdue_days", 0))
                credit = float(customer.get("credit", 0.0))
                payments = float(customer.get("payments", 0.0))
                repay_ratio = float(customer.get("repayment_ratio", 0.0))
                ai_rec = customer.get("ai_rec_mr", "")

                if risk_score >= 70:
                    risk_color = "#ef4444"
                    badge_text = "🔴 हाय रिस्क"
                elif risk_score >= 40:
                    risk_color = "#f59e0b"
                    badge_text = "🟡 मध्यम जोखीम"
                else:
                    risk_color = "#10b981"
                    badge_text = "🟢 सुरक्षित ग्राहक"

                od_tag = f"({overdue_days} दिवस थकीत)" if overdue_days > 0 else ""

                ai_alert_html = ""
                if (risk_score >= 40 or overdue_days > 0) and ai_rec:
                    ai_alert_html = f'''
                    <div style="background: rgba(239, 68, 68, 0.08); border-left: 3px solid {risk_color}; padding: 6px 10px; border-radius: 0 6px 6px 0; margin-top: 8px;">
                        <span style="font-size: 11px; color: #f87171; font-weight: 600;">⚡ AI सूचना: {escape(ai_rec)}</span>
                    </div>
                    '''

                st.markdown(
                    f'''
                    <div style="background: linear-gradient(145deg, rgba(15, 23, 42, 0.95), rgba(10, 15, 30, 0.95)); border: 1.5px solid {risk_color}44; border-radius: 12px; padding: 12px 14px; margin-top: 10px; margin-bottom: 4px; box-shadow: 0 3px 10px rgba(0,0,0,0.25);">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                            <div>
                                <span style="font-size: 16px; font-weight: 800; color: #f8fafc;">{escape(name)}</span>
                                <span style="font-size: 12px; color: #94a3b8; margin-left: 8px;">📞 {escape(customer_phone if customer_phone else "फोन नाही")}</span>
                            </div>
                            <div style="background: {risk_color}22; border: 1px solid {risk_color}; color: {risk_color}; padding: 2px 10px; border-radius: 16px; font-size: 11px; font-weight: 700;">
                                {escape(badge_text)} · {risk_score}/100
                            </div>
                        </div>
                        <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 6px; background: rgba(0,0,0,0.25); padding: 8px 10px; border-radius: 8px;">
                            <div><span style="font-size: 10px; color: #94a3b8;">एकूण उधारी:</span><br><b style="font-size: 13px; color: #e2e8f0;">₹{credit:,.2f}</b></div>
                            <div><span style="font-size: 10px; color: #94a3b8;">जमा:</span><br><b style="font-size: 13px; color: #10b981;">₹{payments:,.2f}</b> <span style="font-size: 9px; color: #6ee7b7;">({repay_ratio*100:.0f}%)</span></div>
                            <div><span style="font-size: 10px; color: #94a3b8;">बाकी शिल्लक:</span><br><b style="font-size: 14px; color: #38bdf8;">₹{balance:,.2f}</b></div>
                            <div><span style="font-size: 10px; color: #94a3b8;">मुदतबाह्य:</span><br><b style="font-size: 14px; color: {risk_color};">₹{overdue_balance:,.2f}</b> <span style="font-size: 10px; color: #fca5a5;">{escape(od_tag)}</span></div>
                        </div>
                        {ai_alert_html}
                    </div>
                    ''',
                    unsafe_allow_html=True,
                )

                # WhatsApp reminder link preparation
                clean_phone = re.sub(r"\D", "", customer_phone)
                if len(clean_phone) == 10:
                    clean_phone = "91" + clean_phone
                elif len(clean_phone) == 11 and clean_phone.startswith("0"):
                    clean_phone = "91" + clean_phone[1:]

                if overdue_days > 0:
                    wa_msg = (
                        f"नमस्कार {name} जी,\n"
                        f"आपल्या '{shop_name}' दुकानाचे ₹{balance:,.2f} उधारी बाकी असून ती गेल्या {overdue_days} दिवसांपासून थकीत आहे.\n"
                        f"कृपया ही रक्कम लवकरात लवकर जमा करावी ही नम्र विनंती."
                    )
                else:
                    wa_msg = (
                        f"नमस्कार {name} जी,\n"
                        f"आपल्या '{shop_name}' दुकानाचे ₹{balance:,.2f} उधारी बाकी आहे.\n"
                        f"कृपया सोयीनुसार जमा करावी ही नम्र विनंती. धन्यवाद!"
                    )

                if business_upi_id and balance > 0:
                    wa_msg += f"\n\n📲 Google Pay / PhonePe द्वारे पेमेंट करण्यासाठी UPI ID:\n{business_upi_id}"

                btn_c1, btn_c2 = st.columns([1, 1])
                with btn_c1:
                    if clean_phone:
                        st.link_button(
                            "💬 WhatsApp आठवण",
                            f"https://wa.me/{clean_phone}?text={urllib.parse.quote(wa_msg)}",
                            key=f"wa_btn_{c_idx}_{clean_phone}",
                            use_container_width=True,
                        )
                    else:
                        st.button("💬 WhatsApp (फोन नाही)", key=f"wa_dis_{c_idx}", disabled=True, use_container_width=True)
                with btn_c2:
                    if customer_phone:
                        st.link_button(
                            "📞 थेट कॉल",
                            f"tel:{customer_phone}",
                            key=f"call_btn_{c_idx}_{customer_phone}",
                            use_container_width=True,
                        )
                    else:
                        st.button("📞 कॉल (नंबर नाही)", key=f"call_dis_{c_idx}", disabled=True, use_container_width=True)

                # Unified Single Action Expander per Customer: Payment, Credit & Passbook
                with st.expander(f"📝 {name} - व्यवहार नोंदवा / पासबुक इतिहास", expanded=False):
                    tab_pay, tab_cred, tab_pass = st.tabs([
                        "💵 पैसे जमा घ्या (Receive Payment)",
                        "➕ नवीन उधारी जोडा (Add Credit)",
                        "📜 पासबुक (Passbook & Delete)",
                    ])
                    with tab_pay:
                        with st.form(key=f"form_quick_pay_{c_idx}_{name}"):
                            p_col1, p_col2 = st.columns(2)
                            with p_col1:
                                default_pay_val = float(balance) if balance > 0 else 100.0
                                pay_amount = st.number_input(
                                    "जमा रक्कम (₹):",
                                    min_value=1.0,
                                    value=default_pay_val,
                                    step=50.0,
                                    key=f"input_pay_amt_{c_idx}",
                                )
                                pay_entry_date = st.date_input("जमा तारीख:", value=date.today(), key=f"input_pay_date_{c_idx}")
                            with p_col2:
                                pay_notes = st.text_input(
                                    "तपशील / पेमेंट पद्धत:",
                                    value="रोख जमा (Cash)" if not business_upi_id else "UPI / GPay द्वारे जमा",
                                    key=f"input_pay_notes_{c_idx}",
                                )
                                st.write("")
                                submit_pay = st.form_submit_button("✅ जमा रक्कम नोंदवा", type="primary", use_container_width=True)

                            if submit_pay:
                                try:
                                    save_khata_transaction(
                                        customer_name=name,
                                        phone=customer_phone,
                                        amount=pay_amount,
                                        transaction_type=KHATA_PAYMENT,
                                        entry_date=pay_entry_date,
                                        due_date=pay_entry_date,
                                        notes=pay_notes,
                                    )
                                    log_activity(
                                        st.session_state.get("current_username", "admin"),
                                        f"Collected payment ₹{pay_amount} from {name}",
                                    )
                                    st.toast(f"{name} यांच्याकडून ₹{pay_amount:,.2f} जमा नोंदवले!", icon="✅")
                                    st.rerun()
                                except Exception as exc:
                                    st.error(f"पेमेंट नोंद सेव्ह करता आले नाही: {exc}")

                    with tab_cred:
                        with st.form(key=f"form_quick_cred_{c_idx}_{name}"):
                            c_col1, c_col2 = st.columns(2)
                            with c_col1:
                                cred_amount = st.number_input(
                                    "उधारी रक्कम (₹):",
                                    min_value=1.0,
                                    value=100.0,
                                    step=50.0,
                                    key=f"input_cred_amt_{c_idx}",
                                )
                                cred_entry_date = st.date_input("उधारी तारीख:", value=date.today(), key=f"input_cred_date_{c_idx}")
                            with c_col2:
                                cred_due_date = st.date_input(
                                    "परतफेडीची मुदत तारीख:",
                                    value=date.today() + timedelta(days=15),
                                    key=f"input_cred_due_{c_idx}",
                                )
                                cred_notes = st.text_input(
                                    "वस्तू तपशील / टीप:",
                                    placeholder="उदा. किराणा सामान, २ किलो साखर...",
                                    key=f"input_cred_notes_{c_idx}",
                                )
                            submit_cred = st.form_submit_button("➕ नवीन उधारी खात्यात जोडा", type="primary", use_container_width=True)

                            if submit_cred:
                                try:
                                    save_khata_transaction(
                                        customer_name=name,
                                        phone=customer_phone,
                                        amount=cred_amount,
                                        transaction_type=KHATA_CREDIT,
                                        entry_date=cred_entry_date,
                                        due_date=cred_due_date,
                                        notes=cred_notes,
                                    )
                                    log_activity(
                                        st.session_state.get("current_username", "admin"),
                                        f"Added credit ₹{cred_amount} for {name}",
                                    )
                                    st.toast(f"{name} यांच्या खात्यात ₹{cred_amount:,.2f} उधारी जोडली!", icon="📝")
                                    st.rerun()
                                except Exception as exc:
                                    st.error(f"उधारी नोंद सेव्ह करता आले नाही: {exc}")

                    with tab_pass:
                        cust_mask = khata_df["customer_name"].fillna("").astype(str).str.casefold() == name.casefold()
                        if customer_phone:
                            cust_mask = cust_mask | (khata_df["phone"].fillna("").astype(str) == customer_phone)
                        cust_txs = khata_df[cust_mask].sort_values(by="id", ascending=False)
                        if cust_txs.empty:
                            st.info("या ग्राहकाचा कोणताही व्यवहार सापडला नाही.")
                        else:
                            show_txs = cust_txs[["id", "date", "transaction_type", "amount", "due_date", "notes"]].copy()
                            show_txs.columns = ["ID", "तारीख", "व्यवहार प्रकार", "रक्कम (₹)", "मुदत तारीख", "तपशील / टीप"]
                            st.dataframe(show_txs, use_container_width=True, hide_index=True)

                            del_col1, del_col2 = st.columns([2, 1])
                            with del_col1:
                                tx_ids = cust_txs["id"].tolist()
                                tx_options = {
                                    tid: f"ID #{tid} - {cust_txs.loc[cust_txs['id']==tid, 'transaction_type'].values[0]} ₹{cust_txs.loc[cust_txs['id']==tid, 'amount'].values[0]} ({cust_txs.loc[cust_txs['id']==tid, 'date'].values[0]})"
                                    for tid in tx_ids
                                }
                                sel_del_id = st.selectbox(
                                    "चुकीची नोंद डिलीट करा:",
                                    tx_ids,
                                    format_func=lambda x: tx_options.get(x, f"ID #{x}"),
                                    key=f"del_tx_sel_{c_idx}_{name}",
                                )
                            with del_col2:
                                st.write("")
                                st.write("")
                                if st.button("🗑️ नोंद डिलीट करा", key=f"del_tx_btn_{c_idx}_{name}", type="secondary", use_container_width=True):
                                    try:
                                        if delete_khata_transaction(sel_del_id):
                                            log_activity(
                                                st.session_state.get("current_username", "admin"),
                                                f"Deleted Khata ID {sel_del_id} for {name}",
                                            )
                                            st.toast(f"नोंद #{sel_del_id} यशस्वीरीत्या डिलीट केली!", icon="🗑️")
                                            st.rerun()
                                        else:
                                            st.error("नोंद सापडली नाही.")
                                    except Exception as exc:
                                        st.error(f"नोंद डिलीट करता आली नाही: {exc}")

                st.write("")

            # --- 4. Master Ledger Database & CSV Export (At the bottom) ---
            st.divider()
            with st.expander("📁 संपूर्ण लेजर डेटाबेस & एक्सेल/CSV एक्सपोर्ट (All Transactions)", expanded=False):
                st.markdown("##### 📋 सर्व ग्राहकांच्या नोंदींचा कच्चा डेटा (Master Khata Records)")
                st.dataframe(khata_df[KHATA_COLUMNS], use_container_width=True, hide_index=True)
                csv_data = khata_df[KHATA_COLUMNS].to_csv(index=False).encode('utf-8-sig')
                st.download_button(
                    label="📥 संपूर्ण लेजर CSV फाईल डाउनलोड करा (Download CSV)",
                    data=csv_data,
                    file_name=f"Customer_Khata_Ledger_{date.today().strftime('%Y%m%d')}.csv",
                    mime="text/csv",
                    key="download_full_khata_csv",
                    use_container_width=True,
                )

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
    st.session_state["ui_language"] = "en"
    st.session_state["ui_language_english"] = True


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
    "Business Operations": "व्यवसाय संचालन",
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
    "Expense successfully recorded!": "खर्च यशस्वीरित्या नोंदवला गेला!",

    "Item Name": "वस्तूचे नाव",
    "Stock Quantity": "उपलब्ध साठा",
    "Unit (e.g. kg, pcs, ltr)": "मोजमापाचे एकक (उदा. kg, नग, ltr)",
    "Low Stock Alert Limit": "कमी साठ्याची सूचना मर्यादा",
    "Save Stock": "स्टॉक सेव्ह करा",
    "Please enter item name!": "कृपया वस्तूचे नाव टाका!",
    "Item ID to delete": "डिलिट करण्यासाठी आयटम ID",
    "No stock available.": "कोणताही स्टॉक उपलब्ध नाही.",
    "Total Business Expenses": "एकूण व्यवसाय खर्च",
    "Expense Records": "खर्च नोंदी",
    "Expense ID to delete": "डिलिट करण्यासाठी खर्च ID",
    "Delete Expense Record": "खर्च नोंद डिलीट करा",
    "No expenses recorded.": "कोणताही खर्च नोंदवलेला नाही.",
    "Restricted Area: Staff not allowed on Staff Management page!": "प्रतिबंधीत क्षेत्रः कामागार/स्टाफला स्टाफ मॅनेजमेंट पेजवर प्रवेश करण्याची परवानगी नाही!",
    "Add New Staff or Admin": "नवीन स्टाफ किंवा ॲडमिन जोडा",
    "Password (Min 6 digits)": "पासवर्ड (किमान ६ अंक/अक्षरे)",
    "Role": "भूमिका",
    "Staff (Cashier - Limited Access)": "कर्मचारी (मर्यादित प्रवेश)",
    "Admin (Owner - Full Access)": "प्रशासक (पूर्ण प्रवेश)",
    "Create Account": "खाते तयार करा",
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
    "Customer Name": "ग्राहकाचे नाव",
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
    "OCR Scanner & Voice Billing": "OCR स्कॅनर आणि व्हॉइस बिलिंग",
    "Instant Digital POS Receipt Parsing & Audio Confirmation": "पावत्या स्कॅन करा आणि आवाजाद्वारे बिल नोंदवा",
    "पावत्या स्कॅन करा आणि आवाजाद्वारे बिल नोंदवा": "Scan receipts and record bills by voice",
    "POS ONLINE": "POS सुरू आहे",
    "Input Mode": "इनपुट प्रकार",
    "ड्युप्लिकेट पावती असल्यास जबरदस्तीने सेव्ह करा (Force Save)": "Save duplicate receipts anyway",
    "⚠️ ड्युप्लिकेट पावती सेव्ह करा (Force Save)": "⚠️ Save duplicate receipt (Force Save)",
    "ड्युप्लिकेट पावती सेव्ह करा": "Save duplicate receipt",
    "⚠️ ड्युप्लिकेट पावती सेव्ह Force Save": "⚠️ Save duplicate receipt (Force Save)",
    "Upload File": "फाइल अपलोड करा",
    "Live Camera": "थेट कॅमेरा",
    "Voice Bill": "व्हॉइस बिल",
    "Take photo": "फोटो घ्या",
    "Choose Receipts": "पावत्या निवडा",
    "प्रोग्रेस सुरू आहे... व्हॉईसवरून बिल तयार होत आहे.": "Processing voice input and preparing the bill...",
    "व्हॉईस बिल Successfully तयार होऊन डेटाबेसमध्ये सेव्ह झाले !": "Voice bill processed and saved successfully!",
    "व्हॉईस बिल सेव्ह झाले!": "Voice bill saved!",
    "Process Receipt(s)": "पावती प्रक्रिया करा",
    "पावती प्रक्रिया करा": "Process Receipt(s)",
    "Successfully processed": "यशस्वी प्रक्रिया:",
    "पावती Successfully स्कॅन झाली!": "Receipt scanned successfully!",
    "कृपया किमान एक पावती निवडा किंवा कॅमेऱ्याने फोटो घ्या.": "Select at least one receipt or take a photo.",
    "Extracted Items & Summary": "काढलेल्या वस्तू आणि सारांश",
    "Scan receipt(s) or use Multi-Language Voice Bill to display extracted items & summary.": "Scan a receipt or use voice billing to see extracted items and the summary.",
    "Scan receipt(s) or use Multi-Language व्हॉइस बिल to display extracted items & summary.": "पावती स्कॅन करा किंवा व्हॉइस बिल वापरून काढलेले तपशील आणि सारांश पहा.",
    "Summary": "सारांश",
    "📋 Summary": "📋 सारांश",
    "NAVIGATION MENU": "नेव्हिगेशन मेनू",
    "PROJECT DEVELOPERS": "प्रकल्प विकासक",
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
    "स्टॉक आयटम डिलिट करा": "Delete stock item",
    "डिलिट करण्यासाठी स्टॉक ID": "Stock ID to delete",
    "कोणताही स्टॉक जोडलेला नाही.": "No stock items have been added.",
    "नवीन माल जोडा": "Add inventory item",
    "वस्तूचे नाव, प्रमाण आणि कमी-साठा मर्यादा भरा.": "Enter the item name, quantity and low-stock limit.",
    "साठ्याचा आढावा": "Inventory overview",
    "वस्तूंची यादी आणि पुन्हा मागवायच्या वस्तू.": "Items in stock and items to reorder.",
    "व्यवसाय खर्च · नोंदवही": "Business Expenses",
    "भाडे, वीज, पगार आणि रोजच्या खर्चांचा स्पष्ट हिशोब.": "Track rent, utilities, payroll and everyday business costs.",
    "खर्चाचा प्रकार, रक्कम आणि तारीख नोंदवा.": "Enter the expense type, amount and date.",
    "खर्चाचे शीर्षक (Expense Title e.g. Light Bill)": "खर्चाचे शीर्षक (उदा. वीज बिल)",
    "खर्चाचा प्रकार (Category)": "खर्चाचा प्रकार",
    "तपशील / टीप (Notes)": "तपशील / टीप",
    "खर्च सेव्ह करा": "Save expense",
    "Admin Staff Management": "स्टाफ व्यवस्थापन",
    "Create and manage staff accounts with role-based access control.": "नवीन कर्मचारी खाती तयार करा आणि भूमिका नियंत्रण व्यवस्थापित करा.",
    "Registered Users List": "नोंदणीकृत वापरकर्त्यांची यादी",
    "Enter username to delete": "डिलिट करण्यासाठी वापरकर्ता नाव टाईप करा",
    "Delete User": "वापरकर्ता डिलीट करा",
    "Master Admin account cannot be deleted!": "मुख्य मास्टर ॲडमिन खाते डिलीट करता येणार नाही!",
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
    "वीज बिल (Electricity Bill)": "वीज बिल",
    "स्टाफ पगार (Staff Salary)": "स्टाफ पगार",
    "वाहतूक (Transport)": "वाहतूक",
    "इतर (Other)": "इतर",
}


def _translate_ui_text(value):
    if not isinstance(value, str):
        return value
    language = st.session_state.get("ui_language", "en")
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
            clean_val = re.sub(r'[\u0900-\u097f]+[^\u0900-\u097f\(]*\(([^()]+)\)', r'\1', value)
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
        key="ui_language_english",
        
        on_change=_sync_language_from_toggle,
    )


_streamlit_ui = st
st = _LocalizedStreamlitProxy(_streamlit_ui)


def render_custom_logo(size="large"):
    if size == "large":
        st.markdown("""
        <div style="display: flex; justify-content: center; align-items: center; margin-bottom: 12px;">
            <div style="background: linear-gradient(135deg, #00f2fe 0%, #3b82f6 50%, #8b5cf6 100%); padding: 14px; border-radius: 20px; box-shadow: 0 10px 25px rgba(0, 242, 254, 0.4), inset 0 2px 4px rgba(255,255,255,0.3); animation: pulseGlow 3s infinite alternate;">
                <svg width="38" height="38" viewBox="0 0 32 32" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M16 2 L28 7 V16 C28 23 23 28 16 30 C9 28 4 23 4 16 V7 L16 2 Z" fill="rgba(255,255,255,0.15)" stroke="white" stroke-width="1.5"></path>
                    <path d="M10 11 L16 22 L22 11" stroke="white" stroke-width="2.5"></path>
                    <path d="M9 16 H23" stroke="rgba(255,255,255,0.6)" stroke-width="1.5" stroke-dasharray="3 3"></path>
                    <circle cx="16" cy="22" r="2" fill="#00ff87" stroke="white" stroke-width="1"></circle>
                    <circle cx="10" cy="11" r="1.5" fill="white" stroke="none"></circle>
                    <circle cx="22" cy="11" r="1.5" fill="white" stroke="none"></circle>
                </svg>
            </div>
        </div>
        """, unsafe_allow_html=True)
    elif size == "compact":
        st.markdown("""
        <div style="display: flex; justify-content: center; align-items: center; margin-bottom: 6px;">
            <div style="background: linear-gradient(135deg, #00f2fe 0%, #3b82f6 50%, #8b5cf6 100%); padding: 8px; border-radius: 12px; box-shadow: 0 6px 15px rgba(0, 242, 254, 0.3), inset 0 1px 2px rgba(255,255,255,0.3);">
                <svg width="22" height="22" viewBox="0 0 32 32" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M16 2 L28 7 V16 C28 23 23 28 16 30 C9 28 4 23 4 16 V7 L16 2 Z" fill="rgba(255,255,255,0.15)" stroke="white" stroke-width="1.5"></path>
                    <path d="M10 11 L16 22 L22 11" stroke="white" stroke-width="2.5"></path>
                    <path d="M9 16 H23" stroke="rgba(255,255,255,0.6)" stroke-width="1.5" stroke-dasharray="3 3"></path>
                    <circle cx="16" cy="22" r="2" fill="#00ff87" stroke="white" stroke-width="1"></circle>
                    <circle cx="10" cy="11" r="1.5" fill="white" stroke="none"></circle>
                    <circle cx="22" cy="11" r="1.5" fill="white" stroke="none"></circle>
                </svg>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="sidebar-brand" style="display: flex; align-items: center; gap: 10px; margin-bottom: 10px; padding: 4px 0;">
            <div style="background: linear-gradient(135deg, #00f2fe 0%, #3b82f6 50%, #8b5cf6 100%); padding: 7px; border-radius: 10px; box-shadow: 0 0 12px rgba(0, 242, 254, 0.5); flex-shrink: 0;">
                <svg width="22" height="22" viewBox="0 0 32 32" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M16 2 L28 7 V16 C28 23 23 28 16 30 C9 28 4 23 4 16 V7 L16 2 Z" fill="rgba(255,255,255,0.15)" stroke="white" stroke-width="1.5"></path>
                    <path d="M10 11 L16 22 L22 11" stroke="white" stroke-width="2.5"></path>
                    <path d="M9 16 H23" stroke="rgba(255,255,255,0.6)" stroke-width="1.5" stroke-dasharray="3 3"></path>
                    <circle cx="16" cy="22" r="2" fill="#00ff87" stroke="white" stroke-width="1"></circle>
                    <circle cx="10" cy="11" r="1.5" fill="white" stroke="none"></circle>
                    <circle cx="22" cy="11" r="1.5" fill="white" stroke="none"></circle>
                </svg>
            </div>
            <div style="line-height: 1.2;">
                <span style="font-size: 16px; font-weight: 800; background: linear-gradient(135deg, #00f2fe 0%, #00ff87 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; display: block; text-shadow: 0 0 8px rgba(0,242,254,0.4);">VernaLedger.AI</span>
                <span style="font-size: 9px; font-weight: 700; color: #94a3b8; display: block; letter-spacing: 0.5px;">AI FINANCIAL SUITE</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
# --- PERFECT DYNAMIC & FULL-WIDTH RESPONSIVE CSS ---
st.markdown("""
<style>

    @import url('https://fonts.googleapis.com/css2?family=Baloo+2:wght@400;500;600;700;800&family=Mukta:wght@400;500;600;700;800&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200');
    @import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200');

    /* --- SAFE FONT & MARATHI UNBROKEN TEXT APPLICATION --- */
    html, body, .stApp, 
    h1, h2, h3, h4, h5, h6, 
    p, li, label, 
    .stMarkdown, .stMarkdown p,
    .stTextInput input, .stTextArea textarea, .stSelectbox select,
    [data-testid="stWidgetLabel"] p, [data-testid="stMarkdownContainer"] p {
        font-family: 'Mukta', 'Baloo 2', 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
        word-break: keep-all !important;
        overflow-wrap: break-word !important;
        hyphens: none !important;
    }
    /* Protect all Streamlit Material Icons from font overrides */
    [data-testid="stIconMaterial"],
    [data-testid^="stIcon"],
    [data-testid*="Icon"],
    [data-testid="stSidebarCollapseButton"] button span,
    [data-testid="stSidebarCollapseButton"] span,
    [data-testid="collapsedControl"] button span,
    [data-testid="collapsedControl"] span,
    [data-testid="stFileUploader"] span[data-testid="stIconMaterial"],
    .material-symbols-rounded,
    .material-symbols-outlined,
    .material-icons,
    [class*="material-symbols"],
    [class*="material-icons"] {
        font-family: 'Material Symbols Rounded', 'Material Symbols Outlined', 'Material Icons' !important;
        font-weight: normal !important;
        font-style: normal !important;
        font-size: 24px !important;
        line-height: 1 !important;
        letter-spacing: normal !important;
        text-transform: none !important;
        display: inline-block !important;
        white-space: nowrap !important;
        word-wrap: normal !important;
        direction: ltr !important;
        -webkit-font-feature-settings: 'liga' !important;
        font-feature-settings: 'liga' !important;
        -webkit-font-smoothing: antialiased !important;
    }
    /* Protect SVG elements */
    svg, svg * {
        font-family: inherit !important; 
    }
    /* --- END SAFE FONT --- */
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
    background: linear-gradient(145deg, rgba(15, 23, 42, 0.8) 0%, rgba(9, 9, 11, 0.7) 100%) !important;
    backdrop-filter: blur(28px) !important;
    border: 1px solid rgba(56, 189, 248, 0.3) !important;
    border-radius: 22px !important;
    padding: 24px !important;
    margin-bottom: 24px !important;
    box-shadow: 0 15px 35px rgba(0, 0, 0, 0.5), inset 0 1px rgba(255, 255, 255, 0.08) !important;
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
    font-size: 12px !important;
    font-weight: 650 !important;
    letter-spacing: normal !important;
    line-height: 1.35 !important;
    margin: 0 !important;
    word-break: keep-all !important;
    overflow-wrap: break-word !important;
    white-space: normal !important;
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
div[data-testid="stFileUploader"] label[data-testid="stWidgetLabel"] {
    display: block !important;
    width: 100% !important;
    margin-bottom: 14px !important;
    padding-bottom: 10px !important;
    border-bottom: 1px dashed rgba(0, 242, 254, 0.25) !important;
}
div[data-testid="stFileUploader"] label[data-testid="stWidgetLabel"] p {
    color: #cbd5e1 !important;
    font-size: 12.5px !important;
    line-height: 1.6 !important;
    margin: 0 !important;
}
div[data-testid="stFileUploader"] label[data-testid="stWidgetLabel"] strong {
    display: inline-flex !important;
    align-items: center !important;
    gap: 6px !important;
    padding: 3px 10px !important;
    border-radius: 20px !important;
    font-size: 11px !important;
    font-weight: 700 !important;
    background: rgba(0, 242, 254, 0.12) !important;
    color: #00f2fe !important;
    border: 1px solid rgba(0, 242, 254, 0.35) !important;
    margin-right: 8px !important;
}
div[data-testid="stFileUploader"] label[data-testid="stWidgetLabel"] em {
    font-style: normal !important;
    font-size: 11px !important;
    color: #94a3b8 !important;
    float: right !important;
}
@media (max-width: 600px) {
    div[data-testid="stFileUploader"] label[data-testid="stWidgetLabel"] em {
        float: none !important;
        display: block !important;
        margin-top: 4px !important;
    }
}
div[data-testid="stFileUploader"] section {
    background: transparent !important;
    border: none !important;
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
    position: relative !important;
    overflow: hidden !important;
    background: linear-gradient(135deg, #0ea5e9 0%, #2563eb 48%, #7c3aed 100%) !important;
    color: #ffffff !important;
    font-weight: 800 !important;
    font-size: 13px !important;
    letter-spacing: 0.02em !important;
    border-radius: 12px !important;
    border: 1px solid rgba(0, 242, 254, 0.7) !important;
    padding: 0.72rem 1.2rem !important;
    min-height: 42px !important;
    box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.28), inset 0 -2px 0 rgba(2, 6, 23, 0.2), 0 4px 0 rgba(2, 8, 23, 0.35), 0 10px 18px rgba(2, 8, 23, 0.28) !important;
    text-shadow: 0 1px 2px rgba(2, 8, 23, 0.45) !important;
    transition: transform 0.16s ease, box-shadow 0.16s ease, border-color 0.16s ease, filter 0.16s ease !important;
}
.stButton>button::before, .stDownloadButton>button::before, div[data-testid="stFormSubmitButton"]>button::before {
    content: "" !important;
    position: absolute !important;
    inset: 1px 1px 52% !important;
    border-radius: 10px 10px 45% 45% !important;
    background: linear-gradient(180deg, rgba(255, 255, 255, 0.2), transparent) !important;
    pointer-events: none !important;
}
.stButton>button:active, .stDownloadButton>button:active, div[data-testid="stFormSubmitButton"]>button:active {
    transform: translateY(3px) !important;
    box-shadow: inset 0 2px 3px rgba(2, 6, 23, 0.3), 0 1px 0 rgba(2, 8, 23, 0.4) !important;
    filter: brightness(0.97) !important;
}
.stButton>button:hover, .stDownloadButton>button:hover, div[data-testid="stFormSubmitButton"]>button:hover {
    box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.34), inset 0 -2px 0 rgba(2, 6, 23, 0.2), 0 5px 0 rgba(2, 8, 23, 0.35), 0 14px 24px rgba(2, 8, 23, 0.32) !important;
    border-color: #00f2fe !important;
    transform: translateY(-2px) scale(1.01) !important;
    filter: brightness(1.04) !important;
}
.stButton>button:focus-visible, .stDownloadButton>button:focus-visible, div[data-testid="stFormSubmitButton"]>button:focus-visible {
    outline: none !important;
    box-shadow: 0 0 0 2px rgba(0, 242, 254, 0.45), 0 0 0 5px rgba(14, 165, 233, 0.2), 0 0 20px rgba(0, 242, 254, 0.45) !important;
}
.stButton>button:disabled, .stDownloadButton>button:disabled, div[data-testid="stFormSubmitButton"]>button:disabled {
    opacity: 0.52 !important;
    cursor: not-allowed !important;
    transform: none !important;
    box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.12), 0 2px 0 rgba(2, 8, 23, 0.25) !important;
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
    
    bg_image_css = ""
    try:
        with open("assets/vernaledger_bg.jpg", "rb") as f_img:
            data = f_img.read()
            b64_img = base64.b64encode(data).decode("utf-8")
            bg_image_css = f"background-image: url('data:image/jpeg;base64,{b64_img}') !important; background-size: cover !important; background-position: center !important;"
    except Exception:
        bg_image_css = "background: radial-gradient(ellipse at 18% 18%, rgba(14, 165, 233, 0.20), transparent 36%), radial-gradient(ellipse at 82% 82%, rgba(99, 102, 241, 0.17), transparent 34%), linear-gradient(145deg, #07111f 0%, #0a1628 52%, #080e1c 100%) !important;"

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
        {bg_image_css}
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
        background: linear-gradient(145deg, rgba(2, 6, 23, 0.7), rgba(15, 23, 42, 0.6)) !important;
        backdrop-filter: blur(30px) !important;
        border: 1px solid rgba(56, 189, 248, 0.3) !important;
        border-radius: 30px !important;
        box-shadow: 0 30px 80px rgba(0, 0, 0, 0.6), inset 0 1px rgba(255,255,255,0.1), 0 0 40px rgba(56, 189, 248, 0.15), 0 0 15px rgba(139, 92, 246, 0.1) !important;
        animation: glowBorder 4s infinite alternate;
    }}
    @keyframes glowBorder {{
        0% {{ border-color: rgba(56, 189, 248, 0.3); box-shadow: 0 30px 80px rgba(0,0,0,0.6), inset 0 1px rgba(255,255,255,0.1), 0 0 20px rgba(56, 189, 248, 0.1); }}
        100% {{ border-color: rgba(139, 92, 246, 0.4); box-shadow: 0 30px 80px rgba(0,0,0,0.6), inset 0 1px rgba(255,255,255,0.15), 0 0 40px rgba(139, 92, 246, 0.2); }}
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
            items_rows = "<tr><td colspan='4' style='padding:8px; color:#94a3b8; text-align:center;'>No itemized details</td></tr>"
            
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

def generate_upi_qr_base64(amount: float, vpa: str = "", payee_name: str = "", note: str = "POS Bill") -> str:
    try:
        if qrcode is None:
            return ""
        vpa = (vpa or get_shop_setting("shop_upi_id", "vernaledger@upi")).strip()
        payee_name = (payee_name or get_shop_setting("shop_name", "VernaLedger Store")).strip()
        clean_amount = f"{max(0.0, float(amount)):.2f}"
        upi_url = f"upi://pay?pa={vpa}&pn={urllib.parse.quote(payee_name)}&am={clean_amount}&cu=INR&tn={urllib.parse.quote(note)}"
        qr = qrcode.QRCode(version=1, box_size=5, border=2)
        qr.add_data(upi_url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        buf = BytesIO()
        img.save(buf, format="PNG")
        return base64.b64encode(buf.getvalue()).decode("utf-8")
    except Exception as e:
        ai_logger.error(f"UPI QR generation failed: {e}")
        return ""

def generate_thermal_receipt_html(vendor: str, date_str: str, category: str, items: list, total: float, upi_qr_b64: str = "", receipt_no: str = "1", is_english: bool = False) -> str:
    item_rows = ""
    for idx, itm in enumerate(items, 1):
        name = str(itm.get("item_name", f"Item {idx}")).strip()
        qty = str(itm.get("quantity", itm.get("qty", "1"))).strip()
        rate = float(itm.get("rate", itm.get("price", 0)) or 0)
        t_price = float(itm.get("total_price", rate * 1) or 0)
        item_rows += f"<tr><td style='word-break: break-word; padding-right: 4px;'>{escape(name)}</td><td style='text-align:center; white-space:nowrap;'>{escape(qty)}</td><td style='text-align:right; white-space:nowrap;'>{rate:.1f}</td><td style='text-align:right; white-space:nowrap;'>{t_price:.2f}</td></tr>"

    title_label = "RETAIL CASH SLIP" if is_english else "किराणा खरेदी पावती"
    tot_label = "GRAND TOTAL" if is_english else "एकूण रक्कम"
    thanks_label = "THANK YOU! VISIT AGAIN" if is_english else "धन्यवाद! पुन्हा भेट द्या"

    cfg_shop_name = get_shop_setting("shop_name", vendor if vendor and vendor != "अनामित" else "VERNALEDGER AI POS")
    cfg_shop_addr = get_shop_setting("shop_address", "")
    cfg_shop_phone = get_shop_setting("shop_phone", "")
    cfg_footer_tagline = get_shop_setting("shop_tagline", thanks_label)
    addr_line = f"<div class='center' style='font-size: 8.5px; color:#333;'>{escape(cfg_shop_addr)}</div>" if cfg_shop_addr else ""
    phone_line = f"<div class='center' style='font-size: 8.5px; color:#333;'>मोबाईल: {escape(cfg_shop_phone)}</div>" if cfg_shop_phone else ""

    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>POS Thermal Slip #{receipt_no}</title>
<style>
    @page {{
        size: 58mm auto;
        margin: 0;
    }}
    body {{
        font-family: 'Courier New', Courier, monospace;
        width: 54mm;
        margin: 0 auto;
        padding: 6px 2px;
        color: #000;
        background: #fff;
        font-size: 11px;
        line-height: 1.25;
    }}
    .center {{ text-align: center; }}
    .bold {{ font-weight: bold; }}
    .divider {{ border-top: 1px dashed #000; margin: 5px 0; }}
    .double-divider {{ border-top: 2px dashed #000; margin: 6px 0; }}
    table {{ width: 100%; border-collapse: collapse; font-size: 10px; }}
    th {{ border-bottom: 1px dashed #000; text-align: left; padding: 2px 0; }}
    td {{ padding: 2px 0; }}
    @media print {{
        .no-print {{ display: none !important; }}
    }}
</style>
</head>
<body>
    <div class="center bold" style="font-size: 13px;">{escape(cfg_shop_name)}</div>
    {addr_line}
    {phone_line}
    <div class="center" style="font-size: 9px; margin-top: 2px;">{title_label}</div>
    <div class="divider"></div>
    <div>Date: {escape(date_str)}</div>
    <div>Slip No: #{receipt_no} | Cat: {escape(category)}</div>
    <div class="divider"></div>
    <table>
        <thead>
            <tr>
                <th>Item</th>
                <th style="text-align:center;">Qty</th>
                <th style="text-align:right;">Rate</th>
                <th style="text-align:right;">Tot</th>
            </tr>
        </thead>
        <tbody>
            {item_rows}
        </tbody>
    </table>
    <div class="double-divider"></div>
    <div style="display:flex; justify-content:space-between; font-size:12px; font-weight:bold;">
        <span>{tot_label}:</span>
        <span>₹{total:,.2f}</span>
    </div>
    <div class="divider"></div>
    <div class="center bold" style="margin-top: 8px; font-size: 10px;">*** {escape(cfg_footer_tagline)} ***</div>
    <div class="center" style="font-size: 8px; color:#555;">Powered by VernaLedger-AI</div>
</body>
</html>"""
    return html

def generate_daily_whatsapp_digest(is_english: bool = False) -> str:
    today_str = date.today().strftime("%Y-%m-%d")
    today_disp = date.today().strftime("%d-%m-%Y")
    total_sales = 0.0
    total_bills = 0
    total_expenses = 0.0
    cash_recovered = 0.0
    pending_khata = 0.0

    try:
        with sqlite3.connect("ledger.db") as conn:
            rec_df = pd.read_sql_query("SELECT grand_total, date FROM receipts", conn)
            if not rec_df.empty:
                today_rec = rec_df[rec_df['date'].astype(str).str.contains(today_str, na=False)]
                if today_rec.empty:
                    today_rec = rec_df
                total_sales = float(today_rec['grand_total'].sum() or 0.0)
                total_bills = len(today_rec)

            exp_df = pd.read_sql_query("SELECT amount, date FROM business_expenses", conn)
            if not exp_df.empty:
                today_exp = exp_df[exp_df['date'].astype(str).str.contains(today_str, na=False)]
                if today_exp.empty:
                    today_exp = exp_df
                total_expenses = float(today_exp['amount'].sum() or 0.0)

            khata_df = pd.read_sql_query("SELECT customer_name, amount, transaction_type FROM customer_khata", conn)
            if not khata_df.empty:
                credit_sum = float(khata_df[khata_df['transaction_type'] == 'Credit Given']['amount'].sum() or 0.0)
                pay_sum = float(khata_df[khata_df['transaction_type'] == 'Payment Received']['amount'].sum() or 0.0)
                cash_recovered = pay_sum
                pending_khata = max(0.0, credit_sum - pay_sum)
    except Exception as e:
        ai_logger.error(f"WhatsApp digest error: {e}")

    net_profit = total_sales - total_expenses

    if is_english:
        return (
            f"📊 *VERNALEDGER AI - DAILY BUSINESS DIGEST*\n"
            f"📅 *Date:* {today_disp}\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"💰 *Total Sales:* ₹{total_sales:,.2f} ({total_bills} bills)\n"
            f"📉 *Total Expenses:* ₹{total_expenses:,.2f}\n"
            f"💵 *Estimated Net Margin:* ₹{net_profit:,.2f}\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"✅ *Khata Cash Recovered:* ₹{cash_recovered:,.2f}\n"
            f"⏳ *Total Outstanding Credit:* ₹{pending_khata:,.2f}\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"🤖 _Automated Report Generated by VernaLedger-AI_"
        )
    else:
        return (
            f"📊 *वर्ना लेजर AI - दैनिक बिझनेस रिपोर्ट*\n"
            f"📅 *तारीख:* {today_disp}\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"💰 *आजची एकूण विक्री:* ₹{total_sales:,.2f} ({total_bills} पावत्या)\n"
            f"📉 *एकूण दैनंदिन खर्च:* ₹{total_expenses:,.2f}\n"
            f"💵 *अंदाजे निव्वळ नफा:* ₹{net_profit:,.2f}\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"✅ *उधारीतून जमा रोख:* ₹{cash_recovered:,.2f}\n"
            f"⏳ *बाकी एकूण उधारी:* ₹{pending_khata:,.2f}\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"🤖 _VernaLedger-AI द्वारे स्वयंचलित जनरेट केलेला अहवाल_"
        )

df = load_receipts_data()

# SIDEBAR NAVIGATION ---
with st.sidebar:
    st.markdown('''
    <style>
    /* Sleek Sidebar CSS */
    section[data-testid="stSidebar"][aria-expanded="true"] {
        background: rgba(10, 15, 30, 0.95) !important;
        border-right: 1px solid rgba(0, 242, 254, 0.2);
        overflow: hidden !important;
        width: 270px !important;
        min-width: 270px !important;
        max-width: 270px !important;
        flex: 0 0 270px !important;
        resize: none !important;
    }
    section[data-testid="stSidebar"][aria-expanded="false"] {
        width: 0 !important;
        min-width: 0 !important;
        max-width: 0 !important;
        flex: 0 0 0 !important;
        overflow: hidden !important;
    }
    [data-testid="stSidebarUserContent"] {
        overflow-y: hidden !important;
        padding-bottom: 0 !important;
    }
    /* Hide the sidebar resizer drag handle */
    [data-testid="stSidebarResizer"] {
        display: none !important;
    }
    [data-testid="stSidebar"] ::-webkit-scrollbar {
        width: 0px;
        background: transparent;
    }
    .stRadio > div {
        gap: 5px;
    }
    .stRadio label {
        font-size: 14px !important;
        font-weight: 600 !important;
        padding: 6px 10px;
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

    _render_language_toggle()
    render_custom_logo("small")
    current_role = st.session_state.get('user_role', 'Admin')
    role_badge_color = "#00ff87" if current_role == 'Admin' else "#f59e0b"
    st.markdown(f"""
    <div style="text-align: center; margin: 2px 0 8px 0;">
        <span style="font-size: 10px; font-weight: 700; color: {role_badge_color}; background: rgba(15, 23, 42, 0.85); border: 1px solid {role_badge_color}55; padding: 2px 10px; border-radius: 12px; letter-spacing: 0.5px;">● ROLE: {current_role.upper()}</span>
    </div>
    """, unsafe_allow_html=True)
    
    if current_role == 'Staff':
        nav_options = ["OCR Scanner", "Customer Khata", "Business Operations", "RAG AI Chat"]
    else:
        nav_options = ["OCR Scanner", "Customer Khata", "Business Operations", "Ledger Database", "RAG AI Chat", "Staff Management"]
        
    default_page = st.query_params.get("page", "OCR Scanner")
    if default_page not in nav_options:
        default_page = nav_options[0]
        
    selected_page = st.radio("Navigation", nav_options, index=nav_options.index(default_page), label_visibility="collapsed")
    if selected_page != st.query_params.get("page"):
        st.query_params["page"] = selected_page
        st.rerun()
    
    st.markdown("<hr style='margin: 8px 0; border-color: rgba(0, 242, 254, 0.15);'>", unsafe_allow_html=True)
    
    st.markdown('''
    <div class="dev-credit-box" style="margin-bottom: 10px; padding: 8px 10px; background: rgba(0, 242, 254, 0.05); border: 1px solid rgba(0, 242, 254, 0.25); border-radius: 8px; border-left: 3px solid #00f2fe;">
        <div style="font-size: 8px; text-transform: uppercase; color: #00f2fe; font-weight: 800; letter-spacing: 0.8px; margin-bottom: 3px;">👨‍💻 Project Developers</div>
        <div style="font-size: 10px; font-weight: 700; color: #ffffff; line-height: 1.3;">
            Sanket Kirdat &nbsp;|&nbsp; Sakshi Bhagat<br>
            Vaishnavi Dhavale &nbsp;|&nbsp; Rushikesh Mulik
        </div>
    </div>
    ''', unsafe_allow_html=True)
    
    st.markdown('<div class="logout-container">', unsafe_allow_html=True)
    if st.button("\U0001f6aa Logout System"):
        log_activity(st.session_state.get('current_username', 'admin'), "User Logged Out")
        st.session_state.clear()
        st.query_params.clear()
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

if selected_page == "OCR Scanner":
    is_english = st.session_state.get("ui_language", "en") == "en"
    header_title = "Universal Smart Scanner" if is_english else "युनिव्हर्सल स्मार्ट स्कॅनर"
    header_subtitle = "Receipts OCR & Voice Billing" if is_english else "पावत्या आणि व्हॉईस बिलिंग एकाच ठिकाणी"
    render_page_header(header_title, header_subtitle, "⚡")

    st.markdown("""
    <style>
    .scanner-viewfinder {
        border: 1px dashed rgba(0, 242, 254, 0.4);
        border-radius: 10px;
        padding: 12px 14px;
        background: rgba(0, 0, 0, 0.25);
        margin-bottom: 12px;
    }
    .scanner-pill {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 3px 10px;
        border-radius: 20px;
        font-size: 11px;
        font-weight: 700;
        background: rgba(0, 242, 254, 0.1);
        color: #00f2fe;
        border: 1px solid rgba(0, 242, 254, 0.3);
    }
    .scanner-pill-success {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 3px 10px;
        border-radius: 20px;
        font-size: 11px;
        font-weight: 700;
        background: rgba(0, 255, 135, 0.1);
        color: #00ff87;
        border: 1px solid rgba(0, 255, 135, 0.3);
    }
    .thermal-preview-wrap {
        background: #ffffff;
        color: #000000;
        border-radius: 8px;
        padding: 10px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        max-height: 340px;
        overflow-y: auto;
        font-family: 'Courier New', Courier, monospace;
        font-size: 11px;
        margin-bottom: 10px;
        border: 1px solid #cbd5e1;
    }
    [data-testid="stCameraInput"] video {
        max-height: 200px !important;
        border-radius: 8px !important;
    }
    [data-testid="stCameraInput"] img {
        max-height: 180px !important;
        border-radius: 8px !important;
    }
    </style>
    """, unsafe_allow_html=True)

    col_u, col_p = st.columns([1.1, 0.9])
    with col_u:
        st.markdown("<div class='panel-card'>", unsafe_allow_html=True)
        
        curr_mode = st.session_state.get('input_method', 'Upload File')
        if curr_mode not in ["Upload File", "Live Camera", "Multi-Language Voice Bill"]:
            curr_mode = "Upload File"
            st.session_state['input_method'] = "Upload File"

        input_method = curr_mode
        is_receipt = input_method in ["Upload File", "Live Camera"]
        is_voice = input_method == "Multi-Language Voice Bill"

        # 3 Clean Input Modes (फक्त ३ बटणे)
        m_c1, m_c2, m_c3 = st.columns(3)
        with m_c1:
            if st.button(
                "📁 फाईल गॅलरी" if not is_english else "📁 Gallery",
                type="primary" if input_method == "Upload File" else "secondary",
                use_container_width=True,
                key="btn_mode_gallery"
            ):
                st.session_state['input_method'] = "Upload File"
                st.session_state['receipt_source'] = "Upload File"
                st.rerun()
        with m_c2:
            if st.button(
                "📸 थेट कॅमेरा" if not is_english else "📸 Camera",
                type="primary" if input_method == "Live Camera" else "secondary",
                use_container_width=True,
                key="btn_mode_camera"
            ):
                st.session_state['input_method'] = "Live Camera"
                st.session_state['receipt_source'] = "Live Camera"
                st.rerun()
        with m_c3:
            if st.button(
                "🎙️ व्हॉईस बिल" if not is_english else "🎙️ Voice Bill",
                type="primary" if is_voice else "secondary",
                use_container_width=True,
                key="btn_mode_voice"
            ):
                st.session_state['input_method'] = "Multi-Language Voice Bill"
                st.rerun()

        if is_receipt:
            ctrl_c1, ctrl_c2 = st.columns([1.2, 0.8])
            with ctrl_c1:
                force_save_option = st.checkbox(
                    _translate_ui_text("⚠️ ड्युप्लिकेट पावती सेव्ह करा (Force Save)"),
                    value=False,
                    help="सक्षम केल्यास एकाच दुकानाची आणि समान रकमेची पावती आधीच डेटाबेसमध्ये असली तरीही पुन्हा सेव्ह केली जाईल."
                )
            with ctrl_c2:
                if st.session_state.get('processed_batch'):
                    if st.button("🔄 रिसेट (Reset)", key="reset_ocr_data", use_container_width=True):
                        st.session_state['processed_batch'] = []
                        st.session_state['processed_data'] = None
                        st.session_state['warning_msg'] = None
                        st.rerun()
        else:
            force_save_option = False

        up_files = []
        up_cam = None
        if input_method == "Upload File":
            up_files = st.file_uploader(
                "पावतीचा फोटो निवडा (JPG, JPEG, PNG):",
                type=["jpg", "jpeg", "png"],
                accept_multiple_files=True,
                key="ocr_receipt_files"
            )
            if up_files:
                st.markdown(f"<div style='font-size: 11px; color: #00ff87; font-weight: 700; margin: 4px 0;'>📸 निवडलेल्या पावत्या ({len(up_files)}):</div>", unsafe_allow_html=True)
                cols = st.columns(min(len(up_files), 5))
                for idx, uf in enumerate(up_files[:5]):
                    with cols[idx]:
                        st.image(uf, width=65)
                if len(up_files) > 5:
                    st.caption(f"+ आणखी {len(up_files)-5} पावत्या")

        elif input_method == "Live Camera":
            st.markdown("""
            <div style='font-size: 11px; color: #94a3b8; margin-bottom: 4px;'>
                📸 पावती फ्रेममध्ये सपाट व स्पष्ट दिसू द्या:
            </div>
            """, unsafe_allow_html=True)
            up_cam = st.camera_input("Take photo", label_visibility="collapsed", key="ocr_live_cam")

        elif input_method == "Multi-Language Voice Bill":
            st.markdown("""
            <div class='scanner-viewfinder' style='border-color: rgba(0, 242, 254, 0.5);'>
                <div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;'>
                    <span class='scanner-pill'>🎙️ AI Voice Studio (Neural Audio Engine)</span>
                    <span class='scanner-pill-success'>● ध्वनी ओळख सज्ज</span>
                </div>
                <div style='font-size: 12px; color: #cbd5e1; line-height: 1.4;'>
                    माइकवर क्लिक करून बिल बोला. AI सर्व वस्तू, प्रमाण आणि किमती आपोआप मोजून बिल तयार करेल.
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            voice_lang_choice = st.radio(
                "भाषा निवडा (Select Language):",
                ["मराठी (mr-IN)", "हिंदी (hi-IN)", "English (en-IN)"],
                index=0,
                horizontal=True,
                key="voice_billing_lang_radio"
            )
            lang_code_map = {
                "मराठी (mr-IN)": "mr-IN",
                "हिंदी (hi-IN)": "hi-IN",
                "English (en-IN)": "en-IN"
            }
            chosen_lang = lang_code_map.get(voice_lang_choice, "mr-IN")
            
            spoken_bill = speech_to_text(
                start_prompt="🎙️ बोलणे सुरू करा (माइक दाबा)",
                stop_prompt="⏹️ बोलणे थांबवा (तयार करा)",
                just_once=True,
                language=chosen_lang,
                key='voice_billing_mic_auto'
            )
            
            if 'voice_billing_transcript' not in st.session_state:
                st.session_state['voice_billing_transcript'] = ""
                
            if spoken_bill and spoken_bill.strip():
                if spoken_bill.strip() != st.session_state.get('last_spoken_bill'):
                    st.session_state['last_spoken_bill'] = spoken_bill.strip()
                    st.session_state['voice_billing_transcript'] = spoken_bill.strip()
            
            st.markdown("<div style='font-size: 12px; font-weight: 700; color: #00f2fe; margin-top: 10px; margin-bottom: 4px;'>📝 ओळखलेला मजकूर / टाइप करून बिल बनवा:</div>", unsafe_allow_html=True)
            voice_text_input = st.text_area(
                "Voice Input Text",
                value=st.session_state.get('voice_billing_transcript', ''),
                height=75,
                placeholder="उदा. श्री गणेश किराणा: ५ किलो साखर २०० रुपये, २ लिटर तेल ३०० रुपये",
                label_visibility="collapsed",
                key="voice_billing_transcript_input"
            )
            st.session_state['voice_billing_transcript'] = voice_text_input
            
            submit_voice = st.button("⚡ व्हॉईस बिल प्रोसेस करा (Generate Bill)", type="primary", use_container_width=True, key="btn_process_voice_bill")
            
            active_voice_text = st.session_state.get('voice_billing_transcript', '').strip()
            if submit_voice:
                if not active_voice_text:
                    st.warning("⚠️ कृपया आधी माईकवर बोला किंवा वरील बॉक्समध्ये मजकूर टाइप करा.")
                else:
                    with st.spinner("🤖 AI गणिती पडताळणी करत आहे... व्हॉईसवरून अचूक बिल तयार होत आहे..."):
                        try:
                            v_data = process_voice_billing_advanced(active_voice_text, API_KEY)
                            st.session_state['processed_data'] = v_data
                            st.session_state['processed_batch'] = [v_data]
                            log_activity(st.session_state.get('current_username', 'admin'), "Processed Voice Bill")
                            st.success("✅ व्हॉईस बिल यशस्वीरित्या तयार होऊन डेटाबेसमध्ये सेव्ह झाले!")
                            st.toast("व्हॉईस बिल सेव्ह झाले!", icon="🎤")
                            st.rerun()
                        except Exception as ve:
                            logging.error(f"Voice billing error: {ve}")
                            st.error(f"व्हॉईस बिल Error: {ve}")

        if input_method != "Multi-Language Voice Bill":
            st.write("")
            process_clicked = st.button("⚡ पावत्या स्कॅन करा (Process Receipts)", type="primary", use_container_width=True, key="btn_process_receipts")
            if process_clicked:
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
                    
                    def process_single_file(idx, single_file):
                        try:
                            data = process_receipt_advanced(single_file, API_KEY, force_save=force_save_option)
                            f_name = getattr(single_file, "name", f"पावती #{idx+1}")
                            if data.get("is_duplicate"):
                                warn_msg = f"दुकान '{data.get('vendor_name')}' चे ₹{data.get('grand_total')} चे बिल आधीच रेकॉर्ड केलेले आहे."
                                return (idx, data, (f_name, f"Duplicate Warning: {warn_msg}"))
                            return (idx, data, None)
                        except Exception as e:
                            f_name = getattr(single_file, "name", f"पावती #{idx+1}")
                            err_str = str(e)
                            return (idx, None, (f_name, err_str))

                    with st.spinner(f"🚀 AI Vision Engine {total_f} पावत्या एकाच वेळी स्कॅन करत आहे... कृपया वाट पहा!"):
                        with concurrent.futures.ThreadPoolExecutor(max_workers=min(total_f, 10)) as executor:
                            futures = {executor.submit(process_single_file, i, f): i for i, f in enumerate(target_files)}
                            
                            results = []
                            completed_count = 0
                            for future in concurrent.futures.as_completed(futures):
                                results.append(future.result())
                                completed_count += 1
                                progress_bar.progress(completed_count / total_f)
                                status_text.markdown(f"<span class='scanner-pill'>⚡ पावती स्कॅन सुरू ({completed_count}/{total_f})...</span>", unsafe_allow_html=True)
                                
                            results.sort(key=lambda x: x[0])
                            
                            for idx, data, err in results:
                                if data:
                                    processed_batch.append(data)
                                if err:
                                    fname, err_str = err
                                    if "Duplicate Warning:" in err_str:
                                        clean_err = err_str.split("Duplicate Warning:")[-1].strip()
                                        warning_messages.append(f"⚠️ {clean_err}")
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
                        st.success(f"✅ {len(processed_batch)} पावती/पावत्या यशस्वीरित्या स्कॅन झाल्या!")
                        st.toast("पावती Successfully स्कॅन झाली!", icon="✅")
                        st.rerun()
                    else:
                        if warning_messages:
                            st.error("पावती स्कॅन करताना अडचण आली: " + " | ".join(warning_messages))
                        else:
                            st.error("पावती स्कॅन करता आली नाही. कृपया पावतीचा फोटो स्पष्ट असल्याची खात्री करा.")
                else:
                    st.warning("⚠️ कृपया किमान एक पावती निवडा किंवा कॅमेऱ्याने फोटो घ्या.")
        
        if st.session_state.get('warning_msg'):
            elapsed = time.time() - st.session_state.get('warning_time', 0)
            if elapsed < 15:
                st.warning(f"ड्युप्लिकेट पावती अलर्ट: {st.session_state['warning_msg']}")
        st.markdown("</div>", unsafe_allow_html=True)
        
    with col_p:
        st.markdown("<div class='panel-card'>", unsafe_allow_html=True)
        batch_data = st.session_state.get('processed_batch', [])
        if batch_data:
            if len(batch_data) == 1:
                p_item = batch_data[0]
                v_disp = decode_unicode(p_item.get('vendor_name'))
                tot = float(p_item.get('grand_total', 0) or 0)
                items_raw = p_item.get('items', [])
                date_disp = p_item.get('date', 'Today') or 'Today'
                cat_disp = p_item.get('category', 'General') or 'General'
                
                # Compact Receipt Header (No big POS card)
                st.markdown(f"""
                <div style='display: flex; justify-content: space-between; align-items: center; background: rgba(0, 242, 254, 0.08); border: 1px solid rgba(0, 242, 254, 0.25); border-radius: 8px; padding: 8px 12px; margin-bottom: 8px;'>
                    <div>
                        <div style='font-size: 15px; font-weight: 800; color: #00f2fe;'>🧾 {v_disp}</div>
                        <div style='font-size: 11px; color: #94a3b8;'>📅 {date_disp} • 🏷️ {cat_disp} • {len(items_raw)} वस्तू</div>
                    </div>
                    <div style='text-align: right;'>
                        <div style='font-size: 10px; color: #94a3b8;'>एकूण रक्कम</div>
                        <div style='font-size: 18px; font-weight: 800; color: #00ff87;'>₹{tot:,.2f}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Pure Thermal Receipt (No Scan & Pay, No Sound Box)
                thermal_html = generate_thermal_receipt_html(v_disp, date_disp, cat_disp, items_raw, tot, receipt_no="1", is_english=is_english)
                
                # Embedded Compact Thermal Receipt Preview
                st.components.v1.html(thermal_html, height=310, scrolling=True)
                
                # Clearly Display Scanned Items Table
                if items_raw:
                    st.markdown("<div style='font-size: 13px; font-weight: 700; color: #00f2fe; margin-top: 10px; margin-bottom: 6px;'>📋 स्कॅन केलेल्या वस्तूंचा तपशील (Scanned Items):</div>", unsafe_allow_html=True)
                    clean_items_display = []
                    for idx_item, itm in enumerate(items_raw, 1):
                        name_val = str(itm.get("item_name", f"Item {idx_item}")).strip()
                        qty_val = str(itm.get("quantity", itm.get("qty", "1"))).strip()
                        rate_val = float(itm.get("rate", itm.get("price", 0)) or 0)
                        tot_val = float(itm.get("total_price", rate_val) or 0)
                        clean_items_display.append({
                            "क्र.": idx_item,
                            "वस्तूचे नाव (Item)": name_val,
                            "प्रमाण (Qty)": qty_val,
                            "दर (Rate ₹)": f"₹{rate_val:,.2f}",
                            "एकूण (Total ₹)": f"₹{tot_val:,.2f}"
                        })
                    st.dataframe(pd.DataFrame(clean_items_display), hide_index=True, use_container_width=True)
                
                # Action Buttons Row
                btn_col1, btn_col2 = st.columns(2)
                with btn_col1:
                    st.download_button(
                        label="🖨️ थर्मल पावती (Print / Download)",
                        data=thermal_html,
                        file_name=f"Thermal_Slip_{v_disp.replace(' ', '_')}.html",
                        mime="text/html",
                        use_container_width=True,
                        type="primary",
                        key="btn_download_thermal_single"
                    )
                with btn_col2:
                    if st.button('📦 इन्व्हेंटरी अपडेट (Sync Stock)', key='inv_sync_single', use_container_width=True):
                        try:
                            with sqlite3.connect('ledger.db') as conn:
                                cursor = conn.cursor()
                                for item in p_item.get('items', []):
                                    i_name = str(item.get('item_name', '')).strip()
                                    if not i_name:
                                        continue
                                    q_raw = str(item.get('quantity', item.get('qty', '1'))).split()[0]
                                    try:
                                        q_val = float(q_raw)
                                    except (ValueError, TypeError):
                                        q_val = 1.0
                                    r_val = float(item.get('rate', item.get('price', 0.0)) or 0.0)
                                    cursor.execute("SELECT id, stock_qty FROM shop_inventory WHERE item_name = ?", (i_name,))
                                    row = cursor.fetchone()
                                    if row:
                                        new_qty = float(row[1] or 0.0) + q_val
                                        cursor.execute("UPDATE shop_inventory SET stock_qty = ? WHERE id = ?", (new_qty, row[0]))
                                    else:
                                        cursor.execute(
                                            "INSERT INTO shop_inventory (item_name, stock_qty, unit, alert_limit, barcode, selling_price) VALUES (?, ?, ?, ?, ?, ?)",
                                            (i_name, q_val, 'units', 5.0, '', r_val)
                                        )
                                conn.commit()
                            st.toast('📦 स्टॉक आपोआप अपडेट झाला!', icon="📦")
                            st.success('इन्व्हेंटरी यशस्वीरित्या अपडेट झाली!')
                        except Exception as e:
                            st.error(str(e))
                
                # Compact Optional Edit Items in collapsed expander
                items_df = pd.DataFrame(items_raw)
                if not items_df.empty:
                    with st.expander("✏️ वस्तू / किमती तपासा किंवा बदला (Edit Items)", expanded=False):
                        edited_df = st.data_editor(items_df, use_container_width=True, key='data_editor_single')
                        p_item['items'] = edited_df.to_dict('records')
            else:
                combined_tot = sum(float(b.get('grand_total', 0) or 0) for b in batch_data)
                total_items_count = sum(len(b.get('items', [])) for b in batch_data)
                
                # Compact Batch Header
                st.markdown(f"""
                <div style='display: flex; justify-content: space-between; align-items: center; background: rgba(0, 242, 254, 0.08); border: 1px solid rgba(0, 242, 254, 0.25); border-radius: 8px; padding: 8px 12px; margin-bottom: 8px;'>
                    <div>
                        <div style='font-size: 15px; font-weight: 800; color: #00f2fe;'>🧾 {len(batch_data)} पावत्या स्कॅन झाल्या</div>
                        <div style='font-size: 11px; color: #94a3b8;'>एकूण {total_items_count} वस्तू</div>
                    </div>
                    <div style='text-align: right;'>
                        <div style='font-size: 10px; color: #94a3b8;'>एकत्रित रक्कम</div>
                        <div style='font-size: 18px; font-weight: 800; color: #00ff87;'>₹{combined_tot:,.2f}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Top Action Row: Sync All + Download All Slips
                c_sync_all, c_dl_all = st.columns(2)
                with c_sync_all:
                    if st.button('📦 सर्व पावत्या इन्व्हेंटरीमध्ये जोडा (Sync All Stock)', key='inv_sync_all_batch', use_container_width=True):
                        try:
                            with sqlite3.connect('ledger.db') as conn:
                                cursor = conn.cursor()
                                for b_item in batch_data:
                                    for item in b_item.get('items', []):
                                        i_name = str(item.get('item_name', '')).strip()
                                        if not i_name:
                                            continue
                                        q_raw = str(item.get('quantity', item.get('qty', '1'))).split()[0]
                                        try:
                                            q_val = float(q_raw)
                                        except (ValueError, TypeError):
                                            q_val = 1.0
                                        r_val = float(item.get('rate', item.get('price', 0.0)) or 0.0)
                                        cursor.execute("SELECT id, stock_qty FROM shop_inventory WHERE item_name = ?", (i_name,))
                                        row = cursor.fetchone()
                                        if row:
                                            new_qty = float(row[1] or 0.0) + q_val
                                            cursor.execute("UPDATE shop_inventory SET stock_qty = ? WHERE id = ?", (new_qty, row[0]))
                                        else:
                                            cursor.execute(
                                                "INSERT INTO shop_inventory (item_name, stock_qty, unit, alert_limit, barcode, selling_price) VALUES (?, ?, ?, ?, ?, ?)",
                                                (i_name, q_val, 'units', 5.0, '', r_val)
                                            )
                                conn.commit()
                            st.toast('📦 सर्व पावत्यांचा स्टॉक जोडला गेला!', icon="📦")
                            st.success('इन्व्हेंटरी यशस्वीरित्या अपडेट झाली!')
                        except Exception as e:
                            st.error(str(e))
                with c_dl_all:
                    # Generate all thermal slips in 1 HTML file for batch printing
                    all_slips_html = """<!DOCTYPE html><html><head><meta charset='utf-8'><title>All Receipts</title><style>@page { size: 58mm auto; margin: 0; } body { width: 54mm; margin: 0 auto; padding: 4px; font-family: 'Courier New', monospace; } .page-sep { page-break-after: always; border-top: 2px dashed #000; margin: 20px 0; }</style></head><body>"""
                    for b_i, b_obj in enumerate(batch_data, 1):
                        b_v = decode_unicode(b_obj.get('vendor_name'))
                        b_tot = float(b_obj.get('grand_total', 0) or 0)
                        b_its = b_obj.get('items', [])
                        b_dt = b_obj.get('date', 'Today') or 'Today'
                        all_slips_html += generate_thermal_receipt_html(b_v, b_dt, "General", b_its, b_tot, receipt_no=str(b_i), is_english=is_english)
                        if b_i < len(batch_data):
                            all_slips_html += "<div class='page-sep'></div>"
                    all_slips_html += "</body></html>"
                    st.download_button(
                        label=f"🖨️ सर्व {len(batch_data)} पावत्या एकत्र डाउनलोड",
                        data=all_slips_html,
                        file_name=f"All_{len(batch_data)}_Thermal_Slips.html",
                        mime="text/html",
                        use_container_width=True,
                        key="btn_dl_all_slips_batch"
                    )

                st.markdown("<hr style='margin: 10px 0 8px 0; border-color: rgba(0, 242, 254, 0.2);'>", unsafe_allow_html=True)
                
                # Receipt Selector Dropdown (पावती सिलेक्टर ड्रॉपडाऊन)
                receipt_labels = [
                    f"🧾 पावती #{i+1}: {decode_unicode(b.get('vendor_name', 'अनामित'))} — ₹{float(b.get('grand_total', 0) or 0):,.2f} ({len(b.get('items', []))} वस्तू)"
                    for i, b in enumerate(batch_data)
                ]
                st.markdown("<div style='font-size: 13px; font-weight: 700; color: #00f2fe; margin-bottom: 4px;'>📋 पाहण्यासाठी पावती निवडा (Select Receipt):</div>", unsafe_allow_html=True)
                selected_idx = st.selectbox(
                    "पावती निवडा",
                    range(len(batch_data)),
                    format_func=lambda i: receipt_labels[i],
                    label_visibility="collapsed",
                    key="batch_receipt_dropdown_selector"
                )

                # Show Selected Receipt Details
                p_item = batch_data[selected_idx]
                v_disp = decode_unicode(p_item.get('vendor_name'))
                tot = float(p_item.get('grand_total', 0) or 0)
                items_raw = p_item.get('items', [])
                date_disp = p_item.get('date', 'Today') or 'Today'
                cat_disp = p_item.get('category', 'General') or 'General'

                # Thermal Slip Preview of Selected Receipt
                b_thermal_html = generate_thermal_receipt_html(v_disp, date_disp, cat_disp, items_raw, tot, receipt_no=str(selected_idx+1), is_english=is_english)
                st.components.v1.html(b_thermal_html, height=310, scrolling=True)

                # Items Table of Selected Receipt
                if items_raw:
                    st.markdown(f"<div style='font-size: 13px; font-weight: 700; color: #00f2fe; margin-top: 10px; margin-bottom: 6px;'>📋 पावती #{selected_idx+1} चा वस्तू तपशील ({len(items_raw)} वस्तू):</div>", unsafe_allow_html=True)
                    clean_b_items = []
                    for bi_idx, bi in enumerate(items_raw, 1):
                        clean_b_items.append({
                            "क्र.": bi_idx,
                            "वस्तूचे नाव (Item)": str(bi.get("item_name", f"Item {bi_idx}")).strip(),
                            "प्रमाण (Qty)": str(bi.get("quantity", bi.get("qty", "1"))).strip(),
                            "दर (Rate ₹)": f"₹{float(bi.get('rate', bi.get('price', 0)) or 0):,.2f}",
                            "एकूण (Total ₹)": f"₹{float(bi.get('total_price', 0) or 0):,.2f}"
                        })
                    st.dataframe(pd.DataFrame(clean_b_items), hide_index=True, use_container_width=True)

                # Action Buttons for Selected Receipt
                b_c1, b_c2 = st.columns(2)
                with b_c1:
                    st.download_button(
                        label=f"🖨️ पावती #{selected_idx+1} डाउनलोड / प्रिंट",
                        data=b_thermal_html,
                        file_name=f"Thermal_Slip_{v_disp.replace(' ', '_')}_{selected_idx+1}.html",
                        mime="text/html",
                        use_container_width=True,
                        type="primary",
                        key=f"btn_dl_thermal_sel_{selected_idx}"
                    )
                with b_c2:
                    if st.button(f'📦 पावती #{selected_idx+1} स्टॉक अपडेट', key=f'inv_sync_sel_{selected_idx}', use_container_width=True):
                        try:
                            with sqlite3.connect('ledger.db') as conn:
                                cursor = conn.cursor()
                                for item in items_raw:
                                    i_name = str(item.get('item_name', '')).strip()
                                    if not i_name:
                                        continue
                                    q_raw = str(item.get('quantity', item.get('qty', '1'))).split()[0]
                                    try:
                                        q_val = float(q_raw)
                                    except (ValueError, TypeError):
                                        q_val = 1.0
                                    r_val = float(item.get('rate', item.get('price', 0.0)) or 0.0)
                                    cursor.execute("SELECT id, stock_qty FROM shop_inventory WHERE item_name = ?", (i_name,))
                                    row = cursor.fetchone()
                                    if row:
                                        new_qty = float(row[1] or 0.0) + q_val
                                        cursor.execute("UPDATE shop_inventory SET stock_qty = ? WHERE id = ?", (new_qty, row[0]))
                                    else:
                                        cursor.execute(
                                            "INSERT INTO shop_inventory (item_name, stock_qty, unit, alert_limit, barcode, selling_price) VALUES (?, ?, ?, ?, ?, ?)",
                                            (i_name, q_val, 'units', 5.0, '', r_val)
                                        )
                                conn.commit()
                            st.toast(f'पावती #{selected_idx+1} चा स्टॉक अपडेट झाला!', icon="📦")
                            st.success(f'पावती #{selected_idx+1} चा स्टॉक यशस्वीरित्या अपडेट झाला!')
                        except Exception as e:
                            st.error(str(e))

                # Optional Edit Items in Expander
                items_df = pd.DataFrame(items_raw)
                if not items_df.empty:
                    with st.expander(f"✏️ पावती #{selected_idx+1} मधील वस्तू / किमती तपासा किंवा बदला (Edit Items)", expanded=False):
                        edited_df = st.data_editor(items_df, use_container_width=True, key=f'data_editor_batch_sel_{selected_idx}')
                        p_item['items'] = edited_df.to_dict('records')
        else:
            st.markdown("""
            <div style='text-align: center; padding: 25px 15px;'>
                <div style='font-size: 36px; margin-bottom: 8px;'>🧾</div>
                <div style='font-size: 15px; font-weight: 700; color: #00f2fe; margin-bottom: 4px;'>स्मार्ट पावती स्कॅनर</div>
                <div style='font-size: 12px; color: #94a3b8; max-width: 300px; margin: 0 auto; line-height: 1.5;'>
                    डाव्या बाजूला पावती निवडा किंवा फोटो काढा, क्षणात ५८mm थर्मल पावती तयार होईल.
                </div>
                <div style='margin-top: 14px; display: flex; justify-content: center; gap: 8px;'>
                    <span class='scanner-pill'>⚡ 58mm Thermal Slip</span>
                    <span class='scanner-pill-success'>🎙️ Voice Bill</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

# FEATURE 3: ADVANCED CUSTOMER KHATA ---
elif selected_page == "Customer Khata":
    render_customer_khata()

# FEATURE 4: STOCK & INVENTORY ---
elif selected_page == "Business Operations":
    render_business_module_styles()
    render_page_header("Business Operations", "इन्व्हेंटरी आणि व्यवसाय खर्च एकाच ठिकाणी व्यवस्थापित करा.", "💼")

    tab_stock, tab_expenses, tab_shop_profile = st.tabs([
        "📦 Stock & Inventory", 
        "💸 Business Expenses", 
        "⚙️ Shop Profile & UPI"
    ])
    
    with tab_stock:
        # Staff can now access this
        st.markdown("<div style='font-size: 16px; font-weight: 800; color: #00ff87; margin-bottom: 12px;'>📦 साठा आणि इन्व्हेंटरी डॅशबोर्ड</div>", unsafe_allow_html=True)

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
                s_name = st.text_input("Item Name (वस्तूचे नाव)")
                s_qty = st.number_input("Stock Quantity (साठा प्रमाण)", min_value=0.0, step=1.0)
                s_price = st.number_input("Selling Price (विक्री दर ₹)", min_value=0.0, step=5.0, value=0.0)
                s_unit = st.text_input("Unit (उदा. kg, pcs, ltr)", value="kg")
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
                                INSERT INTO shop_inventory (item_name, stock_qty, unit, alert_limit, barcode, selling_price)
                                VALUES (?, ?, ?, ?, ?, ?)
                                """, (s_name.strip(), s_qty, s_unit.strip(), s_limit, "", s_price))
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
                stock_df['alert_limit'] = pd.to_numeric(stock_df.get('alert_limit', 5.0), errors='coerce').fillna(5.0)
                stock_df['stock_qty'] = pd.to_numeric(stock_df.get('stock_qty', 0.0), errors='coerce').fillna(0.0)
                if 'selling_price' in stock_df.columns:
                    stock_df['selling_price'] = pd.to_numeric(stock_df['selling_price'], errors='coerce').fillna(0.0)
                else:
                    stock_df['selling_price'] = 0.0

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
                if 'barcode' in display_df.columns:
                    display_df = display_df.drop(columns=['barcode'])
                display_df.insert(0, 'Status', display_df.apply(lambda row: "🚨 Low Stock" if float(row.get('stock_qty', 0.0) or 0.0) <= float(row.get('alert_limit', 5.0) or 5.0) else "✅ In Stock", axis=1))
                st.dataframe(display_df,  hide_index=True)
                if not low_stock_items.empty:
                    # 🧠 AI PREDICTIVE REORDER LIST & WHOLESALE ORDER
                    with st.expander("🧠 AI स्मार्ट साठा अंदाज आणि खरेदी यादी (AI Reorder List)", expanded=True):
                        st.markdown("<div style='font-size:12px; color:#94a3b8; margin-bottom:8px;'>AI ने खपाच्या गतीनुसार खालीलप्रमाणे नवीन माल भरण्याचा अंदाज तयार केला आहे:</div>", unsafe_allow_html=True)
                        reorder_rows = []
                        order_lines = []
                        for _, r in low_stock_items.iterrows():
                            try:
                                c_qty = float(r.get('stock_qty', 0.0) or 0.0)
                            except (ValueError, TypeError):
                                c_qty = 0.0
                            try:
                                a_lim = float(r.get('alert_limit', 5.0) or 5.0)
                            except (ValueError, TypeError):
                                a_lim = 5.0
                            t_unit = str(r.get('unit', 'units') or 'units')
                            needed = max(1.0, math.ceil((a_lim * 3.0) - c_qty))
                            reorder_rows.append({
                                "वस्तू (Item)": str(r.get('item_name', '')),
                                "सध्याचा साठा": f"{c_qty:g} {t_unit}",
                                "सूचना मर्यादा": f"{a_lim:g} {t_unit}",
                                "खरेदी शिफारस": f"{needed:g} {t_unit}"
                            })
                            order_lines.append(f"• {r.get('item_name', '')}: {needed:g} {t_unit}")
                        
                        st.dataframe(pd.DataFrame(reorder_rows), hide_index=True, use_container_width=True)
                        
                        wh_order_text = "🛒 *नवीन माल खरेदी ऑर्डर (Wholesale Purchase Order)*\nदुकानाचे नाव: VernaLedger Store\nतारीख: " + date.today().strftime('%d-%m-%Y') + "\n\n" + "\n".join(order_lines) + "\n\nकृपया लवकरात लवकर डिलिव्हरी पाठवावी. धन्यवाद!"
                        wh_link = f"https://wa.me/?text={urllib.parse.quote(wh_order_text)}"
                        st.markdown(f"""
                        <a href="{wh_link}" target="_blank" style="text-decoration: none;">
                            <button style="width: 100%; height: 38px; border-radius: 8px; background: rgba(0, 242, 254, 0.15); border: 1px solid #00f2fe; color: #00f2fe; font-size: 12px; font-weight: 700; cursor: pointer; display: flex; align-items: center; justify-content: center; gap: 6px; margin-top: 8px; margin-bottom: 12px;">
                                📲 घाऊक व्यापाऱ्याला व्हॉट्सॲप ऑर्डर पाठवा (WhatsApp to Supplier)
                            </button>
                        </a>
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
    with tab_expenses:
        # Staff can now access this

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
                exp_df['amount'] = pd.to_numeric(exp_df['amount'], errors='coerce').fillna(0.0)
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

    with tab_shop_profile:
        st.markdown("<div class='panel-card'>", unsafe_allow_html=True)
        st.markdown("""
        <div class="business-section-heading">
            <div class="business-section-icon">⚙️</div>
            <div>
                <h3 class="business-section-title">Shop Profile & UPI Configuration</h3>
                <p class="business-section-caption">दुकानाचे नाव, पत्ता आणि खरा UPI ID सेट करा. हे तपशील थर्मल पावती, QR कोड आणि व्हॉट्सॲप मेसेजमध्ये आपोआप वापरले जातील.</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

        cur_shop_name = get_shop_setting("shop_name", "VernaLedger Store")
        cur_shop_owner = get_shop_setting("shop_owner", "VernaLedger Admin")
        cur_shop_upi = get_shop_setting("shop_upi_id", "vernaledger@upi")
        cur_shop_phone = get_shop_setting("shop_phone", "+91 9822000000")
        cur_shop_addr = get_shop_setting("shop_address", "मेन मार्केट रोड, सातारा, महाराष्ट्र")
        cur_shop_tagline = get_shop_setting("shop_tagline", "धन्यवाद! पुन्हा भेट द्या.")
        cur_shop_gstin = get_shop_setting("shop_gstin", "27AAAAA0000A1Z5")

        prof_c1, prof_c2 = st.columns([1.1, 0.9])
        with prof_c1:
            with st.form("shop_profile_form"):
                st.markdown("##### 🏪 दुकानाचे मूळ तपशील (Store Information):")
                f_name = st.text_input("दुकानाचे नाव (Shop / Store Name):", value=cur_shop_name)
                f_owner = st.text_input("मालक / प्राप्तकर्त्याचे नाव (Payee / Owner Name):", value=cur_shop_owner)
                f_upi = st.text_input("व्यवसायाचा खरा UPI ID (Business UPI ID e.g. shop@okaxis):", value=cur_shop_upi, help="ग्राहक QR स्कॅन केल्यावर या UPI आयडीवर थेट रक्कम जमा होईल.")
                
                f_col_sub1, f_col_sub2 = st.columns(2)
                with f_col_sub1:
                    f_phone = st.text_input("मोबाईल / संपर्क क्रमांक:", value=cur_shop_phone)
                with f_col_sub2:
                    f_gstin = st.text_input("GSTIN (ऐच्छिक):", value=cur_shop_gstin)
                
                f_addr = st.text_area("दुकानाचा पत्ता (Shop Address):", value=cur_shop_addr, height=70)
                f_tagline = st.text_input("पावतीवरील शुभेच्छा / तळटीप (Receipt Footer):", value=cur_shop_tagline)

                save_prof_btn = st.form_submit_button("💾 प्रोफाइल व UPI सेव्ह करा (Save Configuration)", type="primary", use_container_width=True)
                if save_prof_btn:
                    if not f_name.strip() or not f_upi.strip():
                        st.error("कृपया दुकानाचे नाव आणि UPI ID भरा!")
                    else:
                        set_shop_setting("shop_name", f_name.strip())
                        set_shop_setting("shop_owner", f_owner.strip())
                        set_shop_setting("shop_upi_id", f_upi.strip())
                        set_shop_setting("shop_phone", f_phone.strip())
                        set_shop_setting("shop_address", f_addr.strip())
                        set_shop_setting("shop_tagline", f_tagline.strip())
                        set_shop_setting("shop_gstin", f_gstin.strip())
                        log_activity(st.session_state.get('current_username', 'admin'), "Updated Shop Profile & UPI Settings")
                        st.toast("✅ दुकानाची माहिती व UPI ID सुरक्षित सेव्ह झाले!", icon="💾")
                        st.success("सर्व बदल यशस्वीरित्या जतन झाले! पावती व QR कोड त्वरित अपडेट झाले आहेत.")
                        st.rerun()

        with prof_c2:
            st.markdown("##### ⚡ थेट UPI टेस्ट QR कोड (Live Test Preview):")
            test_amt = st.number_input("चाचणी रक्कम (Test ₹):", min_value=1.0, value=10.0, step=10.0, key="upi_test_amt_input")
            
            test_qr_b64 = generate_upi_qr_base64(test_amt, vpa=cur_shop_upi, payee_name=cur_shop_owner or cur_shop_name, note="UPI Verification")
            
            st.markdown(f"""
            <div style='background:rgba(0,0,0,0.35); border:1px dashed rgba(0, 242, 254, 0.5); border-radius:12px; padding:16px; text-align:center;'>
                <div style='font-size:12px; font-weight:700; color:#00f2fe; margin-bottom:4px;'>{cur_shop_name}</div>
                <div style='font-size:11px; color:#94a3b8; margin-bottom:10px;'>UPI ID: <code style='color:#00ff87;'>{cur_shop_upi}</code></div>
                <img src="data:image/png;base64,{test_qr_b64}" style="width: 140px; height: 140px; border-radius: 8px; background: white; padding: 6px; box-shadow: 0 4px 15px rgba(0,0,0,0.5);" />
                <div style='font-size:16px; font-weight:800; color:#00ff87; margin-top:8px;'>₹{test_amt:,.2f}</div>
                <div style='font-size:10px; color:#cbd5e1; margin-top:4px;'>
                    हा QR तुमच्या मोबाईलवरील GPay, PhonePe किंवा Paytm ने स्कॅन करून थेट पडताळणी करू शकता.
                </div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("<div style='margin-top:14px;'>", unsafe_allow_html=True)
            st.markdown(f"""
            <div style='background:rgba(255,255,255,0.04); border-left:3px solid #00f2fe; padding:10px; border-radius:4px;'>
                <div style='font-size:11px; font-weight:700; color:#00f2fe;'>🧾 पावती हेडर पूर्वावलोकन (POS Slip Header):</div>
                <div style='font-size:12px; font-weight:bold; color:#fff; margin-top:4px;'>{cur_shop_name}</div>
                <div style='font-size:10px; color:#94a3b8;'>{cur_shop_addr}</div>
                <div style='font-size:10px; color:#94a3b8;'>मोबाईल: {cur_shop_phone} | GST: {cur_shop_gstin}</div>
            </div>
            """, unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)
    
# FEATURE 6: ADMIN STAFF MANAGEMENT ---
elif selected_page == "Staff Management":
    is_english = st.session_state.get("ui_language", "en") == "en"
    if st.session_state.get('user_role') == 'Staff':
        st.error("Restricted Area: Staff not allowed on Staff Management page!" if is_english else "प्रतिबंधित क्षेत्र: कर्मचाऱ्यांना स्टाफ व्यवस्थापन पानावर प्रवेश नाही!")
        st.stop()

    page_title = "Staff Management" if is_english else "स्टाफ व्यवस्थापन"
    page_subtitle = "Create and manage staff accounts with role-based access control." if is_english else "नवीन कर्मचारी खाती तयार करा आणि भूमिका नियंत्रण व्यवस्थापित करा."
    render_page_header(page_title, page_subtitle, "👥")

    sc1, sc2 = st.columns([1, 1])
    with sc1:
        st.markdown("<div class='panel-card'>", unsafe_allow_html=True)
        form_heading = "Add New Staff or Admin" if is_english else "नवीन स्टाफ किंवा ॲडमिन जोडा"
        st.markdown(f"<h4 style='color:#00f2fe; margin-top:0;'>{form_heading}</h4>", unsafe_allow_html=True)

        with st.form("new_staff_form"):
            user_lbl = "Username" if is_english else "वापरकर्ता नाव (Username)"
            phone_lbl = "Phone Number" if is_english else "मोबाईल नंबर (Phone Number)"
            pass_lbl = "Password (Min 6 digits)" if is_english else "पासवर्ड (किमान ६ अंक/अक्षरे)"
            role_lbl = "Role" if is_english else "भूमिका (Role)"

            s_user = st.text_input(user_lbl, key="staff_reg_user")
            s_phone = st.text_input(phone_lbl, key="staff_reg_phone")
            s_pass = st.text_input(pass_lbl, type="password", key="staff_reg_pass")

            if is_english:
                role_opts = ["Staff (Cashier - Limited Access)", "Admin (Owner - Full Access)"]
            else:
                role_opts = ["कर्मचारी (कॅशियर - मर्यादित प्रवेश)", "ॲडमिन (मालक - पूर्ण प्रवेश)"]

            s_role = st.selectbox(role_lbl, role_opts, key="staff_reg_role")
            submit_btn_lbl = "Create Account" if is_english else "खाते तयार करा"
            submit_new_user = st.form_submit_button(submit_btn_lbl)

            if submit_new_user:
                if not s_user.strip() or not s_phone.strip() or len(s_pass) < 6:
                    err_msg = "Please fill all fields and enter a password of at least 6 digits!" if is_english else "सर्व माहिती भरणे आणि पासवर्ड किमान ६ अंकी असणे आवश्यक आहे!"
                    st.error(err_msg)
                else:
                    role_val = "Staff" if ("Staff" in s_role or "कर्मचारी" in s_role) else "Admin"
                    pass_hashed = hash_password_secure(s_pass)
                    try:
                        with sqlite3.connect("ledger.db") as conn:
                            conn.execute("BEGIN TRANSACTION;")
                            cursor = conn.cursor()
                            cursor.execute(
                                "INSERT INTO users (username, password_hash, role, phone) VALUES (?, ?, ?, ?)",
                                (s_user.strip(), pass_hashed, role_val, s_phone.strip()),
                            )
                            conn.commit()
                        log_activity(st.session_state.get('current_username', 'admin'), f"Created User {s_user.strip()} as {role_val}")
                        succ_msg = f"New '{role_val}' account ({s_user.strip()}) successfully created!" if is_english else f"नवीन '{role_val}' खाते ({s_user.strip()}) यशस्वीरित्या तयार झाले!"
                        st.success(succ_msg)
                        time.sleep(0.5)
                        st.rerun()
                    except Exception:
                        dup_msg = "Error: Username already exists or database error occurred." if is_english else "त्रुटी: हे वापरकर्ता नाव आधीच अस्तित्वात आहे किंवा डेटाबेस त्रुटी आली."
                        st.error(dup_msg)
        st.markdown("</div>", unsafe_allow_html=True)

    with sc2:
        st.markdown("<div class='panel-card'>", unsafe_allow_html=True)
        list_heading = "Registered Users List" if is_english else "नोंदणीकृत वापरकर्त्यांची यादी"
        st.markdown(f"<h4 style='color:#00f2fe; margin-top:0;'>{list_heading}</h4>", unsafe_allow_html=True)

        try:
            with sqlite3.connect("ledger.db") as conn:
                users_df = pd.read_sql_query("SELECT username, role, phone FROM users", conn)

            if not users_df.empty:
                if is_english:
                    disp_df = users_df.rename(columns={"username": "Username", "role": "Role", "phone": "Phone Number"})
                else:
                    disp_df = users_df.rename(columns={"username": "वापरकर्ता नाव", "role": "भूमिका", "phone": "मोबाईल नंबर"})
                st.dataframe(disp_df, use_container_width=True)
            else:
                st.info("No registered users found." if is_english else "कोणतेही वापरकर्ते नोंदणीकृत नाहीत.")

            del_lbl = "Enter username to delete" if is_english else "डिलिट करण्यासाठी वापरकर्ता नाव टाईप करा"
            del_uname = st.text_input(del_lbl, key="staff_del_uname")

            del_btn_lbl = "Delete User" if is_english else "वापरकर्ता डिलीट करा"
            if st.button(del_btn_lbl, key="btn_del_staff_user"):
                target_user = del_uname.strip().lower()
                if target_user in ["admin", "sanket"]:
                    master_err = "Master Admin account cannot be deleted!" if is_english else "मुख्य मास्टर ॲडमिन खाते डिलीट करता येणार नाही!"
                    st.error(master_err)
                elif not del_uname.strip():
                    empty_err = "Please enter a valid username to delete." if is_english else "कृपया डिलीट करण्यासाठी योग्य वापरकर्ता नाव टाका."
                    st.warning(empty_err)
                else:
                    try:
                        with sqlite3.connect("ledger.db") as conn:
                            conn.execute("BEGIN TRANSACTION;")
                            cursor = conn.cursor()
                            cursor.execute("DELETE FROM users WHERE username = ?", (del_uname.strip(),))
                            conn.commit()
                        log_activity(st.session_state.get('current_username', 'admin'), f"Deleted User {del_uname.strip()}")
                        succ_del = f"User '{del_uname.strip()}' successfully deleted!" if is_english else f"वापरकर्ता '{del_uname.strip()}' यशस्वीरित्या डिलीट झाला!"
                        st.success(succ_del)
                        time.sleep(0.5)
                        st.rerun()
                    except Exception as ex:
                        st.error(f"Error: {ex}")
        except Exception as e:
            st.error(f"Error loading users: {e}")
        st.markdown("</div>", unsafe_allow_html=True)

# FEATURE 7: LEDGER DATABASE ---
elif selected_page == "Ledger Database":
    render_page_header("Ledger Database & Export", "Enterprise Storage, Advanced Filters, Clean Layout & Report Downloads", "📊")

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
    c1, c2, c3, c4 = st.columns([1, 1, 1, 1.2])
    with c1:
        st.markdown(f"<div class='panel-card' style='margin-bottom:15px; border-left:4px solid #00ff87;'><div style='font-size:11px; color:#94a3b8; font-weight:700;'>✅ CASH RECOVERED</div><div style='font-size: 18px; font-weight:800; color:#00ff87; margin-top:4px;'>₹{total_collected:,.2f}</div></div>", unsafe_allow_html=True)
    with c2:
        st.markdown(f"<div class='panel-card' style='margin-bottom:15px; border-left:4px solid #f59e0b;'><div style='font-size:11px; color:#94a3b8; font-weight:700;'>⏳ PENDING UDHAR</div><div style='font-size: 18px; font-weight:800; color:#f59e0b; margin-top:4px;'>₹{total_unpaid:,.2f}</div></div>", unsafe_allow_html=True)
    with c3:
        st.markdown(f"<div class='panel-card' style='margin-bottom:15px; border-left:4px solid #ef4444;'><div style='font-size:11px; color:#94a3b8; font-weight:700;'>🚨 OVERDUE (AT RISK)</div><div style='font-size: 18px; font-weight:800; color:#ef4444; margin-top:4px;'>₹{total_overdue:,.2f}</div></div>", unsafe_allow_html=True)
    with c4:
        db_is_en = st.session_state.get("ui_language", "en") == "en"
        daily_digest_msg = generate_daily_whatsapp_digest(is_english=db_is_en)
        daily_wa_url = f"https://wa.me/?text={urllib.parse.quote(daily_digest_msg)}"
        st.markdown(f"""
        <div class='panel-card' style='margin-bottom:15px; border-left:4px solid #25d366;'>
            <div style='font-size:11px; color:#94a3b8; font-weight:700;'>🌙 DAILY BUSINESS DIGEST</div>
            <a href='{daily_wa_url}' target='_blank' style='text-decoration:none;'>
                <button style='width:100%; height:32px; border-radius:6px; background:#25d366; color:#000; font-weight:700; border:none; cursor:pointer; font-size:11px; display:flex; align-items:center; justify-content:center; gap:4px; margin-top:5px;'>
                    💬 व्हॉट्सॲपवर पाठवा
                </button>
            </a>
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
                if st.button("➕", help="नवीन रो जोडा (Add New Row)"):
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
                if st.button(f"🗑️ निवडलेले records डिलीट करा ({len(selected_ids)})", type="primary"):
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
            st.markdown("#### 📥 अहवाल आणि डाऊनलोड (Reports & Export)")
            st.markdown("<div style='font-size:12px; color:#94a3b8; margin-bottom:10px;'>तारीख आणि दुकान निवडून अहवाल डाऊनलोड करा:</div>", unsafe_allow_html=True)
            
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
            if not csv_df.empty and 'grand_total' in csv_df.columns:
                csv_df['Taxable Value (₹)'] = csv_df['grand_total'].apply(lambda x: round(float(x or 0) / 1.05, 2))
                csv_df['CGST 2.5% (₹)'] = csv_df['grand_total'].apply(lambda x: round((float(x or 0) - round(float(x or 0) / 1.05, 2)) / 2.0, 2))
                csv_df['SGST 2.5% (₹)'] = csv_df.apply(lambda r: round(float(r['grand_total'] or 0) - r['Taxable Value (₹)'] - r['CGST 2.5% (₹)'], 2), axis=1)
                
            csv_data = csv_df.to_csv(index=False).encode('utf-8-sig')
            st.download_button("📊 Export Clean CSV (सह GST & Items)", data=csv_data, file_name=f"ledger_{dl_selected_shop}.csv", mime="text/csv", use_container_width=True)
            st.download_button(f"📄 Export {report_lang} Report (.html)", data=generate_pdf_report(report_df, dl_selected_shop, report_lang), file_name=f"report_{dl_selected_shop}_{report_lang}.html", mime="text/html", use_container_width=True)
            
            # Database Backup & Restore Card
            st.markdown("<hr style='margin:12px 0;'>", unsafe_allow_html=True)
            st.markdown("##### 💾 डेटाबेस बॅकअप आणि रिस्टोअर (Backup & Restore)")
            
            db_bytes = b""
            if os.path.exists("ledger.db"):
                try:
                    with open("ledger.db", "rb") as f_db:
                        db_bytes = f_db.read()
                except Exception as e:
                    ai_logger.error(f"Failed to read ledger.db: {e}")
            
            st.download_button(
                "📥 संपूर्ण डेटाबेस बॅकअप (.db डाउनलोड)",
                data=db_bytes,
                file_name=f"VernaLedger_Backup_{date.today().strftime('%Y-%m-%d')}.db",
                mime="application/x-sqlite3",
                use_container_width=True,
                key="btn_download_db_backup"
            )
            
            with st.expander("📤 डेटाबेस रिस्टोअर करा (Restore DB Backup)", expanded=False):
                uploaded_db = st.file_uploader("बॅकअप फाईल निवडा (.db)", type=["db", "sqlite", "sqlite3"], key="uploader_restore_db")
                if uploaded_db is not None:
                    if st.button("⚠️ रिस्टोअरची पुष्टी करा (Confirm Restore)", type="primary", use_container_width=True):
                        try:
                            with open("ledger.db", "wb") as f_restore:
                                f_restore.write(uploaded_db.getbuffer())
                            st.toast("✅ डेटाबेस यशस्वीरित्या रिस्टोअर झाला!", icon="💾")
                            st.success("डेटाबेस यशस्वीरित्या रिस्टोअर झाला! ॲप रिफ्रेश होत आहे...")
                            time.sleep(1)
                            st.rerun()
                        except Exception as re_err:
                            st.error(f"रिस्टोअर त्रुटी: {re_err}")
            
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
    .stApp {
        font-family: 'Plus Jakarta Sans', 'Mukta', 'Hind', 'Baloo 2', sans-serif;
    }
    h1, h2, h3, h4, h5, h6, p, li, label, .stMarkdown {
        font-family: 'Plus Jakarta Sans', 'Mukta', 'Hind', 'Baloo 2', sans-serif;
    }
    /* Protect all Streamlit default icons and SVG from font overrides */
    svg, svg * {
        font-family: inherit; 
    }
    .material-symbols-rounded, .material-symbols-outlined, .material-icons, [class*="icon"] {
        font-family: 'Material Symbols Rounded', 'Material Symbols Outlined', 'Material Icons' !important;
    }
    /* --- END SAFE FONT --- */
    
    [data-testid="stMainBlockContainer"] {
    box-sizing: border-box !important;
    width: 100% !important;
    max-width: 100% !important;
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
    font-size: clamp(2.5rem, 6vw, 4rem);
    font-weight: 900;
    letter-spacing: -0.02em;
    line-height: 1.2;
    text-align: center;
    background: linear-gradient(135deg, #00f2fe 0%, #4facfe 50%, #f093fb 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    text-shadow: 0px 4px 30px rgba(0, 242, 254, 0.3);
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
    overflow-wrap: break-word;
    word-break: keep-all;
    hyphens: none;
}
.st-key-rag_chat_history {
    box-sizing: border-box;
    display: flex;
    width: 100% !important;
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
    overflow-wrap: break-word;
    word-break: keep-all;
    hyphens: none;
}
[data-testid="stCustomComponentV1"] {
    position: fixed !important;
    left: 50% !important;
    bottom: max(1.1rem, env(safe-area-inset-bottom)) !important;
    transform: translateX(-50%) !important;
    width: calc(100vw - 3rem) !important;
    max-width: 100% !important;
    margin: 0 !important;
    padding: 0 !important;
    z-index: 20 !important;
}
body:has(section[data-testid="stSidebar"][aria-expanded="true"]) [data-testid="stCustomComponentV1"] {
    left: calc(50% + 9.375rem) !important;
    width: calc(100vw - 18.75rem - 3rem) !important;
}
main.block-container {
    padding-bottom: 9rem !important;
}
@media (max-width: 900px) and (min-width: 641px) {
    body:has(section[data-testid="stSidebar"][aria-expanded="true"]) [data-testid="stCustomComponentV1"] {
        left: calc(50% + 9rem) !important;
        width: calc(100vw - 18rem - 3rem) !important;
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

    render_page_header("Verna AI Chatbot", "Your Smart Ledger & Business Assistant", "✨")
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
    <p style="color:#00f2fe; font-size:16px; font-weight:600; margin:0;">Hello! Ask me anything about your shop ledger, stock, or expenses.</p>
  </div>
</section>
""", unsafe_allow_html=True)

        for idx, chat in enumerate(st.session_state["chat_history"]):
            message_role = "user" if chat["role"] == "user" else "assistant"
            with st.chat_message(message_role, avatar='\U0001f916' if message_role == 'assistant' else '\U0001f464'):
                _streamlit_ui.markdown(chat["text"])
                if enable_voice_output and chat.get("audio_file") and os.path.exists(chat["audio_file"]):
                    do_play = False
                    if idx == len(st.session_state["chat_history"]) - 1:
                        do_play = st.session_state.pop("play_latest_audio", False)
                    st.audio(chat["audio_file"], autoplay=do_play)

    chat_input_event = CHAT_INPUT_COMPONENT(
        key="verna_chat_input_component",
        default=None,
        language=st.session_state.get("ui_language", "en"),
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
        st.session_state["play_latest_audio"] = True
        st.rerun()
