with open('api/index.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

import re
endpoints = []
for i, line in enumerate(lines):
    if re.match(r'@app\.(get|post|put|delete|patch|websocket)', line.strip()):
        endpoints.append((i+1, line.strip(), lines[i+1].strip() if i+1 < len(lines) else ''))

print(f"Total API endpoints in api/index.py: {len(endpoints)}")
for ep in endpoints:
    print(f"Line {ep[0]}: {ep[1]} -> {ep[2]}")
