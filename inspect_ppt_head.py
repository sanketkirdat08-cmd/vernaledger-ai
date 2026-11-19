with open('VernaLedger_Presentation.html', 'r', encoding='utf-8') as f:
    text = f.read()

import re
matches = [m.start() for m in re.finditer(r'class="[^"]*hud[^"]*"', text, re.I)]
print("HUD matches:", len(matches))
for p in matches[:5]:
    print(text[p-20:p+120])
