with open('VernaLedger_Presentation.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

def print_clean(start, end):
    for i in range(start, end):
        l = lines[i]
        if 'base64,' in l:
            print(f"{i+1}: [base64 image, length {len(l)}]")
        else:
            print(f"{i+1}: {l.rstrip()}")

print("=== SLIDE 12 ===")
print_clean(1760, 1798)

print("\n=== SLIDE 15 ===")
print_clean(1870, 1904)
