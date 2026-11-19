with open('generate_project_directory_guide_pdf.py', 'r', encoding='utf-8') as f:
    text = f.read()

print("Length:", len(text))
pos = text.find('team-grid')
if pos != -1:
    print(text[pos:pos+1500])
else:
    # search for names
    pos_sanket = text.find('Sanket')
    if pos_sanket != -1:
        print(text[pos_sanket-50:pos_sanket+1000])
