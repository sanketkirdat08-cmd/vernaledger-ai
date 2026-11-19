with open('VernaLedger_Presentation.html', 'r', encoding='utf-8') as f:
    text = f.read()

import re
matches = re.findall(r'(\.slide-title[^{]*\{[^}]*\})', text)
for m in matches:
    print(m)

matches2 = re.findall(r'(\.slide-subtitle[^{]*\{[^}]*\})', text)
for m in matches2:
    print(m)

matches3 = re.findall(r'(\.feature-desc[^{]*\{[^}]*\})', text)
for m in matches3:
    print(m)
