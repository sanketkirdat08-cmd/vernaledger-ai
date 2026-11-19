with open('VernaLedger_Presentation.html', 'r', encoding='utf-8') as f:
    text = f.read()

import re
imgs = re.findall(r'<img[^>]+src=["\']([^"\']+)["\']', text)
print(f"Total img tags: {len(imgs)}")
for i, src in enumerate(imgs):
    if src.startswith('data:image'):
        print(f"  Img {i+1}: base64 image (length {len(src)})")
    else:
        print(f"  Img {i+1}: {src[:60]}")
