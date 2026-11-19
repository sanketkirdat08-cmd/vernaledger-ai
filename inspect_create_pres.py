import re

with open('create_presentation.py', 'r', encoding='utf-8') as f:
    code = f.read()

# Let's find slide sections
slides = re.findall(r'(# =+\s*# SLIDE \d+:.*?(?=# =+\s*# SLIDE \d+:|\Z))', code, re.DOTALL)
print(f"Total slide sections found: {len(slides)}")
for s in slides:
    header = s.strip().split('\n')[1]
    print(header)
