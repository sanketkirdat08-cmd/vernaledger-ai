with open('VernaLedger_Presentation.html', 'r', encoding='utf-8') as f:
    text = f.read()

import re
sections = re.findall(r'<section[^>]*>(.*?)</section>', text, re.DOTALL)

for idx in [12, 13, 15, 16, 17, 18]: # 0-indexed: slides 13, 14, 16, 17, 18, 19
    sec = sections[idx]
    clean = re.sub(r'data:image/[^;]+;base64,[A-Za-z0-9+/=]+', '[IMG]', sec)
    print(f"=== SLIDE {idx+1} ===")
    for line in clean.splitlines():
        l = line.strip()
        if l and not l.startswith('<div class="slide-bg') and not l.startswith('<div class="split-img'):
            print(f"  {l[:110]}")
