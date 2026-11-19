with open('api/index.py', 'r', encoding='utf-8') as f:
    api_lines = f.readlines()

print("=== api/index.py search ===")
for i, line in enumerate(api_lines):
    if any(k in line.lower() for k in ['def extract_receipt', 'disambiguate', 'def parse_voice', 'def init_db', 'def deduct', 'seed_kirana', 'stock_qty']):
        print(f"Line {i+1}: {line.strip()[:90]}")

with open('public/app.js', 'r', encoding='utf-8') as f:
    app_lines = f.readlines()

print("\n=== public/app.js search ===")
for i, line in enumerate(app_lines):
    if any(k in line.lower() for k in ['function initspeech', 'function rendertable', 'function renderpos', 'function toggletheme', 'function exporttoexcel', 'deductstock', 'parsevoicetranscript', 'function openlightbox']):
        print(f"Line {i+1}: {line.strip()[:90]}")
