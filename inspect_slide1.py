with open('VernaLedger_Presentation.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, l in enumerate(lines):
    if '<section' in l:
        print(f"Section at line {i+1}: {l.strip()[:80]}")
