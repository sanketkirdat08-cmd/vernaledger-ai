import urllib.request
import json
import base64
import time
from api.index import get_api_key

api_key = get_api_key()
img_path = r'C:/Users/mahan/.gemini/antigravity/brain/614ae62e-d2c3-4a82-bd0e-932399834a99/.user_uploaded/media_1794849407109_384ce6fe.jpg'
with open(img_path, 'rb') as f:
    b64_data = base64.b64encode(f.read()).decode('utf-8')

prompt = """You are VernaLedger Smart Scanner, an expert multilingual OCR system for Indian retail receipts and Marathi handwritten Kirana slips.

STRICT INSTRUCTIONS:
1. Extract EVERY single handwritten line verbatim in Marathi Devanagari script character-for-character. Do NOT translate into English (e.g. "गहू" must stay "गहू", "तेल" must stay "तेल", "सोनल किराणा" must stay "सोनल किराणा").
2. vendor_name: Exact shop name or merchant name at the top in Marathi. If none, return "किराणा पावती".
3. date: Date in YYYY-MM-DD if written, else null.
4. items: Array of objects for every single item row on the paper:
   - item_name: Exact item name in Marathi Devanagari (e.g. "गहू", "तेल", "साखर").
   - quantity: Quantity string with unit (e.g. "10 किलो", "5 ltr", "1 kg").
   - rate: Numeric price per unit (float). If not explicitly written, compute: total_price / quantity.
   - total_price: Numeric line total in rupees (float, e.g. 50.0, 100.0). Do not include currency text like 'रुपये' in the number.
5. grand_total: Total bill amount as numeric float (e.g. 150.0).

Return valid JSON strictly matching:
{
  "vendor_name": "string",
  "date": "YYYY-MM-DD or null",
  "category": "General",
  "items": [
    {"item_name": "string", "quantity": "string", "rate": 0.0, "total_price": 0.0}
  ],
  "grand_total": 0.0
}"""

url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-lite-latest:generateContent?key={api_key}"
payload = {
    "contents": [{
        "parts": [
            {"text": prompt},
            {
                "inline_data": {
                    "mime_type": "image/jpeg",
                    "data": b64_data
                }
            }
        ]
    }],
    "generationConfig": {
        "responseMimeType": "application/json",
        "temperature": 0.1
    }
}
req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers={"Content-Type": "application/json"})
t0 = time.time()
with urllib.request.urlopen(req, timeout=15) as resp:
    data = json.loads(resp.read().decode('utf-8'))
    text = data['candidates'][0]['content']['parts'][0]['text']
    print(f"Done in {time.time()-t0:.2f}s:")
    print(text)
