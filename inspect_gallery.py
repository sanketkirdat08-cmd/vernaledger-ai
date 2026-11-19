with open('VernaLedger_Presentation.html', 'r', encoding='utf-8') as f:
    text = f.read()

pos = text.find('const galleryItems = [')
print(text[pos:pos+2000])
