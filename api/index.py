"""
VernaLedger.AI: Merchant Pro v7.5 - Production Serverless API (Vercel Ready)
FastAPI Backend providing Multimodal Gemini Flash OCR, Vernacular Voice Billing,
SQLite ACID Ledger, Customer Khata, Business Operations, and Neural RAG Chatbot.
"""

import os
import io
import re
import json
import time
import base64
import sqlite3
import hashlib
import asyncio
import logging
from datetime import date, datetime
from typing import Optional, List, Dict, Any

from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from PIL import Image

try:
    import google.generativeai as genai
except ImportError:
    genai = None

try:
    import edge_tts
except ImportError:
    edge_tts = None

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("vernaledger.api")

app = FastAPI(
    title="VernaLedger.AI Serverless API",
    description="Next-Gen Vernacular Financial & POS Suite API",
    version="7.5"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------------------------------------------------------
# DATABASE MANAGEMENT (SERVERLESS COMPATIBLE)
# -----------------------------------------------------------------------------
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOCAL_DB = os.path.join(ROOT_DIR, "ledger.db")

# In Vercel serverless environment, the filesystem is read-only except /tmp
if os.environ.get("VERCEL"):
    DB_PATH = "/tmp/ledger.db"
    if not os.path.exists(DB_PATH) and os.path.exists(LOCAL_DB):
        try:
            import shutil
            shutil.copy2(LOCAL_DB, DB_PATH)
            logger.info("Successfully seeded /tmp/ledger.db from project template.")
        except Exception as e:
            logger.error(f"Error copying ledger.db to /tmp: {e}")
else:
    DB_PATH = LOCAL_DB

def get_db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    try:
        conn.execute("PRAGMA journal_mode = WAL;")
        conn.execute("PRAGMA synchronous = NORMAL;")
    except Exception:
        pass
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY,
        password_hash TEXT,
        role TEXT DEFAULT 'Admin',
        phone TEXT
    );
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS receipts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        vendor_name TEXT,
        date TEXT,
        category TEXT,
        grand_total REAL,
        raw_json TEXT
    );
    """)
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
    );
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS shop_inventory (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        item_name TEXT,
        stock_qty REAL,
        unit TEXT DEFAULT 'pcs',
        alert_limit REAL DEFAULT 5.0,
        barcode TEXT,
        selling_price REAL DEFAULT 0.0
    );
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS business_expenses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        expense_title TEXT,
        amount REAL,
        category TEXT,
        date TEXT,
        notes TEXT
    );
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS audit_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        action TEXT,
        timestamp TEXT
    );
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS shop_settings (
        key TEXT PRIMARY KEY,
        value TEXT
    );
    """)
    
    # Seed default Admin account if empty
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        admin_pass_hash = hash_password_secure("admin123")
        cursor.execute("INSERT OR IGNORE INTO users VALUES ('admin', ?, 'Admin', '9999999999')", (admin_pass_hash,))
        cursor.execute("INSERT OR IGNORE INTO users VALUES ('sanket', ?, 'Admin', '9999999999')", (admin_pass_hash,))
    
    # Seed sample inventory if empty
    cursor.execute("SELECT COUNT(*) FROM shop_inventory")
    if cursor.fetchone()[0] == 0:
        sample_inv = [
            ("साखर (Sugar M-30)", 45.0, "kg", 10.0, 44.0),
            ("शेंगदाणा तेल (Groundnut Oil)", 12.0, "ltr", 5.0, 165.0),
            ("गहू (Wheat Lokwan)", 80.0, "kg", 15.0, 38.0),
            ("चहा पावडर (Society Tea)", 25.0, "pkt", 5.0, 120.0),
            ("तूर डाळ (Toor Dal Premium)", 30.0, "kg", 8.0, 155.0),
            ("तांदूळ (Kolam Rice)", 50.0, "kg", 10.0, 62.0),
            ("सूर्यफूल तेल (Sunflower Oil)", 4.0, "ltr", 5.0, 140.0), # Alert low stock
            ("साबण (Bathing Soap 4-pack)", 3.0, "pkt", 5.0, 95.0)     # Alert low stock
        ]
        cursor.executemany("INSERT INTO shop_inventory (item_name, stock_qty, unit, alert_limit, selling_price) VALUES (?, ?, ?, ?, ?)", sample_inv)

    # Seed sample customer khata if empty
    cursor.execute("SELECT COUNT(*) FROM customer_khata")
    if cursor.fetchone()[0] == 0:
        sample_khata = [
            ("सागर पाटील (Sagar Patil)", "9876543210", 850.0, "Credit Given", "2026-10-18", "2026-10-25", "किराणा उधारी सामान"),
            ("सागर पाटील (Sagar Patil)", "9876543210", 300.0, "Payment Received", "2026-10-19", "", "Google Pay द्वारे जमा"),
            ("रमेश पवार (Ramesh Pawar)", "9822001122", 1200.0, "Credit Given", "2026-10-15", "2026-10-22", "महिना किराणा उधारी")
        ]
        cursor.executemany("INSERT INTO customer_khata (customer_name, phone, amount, transaction_type, date, due_date, notes) VALUES (?, ?, ?, ?, ?, ?, ?)", sample_khata)

    # Seed sample receipt if empty
    cursor.execute("SELECT COUNT(*) FROM receipts")
    if cursor.fetchone()[0] == 0:
        rec_data = {
            "vendor_name": "महादेव किराणा स्टोअर",
            "date": "2026-10-20",
            "category": "General",
            "items": [
                {"item_name": "साखर", "quantity": "2 kg", "rate": 44.0, "total_price": 88.0},
                {"item_name": "शेंगदाणा तेल", "quantity": "1 ltr", "rate": 165.0, "total_price": 165.0}
            ],
            "grand_total": 253.0
        }
        cursor.execute(
            "INSERT INTO receipts (vendor_name, date, category, grand_total, raw_json) VALUES (?, ?, ?, ?, ?)",
            (rec_data["vendor_name"], rec_data["date"], rec_data["category"], rec_data["grand_total"], json.dumps(rec_data, ensure_ascii=False))
        )
    
    conn.commit()
    conn.close()

def hash_password_secure(password: str) -> str:
    return hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), b'salt_verna_bcrypt_layer', 100000).hex()

def log_activity(username: str, action: str):
    try:
        conn = get_db()
        conn.execute("INSERT INTO audit_logs (username, action, timestamp) VALUES (?, ?, ?)",
                     (username, action, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit()
        conn.close()
    except Exception as e:
        logger.error(f"Audit log error: {e}")

# Initialize on startup
init_db()

def get_api_key() -> str:
    key = os.getenv("GEMINI_API_KEY", "").strip()
    if key:
        return key
    secrets_path = os.path.join(ROOT_DIR, ".streamlit", "secrets.toml")
    try:
        if os.path.exists(secrets_path):
            import tomllib
            with open(secrets_path, "rb") as secrets_file:
                secrets = tomllib.load(secrets_file)
            key = str(secrets.get("GEMINI_API_KEY", "")).strip()
            if key and not key.startswith("PASTE_YOUR_"):
                return key
    except (OSError, ValueError) as exc:
        logger.warning("Could not read local API configuration: %s", exc)
    return ""

# -----------------------------------------------------------------------------
# PYDANTIC DATA MODELS
# -----------------------------------------------------------------------------
class LoginRequest(BaseModel):
    username: str
    password: str

class VoiceBillRequest(BaseModel):
    transcript: str
    username: Optional[str] = "admin"

class TTSRequest(BaseModel):
    text: str
    voice: Optional[str] = "mr-IN-AarohiNeural"

class KhataEntryRequest(BaseModel):
    customer_name: str
    phone: str
    amount: float
    transaction_type: str  # 'Credit Given' or 'Payment Received'
    due_date: Optional[str] = ""
    notes: Optional[str] = ""
    username: Optional[str] = "admin"

class InventoryItemRequest(BaseModel):
    item_name: str
    stock_qty: float
    unit: Optional[str] = "pcs"
    alert_limit: Optional[float] = 5.0
    selling_price: Optional[float] = 0.0

class ExpenseRequest(BaseModel):
    expense_title: str
    amount: float
    category: str
    notes: Optional[str] = ""

class RAGChatRequest(BaseModel):
    message: str
    chat_history: Optional[List[Dict[str, Any]]] = []
    lang: Optional[str] = "mr"
    voice_output: Optional[bool] = False
    username: Optional[str] = "admin"

class NewUserRequest(BaseModel):
    username: str
    password: str
    role: str = "Staff"
    phone: str = ""

# -----------------------------------------------------------------------------
# AUTH & USER ENDPOINTS
# -----------------------------------------------------------------------------
@app.post("/api/login")
def login(req: LoginRequest):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT password_hash, role, phone FROM users WHERE username = ?", (req.username.strip(),))
    user = cursor.fetchone()
    conn.close()

    if not user:
        raise HTTPException(status_code=401, detail="Invalid username or password")

    hashed_input = hash_password_secure(req.password)
    valid = (user["password_hash"] == hashed_input)
    
    # Backward compatibility for default demo passwords
    if not valid and req.username.strip().lower() in ["admin", "sanket"]:
        if req.password in ["admin123", "verna123", "pass123"]:
            valid = True
            # Update hash to new input
            try:
                c2 = get_db()
                c2.execute("UPDATE users SET password_hash = ? WHERE username = ?", (hashed_input, req.username.strip()))
                c2.commit()
                c2.close()
            except Exception:
                pass

    if not valid:
        raise HTTPException(status_code=401, detail="Invalid username or password")

    log_activity(req.username.strip(), "User Logged In")
    return {
        "success": True,
        "username": req.username.strip(),
        "role": user["role"],
        "phone": user["phone"]
    }

# Staff & Audit Logs removed per clean merchant architecture

# -----------------------------------------------------------------------------
# DASHBOARD METRICS ENDPOINT
# -----------------------------------------------------------------------------
@app.get("/api/dashboard")
def get_dashboard_metrics():
    conn = get_db()
    
    # Receipts stats
    total_sales = conn.execute("SELECT SUM(grand_total) FROM receipts").fetchone()[0] or 0.0
    total_bills = conn.execute("SELECT COUNT(*) FROM receipts").fetchone()[0] or 0
    avg_ticket = (total_sales / total_bills) if total_bills > 0 else 0.0

    # Khata stats
    credit_given = conn.execute("SELECT SUM(amount) FROM customer_khata WHERE transaction_type = 'Credit Given'").fetchone()[0] or 0.0
    payment_received = conn.execute("SELECT SUM(amount) FROM customer_khata WHERE transaction_type = 'Payment Received'").fetchone()[0] or 0.0
    pending_udhar = max(0.0, credit_given - payment_received)

    # Expenses
    total_expenses = conn.execute("SELECT SUM(amount) FROM business_expenses").fetchone()[0] or 0.0

    # Low stock items
    low_stock_count = conn.execute("SELECT COUNT(*) FROM shop_inventory WHERE stock_qty <= alert_limit").fetchone()[0] or 0

    # Recent 5 receipts
    recent_receipts = [dict(r) for r in conn.execute("SELECT id, vendor_name, date, category, grand_total FROM receipts ORDER BY id DESC LIMIT 5").fetchall()]

    conn.close()

    net_margin = total_sales - total_expenses
    today_disp = date.today().strftime("%d-%m-%Y")

    daily_digest_mr = (
        f"📊 *वर्ना लेजर AI - दैनिक बिझनेस रिपोर्ट*\n"
        f"📅 *तारीख:* {today_disp}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"💰 *आजची एकूण विक्री:* ₹{total_sales:,.2f} ({total_bills} पावत्या)\n"
        f"📉 *एकूण दैनंदिन खर्च:* ₹{total_expenses:,.2f}\n"
        f"💵 *अंदाजे निव्वळ नफा:* ₹{net_margin:,.2f}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"✅ *उधारीतून जमा रोख:* ₹{payment_received:,.2f}\n"
        f"⏳ *बाकी एकूण उधारी:* ₹{pending_udhar:,.2f}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🤖 _VernaLedger-AI स्वयंचलित अहवाल_"
    )

    return {
        "total_sales": total_sales,
        "total_bills": total_bills,
        "avg_ticket": avg_ticket,
        "cash_recovered": payment_received,
        "pending_udhar": pending_udhar,
        "total_expenses": total_expenses,
        "net_profit": net_margin,
        "low_stock_count": low_stock_count,
        "recent_receipts": recent_receipts,
        "daily_digest_mr": daily_digest_mr
    }

# -----------------------------------------------------------------------------
# MULTIMODAL OCR BILLING (GEMINI FLASH)
# -----------------------------------------------------------------------------
def clean_json_str(text: str) -> dict:
    text = re.sub(r'```json\s*', '', text)
    text = re.sub(r'```\s*$', '', text).strip()
    start_idx = text.find('{')
    end_idx = text.rfind('}')
    if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
        return json.loads(text[start_idx:end_idx + 1])
    return json.loads(text)

@app.post("/api/ocr")
async def process_ocr(file: UploadFile = File(...)):
    api_key = get_api_key()
    if not api_key:
        raise HTTPException(status_code=500, detail="GEMINI_API_KEY is not configured in Vercel environment variables.")
    
    if not genai:
        raise HTTPException(status_code=500, detail="Google Generative AI package is not installed.")

    contents = await file.read()
    try:
        img = Image.open(io.BytesIO(contents)).convert('RGB')
        img.thumbnail((1280, 1280), Image.Resampling.LANCZOS)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid image format: {e}")

    genai.configure(api_key=api_key)
    prompt = """
    You are an expert document OCR scanner specialized in Marathi, Devanagari handwritten and printed ledgers, invoices, and retail receipts.
    CRITICAL OCR INSTRUCTIONS:
    1. Extract Vendor/Shop Name at the top in complete Marathi or English script.
    2. Extract EVERY line item row accurately:
       - item_name: Full item name (e.g. 'साखर', 'शेंगदाणा तेल', 'गहू', 'चहा पावडर').
       - quantity: Numeric count with unit (e.g. '1 kg', '2 pcs', '500 gm').
       - rate: Numeric price per unit in rupees (e.g. 45.0).
       - total_price: Line item total in rupees (quantity * rate).
    3. Calculate grand_total = SUM of all item totals.
    
    Output strictly in this JSON format:
    {
      "vendor_name": "string",
      "date": "string",
      "category": "General",
      "items": [
        {"item_name": "string", "quantity": "string", "rate": 0.0, "total_price": 0.0}
      ],
      "grand_total": 0.0
    }
    Return ONLY valid JSON.
    """

    models_to_try = ['gemini-2.5-flash-lite', 'gemini-2.5-flash', 'gemini-1.5-flash']
    response = None
    last_err = None

    for m in models_to_try:
        try:
            model = genai.GenerativeModel(m)
            res = model.generate_content([prompt, img])
            if res and res.text:
                response = res.text
                break
        except Exception as exc:
            last_err = exc
            continue

    if not response:
        raise HTTPException(status_code=500, detail=f"AI Vision Scan failed: {last_err}")

    data = clean_json_str(response)
    if data.get('items') and data.get('grand_total', 0) == 0:
        data['grand_total'] = sum(i.get('total_price', 0) for i in data['items'])

    # Save to SQLite
    today_str = date.today().strftime("%Y-%m-%d")
    rec_date = data.get("date") or today_str
    raw_json_str = json.dumps(data, ensure_ascii=False)

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO receipts (vendor_name, date, category, grand_total, raw_json) VALUES (?, ?, ?, ?, ?)",
        (data.get("vendor_name", "Kirana Store"), rec_date, data.get("category", "General"), data.get("grand_total", 0.0), raw_json_str)
    )
    data["id"] = cursor.lastrowid
    # Auto-sync to Customer Khata if spoken text mentions credit/udhar
    if any(k in req.transcript for k in ["उधारी", "खाते", "खात्यावर", "credit", "उधार"]) and data.get("grand_total", 0) > 0:
        cust = data.get("vendor_name", "").replace("अनामित (Local Kirana)", "").strip() or "ग्राहक"
        cursor.execute(
            "INSERT INTO customer_khata (customer_name, phone, amount, transaction_type, date, due_date, notes) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (cust, "", data["grand_total"], "Credit Given", date.today().strftime("%Y-%m-%d"), "", f"व्हॉइस बिल #{data['id']}")
        )
        data["auto_khata_added"] = True
    conn.commit()
    conn.close()

    return {"success": True, "data": data}

# -----------------------------------------------------------------------------
# VERNACULAR VOICE BILLING
# -----------------------------------------------------------------------------
@app.post("/api/voice-billing")
def process_voice_billing(req: VoiceBillRequest):
    api_key = get_api_key()
    if not api_key:
        raise HTTPException(status_code=500, detail="GEMINI_API_KEY is not configured in Vercel environment.")

    genai.configure(api_key=api_key)
    prompt = f"""
    Convert the following spoken Marathi/English store billing transaction into structured receipt JSON:
    Spoken Text: "{req.transcript}"
    
    1. Extract vendor name if spoken, otherwise "अनामित (Local Kirana)".
    2. Extract all items, quantities, rates per unit, and calculate total_price = quantity * rate.
    3. Calculate grand_total = sum of all items total_price.
    
    Output strictly in this JSON format:
    {{
      "vendor_name": "string",
      "date": "Voice Bill",
      "category": "General",
      "items": [
        {{"item_name": "string", "quantity": "string", "rate": 0.0, "total_price": 0.0}}
      ],
      "grand_total": 0.0
    }}
    Return ONLY valid JSON.
    """

    models_to_try = ['gemini-2.5-flash-lite', 'gemini-2.5-flash', 'gemini-1.5-flash']
    res_text = None
    for m in models_to_try:
        try:
            model = genai.GenerativeModel(m)
            res = model.generate_content(prompt)
            if res and res.text:
                res_text = res.text
                break
        except Exception:
            continue

    if not res_text:
        raise HTTPException(status_code=500, detail="Could not parse voice billing input")

    data = clean_json_str(res_text)
    raw_json_str = json.dumps(data, ensure_ascii=False)

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO receipts (vendor_name, date, category, grand_total, raw_json) VALUES (?, ?, ?, ?, ?)",
        (data.get("vendor_name", "Voice Bill"), date.today().strftime("%Y-%m-%d"), data.get("category", "General"), data.get("grand_total", 0.0), raw_json_str)
    )
    data["id"] = cursor.lastrowid
    # Auto-sync to Customer Khata if spoken text mentions credit/udhar
    if any(k in req.transcript for k in ["उधारी", "खाते", "खात्यावर", "credit", "उधार"]) and data.get("grand_total", 0) > 0:
        cust = data.get("vendor_name", "").replace("अनामित (Local Kirana)", "").strip() or "ग्राहक"
        cursor.execute(
            "INSERT INTO customer_khata (customer_name, phone, amount, transaction_type, date, due_date, notes) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (cust, "", data["grand_total"], "Credit Given", date.today().strftime("%Y-%m-%d"), "", f"व्हॉइस बिल #{data['id']}")
        )
        data["auto_khata_added"] = True
    conn.commit()
    conn.close()

    log_activity(req.username or "admin", f"Created Voice Bill #{data['id']} (₹{data.get('grand_total', 0)})")
    return {"success": True, "data": data}

SUPPORTED_LANGUAGES = {
    "mr": ("Marathi", "mr-IN"), "en": ("English", "en-IN"),
    "hi": ("Hindi", "hi-IN"), "gu": ("Gujarati", "gu-IN"),
    "ta": ("Tamil", "ta-IN"), "te": ("Telugu", "te-IN"),
    "kn": ("Kannada", "kn-IN"), "bn": ("Bengali", "bn-IN"),
    "es": ("Spanish", "es-ES"), "fr": ("French", "fr-FR"),
}

def detect_msg_language(text: str, requested: str = "mr") -> str:
    """Detect whether user query is in Marathi or English based on actual text first, fallback to requested."""
    clean = (text or "").strip()
    if not clean:
        return requested if requested in ["mr", "en"] else "mr"

    devanagari_count = len(re.findall(r"[\u0900-\u097f]", clean))
    latin_count = len(re.findall(r"[A-Za-z]", clean))

    # 1. If message has Devanagari characters, it is 100% Marathi
    if devanagari_count >= 2:
        return "mr"

    # 2. Check for common Marathi / Marathi-English phonetics (Hinglish/Maringlish)
    marathi_markers = [
        "ahe", "aahe", "nahi", "nahiy", "sanga", "kiti", "kay", "udhari", "kharch",
        "vikri", "satha", "pavti", "hishob", "konakade", "koni", "namaskar",
        "dili", "dile", "ghetle", "zale", "jhale", "kar", "kara", "lihi", "dya",
        "साखर", "तेल", "गहू", "तांदूळ", "चहा", "साबण", "दुकान", "बाकी"
    ]
    lower_clean = clean.lower()
    if any(m in lower_clean for m in marathi_markers):
        return "mr"

    # 3. If predominantly Latin letters without Marathi markers, it's English
    if latin_count > devanagari_count and latin_count >= 3:
        return "en"

    # 4. Fallback to requested language
    return requested if requested in ["mr", "en"] else "mr"

TTS_VOICES = {
    "mr": "mr-IN-AarohiNeural", "en": "en-IN-NeerjaNeural",
    "hi": "hi-IN-SwaraNeural", "gu": "gu-IN-DhwaniNeural",
    "ta": "ta-IN-PallaviNeural", "te": "te-IN-ShrutiNeural",
    "kn": "kn-IN-SapnaNeural", "bn": "bn-IN-TanishaaNeural",
    "es": "es-ES-ElviraNeural", "fr": "fr-FR-DeniseNeural",
}

def prepare_speech_phonetics(audio_text: str, tts_voice: str = "mr-IN-AarohiNeural") -> str:
    """Accurate Marathi and English phonetic pronunciation engine directly from Streamlit."""
    if not audio_text:
        return ""
    audio_text = re.sub(r"[*#_`]", "", audio_text)
    devanagari_count = len(re.findall(r"[\u0900-\u097f]", audio_text))
    if devanagari_count:
        audio_text = re.sub(r"\s*[\(\[][A-Za-z][^\)\]]*[\)\]]", "", audio_text)

    if tts_voice.startswith("mr-") or devanagari_count >= 2:
        audio_text = re.sub(r"\bVernaLedger\s*AI\b", "व्हर्ना लेजर ए आय", audio_text, flags=re.IGNORECASE)
        audio_text = re.sub(r"\bVernaLedger\b", "व्हर्ना लेजर", audio_text, flags=re.IGNORECASE)
        audio_text = re.sub(r"\bAI\b", "ए आय", audio_text, flags=re.IGNORECASE)
        audio_text = re.sub(r"\bGST\b", "जी एस टी", audio_text, flags=re.IGNORECASE)
        audio_text = re.sub(r"\bUPI\b", "यु पी आय", audio_text, flags=re.IGNORECASE)
        audio_text = re.sub(r"\bSMS\b", "एस एम एस", audio_text, flags=re.IGNORECASE)
        audio_text = re.sub(r"\bAGCE\b", "ए जी सी ई", audio_text, flags=re.IGNORECASE)
        audio_text = re.sub(r"\bAGCOE\b", "ए जी सी ओ ई", audio_text, flags=re.IGNORECASE)
        audio_text = re.sub(r"\bDBATU\b", "डी बाटू", audio_text, flags=re.IGNORECASE)
        audio_text = re.sub(r"[₹]|(?:\b(?:Rs|रु)\.?\s*)", "रुपये ", audio_text, flags=re.IGNORECASE)

        # Convert English name occurrences to Marathi so Aarohi won't stumble on English
        audio_text = re.sub(r"\bSanket\s+Kirdat\b", "संकेत किर-दत", audio_text, flags=re.IGNORECASE)
        audio_text = re.sub(r"\bSanket\b", "संकेत", audio_text, flags=re.IGNORECASE)
        audio_text = re.sub(r"\bSakshi\s+Bhagat\b", "साक्षी भगत", audio_text, flags=re.IGNORECASE)
        audio_text = re.sub(r"\bVaishnavi\s+(?:Dhavale|Dhawale)\b", "वैष्णवी ढव्-ळे", audio_text, flags=re.IGNORECASE)
        audio_text = re.sub(r"\bRushikesh\s+Mulik\b", "ऋषिकेश मुळीक", audio_text, flags=re.IGNORECASE)
        audio_text = re.sub(r"\b(?:Prof\.?\s*)?Kaisar\s+(?:Atar|Attar)(?:\s+Sir)?\b", "प्राध्यापक कै-सर अतार सर", audio_text, flags=re.IGNORECASE)
        audio_text = re.sub(r"\bArvind\s+Gavali(?:\s+College(?:\s+of\s+Engineering)?)?\b", "अरविंद गव्-ळी कॉलेज", audio_text, flags=re.IGNORECASE)
        audio_text = re.sub(r"\bLead\s+Developer\b", "प्रमुख विकासक", audio_text, flags=re.IGNORECASE)
        audio_text = re.sub(r"\bProject\s+Guide\b", "प्रकल्प मार्गदर्शक", audio_text, flags=re.IGNORECASE)
        audio_text = re.sub(r"\bDevelopers\b", "इतर विकासक", audio_text, flags=re.IGNORECASE)
        audio_text = re.sub(r"\bCollege\b", "महाविद्यालय", audio_text, flags=re.IGNORECASE)

        pronunciation_hints = {
            "वैष्णवी ढवळे": "वैष्णवी ढव्-ळे",
            "ढवाळे": "ढव्-ळे",
            "ढवळे": "ढव्-ळे",
            "अरविंद गवळी": "अरविंद गव्-ळी",
            "गवाली": "गव्-ळी",
            "गवळी": "गव्-ळी",
            "कैसर अतार": "कै-सर अतार",
            "कॅसर अतार": "कै-सर अतार",
            "कैसर अत्तार": "कै-सर अतार",
            "कॅसर अत्तार": "कै-सर अतार",
            "कैसर": "कै-सर",
            "कॅसर": "कै-सर",
            "कौसर": "कै-सर",
            "अतार सर": "अतार सर",
            "किर्दत": "किर-दत",
            "किरदत": "किर-दत",
            "साक्षी भगत": "साक्षी भगत",
            "ऋषिकेश मुळीक": "ऋषिकेश मुळीक",
            "मुळीक": "मुळीक",
            "मुलिक": "मुळीक",
        }
        for name, pronunciation in pronunciation_hints.items():
            audio_text = audio_text.replace(name, pronunciation)
        audio_text = re.sub(r"\bGavali\b", "गव्-ळी", audio_text, flags=re.IGNORECASE)

    elif tts_voice.startswith("en-"):
        audio_text = re.sub(r"\bVernaLedger\b", "Verna Ledger", audio_text, flags=re.IGNORECASE)
        audio_text = re.sub(r"[₹]|(?:\b(?:Rs|रु)\.?\s*)", "Rupees ", audio_text, flags=re.IGNORECASE)
        audio_text = re.sub(r"\bAGCE\b", "A G C E", audio_text, flags=re.IGNORECASE)
        audio_text = re.sub(r"\bAGCOE\b", "A G C O E", audio_text, flags=re.IGNORECASE)
        en_pronunciations = {
            "Kirdat": "Keer-dat",
            "Atar": "Ah-tar",
            "Attar": "Ah-tar",
            "Dhavale": "Dhaw-ley",
            "Dhawale": "Dhaw-ley",
            "Mulik": "Moo-lik",
            "Gavali": "Gawali",
        }
        for name, pronunciation in en_pronunciations.items():
            audio_text = audio_text.replace(name, pronunciation)

    audio_text = re.sub(r"[ \t]+", " ", audio_text)
    audio_text = re.sub(r" *([,;:]) *", r"\1 ", audio_text)
    audio_text = re.sub(r" *([.!?।]) *", r"\1 ", audio_text)
    audio_text = re.sub(r"\s*\n\s*", ". ", audio_text).strip()
    return audio_text

def get_tts_voice(text: str, language: str = "") -> str:
    """Exact Edge TTS voice selection from Streamlit."""
    clean = text or ""
    devanagari_count = len(re.findall(r"[\u0900-\u097f]", clean))
    latin_count = len(re.findall(r"[A-Za-z]", clean))

    if devanagari_count >= 2 or language == "mr":
        return "mr-IN-AarohiNeural"
    if (latin_count > devanagari_count and latin_count >= 3) or language == "en":
        return "en-IN-NeerjaNeural"
    return "mr-IN-AarohiNeural"
    if (latin_count > devanagari_count and latin_count >= 3) or language == "en":
        return "en-IN-NeerjaNeural"
    return "mr-IN-AarohiNeural"

# -----------------------------------------------------------------------------
# EDGE TTS MARATHI / ENGLISH AUDIO GENERATION
# -----------------------------------------------------------------------------
@app.post("/api/tts")
async def generate_tts(req: TTSRequest):
    if not edge_tts:
        raise HTTPException(status_code=500, detail="Edge TTS library is not installed")

    voice = req.voice if req.voice in TTS_VOICES.values() else get_tts_voice(req.text)
    clean_speech = prepare_speech_phonetics(req.text, voice)
    if len(clean_speech) > 750:
        spoken_text = clean_speech[:750]
        sentence_end = re.search(r'([.!?।])(?=[^.!?।]*$)', spoken_text)
        if sentence_end and sentence_end.end() > 600:
            spoken_text = spoken_text[:sentence_end.end()]
    else:
        spoken_text = clean_speech
    try:
        communicate = edge_tts.Communicate(spoken_text, voice, rate="+10%")
        audio_bytes = bytearray()
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_bytes.extend(chunk["data"])
        
        b64_audio = base64.b64encode(audio_bytes).decode("utf-8")
        return {"success": True, "audio_data": f"data:audio/mp3;base64,{b64_audio}"}
    except Exception as e:
        logger.error(f"TTS error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# -----------------------------------------------------------------------------
# RECEIPTS & LEDGER DATABASE
# -----------------------------------------------------------------------------
@app.get("/api/receipts")
def get_receipts(search: Optional[str] = None):
    conn = get_db()
    if search:
        s = f"%{search}%"
        rows = conn.execute("SELECT * FROM receipts WHERE vendor_name LIKE ? OR category LIKE ? OR date LIKE ? ORDER BY id DESC", (s, s, s)).fetchall()
    else:
        rows = conn.execute("SELECT * FROM receipts ORDER BY id DESC").fetchall()
    conn.close()
    
    result = []
    for r in rows:
        d = dict(r)
        try:
            d["raw_json"] = json.loads(d["raw_json"]) if d["raw_json"] else {}
        except Exception:
            d["raw_json"] = {}
        result.append(d)
    return result

@app.delete("/api/receipts/{receipt_id}")
def delete_receipt(receipt_id: int):
    conn = get_db()
    conn.execute("DELETE FROM receipts WHERE id = ?", (receipt_id,))
    conn.commit()
    conn.close()
    return {"success": True}

# -----------------------------------------------------------------------------
# CUSTOMER KHATA (DIGITAL UDHAR LEDGER)
# -----------------------------------------------------------------------------
@app.get("/api/khata")
def get_khata():
    conn = get_db()
    rows = [dict(r) for r in conn.execute("SELECT * FROM customer_khata ORDER BY id DESC").fetchall()]
    conn.close()

    # Calculate per-customer balance summary
    cust_balances = {}
    for r in rows:
        c_name = r["customer_name"]
        if c_name not in cust_balances:
            cust_balances[c_name] = {
                "name": c_name,
                "phone": r.get("phone", ""),
                "credit": 0.0,
                "paid": 0.0,
                "balance": 0.0,
                "latest_due": r.get("due_date", "")
            }
        if r["transaction_type"] == "Credit Given":
            cust_balances[c_name]["credit"] += r["amount"]
            cust_balances[c_name]["balance"] += r["amount"]
        else:
            cust_balances[c_name]["paid"] += r["amount"]
            cust_balances[c_name]["balance"] -= r["amount"]

    return {
        "transactions": rows,
        "customers": list(cust_balances.values())
    }

@app.post("/api/khata")
def add_khata_entry(req: KhataEntryRequest):
    conn = get_db()
    cursor = conn.cursor()
    today_str = date.today().strftime("%Y-%m-%d")
    cursor.execute(
        "INSERT INTO customer_khata (customer_name, phone, amount, transaction_type, date, due_date, notes) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (req.customer_name.strip(), req.phone.strip(), req.amount, req.transaction_type, today_str, req.due_date, req.notes)
    )
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    log_activity(req.username or "admin", f"Added Khata #{new_id} for {req.customer_name} (₹{req.amount} - {req.transaction_type})")
    return {"success": True, "id": new_id}

@app.delete("/api/khata/{entry_id}")
def delete_khata_entry(entry_id: int):
    conn = get_db()
    conn.execute("DELETE FROM customer_khata WHERE id = ?", (entry_id,))
    conn.commit()
    conn.close()
    return {"success": True}

# -----------------------------------------------------------------------------
# INVENTORY & BUSINESS OPERATIONS
# -----------------------------------------------------------------------------
@app.get("/api/inventory")
def get_inventory():
    conn = get_db()
    rows = [dict(r) for r in conn.execute("SELECT * FROM shop_inventory ORDER BY id DESC").fetchall()]
    conn.close()
    return rows

@app.post("/api/inventory")
def add_inventory_item(req: InventoryItemRequest):
    conn = get_db()
    conn.execute(
        "INSERT INTO shop_inventory (item_name, stock_qty, unit, alert_limit, selling_price) VALUES (?, ?, ?, ?, ?)",
        (req.item_name.strip(), req.stock_qty, req.unit, req.alert_limit, req.selling_price)
    )
    conn.commit()
    conn.close()
    return {"success": True}

@app.delete("/api/inventory/{item_id}")
def delete_inventory_item(item_id: int):
    conn = get_db()
    conn.execute("DELETE FROM shop_inventory WHERE id = ?", (item_id,))
    conn.commit()
    conn.close()
    return {"success": True}

@app.get("/api/expenses")
def get_expenses():
    conn = get_db()
    rows = [dict(r) for r in conn.execute("SELECT * FROM business_expenses ORDER BY id DESC").fetchall()]
    conn.close()
    return rows

@app.post("/api/expenses")
def add_expense(req: ExpenseRequest):
    conn = get_db()
    today_str = date.today().strftime("%Y-%m-%d")
    conn.execute(
        "INSERT INTO business_expenses (expense_title, amount, category, date, notes) VALUES (?, ?, ?, ?, ?)",
        (req.expense_title.strip(), req.amount, req.category, today_str, req.notes)
    )
    conn.commit()
    conn.close()
    return {"success": True}

# -----------------------------------------------------------------------------
# NEURAL AI STUDIO (RAG ENGINE QUERY & VOICE ACTION EXECUTOR)
# -----------------------------------------------------------------------------
@app.post("/api/rag-chat")
async def rag_chat(req: RAGChatRequest):
    # 1. Voice Action Command Detection & Auto-Execution
    action_status = ""
    user_msg = req.message.strip()

    # (A) उधारी नोंदवणे (Add Khata Credit)
    if any(kw in user_msg for kw in ["उधारी नोंदव", "उधारी लिही", "उधारी कर", "उधारी झाली", "उधारी दिली", "उधारी नोंद", "उधारी सेव्ह", "credit दे"]):
        try:
            phone_m = re.search(r"(?<!\d)[6-9]\d{9}(?!\d)", user_msg)
            phone = phone_m.group(0) if phone_m else ""
            txt = user_msg.replace(phone, "") if phone else user_msg
            amt_matches = re.findall(r"\d+(?:[.,]\d+)?", txt)
            amount = float(amt_matches[0].replace(",", "")) if amt_matches else 0.0
            ignored = {"उधारी", "नोंदव", "नोंदवा", "लिही", "लिहा", "कर", "करा", "झाली", "झाले", "दिली", "नोंद", "सेव्ह", "credit", "दे", "रुपये", "रुपया", "रु", "₹"}
            parts = [re.sub(r"^[.,!?;:]+|[.,!?;:]+$", "", w) for w in txt.split() if not re.search(r"\d", w) and w.casefold() not in ignored]
            cust_name = " ".join(p for p in parts if p).strip() or "ग्राहक"
            if amount > 0:
                conn = get_db()
                conn.execute(
                    "INSERT INTO customer_khata (customer_name, phone, amount, transaction_type, date, due_date, notes) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (cust_name, phone, amount, "Credit Given", date.today().strftime("%Y-%m-%d"), "", user_msg)
                )
                conn.commit()
                conn.close()
                action_status = f"✅ Customer Khata मध्ये {cust_name} साठी ₹{amount:,.2f} उधारी नोंदवली गेली."
        except Exception as e:
            action_status = f"उधारी नोंद त्रुटी: {e}"

    # (B) जमा / वसुली नोंदवणे (Record Customer Payment)
    elif any(kw in user_msg for kw in ["जमा कर", "जमा लिही", "जमा नोंदव", "जमा झाले", "पैसे दिले", "पावती कर", "पेमेंट जमा", "हप्ता दिला"]):
        try:
            phone_m = re.search(r"(?<!\d)[6-9]\d{9}(?!\d)", user_msg)
            phone = phone_m.group(0) if phone_m else ""
            txt = user_msg.replace(phone, "") if phone else user_msg
            amt_matches = re.findall(r"\d+(?:[.,]\d+)?", txt)
            amount = float(amt_matches[0].replace(",", "")) if amt_matches else 0.0
            ignored = {"जमा", "कर", "करा", "लिही", "लिहा", "नोंदव", "नोंदवा", "झाले", "झाली", "पैसे", "दिले", "पावती", "पेमेंट", "हप्ता", "दिला", "सेव्ह", "रुपये", "रु", "₹"}
            parts = [re.sub(r"^[.,!?;:]+|[.,!?;:]+$", "", w) for w in txt.split() if not re.search(r"\d", w) and w.casefold() not in ignored]
            cust_name = " ".join(p for p in parts if p).strip() or "ग्राहक"
            if amount > 0:
                conn = get_db()
                conn.execute(
                    "INSERT INTO customer_khata (customer_name, phone, amount, transaction_type, date, due_date, notes) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (cust_name, phone, amount, "Payment Received", date.today().strftime("%Y-%m-%d"), "", user_msg)
                )
                conn.commit()
                conn.close()
                action_status = f"✅ Customer Khata मध्ये {cust_name} यांच्याकडून ₹{amount:,.2f} जमा नोंदवले गेले."
        except Exception as e:
            action_status = f"जमा नोंद त्रुटी: {e}"

    # (C) व्यवसाय खर्च नोंदवणे (Record Expense)
    elif any(kw in user_msg for kw in ["खर्च नोंदव", "खर्च लिही", "खर्च जोड", "खर्च झाला", "खर्च सेव्ह", "expense add"]):
        try:
            amt_matches = re.findall(r"\d+(?:[.,]\d+)?", user_msg)
            amount = float(amt_matches[0].replace(",", "")) if amt_matches else 0.0
            ignored = {"खर्च", "नोंदव", "नोंदवा", "लिही", "लिहा", "जोड", "जोडा", "झाला", "झाले", "सेव्ह", "करा", "रुपये", "रुपया", "रु", "₹", "expense", "add"}
            parts = [re.sub(r"^[.,!?;:]+|[.,!?;:]+$", "", w) for w in user_msg.split() if not re.search(r"\d", w) and w.casefold() not in ignored]
            exp_title = " ".join(p for p in parts if p).strip() or "दुकान खर्च"
            if amount > 0:
                conn = get_db()
                conn.execute(
                    "INSERT INTO business_expenses (expense_title, amount, category, date, notes) VALUES (?, ?, ?, ?, ?)",
                    (exp_title, amount, "दुकान खर्च", date.today().strftime("%Y-%m-%d"), user_msg)
                )
                conn.commit()
                conn.close()
                action_status = f"✅ दुकान खर्च नोंद: '{exp_title}' साठी ₹{amount:,.2f} सेव्ह झाले."
        except Exception as e:
            action_status = f"खर्च नोंद त्रुटी: {e}"

    # 2. Build Rich Live SQLite Context
    conn = get_db()
    total_sales = conn.execute("SELECT SUM(grand_total) FROM receipts").fetchone()[0] or 0.0
    bill_count = conn.execute("SELECT COUNT(*) FROM receipts").fetchone()[0] or 0
    today_str = date.today().strftime("%Y-%m-%d")
    today_sales = conn.execute("SELECT SUM(grand_total) FROM receipts WHERE date = ?", (today_str,)).fetchone()[0] or 0.0
    recent_receipts = [dict(r) for r in conn.execute("SELECT vendor_name, date, grand_total FROM receipts ORDER BY id DESC LIMIT 5").fetchall()]
    
    # Khata & Customer Dues context
    khata_rows = [dict(r) for r in conn.execute("SELECT customer_name, amount, transaction_type, due_date FROM customer_khata ORDER BY id DESC LIMIT 10").fetchall()]
    credit_sum = conn.execute("SELECT SUM(amount) FROM customer_khata WHERE transaction_type = 'Credit Given'").fetchone()[0] or 0.0
    paid_sum = conn.execute("SELECT SUM(amount) FROM customer_khata WHERE transaction_type = 'Payment Received'").fetchone()[0] or 0.0
    pending_udhar = max(0.0, credit_sum - paid_sum)

    # Calculate individual customer balances
    cust_dues = {}
    for row in conn.execute("SELECT customer_name, amount, transaction_type FROM customer_khata").fetchall():
        c = row["customer_name"]
        a = float(row["amount"] or 0)
        if row["transaction_type"] == "Credit Given":
            cust_dues[c] = cust_dues.get(c, 0.0) + a
        elif row["transaction_type"] == "Payment Received":
            cust_dues[c] = cust_dues.get(c, 0.0) - a
    sorted_dues = sorted([(k, max(0.0, v)) for k, v in cust_dues.items() if v > 0], key=lambda x: x[1], reverse=True)

    # Inventory context (Full inventory for accurate stock lookups)
    all_inv = [dict(r) for r in conn.execute("SELECT item_name, stock_qty, unit, alert_limit, selling_price FROM shop_inventory ORDER BY stock_qty ASC").fetchall()]
    low_stock = [i for i in all_inv if i["stock_qty"] <= i["alert_limit"]]

    # Expenses & Profit context
    total_expenses = conn.execute("SELECT SUM(amount) FROM business_expenses").fetchone()[0] or 0.0
    today_expenses = conn.execute("SELECT SUM(amount) FROM business_expenses WHERE date = ?", (today_str,)).fetchone()[0] or 0.0
    recent_expenses = [dict(r) for r in conn.execute("SELECT expense_title, category, amount, date FROM business_expenses ORDER BY id DESC LIMIT 5").fetchall()]
    net_profit = total_sales - total_expenses
    conn.close()

    # Targeted Query Entity Search (Directly from Streamlit)
    specific_context = []
    clean_q_words = re.findall(r'[\u0900-\u097fA-Za-z]+', req.message)
    for w in clean_q_words:
        if len(w) >= 3 and w.lower() not in ["किती", "आहे", "सांगा", "माहिती", "काय", "कसे", "कोठे", "येणे", "बाकी", "shop", "what", "how"]:
            c_match = conn.execute("SELECT customer_name, SUM(CASE WHEN transaction_type = 'Credit Given' THEN amount ELSE -amount END) as bal FROM customer_khata WHERE customer_name LIKE ? GROUP BY customer_name", (f"%{w}%",)).fetchone()
            if c_match and c_match[0]:
                specific_context.append(f"शोधलेला ग्राहक '{c_match[0]}': शिल्लक उधारी = {float(c_match[1] or 0):,.2f} रुपये")
            s_match = conn.execute("SELECT item_name, stock_qty, unit, selling_price FROM shop_inventory WHERE item_name LIKE ?", (f"%{w}%",)).fetchall()
            for sm in s_match:
                specific_context.append(f"शोधलेली वस्तू '{sm[0]}': साठा = {sm[1]} {sm[2]}, दर = ₹{sm[3]}")

    db_context = f"""
    [लाइव्ह दुकानाची आकडेवारी (Live Shop Statistics)]:
    - आजची विक्री: {today_sales:,.2f} रुपये
    - एकूण विक्री: {total_sales:,.2f} रुपये ({bill_count} पावत्या)
    - बाजारातील एकूण उधारी येणे बाकी: {pending_udhar:,.2f} रुपये
    - प्रमुख उधारी ग्राहक (शिल्लक): {sorted_dues[:5]}
    - कमी साठा (Low Stock Warning): {low_stock}
    - संपूर्ण साठा: {all_inv}
    - एकूण व्यवसाय खर्च: {total_expenses:,.2f} रुपये
    - निव्वळ नफा (Net Margin): {net_profit:,.2f} रुपये
    - अलीकडील पावत्या: {recent_receipts}
    - अलीकडील खर्च: {recent_expenses}
    {('- विशिष्ट शोध परिणाम: ' + '; '.join(specific_context)) if specific_context else ''}
    """

    query_lang = detect_msg_language(req.message, req.lang or "mr")
    is_marathi = (query_lang == "mr")

    # Exact instructions from Streamlit commit 32e8d15 and e54dfe6
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
        "project details, creators, developers, guide, college, or ledger records such as receipts, credit, "
        "expenses, and stock, use the supplied reference context as the source of truth.\n"
        "When asked who made the project, who the developers are, or who the guide is, ALWAYS explicitly and completely state the names:\n"
        "- प्रकल्प मार्गदर्शक (Project Guide): प्रा. कैसर अतार सर (Prof. Kaisar Atar Sir)\n"
        "- प्रमुख विकासक (Lead Developer): संकेत किर्दत (Sanket Kirdat)\n"
        "- इतर विकासक (Developers): साक्षी भगत, वैष्णवी ढवळे, ऋषिकेश मुळीक (Sakshi Bhagat, Vaishnavi Dhavale, Rushikesh Mulik)\n"
        "- महाविद्यालय (College): अरविंद गवळी कॉलेज ऑफ इंजिनिअरिंग, सातारा (Arvind Gavali College of Engineering, Satara)\n"
        "If answering in Marathi, write all names strictly in Marathi Devanagari script without brackets or English translations.\n"
        "Format monetary answers clearly and professionally. Use bold text or bullet points where appropriate.\n"
        "STRICT BREVITY: Answer ONLY what was specifically asked. Keep answers concise, factual, and strictly limited to the user's specific query ('जे विचारले तेवढेच मर्यादित व अचूक उत्तर द्या').\n"
        "Item & Customer Names: When answering in Marathi use only Marathi names; when answering in English use only English names.\n"
        "Do not invent internal project facts or database values. If a requested internal "
        "fact is absent from the supplied context, say that it is not present in the "
        "available context instead of guessing. Always follow the response-language instruction."
    )

    rag_context = f"""
    The following are reference facts only. They do not set the response language.

    [Reference context]:
    - Project: VernaLedger AI
    - Project Guide: प्रा. कैसर अतार सर (Prof. Kaisar Atar Sir)
    - Lead Developer: संकेत किर्दत (Sanket Kirdat)
    - Developers: साक्षी भगत, वैष्णवी ढवळे, ऋषिकेश मुळीक (Sakshi Bhagat, Vaishnavi Dhavale, Rushikesh Mulik)
    - College: अरविंद गवळी कॉलेज ऑफ इंजिनिअरिंग, सातारा (Arvind Gavali College of Engineering, Satara)
    - Database Context:
    {db_context}
    - Database Action Result:
    {action_status or "No database action was performed."}

    [Recent conversation context]:
    {history_text or "(none)"}
    """

    api_key = get_api_key()
    answer = None
    if api_key and genai:
        try:
            genai.configure(api_key=api_key)
            generation_config = {
                "temperature": 0.3,
                "max_output_tokens": 1024,
            }
            models_to_try = ['gemini-2.5-flash-lite', 'gemini-2.5-flash', 'gemini-1.5-flash', 'gemini-flash-lite-latest', 'gemini-pro']
            for m in models_to_try:
                try:
                    model = genai.GenerativeModel(
                        model_name=m,
                        system_instruction=f"{language_instruction}\n\n{assistant_instruction}",
                        generation_config=generation_config
                    )
                    res = model.generate_content([rag_context, f"[Latest user query — answer this query]\n{req.message}"])
                    if res and res.text:
                        answer = res.text.strip()
                        break
                except Exception:
                    continue
        except Exception as e:
            logger.error(f"Gemini error: {e}")

    if not answer:
        if action_status:
            answer = action_status
        else:
            normalized = user_msg.casefold()
            is_english = (query_lang == "en")

            # Helper for localized name in fallback
            def clean_name(val):
                if "(" in val and ")" in val:
                    parts = val.split("(")
                    return parts[1].replace(")", "").strip() if is_english else parts[0].strip()
                return val

            if any(word in normalized for word in ["कोणाकडे जास्त", "जास्त उधारी", "who owes", "highest credit", "highest due"]):
                if sorted_dues:
                    top_list = [f"{clean_name(name)}: ₹{amt:,.2f}" for name, amt in sorted_dues[:3]]
                    answer = (
                        f"Top pending dues: {', '.join(top_list)}. Total credit: ₹{pending_udhar:,.2f}."
                        if is_english else
                        f"सर्वात जास्त उधारी: {', '.join(top_list)}. एकूण बाकी उधारी: ₹{pending_udhar:,.2f}."
                    )
                else:
                    answer = "No pending customer dues currently." if is_english else "सध्या कोणाकडेही उधारी बाकी नाही."
            elif any(word in normalized for word in ["उधारी", "credit", "pending", "बाकी"]):
                answer = (
                    f"Total pending customer credit is ₹{pending_udhar:,.2f}."
                    if is_english else
                    f"एकूण बाकी उधारी ₹{pending_udhar:,.2f} आहे."
                )
            elif any(word in normalized for word in ["कमी साठा", "low stock", "साठा संपत", "out of stock"]):
                if low_stock:
                    items = ", ".join(f"{clean_name(item['item_name'])} ({item['stock_qty']} {item['unit']})" for item in low_stock)
                    answer = (f"Low-stock items: {items}." if is_english else f"कमी साठा असलेल्या वस्तू: {items}.")
                else:
                    answer = "All items have sufficient stock." if is_english else "सर्व वस्तूंचा साठा मुबलक आहे."
            elif any(word in normalized for word in ["साठा", "stock", "inventory"]):
                answer = (
                    f"There are {len(all_inv)} items in stock. Low stock items: {len(low_stock)}."
                    if is_english else
                    f"दुकानात एकूण {len(all_inv)} वस्तूंचा साठा आहे. यापैकी {len(low_stock)} वस्तूंचा साठा कमी आहे."
                )
            elif any(word in normalized for word in ["नफा", "profit", "margin", "खर्च", "expense"]):
                answer = (
                    f"Total expenses: ₹{total_expenses:,.2f}. Net margin: ₹{net_profit:,.2f}."
                    if is_english else
                    f"एकूण दुकान खर्च: ₹{total_expenses:,.2f}. निव्वळ नफा (Net Margin): ₹{net_profit:,.2f}."
                )
            elif any(word in normalized for word in ["आजची विक्री", "today's sales", "today sales"]):
                answer = (
                    f"Today's sales are ₹{today_sales:,.2f}."
                    if is_english else
                    f"आजची एकूण विक्री ₹{today_sales:,.2f} आहे."
                )
            elif any(word in normalized for word in ["विक्री", "sales", "revenue", "हिशोब"]):
                answer = (
                    f"Today's sales: ₹{today_sales:,.2f}. Gross revenue: ₹{total_sales:,.2f} across {bill_count} bills."
                    if is_english else
                    f"आजची विक्री: ₹{today_sales:,.2f}. एकूण विक्री: ₹{total_sales:,.2f} ({bill_count} पावत्या)."
                )
            elif any(word in normalized for word in ["कोणी", "developer", "developers", "project", "प्रकल्प", "guide", "मार्गदर्शक", "kaisar", "atar", "attar", "ढवळे", "मुळीक", "गवळी"]):
                answer = (
                    "Project Guide: Prof. Kaisar Atar Sir. Lead Developer: Sanket Kirdat. Developers: Sakshi Bhagat, Vaishnavi Dhavale and Rushikesh Mulik. College: Arvind Gavali College of Engineering, Satara, Maharashtra."
                    if is_english else
                    "प्रकल्प मार्गदर्शक: प्रा. कैसर अतार सर. प्रमुख विकासक: संकेत किर्दत. इतर विकासक: साक्षी भगत, वैष्णवी ढवळे आणि ऋषिकेश मुळीक. महाविद्यालय: अरविंद गवळी कॉलेज ऑफ इंजिनिअरिंग, सातारा."
                )
            else:
                answer = (
                    f"Today's sales: ₹{today_sales:,.2f} | Pending credit: ₹{pending_udhar:,.2f}."
                    if is_english else
                    f"आजची विक्री: ₹{today_sales:,.2f} | बाकी उधारी: ₹{pending_udhar:,.2f}."
                )

    # 3. Edge TTS Voice Output (Auto voice speech if enabled with Streamlit exact voice logic)
    audio_data = None
    if req.voice_output and edge_tts:
        try:
            voice = get_tts_voice(answer, query_lang)
            clean_speech = prepare_speech_phonetics(answer, voice)
            if len(clean_speech) > 750:
                spoken_text = clean_speech[:750]
                sentence_end = re.search(r'([.!?।])(?=[^.!?।]*$)', spoken_text)
                if sentence_end and sentence_end.end() > 600:
                    spoken_text = spoken_text[:sentence_end.end()]
            else:
                spoken_text = clean_speech

            communicate = edge_tts.Communicate(spoken_text, voice, rate="+10%")
            audio_bytes = bytearray()
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    audio_bytes.extend(chunk["data"])
            b64_audio = base64.b64encode(audio_bytes).decode("utf-8")
            audio_data = f"data:audio/mp3;base64,{b64_audio}"
        except Exception as e:
            logger.warning(f"Voice output generation error: {e}")

    return {
        "success": True,
        "answer": answer,
        "action_status": action_status,
        "audio_data": audio_data
    }

@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "app": "VernaLedger.AI Merchant Pro v7.5",
        "runtime": "Vercel Serverless Python",
        "timestamp": datetime.now().isoformat()
    }

# -----------------------------------------------------------------------------
# DUAL ROUTE ALIASES (SUPPORTS BOTH /api/* AND /* FOR VERCEL REWRITES)
# -----------------------------------------------------------------------------
for route in list(app.routes):
    if hasattr(route, "path") and route.path.startswith("/api/"):
        alias_path = route.path.replace("/api", "", 1)
        if alias_path:
            app.add_api_route(alias_path, route.endpoint, methods=route.methods)

# -----------------------------------------------------------------------------
# STATIC FILES SERVING (FOR LOCAL RUN & FALLBACK)
# -----------------------------------------------------------------------------
public_dir = os.path.join(ROOT_DIR, "public")
if os.path.exists(public_dir):
    from fastapi.staticfiles import StaticFiles
    app.mount("/", StaticFiles(directory=public_dir, html=True), name="static")
