import re

with open('api/index.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

comment_code_blocks = []
current_block = []

for i, line in enumerate(lines):
    stripped = line.strip()
    # Check if commented line looks like code (e.g. # def, # import, # if, # return, # for, # app., # db.)
    if stripped.startswith('#') and any(stripped.startswith(f'# {kw}') or stripped.startswith(f'#{kw}') for kw in ['def', 'import', 'if', 'return', 'for', 'app.', 'db.', 'cursor.', 'print(', 'console.', 'var ', 'let ', 'const ']):
        current_block.append((i+1, stripped))
    else:
        if len(current_block) > 0:
            comment_code_blocks.append(current_block)
            current_block = []

print(f"Commented code blocks found in api/index.py: {len(comment_code_blocks)}")
for b in comment_code_blocks[:15]:
    print(f"Lines {b[0][0]}-{b[-1][0]}: {b[0][1][:60]} (len {len(b)})")
