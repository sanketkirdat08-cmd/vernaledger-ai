with open('VernaLedger_Presentation.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if 'slide-badge' in line and any(k in line for k in ['12', '15']):
        print(f"=== Found at line {i+1}: {line.strip()} ===")
        # Print next 80 lines or up to next slide
        for j in range(max(0, i-4), min(len(lines), i+80)):
            l = lines[j]
            if j > i and '<!-- Slide' in l:
                break
            # Truncate very long lines like base64
            if len(l) > 120:
                print(f"{j+1}: {l[:100]}... [len {len(l)}]")
            else:
                print(f"{j+1}: {l.rstrip()}")
