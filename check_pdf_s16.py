with open('generate_presentation_script_pdf.py', 'r', encoding='utf-8') as f:
    text = f.read()

s16_start = text.find('<!-- SLIDE 16:')
s17_start = text.find('<!-- SLIDE 17:')
print(text[s16_start:s17_start])
