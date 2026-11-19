import re
import json

with open('VernaLedger_Presentation.html', 'r', encoding='utf-8') as f:
    html = f.read()

slide_blocks = re.split(r'<!-- SLIDE (\d+): (.*?) -->', html)
slides_dict = {}
for i in range(1, len(slide_blocks), 3):
    num = int(slide_blocks[i])
    name = slide_blocks[i+1]
    content = slide_blocks[i+2]
    slides_dict[num] = {"name": name, "content": content}

results_data = {}

for num in range(12, 20):
    c = slides_dict[num]['content']
    title_m = re.search(r'<h2 class="slide-title">([^<]+)</h2>', c)
    sub_m = re.search(r'<div class="slide-subtitle">([^<]+)</div>', c)
    eyebrow_m = re.search(r'<div class="slide-eyebrow">([^<]+)</div>', c)
    title = title_m.group(1).strip() if title_m else ""
    sub = sub_m.group(1).strip() if sub_m else ""
    eyebrow = eyebrow_m.group(1).strip() if eyebrow_m else ""
    
    # Extract features
    features = []
    f_matches = re.findall(r'<div class="feature-item[^"]*">\s*<div class="feature-title">(.*?)</div>\s*<p class="feature-desc">(.*?)</p>', c, re.DOTALL)
    for ft, fd in f_matches:
        # strip tags
        ft_clean = re.sub(r'<[^>]+>', '', ft).strip()
        fd_clean = re.sub(r'<[^>]+>', '', fd).strip()
        features.append({"title": ft_clean, "desc": fd_clean})
    
    results_data[num] = {
        "title": title,
        "subtitle": sub,
        "eyebrow": eyebrow,
        "features": features
    }
    print(f"\nSlide {num}: {title} ({len(features)} features)")
    for f in features:
        print(f"  * {f['title']}: {f['desc'][:60]}...")

with open('results_slides_content.json', 'w', encoding='utf-8') as jf:
    json.dump(results_data, jf, indent=2, ensure_ascii=False)
