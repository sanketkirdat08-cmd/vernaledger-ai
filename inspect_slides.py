with open('VernaLedger_Presentation.html', 'r', encoding='utf-8') as f:
    text = f.read()

import re
slides = re.findall(r'(<section[^>]*>.*?</section>)', text, flags=re.DOTALL)

def clean_slide(s):
    s_clean = re.sub(r'src="data:image/[^;]+;base64,[^"]+"', 'src="[BASE64_IMAGE]"', s)
    return s_clean

print('=== SLIDE 12 ===')
print(clean_slide(slides[11]))
print('\n=== SLIDE 15 ===')
print(clean_slide(slides[14]))
