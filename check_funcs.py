import re

with open('create_presentation.py', 'r', encoding='utf-8') as f:
    code = f.read()

pos = code.find('def set_slide_background')
pos_end = code.find('# SLIDE 1:')
print(code[pos:pos_end])
