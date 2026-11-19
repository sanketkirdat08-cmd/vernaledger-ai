with open('VernaLedger_Presentation.html', 'r', encoding='utf-8') as f:
    text = f.read()

# Let's inspect slide 2, 3, 4
s2 = text.find('<!-- SLIDE 02: INTRODUCTION -->')
s5 = text.find('<!-- SLIDE 05: GAP ANALYSIS -->')
print(text[s2:s2+1500])
