with open('VernaLedger_Presentation.html', 'r', encoding='utf-8') as f:
    text = f.read()

import re

# find openLightbox calls
matches = re.findall(r'openLightbox\([^,]+,\s*[\'"]([^\'"]+)[\'"]\s*,\s*[\'"]([^\'"]+)[\'"]', text)
print(f"Total openLightbox calls: {len(matches)}")
for i, (title, desc) in enumerate(matches):
    print(f"{i+1}: {title} | {desc[:60]}...")
