with open('api/index.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, l in enumerate(lines):
    if 'extract-receipt' in l or 'disambiguate' in l or 'disambiguate_rate' in l or 'gemini-flash' in l or 'model_name' in l:
        print(f"api/index.py Line {i+1}: {l.strip()[:90]}")

with open('public/app.js', 'r', encoding='utf-8') as f:
    app_lines = f.readlines()

for i, l in enumerate(app_lines):
    if 'disambiguate' in l.lower() or 'exporttoexcel' in l.lower() or 'exportexcel' in l.lower() or 'xlsx' in l.lower() or 'renderbill' in l.lower() or 'renderpos' in l.lower() or 'rendertable' in l.lower() or 'renderinventory' in l.lower():
        print(f"public/app.js Line {i+1}: {l.strip()[:90]}")
