with open('VernaLedger_Presentation.html', 'r', encoding='utf-8') as f:
    content = f.read()

import re
badges = re.findall(r'<div class="zoom-badge">[^<]+</div>', content)
print("Found zoom badges:", len(badges), set(badges))
