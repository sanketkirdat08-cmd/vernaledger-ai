with open('generate_presentation_script_pdf.py', 'r', encoding='utf-8') as f:
    text = f.read()

start_css = text.find('<style>')
end_css = text.find('</style>')
print(text[start_css+1200:end_css])
