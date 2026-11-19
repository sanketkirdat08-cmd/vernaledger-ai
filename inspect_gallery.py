with open('VernaLedger_Presentation.html', 'r', encoding='utf-8') as f:
    text = f.read()

import re

# find objects in galleryItems
pos = text.find('const galleryItems = [')
end_pos = text.find('];', pos)
gallery_text = text[pos:end_pos]

items = re.findall(r'title:\s*[\'"]([^\'"]+)[\'"]\s*,\s*desc:\s*[\'"]([^\'"]+)[\'"]', gallery_text)
print(f"Total items in galleryItems: {len(items)}")
for i, (t, d) in enumerate(items):
    print(f"Item {i+1}: {t} -> {d[:60]}...")
