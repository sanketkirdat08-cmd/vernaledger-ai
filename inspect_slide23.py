with open('VernaLedger_Presentation.html', 'r', encoding='utf-8') as f:
    text = f.read()

s = text.find('<!-- SLIDE 23: CONCLUSION & THANK YOU -->')
print(text[s:])
