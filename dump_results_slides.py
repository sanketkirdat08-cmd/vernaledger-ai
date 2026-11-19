import re

with open('VernaLedger_Presentation.html', 'r', encoding='utf-8') as f:
    html = f.read()

slide_blocks = re.split(r'<!-- SLIDE (\d+): (.*?) -->', html)
slides_dict = {}
for i in range(1, len(slide_blocks), 3):
    num = int(slide_blocks[i])
    name = slide_blocks[i+1]
    content = slide_blocks[i+2]
    slides_dict[num] = {"name": name, "content": content}

for num in range(12, 20):
    c = slides_dict[num]['content']
    title_m = re.search(r'<h2 class="slide-title">([^<]+)</h2>', c)
    sub_m = re.search(r'<p class="slide-subtitle">([^<]+)</p>', c)
    title = title_m.group(1).strip() if title_m else ""
    sub = sub_m.group(1).strip() if sub_m else ""
    
    items = re.findall(r'<div class="split-item">\s*<h4[^>]*>([^<]+)</h4>\s*<p>([^<]+)</p>', c)
    print(f"\n=== SLIDE {num}: {title} ===")
    print(f"Subtitle: {sub}")
    for h, p in items:
        print(f"  - {h.strip()}: {p.strip()[:80]}...")
