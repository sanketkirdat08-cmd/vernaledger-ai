import re

with open('create_presentation.py', 'r', encoding='utf-8') as f:
    code = f.read()

# Let's see helper functions
helpers_match = re.search(r'# Cyberpunk Neon Color Palette.*?(?=# SLIDE 1:)', code, re.DOTALL)
if helpers_match:
    print(helpers_match.group(0)[:1500])
