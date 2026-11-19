with open('VernaLedger_Presentation.html', 'r', encoding='utf-8') as f:
    text = f.read()

hud_start = text.find('<!-- Top HUD Navbar -->')
if hud_start == -1:
    hud_start = text.find('top-hud')
    
print("HUD section:")
print(text[hud_start-50:hud_start+1500])
