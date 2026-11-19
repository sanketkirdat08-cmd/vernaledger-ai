import re
import os
import base64

with open('VernaLedger_Presentation.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Find all img tags
img_tags = re.findall(r'<img[^>]+>', html)
print(f"Total img tags found: {len(img_tags)}")

os.makedirs('real_screenshots', exist_ok=True)

saved = 0
for i, tag in enumerate(img_tags):
    alt_match = re.search(r'alt=["\']([^"\']*)["\']', tag)
    alt = alt_match.group(1) if alt_match else f"image_{i+1}"
    
    src_match = re.search(r'src=["\']([^"\']+)["\']', tag)
    if not src_match:
        continue
    src = src_match.group(1)
    if src.startswith('data:image/'):
        header, b64_data = src.split(';base64,', 1)
        ext = header.split('/')[1]
        if '+' in ext:
            ext = ext.split('+')[0]
        filename = f"real_screenshots/slide_img_{i+1}_{re.sub(r'[^a-zA-Z0-9_]', '_', alt)[:30]}.{ext}"
        with open(filename, 'wb') as img_f:
            img_f.write(base64.b64decode(b64_data))
        print(f"Saved {filename} ({os.path.getsize(filename)} bytes) - Alt: {alt}")
        saved += 1
    else:
        print(f"Non-base64: {src[:60]}")

print(f"Total saved: {saved}")
