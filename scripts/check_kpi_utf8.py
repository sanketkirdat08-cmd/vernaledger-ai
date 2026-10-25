import sys
sys.stdout.reconfigure(encoding='utf-8')

with open("index.html", "r", encoding="utf-8") as f:
    lines = f.readlines()

for i in range(375, 390):
    if i < len(lines):
        print(f"{i+1}: {repr(lines[i])}")

