with open('VernaLedger_Presentation.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for idx in range(1782, 1792):
    print(f"{idx+1}: {lines[idx].rstrip()[:120]}")
