with open('VernaLedger_Presentation.html', 'r', encoding='utf-8') as f:
    text = f.read()

import re

# Find sections
sections = re.findall(r'<section[^>]*>(.*?)</section>', text, re.DOTALL)
print(f"Total sections: {len(sections)}")

for i, sec in enumerate(sections):
    # extract title
    title_match = re.search(r'<h[12][^>]*>(.*?)</h[12]>', sec)
    title = title_match.group(1).strip() if title_match else "No title"
    # clean HTML tags from title
    title = re.sub(r'<[^>]+>', '', title)
    
    badge_match = re.search(r'class="slide-badge">([^<]+)<', sec)
    badge = badge_match.group(1).strip() if badge_match else ""
    
    # Check if there is base64
    has_img = 'data:image' in sec
    
    # Content length without base64
    clean_sec = re.sub(r'data:image/[^;]+;base64,[A-Za-z0-9+/=]+', '[IMG]', sec)
    text_content = re.sub(r'<[^>]+>', ' ', clean_sec)
    text_content = ' '.join(text_content.split())[:120]
    
    print(f"Slide {i+1}: [{badge}] {title} | Img: {has_img} | Preview: {text_content[:80]}...")
