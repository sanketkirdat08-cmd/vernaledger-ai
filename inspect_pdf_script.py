with open('generate_presentation_script_pdf.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

s12_lines = []
s15_lines = []

recording_12 = False
recording_15 = False

for idx, line in enumerate(lines):
    if 'SLIDE 12:' in line:
        recording_12 = True
    elif recording_12 and 'SLIDE 13:' in line:
        recording_12 = False
    
    if recording_12:
        s12_lines.append((idx + 1, line))
        
    if 'SLIDE 15:' in line:
        recording_15 = True
    elif recording_15 and 'SLIDE 16:' in line:
        recording_15 = False
        
    if recording_15:
        s15_lines.append((idx + 1, line))

print("=== SLIDE 12 SECTION (lines %d-%d) ===" % (s12_lines[0][0], s12_lines[-1][0]))
for num, line in s12_lines:
    print(f"{num}: {line.rstrip()}")

print("\n=== SLIDE 15 SECTION (lines %d-%d) ===" % (s15_lines[0][0], s15_lines[-1][0]))
for num, line in s15_lines:
    print(f"{num}: {line.rstrip()}")
