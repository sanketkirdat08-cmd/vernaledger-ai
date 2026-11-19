with open('VernaLedger_Presentation.html', 'r', encoding='utf-8') as f:
    text = f.read()

import re
sections = re.findall(r'<section[^>]*>(.*?)</section>', text, re.DOTALL)

for idx in [2, 4, 7, 8, 9, 10, 19, 20, 21, 22]:
    sec = sections[idx]
    clean = re.sub(r'data:image/[^;]+;base64,[A-Za-z0-9+/=]+', '[IMG]', sec)
    badge = re.search(r'class="slide-badge">([^<]+)<', sec)
    b_text = badge.group(1).strip() if badge else "Cover/End"
    title = re.search(r'<h[12][^>]*>(.*?)</h[12]>', sec)
    t_text = re.sub(r'<[^>]+>', '', title.group(1).strip()) if title else ""
    print(f"=== SLIDE {idx+1} [{b_text}]: {t_text} ===")
    for line in clean.splitlines():
        l = line.strip()
        if l and not l.startswith('<div class="slide-bg') and not l.startswith('<div class="split-img'):
            print(f"  {l[:100]}")
    print("\n")
