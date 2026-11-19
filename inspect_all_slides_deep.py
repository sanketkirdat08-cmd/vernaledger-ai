with open('VernaLedger_Presentation.html', 'r', encoding='utf-8') as f:
    text = f.read()

import re
sections = re.findall(r'<section[^>]*>(.*?)</section>', text, re.DOTALL)
print(f"Total sections: {len(sections)}\n")

for i, sec in enumerate(sections):
    clean = re.sub(r'data:image/[^;]+;base64,[A-Za-z0-9+/=]+', '[BASE64_IMAGE]', sec)
    lines = [l.strip() for l in clean.splitlines() if l.strip()]
    print(f"=== SLIDE {i+1} ===")
    for l in lines[:10]:
        print(f"  {l[:100]}")
    print("...")
