with open('VernaLedger_Presentation.html', 'r', encoding='utf-8') as f:
    text = f.read()

import re
matches = re.findall(r'<div class="slide-badge">([^<]+)</div>\s*<h2 class="slide-title">([^<]+)</h2>', text)
print(f"Total slides: {len(matches)}")
for badge, title in matches:
    print(f"{badge.strip()} -> {title.strip()}")
