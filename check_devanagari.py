with open('VernaLedger_Presentation.html', 'r', encoding='utf-8') as f:
    text = f.read()

import re
sections = re.findall(r'<section[^>]*>(.*?)</section>', text, re.DOTALL)

for i, sec in enumerate(sections):
    clean = re.sub(r'data:image/[^;]+;base64,[A-Za-z0-9+/=]+', '[IMG]', sec)
    # Check if there is Marathi Devanagari text
    devanagari = re.findall(r'[\u0900-\u097F]+', clean)
    dev_count = len(devanagari)
    badge = re.search(r'class="slide-badge">([^<]+)<', sec)
    b_text = badge.group(1).strip() if badge else "Cover/End"
    title = re.search(r'<h[12][^>]*>(.*?)</h[12]>', sec)
    t_text = re.sub(r'<[^>]+>', '', title.group(1).strip()) if title else ""
    print(f"Slide {i+1} [{b_text}]: '{t_text}' -> Devanagari words: {dev_count}")
    if dev_count > 0:
        print(f"   Sample Devanagari: {' '.join(devanagari[:8])}")
