with open('VernaLedger_Presentation.html', 'r', encoding='utf-8') as f:
    text = f.read()

import re
m = re.search(r'<div class="slides">\s*(<section.*?</section>)', text, re.DOTALL)
if m:
    print(m.group(1)[:2000])
