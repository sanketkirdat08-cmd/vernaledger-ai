import re

with open('VernaLedger_Presentation.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Split by slide comments
slide_blocks = re.split(r'<!-- SLIDE (\d+): (.*?) -->', html)
# slide_blocks[0] is header
print(f"Total parts: {len(slide_blocks)}")

slides_dict = {}
for i in range(1, len(slide_blocks), 3):
    num = int(slide_blocks[i])
    name = slide_blocks[i+1]
    content = slide_blocks[i+2]
    slides_dict[num] = {"name": name, "content": content}

print(f"Extracted {len(slides_dict)} slides.")
for num in sorted(slides_dict.keys()):
    c = slides_dict[num]['content']
    # extract title
    title_m = re.search(r'<h2 class="slide-title">([^<]+)</h2>', c)
    sub_m = re.search(r'<p class="slide-subtitle">([^<]+)</p>', c)
    title = title_m.group(1).strip() if title_m else ""
    sub = sub_m.group(1).strip() if sub_m else ""
    card_titles = re.findall(r'<h3 class="card-title"[^>]*>([^<]+)</h3>', c)
    print(f"Slide {num:02d}: {title} | Cards: {len(card_titles)} -> {card_titles[:2]}")
