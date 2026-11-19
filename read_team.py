with open('generate_presentation_script_pdf.py', 'r', encoding='utf-8') as f:
    text = f.read()

pos = text.find('team-grid')
if pos != -1:
    # find next team-grid occurrence in body
    pos2 = text.find('team-grid', pos + 20)
    print(text[pos2-20:pos2+2000])
