import re

with open('VernaLedger_Presentation.html', 'r', encoding='utf-8') as f:
    html = f.read()

pos12 = html.find('<!-- SLIDE 12:')
pos13 = html.find('<!-- SLIDE 13:')
# print without base64 img
s12_clean = re.sub(r'data:image/[^;]+;base64,[^"\']+', '[BASE64_IMAGE]', html[pos12:pos13])
print(s12_clean)
