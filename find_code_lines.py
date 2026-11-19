with open('api/index.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, l in enumerate(lines):
    if '@app.post' in l or '@app.get' in l:
        print(f"api/index.py Line {i+1}: {l.strip()[:90]}")
