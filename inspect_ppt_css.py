with open('VernaLedger_Presentation.html', 'r', encoding='utf-8') as f:
    text = f.read()

# Let's inspect styles
start_css = text.find('<style>')
end_css = text.find('</style>')
print(text[start_css:start_css+2000])
