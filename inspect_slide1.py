with open('VernaLedger_Presentation.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, l in enumerate(lines[:450]):
    if '<section' in l or 'class="slides"' in l or 'VernaLedger' in l:
        print(f"Line {i+1}: {l.strip()[:100]}")
