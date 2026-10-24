import re, sys

sys.stdout.reconfigure(encoding='utf-8')

with open('index.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

devanagari_pattern = re.compile(r'[\u0900-\u097F]+')

untranslated_lines = []

for idx, line in enumerate(lines, start=1):
    # Skip script tags, style tags, comments
    stripped = line.strip()
    if not stripped or stripped.startswith('<!--') or stripped.startswith('//') or stripped.startswith('*'):
        continue
    
    # Check if line contains Devanagari
    if devanagari_pattern.search(line):
        # Check if line has data-i18n
        if 'data-i18n' not in line and 'data-i18n-ph' not in line and 'data-i18n-title' not in line:
            untranslated_lines.append((idx, stripped))

print(f"Found {len(untranslated_lines)} lines with Devanagari text missing data-i18n:")
for idx, text in untranslated_lines:
    print(f"Line {idx:3d}: {text[:100]}")
