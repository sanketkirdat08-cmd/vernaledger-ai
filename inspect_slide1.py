with open('VernaLedger_Presentation.html', 'r', encoding='utf-8') as f:
    text = f.read()

s1 = text.find('<!-- SLIDE 1: COVER / TITLE -->')
s2 = text.find('<!-- SLIDE 2: INTRODUCTION -->')
print(text[s1:s2])
