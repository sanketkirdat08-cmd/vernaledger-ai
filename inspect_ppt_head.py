with open('VernaLedger_Presentation.html', 'r', encoding='utf-8') as f:
    text = f.read()

start_css = text.find('<style>')
end_css = text.find('</style>')
css = text[start_css:end_css]

import re
rules = re.findall(r'([^{]+)\{', css)
print(f"Total CSS selectors: {len(rules)}")
for r in rules[:30]:
    print(" ", r.strip()[:60])
