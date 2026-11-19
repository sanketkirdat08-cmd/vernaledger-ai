with open('VernaLedger_Presentation.html', 'r', encoding='utf-8') as f:
    text = f.read()

s = text.find('<!-- SLIDE 05: GAP ANALYSIS -->')
e = text.find('<!-- SLIDE 06: OBJECTIVES -->')
print(text[s:e])
