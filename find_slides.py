with open('VernaLedger_Presentation.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for idx in range(1782, 1791):
    print(f"--- Line {idx+1} ---")
    print(lines[idx])
