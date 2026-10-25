import os, sys, re
sys.stdout.reconfigure(encoding='utf-8')

search_terms = [
    "3034", "3036", "3035", "3033",
    "24213340334", "24213340336", "24213340335", "24213340333",
    "4060", "4054", "4056", "4004"
]

for root, dirs, files in os.walk('.'):
    if any(p in root for p in ['venv', '.git', '__pycache__']):
        continue
    for f in files:
        if f.endswith(('.py', '.html', '.md', '.json', '.js', '.txt')):
            path = os.path.join(root, f)
            try:
                with open(path, 'r', encoding='utf-8', errors='ignore') as fp:
                    content = fp.read()
                    for term in search_terms:
                        if term in content:
                            print(f"Found '{term}' in {path}")
            except Exception as e:
                pass
