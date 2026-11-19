with open('VernaLedger_Presentation.html', 'r', encoding='utf-8') as f:
    text = f.read()

import re

s16_start = text.find('<!-- SLIDE 16:')
s17_start = text.find('<!-- SLIDE 17:')
clean = re.sub(r'data:image/[^;]+;base64,[A-Za-z0-9+/=]+', '[IMG_BASE64]', text[s16_start:s17_start])
print(clean)
