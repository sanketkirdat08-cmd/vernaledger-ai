import re

with open('generate_presentation_script_pdf.py', 'r', encoding='utf-8') as f:
    pdf_text = f.read()

with open('VernaLedger_Presentation.html', 'r', encoding='utf-8') as f:
    html_text = f.read()

pdf_slides = re.findall(r'<span class="slide-pill">(SLIDE \d+)</span>\s*([^<]+)', pdf_text)
print(f"Total slides in PDF generator: {len(pdf_slides)}")
for s, title in pdf_slides:
    print(f"  {s}: {title.strip()}")

html_badges = re.findall(r'<div class="slide-badge">(\d+)[^<]*</div>\s*<h2 class="slide-title">([^<]+)</h2>', html_text)
print(f"\nTotal slides in HTML: {len(html_badges)}")
for num, title in html_badges:
    print(f"  SLIDE {num}: {title.strip()}")
