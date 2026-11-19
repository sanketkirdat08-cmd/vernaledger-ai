with open('VernaLedger_Presentation.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i in range(1270, 1310):
    print(f"{i+1}: {lines[i].rstrip()}")
