import google.generativeai as genai
from PIL import Image
import json
import sqlite3
import re
import os
import time
import logging
import asyncio
import edge_tts
from schema import ReceiptData

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_db() -> None:
    conn = sqlite3.connect("ledger.db")
    cursor = conn.cursor()
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

def get_active_gemini_models():
    """Returns the absolute fastest models first, skipping the slow list_models API call to save 1s per request."""
    return ['gemini-2.0-flash', 'gemini-1.5-flash', 'gemini-2.0-pro-exp', 'gemini-1.5-pro', 'gemini-1.0-pro']

def process_receipt_advanced(image_path: str, api_key: str, force_save: bool = False) -> dict:
    genai.configure(api_key=api_key)
    
    with Image.open(image_path) as img:
        img_copy = img.copy()
        img_copy.thumbnail((800, 800))

    prompt = """
    You are an expert document OCR scanner for Marathi/Hindi handwritten and printed ledgers/receipts.
    CRITICAL MATHEMATICAL TASK:
    1. Extract the Vendor/Shop Name at the top in Marathi script.
    2. Extract ALL item rows listed in the table or list.
    3. For each row, parse accurately:
       item_name: Name of item.
       quantity: Specify numeric quantity along with exact measurement unit (e.g. '10 kg', '1 ltr'). Remove commas from numbers. If no unit, just the number.
       rate: Price per unit in numeric rupees (e.g. 20.0). Remove commas.
       total_price: Total amount for this line item in rupees.
    
    VERIFICATION RULES:
    - You MUST mathematically verify that: (quantity numeric part) * rate = total_price.
    - If the math on the receipt is wrong or unreadable, YOU MUST CORRECT IT. Set total_price = quantity * rate.
    - You MUST mathematically verify that grand_total = SUM(all item total_price). Do NOT blindly copy a wrong total from the image.

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
                logger.info(f"Successfully processed receipt using active model: {model_name}")
                break
        except Exception as exc:
            last_error = exc
            continue

    if not response or not response.text:
        raise RuntimeError(f"API Connection Error: {last_error!s}")

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

    with sqlite3.connect("ledger.db") as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id FROM receipts WHERE vendor_name = ? AND date = ? AND grand_total = ?",
            (validated_data.vendor_name, validated_data.date, validated_data.grand_total)
        )
        existing_record = cursor.fetchone()

        if existing_record and not force_save:
            raise ValueError(
                f"Duplicate Warning: दुकान '{validated_data.vendor_name}' चे ₹{validated_data.grand_total} चे बिल आधीच रेकॉर्ड केलेले आहे!"
            )

        raw_json_str = json.dumps(validated_data.model_dump(), ensure_ascii=False)
        cursor.execute(
            "INSERT INTO receipts (vendor_name, date, category, grand_total, raw_json) VALUES (?, ?, ?, ?, ?)",
            (validated_data.vendor_name, validated_data.date, validated_data.category, validated_data.grand_total, raw_json_str)
        )
        conn.commit()

    return validated_data.model_dump()

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
        if os.path.exists(output_path):
            try:
                os.remove(output_path)
            except PermissionError:
                output_path = f"summary_{os.urandom(4).hex()}.mp3"

        async def _main():
            communicate = edge_tts.Communicate(text_marathi, voice, rate="+15%")
            await communicate.save(output_path)

        asyncio.run(_main())
        return output_path
    except Exception as exc:
        logger.error("TTS Generation Error: %s", exc)
        return None