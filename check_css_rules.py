with open('VernaLedger_Presentation.html', 'r', encoding='utf-8') as f:
    text = f.read()

import re
matches = re.findall(r'(\.split-layout[^{]*\{[^}]*\})', text)
for m in matches[:5]:
    print(m)

matches2 = re.findall(r'(\.feature-item[^{]*\{[^}]*\})', text)
for m in matches2[:5]:
    print(m)
