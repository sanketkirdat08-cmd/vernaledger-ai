with open('VernaLedger_Presentation.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

def print_slice(start, end):
    for idx in range(start-1, end):
        line = lines[idx]
        if 'base64,' in line:
            # show start and end
            prefix = line[:line.find('base64,') + 15]
            print(f"{idx+1}: {prefix}... [len {len(line)}]")
        else:
            print(f"{idx+1}: {line.rstrip()}")

print("=== SLIDE 12 ===")
print_slice(1760, 1798)

print("\n=== SLIDE 15 ===")
print_slice(1860, 1903)
