import google.generativeai as genai
from PIL import Image
import json
import sqlite3
import re
import os
import logging
import asyncio
import time
from gtts import gTTS
import edge_tts
from schema import ReceiptData

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_db() -> None:
    conn = sqlite3.connect("ledger.db")
    cursor = conn.cursor()
    cursor.execute("PRAGMA journal_mode = WAL;")
    cursor.execute("PRAGMA synchronous = NORMAL;")
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS receipts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        vendor_name TEXT,
        date TEXT,
        category TEXT,
        grand_total REAL,
        raw_json TEXT
    )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_receipts_lookup ON receipts(vendor_name, date, grand_total);")
    conn.commit()
    conn.close()

init_db()

def extract_valid_json(text: str) -> dict:
    text = re.sub(r'```json\s*', '', text)
    text = re.sub(r'```\s*$', '', text).strip()
    
    start_idx = text.find('{')
    end_idx = text.rfind('}')
    
    if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
        json_str = text[start_idx:end_idx + 1]
        return json.loads(json_str)
        
    return json.loads(text)

_PRIORITY_FAST_MODELS = [
    'gemini-3.5-flash-lite',
    'gemini-flash-lite-latest',
    'gemini-3.1-flash-lite',
    'gemini-3.8-flash',
]
_CACHED_WORKING_MODELS = None

def get_active_gemini_models():
    """Returns fastest working vision models instantly without expensive blocking network discovery."""
    global _CACHED_WORKING_MODELS
    if _CACHED_WORKING_MODELS:
        return _CACHED_WORKING_MODELS
    return _PRIORITY_FAST_MODELS

def update_working_model(model_name: str):
    global _CACHED_WORKING_MODELS
    _CACHED_WORKING_MODELS = [model_name] + [m for m in _PRIORITY_FAST_MODELS if m != model_name]

def process_receipt_advanced(image_input, api_key: str, force_save: bool = False) -> dict:
    genai.configure(api_key=api_key)
    
    if isinstance(image_input, (str, os.PathLike)):
        img = Image.open(image_input)
    else:
        if hasattr(image_input, "seek"):
            image_input.seek(0)
        img = Image.open(image_input)

    img_copy = img.convert('RGB')
    img_copy.thumbnail((1280, 1280), Image.Resampling.LANCZOS)

    prompt = """
    You are an expert document OCR scanner specialized in Marathi, Devanagari handwritten and printed ledgers, invoices, and retail receipts.
    CRITICAL OCR INSTRUCTIONS:
    1. Extract the Vendor/Shop Name at the top in complete Marathi or English script.
    2. Carefully scan and extract EVERY single line item row listed in the receipt. DO NOT skip or omit any rows.
    3. Read the complete item name accurately in original Marathi / English script (e.g., 'शेंगदाणा तेल १ लि', 'साखर ५ किलो', 'हळद पावडर', 'गहू', 'तूर डाळ'). DO NOT truncate or abbreviate names.
    4. For each row, accurately extract:
       - item_name: Full name of the item.
       - quantity: Numeric quantity along with exact measurement unit (e.g. '1 kg', '2 pcs', '500 gm', '1 ltr', '1 pkt'). If unit is not written, specify count as string (e.g. '1').
       - rate: Price per unit in rupees as a numeric float (e.g. 45.0). Remove commas or currency symbols.
       - total_price: Total amount for this item line in rupees as a numeric float (quantity * rate).
    5. MATHEMATICAL VERIFICATION:
       - Verify that total_price = numeric quantity * rate for each item.
       - Verify that grand_total = sum of all item total_price values.
       - If the receipt total is blurry, faint, or mathematically incorrect, compute and set the correct sum.

    Output strictly in this JSON structure:
    {
      "vendor_name": "string",
      "date": "string",
      "category": "General",
      "items": [
        {"item_name": "string", "quantity": "string", "rate": 0.0, "total_price": 0.0}
      ],
      "grand_total": 0.0
    }
    Return ONLY valid JSON object.
    """
    
    models_to_try = get_active_gemini_models()
    response = None
    last_error = None

    for model_name in models_to_try:
        try:
            model = genai.GenerativeModel(model_name)
            res = model.generate_content([prompt, img_copy])
            if res and res.text:
                response = res
                update_working_model(model_name)
                logger.info(f"Successfully processed receipt using active model: {model_name}")
                break
        except Exception as exc:
            last_error = exc
            logger.warning(f"Model {model_name} failed: {exc}, trying next model...")
            continue

    if not response or not response.text:
        raise RuntimeError(f"AI स्कॅनिंग त्रुटी: {last_error!s}")

    raw_text = response.text
    data_dict = extract_valid_json(raw_text)

    if data_dict.get('items') and data_dict.get('grand_total', 0) == 0:
        calc_total = sum(item.get('total_price', 0) for item in data_dict['items'])
        if calc_total > 0:
            data_dict['grand_total'] = calc_total

    validated_data = ReceiptData(**data_dict)

    clean_vendor = validated_data.vendor_name
    if '\\u' in clean_vendor:
        try:
            clean_vendor = clean_vendor.encode('utf-8').decode('unicode-escape')
        except UnicodeDecodeError:
            logger.debug("Unicode decoding skipped for vendor name.")

    clean_cat = validated_data.category
    if '\\u' in clean_cat:
        try:
            clean_cat = clean_cat.encode('utf-8').decode('unicode-escape')
        except UnicodeDecodeError:
            logger.debug("Unicode decoding skipped for category.")

    validated_data.vendor_name = clean_vendor
    validated_data.category = clean_cat

    ret_dict = validated_data.model_dump()

    with sqlite3.connect("ledger.db") as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id FROM receipts WHERE vendor_name = ? AND date = ? AND grand_total = ?",
            (validated_data.vendor_name, validated_data.date, validated_data.grand_total)
        )
        existing_record = cursor.fetchone()

        if existing_record and not force_save:
            ret_dict["is_duplicate"] = True
            ret_dict["existing_id"] = existing_record[0]
            logger.info(f"Duplicate receipt detected for {validated_data.vendor_name} (ID: {existing_record[0]})")
        else:
            raw_json_str = json.dumps(validated_data.model_dump(), ensure_ascii=False)
            cursor.execute(
                "INSERT INTO receipts (vendor_name, date, category, grand_total, raw_json) VALUES (?, ?, ?, ?, ?)",
                (validated_data.vendor_name, validated_data.date, validated_data.category, validated_data.grand_total, raw_json_str)
            )
            conn.commit()
            ret_dict["is_duplicate"] = False

    return ret_dict

def process_voice_billing_advanced(voice_text: str, api_key: str) -> dict:
    genai.configure(api_key=api_key)
    
    prompt = f"""
    You are an expert Marathi financial assistant and math wizard. Convert the following spoken text into a structured receipt JSON object.
    Spoken Input: "{voice_text}"

    CRITICAL MATHEMATICAL TASK:
    1. Extract Vendor/Shop Name if mentioned, otherwise set to "अनामित (Local Shop)".
    2. Extract all item names, quantity, rate per unit, and calculate total_price for each item.
    3. YOU MUST mathematically calculate: total_price = quantity * rate for EVERY item.
    4. YOU MUST mathematically calculate: grand_total = SUM(all item total_price).

    Strict JSON Output Format:
    {{
      "vendor_name": "string",
      "date": "Voice Bill",
      "category": "General",
      "items": [
        {{"item_name": "string", "quantity": "string", "rate": 0.0, "total_price": 0.0}}
      ],
      "grand_total": 0.0
    }}
    Return ONLY valid JSON object.
    """
    
    models_to_try = get_active_gemini_models()
    res = None
    last_error = None

    for model_name in models_to_try:
        try:
            model = genai.GenerativeModel(model_name)
            res = model.generate_content(prompt)
            if res and res.text:
                update_working_model(model_name)
                logger.info(f"Successfully processed voice bill using active model: {model_name}")
                break
        except Exception as exc:
            last_error = exc
            continue

    if not res or not res.text:
        raise RuntimeError(f"व्हॉईस बिल जनरेट करता आले नाही: {last_error!s}")

    data_dict = extract_valid_json(res.text)
    validated_data = ReceiptData(**data_dict)

    with sqlite3.connect("ledger.db") as conn:
        cursor = conn.cursor()
        raw_json_str = json.dumps(validated_data.model_dump(), ensure_ascii=False)
        cursor.execute(
            "INSERT INTO receipts (vendor_name, date, category, grand_total, raw_json) VALUES (?, ?, ?, ?, ?)",
            (validated_data.vendor_name, "Voice Entry", validated_data.category, validated_data.grand_total, raw_json_str)
        )
        conn.commit()

    return validated_data.model_dump()

def generate_marathi_tts(text_marathi: str, output_path: str = "summary.mp3", voice: str = "mr-IN-AarohiNeural") -> str | None:
    try:
        os.makedirs("audio_cache", exist_ok=True)
        if output_path == "summary.mp3":
            output_path = f"audio_cache/tts_{int(time.time() * 1000)}.mp3"
        elif os.path.exists(output_path):
            try:
                os.remove(output_path)
            except PermissionError:
                output_path = f"audio_cache/tts_{os.urandom(4).hex()}.mp3"

        # Clean text for high quality TTS
        clean_text = re.sub(r'[*#_`~>]', ' ', text_marathi)
        clean_text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', clean_text)
        clean_text = re.sub(r'https?://\S+', '', clean_text)
        clean_text = re.sub(r'[\U00010000-\U0010ffff]', '', clean_text)
        clean_text = re.sub(r'\s+', ' ', clean_text).strip()

        if not clean_text:
            return None

        # Take first ~350 chars or first 2 complete sentences for fast conversational voice
        spoken_text = clean_text[:380]
        sentence_end = re.search(r'([.!?।])(?=[^.!?।]*$)', spoken_text)
        if sentence_end and sentence_end.end() > 60:
            spoken_text = spoken_text[:sentence_end.end()]

        v_lower = (voice or "").lower()
        if v_lower.startswith("mr") or "marathi" in v_lower:
            lang = "mr"
        elif v_lower.startswith("hi") or "hindi" in v_lower:
            lang = "hi"
        else:
            lang = "en"

        # Primary: gTTS (fast, reliable, natural pronunciation)
        try:
            tts = gTTS(text=spoken_text, lang=lang, slow=False)
            tts.save(output_path)
            if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                return output_path
        except Exception as gtts_err:
            logger.warning("gTTS generation error, falling back to edge_tts: %s", gtts_err)

        # Fallback: edge_tts with strict 3-second timeout
        try:
            async def _main():
                communicate = edge_tts.Communicate(spoken_text, voice, rate="+15%")
                await communicate.save(output_path)

            asyncio.run(asyncio.wait_for(_main(), timeout=3.0))
            if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                return output_path
        except Exception as edge_err:
            logger.error("edge_tts fallback failed: %s", edge_err)

        return None
    except Exception as exc:
        logger.error("TTS Generation Error: %s", exc)
        return None