with open('VernaLedger_Presentation.html', 'r', encoding='utf-8') as f:
    text = f.read()

import re

# print slides 12 through 19 without base64
for s_num in range(12, 20):
    start_tag = f"<!-- SLIDE {s_num:02d}:"
    end_tag = f"<!-- SLIDE {s_num+1:02d}:" if s_num < 19 else "<!-- SLIDE 20:"
    
    start_pos = text.find(start_tag)
    end_pos = text.find(end_tag)
    
    if start_pos != -1 and end_pos != -1:
        s_text = text[start_pos:end_pos]
        clean = re.sub(r'data:image/[^;]+;base64,[A-Za-z0-9+/=]+', '[IMG_BASE64]', s_text)
        print(f"***** SLIDE {s_num} *****")
        print(clean.strip())
        print("\n")
