import re

with open('VernaLedger_Presentation.html', 'r', encoding='utf-8') as f:
    html = f.read()

sections = re.findall(r'<section class="slide[^"]*" id="slide-(\d+)">(.*?)</section>', html, re.DOTALL)
print(f"Total sections found in HTML: {len(sections)}")

for num, content in sections:
    title_m = re.search(r'<h2 class="slide-title">([^<]+)</h2>', content)
    sub_m = re.search(r'<p class="slide-subtitle">([^<]+)</p>', content)
    eyebrow_m = re.search(r'<div class="slide-eyebrow">([^<]+)</div>', content)
    badge_m = re.search(r'<div class="slide-badge">([^<]+)</div>', content)
    
    title = title_m.group(1).strip() if title_m else "N/A"
    sub = sub_m.group(1).strip() if sub_m else "N/A"
    eyebrow = eyebrow_m.group(1).strip() if eyebrow_m else "N/A"
    badge = badge_m.group(1).strip() if badge_m else "N/A"
    
    print(f"Slide {num}: {eyebrow} | {badge} | {title} | {sub}")
