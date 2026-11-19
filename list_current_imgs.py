with open('VernaLedger_Presentation.html', 'r', encoding='utf-8') as f:
    text = f.read()

import re
sections = re.findall(r'<section[^>]*>(.*?)</section>', text, re.DOTALL)

for i, sec in enumerate(sections):
    imgs = re.findall(r'<img[^>]+src=["\']([^"\']+)["\']', sec)
    titles = re.findall(r'<h[12][^>]*>(.*?)</h[12]>', sec)
    title = re.sub(r'<[^>]+>', '', titles[0]) if titles else ""
    if imgs:
        print(f"Slide {i+1} ({title}): {len(imgs)} image(s), lengths: {[len(img) for img in imgs]}")
