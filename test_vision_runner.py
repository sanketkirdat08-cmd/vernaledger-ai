import urllib.request
import json
import base64
import time
from api.index import get_api_key

api_key = get_api_key()
img_path = r'C:/Users/mahan/.gemini/antigravity/brain/614ae62e-d2c3-4a82-bd0e-932399834a99/.user_uploaded/media_1794849407109_384ce6fe.jpg'
with open(img_path, 'rb') as f:
    b64_data = base64.b64encode(f.read()).decode('utf-8')

prompt = """You are an expert multilingual OCR system for Marathi Kirana receipts.
Extract verbatim Devanagari text. Do not translate.
Return JSON with keys: vendor_name, date, items (list of {item_name, quantity, rate, total_price}), grand_total."""

models_to_test = ['gemini-flash-lite-latest', 'gemini-2.5-flash', 'gemini-flash-latest']

for m in models_to_test:
    t0 = time.time()
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent?key={api_key}"
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
            "responseMimeType": "application/json"
        }
    }
    req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            text = data['candidates'][0]['content']['parts'][0]['text']
            print(f"=== {m} SUCCESS ({time.time()-t0:.2f}s) ===")
            print(text)
            break
    except Exception as e:
        print(f"=== {m} FAILED ({time.time()-t0:.2f}s) ===: {e}")
