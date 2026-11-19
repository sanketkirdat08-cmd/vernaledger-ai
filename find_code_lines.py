with open('api/index.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, l in enumerate(lines):
    if '/extract-receipt' in l or 'disambiguate_kirana_rate' in l or 'disambiguate_rate' in l or 'def extract_receipt' in l:
        print(f"api/index.py Line {i+1}: {l.strip()[:90]}")

with open('public/app.js', 'r', encoding='utf-8') as f:
    app_lines = f.readlines()

for i, l in enumerate(app_lines):
    if 'disambiguate_kirana_rate' in l or 'disambiguate' in l or 'processreceiptimage' in l.lower() or 'handleocr' in l.lower() or 'renderbillitems' in l.lower():
        print(f"public/app.js Line {i+1}: {l.strip()[:90]}")
